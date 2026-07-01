"""test_evolution_trigger.py 鈥?EvolutionTrigger unit tests"""

import json, os, shutil, sys, tempfile, unittest

from dataclasses import dataclass, field



sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))

from evolution_trigger import EvolutionTrigger



@dataclass

class FakeState:

    hp: int = 100; max_hp: int = 100; energy: int = 100

    goodwill: int = 0; money: int = 0; phase: int = 1

    inventory: list = field(default_factory=list)

    bg: str = ""; emotion: str = "neutral"; cg: str = ""



class FakeCharMgr:

    def __init__(self):

        self.rules = []

        self.state = {"honor": 50, "suspicion": 30}

        self.conditional_memories = [

            {"id": "mem1", "content": "secret", "unlocked": False},

        ]



class TestEvolutionTrigger(unittest.TestCase):

    def setUp(self):

        self.tmp = tempfile.mkdtemp()

        self.state = FakeState()

        self.char = FakeCharMgr()



    def tearDown(self):

        shutil.rmtree(self.tmp, ignore_errors=True)



    def _make_rules(self, rules):

        p = os.path.join(self.tmp, "rules.json")

        with open(p, "w", encoding="utf-8") as f:

            json.dump({"evolution_rules": rules}, f)

        return p



    def test_global_rule_trigger_set_phase(self):

        rules = [{"id": "r1", "trigger": "ALWAYS", "condition": {"type": "lt", "field": "hp", "value": 50}, "action": [{"type": "set_phase", "value": 2}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        self.state.hp = 30

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 1)

        self.assertEqual(self.state.phase, 2)



    def test_condition_not_met_no_trigger(self):

        rules = [{"id": "r1", "trigger": "ALWAYS", "condition": {"type": "lt", "field": "hp", "value": 50}, "action": [{"type": "set_phase", "value": 2}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        self.state.hp = 80

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 0)



    def test_keyword_trigger(self):

        rules = [{"id": "r_kw", "trigger_keywords": ["attack", "fight"], "condition": {"type": "gt", "field": "hp", "value": 0}, "action": [{"type": "set_emotion", "value": "combat"}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        d = et.evaluate(self.state, user_input="I attack the monster!")

        self.assertEqual(len(d), 1)

        self.assertEqual(self.state.emotion, "combat")



    def test_and_condition(self):

        rules = [{"id": "r_and", "trigger": "ALWAYS", "condition": {"type": "AND", "conditions": [{"type": "lt", "field": "hp", "value": 50}, {"type": "lt", "field": "energy", "value": 30}]}, "action": [{"type": "add_item", "value": "desperation"}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        self.state.hp = 30; self.state.energy = 20

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 1)

        self.assertIn("desperation", self.state.inventory)



    def test_or_condition(self):

        rules = [{"id": "r_or", "trigger": "ALWAYS", "condition": {"type": "OR", "conditions": [{"type": "lt", "field": "hp", "value": 10}, {"type": "lt", "field": "energy", "value": 30}]}, "action": [{"type": "set_bg", "value": "crisis"}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        self.state.hp = 50; self.state.energy = 20

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 1)

        self.assertEqual(self.state.bg, "crisis")



    def test_contains_operator(self):

        rules = [{"id": "r_cont", "trigger": "ALWAYS", "condition": {"type": "contains", "field": "inventory", "value": "key"}, "action": [{"type": "set_phase", "value": 3}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        self.state.inventory = ["rusty key", "map"]

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 1)



    def test_character_rule_trigger(self):

        self.char.rules = [{"id": "char_r1", "trigger": "ALWAYS", "condition": {"type": "lt", "field": "character_state.honor", "value": 30}, "actions": [{"type": "change_variable", "target": "character_state.honor", "delta": -10}]}]

        et = EvolutionTrigger()

        self.char.state["honor"] = 20

        d = et.evaluate(self.state, self.char)

        self.assertEqual(len(d), 1)

        self.assertEqual(self.char.state["honor"], 10)



    def test_empty_rules_file_no_crash(self):

        et = EvolutionTrigger(self._make_rules([]))

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 0)



    def test_action_exception_no_crash(self):

        rules = [{"id": "r_bad", "trigger": "ALWAYS", "condition": {"type": "gt", "field": "hp", "value": 0}, "action": [{"type": "BAD_ACTION", "value": "x"}]}]

        et = EvolutionTrigger(self._make_rules(rules))

        d = et.evaluate(self.state)

        self.assertEqual(len(d), 1)  # Still recorded as triggered



    def test_hot_reload(self):

        p = self._make_rules([{"id": "r1", "trigger": "ALWAYS", "condition": {"type": "gt", "field": "hp", "value": 0}, "action": [{"type": "set_phase", "value": 5}]}])

        et = EvolutionTrigger(p)

        d = et.evaluate(self.state)

        self.assertEqual(self.state.phase, 5)

        # Write new rules

        with open(p, "w", encoding="utf-8") as f:

            json.dump({"evolution_rules": []}, f)

        et.reload_rules(p)

        self.state.phase = 1

        d2 = et.evaluate(self.state)

        self.assertEqual(len(d2), 0)





if __name__ == "__main__":

    unittest.main(verbosity=2)



