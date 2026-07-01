"""

Kernelsoul - Core Engine v2.3

Architecture: config -> character -> paths -> state -> memory -> worldbook -> AI -> parser -> main loop

"""



import json, os, sys

from datetime import datetime, timezone



from game_state import GameState

from path_resolver import PathResolver

from state_manager import StateManager

from session_meta import SessionMeta, load_meta, save_meta

from parser_engine import ParserEngine
from semantic_engine import SemanticEngine
from semantic_renderer import SemanticRenderer
from phrase_library import PhraseLibrary

from memory_manager import MemoryManager

from worldbook_retriever import WorldBookRetriever, load_from_character

from worldbook_retriever import WorldBookRetriever, load_from_character

from plugin_manager import PluginManager

from evolution_trigger import EvolutionTrigger

from context_wrappers import get_context

from ai_bridge import AIBridge





# --- ConfigManager ---

class ConfigManager:

    def __init__(self, config_dir: str):

        self.config_dir = config_dir

        self.system = self._load_json('system.json')

        self.rules = self._load_json('rules.json')



    def _load_json(self, filename: str) -> dict:

        path = os.path.join(self.config_dir, filename)

        if os.path.exists(path):

            with open(path, "r", encoding="utf-8-sig") as f:

                return json.load(f)

        return {}





# --- WorldBookRetriever (minimal) ---

class WorldBookRetriever:

    def __init__(self, lorebook_path=None):

        self.entries = []

        if lorebook_path and os.path.exists(lorebook_path):

            with open(lorebook_path, "r", encoding="utf-8") as f:

                data = json.load(f)

                self.entries = data if isinstance(data, list) else data.get("entries", [])



    def query(self, user_input: str) -> list:

        hits = []

        for entry in self.entries:

            if isinstance(entry, dict):

                keys = entry.get("keys", entry.get("key", []))

                if isinstance(keys, str):

                    keys = [keys]

                content = entry.get("content", "")

                for k in keys:

                    if k in user_input:

                        hits.append(content)

                        break

        return hits





# --- CharacterStateManager (minimal) ---

class CharacterStateManager:

    def __init__(self, character_data: dict):

        self.variables = character_data.get("character_state", {}).get("variables", {})

        self.rules = character_data.get("character_rules", [])

        self._init_state()



    def _init_state(self):

        self.state = {}

        for name, var in self.variables.items():

            self.state[name] = var.get("default", 0)





# --- V4Engine ---

