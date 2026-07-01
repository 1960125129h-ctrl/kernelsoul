"""
Kernelsoul - Semantic Rendering Engine (v2.4)
Chapter 21.2-21.3: Semantic axes, state projection, Warp calibration, SLERP updates.

Core math layer - pure numpy, no AI calls here.
"""
from __future__ import annotations
import json, os, math
from typing import Optional
import numpy as np


class SemanticEngine:
    """Manages semantic axes, subspace projection, and state evolution in embedding space.

    The engine converts GameState numeric deltas into semantic-space movements
    using a calibrated Warp function, then updates a state point (position + intensity)
    through the subspace.

    Key data structures:
      A matrix [d, m] — semantic axes (one column per game dimension)
      G matrix [m, m] — Gram matrix A^T A (for coordinate de-correlation)
      Q matrix [d, k] — reduced subspace basis (k << d)
      Warp stages — per-axis stage boundaries with density curves
    """

    def __init__(self, embedding_dim: int = 1536, subspace_k: int = 20):
        self.dim = embedding_dim
        self.subspace_k = subspace_k

        # ── Axes (built lazily via build_axes) ──
        self.axis_names: list[str] = []
        self.axis_positive_anchors: list[str] = []
        self.axis_negative_anchors: list[str] = []
        self.design_weights: list[float] = []

        # Matrices
        self.A: Optional[np.ndarray] = None       # [d, m]
        self.G: Optional[np.ndarray] = None       # [m, m]
        self.G_inv: Optional[np.ndarray] = None   # [m, m]
        self.Q: Optional[np.ndarray] = None       # [d, k]
        self.center: Optional[np.ndarray] = None  # [d]

        # ── Warp calibration (per axis) ──
        self.warp_stages: list[list[str]] = []       # per-axis stage anchors
        self.warp_stage_embeddings: list[np.ndarray] = []  # per-axis [n_stages, d]
        self.warp_density_curves: list[np.ndarray] = []    # per-axis [n_stages-1]

        # ── Runtime state ──
        self.semantic_p: Optional[np.ndarray] = None  # [k] normalized direction
        self.semantic_r: float = 1.0                  # intensity scalar
        self.semantic_momentum: Optional[np.ndarray] = None  # [k]
        self.momentum_decay: float = 0.85

        # State variable ranges (for value→stage interpolation)
        self.var_ranges: dict[str, tuple[float, float]] = {}
        self.var_currents: dict[str, float] = {}

        # ── Embed function (set by caller) ──
        self._embed_fn = None

    # ═══════════════════════════════════════════════════
    # 21.3.1  Semantic axis construction
    # ═══════════════════════════════════════════════════

    def register_axis(self, name: str, positive_anchor: str, negative_anchor: str,
                      design_weight: float = 1.0, warp_stages: list[str] | None = None):
        """Register a game dimension for semantic rendering."""
        self.axis_names.append(name)
        self.axis_positive_anchors.append(positive_anchor)
        self.axis_negative_anchors.append(negative_anchor)
        self.design_weights.append(design_weight)
        self.warp_stages.append(warp_stages or [])

    def build_axes(self):
        """Construct A matrix from registered axes using embedding function.
        D_i = embed(positive_anchor_i) - embed(negative_anchor_i)
        """
        if self._embed_fn is None:
            raise RuntimeError("Embed function not set. Call set_embed_fn() first.")

        m = len(self.axis_names)
        if m == 0:
            raise RuntimeError("No axes registered. Call register_axis() first.")

        # Embed all anchors in one batch
        all_anchors = []
        for i in range(m):
            all_anchors.append(self.axis_positive_anchors[i])
            all_anchors.append(self.axis_negative_anchors[i])
        all_emb = self._embed_fn(all_anchors)  # [2m, d]
        all_emb = np.array(all_emb, dtype=np.float64)

        # Build A matrix
        self.A = np.zeros((self.dim, m), dtype=np.float64)
        for i in range(m):
            D_i = all_emb[2*i] - all_emb[2*i + 1]
            self.A[:, i] = D_i

        # Embed warp stage anchors
        self._build_warp_stages()

        # Build combined matrix for subspace
        self._build_subspace()

    def _build_warp_stages(self):
        """Embed all warp stage anchors per axis."""
        self.warp_stage_embeddings = []
        self.warp_density_curves = []

        all_stage_texts = []
        stage_counts = []
        for stages in self.warp_stages:
            stage_counts.append(len(stages))
            all_stage_texts.extend(stages)

        if all_stage_texts:
            all_stage_emb = self._embed_fn(all_stage_texts)
            all_stage_emb = np.array(all_stage_emb, dtype=np.float64)

            idx = 0
            for count in stage_counts:
                if count > 0:
                    stages_emb = all_stage_emb[idx:idx + count]
                    self.warp_stage_embeddings.append(stages_emb)
                    # Compute densities from projection onto axes
                else:
                    self.warp_stage_embeddings.append(np.empty((0, self.dim)))
                idx += count

    def _build_subspace(self):
        """21.3.3 Build reduced subspace via SVD on combined matrix B."""
        m = len(self.axis_names)
        self.center = np.zeros(self.dim, dtype=np.float64)

        # Collect all basis vectors: axes + (stage_points - center)
        parts = [self.A]
        for stages_emb in self.warp_stage_embeddings:
            if stages_emb.shape[0] > 0:
                parts.append(stages_emb.T)
        if len(parts) == 0:
            return

        B = np.hstack(parts)

        # SVD for dimensionality reduction
        if B.shape[1] >= self.subspace_k:
            U, S, Vt = np.linalg.svd(B, full_matrices=False)
            self.Q = U[:, :self.subspace_k].copy()
        else:
            # Fewer basis vectors than k, pad with zeros
            self.Q = np.zeros((self.dim, self.subspace_k), dtype=np.float64)
            self.Q[:, :B.shape[1]] = B

        # Gram matrix
        self.G = self.A.T @ self.A
        try:
            self.G_inv = np.linalg.inv(self.G)
        except np.linalg.LinAlgError:
            self.G_inv = np.linalg.pinv(self.G)

    # ═══════════════════════════════════════════════════
    # 21.3.2  Coordinate de-correlation
    # ═══════════════════════════════════════════════════

    def project_to_coordinates(self, embedding: np.ndarray) -> np.ndarray:
        """τ(e) = G^(-1) A^T (e - c)"""
        if self.G_inv is None or self.A is None:
            raise RuntimeError("Axes not built")
        e = np.asarray(embedding, dtype=np.float64)
        return self.G_inv @ self.A.T @ (e - self.center)

    def project_to_subspace(self, embedding: np.ndarray) -> np.ndarray:
        """z = Q^T (e - c)"""
        if self.Q is None:
            raise RuntimeError("Subspace not built")
        e = np.asarray(embedding, dtype=np.float64)
        return self.Q.T @ (e - self.center)

    # ═══════════════════════════════════════════════════
    # 21.3.4  Warp calibration
    # ═══════════════════════════════════════════════════

    def set_var_range(self, name: str, lo: float, hi: float):
        self.var_ranges[name] = (lo, hi)

    def set_var_value(self, name: str, value: float):
        self.var_currents[name] = value

    def compute_warp_delta(self, axis_idx: int, v_old: float, v_new: float) -> float:
        """Compute Δt for one axis given numeric value change.
        Uses the calibrated stage densities for Warp mapping.
        """
        if axis_idx >= len(self.warp_stage_embeddings):
            return 0.0

        stages_emb = self.warp_stage_embeddings[axis_idx]
        n_stages = stages_emb.shape[0]
        if n_stages < 2:
            # No warp stages → linear mapping
            return (v_new - v_old) * self.design_weights[axis_idx]

        # Get the axis direction in full embedding space
        axis_vec = self.A[:, axis_idx]  # [d]

        # Project stages onto this axis
        stage_projections = stages_emb @ axis_vec  # [n_stages]
        stage_projections = (stage_projections - stage_projections.min())
        denom = stage_projections.max() or 1.0
        stage_projections /= denom  # [0, 1] normalized

        # Compute density per stage interval
        eps = 1e-8
        densities = []
        for i in range(n_stages - 1):
            gap = stage_projections[i+1] - stage_projections[i]
            densities.append(1.0 / (gap + eps))
        total_density = sum(densities) or 1.0
        densities = [d / total_density for d in densities]

        # Interpolate Δv → Δt using density curve
        v_range = self.var_ranges.get(self.axis_names[axis_idx], (-100, 100))
        v_norm_old = (v_old - v_range[0]) / max(v_range[1] - v_range[0], 1)
        v_norm_new = (v_new - v_range[0]) / max(v_range[1] - v_range[0], 1)
        v_norm_old = max(0, min(1, v_norm_old))
        v_norm_new = max(0, min(1, v_norm_new))

        # Stage index lookup
        def stage_index(vn):
            for i in range(n_stages - 1):
                if vn <= stage_projections[i + 1]:
                    return i
            return n_stages - 2

        idx_old = stage_index(v_norm_old)
        idx_new = stage_index(v_norm_new)

        # Integrate over density
        if idx_old == idx_new:
            seg_len = abs(v_norm_new - v_norm_old)
            return densities[idx_old] * seg_len * self.design_weights[axis_idx]
        else:
            step = 1 if idx_new > idx_old else -1
            total = 0.0
            cur = v_norm_old
            i = idx_old
            while i != idx_new:
                boundary = stage_projections[i + 1] if step > 0 else stage_projections[i]
                total += densities[i] * abs(boundary - cur)
                cur = boundary
                i += step
            total += densities[idx_new] * abs(v_norm_new - cur)
            return total * self.design_weights[axis_idx]

    def compute_total_warp(self, var_deltas: dict[str, float]) -> np.ndarray:
        """Compute full warp vector Δt from all variable deltas."""
        if self.Q is None:
            raise RuntimeError("Subspace not built")

        dt = np.zeros(self.subspace_k, dtype=np.float64)
        for i, name in enumerate(self.axis_names):
            if name in var_deltas:
                v_old = self.var_currents.get(name, 0.0)
                v_new = v_old + var_deltas[name]
                t_i = self.compute_warp_delta(i, v_old, v_new)
                if i < self.A.shape[1]:
                    # Project axis direction into subspace
                    axis_sub = self.Q.T @ self.A[:, i]
                    axis_sub_norm = np.linalg.norm(axis_sub) or 1.0
                    dt += t_i * axis_sub / axis_sub_norm
        return dt

    # ═══════════════════════════════════════════════════
    # 21.3.5  Semantic field synthesis
    # ═══════════════════════════════════════════════════

    def synthesize_event(self, dt: np.ndarray, event_direction: np.ndarray | None = None) -> np.ndarray:
        """Combine warp delta with event direction into perpendicular movement.
        d_perp = Normalize(d_raw - (d_raw·p)·p)
        """
        if self.semantic_p is None:
            return dt

        p = self.semantic_p
        dt_norm = np.linalg.norm(dt)
        if dt_norm < 1e-6:
            return np.zeros_like(dt)

        if event_direction is not None:
            d_raw = event_direction
        else:
            d_raw = dt / dt_norm

        # Remove component parallel to current state
        proj = np.dot(d_raw, p) * p
        d_perp = d_raw - proj
        perp_norm = np.linalg.norm(d_perp)
        if perp_norm < 1e-6:
            return np.zeros_like(dt)

        d_perp /= perp_norm
        return dt_norm * d_perp

    def combine_events(self, events: list[np.ndarray]) -> np.ndarray:
        """v_raw = Σ δ_i"""
        if not events:
            return np.zeros(self.subspace_k if self.semantic_p is not None else 0, dtype=np.float64)
        raw = np.sum(events, axis=0)
        # Project onto perpendicular space
        if self.semantic_p is not None:
            proj = np.dot(raw, self.semantic_p) * self.semantic_p
            raw -= proj
        return raw

    # ═══════════════════════════════════════════════════
    # 21.3.6  State update via SLERP
    # ═══════════════════════════════════════════════════

    def update_state(self, v_raw: np.ndarray) -> dict:
        """Update semantic state point (p, r) from raw movement vector.
        Returns debug info about the update.
        """
        if self.semantic_p is None:
            self.semantic_p = np.zeros(self.subspace_k, dtype=np.float64)
            self.semantic_p[0] = 1.0  # arbitrary start direction

        theta = float(np.linalg.norm(v_raw))
        info = {"theta": theta, "r_before": self.semantic_r}

        if theta < 1e-8:
            return info

        d_perp = v_raw / theta
        p = self.semantic_p

        # Determine if SLERP (large step) or linear interpolation
        SLERP_THRESHOLD = 0.3  # radians
        if theta > SLERP_THRESHOLD:
            # SLERP for large steps
            cos_theta = np.dot(p, d_perp)
            cos_theta = max(-1.0, min(1.0, cos_theta))
            target = p + d_perp
            target_norm = np.linalg.norm(target) or 1.0
            target /= target_norm

            angle = math.acos(cos_theta)
            if angle < 1e-8:
                p_new = p.copy()
            else:
                t = theta  # semantic_warp(v) maps to interpolation fraction
                t = max(0, min(1, t / math.pi))
                sin_a = math.sin(angle)
                p_new = (math.sin((1-t)*angle)/sin_a) * p + (math.sin(t*angle)/sin_a) * target
        else:
            # Cosine interpolation for small steps
            p_new = p * math.cos(theta) + d_perp * math.sin(theta)

        # Normalize
        p_new_norm = np.linalg.norm(p_new) or 1.0
        self.semantic_p = p_new / p_new_norm

        # Update intensity
        self.semantic_r = self._update_magnitude(self.semantic_r, v_raw)

        info["r_after"] = self.semantic_r
        info["p_norm"] = float(p_new_norm)
        return info

    def _update_magnitude(self, r: float, v_raw: np.ndarray) -> float:
        """Update intensity based on movement magnitude."""
        movement = float(np.linalg.norm(v_raw))
        if movement < 0.01:
            return r
        # Small damping towards 1.0 with drift from movement
        return r * 0.98 + movement * 0.02

    # ═══════════════════════════════════════════════════
    # 21.3.7  Semantic momentum
    # ═══════════════════════════════════════════════════

    def update_momentum(self, v_raw: np.ndarray):
        """v_semantic(t) = α·v_semantic(t-1) + v_raw"""
        if self.semantic_momentum is None:
            self.semantic_momentum = np.zeros_like(v_raw)

        self.semantic_momentum = self.momentum_decay * self.semantic_momentum + v_raw

        # Remove component along current state direction
        if self.semantic_p is not None:
            proj = np.dot(self.semantic_momentum, self.semantic_p) * self.semantic_p
            self.semantic_momentum -= proj

    def get_momentum_vector(self) -> np.ndarray:
        if self.semantic_momentum is None:
            return np.zeros(self.subspace_k, dtype=np.float64)
        return self.semantic_momentum.copy()

    # ═══════════════════════════════════════════════════
    # 21.6.2  Character semantic config loading
    # ═══════════════════════════════════════════════════

    def load_from_character(self, char_path: str):
        """Load axes and warp config from character_semantic.json."""
        config_path = os.path.join(char_path, "character_semantic.json")
        if not os.path.exists(config_path):
            return  # No semantic config, engine stays in direct mode

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for var_name, var_cfg in config.get("variables", {}).items():
            lo, hi = var_cfg.get("range", [-100, 100])
            self.set_var_range(var_name, float(lo), float(hi))

            sc = var_cfg.get("semantic_config", {})
            if sc:
                self.register_axis(
                    name=var_name,
                    positive_anchor=sc.get("axis_positive", f"extremely high {var_name}"),
                    negative_anchor=sc.get("axis_negative", f"extremely low {var_name}"),
                    design_weight=float(sc.get("design_weight", 1.0)),
                    warp_stages=sc.get("warp_stages", []),
                )

    def set_embed_fn(self, fn):
        """Set the embedding function. fn(texts: list[str]) -> list[list[float]]"""
        self._embed_fn = fn

    def is_ready(self) -> bool:
        return self.Q is not None and self._embed_fn is not None

    # ── Serialization ──

    def save_state(self) -> dict:
        return {
            "semantic_p": self.semantic_p.tolist() if self.semantic_p is not None else None,
            "semantic_r": self.semantic_r,
            "semantic_momentum": self.semantic_momentum.tolist() if self.semantic_momentum is not None else None,
        }

    def load_state(self, data: dict):
        if data.get("semantic_p"):
            self.semantic_p = np.array(data["semantic_p"], dtype=np.float64)
        self.semantic_r = float(data.get("semantic_r", 1.0))
        if data.get("semantic_momentum"):
            self.semantic_momentum = np.array(data["semantic_momentum"], dtype=np.float64)
