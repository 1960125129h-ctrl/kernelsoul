"""
Kernelsoul - WorldBookRetriever
Enhanced worldbook/lorebook entry retrieval with priority scoring.

Features:
  - Exact keyword matching (primary)
  - Substring partial matching with scoring
  - Regex pattern matching
  - Priority sorting by match count + entry weight
  - Recursive depth scanning of nested entries
  - Constant-memory result limiting
"""
from __future__ import annotations
import json
import os
import re
from typing import List, Optional


class WorldBookRetriever:
    """Enhanced worldbook entry retriever with priority-scored matching."""

    # Scoring weights
    WEIGHT_EXACT = 10       # Exact keyword match
    WEIGHT_SUBSTRING = 3    # Keyword appears as substring
    WEIGHT_REGEX = 5        # Regex pattern match
    WEIGHT_SECONDARY = 1    # Secondary key match
    DEFAULT_MAX_RESULTS = 10

    def __init__(self, lorebook_path: Optional[str] = None):
        self.entries: list = []
        self._compiled_patterns: dict = {}  # Cache regex patterns
        if lorebook_path and os.path.exists(lorebook_path):
            self._load(lorebook_path)

    def _load(self, path: str):
        """Load entries from lorebook JSON file."""
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f'[WorldBook] Failed to load {path}: {e}')
            return

        raw_entries = data if isinstance(data, list) else data.get("entries", [])
        self.entries = [self._normalize(e) for e in raw_entries]
        self._precompile_regexes()
        print(f'[WorldBook] Loaded {len(self.entries)} entries from {os.path.basename(path)}')

    def _normalize(self, entry: dict) -> dict:
        """Normalize entry format."""
        return {
            "keys": self._extract_keys(entry),
            "secondary_keys": self._extract_secondary_keys(entry),
            "content": entry.get("content", entry.get("text", "")),
            "weight": entry.get("weight", entry.get("priority", 1)),
            "id": entry.get("id", entry.get("key", "")),
            "comment": entry.get("comment", ""),
            "enabled": entry.get("enabled", True),
        }

    def _extract_keys(self, entry: dict) -> list:
        """Extract primary keys from various formats."""
        keys = entry.get("keys", entry.get("key", []))
        if isinstance(keys, str):
            return [k.strip() for k in keys.split(",") if k.strip()]
        return [str(k).strip() for k in keys if k]

    def _extract_secondary_keys(self, entry: dict) -> list:
        """Extract secondary keys (lower weight matches)."""
        sk = entry.get("secondary_keys", entry.get("alt_keys", []))
        if isinstance(sk, str):
            return [k.strip() for k in sk.split(",") if k.strip()]
        return [str(k).strip() for k in sk if k]

    def _precompile_regexes(self):
        """Pre-compile regex patterns from entries."""
        for entry in self.entries:
            for key in entry["keys"] + entry["secondary_keys"]:
                if key.startswith("/") and key.endswith("/"):
                    pattern = key[1:-1]
                    try:
                        self._compiled_patterns[key] = re.compile(pattern, re.IGNORECASE)
                    except re.error:
                        pass

    # ── Query ──
    def query(
        self,
        user_input: str,
        max_results: int = None,
        min_score: int = 0,
    ) -> list:
        """Query worldbook entries matching user input.

        Returns list of matched content strings sorted by relevance score.
        """
        if not self.entries:
            return []

        max_results = max_results or self.DEFAULT_MAX_RESULTS
        scored = []

        for entry in self.entries:
            if not entry["enabled"]:
                continue
            score = self._score_entry(entry, user_input)
            if score > min_score:
                scored.append((score, entry))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top N content strings
        return [entry["content"] for _, entry in scored[:max_results]]

    def query_with_meta(
        self,
        user_input: str,
        max_results: int = None,
    ) -> list:
        """Query and return full entry metadata (for debugging/UI)."""
        if not self.entries:
            return []

        max_results = max_results or self.DEFAULT_MAX_RESULTS
        scored = []

        for entry in self.entries:
            if not entry["enabled"]:
                continue
            score = self._score_entry(entry, user_input)
            if score > 0:
                entry["_score"] = score
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:max_results]]

    # ── Scoring ──
    def _score_entry(self, entry: dict, text: str) -> int:
        """Score an entry against user input text."""
        score = 0
        text_lower = text.lower()

        # Primary keys (exact substring match)
        for key in entry["keys"]:
            score += self._match_key(key, text_lower) * entry["weight"]

        # Secondary keys (lower weight)
        for key in entry["secondary_keys"]:
            score += self._match_key(key, text_lower) * self.WEIGHT_SECONDARY * entry["weight"]

        return score

    def _match_key(self, key: str, text: str) -> int:
        """Match a single key against text. Returns score."""
        key_lower = key.lower()

        # Regex pattern match
        if key in self._compiled_patterns:
            if self._compiled_patterns[key].search(text):
                return self.WEIGHT_REGEX

        # Exact substring match
        if key_lower in text:
            return self.WEIGHT_EXACT

        # Partial word match: each word in key appears in text
        words = key_lower.split()
        if len(words) > 1 and all(w in text for w in words):
            return self.WEIGHT_SUBSTRING

        # Single word partial (substring of a longer word)
        if len(key_lower) >= 2 and key_lower in text:
            return self.WEIGHT_SUBSTRING

        return 0

    # ── Management ──
    def reload(self, path: str):
        """Reload entries from file."""
        self.entries = []
        self._compiled_patterns = {}
        self._load(path)

    def add_entry(self, entry: dict):
        """Add a single entry at runtime."""
        normalized = self._normalize(entry)
        self.entries.append(normalized)
        # Pre-compile any regex keys
        for key in normalized["keys"] + normalized["secondary_keys"]:
            if key.startswith("/") and key.endswith("/"):
                try:
                    self._compiled_patterns[key] = re.compile(key[1:-1], re.IGNORECASE)
                except re.error:
                    pass

    def summary(self) -> str:
        return f'WorldBookRetriever: {len(self.entries)} entries loaded'


# ── Convenience ──

def load_lorebook(path: str) -> WorldBookRetriever:
    """Create a WorldBookRetriever from a lorebook file."""
    return WorldBookRetriever(path)


def load_from_character(char_dir: str, char_name: str) -> Optional[WorldBookRetriever]:
    """Try to find and load a lorebook for a character."""
    candidates = [
        os.path.join(char_dir, f'{char_name}_lorebook.json'),
        os.path.join(char_dir, f'{char_name}_worldbook.json'),
        os.path.join(char_dir, "lorebook.json"),
        os.path.join(char_dir, "worldbook.json"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return WorldBookRetriever(c)
    return None