class V4Engine:

    def __init__(self, base_dir: str):

        self.base_dir = base_dir

        self.config_dir = os.path.join(base_dir, "configs")

        self.char_dir = os.path.join(base_dir, "characters")

        self.saves_dir = os.path.join(base_dir, "saves")

        self.config = ConfigManager(self.config_dir)

        self.char = self.config.system.get("last_character", "test_char")

        self.session = self.config.system.get("last_session", "session_01")

        self.paths = PathResolver(self.base_dir, self.char, self.session)

        self.state_mgr = StateManager(self.paths)

        self.bridge = AIBridge(self.config.system)

        self.memory = MemoryManager(self.paths, self.bridge)

        self.plugins = PluginManager(self.paths.get_plugins_dir())

        self.evolution = EvolutionTrigger(os.path.join(self.config_dir, "rules.json"))

        # v2.4 Semantic rendering engine
        self.semantic = SemanticEngine() 
        self.semantic_renderer = SemanticRenderer(self.semantic)
        self.render_mode = "direct"  # direct | semantic | hybrid

        self.parser = ParserEngine()

        self.worldbook = WorldBookRetriever()  # Replaced by load_character  # Replaced by load_character

        self.session_meta = self._load_or_create_meta()

        self.char_system_prompt = ""

        self.debug = False

        self._last_drafts = []  # For /roll /select /drafts



    def _load_or_create_meta(self):

        return load_meta(self.paths.get_meta_file())



    def load_character(self, char_id: str) -> dict:

        char_dir = os.path.join(self.char_dir, char_id)

        if os.path.isdir(char_dir):

            data_path = os.path.join(char_dir, "character_data.json")

            if os.path.exists(data_path):

                with open(data_path, "r", encoding="utf-8-sig") as f:

                    char_data = json.load(f)

                lore_path = os.path.join(char_dir, "character_lorebook.json")

                if os.path.exists(lore_path):

                    self.worldbook = load_from_character(char_dir, char_id) or WorldBookRetriever(lore_path)

                self.char_system_prompt = self._build_system_prompt(char_data)

                self.plugins.fire_hook("on_character_load", char_data)

                get_context("character_context").on_loaded(char_data)

                self.char = char_id

                self.paths.bind(char=char_id)

                return char_data

        # Hardcoded fallback

        char_data = {

            "name": char_id,

            "description": "A mysterious adventurer in a fantasy world.",

            "personality": "brave, witty, slightly sarcastic",

            "prompt": "You are a character in a role-playing game. Respond naturally in character using Chinese.",

            "first_message": "Hello, traveler.",

        }

        self.char_system_prompt = self._build_system_prompt(char_data)

        self.char = char_id

        self.paths.bind(char=char_id)

        return char_data



    def _build_system_prompt(self, char_data: dict) -> str:

        name = char_data.get("name", self.char)

        personality = char_data.get("personality", "")

        desc = char_data.get("description", "")

        custom_prompt = char_data.get("prompt", "")

        parts = [

            f'You are {name}, a character in an immersive narrative game.',

            f'Personality: {personality}' if personality else "",

            f'Background: {desc}' if desc else "",

            "",

            "[CORE RULES]",

            "Your only job is to write compelling narrative. Push the story forward like a novelist.",

            "ONLY when this round causes clear state changes should you append a JSON block at the end.",

            "If nothing changed, output narrative only - no JSON.",

            "",

            "[JSON FORMAT - only when state changed]",

            "Append a ```json``` code block at the very end of your response:",

            '{"hp": -5, "energy": -10, "goodwill": 2, "inventory_add": ["rusty key"], "inventory_remove": ["old contract"], "bg": "dark corridor", "emotion": "angry"}',

            "",

            "Field guide (only include changed fields):",

            "- hp: HP delta (negative=damage, positive=healing)",

            "- energy: energy delta",

            "- goodwill: relationship delta",

            "- money: gold delta",

            "- inventory_add / inventory_remove: lists of item names",

            "- bg: scene name when location changes",

            "- emotion: current emotion when it shifts",

            "- cg: CG trigger name if applicable",

            "",

            "[STRICTLY FORBIDDEN]",

            "- DO NOT output JSON inside natural language paragraphs",

            "- DO NOT say things like 'I cannot determine' or 'as an AI' - break immersion",

            "- DO NOT invent state changes just to produce JSON. No change = no JSON.",

            "",

            "[EXAMPLE - damage happened]",

            'Player: "I punch the wall."',

            "Your response:",

            "Your fist slams into the stone wall. Pain shoots through your knuckles. Dust falls from the impact.",

            "",

            "```json",

            '{"hp": -3, "emotion": "angry"}',

            "```",

            "",

            "[EXAMPLE - nothing changed]",

            'Player: "I look around the room."',

            "Your response:",

            "You scan the dim chamber. Faded tapestries line the walls. A single candle flickers on a stone altar. Nothing else catches your eye.",

            "(No JSON block - nothing changed.)",

            "",

            custom_prompt if custom_prompt else "",

        ]

        return "\n".join(p for p in parts if p)



    def _apply_semantic_renderer(self, state_deltas: dict, last_narrative: str = "") -> str:
        """Run semantic rendering and return prompt hints for injection."""
        if self.render_mode == "direct":
            return ""
        packet = self.semantic_renderer.render(
            state_deltas=state_deltas,
            current_state=self.state_mgr.state,
            last_narrative=last_narrative,
        )
        return self.semantic_renderer.build_prompt_hint(packet)

    def load_semantic_for_character(self, char_id: str):
        """Load character semantic config and build axes."""
        char_path = os.path.join(self.char_dir, char_id)
        if not os.path.isdir(char_path):
            return
        self.semantic.load_from_character(char_path)
        self.semantic.set_embed_fn(self.bridge.embed)
        if self.semantic.axis_names:
            try:
                self.semantic.build_axes()
                print(f"[SemanticEngine] Built {len(self.semantic.axis_names)} axes for {char_id}")
            except Exception as e:
                print(f"[SemanticEngine] Axis build failed: {e}")

    def build_prompt(self, user_input: str) -> tuple:

        s = self.state_mgr.state

        state_text = (

            f'HP: {s.hp}/{s.max_hp} | Energy: {s.energy} | '

            f'Goodwill: {s.goodwill} | Gold: {s.money} | '

            f"Emotion: {s.emotion} | Scene: {s.bg or 'default'} | "
            f"Inventory: {', '.join(s.inventory) if s.inventory else 'empty'}"
        )



        recent_path = self.paths.get_recent_log()

        recent_text = "(No previous dialogue)"

        if os.path.exists(recent_path):

            with open(recent_path, "r", encoding="utf-8") as f:

                recent_text = f.read().strip() or recent_text



        wb_hits = self.worldbook.query(user_input)

        wb_text = "\n".join(wb_hits) if wb_hits else "(None)"



        user_prompt = (

            f'[Current Game State]\n{state_text}\n\n'

            f'[World Info]\n{wb_text}\n\n'

            f'[Recent Dialogue]\n{recent_text}\n\n'

            f'[Player Action]\n{user_input}\n\n'

            "Respond in character. Include JSON state changes at end if needed."

        )

        return self.char_system_prompt, user_prompt



    def run_turn(self, user_input: str) -> dict:

        hp_before = self.state_mgr.state.hp

        system_prompt, user_prompt = self.build_prompt(user_input)

        self.plugins.fire_hook("on_user_input", user_input, self.state_mgr.state)

        raw_response = self.bridge.generate(system_prompt, user_prompt)

        parsed = self.parser.parse(raw_response)

        narrative = parsed["narrative"]

        state_changes = parsed["state_changes"]

        self.last_parse_method = parsed.get("method", "none")

        get_context("ai_context").on_response(narrative, state_changes)

        self.plugins.fire_hook("on_draft_created", narrative, state_changes)

        change_log = self.state_mgr.apply_state_changes(state_changes)



        timestamp = datetime.now(timezone.utc).isoformat()

        with open(self.paths.get_full_log(), "a", encoding="utf-8") as f:

            f.write(f'[{timestamp}] PLAYER: {user_input}\n')

            f.write(f'[{timestamp}] AI: {narrative}\n\n')

        self.plugins.fire_hook("on_state_change", state_changes, self.state_mgr.state)

        get_context("state_context").on_changed(state_changes, self.state_mgr.state)

        decisions = self.evolution.evaluate(self.state_mgr.state, getattr(self, "char_state_mgr", None), user_input, narrative)

        for d in decisions:

            get_context("rules_context").on_triggered(d["rule_id"], d["level"], d["description"], d["actions_executed"])

        self._refresh_recent_log()

        self.state_mgr.save()

        self.session_meta.increment_rounds()

        self.memory.maybe_compress(self.session_meta.total_rounds)

        save_meta(self.session_meta, self.paths.get_meta_file())

        self.plugins.fire_hook("on_round_end", narrative, state_changes, self.state_mgr.state)

        hp_after = self.state_mgr.state.hp

        self._last_drafts.append({

            "draft_id": len(self._last_drafts) + 1,

            "narrative": narrative,

            "state_changes": state_changes,

            "hp_before": hp_before,

            "hp_after": hp_after,

            "parse_method": self.last_parse_method,

        })

        if len(self._last_drafts) > 5:

            self._last_drafts = self._last_drafts[-5:]



        return {

            "narrative": narrative,

            "state_changes": state_changes,

            "change_log": change_log,

            "hp_before": hp_before,

            "hp_after": hp_after,

            "parse_method": self.last_parse_method,

        }



    def _refresh_recent_log(self):

        full_path = self.paths.get_full_log()

        if not os.path.exists(full_path):

            return

        with open(full_path, "r", encoding="utf-8") as f:

            all_lines = f.readlines()

        recent = all_lines[-20:] if len(all_lines) >= 20 else all_lines

        with open(self.paths.get_recent_log(), "w", encoding="utf-8") as f:

            f.writelines(recent)





