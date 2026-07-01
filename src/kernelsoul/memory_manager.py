"""
Kernelsoul - MemoryManager v2.0
3-layer hierarchical compression: light -> deep -> epic
Dual-track logging + safe truncation + merge fallback
"""

import json, os
from datetime import datetime, timezone


class MemoryManager:
    # Intervals
    LIGHT_INTERVAL = 10
    DEEP_INTERVAL = 50
    EPIC_INTERVAL = 200
    # Limits
    LIGHT_MAX_CHARS = 200
    DEEP_MAX_CHARS = 2500
    EPIC_MAX_CHARS = 5000
    # Working memory counts
    WORKING_LIGHT_COUNT = 3
    WORKING_DEEP_COUNT = 1
    WORKING_EPIC_COUNT = 1

    def __init__(self, paths, ai_bridge):
        self.paths = paths
        self.ai = ai_bridge
        self.round_count = 0
        self.light_template = self._load_template(self.paths.get_compression_prompt_light())
        self.deep_template = self._load_template(self.paths.get_compression_prompt_deep())
        self.merge_template = self._load_template_optional("compression_prompt_merge.txt")
        self.epic_template = self._load_template_optional("compression_prompt_epic.txt")

    def _load_template(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                return f.read()
        return "{chat_history}"

    def _load_template_optional(self, filename: str) -> str:
        p = os.path.join(self.paths.base_configs, filename)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8-sig") as f:
                return f.read()
        return None

    # -- Trigger --
    def maybe_compress(self, round_num: int):
        self.round_count = round_num
        if self.round_count > 0 and self.round_count % self.LIGHT_INTERVAL == 0:
            self._do_light_compress()
        if self.round_count > 0 and self.round_count % self.DEEP_INTERVAL == 0:
            self._do_deep_compress()
        if self.round_count > 0 and self.round_count % self.EPIC_INTERVAL == 0:
            self._do_epic_compress()

    # -- Light compression --
    def _do_light_compress(self):
        recent = self._get_recent_rounds(self.LIGHT_INTERVAL)
        if not recent.strip():
            return
        prompt = self.light_template.replace("{chat_history}", recent)
        summary = self.ai.generate("Summarize this game dialogue.", prompt)
        if summary.startswith("[ERROR]"):
            return
        summary = self._safe_truncate(summary, self.LIGHT_MAX_CHARS)
        entry = {
            "compression_id": self._next_compression_id(),
            "type": "light",
            "round_range": f"{self.round_count - self.LIGHT_INTERVAL + 1}-{self.round_count}",
            "summary": summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_to_full_memory(entry)
        self._rebuild_working_memory()

    # -- Deep compression (hierarchical merge) --
    def _do_deep_compress(self):
        full_memory = self._load_full_memory()
        last_deep = self._get_last_deep_round()
        light_entries = [
            e for e in full_memory.get("entries", [])
            if e.get("type") == "light"
            and int(e["round_range"].split("-")[0]) > last_deep
        ]
        if len(light_entries) >= 3 and self.merge_template:
            summary = self._merge_light_summaries(light_entries)
        else:
            summary = self._deep_compress_from_raw()
        if not summary or summary.startswith("[ERROR]"):
            return
        summary = self._safe_truncate(summary, self.DEEP_MAX_CHARS)
        start_round = last_deep + 2
        entry = {
            "compression_id": self._next_compression_id(),
            "type": "deep",
            "round_range": f"{start_round}-{self.round_count}",
            "summary": summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_to_full_memory(entry)
        self._rebuild_working_memory()

    def _merge_light_summaries(self, light_entries: list) -> str:
        combined = "\n\n".join([
            f"[Rounds {e['round_range']}] {e['summary']}"
            for e in light_entries
        ])
        prompt = self.merge_template.replace("{combined_summaries}", combined)
        return self.ai.generate("Merge these story segments.", prompt)

    def _deep_compress_from_raw(self) -> str:
        last_deep = self._get_last_deep_round()
        chat_text = self._get_rounds_from(last_deep + 1)
        if not chat_text.strip():
            return ""
        prompt = self.deep_template.replace("{chat_history}", chat_text)
        return self.ai.generate("Deep summarize this game history.", prompt)

    # -- Epic compression (200-round) --
    def _do_epic_compress(self):
        full_memory = self._load_full_memory()
        last_epic = self._get_last_epic_round()
        deep_entries = [
            e for e in full_memory.get("entries", [])
            if e.get("type") == "deep"
            and int(e["round_range"].split("-")[0]) > last_epic
        ]
        if len(deep_entries) >= 2 and self.epic_template:
            summary = self._merge_deep_summaries(deep_entries)
        else:
            light_entries = [
                e for e in full_memory.get("entries", [])
                if e.get("type") == "light"
                and int(e["round_range"].split("-")[0]) > last_epic
            ]
            if self.merge_template:
                summary = self._merge_light_summaries(light_entries)
            else:
                summary = self._deep_compress_from_raw()
        if not summary or summary.startswith("[ERROR]"):
            return
        summary = self._safe_truncate(summary, self.EPIC_MAX_CHARS)
        start_round = last_epic + 2
        entry = {
            "compression_id": self._next_compression_id(),
            "type": "epic",
            "round_range": f"{start_round}-{self.round_count}",
            "summary": summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_to_full_memory(entry)
        self._rebuild_working_memory()

    def _merge_deep_summaries(self, deep_entries: list) -> str:
        combined = "\n\n---\n\n".join([
            f"[Rounds {e['round_range']} deep summary]\n{e['summary']}"
            for e in deep_entries
        ])
        prompt = self.epic_template.replace("{combined_deep_summaries}", combined)
        return self.ai.generate("Compose epic story summary.", prompt)

    def _get_last_epic_round(self) -> int:
        data = self._load_full_memory()
        for entry in reversed(data.get("entries", [])):
            if entry.get("type") == "epic":
                rng = entry.get("round_range", "0-0")
                try:
                    return int(rng.split("-")[1])
                except (ValueError, IndexError):
                    pass
        return -1

    # -- Safe truncation --
    def _safe_truncate(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        # 常见中文标点 + 英文标点
        for punct in ["。", "，", "！", "？", ".", "!", "?", "\n"]:
            pos = text.rfind(punct, 0, max_chars + 1)
            if pos > max_chars * 0.8:
                return text[:pos + 1]
        return text[:max_chars]

    # -- Archive operations --
    def _append_to_full_memory(self, entry: dict):
        path = self.paths.get_full_memory()
        data = self._load_full_memory()
        data["entries"].append(entry)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_full_memory(self) -> dict:
        path = self.paths.get_full_memory()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        return {"data_version": 1, "entries": []}

    def _next_compression_id(self) -> int:
        data = self._load_full_memory()
        entries = data.get("entries", [])
        return max((e.get("compression_id", 0) for e in entries), default=0) + 1

    def _get_last_deep_round(self) -> int:
        data = self._load_full_memory()
        for entry in reversed(data.get("entries", [])):
            if entry.get("type") == "deep":
                rng = entry.get("round_range", "0-0")
                try:
                    return int(rng.split("-")[1])
                except (ValueError, IndexError):
                    pass
        return -1

    # -- Working memory (3-layer) --
    def _rebuild_working_memory(self):
        data = self._load_full_memory()
        entries = data.get("entries", [])
        epics = [e for e in entries if e.get("type") == "epic"]
        deeps = [e for e in entries if e.get("type") == "deep"]
        lights = [e for e in entries if e.get("type") == "light"]
        working = {
            "epic_summary": self._summarize_entry(epics[-1]) if epics else None,
            "deep_summaries": [
                self._summarize_entry(e)
                for e in deeps[-self.WORKING_DEEP_COUNT:]
            ],
            "light_summaries": [
                self._summarize_entry(e)
                for e in lights[-self.WORKING_LIGHT_COUNT:]
            ],
        }
        path = self.paths.get_working_memory()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(working, f, ensure_ascii=False, indent=2)

    def _summarize_entry(self, entry: dict) -> dict:
        return {
            "compression_id": entry["compression_id"],
            "round_range": entry["round_range"],
            "summary": entry["summary"],
        }

    def get_context_summaries(self) -> str:
        path = self.paths.get_working_memory()
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        parts = []
        if data.get("epic_summary"):
            parts.append("[Story Arc]\n" + data["epic_summary"]["summary"])
        for s in data.get("deep_summaries", []):
            parts.append(f"[Deep Summary rounds {s['round_range']}]\n{s['summary']}")
        for s in data.get("light_summaries", []):
            parts.append(f"[Light Summary rounds {s['round_range']}]\n{s['summary']}")
        return "\n\n".join(parts)

    # -- Log access (0-indexed rounds) --
    def _get_recent_rounds(self, n: int) -> str:
        path = self.paths.get_full_log()
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        recent = all_lines[-(n * 2):] if len(all_lines) >= n * 2 else all_lines
        return "".join(recent)

    def _get_rounds_from(self, start_round: int) -> str:
        path = self.paths.get_full_log()
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        start_line = start_round * 2
        if start_line >= len(all_lines):
            return ""
        return "".join(all_lines[start_line:])

    # -- Manual memory --
    def add_manual_memory(self, content: str):
        path = self.paths.get_manual_memory()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        entries = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                entries = json.load(f)
        entries.append({
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def get_manual_memories(self) -> list:
        path = self.paths.get_manual_memory()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        return []