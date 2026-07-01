"""
Kernelsoul - EvolutionTrigger (Manual Section 6)
Dual-layer rule engine: global rules -> character rules.
Pure deterministic execution, no AI dependency.
"""
import json
import os
from typing import Any, Optional


class EvolutionTrigger:
    """Dual-layer rule engine. Evaluates global rules.json then character rules."""

    OPERATORS = {
        "eq": lambda a, b: a == b,
        "neq": lambda a, b: a != b,
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
        "contains": lambda a, b: str(b) in str(a) if a else False,
    }

    def __init__(self, rules_path: str = None):
        self.global_rules: list = []
        if rules_path and os.path.exists(rules_path):
            try:
                with open(rules_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                self.global_rules = data.get("evolution_rules", [])
                print(f"[EvolutionTrigger] Loaded {len(self.global_rules)} global rules")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[EvolutionTrigger] Failed to load rules: {e}")

    def evaluate(
        self,
        game_state: Any,
        character_state_manager: Optional[Any] = None,
        user_input: str = "",
        ai_response: str = "",
    ) -> list:
        """Scan all rules, return triggered decisions.
        Order: global rules first, then character rules.
        """
        decisions = []

        # Layer 1: Global rules (rules.json)
        for rule in self.global_rules:
            if not rule.get("enabled", True):
                continue
            if self._check_trigger(rule, user_input, ai_response):
                cond = rule.get("condition")
                if cond and self._evaluate_condition(cond, game_state, character_state_manager):
                    actions = self._execute_actions(rule.get("action", []), game_state, character_state_manager)
                    decisions.append({
                        "rule_id": rule.get("id", "?"),
                        "level": "global",
                        "description": rule.get("description", ""),
                        "actions_executed": actions,
                    })
                    print(f"[EvolutionTrigger] Global rule fired: {rule.get('id')}")

        # Layer 2: Character rules (from CharacterStateManager)
        if character_state_manager:
            char_rules = character_state_manager.rules or []
            for rule in char_rules:
                if not rule.get("enabled", True):
                    continue
                if self._check_trigger(rule, user_input, ai_response):
                    cond = rule.get("condition")
                    if cond and self._evaluate_condition(cond, game_state, character_state_manager):
                        actions = self._execute_actions(rule.get("actions", []), game_state, character_state_manager)
                        decisions.append({
                            "rule_id": rule.get("id", "?"),
                            "level": "character",
                            "description": rule.get("description", ""),
                            "actions_executed": actions,
                        })
                        print(f"[EvolutionTrigger] Character rule fired: {rule.get('id')}")

        return decisions

    def _check_trigger(self, rule: dict, user_input: str, ai_response: str) -> bool:
        trigger = rule.get("trigger", "")
        if trigger == "ALWAYS":
            return True
        keywords = rule.get("trigger_keywords", [])
        if keywords:
            combined = f"{user_input} {ai_response}".lower()
            return any(kw.lower() in combined for kw in keywords)
        return False

    def _evaluate_condition(self, condition: dict, game_state, char_mgr) -> bool:
        cond_type = condition.get("type", "")
        field = condition.get("field", "")
        value = condition.get("value")

        # AND/OR logic
        if cond_type in ("AND", "OR"):
            subs = condition.get("conditions", [])
            results = [self._evaluate_condition(sub, game_state, char_mgr) for sub in subs]
            return all(results) if cond_type == "AND" else any(results)

        # Single condition
        actual = self._resolve_field(field, game_state, char_mgr)
        if actual is None:
            return False
        op = self.OPERATORS.get(cond_type)
        return op(actual, value) if op else False

    def _resolve_field(self, field: str, game_state, char_mgr) -> Any:
        if field.startswith("character_state."):
            var_name = field.replace("character_state.", "")
            if char_mgr and hasattr(char_mgr, "state"):
                return char_mgr.state.get(var_name)
            return None
        if field.startswith("game."):
            attr = field.replace("game.", "")
            return getattr(game_state, attr, None)
        return getattr(game_state, field, None)

    def _execute_actions(self, actions: list, game_state, char_mgr) -> list:
        executed = []
        for action in actions:
            atype = action.get("type", "")
            target = action.get("target", "")
            val = action.get("value")
            delta = action.get("delta", 0)
            try:
                if atype == "set_phase":
                    game_state.phase = val
                elif atype == "set_max_hp":
                    game_state.max_hp = val
                    game_state.hp = min(game_state.hp, val)
                elif atype == "add_item":
                    if val and val not in game_state.inventory:
                        game_state.inventory.append(val)
                elif atype == "remove_item":
                    if val and val in game_state.inventory:
                        game_state.inventory.remove(val)
                elif atype == "set_bg":
                    game_state.bg = str(val)
                elif atype == "set_emotion":
                    game_state.emotion = str(val)
                elif atype == "set_variable" and char_mgr:
                    var_name = target.replace("character_state.", "")
                    if hasattr(char_mgr, "state") and var_name in char_mgr.state:
                        char_mgr.state[var_name] = val
                elif atype == "change_variable" and char_mgr:
                    var_name = target.replace("character_state.", "")
                    if hasattr(char_mgr, "state") and var_name in char_mgr.state:
                        char_mgr.state[var_name] += delta
                elif atype == "unlock_memory" and char_mgr:
                    for mem in getattr(char_mgr, "conditional_memories", []):
                        if mem.get("id") == target:
                            mem["unlocked"] = True
                            break
                elif atype == "force_emotion":
                    game_state.emotion = str(val)
                executed.append({"type": atype, "target": target, "value": val, "delta": delta})
            except Exception as e:
                print(f"[EvolutionTrigger] Action failed [{atype}]: {e}")
        return executed

    def reload_rules(self, rules_path: str):
        self.global_rules = []
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            self.global_rules = data.get("evolution_rules", [])
            print(f"[EvolutionTrigger] Reloaded {len(self.global_rules)} rules")