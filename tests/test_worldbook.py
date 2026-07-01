"""test_worldbook.py - WorldBookRetriever tests"""
import json, os, shutil, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))
from worldbook_retriever import WorldBookRetriever, load_lorebook, load_from_character


class TestWorldBookRetriever(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_lorebook(self, entries):
        p = os.path.join(self.tmp, "test_lorebook.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"entries": entries}, f)
        return p

    def test_empty_no_entries(self):
        wb = WorldBookRetriever()
        self.assertEqual(wb.query("anything"), [])

    def test_exact_keyword_match(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["sword", "blade"], "content": "A legendary blade."}
        ]))
        results = wb.query("I draw my sword")
        self.assertEqual(len(results), 1)
        self.assertIn("legendary", results[0])

    def test_no_match(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["dragon"], "content": "A fearsome dragon."}
        ]))
        results = wb.query("I walk through the forest")
        self.assertEqual(results, [])

    def test_multiple_matches_scored(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["sword"], "content": "Sword info."},
            {"keys": ["sword", "ancient"], "content": "Ancient sword lore."},
        ]))
        results = wb.query("I found an ancient sword in the ruins")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], "Ancient sword lore.")  # Higher score first

    def test_weight_boost(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["tavern"], "content": "Low priority", "weight": 1},
            {"keys": ["tavern"], "content": "High priority", "weight": 5},
        ]))
        results = wb.query("I enter the tavern")
        self.assertEqual(results[0], "High priority")

    def test_string_keys_format(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"key": "castle, fortress, keep", "content": "Stronghold info."}
        ]))
        results = wb.query("the old fortress stands tall")
        self.assertEqual(len(results), 1)

    def test_query_with_meta(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["forest"], "content": "Dark forest lore."}
        ]))
        results = wb.query_with_meta("dark forest")
        self.assertEqual(len(results), 1)
        self.assertIn("_score", results[0])
        self.assertGreater(results[0]["_score"], 0)

    def test_disabled_entry_skipped(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["secret"], "content": "Hidden secret.", "enabled": False}
        ]))
        self.assertEqual(wb.query("I found a secret"), [])

    def test_add_entry_runtime(self):
        wb = WorldBookRetriever()
        wb.add_entry({"keys": ["gold"], "content": "Golden treasure."})
        results = wb.query("gold coins")
        self.assertEqual(len(results), 1)

    def test_load_from_character(self):
        char_dir = os.path.join(self.tmp, "test_char")
        os.makedirs(char_dir)
        p = os.path.join(char_dir, "test_char_lorebook.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"entries": [{"keys": ["magic"], "content": "Magic info."}]}, f)
        wb = load_from_character(char_dir, "test_char")
        self.assertIsNotNone(wb)
        self.assertEqual(len(wb.query("magic")), 1)

    def test_substring_match(self):
        wb = WorldBookRetriever(self._make_lorebook([
            {"keys": ["dragon"], "content": "Dragon matched."}
        ]))
        results = wb.query("a dragon appears")
        self.assertEqual(len(results), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)