# --- CLI ---

def main():

    base = os.path.dirname(os.path.abspath(__file__))

    print("=" * 50)

    print("  Kernelsoul Engine v2.3")

    print(f'  Base: {base}')

    print("=" * 50)

    engine = V4Engine(base)

    cfg = engine.config.system

    has_key = cfg.get("api_key", "").startswith("sk-")

    print(f"  API: {cfg.get('api_type', '?')} | Model: {cfg.get('model', '?')}")

    print(f"  Key: {'configured' if has_key else 'MISSING'}")

    # Load default character

    char_name = cfg.get("last_character", "test_char")

    engine.load_character(char_name)

    engine.plugins.fire_hook("on_engine_start")

    print(f'  Character: {char_name}')

    print(f'  Session: {engine.session} | Round: {engine.session_meta.total_rounds}')

    print("-" * 50)

    print("  Commands:")

    print("    /list         - Show available characters")

    print("    /character N  - Switch character (resets memory)")

    print("    /newgame      - Start fresh session")

    print("    /load S       - Load existing session")

    print("    /state        - Show game state")

    print("    /quit         - Save and exit")

    print("  Or just type to chat with the character.")

    print("-" * 50)

    while True:

        try:

            user_input = input("\nYou: ").strip()

        except (EOFError, KeyboardInterrupt):

            print("\nGoodbye!")

            engine.plugins.fire_hook("on_engine_stop")

            break

        if not user_input:

            continue

        # --- System commands ---

        if user_input == "/quit":

            print("Saving...")

            engine.plugins.fire_hook("on_session_end")

            engine.state_mgr.save()

            save_meta(engine.session_meta, engine.paths.get_meta_file())

            engine.plugins.fire_hook("on_engine_stop")

            break

        if user_input == "/plugin list":

            _cmd_plugin_list(engine)

            continue

        if user_input == "/plugin reload":

            _cmd_plugin_reload(engine)

            continue

        if user_input.startswith("/plugin enable "):

            _cmd_plugin_enable(engine, user_input.split()[-1])

            continue

        if user_input.startswith("/plugin disable "):

            _cmd_plugin_disable(engine, user_input.split()[-1])

            continue



        if user_input.startswith("/draft save "):

            _cmd_draft_save(engine, user_input)

            continue

        if user_input == "/saved":

            _cmd_saved_list(engine)

            continue

        if user_input.startswith("/saved load "):

            _cmd_saved_load(engine, user_input)

            continue

        if user_input.startswith("/rules export "):

            _cmd_rules_export(engine, user_input.split(" ", 2)[2])

            continue

        if user_input.startswith("/rules import "):

            _cmd_rules_import(engine, user_input.split(" ", 2)[2])

            continue

        if user_input.startswith("/export "):

            _cmd_export(engine, user_input.split(" ", 1)[1].strip())

            continue

        if user_input.startswith("/import "):

            _cmd_import(engine, user_input.split(" ", 1)[1].strip())

            continue



        if user_input == "/list":

            _cmd_list(engine)

            continue

        if user_input.startswith("/character "):

            target = user_input.split(" ", 1)[1].strip()

            _cmd_switch_character(engine, target)

            continue

        if user_input == "/newgame":

            engine.plugins.fire_hook("on_session_end")

            _cmd_newgame(engine)

            continue

        if user_input.startswith("/load "):

            target = user_input.split(" ", 1)[1].strip()

            _cmd_load(engine, target)

            continue

        if user_input == "/state":

            _cmd_state(engine)

            continue

        # --- Chat ---

        print("  (generating...)")

        result = engine.run_turn(user_input)

        _display_result(engine, result)

