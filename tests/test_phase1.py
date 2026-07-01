"""
Kernelsoul - MVP Phase 1 Tests: GameState + PathResolver + StateManager + SessionMeta
"""
import json, os, shutil, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_state import GameState, load_state, save_state
from path_resolver import PathResolver
from state_manager import StateManager
from session_meta import SessionMeta, load_meta, save_meta, CURRENT_DATA_VERSION


class TestGameState(unittest.TestCase):
    def test_default_values(self):
        gs = GameState()
        self.assertEqual(gs.hp, 100); self.assertEqual(gs.energy, 100)
        self.assertEqual(gs.goodwill, 0); self.assertEqual(gs.money, 0)
        self.assertEqual(gs.inventory, []); self.assertEqual(gs.bg, "")
        self.assertEqual(gs.emotion, "neutral"); self.assertEqual(gs.cg, "")
        self.assertEqual(gs.phase, 1); self.assertEqual(gs.max_hp, 100)

    def test_custom_init(self):
        gs = GameState(hp=50, money=200, bg="tavern", emotion="curious")
        self.assertEqual(gs.hp, 50); self.assertEqual(gs.money, 200)
        self.assertEqual(gs.bg, "tavern"); self.assertEqual(gs.emotion, "curious")
        self.assertEqual(gs.energy, 100)

    def test_to_dict(self):
        gs = GameState(hp=80, inventory=["sword", "map"])
        d = gs.to_dict()
        self.assertEqual(d["hp"], 80); self.assertEqual(d["inventory"], ["sword", "map"])

    def test_from_dict_complete(self):
        d = {"hp": 60, "energy": 50, "goodwill": 10, "money": 500, "inventory": ["apple", "key"], "bg": "basement", "emotion": "fear", "cg": "cg_monster", "phase": 2, "max_hp": 120}
        gs = GameState.from_dict(d)
        self.assertEqual(gs.hp, 60); self.assertEqual(gs.emotion, "fear")
        self.assertEqual(gs.phase, 2); self.assertEqual(gs.max_hp, 120)

    def test_from_dict_missing_fields(self):
        gs = GameState.from_dict({"hp": 30, "emotion": "sad"})
        self.assertEqual(gs.hp, 30); self.assertEqual(gs.energy, 100)

    def test_from_dict_extra_fields(self):
        gs = GameState.from_dict({"hp": 10, "unknown_field": 999})
        self.assertEqual(gs.hp, 10)
        with self.assertRaises(AttributeError): _ = gs.unknown_field

    def test_serialize_roundtrip(self):
        gs1 = GameState(hp=75, energy=90, inventory=["sword", "shield"], bg="castle", phase=3, max_hp=150)
        gs2 = GameState.from_dict(json.loads(json.dumps(gs1.to_dict())))
        for f in GameState.__dataclass_fields__:
            self.assertEqual(getattr(gs1, f), getattr(gs2, f))

    def test_default_state(self):
        gs = GameState.default_state(hp=50, money=1000)
        self.assertEqual(gs.hp, 50); self.assertEqual(gs.energy, 100)

    def test_reset(self):
        gs = GameState(hp=30, money=500, bg="forest")
        gs.reset()
        self.assertEqual(gs.hp, 100); self.assertEqual(gs.money, 0)

    def test_save_and_load_file(self):
        d = tempfile.mkdtemp()
        try:
            path = os.path.join(d, "state.sav")
            gs = GameState(hp=60, inventory=["watch"], bg="tower")
            save_state(gs, path)
            self.assertTrue(os.path.exists(path))
            gs2 = load_state(path)
            self.assertEqual(gs2.hp, 60)
        finally: shutil.rmtree(d, ignore_errors=True)

    def test_load_nonexistent(self):
        gs = load_state("/nonexistent/path.sav")
        self.assertEqual(gs.hp, 100)


