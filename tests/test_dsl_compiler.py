"""
test_dsl_compiler.py - DSL Compiler tests
"""
import json, os, shutil, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))
from dsl_compiler import DSLCompiler, DSLCompileError


class TestDSLCompiler(unittest.TestCase):

    def test_basic_rule(self):
        src = "WHEN player_attacks\nIF hp < 50\nTHEN\n  SET emotion = angry\n"
        rules = DSLCompiler.compile(src)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["trigger"], "player_attacks")
        self.assertEqual(rules[0]["condition"]["type"], "lt")
        self.assertEqual(rules[0]["condition"]["value"], 50)
        self.assertEqual(rules[0]["actions"][0]["type"], "set_variable")

    def test_keywords(self):
        src = "WHEN test KEYWORDS attack, fight, battle\nIF goodwill > 10\nTHEN\n  SET mood = hostile\n"
        rules = DSLCompiler.compile(src)
        self.assertEqual(rules[0]["trigger_keywords"], ["attack", "fight", "battle"])

    def test_and_condition(self):
        src = "WHEN test\nIF hp < 50 AND energy < 30\nTHEN\n  SET bg = danger\n"
        rules = DSLCompiler.compile(src)
        self.assertEqual(rules[0]["condition"]["type"], "AND")
        self.assertEqual(len(rules[0]["condition"]["conditions"]), 2)

    def test_or_condition(self):
        src = "WHEN test\nIF hp < 10 OR goodwill < 0\nTHEN\n  SET phase = 3\n"
        rules = DSLCompiler.compile(src)
        self.assertEqual(rules[0]["condition"]["type"], "OR")

    def test_multiple_rules(self):
        src = "WHEN a\nIF hp > 0\nTHEN\n  SET x = 1\n\nWHEN b\nIF hp > 0\nTHEN\n  SET y = 2\n"
        rules = DSLCompiler.compile(src)
        self.assertEqual(len(rules), 2)

    def test_all_action_types(self):
        src = "WHEN full\nIF hp > 0\nTHEN\n  SET honor = 100\n  CHANGE honor BY -10\n  FORCE emotion = angry\n  UNLOCK secret\n  ADD_ITEM sword\n  REMOVE_ITEM key\n  SET_BG forest\n  SET_PHASE 3\n"
        rules = DSLCompiler.compile(src)
        types = [a["type"] for a in rules[0]["actions"]]
        for t in ["set_variable", "change_variable", "force_emotion", "unlock_memory", "add_item", "remove_item", "set_bg", "set_phase"]:
            self.assertIn(t, types, f"{t} not found in actions")

    def test_comments_ignored(self):
        src = "# comment\nWHEN test\nIF hp > 0\nTHEN\n  SET x = 1\n"
        rules = DSLCompiler.compile(src)
        self.assertEqual(len(rules), 1)

    def test_error_line_number(self):
        src = "WHEN test\nIF hp > 0\nTHEN\n  BAD_ACTION x\n"
        try:
            DSLCompiler.compile(src)
            self.fail("Should have raised")
        except DSLCompileError as e:
            self.assertGreater(e.line, 0)

    def test_missing_if(self):
        with self.assertRaises(DSLCompileError):
            DSLCompiler.compile("WHEN test\nTHEN\n  SET x = 1\n")

    def test_decompile_roundtrip(self):
        src = "WHEN honor_drop KEYWORDS cheat, lie\nIF character_state.honor < 0\nTHEN\n  SET current_tone = cold\n  CHANGE sword_spirit BY -10\n"
        rules = DSLCompiler.compile(src)
        regen = DSLCompiler.decompile(rules)
        rules2 = DSLCompiler.compile(regen)
        self.assertEqual(len(rules2), 1)
        self.assertEqual(rules2[0]["trigger_keywords"], ["cheat", "lie"])

    def test_compile_file(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "test.dsl")
            with open(p, "w", encoding="utf-8") as f:
                f.write("WHEN test\nIF hp > 0\nTHEN\n  SET x = 1\n")
            rules = DSLCompiler.compile_file(p)
            self.assertEqual(len(rules), 1)
        finally: shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
