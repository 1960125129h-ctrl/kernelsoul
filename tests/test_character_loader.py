"""
test_character_loader.py - CharacterCardLoader tests (4 formats)
"""
import json, os, shutil, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from character_card_loader import CharacterCardLoader


class TestCharacterCardLoader(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- V1: SillyTavern V1 (no spec, has name+description) --
    def test_load_v1_basic(self):
        path = os.path.join(self.tmp, "char_v1.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "name": "TestCharV1",
                "description": "A V1 test character.",
                "personality": "friendly",
                "first_mes": "Hello!",
                "scenario": "In a tavern.",
                "system_prompt": "You are a test.",
            }, f)
        char = CharacterCardLoader.load(path)
        self.assertEqual(char["name"], "TestCharV1")
        self.assertEqual(char["description"], "A V1 test character.")
        self.assertEqual(char["first_message"], "Hello!")
        self.assertEqual(char["spec"], "chara_card_v1")
        # V4 upgrade padding
        self.assertIn("character_state", char)
        self.assertIn("character_rules", char)
        self.assertIn("conditional_memories", char)
        self.assertEqual(char["character_rules"], [])

    # -- V2: SillyTavern V2 (spec chara_card_v2, data nested) --
    def test_load_v2(self):
        path = os.path.join(self.tmp, "char_v2.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "spec": "chara_card_v2",
                "data": {
                    "name": "TestCharV2",
                    "description": "V2 character.",
                    "personality": "brave",
                    "first_mes": "Hi there.",
                    "scenario": "On a quest.",
                    "system_prompt": "Be brave.",
                }
            }, f)
        char = CharacterCardLoader.load(path)
        self.assertEqual(char["name"], "TestCharV2")
        self.assertEqual(char["spec"], "chara_card_v2")
        self.assertEqual(char["first_message"], "Hi there.")
        self.assertEqual(char["character_rules"], [])

    # -- V3: SillyTavern V3 (spec chara_card_v3, extensions) --
    def test_load_v3_full(self):
        path = os.path.join(self.tmp, "char_v3.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "spec": "chara_card_v3",
                "data": {
                    "name": "TestCharV3",
                    "description": "V3 with extensions.",
                    "personality": "mysterious",
                    "first_mes": "Who goes there?",
                    "scenario": "Dark forest.",
                    "system_prompt": "Be mysterious.",
                    "mes_example": "<example dialogue>",
                    "alternate_greetings": ["Hey.", "Hello."],
                    "tags": ["fantasy", "dark"],
                    "creator": "AuthorName",
                    "creator_notes": "Test only.",
                    "character_version": "1.0",
                    "extensions": {
                        "engine_state": {
                            "hp": 80,
                            "max_hp": 120,
                            "energy": 50,
                            "phase": 2,
                        }
                    }
                }
            }, f)
        char = CharacterCardLoader.load(path)
        self.assertEqual(char["name"], "TestCharV3")
        self.assertEqual(char["spec"], "chara_card_v3")
        self.assertEqual(char["mes_example"], "<example dialogue>")
        self.assertEqual(char["alternate_greetings"], ["Hey.", "Hello."])
        self.assertEqual(char["tags"], ["fantasy", "dark"])
        self.assertEqual(char["creator"], "AuthorName")
        # engine_state -> character_initstate
        self.assertIn("character_initstate", char)
        self.assertEqual(char["character_initstate"]["hp"], 80)
        self.assertEqual(char["character_initstate"]["max_hp"], 120)

    # -- V3 without extensions --
    def test_load_v3_no_extensions(self):
        path = os.path.join(self.tmp, "char_v3_min.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "spec": "chara_card_v3",
                "data": {
                    "name": "MinimalV3",
                    "description": "No extensions.",
                }
            }, f)
        char = CharacterCardLoader.load(path)
        self.assertEqual(char["name"], "MinimalV3")
        self.assertEqual(char["character_initstate"], {})
        self.assertEqual(char["character_rules"], [])

    # -- V4: native folder format --
    def test_load_v4_folder(self):
        char_dir = os.path.join(self.tmp, "v4_char")
        os.makedirs(char_dir)
        # character_data.json
        with open(os.path.join(char_dir, "character_data.json"), "w", encoding="utf-8") as f:
            json.dump({
                "name": "V4TestChar",
                "description": "V4 native character.",
                "personality": "complex",
                "prompt": "Speak wisely.",
                "character_state": {"variables": {"mood": {"type": "int", "default": 0}}},
                "character_rules": [{"id": "r1", "trigger": "insult", "condition": {}, "action": []}],
                "meta_cognition_prompt": "Stay in character.",
            }, f)
        # character_rules.json
        with open(os.path.join(char_dir, "character_rules.json"), "w", encoding="utf-8") as f:
            json.dump([{"id": "compiled_r1"}], f)
        # character.dsl
        with open(os.path.join(char_dir, "character.dsl"), "w", encoding="utf-8") as f:
            f.write("WHEN insult THEN SET mood = angry")
        # character_lorebook.json
        with open(os.path.join(char_dir, "character_lorebook.json"), "w", encoding="utf-8") as f:
            json.dump({
                "entries": [{"keys": ["sword"], "content": "A legendary blade."}]
            }, f)
        # character_initstate.json
        with open(os.path.join(char_dir, "character_initstate.json"), "w", encoding="utf-8") as f:
            json.dump({"hp": 50, "inventory": ["old key"]}, f)
        # meta_cognition.txt
        with open(os.path.join(char_dir, "meta_cognition.txt"), "w", encoding="utf-8") as f:
            f.write("Remember your role.")

        char = CharacterCardLoader.load(char_dir)
        self.assertEqual(char["name"], "V4TestChar")
        self.assertEqual(char["spec"], "chara_card_v4")
        self.assertIn("mood", char["character_state"]["variables"])
        self.assertEqual(len(char["character_rules"]), 1)
        self.assertGreater(len(char.get("character_rules", [])), 0)
        self.assertIn("WHEN insult", char["character_rules_dsl"])
        self.assertIn("entries", char["character_lorebook"])
        self.assertEqual(char["character_initstate"]["hp"], 50)
        self.assertEqual(char["meta_cognition_prompt"], "Remember your role.")
        self.assertIn(char.get("character_rules_source", ""), ["dsl", "ai", "auto", ""])

    # -- V4 folder minimal --
    def test_load_v4_folder_minimal(self):
        char_dir = os.path.join(self.tmp, "v4_min")
        os.makedirs(char_dir)
        with open(os.path.join(char_dir, "character_data.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "MinV4", "description": "Minimal V4."}, f)

        char = CharacterCardLoader.load(char_dir)
        self.assertEqual(char["name"], "MinV4")
        self.assertEqual(char["character_rules"], [])
        self.assertEqual(char["character_state"]["variables"], {})
        self.assertIn(char.get("character_rules_source", ""), ["ai", "dsl", ""])

    # -- Edge: unrecognized format --
    def test_load_unrecognized_raises(self):
        path = os.path.join(self.tmp, "bad.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"unknown": "format"}, f)
        with self.assertRaises(ValueError):
            CharacterCardLoader.load(path)

    # -- V1 with prompt alias (prompt -> system_prompt) --
    def test_load_v1_prompt_alias(self):
        path = os.path.join(self.tmp, "char_v1_prompt.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "name": "PromptChar",
                "description": "Uses prompt field.",
                "prompt": "Custom system prompt text.",
            }, f)
        char = CharacterCardLoader.load(path)
        self.assertEqual(char["system_prompt"], "Custom system prompt text.")

    # -- V4 upgrade: V1 card gets empty initstate --
    def test_v1_upgrade_empty_initstate(self):
        path = os.path.join(self.tmp, "char_v1_upg.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"name": "UpgradeTest", "description": "test"}, f)
        char = CharacterCardLoader.load(path)
        self.assertEqual(char["character_initstate"], {})
        self.assertEqual(char["character_rules"], [])
        self.assertEqual(char["conditional_memories"], [])
        self.assertEqual(char["meta_cognition_prompt"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