def _cmd_list(engine):

    """List available characters in characters/ directory."""

    char_dir = engine.char_dir

    found = []

    if os.path.isdir(char_dir):

        for name in sorted(os.listdir(char_dir)):

            full = os.path.join(char_dir, name)

            # V4 folder

            if os.path.isdir(full):

                dp = os.path.join(full, "character_data.json")

                if os.path.exists(dp):

                    try:

                        with open(dp, "r", encoding="utf-8-sig") as f:

                            d = json.load(f)

                        found.append((name, d.get("description", "")))

                    except:

                        found.append((name, ""))

            # Tavern JSON

            elif name.endswith(".json"):

                cid = name[:-5]

                try:

                    with open(full, "r", encoding="utf-8-sig") as f:

                        d = json.load(f)

                    dn = d.get("data", d)

                    found.append((cid, dn.get("description", "")))

                except:

                    found.append((cid, ""))

    if not found:

        print("  No characters found in characters/ directory.")

        print("  Place .json or V4 folder characters in:", char_dir)

        return

    print(f'  Characters ({len(found)}):')

    for cid, desc in found:

        marker = " < current" if cid == engine.char else ""

        d = desc[:60] + "..." if len(desc) > 60 else desc

        print(f'    {cid}{marker}')

        if d:

            print(f'      {d}')

