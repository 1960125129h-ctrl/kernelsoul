"""
Kernelsoul - Semantic Renderer (v2.4, Chapter 21.4)
Rendering pipeline: Fact labels → KNN retrieval → ContextPacket → LLM generation.

Sits between rule execution and prompt construction.
"""
from __future__ import annotations
import json, os
from typing import Optional
import numpy as np


class SemanticRenderer:
    """Orchestrates the semantic rendering pipeline.

    Three modes (21.6.3):
      direct   - Numeric values inlined into prompt (current v2.3 behavior).
      semantic - Full semantic rendering via embedding subspace pipeline.
      hybrid   - State-rich dimensions use semantic, others use direct.
    """

    MODES = ("direct", "semantic", "hybrid")

    def __init__(self, semantic_engine, phrase_library=None, render_mode: str = "direct"):
        self.engine = semantic_engine
        self.phrases = phrase_library
        self.mode = render_mode

        # KNN / generation params
        self.knn_top_k = 5
        self.fallback_llm = True  # Use LLM when KNN fails

        # Records
        self.last_context_packet: Optional[dict] = None
        self.last_selected_phrases: list[str] = []

    # ═══════════════════════════════════════════════════
    # Main entry point
    # ═══════════════════════════════════════════════════

    def render(self, state_deltas: dict[str, float],
               current_state,  # GameState
               last_narrative: str = "",
               ) -> dict:
        """Main rendering pipeline.
        Returns ContextPacket dict for prompt construction.
        """
        if self.mode == "direct":
            return self._render_direct(state_deltas, current_state)

        # ── Semantic / hybrid path ──
        if not self.engine.is_ready():
            # Fallback to direct if engine not built
            return self._render_direct(state_deltas, current_state)

        # 1. Compute warp delta
        dt = self.engine.compute_total_warp(state_deltas)

        # 2. Synthesize events and combine
        event = self.engine.synthesize_event(dt)
        v_raw = self.engine.combine_events([event])

        # 3. Update semantic state
        update_info = self.engine.update_state(v_raw)
        self.engine.update_momentum(v_raw)

        # 4. Update variable currents
        for name, delta in state_deltas.items():
            old = self.engine.var_currents.get(name, 0)
            self.engine.var_currents[name] = old + delta

        # 5. Get current state in semantic coordinates
        current_coords = None
        if self.engine.semantic_p is not None:
            current_coords = self.engine.semantic_p * self.engine.semantic_r

        # 6. KNN phrase retrieval
        selected_phrases = []
        knn_detail = {}
        if self.phrases and current_coords is not None:
            momentum = self.engine.get_momentum_vector()
            results = self.phrases.knn_search(
                target_coords=current_coords,
                momentum_vec=momentum,
                top_k=self.knn_top_k,
                semantic_engine=self.engine,
            )

            if results:
                for idx, score, detail in results:
                    phrase = self.phrases.phrases[idx]
                    selected_phrases.append(phrase["text"])
                knn_detail = {
                    "found": len(results),
                    "top_score": float(results[0][1]) if results else 0,
                }
                self.last_selected_phrases = selected_phrases
            else:
                # Record miss
                self.phrases.record_miss(
                    state_coords=current_coords,
                    reason="no_matches" if not self.phrases.phrases else "all_conflict"
                )

        # 7. Build ContextPacket
        packet = self._build_context_packet(
            state_deltas=state_deltas,
            current_state=current_state,
            update_info=update_info,
            selected_phrases=selected_phrases,
            knn_detail=knn_detail,
            last_narrative=last_narrative,
        )
        self.last_context_packet = packet
        return packet

    def _render_direct(self, state_deltas: dict, state) -> dict:
        """Direct mode: pass numeric values through (v2.3 behavior)."""
        lines = []
        for k, v in state_deltas.items():
            lines.append(f"{k}: {v:+d}" if isinstance(v, (int, float)) and v == int(v) else f"{k}: {v}")

        return {
            "mode": "direct",
            "narrative_hints": [],
            "state_summary": "; ".join(lines) if lines else "no changes",
            "needs_llm": False,
        }

    def _build_context_packet(self, state_deltas: dict, current_state,
                               update_info: dict, selected_phrases: list[str],
                               knn_detail: dict, last_narrative: str) -> dict:
        """Build the ContextPacket for prompt assembly (21.4.3).

        In semantic/hybrid mode, this replaces numeric inlining with
        semantically-selected narrative hints.
        """
        # Build human-readable state description
        state_desc = {}
        for name in self.engine.axis_names:
            val = self.engine.var_currents.get(name, "unknown")
            # Map value to description using axis extremes
            lo, hi = self.engine.var_ranges.get(name, (-100, 100))
            pct = (val - lo) / max(hi - lo, 1) * 100
            if pct > 75:
                desc = f"偏高（{val}）"
            elif pct < 25:
                desc = f"偏低（{val}）"
            else:
                desc = f"中等（{val}）"
            state_desc[name] = desc

        # Build change direction hints
        change_hints = {}
        for name, delta in state_deltas.items():
            if delta > 0:
                change_hints[name] = "上升"
            elif delta < 0:
                change_hints[name] = "下降"
            else:
                change_hints[name] = "不变"

        # Build prohibition list from momentum extremes
        prohibitions = []
        if self.engine.semantic_momentum is not None:
            mom_norm = np.linalg.norm(self.engine.semantic_momentum)
            if mom_norm > 0.5:
                prohibitions.append("避免状态剧烈波动")
            for i, name in enumerate(self.engine.axis_names):
                if i < len(self.engine.semantic_momentum):
                    val = float(self.engine.semantic_momentum[i])
                    if abs(val) > 0.3:
                        direction = "过度上升" if val > 0 else "过度下降"
                        lo, hi = self.engine.var_ranges.get(name, (-100, 100))
                        extremes = f"({lo}~{hi})"
                        prohibitions.append(f"避免{name}在{direction}范围{extremes}内偏离")

        return {
            "mode": self.mode,
            "current_state": state_desc,
            "change_direction": change_hints,
            "last_narrative": last_narrative[:200] if last_narrative else "",
            "selected_phrases": selected_phrases,
            "prohibitions": prohibitions,
            "knn_detail": knn_detail,
            "update_info": update_info,
            "needs_llm": not selected_phrases and self.fallback_llm,
        }

    def build_prompt_hint(self, context_packet: dict) -> str:
        """Convert ContextPacket into a prompt-insertable text block."""
        if context_packet.get("mode") == "direct":
            return f"[状态变化: {context_packet['state_summary']}]"

        parts = ["[语义渲染状态]"]

        # State snapshot
        state_items = []
        for k, v in context_packet.get("current_state", {}).items():
            state_items.append(f"  {k}: {v}")
        if state_items:
            parts.append("状态概览:\n" + "\n".join(state_items))

        # Selected phrases
        phrases = context_packet.get("selected_phrases", [])
        if phrases:
            parts.append("叙事提示:")
            for p in phrases[:3]:
                parts.append(f"  → {p}")

        # Prohibitions
        proh = context_packet.get("prohibitions", [])
        if proh:
            parts.append("边界约束:")
            for p in proh:
                parts.append(f"  ⚠ {p}")

        # Change direction
        changes = context_packet.get("change_direction", {})
        if changes:
            change_str = ", ".join(f"{k}{v}" for k, v in changes.items())
            parts.append(f"变化趋势: {change_str}")

        return "\n".join(parts)

    # ═══════════════════════════════════════════════════
    # 21.6.3  Render mode switching
    # ═══════════════════════════════════════════════════

    def switch_mode(self, mode: str) -> bool:
        if mode not in self.MODES:
            return False
        self.mode = mode
        return True

    def get_mode(self) -> str:
        return self.mode
