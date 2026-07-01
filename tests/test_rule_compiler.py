"""
Tests for RuleCompiler (natural language -> DSL).
"""
import unittest, sys, os, json, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))

# Mock AI bridge for testing
class MockBridge:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return a valid rules JSON for testing."""
        return json.dumps({
            "character_rules": [
                {
                    "id": "r1",
                    "trigger": "player insults the character",
                    "trigger_keywords": ["insult", "idiot"],
                    "condition": {"type": "compare", "field": "goodwill", "value": 10},
                    "actions": [
                        {"type": "delta", "field": "goodwill", "delta": -5},
                        {"type": "force_tone", "tone": "angry"},
                    ],
                    "description": "Character gets angry when insulted",
                },
                {
                    "id": "r2",
                    "trigger": "player gives a gift",
                    "trigger_keywords": ["gift", "present", "for you"],
                    "condition": {"type": "compare", "field": "goodwill", "value": 50},
                    "actions": [
                        {"type": "delta", "field": "goodwill", "delta": 5},
                    ],
                    "description": "Gifts improve goodwill",
                },
            ],
            "conditional_memories": [
                {
                    "id": "mem_trust",
                    "content": "This person has earned my trust.",
                    "unlock_condition": {"type": "compare", "field": "goodwill", "value": 80},
                    "unlocked": False,
                },
            ],
            "suggested_variables": {"honor": 0, "trust_level": 0},
        })


class TestRuleCompiler(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.tmp, "configs")
        os.makedirs(self.config_dir)
        # Write a minimal compiler prompt
        with open(os.path.join(self.config_dir, "rule_compiler_prompt.txt"), "w", encoding="utf-8") as f:
            f.write("Generate rules from: {character_description}")
        from rule_compiler import RuleCompiler
        self.rc = RuleCompiler(MockBridge(), self.config_dir)

    def test_compile_valid_input(self):
        result = self.rc.compile("A proud knight who values honor.")
        self.assertGreater(len(result["character_rules"]), 0)
        self.assertEqual(result["character_rules"][0]["id"], "r1")
        self.assertEqual(result["character_rules"][0]["description"], "Character gets angry when insulted")

    def test_compile_includes_memories(self):
        result = self.rc.compile("Any description.")
        self.assertGreater(len(result["conditional_memories"]), 0)
        self.assertEqual(result["conditional_memories"][0]["id"], "mem_trust")

    def test_compile_includes_variables(self):
        result = self.rc.compile("Any description.")
        self.assertIn("honor", result["suggested_variables"])

    def test_to_dsl_generates_valid_syntax(self):
        result = self.rc.compile("Knight character.")
        rules = result["character_rules"]
        dsl = self.rc.to_dsl(rules)
        # Basic DSL validation
        self.assertIn("WHEN", dsl)
        self.assertIn("IF goodwill <= 10", dsl)
        self.assertIn("THEN", dsl)
        self.assertIn("CHANGE", dsl)
        self.assertIn("FORCE", dsl)

    def test_to_dsl_includes_keywords(self):
        result = self.rc.compile("Any.")
        dsl = self.rc.to_dsl(result["character_rules"])
        self.assertIn("KEYWORDS", dsl)
        self.assertIn("insult", dsl)

    def test_to_dsl_empty_rules(self):
        dsl = self.rc.to_dsl([])
        self.assertIn("Auto-generated", dsl)

    def test_save_rules_writes_files(self):
        result = self.rc.compile("Test character.")
        char_dir = os.path.join(self.tmp, "test_char")
        os.makedirs(char_dir)
        rp, dp = self.rc.save_rules(result, char_dir)
        self.assertTrue(os.path.exists(rp))
        self.assertTrue(os.path.exists(dp))
        # Verify content
        with open(rp, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(len(saved["rules"]), 2)

    def test_parse_response_code_block(self):
        response = """OK here are the rules:
```json
{"character_rules": [{"id": "x1", "trigger": "test", "trigger_keywords": ["a"], "condition": {}, "actions": [], "description": "t"}], "conditional_memories": [], "suggested_variables": {}}
```
Done."""
        parsed = self.rc._parse_response(response)
        self.assertEqual(len(parsed["character_rules"]), 1)
        self.assertEqual(parsed["character_rules"][0]["id"], "x1")

    def test_parse_response_bare_json(self):
        response = '{"character_rules": [], "conditional_memories": [{"id": "m1", "content": "test", "unlock_condition": {}, "unlocked": false}], "suggested_variables": {"x": 0}}'
        parsed = self.rc._parse_response(response)
        self.assertEqual(len(parsed["conditional_memories"]), 1)

    def test_parse_response_invalid(self):
        response = "I cannot generate rules because..."
        parsed = self.rc._parse_response(response)
        self.assertIn("error", parsed)
        self.assertEqual(len(parsed["character_rules"]), 0)


if __name__ == "__main__":
    unittest.main()
