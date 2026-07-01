"""
Kernelsoul - CharacterCardLoader v2.0
Supports 4 formats: V1, V2, V3, V4 folder. Auto-upgrade + DSL auto-compile.
"""
from __future__ import annotations
import json, os
from typing import Optional


class CharacterCardLoader:
    FIELD_MAPPING = {
        "name": "name", "description": "description",
        "personality": "personality", "first_mes": "first_message",
        "scenario": "scenario", "system_prompt": "system_prompt",
        "mes_example": "mes_example",
    }

    @classmethod
    def load(cls, file_path: str) -> dict:
        if os.path.isdir(file_path):
            return cls._load_v4_folder(file_path)
        with open(file_path, "r", encoding="utf-8-sig") as f:
            raw = json.load(f)
        spec = raw.get("spec", "")
        if spec == "chara_card_v3": return cls._load_v3(raw)
        elif spec == "chara_card_v2": return cls._load_v2(raw)
        elif "name" in raw: return cls._load_v1(raw)
        else: raise ValueError(f"Unrecognized format: {file_path}")

    @classmethod
    def _load_v4_folder(cls, folder_path: str) -> dict:
        result = {}
        data_path = os.path.join(folder_path, "character_data.json")
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8-sig") as f:
                result = json.load(f)
        rules_path = os.path.join(folder_path, "character_rules.json")
        dsl_path2 = os.path.join(folder_path, "character.dsl")
        if os.path.exists(dsl_path2):
            dsl_mtime = os.path.getmtime(dsl_path2)
            rules_mtime = os.path.getmtime(rules_path) if os.path.exists(rules_path) else 0
            if dsl_mtime > rules_mtime:
                try:
                    from dsl_compiler import DSLCompiler
                    compiled = DSLCompiler.compile_file(dsl_path2)
                    with open(rules_path, "w", encoding="utf-8") as f:
                        json.dump(compiled, f, ensure_ascii=False, indent=2)
                    result["character_rules"] = compiled
                    result["character_rules_source"] = "dsl"
                except Exception as e:
                    pass
            elif os.path.exists(rules_path):
                with open(rules_path, "r", encoding="utf-8-sig") as f:
                    result["character_rules"] = json.load(f)
        elif os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                result["character_rules"] = json.load(f)
        dsl_path = os.path.join(folder_path, "character.dsl")
        if os.path.exists(dsl_path):
            with open(dsl_path, "r", encoding="utf-8-sig") as f:
                result["character_rules_dsl"] = f.read()
        lorebook_path = os.path.join(folder_path, "character_lorebook.json")
        if os.path.exists(lorebook_path):
            with open(lorebook_path, "r", encoding="utf-8-sig") as f:
                result["character_lorebook"] = json.load(f)
        initstate_path = os.path.join(folder_path, "character_initstate.json")
        if os.path.exists(initstate_path):
            with open(initstate_path, "r", encoding="utf-8-sig") as f:
                result["character_initstate"] = json.load(f)
        meta_path = os.path.join(folder_path, "meta_cognition.txt")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8-sig") as f:
                result["meta_cognition_prompt"] = f.read()
        result.setdefault("spec", "chara_card_v4")
        result.setdefault("character_state", {"variables": {}})
        result.setdefault("character_rules", [])
        result.setdefault("conditional_memories", [])
        result.setdefault("meta_cognition_prompt", "")
        return result

    @classmethod
    def _load_v3(cls, raw: dict) -> dict:
        data = raw.get("data", {})
        result = {
            "spec": "chara_card_v3",
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "personality": data.get("personality", ""),
            "first_message": data.get("first_mes", ""),
            "scenario": data.get("scenario", ""),
            "system_prompt": data.get("system_prompt", ""),
            "mes_example": data.get("mes_example", ""),
            "alternate_greetings": data.get("alternate_greetings", []),
            "tags": data.get("tags", []),
            "creator": data.get("creator", ""),
            "creator_notes": data.get("creator_notes", ""),
        }
        extensions = data.get("extensions", {})
        engine_state = extensions.get("engine_state", {})
        if engine_state:
            result["initial_state"] = engine_state
        return cls._upgrade_to_v4(result)

    @classmethod
    def _load_v2(cls, raw: dict) -> dict:
        data = raw.get("data", raw)
        result = {
            "spec": "chara_card_v2", "name": data.get("name", ""),
            "description": data.get("description", ""), "personality": data.get("personality", ""),
            "first_message": data.get("first_mes", ""), "scenario": data.get("scenario", ""),
            "system_prompt": data.get("system_prompt", ""),
        }
        return cls._upgrade_to_v4(result)

    @classmethod
    def _load_v1(cls, raw: dict) -> dict:
        result = {
            "spec": "chara_card_v1", "name": raw.get("name", ""),
            "description": raw.get("description", ""), "personality": raw.get("personality", ""),
            "first_message": raw.get("first_mes", raw.get("first_message", "")),
            "scenario": raw.get("scenario", ""),
            "system_prompt": raw.get("system_prompt", raw.get("prompt", "")),
        }
        return cls._upgrade_to_v4(result)

    @classmethod
    def _upgrade_to_v4(cls, result: dict) -> dict:
        result.setdefault("character_state", {"variables": {}})
        result.setdefault("character_rules", [])
        result.setdefault("conditional_memories", [])
        result.setdefault("meta_cognition_prompt", "")
        result.setdefault("character_rules_dsl", "")
        result.setdefault("character_rules_source", "ai")
        result.setdefault("character_initstate", result.pop("initial_state", {}))
        return result
