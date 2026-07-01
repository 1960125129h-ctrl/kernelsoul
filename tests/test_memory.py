"""
test_memory.py - MemoryManager unit + integration tests (fixed)
Mock standardization, round logic fix, assertion hardening.
"""
import json, os, shutil, sys, tempfile, unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))
from path_resolver import PathResolver
from memory_manager import MemoryManager


class TestMemoryManager(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "configs"), exist_ok=True)
        for fname, tmpl in [("compression_prompt_light.txt", "Light template:\n{chat_history}\n\nSummary:"),
                           ("compression_prompt_deep.txt", "Deep template:\n{chat_history}\n\nDeep summary:")]:
            with open(os.path.join(self.tmp, "configs", fname), "w", encoding="utf-8") as f:
                f.write(tmpl)
        self.pr = PathResolver(self.tmp, "test_char", "test_session")
        self.ai = MagicMock()
        self.ai.generate = MagicMock(return_value="Mock summary of the conversation.")
        self.mm = MemoryManager(self.pr, self.ai)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_light_template(self):
        self.assertIn("Light template", self.mm.light_template)
    def test_load_deep_template(self):
        self.assertIn("Deep template", self.mm.deep_template)

    def test_full_memory_read_write(self):
        entry = {"compression_id": 1, "type": "light", "round_range": "1-10", "summary": "Test summary", "timestamp": "t"}
        self.mm._append_to_full_memory(entry)
        data = self.mm._load_full_memory()
        self.assertEqual(len(data["entries"]), 1)
        self.assertEqual(data["entries"][0]["compression_id"], 1)
        self.assertEqual(data["entries"][0]["type"], "light")

    def test_full_memory_id_increment(self):
        for i in range(2):
            rng = f'{i*10+1}-{(i+1)*10}'
            self.mm._append_to_full_memory({"compression_id": i+1, "type": "light", "round_range": rng, "summary": f's{i}', "timestamp": "t"})
        data = self.mm._load_full_memory()
        self.assertEqual(len(data["entries"]), 2)
        self.assertEqual(data["entries"][1]["compression_id"], 2)

    def test_working_memory_rebuild(self):
        for i in range(5):
            rng = f'{i*10+1}-{(i+1)*10}'
            self.mm._append_to_full_memory({"compression_id": i+1, "type": "light", "round_range": rng, "summary": f'L{i+1}', "timestamp": "t"})
        self.mm._append_to_full_memory({"compression_id": 6, "type": "deep", "round_range": "1-50", "summary": "Deep", "timestamp": "t"})
        self.mm._rebuild_working_memory()
        with open(self.pr.get_working_memory(), "r", encoding="utf-8") as f:
            wm = json.load(f)
        self.assertEqual(len(wm["deep_summaries"]), 1)
        self.assertEqual(len(wm["light_summaries"]), 3)

    def test_working_memory_empty(self):
        self.mm._rebuild_working_memory()
        with open(self.pr.get_working_memory(), "r", encoding="utf-8") as f:
            wm = json.load(f)
        self.assertEqual(len(wm["deep_summaries"]), 0)
        self.assertEqual(len(wm["light_summaries"]), 0)

    def test_get_context_summaries(self):
        self.mm._append_to_full_memory({"compression_id": 1, "type": "deep", "round_range": "1-50", "summary": "Epic adventure story.", "timestamp": "t"})
        self.mm._append_to_full_memory({"compression_id": 2, "type": "light", "round_range": "41-50", "summary": "Recent events.", "timestamp": "t"})
        self.mm._rebuild_working_memory()
        text = self.mm.get_context_summaries()
        self.assertIn("Epic adventure story", text)
        self.assertIn("Recent events", text)
        self.assertIn("Deep Summary", text)

    def test_get_last_deep_round_empty(self):
        self.assertEqual(self.mm._get_last_deep_round(), -1)

    def test_get_last_deep_round_after_compress(self):
        self.mm._append_to_full_memory({"compression_id": 1, "type": "deep", "round_range": "1-50", "summary": "Deep", "timestamp": "t"})
        self.assertEqual(self.mm._get_last_deep_round(), 50)

    def test_get_recent_rounds_count(self):
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(10):
                f.write(f'PLAYER: round {i}\nAI: reply {i}\n')
        text = self.mm._get_recent_rounds(3)
        self.assertIn("round 7", text)
        self.assertIn("round 9", text)
        self.assertNotIn("round 0", text)

    def test_get_rounds_from_inclusive(self):
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(10):
                f.write(f'PLAYER: r{i}\nAI: r{i}\n')
        text = self.mm._get_rounds_from(7)
        self.assertIn("r7", text)
        self.assertIn("r9", text)
        self.assertNotIn("r6", text)
        self.assertNotIn("r0", text)

    def test_get_rounds_from_start(self):
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(5):
                f.write(f'PLAYER: r{i}\nAI: r{i}\n')
        text = self.mm._get_rounds_from(0)
        self.assertIn("r0", text)
        self.assertIn("r4", text)

    def test_get_rounds_from_beyond(self):
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            f.write("PLAYER: r0\nAI: r0\n")
        text = self.mm._get_rounds_from(10)
        self.assertEqual(text, "")

    def test_no_compress_before_threshold(self):
        self.mm.maybe_compress(3)
        self.ai.generate.assert_not_called()

    def test_light_compress_trigger_at_10(self):
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(20):
                f.write(f'PLAYER: msg {i}\nAI: reply {i}\n')
        self.mm.maybe_compress(10)
        self.ai.generate.assert_called_once()
        call_args = self.ai.generate.call_args[0]
        self.assertIn("Light template", call_args[1])
        data = self.mm._load_full_memory()
        self.assertEqual(len(data["entries"]), 1)
        self.assertEqual(data["entries"][0]["type"], "light")
        self.assertEqual(data["entries"][0]["round_range"], "1-10")

    def test_both_compress_at_50(self):
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(100):
                f.write(f'PLAYER: msg {i}\nAI: reply {i}\n')
        self.mm.maybe_compress(50)
        self.assertGreaterEqual(self.ai.generate.call_count, 2)
        data = self.mm._load_full_memory()
        types = {e["type"] for e in data["entries"]}
        self.assertIn("light", types)
        self.assertIn("deep", types)

    def test_add_manual_memory(self):
        self.mm.add_manual_memory("Important: the key is under the rug.")
        memories = self.mm.get_manual_memories()
        self.assertEqual(len(memories), 1)
        self.assertIn("key is under", memories[0]["content"])

    def test_multiple_manual_memories(self):
        for m in ["Memory 1", "Memory 2", "Memory 3"]:
            self.mm.add_manual_memory(m)
        self.assertEqual(len(self.mm.get_manual_memories()), 3)

    def test_manual_memory_has_timestamp(self):
        self.mm.add_manual_memory("Test memory")
        memories = self.mm.get_manual_memories()
        self.assertIn("timestamp", memories[0])
        self.assertIn("content", memories[0])


    # -- Deep compression: merge mode vs fallback --
    def test_deep_compress_merge_mode(self):
        merge_path = os.path.join(self.tmp, 'configs', 'compression_prompt_merge.txt')
        with open(merge_path, "w", encoding="utf-8") as f:
            f.write("Merge: {combined_summaries}")
        self.mm = MemoryManager(self.pr, self.ai)
        for i in range(5):
            rng = f'{i*10+1}-{(i+1)*10}'
            self.mm._append_to_full_memory({"compression_id": i+1, "type": "light", "round_range": rng, "summary": f'L{i+1}', "timestamp": "t"})
        self.mm.maybe_compress(50)
        call_args = self.ai.generate.call_args[0]
        self.assertIn("Merge", call_args[0])
        data = self.mm._load_full_memory()
        deeps = [e for e in data["entries"] if e["type"] == "deep"]
        self.assertGreaterEqual(len(deeps), 1)

    def test_deep_compress_fallback_to_raw(self):
        self.mm._append_to_full_memory({"compression_id": 1, "type": "light", "round_range": "1-10", "summary": "Only light", "timestamp": "t"})
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(100):
                f.write(f'PLAYER: msg {i}\nAI: reply {i}\n')
        self.mm.maybe_compress(50)
        self.ai.generate.assert_called()
        data = self.mm._load_full_memory()
        deeps = [e for e in data["entries"] if e["type"] == "deep"]
        self.assertGreaterEqual(len(deeps), 1)

    def test_safe_truncate_no_truncation(self):
        text = "Short text."
        result = self.mm._safe_truncate(text, 100)
        self.assertEqual(result, "Short text.")

    def test_safe_truncate_at_sentence_boundary(self):
        text = "First sentence.Second sentence.Third sentence."
        result = self.mm._safe_truncate(text, 30)
        self.assertTrue(result.endswith("."), f'Should end with period: {repr(result)}')

    def test_safe_truncate_hard_cut(self):
        text = "No punctuation at all in this very long text that should be cut"
        result = self.mm._safe_truncate(text, 10)
        self.assertEqual(len(result), 10)

    def test_epic_compress_with_deep_entries(self):
        with open(os.path.join(self.tmp, "configs", "compression_prompt_epic.txt"), "w", encoding="utf-8") as f:
            f.write("Epic: {combined_deep_summaries}")
        with open(os.path.join(self.tmp, "configs", "compression_prompt_merge.txt"), "w", encoding="utf-8") as f:
            f.write("Merge: {combined_summaries}")
        self.mm = MemoryManager(self.pr, self.ai)
        for i in range(4):
            rng = f'{i*50+1}-{(i+1)*50}'
            self.mm._append_to_full_memory({"compression_id": i+1, "type": "deep", "round_range": rng, "summary": f'D{i+1}', "timestamp": "t"})
        self.mm.maybe_compress(200)
        data = self.mm._load_full_memory()
        epics = [e for e in data["entries"] if e["type"] == "epic"]
        self.assertGreaterEqual(len(epics), 1)
        self.assertLessEqual(len(epics[-1]["summary"]), 5500)

    def test_working_memory_three_layer_structure(self):
        self.mm._append_to_full_memory({"compression_id": 1, "type": "epic", "round_range": "1-200", "summary": "Epic story", "timestamp": "t"})
        self.mm._append_to_full_memory({"compression_id": 2, "type": "deep", "round_range": "151-200", "summary": "Deep story", "timestamp": "t"})
        self.mm._append_to_full_memory({"compression_id": 3, "type": "light", "round_range": "191-200", "summary": "Light story", "timestamp": "t"})
        self.mm._rebuild_working_memory()
        with open(self.pr.get_working_memory(), "r", encoding="utf-8") as f:
            wm = json.load(f)
        self.assertIsNotNone(wm.get("epic_summary"))
        self.assertGreaterEqual(len(wm.get("deep_summaries", [])), 1)
        self.assertGreaterEqual(len(wm.get("light_summaries", [])), 1)

    def test_epic_interval_not_triggered_at_100(self):
        with open(os.path.join(self.tmp, "configs", "compression_prompt_epic.txt"), "w", encoding="utf-8") as f:
            f.write("Epic: {combined_deep_summaries}")
        with open(os.path.join(self.tmp, "configs", "compression_prompt_merge.txt"), "w", encoding="utf-8") as f:
            f.write("Merge: {combined_summaries}")
        self.mm = MemoryManager(self.pr, self.ai)
        with open(self.pr.get_full_log(), "w", encoding="utf-8") as f:
            for i in range(200):
                f.write(f'PLAYER: r{i}\nAI: r{i}\n')
        self.mm.maybe_compress(100)
        data = self.mm._load_full_memory()
        epics = [e for e in data["entries"] if e["type"] == "epic"]
        self.assertEqual(len(epics), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
