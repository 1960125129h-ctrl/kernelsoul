"""
test_plugin.py - PluginManager tests
"""
import json, os, shutil, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))
from plugin_manager import PluginManager


class TestPluginManager(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "plugins"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _create_plugin(self, pid, manifest_dict, init_content=None):
        d = os.path.join(self.tmp, "plugins", pid)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_dict, f, indent=2)
        if init_content:
            with open(os.path.join(d, "__init__.py"), "w", encoding="utf-8") as f:
                f.write(init_content)

    def test_empty_plugins_dir(self):
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        self.assertEqual(len(pm.list_plugins()), 0)

    def test_nonexistent_plugins_dir(self):
        pm = PluginManager("/nonexistent/path")
        self.assertEqual(len(pm.list_plugins()), 0)

    def test_load_valid_plugin(self):
        self._create_plugin("test_plugin", {
            "id": "test_plugin", "name": "Test", "version": "1.0",
            "description": "A test plugin.", "hooks": []
        })
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        plugins = pm.list_plugins()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["id"], "test_plugin")
        self.assertTrue(plugins[0]["enabled"])

    def test_skip_broken_manifest(self):
        self._create_plugin("broken", {"name": "No ID", "version": "1"})
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        self.assertEqual(len(pm.list_plugins()), 0)

    def test_skip_id_mismatch(self):
        self._create_plugin("folder_x", {"id": "manifest_y", "name": "X", "version": "1"})
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        self.assertEqual(len(pm.list_plugins()), 0)

    def test_plugin_with_hooks(self):
        init = """class Plugin:
    def __init__(self): self.calls = []
    def on_turn_start(self, ui, state): self.calls.append("start")
"""
        self._create_plugin("hooked", {
            "id": "hooked", "name": "Hooked", "version": "1.0",
            "hooks": ["on_turn_start"]
        }, init)
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        p = pm.list_plugins()[0]
        self.assertIn("on_turn_start", p["hooks"])

    def test_trigger_hook(self):
        init = """class Plugin:
    def __init__(self): self.triggered = False
    def on_turn_end(self, narrative, changes, state): self.triggered = True
"""
        self._create_plugin("trigger_test", {
            "id": "trigger_test", "name": "T", "version": "1.0",
            "hooks": ["on_turn_end"]
        }, init)
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        pm.fire_hook("on_round_end", "test narrative", {}, None)
        # Hook should have run without error

    def test_disable_enable_plugin(self):
        init = """class Plugin:
    def __init__(self): pass
    def on_state_change(self, changes, state): pass
"""
        self._create_plugin("toggle_test", {
            "id": "toggle_test", "name": "Toggle", "version": "1.0",
            "hooks": ["on_state_change"]
        }, init)
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        self.assertTrue(pm.list_plugins()[0]["enabled"])
        pm.disable("toggle_test")
        self.assertFalse(pm.list_plugins()[0]["enabled"])
        pm.enable("toggle_test")
        self.assertTrue(pm.list_plugins()[0]["enabled"])

    def test_list_plugins_format(self):
        self._create_plugin("p1", {"id": "p1", "name": "P1", "version": "1.0", "hooks": []})
        self._create_plugin("p2", {"id": "p2", "name": "P2", "version": "2.0", "description": "desc", "hooks": ["on_turn_end"]})
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        plugins = pm.list_plugins()
        self.assertEqual(len(plugins), 2)
        for key in ["id", "name", "version", "enabled", "description", "hooks"]:
            self.assertIn(key, plugins[0])

    def test_hook_error_does_not_crash(self):
        init = """class Plugin:
    def __init__(self): pass
    def on_turn_start(self, ui, state): raise RuntimeError("boom")
"""
        self._create_plugin("crashy", {
            "id": "crashy", "name": "C", "version": "1.0",
            "hooks": ["on_turn_start"]
        }, init)
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        pm.fire_hook("on_round_end", "hello", None)
        # Should not raise

    def test_summary(self):
        self._create_plugin("s1", {"id": "s1", "name": "S1", "version": "1.0"})
        pm = PluginManager(os.path.join(self.tmp, "plugins"))
        s = pm.summary()
        self.assertIn("s1", s)
        self.assertIn("Plugins (1)", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)