def _cmd_switch_character(engine, char_id: str):

    """Switch character with full memory reset."""

    # Validate character exists

    char_dir = os.path.join(engine.char_dir, char_id)

    char_file = os.path.join(engine.char_dir, f'{char_id}.json')

    if not os.path.isdir(char_dir) and not os.path.exists(char_file):

        print(f'  Character "{char_id}" not found. Use /list to see available.')

        return

    engine.plugins.fire_hook("on_session_end")

    # Save current session before switching

    engine.state_mgr.save()

    save_meta(engine.session_meta, engine.paths.get_meta_file())

    # Generate new session ID

    import uuid

    new_session = f'session_{uuid.uuid4().hex[:8]}'

    # Memory reset

    engine.char = char_id

    engine.session = new_session

    engine.paths.bind(char=char_id, session=new_session)

    # Re-init MemoryManager & StateManager & SessionMeta

    engine.state_mgr = StateManager(engine.paths)

    engine.memory = MemoryManager(engine.paths, engine.bridge)

    engine.session_meta = SessionMeta.create(character_name=char_id, session_id=new_session)

    # Load new character

    try:

        char_data = engine.load_character(char_id)

        print(f"  Switched to: {char_data.get('name', char_id)}")
        print(f'  Session: {new_session} | State reset to defaults')

        print(f"  Personality: {char_data.get('personality', '?')}")
    except Exception as e:

        print(f'  Load failed: {e}')

def _cmd_newgame(engine):

    """Start a fresh session with current character, resetting state."""

    engine.state_mgr.save()

    save_meta(engine.session_meta, engine.paths.get_meta_file())

    import uuid

    new_session = f'session_{uuid.uuid4().hex[:8]}'

    engine.session = new_session

    engine.paths.bind(session=new_session)

    engine.state_mgr = StateManager(engine.paths)

    engine.memory = MemoryManager(engine.paths, engine.bridge)

    engine.session_meta = SessionMeta.create(character_name=engine.char, session_id=new_session)

    print(f'  New game started.')

    print(f'  Character: {engine.char} | Session: {new_session}')

    print(f'  HP: {engine.state_mgr.state.hp}/{engine.state_mgr.state.max_hp}')

def _cmd_load(engine, session_id: str):

    """Load an existing session for the current character."""

    old_session = engine.session

    engine.session = session_id

    engine.paths.bind(session=session_id)

    meta_path = engine.paths.get_meta_file()

    if not os.path.exists(meta_path):

        print(f"  Session {session_id} not found. Keeping current session.")

        engine.session = old_session

        engine.paths.bind(session=old_session)

        return

    # Reload state and meta

    engine.state_mgr = StateManager(engine.paths)

    engine.memory = MemoryManager(engine.paths, engine.bridge)

    engine.session_meta = load_meta(meta_path)

    engine.plugins.fire_hook("on_session_start")

    print(f'  Loaded session: {session_id}')

    print(f'  Character: {engine.session_meta.character_name}')

    print(f'  Rounds: {engine.session_meta.total_rounds}')

    print(f'  HP: {engine.state_mgr.state.hp}/{engine.state_mgr.state.max_hp}')

