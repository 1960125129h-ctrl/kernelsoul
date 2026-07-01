"""
Tests for DraftManager (saved_drafts feature)
Covers: save, list, load, delete, edge cases, persistence
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft_manager import DraftManager


class TestDraftManager(unittest.TestCase):
    """Unit tests for DraftManager saved drafts functionality."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='test_saved_drafts_')
        self.dm = DraftManager(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # -- Test 1: save_draft creates a file and returns valid ID --

    def test_save_draft_creates_file(self):
        """Saving a draft should create a JSON file and return a sequential ID."""
        draft_id = self.dm.save_draft(
            narrative='The dragon awakens.',
            state_changes={'hp': -10},
            hp_before=100,
            hp_after=90,
            parse_method='regex',
            label='dragon scene',
        )
        self.assertEqual(draft_id, 1)

        filepath = os.path.join(self.tmpdir, 'saved_001.json')
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data['draft_id'], 1)
        self.assertEqual(data['narrative'], 'The dragon awakens.')
        self.assertEqual(data['state_changes'], {'hp': -10})
        self.assertEqual(data['hp_before'], 100)
        self.assertEqual(data['hp_after'], 90)
        self.assertEqual(data['parse_method'], 'regex')
        self.assertEqual(data['label'], 'dragon scene')
        self.assertIn('timestamp', data)

    # -- Test 2: list_saved_drafts returns metadata summaries --

    def test_list_saved_drafts(self):
        """List should return metadata for all saved drafts in order."""
        self.dm.save_draft(narrative='First story.', state_changes={}, hp_before=100, hp_after=100)
        self.dm.save_draft(narrative='Second story.', state_changes={}, hp_before=90, hp_after=80)

        drafts = self.dm.list_saved_drafts()
        self.assertEqual(len(drafts), 2)
        self.assertEqual(drafts[0]['draft_id'], 1)
        self.assertEqual(drafts[0]['narrative_preview'], 'First story.')
        self.assertEqual(drafts[1]['draft_id'], 2)
        self.assertEqual(drafts[1]['narrative_preview'], 'Second story.')

    # -- Test 3: load_saved_draft returns full data --

    def test_load_saved_draft(self):
        """Load should return the complete draft data."""
        self.dm.save_draft(
            narrative='The hero falls.',
            state_changes={'hp': -50, 'emotion': 'sad'},
            hp_before=50,
            hp_after=0,
            parse_method='json',
            label='tragedy',
            char='knight',
            session='session_abc',
        )
        data = self.dm.load_saved_draft(1)
        self.assertIsNotNone(data)
        self.assertEqual(data['narrative'], 'The hero falls.')
        self.assertEqual(data['state_changes'], {'hp': -50, 'emotion': 'sad'})
        self.assertEqual(data['hp_before'], 50)
        self.assertEqual(data['hp_after'], 0)
        self.assertEqual(data['label'], 'tragedy')
        self.assertEqual(data['char'], 'knight')
        self.assertEqual(data['session'], 'session_abc')

    # -- Test 4: load returns None for missing draft --

    def test_load_missing_draft(self):
        """Loading a non-existent draft should return None."""
        result = self.dm.load_saved_draft(999)
        self.assertIsNone(result)

    # -- Test 5: delete_saved_draft removes the file --

    def test_delete_saved_draft(self):
        """Delete should remove the file and return True."""
        self.dm.save_draft(narrative='Temp draft.', state_changes={}, hp_before=100, hp_after=100)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, 'saved_001.json')))

        result = self.dm.delete_saved_draft(1)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(os.path.join(self.tmpdir, 'saved_001.json')))

    # -- Test 6: delete returns False for missing draft --

    def test_delete_missing_draft(self):
        """Deleting a non-existent draft should return False."""
        result = self.dm.delete_saved_draft(42)
        self.assertFalse(result)

    # -- Test 7: count tracks number of saved drafts --

    def test_count(self):
        """Count should reflect the number of saved drafts."""
        self.assertEqual(self.dm.count(), 0)
        self.dm.save_draft(narrative='A.', state_changes={}, hp_before=100, hp_after=100)
        self.assertEqual(self.dm.count(), 1)
        self.dm.save_draft(narrative='B.', state_changes={}, hp_before=100, hp_after=100)
        self.assertEqual(self.dm.count(), 2)
        self.dm.delete_saved_draft(1)
        self.assertEqual(self.dm.count(), 1)

    # -- Test 8: _next_id works with gaps --

    def test_next_id_with_gaps(self):
        """Next ID should be max+1 even when earlier drafts are deleted."""
        self.dm.save_draft(narrative='1', state_changes={}, hp_before=100, hp_after=100)
        self.dm.save_draft(narrative='2', state_changes={}, hp_before=100, hp_after=100)
        self.dm.delete_saved_draft(1)

        next_id = self.dm._next_id()
        self.assertEqual(next_id, 3)  # max existing is 2, so next is 3

    # -- Test 9: list handles empty directory --

    def test_list_empty_directory(self):
        """List on empty directory returns empty list."""
        drafts = self.dm.list_saved_drafts()
        self.assertEqual(drafts, [])

    # -- Test 10: list filters non-draft files --

    def test_list_ignores_other_files(self):
        """List should ignore files that don't match saved_XXX.json pattern."""
        with open(os.path.join(self.tmpdir, 'something_else.json'), 'w') as f:
            json.dump({}, f)
        with open(os.path.join(self.tmpdir, 'saved_001.txt'), 'w') as f:
            f.write('not json')
        self.dm.save_draft(narrative='Real draft.', state_changes={}, hp_before=100, hp_after=100)
        drafts = self.dm.list_saved_drafts()
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]['draft_id'], 1)

    # -- Test 11: save without optional fields uses defaults --

    def test_save_minimal(self):
        """Saving with only narrative and state_changes should work with defaults."""
        draft_id = self.dm.save_draft(narrative='Minimal.', state_changes={})
        self.assertEqual(draft_id, 1)
        data = self.dm.load_saved_draft(1)
        self.assertEqual(data['hp_before'], 0)
        self.assertEqual(data['label'], '')
        self.assertIn('timestamp', data)

    # -- Test 12: load handles corrupt JSON gracefully --

    def test_load_corrupt_json(self):
        """Loading a corrupt JSON file should return None, not raise."""
        corrupt_path = os.path.join(self.tmpdir, 'saved_001.json')
        with open(corrupt_path, 'w', encoding='utf-8') as f:
            f.write('not valid json {{{')
        result = self.dm.load_saved_draft(1)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
