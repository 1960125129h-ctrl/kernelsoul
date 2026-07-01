"""
Kernelsoul - DraftManager
Manages saved drafts that persist across sessions, stored as JSON files
in saves/{char}/{session}/context/saved_drafts/ per the manual v1.6 spec.
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


class DraftManager:
    """Persisted draft manager.

    Saves drafts as JSON files (saved_001.json, saved_002.json, ...) in the
    saved_drafts directory. Unlike regular in-memory drafts that get cleared
    per session, saved drafts persist and are manually managed by the user.

    Each saved draft stores:
      - Full narrative text
      - State changes dict
      - HP before/after
      - Parse method
      - Timestamp (UTC ISO)
      - Optional user label
      - Character and session identifiers
    """

    def __init__(self, saved_drafts_dir: str):
        self.dir = saved_drafts_dir
        os.makedirs(self.dir, exist_ok=True)

    # -- Internal helpers --

    def _next_id(self) -> int:
        """Find the next available sequential draft ID."""
        existing = self.list_saved_drafts()
        if not existing:
            return 1
        return max(d['draft_id'] for d in existing) + 1

    def _path(self, draft_id: int) -> str:
        """Get the file path for a saved draft by ID."""
        return os.path.join(self.dir, f'saved_{draft_id:03d}.json')

    # -- Public API --

    def save_draft(
        self,
        narrative: str,
        state_changes: dict,
        hp_before: int = 0,
        hp_after: int = 0,
        parse_method: str = '',
        label: str = '',
        char: str = '',
        session: str = '',
    ) -> int:
        """Save a draft to persistent storage. Returns the assigned draft_id."""
        draft_id = self._next_id()
        data = {
            'draft_id': draft_id,
            'narrative': narrative,
            'state_changes': state_changes,
            'hp_before': hp_before,
            'hp_after': hp_after,
            'parse_method': parse_method,
            'label': label,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'char': char,
            'session': session,
        }
        path = self._path(draft_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return draft_id

    def list_saved_drafts(self) -> List[Dict[str, Any]]:
        """List all saved drafts with metadata summaries."""
        results = []
        if not os.path.isdir(self.dir):
            return results
        for fname in sorted(os.listdir(self.dir)):
            if not fname.startswith('saved_') or not fname.endswith('.json'):
                continue
            fpath = os.path.join(self.dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                results.append({
                    'draft_id': data.get('draft_id', 0),
                    'label': data.get('label', ''),
                    'timestamp': data.get('timestamp', ''),
                    'narrative_preview': data.get('narrative', '')[:80],
                    'hp_before': data.get('hp_before', 0),
                    'hp_after': data.get('hp_after', 0),
                    'char': data.get('char', ''),
                    'session': data.get('session', ''),
                })
            except (json.JSONDecodeError, KeyError, OSError):
                pass
        return sorted(results, key=lambda d: d['draft_id'])

    def load_saved_draft(self, draft_id: int) -> Optional[Dict[str, Any]]:
        """Load the complete data of a saved draft. Returns None if not found."""
        fpath = self._path(draft_id)
        if not os.path.exists(fpath):
            return None
        try:
            with open(fpath, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def delete_saved_draft(self, draft_id: int) -> bool:
        """Delete a saved draft by ID. Returns True if deleted, False if not found."""
        fpath = self._path(draft_id)
        if os.path.exists(fpath):
            os.remove(fpath)
            return True
        return False

    def count(self) -> int:
        """Return the number of saved drafts."""
        return len(self.list_saved_drafts())