def _cmd_state(engine):

    """Display current game state."""

    s = engine.state_mgr.state

    print(f'  HP: {s.hp}/{s.max_hp} | Energy: {s.energy} | Goodwill: {s.goodwill}')

    print(f'  Gold: {s.money} | Emotion: {s.emotion} | Phase: {s.phase}')

    print(f"  Scene: {s.bg or 'default'} | CG: {s.cg or 'none'}")
    print(f"  Inventory: {s.inventory if s.inventory else 'empty'}")
    print(f'  Character: {engine.char} | Session: {engine.session}')

    print(f"  Rounds: {engine.session_meta.total_rounds} | Parse method: {getattr(engine, 'last_parse_method', '?')}")
def _display_result(engine, result):

    """Display AI response and state changes."""

    hp_delta = result["hp_after"] - result["hp_before"]

    hp_str = f" [HP {result['hp_before']}->{result['hp_after']}]" if hp_delta else ""

    print(f"\n  [{engine.char}] {result['narrative']}")

    if result['state_changes']:

        cs = ", ".join(f'{k}={v}' for k, v in result["state_changes"].items())

        print(f'  --- Changes{hp_str}: {cs}')

    elif hp_str:

        print(f'  ---{hp_str}')





# ════════════════════════════════════════

# CLI Command Functions

# ════════════════════════════════════════



def _cmd_help():

    print("  Available commands:")

    print("    /help                        - Show this help")

    print("    /list                        - List available characters")

    print("    /character <name>            - Switch character (resets memory)")

    print("    /newgame                     - Start fresh session")

    print("    /load <session>              - Load existing session")

    print("    /state                       - Show game state")

    print("    /quit                        - Save and exit")

    print("    /preset <name>               - Load system preset from configs/presets/")

    print("    /debug [on|off]              - Toggle debug mode")

    print("    /stop                        - Interrupt current generation")

    print("    /roll                        - Re-generate last turn")

    print("    /select <n>                  - Select and commit a draft")

    print("    /drafts                      - List all pending drafts")

    print("    /memory add <text>           - Add manual memory anchor")

    print("    /memory list                 - List manual memories")

    print("    /memory delete <n>           - Delete manual memory (1-based)")

    print("    /plugin list                  - List loaded plugins")

    print("    /plugin reload                - Hot-reload all plugins")

    print("    /plugin enable/disable <id>   - Enable/disable plugin")

    print("    /draft save <n>               - Save draft to collection")

    print("    /saved                        - List saved drafts")

    print("    /saved load <n>               - Load saved draft")

    print("    /rules export <file>          - Export rules")

    print("    /rules import <file>          - Import rules")

    print("    /export <session>             - Export session as ZIP")

    print("    /import <path>                - Import session ZIP")



def _cmd_preset(engine, name: str):

    preset_dir = os.path.join(engine.config_dir, "presets")

    target = os.path.join(preset_dir, name)

    if not os.path.exists(target):

        print(f"  Preset {name} not found in {preset_dir}")

        print(f"  Available: {os.listdir(preset_dir) if os.path.isdir(preset_dir) else 'none'}")
        return

    with open(target, "r", encoding="utf-8-sig") as f:

        content = f.read()

    engine.char_system_prompt = content

    print(f'  Preset loaded: {name} ({len(content)} chars)')



# -- Draft commands --

def _cmd_roll(engine):

    if not engine._last_drafts:

        print("  No previous turn to re-roll.")

        return

    last = engine._last_drafts[-1]

    print(f'  Re-rolling turn {engine.session_meta.total_rounds}...')

    # Rollback state to before last turn

    s = engine.state_mgr.state

    s.hp = last["hp_before"]

    saves_dir = engine.paths.get_session_dir()

    engine.state_mgr.save()

    print(f'  State rolled back. HP: {s.hp}')

    print(f"  Previous response was: {last['narrative'][:200]}...")



