"""

Kernelsoul - DSL Compiler (Manual Section 7.5.1)

Compiles character.dsl source to character_rules.json format.

Line-number-accurate error reporting. Auto-compile on file change.



DSL Syntax:

  WHEN <trigger_description> [KEYWORDS k1, k2]

  IF <field> <op> <value> [AND/OR <field> <op> <value>]

  THEN

    SET <variable> = <value>

    CHANGE <variable> BY <delta>

    FORCE <emotion|tone> = <value>

    UNLOCK <memory_id>

    ADD_ITEM <item>

    REMOVE_ITEM <item>

    SET_BG <scene>

    SET_PHASE <n>

"""

import re

from typing import Tuple, Optional





class DSLCompileError(Exception):

    """DSL compile error with line number."""

    def __init__(self, msg: str, line: int):

        self.line = line

        super().__init__(f'Line {line}: {msg}')





class DSLCompiler:

    """Compiles .dsl source to character_rules JSON."""



    OP_MAP = {"<": "lt", ">": "gt", "=": "eq", "!=": "neq",

              "<=": "lte", ">=": "gte", "CONTAINS": "contains"}



    @classmethod

    def compile(cls, source: str) -> list:

        """Compile DSL source to list of character rules (dicts).

        Raises DSLCompileError with line number on failure.

        """

        rules = []

        lines = source.split("\n")

        i = 0



        while i < len(lines):

            stripped = lines[i].strip()

            if not stripped or stripped.startswith("#"):

                i += 1

                continue



            upper = stripped.upper()



            if upper.startswith("WHEN "):

                rule, i = cls._parse_rule(lines, i)

                if rule:

                    rules.append(rule)

            elif upper.startswith("MEMORY ") or upper.startswith("CONDITIONAL_MEMORY "):

                # TODO: parse conditional memories

                i += 1

            else:

                i += 1



        return rules



    @classmethod

    def _parse_rule(cls, lines: list, start: int) -> Tuple[Optional[dict], int]:

        """Parse one WHEN...THEN rule block. Returns (rule_dict, next_index)."""

        i = start

        line_num = i + 1

        stripped = lines[i].strip()



        # WHEN <trigger> [KEYWORDS k1, k2]

        when_part = stripped[4:].strip()  # Remove "WHEN"

        trigger = ""

        trigger_keywords = []



        kw_match = re.search(r'(?i)(?<!\w)KEYWORDS(?!\w)\s+(.+)', when_part)

        if kw_match:

            trigger = when_part[:kw_match.start()].strip().strip('"').strip("'")

            trigger_keywords = [k.strip().strip('"').strip("'") for k in kw_match.group(1).split(",")]

        else:

            trigger = when_part.strip().strip('"').strip("'")



        i += 1



        # Skip comments before IF

        while i < len(lines):

            s = lines[i].strip()

            if s and not s.startswith("#"):

                break

            i += 1



        # IF condition

        if i >= len(lines) or not lines[i].strip().upper().startswith("IF "):

            raise DSLCompileError("Expected IF after WHEN", line_num)

        condition = cls._parse_condition(lines[i].strip()[3:].strip(), i + 1)

        i += 1



        # Skip comments before THEN

        while i < len(lines):

            s = lines[i].strip()

            if s and not s.startswith("#"):

                break

            i += 1



        # THEN

        if i >= len(lines) or not lines[i].strip().upper().startswith("THEN"):

            raise DSLCompileError("Expected THEN after IF", i + 1)

        i += 1



        # Actions (indented under THEN)

        actions = []

        while i < len(lines):

            raw = lines[i]

            stripped = raw.strip()

            if not stripped or stripped.startswith("#"):

                i += 1

                continue

            # End of rule: next WHEN or MEMORY or outdent

            upper = stripped.upper()

            if upper.startswith("WHEN ") or upper.startswith("MEMORY ") or upper.startswith("CONDITIONAL_MEMORY "):

                break

            if not raw.startswith("  ") and not raw.startswith("\t"):

                # Not indented, end of this rule's actions

                break

            action = cls._parse_action(stripped, i + 1)

            if action:

                actions.append(action)

            i += 1



        return {

            "id": cls._make_id(trigger, trigger_keywords, start),

            "trigger": trigger if trigger else "玩家行为触发",

            "trigger_keywords": trigger_keywords,

            "condition": condition,

            "actions": actions,

            "description": f'WHEN {trigger}' if trigger else "",

            "enabled": True,

        }, i



    @classmethod

    def _parse_condition(cls, cond_str: str, line_num: int) -> dict:

        """Parse IF condition with optional AND/OR."""

        upper = cond_str.upper()



        for logic in [" AND ", " OR "]:

            if f' {logic.strip()} ' in upper:

                parts = re.split(rf'(?i)\s+{logic.strip()}\s+', cond_str, maxsplit=1)

                if len(parts) == 2:

                    return {

                        "type": logic.strip(),

                        "conditions": [

                            cls._parse_single_condition(parts[0], line_num),

                            cls._parse_single_condition(parts[1], line_num),

                        ]

                    }



        return cls._parse_single_condition(cond_str, line_num)



    @classmethod

    def _parse_single_condition(cls, s: str, line_num: int) -> dict:

        s = s.strip()

        # Try pattern: field OP value

        for op_str in ["<=", ">=", "!=", "=", "<", ">", "CONTAINS"]:

            pattern = rf'\s*{re.escape(op_str)}\s*'

            m = re.search(pattern, s, re.IGNORECASE)

            if m:

                field = s[:m.start()].strip()

                value = s[m.end():].strip()

                # Try parse value as number

                try:

                    value = int(value)

                except ValueError:

                    try:

                        value = float(value)

                    except ValueError:

                        value = value.strip('"').strip("'")

                return {

                    "type": cls.OP_MAP.get(op_str.upper(), "eq"),

                    "field": field,

                    "value": value,

                }

        raise DSLCompileError(f'Invalid condition: {s}', line_num)



    @classmethod

    def _parse_action(cls, s: str, line_num: int) -> Optional[dict]:

        s = s.strip()

        upper = s.upper()



        # SET var = value

        m = re.match(r'^SET\s+(\S+)\s*=\s*(.+)$', s, re.IGNORECASE)

        if m:

            val = cls._coerce_value(m.group(2).strip())

            return {"type": "set_variable", "target": m.group(1).strip(), "value": val}



        # CHANGE var BY delta

        m = re.match(r'^CHANGE\s+(\S+)\s+BY\s+(.+)$', s, re.IGNORECASE)

        if m:

            try:

                delta = int(m.group(2).strip())

            except ValueError:

                raise DSLCompileError(f'Invalid delta: {m.group(2)}', line_num)

            return {"type": "change_variable", "target": m.group(1).strip(), "delta": delta}



        # FORCE emotion|tone = value

        m = re.match(r'^FORCE\s+(\S+)\s*=\s*(.+)$', s, re.IGNORECASE)

        if m:

            val = m.group(2).strip().strip('"').strip("'")

            return {"type": "force_emotion", "target": m.group(1).strip(), "value": val}



        # UNLOCK memory_id

        m = re.match(r'^UNLOCK\s+(.+)$', s, re.IGNORECASE)

        if m:

            return {"type": "unlock_memory", "target": m.group(1).strip()}



        # ADD_ITEM item

        m = re.match(r'^ADD_ITEM\s+(.+)$', s, re.IGNORECASE)

        if m:

            return {"type": "add_item", "value": m.group(1).strip().strip('"').strip("'")}



        # REMOVE_ITEM item

        m = re.match(r'^REMOVE_ITEM\s+(.+)$', s, re.IGNORECASE)

        if m:

            return {"type": "remove_item", "value": m.group(1).strip().strip('"').strip("'")}



        # SET_BG scene

        m = re.match(r'^SET_BG\s+(.+)$', s, re.IGNORECASE)

        if m:

            return {"type": "set_bg", "value": m.group(1).strip().strip('"').strip("'")}



        # SET_PHASE n

        m = re.match(r'^SET_PHASE\s+(.+)$', s, re.IGNORECASE)

        if m:

            try:

                val = int(m.group(1).strip())

            except ValueError:

                raise DSLCompileError(f'Invalid phase: {m.group(1)}', line_num)

            return {"type": "set_phase", "value": val}



        raise DSLCompileError(f'Unknown action: {s}', line_num)



    @classmethod

    def _coerce_value(cls, val: str):

        val = val.strip().strip('"').strip("'")

        try:

            return int(val)

        except ValueError:

            try:

                return float(val)

            except ValueError:

                return val



    @classmethod

    def _make_id(cls, trigger: str, keywords: list, line: int) -> str:

        if keywords:

            return f'rule_{keywords[0]}_{line}'

        tid = trigger[:20].replace(" ", "_").replace('"', "").replace("'", "")

        return f'rule_{tid}_{line}'



    @classmethod

    def compile_file(cls, dsl_path: str) -> list:

        """Compile a .dsl file. Returns list of rules."""

        with open(dsl_path, "r", encoding="utf-8-sig") as f:

            source = f.read()

        return cls.compile(source)



    @classmethod

    def decompile(cls, rules: list) -> str:

        """Reverse: character_rules -> .dsl source string."""

        lines = []

        for rule in rules:

            trigger = rule.get("trigger", "")

            kws = rule.get("trigger_keywords", [])

            when_line = f'WHEN {trigger}'

            if kws:

                when_line += " KEYWORDS " + ", ".join(kws)

            lines.append(when_line)



            cond = rule.get("condition", {})

            if cond:

                cond_str = cls._decompile_condition(cond)

                lines.append(f'IF {cond_str}')



            lines.append("THEN")

            for action in rule.get("actions", []):

                action_str = cls._decompile_action(action)

                lines.append(f'  {action_str}')

            lines.append("")

        return "\n".join(lines)



    @classmethod

    def _decompile_condition(cls, cond: dict) -> str:

        if cond.get("type") in ("AND", "OR"):

            subs = [cls._decompile_condition(c) for c in cond.get("conditions", [])]

            return f' {cond['type']} '.join(subs)

        field = cond.get("field", "?")

        val = cond.get("value", "?")

        rev_op = {v: k for k, v in cls.OP_MAP.items()}

        op = rev_op.get(cond.get("type", ""), "=")

        return f'{field} {op} {val}'



    @classmethod

    def _decompile_action(cls, action: dict) -> str:

        atype = action.get("type", "")

        target = action.get("target", "")

        val = action.get("value")

        delta = action.get("delta")

        if atype == "set_variable":

            return f'SET {target} = {val}'

        elif atype == "change_variable":

            return f'CHANGE {target} BY {delta}'

        elif atype == "force_emotion":

            return f'FORCE {target} = {val}'

        elif atype == "unlock_memory":

            return f'UNLOCK {target}'

        elif atype == "add_item":

            return f'ADD_ITEM {val}'

        elif atype == "remove_item":

            return f'REMOVE_ITEM {val}'

        elif atype == "set_bg":

            return f'SET_BG {val}'

        elif atype == "set_phase":

            return f'SET_PHASE {val}'

        return f'# {atype}'



