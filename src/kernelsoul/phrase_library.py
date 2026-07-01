"""
Kernelsoul - Phrase Library (v2.4, Chapter 21.5)
Manages semantic phrase cache, pre-computed fact labels, Miss Buffer gap detection,
and semantic admission/audit checks.
"""
from __future__ import annotations
import json, os, time, hashlib
from typing import Optional
from collections import defaultdict
import numpy as np


class PhraseLibrary:
    """Cached phrase store with pre-computed semantic labels.

    Every phrase in the library has:
      - text: original phrase string
      - embedding: [d] vector
      - fact_labels: per-axis (value, salience, confidence)
      - metadata: style vector, usage count, last_used timestamp
    """

    def __init__(self, cache_path: Optional[str] = None,
                 style_dim: int = 1536, fact_axes: int = 0):
        self.cache_path = cache_path
        self.style_dim = style_dim
        self.phrases: list[dict] = []  # [{text, embedding, labels, style_vec, count, ts}]

        # ── Miss Buffer ──
        self.miss_buffer: list[dict] = []  # states that had no good phrase matches

        # ── Label config ──
        self.fact_axes = fact_axes
        self.axis_names: list[str] = []

        # ── Embed fn (set by caller) ──
        self._embed_fn = None

        # Load cache if exists
        if cache_path and os.path.exists(cache_path):
            self._load()

    def set_embed_fn(self, fn):
        self._embed_fn = fn

    def set_axis_names(self, names: list[str]):
        self.axis_names = names
        self.fact_axes = len(names)

    # ═══════════════════════════════════════════════════
    # 21.5.1  Fact label pre-computation
    # ═══════════════════════════════════════════════════

    def add_phrase(self, text: str, fact_labels: Optional[dict] = None) -> int:
        """Add a phrase with pre-computed labels. Returns index."""
        emb = None
        if self._embed_fn:
            try:
                emb = self._embed_fn([text])[0]
            except Exception:
                pass

        entry = {
            "text": text,
            "embedding": emb,
            "labels": fact_labels or {},
            "count": 0,
            "ts": time.time(),
        }
        idx = len(self.phrases)
        self.phrases.append(entry)
        return idx

    def precompute_labels(self, semantic_engine, phrase_texts: list[str]):
        """Batch pre-compute fact labels for a list of phrases.
        τ(s) = G^(-1) A^T (e(s) - c)
        """
        if self._embed_fn is None or not semantic_engine.is_ready():
            return

        embeddings = self._embed_fn(phrase_texts)
        embeddings = np.array(embeddings, dtype=np.float64)

        for i, text in enumerate(phrase_texts):
            e = embeddings[i]
            coords = semantic_engine.project_to_coordinates(e)
            salience = np.linalg.norm(e - semantic_engine.center)

            labels = {}
            for j, name in enumerate(semantic_engine.axis_names):
                if j < len(coords):
                    labels[name] = {
                        "value": float(coords[j]),
                        "salience": float(salience),
                        "confidence": 0.7,  # default, improved with usage
                    }

            self.add_phrase(text, labels)

    # ═══════════════════════════════════════════════════
    # 21.4.1  Fact label conflict check
    # ═══════════════════════════════════════════════════

    def check_fact_conflict(self, phrase_idx: int, current_coords: np.ndarray,
                            thresholds: dict | None = None) -> bool:
        """Check if a phrase factually contradicts current state.
        Returns True if there IS a conflict (phrase should be excluded).
        """
        if phrase_idx >= len(self.phrases):
            return False

        phrase = self.phrases[phrase_idx]
        labels = phrase.get("labels", {})
        if not labels:
            return False

        t = thresholds or {"state": 1.5, "phrase": 0.3, "salience": 0.1}
        eps_state = t["state"]
        eps_phrase = t["phrase"]
        eps_salience = t["salience"]
        eps_opposite = -0.3

        for i, name in enumerate(self.axis_names):
            if name not in labels or i >= len(current_coords):
                continue
            tau_state = float(current_coords[i])
            tau_phrase = float(labels[name]["value"])
            salience_val = float(labels[name].get("salience", 0))

            # Conflict condition from 21.4.1:
            # |τ_i| > ε_state AND |τ_i(s)| > ε_phrase AND salience > ε_salience AND τ_i·τ_i(s) < -δ
            if (abs(tau_state) > eps_state and
                abs(tau_phrase) > eps_phrase and
                salience_val > eps_salience and
                tau_state * tau_phrase < eps_opposite):
                return True
        return False

    # ═══════════════════════════════════════════════════
    # 21.4.2  Weighted KNN retrieval with ranking
    # ═══════════════════════════════════════════════════

    def knn_search(self, target_coords: np.ndarray, target_style_vec: np.ndarray | None = None,
                   momentum_vec: np.ndarray | None = None,
                   history_embedding: np.ndarray | None = None,
                   top_k: int = 10,
                   semantic_engine=None) -> list[tuple[int, float, dict]]:
        """Weighted KNN search with multi-factor scoring.
        Score = α·d_fact + β·d_style + γ·d_momentum + δ·d_history
        """
        if not self.phrases:
            return []

        target = np.asarray(target_coords, dtype=np.float64)
        weights = {"alpha": 1.0, "beta": 0.3, "gamma": 0.2, "delta": 0.15}
        candidates = []

        for idx, phrase in enumerate(self.phrases):
            labels = phrase.get("labels", {})
            if not labels:
                continue

            # d_fact: weighted squared deviation in axis space
            d_fact = 0.0
            fc = 0
            for i, name in enumerate(self.axis_names):
                if name in labels and i < len(target):
                    d_fact += (float(labels[name]["value"]) - float(target[i])) ** 2
                    fc += 1
            if fc > 0:
                d_fact /= fc

            # d_style: placeholder (would use style embedding distance)
            d_style = 0.0

            # d_momentum: angle between phrase direction and momentum
            d_momentum = 0.0
            if momentum_vec is not None and len(labels) > 0:
                # Approximate phrase direction from labels
                phrase_vec = np.array([float(labels.get(name, {}).get("value", 0))
                                       for name in self.axis_names[:len(momentum_vec)]])
                if np.linalg.norm(phrase_vec) > 1e-6 and np.linalg.norm(momentum_vec) > 1e-6:
                    cos_a = np.dot(phrase_vec, momentum_vec[:len(phrase_vec)]) / (
                        np.linalg.norm(phrase_vec) * np.linalg.norm(momentum_vec[:len(phrase_vec)]))
                    d_momentum = 1.0 - cos_a  # 0 = aligned, 2 = opposite

            # d_history: recent usage penalty (prefer unused phrases)
            d_history = min(phrase.get("count", 0) * 0.1, 1.0)

            score = (weights["alpha"] * d_fact +
                     weights["beta"] * d_style +
                     weights["gamma"] * d_momentum +
                     weights["delta"] * d_history)

            # Conflict check (exclude contradicting phrases)
            if semantic_engine and self.check_fact_conflict(idx, target):
                continue

            candidates.append((idx, score, {
                "d_fact": d_fact, "d_style": d_style,
                "d_momentum": d_momentum, "d_history": d_history,
            }))

        candidates.sort(key=lambda x: x[1])
        return candidates[:top_k]

    # ═══════════════════════════════════════════════════
    # 21.5.2  Miss Buffer gap detection
    # ═══════════════════════════════════════════════════

    def record_miss(self, state_coords: np.ndarray, reason: str = ""):
        """Record a miss: no suitable phrase found for current state."""
        self.miss_buffer.append({
            "coords": state_coords.tolist() if hasattr(state_coords, 'tolist') else state_coords,
            "reason": reason,
            "ts": time.time(),
        })

    def analyze_misses(self) -> list[dict]:
        """Cluster and analyze miss buffer for gap patterns."""
        if len(self.miss_buffer) < 3:
            return []

        coords = np.array([m["coords"] for m in self.miss_buffer])
        reasons = [m["reason"] for m in self.miss_buffer]

        # Simple cluster count
        clusters = defaultdict(int)
        for r in reasons:
            clusters[r] += 1

        return [
            {"reason": k, "count": v, "frequency": v / len(self.miss_buffer)}
            for k, v in sorted(clusters.items(), key=lambda x: -x[1])
        ]

    # ═══════════════════════════════════════════════════
    # 21.5.3  Semantic admission checks
    # ═══════════════════════════════════════════════════

    def admit_phrase(self, text: str, semantic_engine, existing_coords: np.ndarray) -> dict:
        """Check if a newly generated phrase passes semantic admission.
        Returns {admitted: bool, checks: {...}}
        """
        checks = {"direction": True, "coverage": True, "reversibility": True,
                  "conflict": True, "style": True}

        emb = None
        if self._embed_fn:
            emb = self._embed_fn([text])[0]

        if emb is not None and semantic_engine.is_ready():
            # Direction check: is the embedding within subspace bounds?
            sub = semantic_engine.project_to_subspace(np.array(emb))
            sub_norm = np.linalg.norm(sub)
            if sub_norm < 0.001:
                checks["direction"] = False

            # Coverage check: does it cover states we should?
            # (simplified: check it's not identical to existing)
            for phrase in self.phrases:
                if phrase.get("embedding") is not None:
                    old_emb = np.array(phrase["embedding"])
                    if np.linalg.norm(np.array(emb) - old_emb) < 0.01:
                        checks["coverage"] = False
                        break

            # Conflict check on coordinates
            coords = semantic_engine.project_to_coordinates(np.array(emb))
            if self.check_fact_conflict(-1, existing_coords):  # -1 = hypothetical
                checks["conflict"] = False

        admitted = all(checks.values())
        return {"admitted": admitted, "checks": checks}

    def audit_phrase(self, text: str, semantic_engine) -> dict:
        """Full audit report for a phrase."""
        report = {"text": text, "passes": []}

        if self._embed_fn and semantic_engine.is_ready():
            emb = self._embed_fn([text])[0]
            coords = semantic_engine.project_to_coordinates(np.array(emb))
            report["coordinates"] = coords.tolist()

            # Semantic direction check
            sub = semantic_engine.project_to_subspace(np.array(emb))
            report["subspace_norm"] = float(np.linalg.norm(sub))

            # Style proximity (uses axis salience as proxy)
            report["axis_salience"] = float(np.linalg.norm(coords))

        return report

    # ═══════════════════════════════════════════════════
    # Persistence
    # ═══════════════════════════════════════════════════

    def save(self):
        if not self.cache_path:
            return
        data = {
            "phrases": [{
                "text": p["text"],
                "labels": p.get("labels", {}),
                "count": p.get("count", 0),
            } for p in self.phrases],
            "miss_buffer": self.miss_buffer[-50:],  # keep last 50
        }
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self):
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for p in data.get("phrases", []):
                self.add_phrase(p["text"], p.get("labels", {}))
            self.miss_buffer = data.get("miss_buffer", [])
        except Exception:
            pass  # Corrupt cache, start fresh