def _cmd_select(engine, user_input: str):

    parts = user_input.split()

    if len(parts) < 2:

        print("  Usage: /select <draft_number>")

        return

    try:

        n = int(parts[1])

    except ValueError:

        print("  Invalid draft number.")

        return

    if not engine._last_drafts or n < 1 or n > len(engine._last_drafts):

        print(f'  Draft {n} not available. Use /drafts to see list.')

        return

    draft = engine._last_drafts[n - 1]

    # Apply state changes from selected draft

    engine.state_mgr.apply_state_changes(draft["state_changes"])

    engine.state_mgr.save()

    print(f'  Draft {n} selected and committed.')

    print(f"  Narrative: {draft['narrative'][:200]}...")

    if draft["state_changes"]:

        print(f"  Changes: {draft['state_changes']}")



def _cmd_drafts(engine):

    if not engine._last_drafts:

        print("  No drafts available.")

        return

    print(f'  Drafts ({len(engine._last_drafts)}):')

    for d in engine._last_drafts:

        n = d["draft_id"]

        preview = d["narrative"][:80].replace("\n", " ")

        changes = ", ".join(f'{k}={v}' for k, v in d["state_changes"].items()) if d["state_changes"] else "none"

        print(f"    [{n}] HP: {d['hp_before']}->{d['hp_after']} | {changes} | {preview}...")



# -- Memory commands --

def _cmd_memory_add(engine, content: str):

    if not content.strip():

        print("  Usage: /memory add <text>")

        return

    engine.memory.add_manual_memory(content.strip())

    print(f'  Memory added: {content[:80]}...')



def _cmd_memory_list(engine):

    memories = engine.memory.get_manual_memories()

    if not memories:

        print("  No manual memories.")

        return

    print(f'  Manual memories ({len(memories)}):')

    for i, m in enumerate(memories, 1):

        print(f"    [{i}] {m['content'][:100]}")



def _cmd_plugin_list(engine):

    print("  " + engine.plugins.summary().replace("\n", "\n  "))



def _cmd_plugin_reload(engine):

    engine.plugins.reload()

    print("  Plugins reloaded.")

    _cmd_plugin_list(engine)



def _cmd_plugin_enable(engine, pid: str):

    engine.plugins.enable(pid)

    print(f"  Plugin {pid} enabled.")



def _cmd_plugin_disable(engine, pid: str):

    engine.plugins.disable(pid)

    print(f"  Plugin {pid} disabled.")





import shutil



def _cmd_draft_save(engine, user_input: str):

    parts = user_input.split()

    if len(parts) < 3:

        print("  Usage: /draft save <draft_number>")

        return

    try:

        n = int(parts[2])

    except ValueError:

        print("  Invalid draft number.")

        return

    if not engine._last_drafts or n < 1 or n > len(engine._last_drafts):

        print(f'  Draft {n} not available.')

        return

    draft = engine._last_drafts[n - 1]

    saved_dir = engine.paths.get_saved_drafts_dir()

    os.makedirs(saved_dir, exist_ok=True)

    fname = f"saved_draft_{draft['draft_id']}.json"

    fpath = os.path.join(saved_dir, fname)

    with open(fpath, "w", encoding="utf-8") as f:

        json.dump(draft, f, ensure_ascii=False, indent=2)

    print(f'  Draft {n} saved to {fname}')



def _cmd_saved_list(engine):

    saved_dir = engine.paths.get_saved_drafts_dir()

    if not os.path.isdir(saved_dir):

        print("  No saved drafts.")

        return

    files = sorted([f for f in os.listdir(saved_dir) if f.endswith(".json")])

    if not files:

        print("  No saved drafts.")

        return

    print(f'  Saved drafts ({len(files)}):')

    for i, fname in enumerate(files, 1):

        fpath = os.path.join(saved_dir, fname)

        with open(fpath, "r", encoding="utf-8") as f:

            d = json.load(f)

        preview = d["narrative"][:80].replace("\n", " ")

        print(f'    [{i}] {fname} | {preview}...')