class TestPathResolver(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for sub in ["configs", "characters", "assets", "saves", "plugins"]:
            os.makedirs(os.path.join(self.tmp, sub), exist_ok=True)
    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic_paths(self):
        pr = PathResolver(self.tmp, "demon", "s1")
        self.assertEqual(pr.char, "demon"); self.assertEqual(pr.session, "s1")

    def test_session_dir_created(self):
        pr = PathResolver(self.tmp, "demon", "s1")
        self.assertTrue(os.path.isdir(pr.get_session_dir()))

    def test_dirs_created(self):
        pr = PathResolver(self.tmp, "demon", "s1")
        self.assertTrue(os.path.isdir(pr.get_history_dir()))
        self.assertTrue(os.path.isdir(pr.get_context_dir()))
        self.assertTrue(os.path.isdir(pr.get_drafts_dir()))

    def test_state_file_path(self):
        pr = PathResolver(self.tmp, "demon", "s1")
        self.assertTrue(pr.get_state_file().endswith("state.sav"))

    def test_config_paths(self):
        pr = PathResolver(self.tmp, "", "")
        self.assertEqual(pr.get_system_config(), os.path.join(self.tmp, "configs", "system.json"))

    def test_character_paths(self):
        pr = PathResolver(self.tmp, "innkeeper", "s1")
        self.assertEqual(pr.get_character_dir(), os.path.join(self.tmp, "characters", "innkeeper"))

    def test_bind_switch(self):
        pr = PathResolver(self.tmp, "a", "s1")
        pr.bind(char="b")
        self.assertEqual(pr.char, "b")
        self.assertTrue(os.path.isdir(pr.get_session_dir()))

    def test_bind_session(self):
        pr = PathResolver(self.tmp, "demon", "s1")
        pr.bind(session="s2")
        self.assertEqual(pr.session, "s2")

    def test_draft_path(self):
        pr = PathResolver(self.tmp, "t", "s1")
        self.assertTrue(pr.resolve_draft_path(42).endswith("draft_042.json"))

    def test_list_drafts(self):
        pr = PathResolver(self.tmp, "t", "s1")
        for i in [1, 5, 10]:
            with open(pr.resolve_draft_path(i), "w") as f: f.write("{}")
        self.assertEqual(pr.list_drafts(), [1, 5, 10])

    def test_plugin_paths(self):
        pr = PathResolver(self.tmp, "", "")
        self.assertEqual(pr.get_plugin_manifest("example"), os.path.join(self.tmp, "plugins", "example", "manifest.json"))

    def test_empty_no_crash(self):
        pr = PathResolver(self.tmp, "", "")
        self.assertEqual(pr.char, "")


class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "configs"), exist_ok=True)
        self.pr = PathResolver(self.tmp, "test", "s1")
        self.sm = StateManager(self.pr)
    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_default(self):
        self.assertEqual(self.sm.state.hp, 100)

    def test_save_reload(self):
        self.sm.state.hp = 50; self.sm.save()
        sm2 = StateManager(self.pr)
        self.assertEqual(sm2.state.hp, 50)

    def test_modify_hp_clamps(self):
        self.sm.modify_hp(-200); self.assertEqual(self.sm.state.hp, 0)
        self.sm.modify_hp(500); self.assertEqual(self.sm.state.hp, 100)

    def test_modify_money_no_negative(self):
        self.sm.modify_money(-200); self.assertEqual(self.sm.state.money, 0)

    def test_add_item(self):
        self.sm.add_item("sword"); self.assertIn("sword", self.sm.state.inventory)
        self.sm.add_item("sword"); self.assertEqual(self.sm.state.inventory.count("sword"), 1)

    def test_remove_item(self):
        self.sm.state.inventory = ["key", "map"]
        self.assertTrue(self.sm.remove_item("key"))
        self.assertNotIn("key", self.sm.state.inventory)

    def test_remove_item_nonexistent(self):
        self.assertFalse(self.sm.remove_item("ghost"))

    def test_apply_changes_basic(self):
        self.sm.apply_state_changes({"hp": -20, "energy": -10, "goodwill": 5, "money": 100})
        self.assertEqual(self.sm.state.hp, 80); self.assertEqual(self.sm.state.goodwill, 5)

    def test_apply_changes_string(self):
        self.sm.apply_state_changes({"bg": "forest", "emotion": "fear", "cg": "cg_shadow"})
        self.assertEqual(self.sm.state.bg, "forest")

    def test_apply_illegal_field(self):
        self.sm.apply_state_changes({"hp": -10, "phase": 99, "max_hp": 999})
        self.assertEqual(self.sm.state.phase, 1); self.assertEqual(self.sm.state.hp, 90)

    def test_inventory_add_remove_order(self):
        self.sm.state.inventory = ["old_key"]
        self.sm.apply_state_changes({"inventory_remove": ["old_key"], "inventory_add": ["new_key", "map"]})
        self.assertNotIn("old_key", self.sm.state.inventory)
        self.assertIn("new_key", self.sm.state.inventory)

    def test_reset(self):
        self.sm.state.hp = 30; self.sm.reset()
        self.assertEqual(self.sm.state.hp, 100)

    def test_reload_discards_unsaved(self):
        self.sm.state.hp = 30; self.sm.save()
        self.sm.state.hp = 99; self.sm.reload()
        self.assertEqual(self.sm.state.hp, 30)

    def test_save_roundtrip(self):
        self.sm.state.hp = 40; self.sm.state.inventory = ["book", "quill"]
        self.sm.state.bg = "library"; self.sm.save()
        sm2 = StateManager(self.pr)
        self.assertEqual(sm2.state.hp, 40); self.assertEqual(sm2.state.inventory, ["book", "quill"])


