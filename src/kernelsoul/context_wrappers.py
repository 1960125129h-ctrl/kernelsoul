"""
Kernelsoul - Context Wrappers for Core Modules
Each module gets a Context subclass that emits events on the shared bus.
"""
from context import Context, bus, GlobalContext
from typing import Any


class CharacterContext(Context):
    """Context for CharacterCardLoader / character management."""
    def __init__(self):
        super().__init__("character_context")
        self.current = None

    def on_loaded(self, char_data: dict):
        self.current = char_data
        self.emit("character.loaded", {"name": char_data.get("name"), "spec": char_data.get("spec")})

    def on_switched(self, char_id: str):
        self.emit("character.switched", {"id": char_id})


class StateContext(Context):
    """Context for StateManager / game state changes."""
    def __init__(self, state_mgr=None):
        super().__init__("state_context")
        self.state_mgr = state_mgr
        self._last_hp = None

    def on_changed(self, changes: dict, state: Any):
        hp = getattr(state, "hp", None)
        if self._last_hp is not None and hp != self._last_hp:
            self.emit("state.hp_changed", {"before": self._last_hp, "after": hp, "delta": hp - self._last_hp})
        self._last_hp = hp
        self.emit("state.changed", {"hp": hp, "energy": getattr(state, "energy", None),
                                     "emotion": getattr(state, "emotion", ""), "changes": changes})


class MemoryContext(Context):
    """Context for MemoryManager."""
    def __init__(self):
        super().__init__("memory_context")

    def on_compressed(self, comp_type: str, round_range: str, summary_len: int):
        self.emit("memory.compressed", {"type": comp_type, "rounds": round_range, "length": summary_len})

    def on_manual_added(self, content: str):
        self.emit("memory.manual_added", {"content": content[:100]})


class RulesContext(Context):
    """Context for EvolutionTrigger."""
    def __init__(self):
        super().__init__("rules_context")

    def on_triggered(self, rule_id: str, level: str, description: str, actions: list):
        self.emit("rule.triggered", {"id": rule_id, "level": level, "description": description, "actions": actions})

    def on_phase_changed(self, old_phase: int, new_phase: int):
        self.emit("rule.phase_changed", {"old": old_phase, "new": new_phase})


class AIContext(Context):
    """Context for AIBridge / AI generation."""
    def __init__(self):
        super().__init__("ai_context")

    def on_response(self, narrative: str, state_changes: dict):
        self.emit("ai.response_generated", {"narrative": narrative, "state_changes": state_changes})

    def on_stream_token(self, token: str):
        self.emit("ai.stream_token", {"token": token})


class PluginContext(Context):
    """Context for PluginManager."""
    def __init__(self):
        super().__init__("plugin_context")

    def on_loaded(self, plugin_id: str, version: str):
        self.emit("plugin.loaded", {"id": plugin_id, "version": version})

    def on_reloaded(self, plugin_id: str = None):
        self.emit("plugin.reloaded", {"id": plugin_id})


# Factory: get or create context instances
_contexts = {}

def get_context(name: str):
    """Get or lazily-create a context instance."""
    if name not in _contexts:
        mapping = {
            "character_context": CharacterContext,
            "state_context": StateContext,
            "memory_context": MemoryContext,
            "rules_context": RulesContext,
            "ai_context": AIContext,
            "plugin_context": PluginContext,
        }
        cls = mapping.get(name)
        if cls:
            _contexts[name] = cls()
    return _contexts.get(name)