def _cmd_saved_load(engine, user_input: str):

    parts = user_input.split()

    if len(parts) < 3:

        print("  Usage: /saved load <number>")

        return

    try:

        n = int(parts[2])

    except ValueError:

        print("  Invalid number.")

        return

    saved_dir = engine.paths.get_saved_drafts_dir()

    files = sorted([f for f in os.listdir(saved_dir) if f.endswith(".json")])

    if n < 1 or n > len(files):

        print(f'  Saved draft {n} not found.')

        return

    fpath = os.path.join(saved_dir, files[n - 1])

    with open(fpath, "r", encoding="utf-8") as f:

        draft = json.load(f)

    engine._last_drafts.append(draft)

    print(f"  Loaded saved draft: {draft['narrative'][:100]}...")



def _cmd_rules_export(engine, filename: str):

    if not filename:

        print("  Usage: /rules export <filename>")

        return

    rules_path = os.path.join(engine.config_dir, "rules.json")

    if not os.path.exists(rules_path):

        print("  No rules.json found.")

        return

    export_path = os.path.join(engine.config_dir, filename)

    shutil.copy2(rules_path, export_path)

    print(f'  Rules exported to: {export_path}')



def _cmd_rules_import(engine, filename: str):

    if not filename:

        print("  Usage: /rules import <filename>")

        return

    import_path = os.path.join(engine.config_dir, filename)

    if not os.path.exists(import_path):

        import_path = filename  # Try absolute path

    if not os.path.exists(import_path):

        print(f'  File not found: {filename}')

        return

    rules_path = os.path.join(engine.config_dir, "rules.json")

    with open(import_path, "r", encoding="utf-8-sig") as f:

        new_rules = json.load(f)

    with open(rules_path, "w", encoding="utf-8") as f:

        json.dump(new_rules, f, ensure_ascii=False, indent=2)

    engine.config.rules = new_rules

    print(f'  Rules imported from: {import_path}')



def _cmd_export(engine, session_id: str):

    """Export a session as ZIP archive."""

    import zipfile

    if not session_id:

        print("  Usage: /export <session_id>")

        return

    session_dir = os.path.join(engine.paths.base_saves, engine.char, session_id)

    if not os.path.isdir(session_dir):

        print(f"  Session {session_id} not found.")

        return

    export_dir = os.path.join(engine.base_dir, "exports")

    os.makedirs(export_dir, exist_ok=True)

    zip_path = os.path.join(export_dir, f'{engine.char}_{session_id}.zip')

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:

        for root, dirs, files in os.walk(session_dir):

            for fname in files:

                fpath = os.path.join(root, fname)

                arcname = os.path.relpath(fpath, session_dir)

                zf.write(fpath, arcname)

    size_kb = os.path.getsize(zip_path) / 1024

    print(f'  Exported: {zip_path} ({size_kb:.1f} KB)')



def _cmd_import(engine, zip_path: str):

    """Import a session from ZIP archive."""

    import zipfile

    if not os.path.exists(zip_path):

        print(f'  File not found: {zip_path}')

        return

    # Extract session_id from filename

    basename = os.path.splitext(os.path.basename(zip_path))[0]

    parts = basename.rsplit("_", 1)

    if len(parts) == 2:

        char_name, session_id = parts

    else:

        session_id = f'session_imported'

        char_name = engine.char

    session_dir = os.path.join(engine.paths.base_saves, char_name, session_id)

    os.makedirs(session_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:

        zf.extractall(session_dir)

    print(f'  Imported session: {char_name}/{session_id}')

    print(f'  Use /load {session_id} to play it.')





def _cmd_memory_delete(engine, idx_str: str):

    try:

        idx = int(idx_str) - 1

    except ValueError:

        print("  Usage: /memory delete <number>")

        return

    memories = engine.memory.get_manual_memories()

    if idx < 0 or idx >= len(memories):

        print(f'  Memory {idx + 1} not found.')

        return

    deleted = memories.pop(idx)

    path = engine.paths.get_manual_memory()

    with open(path, "w", encoding="utf-8") as f:

        json.dump(memories, f, ensure_ascii=False, indent=2)

    print(f"  Deleted: {deleted['content'][:80]}")





if __name__ == "__main__":

    main()