class TestSessionMeta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "saves", "test", "s1"), exist_ok=True)
    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def test_defaults(self):
        sm = SessionMeta()
        self.assertEqual(sm.data_version, 1); self.assertEqual(sm.total_rounds, 0)

    def test_create_fills_timestamps(self):
        sm = SessionMeta.create(character_name="demon", session_id="s1")
        self.assertNotEqual(sm.created_at, ""); self.assertEqual(sm.character_name, "demon")

    def test_touch(self):
        sm = SessionMeta(); old = sm.last_saved_at
        sm.touch(); self.assertNotEqual(sm.last_saved_at, old)

    def test_increment_rounds(self):
        sm = SessionMeta(); sm.increment_rounds(5)
        self.assertEqual(sm.total_rounds, 5)

    def test_to_dict(self):
        sm = SessionMeta.create(character_name="demon")
        self.assertEqual(sm.to_dict()["character_name"], "demon")

    def test_from_dict(self):
        d = {"data_version": 1, "total_rounds": 67, "character_name": "demon", "session_id": "s1"}
        sm = SessionMeta.from_dict(d)
        self.assertEqual(sm.total_rounds, 67)

    def test_from_dict_missing(self):
        sm = SessionMeta.from_dict({"character_name": "test"})
        self.assertEqual(sm.total_rounds, 0)

    def test_save_load(self):
        path = os.path.join(self.tmp, "saves", "test", "s1", "session_meta.json")
        sm1 = SessionMeta.create(character_name="innkeeper"); sm1.total_rounds = 42
        save_meta(sm1, path)
        sm2 = load_meta(path)
        self.assertEqual(sm2.character_name, "innkeeper"); self.assertEqual(sm2.total_rounds, 42)

    def test_load_nonexistent(self):
        sm = load_meta("/nonexistent.json")
        self.assertEqual(sm.data_version, 1)

    def test_v2_reserved(self):
        sm = SessionMeta.create()
        self.assertEqual(sm.active_characters, [])

    def test_roundtrip(self):
        path = os.path.join(self.tmp, "saves", "test", "s1", "session_meta.json")
        sm = SessionMeta.create(character_name="demon")
        save_meta(sm, path)
        sm2 = load_meta(path); sm2.increment_rounds(10)
        save_meta(sm2, path)
        sm3 = load_meta(path)
        self.assertEqual(sm3.total_rounds, 10)
        self.assertNotEqual(sm3.last_saved_at, sm3.created_at)


if __name__ == "__main__":
    unittest.main(verbosity=2)
