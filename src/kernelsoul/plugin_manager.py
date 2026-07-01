"""
Kernelsoul - PluginManager v2.0
Full lifecycle hooks + permission review + hot reload.
"""
import json, os, sys, importlib, importlib.util
from typing import Dict, List, Optional, Callable

ALL_HOOKS = [
    "on_engine_start", "on_session_start", "on_user_input",
    "on_draft_created", "on_draft_selected", "on_round_end",
    "on_state_change", "on_memory_compressed", "on_character_load",
    "on_session_end", "on_engine_stop",
]

HIGH_RISK_PERMS = ["write_state", "network"]


class PluginManager:
    def __init__(self, plugins_dir: str):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, dict] = {}
        self._hook_registry: Dict[str, List[Callable]] = {h: [] for h in ALL_HOOKS}
        self._scan_and_load()

    def _scan_and_load(self):
        if not os.path.isdir(self.plugins_dir):
            return
        for name in sorted(os.listdir(self.plugins_dir)):
            d = os.path.join(self.plugins_dir, name)
            if not os.path.isdir(d):
                continue
            mf = os.path.join(d, "manifest.json")
            if os.path.exists(mf):
                self._load_plugin(d, mf, name)

    def _load_plugin(self, plugin_dir, manifest_path, plugin_id):
        try:
            with open(manifest_path, "r", encoding="utf-8-sig") as f:
                manifest = json.load(f)
        except Exception as e:
            print(f"[PluginManager] {plugin_id}: invalid manifest ({e})")
            return
        if not self._validate(manifest, plugin_id):
            return
        self._review_permissions(manifest, plugin_id)

        module = None
        init = os.path.join(plugin_dir, "__init__.py")
        if os.path.exists(init):
            try:
                spec = importlib.util.spec_from_file_location(f"v4_plugin_{plugin_id}", init)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
            except Exception as e:
                print(f"[PluginManager] {plugin_id}: load failed ({e})")

        hooks = {}
        if module and hasattr(module, "Plugin"):
            inst = module.Plugin()
            for h in manifest.get("hooks", []):
                if hasattr(inst, h):
                    hooks[h] = getattr(inst, h)

        self.plugins[plugin_id] = {
            "manifest": manifest, "module": module, "hooks": hooks,
            "enabled": True, "dir": plugin_dir,
        }
        self._register_hooks(plugin_id, hooks)

    def _validate(self, manifest, plugin_id):
        for f in ["id", "name", "version"]:
            if f not in manifest:
                print(f"[PluginManager] {plugin_id}: missing {f}")
                return False
        if manifest["id"] != plugin_id:
            print(f"[PluginManager] {plugin_id}: id mismatch")
            return False
        return True

    def _review_permissions(self, manifest, plugin_id):
        for p in manifest.get("permissions", []):
            if p in HIGH_RISK_PERMS:
                print(f"[PluginManager] WARNING: {plugin_id} requests {p}")

    def _register_hooks(self, plugin_id, hooks):
        for h in hooks:
            if h in self._hook_registry:
                self._hook_registry[h].append(hooks[h])

    def fire_hook(self, hook_name, *args, **kwargs):
        for fn in self._hook_registry.get(hook_name, []):
            try: fn(*args, **kwargs)
            except Exception as e: print(f"[PluginManager] Hook {hook_name} error: {e}")

    
    def filter_hook(self, hook_name, value):
        """Apply filter hooks that transform and return a value."""
        for fn in self._hook_registry.get(hook_name, []):
            try:
                result = fn(value)
                if result is not None:
                    value = result
            except Exception as e:
                print(f"[PluginManager] Filter hook {hook_name} error: {e}")
        return value

    def reload(self, plugin_id=None):
        if plugin_id and plugin_id in self.plugins:
            self._unregister(plugin_id)
            d = self.plugins[plugin_id]["dir"]
            mf = os.path.join(d, "manifest.json")
            if os.path.exists(mf): self._load_plugin(d, mf, plugin_id)
        else:
            self._hook_registry = {h: [] for h in ALL_HOOKS}
            self.plugins.clear()
            self._scan_and_load()

    def enable(self, plugin_id):
        if plugin_id in self.plugins:
            self.plugins[plugin_id]["enabled"] = True
            self._register_hooks(plugin_id, self.plugins[plugin_id]["hooks"])

    def disable(self, plugin_id):
        if plugin_id in self.plugins:
            self.plugins[plugin_id]["enabled"] = False
            self._unregister(plugin_id)

    def _unregister(self, plugin_id):
        if plugin_id not in self.plugins: return
        for h, fn in self.plugins[plugin_id]["hooks"].items():
            if h in self._hook_registry:
                self._hook_registry[h] = [x for x in self._hook_registry[h] if x is not fn]

    def list_plugins(self) -> list:
        r = []
        for pid, info in self.plugins.items():
            m = info["manifest"]
            r.append({
                "id": pid, "name": m.get("name", pid),
                "version": m.get("version", "?"), "enabled": info["enabled"],
                "description": m.get("description", ""),
                "hooks": list(info["hooks"].keys()),
                "permissions": m.get("permissions", []),
            })
        return r

    def summary(self) -> str:
        sl = [f"Plugins ({len(self.plugins)}):"]
        for p in self.list_plugins():
            s = "enabled" if p["enabled"] else "disabled"
            sl.append(f"  [{s}] {p['id']} v{p['version']} - {p['description'][:60]}")
        return "\n".join(sl)
