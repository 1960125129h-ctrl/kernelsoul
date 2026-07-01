# Kernelsoul Development & Execution Manual v2.4

--- **⚠️ Translation Notice**: The author is not a native English speaker. This English README was machine-translated and may contain awkward phrasing or terminology errors. Corrections and pull requests are warmly welcomed. The [Chinese version](README.md) is the authoritative reference.

## Quick Start (5 Minutes to Get Started)

**Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Step 2: Configure API**

Edit `/configs/system.json` and fill in your API key:

```json
{
  "api_type": "deepseek", /* or other providers */
  "api_key": "sk-your-key-here",
  "model": "deepseek-chat",
  "max_tokens": 4096
}
```

**Step 3: Place Character Cards**

Place downloaded character card JSON files in the `/characters/` directory. Tavern format is supported.

**Step 4: Start the Engine**

```bash
python core_engine.py
```

---

## Directory Structure

```
Kernelsoul/
├── /configs/                        # [Configuration Layer]
│   ├── system.json                  # API key, model name, token window
│   ├── rules.json                   # Core algorithm & evolution rules
│   ├── compression_prompt_light.txt  # Lightweight compression template (10 rounds, 200-char limit) [v2.3]
│   ├── compression_prompt_deep.txt   # Deep compression template (50 rounds, 2500-char limit) [v2.3]
│   ├── compression_prompt_merge.txt  # Lightweight summary merging template [v2.3.1]
│   ├── compression_prompt_epic.txt   # Epic compression template (200 rounds, 5000-char limit) [v2.3.1]
│   ├── fallback_prompt.txt          # Simplified prompt for consecutive JSON parse failures [v1.3]
│   ├── rule_compiler_prompt.txt     # AI rule compiler template [v2.0]
│   └── /presets/                    # Preset jailbreak pool
├── /characters/                     # [Character & Worldbuilding Layer]
│   │
│   │   # === Kernelsoul Character Folders ===
│   └── /{character_id}/             # Kernelsoul character folder (standard)
│       ├── character.dsl            # DSL source (single source of truth)
│       ├── character_rules.json     # Compiled output
│       ├── character_data.json      # Character base data
│       ├── character_lorebook.json  # Lorebook (optional)
│       ├── character_initstate.json # Sidecar initial state (optional)
│       ├── character_semantic.json  # Semantic rendering config (optional) [v2.4]
│       ├── meta_cognition.txt       # Meta-cognition prompt
│       └── /assets/                 # Character-specific assets (optional)
│   │
│   │   # === Legacy Compatible Character Cards (V3 Transition Format) ===
│   ├── demon_hotel.json             # Character card example 1 (little demon, with name, description, personality, prompt, initial state)
│   ├── demon_hotel_lorebook.json    # Lorebook for character card 1
│   └── cyber_elf.json               # Character card example 2 (cyber elf)
├── /assets/                         # [Art Assets Layer] (can be empty initially, auto-degrades to plain text)
├── /saves/                          # [Multi-character Multi-session Save Pool]
│   │
│   │   # === Universal Save Structure ===
│   └── /{character_name}/{session_id}/
│       ├── /history/                # Full history archive (append-only, permanent) [v1.2]
│       │   ├── full_log.txt         # All confirmed dialogue text since genesis, append-only
│       │   └── full_memory.json     # Summary chain from all past compressions, append-only
│       ├── /context/                # Runtime workspace (dynamic trimming) [v1.2]
│       │   ├── recent_log.txt       # Last 10 rounds of confirmed dialogue, for context packing
│       │   ├── working_memory.json  # Current round's filtered summary collection
│       │   ├── manual_memory.json   # Manual memory anchors (persistent context injection)
│       │   ├── /drafts/             # Temporary draft area (round-level, pending confirmation) [v1.2]
│       │   └── /saved_drafts/       # Saved draft area (manually saved drafts, not cleared on submit) [v1.6]
│       ├── state.sav                # Precise game state (updated only on submit)
│       └── session_meta.json        # Metadata (includes data version for archive migration) [v1.3]
│   │
│   │   # === Specific Example: Little Demon Character Playthrough 1 ===
│   └── /demon_hotel/                # [Little Demon's Character-Specific Save Folder]
│       └── /session_01/             # Playthrough 1
│           ├── /history/
│           │   ├── full_log.txt
│           │   └── full_memory.json
│           ├── /context/
│           │   ├── recent_log.txt
│           │   ├── working_memory.json
│           │   └── /drafts/
│           │       ├── draft_001.json
│           │       ├── draft_002.json
│           │       └── ...
│           ├── state.sav
│           └── session_meta.json
├── /plugins/                        # Plugin ecosystem [v1.3]
│   │
│   │   # === Universal Plugin Structure ===
│   └── /{plugin_id}/
│       ├── manifest.json            # Plugin manifest (required)
│       └── __init__.py              # Plugin entry point (required)
│   │
│   │   # === Official Example Plugins ===
│   ├── /example_stats_tracker/      # Stats tracker
│   │   ├── manifest.json
│   │   └── __init__.py
│   └── /example_auto_save/          # Auto-save
│       ├── manifest.json
│       └── __init__.py
└── core_engine.py                   # Engine main entry point
```

---

## Kernelsoul Character File Standard Convention (v2.3)

In the `/characters/` directory, each character is organized as a folder containing the following standard files:

```
/characters/
└── /innkeeper/          # Folder named after character ID
    ├── character.dsl             # DSL source (version-controllable, single source of truth)
    ├── character_rules.json      # Compiled output (generated by DSLCompiler from .dsl)
    ├── character_data.json       # Character base data (name, description, personality, prompt, etc.)
    ├── character_lorebook.json   # Lorebook (optional)
    ├── character_initstate.json  # Sidecar initial state file (optional)
    ├── meta_cognition.txt        # Meta-cognition prompt (natural language)
    └── /assets/                  # Character-specific art assets (optional)
        ├── avatar.png            # Avatar
        └── full_body.png         # Full-body portrait
```

### File Responsibilities

| File | Type | Responsibility | Version Control |
|------|------|---------------|-----------------|
| character.dsl | Source | DSL source for character behavior logic. Single source of truth. | Yes |
| character_rules.json | Compiled output | JSON rules compiled from .dsl by DSLCompiler. Should not be manually edited. | No (generated by compilation) |
| character_data.json | Data | Character base attributes: name, description, personality, prompt, first_mes, etc. | Yes |
| character_lorebook.json | Data | Lorebook entries. | Yes |
| character_initstate.json | Data | Sidecar initial game state. | Yes |
| meta_cognition.txt | Source | Meta-cognition "superego" prompt. | Yes |

### Load Priority (Engine Startup)

1. If `character.dsl` exists and is newer than `character_rules.json`, auto-recompile.
2. If only `character_rules.json` exists without .dsl, the engine attempts decompilation to generate .dsl (via `DSLCompiler.decompile()`).
3. If both exist and .dsl is newer, the .dsl compilation result overwrites character_rules.json.
4. `character_data.json` is required; the rest are optional.

Note: On engine startup, `last_character` and `last_session` are read from `system.json` to auto-load the previous session's progress.

---

## Multi-Character Scene Support (V2.0 Planning, v1.6 Design Reserve)

The following content is not in the MVP scope; it is reserved data structure and interface design for V2.0.

**Reserved fields:** `session_meta.json` can contain `active_characters` (list of present character IDs) and `primary_character` (the main character in the current dialogue).

**Reserved module:** A future "Scene Character Manager" could maintain independent sub-state blocks for each present character, manage auto-interaction and interjection logic between characters, and handle entrance/exit events.

**Reserved AI prompt structure:**
```
Characters in the current scene:
- {Character1 Name}: {Character1 current emotion}, talking to the player.
- {Character2 Name}: {Character2 current emotion}, observing nearby.
{Character2 Name} may interject at appropriate times.
```

**Current compatibility strategy:** During MVP, `active_characters` defaults to containing only the current character. Users can simulate other characters' presence via `/memory add`.

---

## III. Core Data Model & Communication Protocol

### 3.1 GameState Strongly-Typed Definition

All modules share the same GameState instance, defined using Python `@dataclass` with a strictly limited whitelist of fields:

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class GameState:
    # AI-modifiable fields (whitelist)
    hp: int = 100
    energy: int = 100
    goodwill: int = 0
    money: int = 0
    inventory: List[str] = field(default_factory=list)
    bg: str = ""           # Current background description
    emotion: str = "neutral" # Emotion label
    cg: str = ""           # Current triggered CG name

    # Read-only fields (AI cannot modify)
    phase: int = 1
    max_hp: int = 100
```

- Serialization: `state.sav` is stored in JSON format (human-readable).
- On load, GameState is reconstructed from JSON; missing fields use default values.
- Before any module modifies GameState, it must go through controlled methods provided by the State Manager (e.g., `modify_hp(delta)`) to prevent unauthorized access.

### 3.2 AI Response Protocol (Natural Language First, JSON Optional Enhancement)

The AI is instructed to prioritize natural language narrative, focusing on writing compelling storylines. **If and only if** the AI determines that the narrative has led to a clear state change, it may append a Markdown code block (wrapped in ```json) at the end of the response to describe these changes.

Format:

```json
{
  "hp": -5,
  "energy": -10,
  "goodwill": 2,
  "money": 0,
  "inventory_add": ["moldy bread"],
  "inventory_remove": ["little demon's contract"],
  "bg": "dark corridor",
  "emotion": "angry",
  "cg": "cg_door_open"
}
```

- All keys in `state_changes` must belong to the AI-modifiable whitelist. The parser performs strict validation: illegal fields are discarded, and only legal changes are kept.
- `inventory_add/remove` processing order: remove is executed first, then add, to avoid dependency conflicts.
- Inventory fault tolerance: if the item to remove does not exist, the removal command is ignored and logged — no error, no interruption.
- If the AI does not provide JSON, or if the parser fails to extract it, the round proceeds with narrative only, and the game state remains unchanged. **Narrative always comes first.**

**New Paragraph:**

#### Recommended System Prompt Template

When constructing AI requests, the following hard-instruction style prompt template is recommended (stored in `/configs/system_prompt_template.txt`):

```
You are {character name}, a character in an immersive narrative game.

[Core Rules]
Your only task is to write compelling narrative, advancing the story like a novelist.
If and only if this round's narrative leads to a clear state change,
you MUST append a JSON state block at the end of your response.

[JSON Format Requirements]
If appending JSON, wrap it in a json code block, placed at the very end of the response.
Format: {"hp": -5, "energy": 0}

Field descriptions (only write changed fields):
  hp: HP change (negative = damage, positive = recovery)
  energy: Energy change
  goodwill: Affection change
  money: Money change
  inventory_add: List of obtained items
  inventory_remove: List of lost items
  character_state: Internal character state changes, e.g., {"current_tone": "sarcastic"}

[Strictly Prohibited]
- Do NOT output JSON within natural language paragraphs.
- Do NOT use phrases like "I can't determine" or "As an AI I'm not sure" that break immersion.
- Do NOT fabricate non-existent state changes just to produce JSON.
  If there is no change in the narrative, output ONLY narrative, no JSON.
```

Note: This template forms a two-level system with `/configs/fallback_prompt.txt` — formal dialogue uses this template, and after consecutive JSON failures, the system automatically switches to the degraded template.

---

**Relationship with existing content:**

- The whitelist rules, inventory logic, and fault tolerance descriptions in Section 3.2 remain **completely unchanged**.
- The new Prompt template is an **implementation recommendation**, telling developers and creators "how to make the AI follow this protocol."
- The template itself is stored in `/configs/system_prompt_template.txt`; Section 3.2 only references it and explains its design intent.
- This insertion does not change any existing rules — it only converts the abstract protocol into directly usable Prompt text.

### 3.3 Draft File Structure

Each draft file `draft_xxx.json` stores a complete data packet from one AI generation:

```json
{
  "draft_id": 1,
  "raw_response": "Raw text returned by AI (containing narrative and optional trailing JSON code block)",
  "parsed": {
    "narrative": "Extracted plain-text story",
    "state_changes": { ... }
  },
  "timestamp": "2026-06-28T14:00:00"
}
```

- `state_changes` may be an empty object `{}`, indicating no state change in this round.

### 3.4 Session Metadata Structure (session_meta.json)

```json
{
  "data_version": 1,
  "created_at": "2026-06-28T14:00:00",
  "last_saved_at": "2026-06-28T15:45:00",
  "total_rounds": 67,
  "character_name": "demon_hotel",
  "session_id": "session_01"
}
```

### 3.5 History Summary Chain Structure (full_memory.json)

```json
{
  "data_version": 1,
  "entries": [
    {
      "compression_id": 1,
      "round_range": "1-50",
      "summary": "The player awoke in the Little Demon Hotel and met the front desk receptionist Lilith...",
      "timestamp": "2026-06-28T14:00:00"
    },
    {
      "compression_id": 2,
      "round_range": "51-100",
      "summary": "The player went to investigate the rooftop and discovered a hidden portal...",
      "timestamp": "2026-06-28T15:30:00"
    }
  ]
}
```

### 3.6 Kernelsoul Character Card Extension Structure (v2.0)

Kernelsoul character cards are identified by `spec: "chara_card_v4"`, adding three core extension blocks on top of V2/V3 compatible fields: `character_state` (character-specific dynamic variables), `character_rules` (behavior state machine), and `conditional_memories` (conditional knowledge).

**Complete Structure:**

```json
{
  "spec": "chara_card_v4",
  "name": "Lilith the Little Demon",
  "character_state": {
    "variables": {
      "mood": { "type": "int", "range": [-10, 10], "default": 0, "description": "Mood value" },
      "trust_player": { "type": "int", "range": [0, 100], "default": 20, "description": "Trust in player" },
      "fatigue": { "type": "int", "range": [0, 100], "default": 0, "description": "Fatigue level" },
      "suspicion": { "type": "int", "range": [0, 100], "default": 30, "description": "Suspicion level" },
      "current_tone": { "type": "string", "default": "neutral", "description": "Current speaking tone" }
    }
  },
  "character_rules": [
    {
      "id": "praise_king_trigger",
      "trigger": "Player mentions or praises the king",
      "condition": { "type": "lt", "field": "character_state.mood", "value": 0 },
      "action": [
        { "type": "set_variable", "target": "character_state.current_tone", "value": "sarcastic" },
        { "type": "set_variable_delta", "target": "character_state.suspicion", "delta": 10 },
        { "type": "force_emotion", "value": "resentful" }
      ],
      "description": "When mood is low and the king is praised, force sarcastic tone"
    }
  ],
  "conditional_memories": [
    {
      "id": "lilith_betrayal_night",
      "content": "A hundred years ago, Lilith was betrayed by her most trusted knight and lost her left wing on the night of the full moon.",
      "unlock_condition": { "type": "gte", "field": "character_state.trust_player", "value": 60 },
      "unlocked": false
    }
  ],
  "meta_cognition_prompt": "You are a method actor playing {name}. Constantly check whether you are deviating from the character setting. If you feel you are about to break character, naturally steer the conversation back in a way consistent with the character.",
  "initial_state": { "hp": 100, "max_hp": 100 },
  "character_rules_dsl": "WHEN player mentions \"king\" IF mood < 0 THEN SET current_tone = \"sarcastic\" ...",
  "character_rules_source": "dsl"
}
```

**Field Descriptions:**

- `character_state.variables`: Character-specific dynamic variables, independent of GameState. AI can read and write; engine code can read and enforce.
- `character_rules`: Character behavior state machine. `trigger` is the trigger description, `condition` is the judgment condition, `action` is the enforced action.
- `conditional_memories`: Conditional knowledge. When `unlocked: false`, it is not injected into the Prompt until the unlock condition is met.
- `meta_cognition_prompt`: The character's "superego" prompt, injected at the end of the system preset.
- `character_rules_dsl` (optional, v2.1): DSL source text. If present, the engine prioritizes this for compiling `character_rules`.
- `character_rules_source` (optional, v2.1): Marks the rule source. "dsl" means hand-written DSL, "ai" means AI-generated, "mixed" means hybrid.

**Relationship with GameState:** GameState is the cross-character game world state; `character_state` is the character's internal psychological state. The two are maintained by different managers and merged during context packing.

**Backward Compatibility:** V2/V3 character cards automatically have default values filled in on load, without affecting existing character card usage.

---

## IV. Core Engine Module Responsibilities

| Module Class | Responsibilities & Special Settings | AI Dependency |
|---|---|---|
| Config Manager | Loads system.json, rules.json, compression prompt templates, fallback prompt templates, preset list; reads last_character, last_session to initialize paths | No |
| CharacterCardLoader | Auto-identifies and parses multiple character card formats (Tavern format preferred); extracts name, description, personality, prompt, initial state, first_mes fields; maps to engine internal structure; supports lorebook associated loading | No |
| PathResolver | Dynamically concatenates all paths (history, context, drafts, plugin data); auto-creates non-existent folders; rebinds new instance when switching character/session | No |
| State Manager | Reads/writes state.sav via PathResolver; provides `apply_state_changes(changes_dict)` method with internal whitelist validation and add/subtract/inventory operations; built-in inventory fault tolerance: ignores remove on non-existent item and logs; only invoked on user confirmation submit | Absolutely No |
| Memory Manager | Maintains dual-track archive: daily append to history/full_log.txt; refreshes context/recent_log.txt; executes dual-layer compression | Yes (summary generation) |
| Lorebook Retriever | Pure code module; performs keyword matching on player input against the `_lorebook.json` file; returns matched entry list | Absolutely No |
| AI Bridge | Combines current preset, character card settings, lorebook entries, textified GameState, working_memory (last 3 summaries), recent_log (last 10 dialogue rounds) into final Prompt; calls LLM API; temporarily stores generated result as draft without writing to history; supports auto-switch to degraded prompt template on consecutive JSON extraction failures | Yes |
| Parser Engine | Smart extraction of state changes from AI response text. Three-stage strategy: 1) extract ```json code block; 2) max brace backtracking; 3) natural language simple rule matching. Validates field whitelist; returns empty changes on failure. Never crashes | No |
| Evolution Trigger | After user confirmation submit in main loop, automatically scans rules.json for evolution rules; forcibly modifies GameState read-only fields (e.g., phase) if conditions met | Absolutely No |
| UI Observer | Monitors GameState changes; displays narrative during draft preview; manages streaming render buffer; concatenates token stream from AI Bridge into narrative segments; controls typewriter animation speed and state; monitors user skip animation or stop generation triggers; auto-degrades to plain text if /assets/ is empty | No |
| Plugin Manager | Scans /plugins/ directory; validates manifest.json; registers lifecycle hooks; provides sandbox isolation and /plugin hot-reload command | No |
| Main Loop Entry | Async event-driven; intercepts system commands starting with `/` for dispatch; manages draft generation/selection/submission flow; triggers plugin hooks at key nodes | No |
| CharacterStateManager | Maintains current character's `character_state` variables; executes `character_rules`; manages `conditional_memories` unlocking; runs only after draft submission | Absolutely No |
| AI RuleCompiler (RuleCompiler) | Compiles creator's natural language character script into Kernelsoul character card's `character_rules` and `conditional_memories` JSON; used only during character card creation, not a runtime module | Yes |
| DSL Compiler (DSLCompiler) | Deterministically compiles SLL script logic language source into `character_rules` JSON; supports reverse compilation (JSON → DSL); does not depend on AI | Absolutely No |

**Future Module Reserve (V2.0):** Scene Character Manager — maintains independent sub-state blocks for each present character; manages auto-interaction and interjection logic between characters; handles entrance/exit events.

### 4.1 PathResolver Complete Implementation

```python
import os

class PathResolver:
    def __init__(self, base_saves: str, base_configs: str, active_char: str, active_session: str):
        self.base_saves = base_saves
        self.base_configs = base_configs
        self.char = active_char
        self.session = active_session
        self._ensure_dirs()

    def _ensure_dirs(self):
        os.makedirs(self.get_session_dir(), exist_ok=True)
        os.makedirs(self.get_history_dir(), exist_ok=True)
        os.makedirs(self.get_context_dir(), exist_ok=True)
        os.makedirs(self.get_drafts_dir(), exist_ok=True)

    def get_session_dir(self):
        return os.path.join(self.base_saves, self.char, self.session)

    def get_history_dir(self):
        return os.path.join(self.get_session_dir(), "history")

    def get_context_dir(self):
        return os.path.join(self.get_session_dir(), "context")

    def get_drafts_dir(self):
        return os.path.join(self.get_context_dir(), "drafts")

    def get_state_file(self):
        return os.path.join(self.get_session_dir(), "state.sav")

    def get_meta_file(self):
        return os.path.join(self.get_session_dir(), "session_meta.json")

    def get_full_log(self):
        return os.path.join(self.get_history_dir(), "full_log.txt")

    def get_full_memory(self):
        return os.path.join(self.get_history_dir(), "full_memory.json")

    def get_recent_log(self):
        return os.path.join(self.get_context_dir(), "recent_log.txt")

    def get_working_memory(self):
        return os.path.join(self.get_context_dir(), "working_memory.json")

    def get_compression_prompt(self):
        return os.path.join(self.base_configs, "compression_prompt.txt")

    def get_fallback_prompt(self):
        return os.path.join(self.base_configs, "fallback_prompt.txt")
```

---

### 4.2 CharacterCardLoader

#### 4.2.1 Design Purpose

SillyTavern (Tavern) JSON character card format has become the universal standard in the AI roleplay community. This engine must achieve first-class compatibility with this format, allowing zero-friction import of the community's vast character resources.

#### 4.2.2 Supported Formats

| Format | Priority | Identification Method |
|--------|----------|----------------------|
| SillyTavern V3 Spec | 1 | JSON contains `spec` field with value `"chara_card_v3"`, data nested in `data` object |
| SillyTavern V2 Spec | 2 | JSON contains `spec` field with value `"chara_card_v2"` |
| SillyTavern V1 | 3 | JSON contains `name`, `description` fields, no `spec` field |
| Engine Native Kernelsoul Format (v4) | 4 | Folder contains `character.dsl` + `character_data.json` + `character_rules.json` |

#### 4.2.3 Field Mapping Logic

```python
class CharacterCardLoader:
    """Character card loader: maps external formats to engine internal structure"""
    FIELD_MAPPING = {
        "name": "name", "description": "description", "personality": "personality",
        "first_message": "first_mes", "scenario": "scenario", "prompt": "system_prompt",
    }

    @classmethod
    def load(cls, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        spec = raw.get("spec", "")
        if spec == "chara_card_v2": return cls._load_tavern_v2(raw)
        elif "name" in raw: return cls._load_tavern_v1(raw)
        else: return cls._load_native(raw)

    @classmethod
    def _load_tavern_v2(cls, raw: dict) -> dict:
        data = raw.get("data", {})
        return {
            "name": data.get("name", ""), "description": data.get("description", ""),
            "personality": data.get("personality", ""), "prompt": data.get("system_prompt", ""),
            "first_message": data.get("first_mes", ""), "scenario": data.get("scenario", ""),
            "initial_state": cls._extract_initial_state(data),
            "lorebook_file": cls._find_lorebook(os.path.dirname(file_path), data.get("name", ""))
        }

    @classmethod
    def _extract_initial_state(cls, data: dict) -> dict:
        ext = data.get("extensions", {})
        es = ext.get("engine_state", {})
        return {
            "hp": es.get("hp", 100), "max_hp": es.get("max_hp", 100),
            "energy": es.get("energy", 100), "goodwill": es.get("goodwill", 0),
            "phase": es.get("phase", 1)
        }

    @classmethod
    def _find_lorebook(cls, char_dir: str, char_name: str) -> str | None:
        for c in [f"{char_name}_lorebook.json", f"{char_name}_worldbook.json",
                   "worldbook.json", "lorebook.json"]:
            p = os.path.join(char_dir, c)
            if os.path.exists(p): return p
        return None
```

#### 4.2.4 Import Flow

1. Player places Tavern character card JSON file in `/characters/` directory.
2. On engine startup, CharacterCardLoader auto-scans and identifies format.
3. If character card comes with a lorebook, Loader auto-associates and loads.
4. Engine generates missing default fields for each character card.
5. Character list (`/list`) displays normally.

#### 4.2.5 Compatibility Commitment

- The engine will not modify original character card files. All mapping and supplementary data is done in memory and in save data only.
- When Tavern format upgrades in the future, Loader adapts through version numbers, maintaining backward compatibility.

#### 4.2.6 Sidecar Initial State File (v1.6)

Tavern character cards typically don't include game state definitions. When loading a character card, the engine simultaneously checks for a sidecar initial state file in the same directory.

**File naming convention:** `{character_card_filename_without_ext}_initstate.json`

Example:
- Character card: `/characters/demon_hotel.json`
- Initial state: `/characters/demon_hotel_initstate.json`

**File format:**

```json
{
  "hp": 80,
  "max_hp": 80,
  "energy": 50,
  "goodwill": -10,
  "money": 200,
  "phase": 1,
  "inventory": ["rusty dagger", "worn map"],
  "bg": "dim hotel lobby",
  "emotion": "vigilant"
}
```

**Load priority (high to low):**
1. Sidecar `_initstate.json` file (if exists)
2. `extensions.engine_state` field within character card (if exists)
3. Engine defaults (default values defined in GameState class)

**Implementation logic:**

```python
@classmethod
def _load_initial_state(cls, char_file_path: str, char_data: dict) -> dict:
    """Load initial state by priority"""
    base_path = os.path.splitext(char_file_path)[0]
    sidecar_path = f"{base_path}_initstate.json"
    if os.path.exists(sidecar_path):
        with open(sidecar_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    extensions = char_data.get("extensions", {})
    engine_state = extensions.get("engine_state", {})
    if engine_state:
        return engine_state
    return {}
```

**Design advantage:** Players can customize initial game state per character without modifying the original character card file. Sidecar files can be independently shared and backed up without breaking cross-platform compatibility of the original card.

#### 4.2.7 Character Card Version Identification (v2.0, v2.3 revision)

CharacterCardLoader automatically identifies the character card version through the `spec` field and file structure:

| spec Value | Version | Characteristics |
|------------|---------|-----------------|
| `"chara_card_v3"` | V3 | `data` nested structure; includes `alternate_greetings`, `tags`, `creator`, `mes_example` fields; `extensions` object may contain `engine_state` |
| `"chara_card_v2"` | V2 | Flat JSON structure; static character description; no `data` nesting; no state extension fields |
| No `spec`, has `name` + `description` | V1 | Minimal character card; only basic description fields; no state or rule extensions |
| Folder contains `character.dsl` + `character_data.json` + `character_rules.json` | Kernelsoul Native | Includes `character_state`, `character_rules`, `conditional_memories`, `meta_cognition_prompt`; DSL source as single source of truth |

**Upgrade fill logic:**

When loading V1/V2/V3 character cards, the engine automatically fills in Kernelsoul field defaults (empty `character_state`, empty `character_rules`, empty `conditional_memories`, default `meta_cognition_prompt`).

At runtime, CharacterStateManager performs no operations on ruleless character cards, with zero overhead.

The `extensions.engine_state` field of V3 character cards is auto-extracted as the initial game state.

Creators can upgrade any version character card to Kernelsoul (v4) at any time: add `character_state` and `character_rules` extension fields in the editor, or create a `character.dsl` file and modify the `spec`.

#### 4.2.8 V3 Character Card Format Support (v2.3)

**V3 Format Identification**

V3 character cards are identified by the `"spec"` field:

```json
{
  "spec": "chara_card_v3",
  "data": {
    "name": "Character Name",
    "description": "Description",
    "personality": "Personality",
    "scenario": "Scenario",
    "first_mes": "First Message",
    "mes_example": "Dialogue Example",
    "system_prompt": "System Prompt",
    "creator_notes": "Creator Notes",
    "character_version": "1.0",
    "alternate_greetings": ["Greeting 1", "Greeting 2"],
    "tags": ["tag1", "tag2"],
    "creator": "Creator Name",
    "extensions": {}
  }
}
```

**Key Differences Between V2 and V3:**

| Feature | V2 | V3 |
|---------|----|----|
| Data Structure | Flat JSON | `data` nested structure |
| Character Version | None | `character_version` field |
| Multiple Greetings | None | `alternate_greetings` array |
| Tag System | None | `tags` array |
| Creator Attribution | None | `creator` field |
| Dialogue Examples | None | `mes_example` field |
| Extension Fields | No standard | `extensions` object (may contain `engine_state`) |

**Field Mapping Logic:**

```python
V3_FIELD_MAPPING = {
    "name": "data.name",
    "description": "data.description",
    "personality": "data.personality",
    "scenario": "data.scenario",
    "first_message": "data.first_mes",
    "prompt": "data.system_prompt",
    "creator_notes": "data.creator_notes",
    "character_version": "data.character_version",
    "alternate_greetings": "data.alternate_greetings",
    "tags": "data.tags",
    "creator": "data.creator",
    "extensions": "data.extensions",
}
```

**CharacterCardLoader Supplementary Implementation:**

```python
@classmethod
def _load_tavern_v3(cls, raw: dict, file_path: str = "") -> dict:
    """Load SillyTavern V3 format"""
    data = raw.get("data", {})

    char_data = {
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "personality": data.get("personality", ""),
        "prompt": data.get("system_prompt", ""),
        "first_message": data.get("first_mes", ""),
        "scenario": data.get("scenario", ""),
        "creator_notes": data.get("creator_notes", ""),
        "character_version": data.get("character_version", "1.0"),
        "alternate_greetings": data.get("alternate_greetings", []),
        "tags": data.get("tags", []),
        "creator": data.get("creator", ""),
        "initial_state": cls._extract_initial_state_v3(data),
    }

    # Try to associate lorebook
    lorebook = cls._find_lorebook(os.path.dirname(file_path) if file_path else "",
                                   data.get("name", ""))
    if lorebook:
        char_data["lorebook_file"] = lorebook

    return char_data

@classmethod
def _extract_initial_state_v3(cls, data: dict) -> dict:
    """Extract initial state from V3 character card"""
    extensions = data.get("extensions", {})
    engine_state = extensions.get("engine_state", {})
    if engine_state:
        return {
            "hp": engine_state.get("hp", 100),
            "max_hp": engine_state.get("max_hp", 100),
            "energy": engine_state.get("energy", 100),
            "goodwill": engine_state.get("goodwill", 0),
            "phase": engine_state.get("phase", 1),
            "inventory": engine_state.get("inventory", []),
            "character_state": engine_state.get("character_state", {}),
        }

    # Check top-level extension fields
    top_extensions = data.get("extensions", {}) if "extensions" not in data else {}
    top_engine = top_extensions.get("engine_state", {})
    if top_engine:
        return {
            "hp": top_engine.get("hp", 100),
            "max_hp": top_engine.get("max_hp", 100),
            "energy": top_engine.get("energy", 100),
            "goodwill": top_engine.get("goodwill", 0),
            "phase": top_engine.get("phase", 1),
        }

    return {}
```

**V3-Specific Feature Support:**

1. **Multiple Greetings:** `first_mes` is used by default on load. If `alternate_greetings` is non-empty and the user hasn't specified a choice, the first entry is used by default. Switch via `/greeting [index]` (this command is reserved, not in MVP scope).
2. **Dialogue Examples:** `mes_example` field is injected into the System Prompt's dialogue style reference section, helping AI mimic the character's tone.
3. **Tags & Version:** Displayed in the character info panel after loading, making it easy to manage multiple versions of character cards.

**Updated Version Identification Matrix:**

| `spec` Value | Version | Load Method |
|---|---|---|
| `"chara_card_v3"` | V3 | `_load_tavern_v3()` |
| `"chara_card_v2"` | V2 | `_load_tavern_v2()` |
| No `spec`, has `name` + `description` | V1 | `_load_tavern_v1()` |
| No `spec`, has `character.dsl` + `character_data.json` | Kernelsoul Native | `_load_native_v4()` |

### 4.3 CharacterStateManager (v2.0)

#### 4.3.1 Responsibilities

1. Initialize `character_state` variable table on character card load.
2. After each round submission, scan `character_rules`, check trigger conditions, and execute matching actions.
3. Manage `conditional_memories` unlock status.
4. Inject current character state into context packing.

#### 4.3.2 Core Implementation Skeleton

```python
class CharacterStateManager:
    def __init__(self, character_card: dict):
        self.variables = {}
        self.memories = {}
        self.rules = character_card.get("character_rules", [])
        for var_name, var_def in character_card.get("character_state", {}).get("variables", {}).items():
            self.variables[var_name] = var_def["default"]
        for mem in character_card.get("conditional_memories", []):
            self.memories[mem["id"]] = {
                "content": mem["content"],
                "unlock_condition": mem["unlock_condition"],
                "unlocked": mem.get("unlocked", False)
            }

    def evaluate_condition(self, condition: dict, game_state=None) -> bool:
        field = condition["field"]; target = condition["value"]
        if field.startswith("character_state."):
            actual = self.variables.get(field.split(".", 1)[1])
        else:
            return False
        op = condition["type"]
        if op == "gte": return actual >= target
        if op == "lte": return actual <= target
        if op == "eq": return actual == target
        if op == "lt": return actual < target
        if op == "gt": return actual > target
        return False

    def execute_action(self, action: dict):
        if action["type"] == "set_variable":
            self.variables[action["target"].split(".", 1)[1]] = action["value"]
        elif action["type"] == "set_variable_delta":
            self.variables[action["target"].split(".", 1)[1]] += action.get("delta", 0)
        elif action["type"] == "unlock_memory":
            if action["target"] in self.memories:
                self.memories[action["target"]]["unlocked"] = True

    def check_rules(self, user_input: str, ai_response: str, game_state) -> list:
        triggered = []
        for rule in self.rules:
            if rule.get("trigger", "") and rule["trigger"] in user_input + ai_response:
                if self.evaluate_condition(rule.get("condition", {}), game_state):
                    triggered.append(rule)
        return triggered

    def get_unlocked_memories(self) -> str:
        return "\n".join([m["content"] for m in self.memories.values() if m["unlocked"]])

    def get_state_text(self) -> str:
        lines = ["[Internal State]"]
        for var_name, value in self.variables.items():
            lines.append(f"- {var_name}: {value}")
        return "\n".join(lines)
```

#### 4.3.3 Collaboration with Existing Modules

- CharacterStateManager runs sequentially with the global StateManager after each round submission, without interfering with each other.
- Character rules and global rules are executed within the same submission cycle in order — global rules first, then character rules.
- Results of `get_state_text()` and `get_unlocked_memories()` are injected into the Prompt, positioned after the global state and before lorebook entries.

---

### 4.3.3 Python Complete Implementation (v2.3)

```python
"""
Kernelsoul CharacterStateManager — Python Implementation
Responsible for variable initialization, rule evaluation, condition judgment, and action execution.
"""

from typing import Any, Optional


class CharacterStateManager:
    """Character State Manager — Runtime Core"""

    def __init__(self):
        self.variables: dict[str, Any] = {}
        self.memories: dict[str, dict] = {}
        self.rules: list = []

    def init_variables(self, defs: dict[str, Any]):
        for name, var_def in defs.items():
            default = getattr(var_def, 'default', 0)
            self.variables[name] = default

    def load_rules(self, rules: list):
        self.rules = rules

    def init_memories(self, memories: list):
        for mem in memories:
            mem_id = mem.get('id') if isinstance(mem, dict) else mem.id
            self.memories[mem_id] = {
                'content': mem.get('content', '') if isinstance(mem, dict) else mem.content,
                'unlock_condition': mem.get('unlock_condition') if isinstance(mem, dict) else mem.unlock_condition,
                'unlocked': mem.get('unlocked', False) if isinstance(mem, dict) else getattr(mem, 'unlocked', False)
            }

    def get_current_state(self) -> dict[str, Any]:
        return dict(self.variables)

    def get_unlocked_memories(self) -> list[str]:
        return [m['content'] for m in self.memories.values() if m['unlocked']]

    def get_state_text(self) -> str:
        lines = ["[Character Internal State]"]
        for name, value in self.variables.items():
            lines.append(f"- {name}: {value}")
        unlocked = self.get_unlocked_memories()
        if unlocked:
            lines.append("\n[Unlocked Memories]")
            for mem in unlocked:
                lines.append(f"- {mem}")
        return "\n".join(lines)

    def evaluate(self, context: dict) -> list[dict]:
        decisions = []
        message = context.get('message', {})
        message_content = message.get('content', '')

        for rule in self.rules:
            if not self._check_trigger(rule, message_content):
                continue
            condition = getattr(rule, 'condition', None) if hasattr(rule, 'condition') else rule.get('condition')
            if condition and not self._evaluate_condition(condition):
                continue
            actions = getattr(rule, 'actions', []) if hasattr(rule, 'actions') else rule.get('actions', [])
            executed_actions = []
            for action in actions:
                self._execute_action(action)
                executed_actions.append(action)
            rule_id = getattr(rule, 'id', '') if hasattr(rule, 'id') else rule.get('id', '')
            description = getattr(rule, 'description', '') if hasattr(rule, 'description') else rule.get('description', '')
            decisions.append({
                'rule_id': rule_id,
                'rule_description': description,
                'triggered_at': context.get('timestamp', 0),
                'condition_result': True,
                'actions_executed': executed_actions,
                'variable_snapshot': self.get_current_state()
            })
        return decisions

    def _check_trigger(self, rule, message_content: str) -> bool:
        trigger = getattr(rule, 'trigger', '') if hasattr(rule, 'trigger') else rule.get('trigger', '')
        if trigger == 'ALWAYS':
            return True
        keywords = getattr(rule, 'trigger_keywords', []) if hasattr(rule, 'trigger_keywords') else rule.get('trigger_keywords', [])
        if keywords:
            content_lower = message_content.lower()
            return any(kw.lower() in content_lower for kw in keywords)
        return False

    def _evaluate_condition(self, condition) -> bool:
        cond_type = getattr(condition, 'type', '') if hasattr(condition, 'type') else condition.get('type', '')
        field = getattr(condition, 'field', '') if hasattr(condition, 'field') else condition.get('field', '')
        expected = getattr(condition, 'value', None) if hasattr(condition, 'value') else condition.get('value')
        actual = None
        if field.startswith('character_state.'):
            var_name = field.replace('character_state.', '')
            actual = self.variables.get(var_name)
        elif field.startswith('game.'):
            return False
        else:
            actual = self.variables.get(field)
        if actual is None:
            return False
        if cond_type == 'gte': return actual >= expected
        if cond_type == 'lte': return actual <= expected
        if cond_type == 'gt': return actual > expected
        if cond_type == 'lt': return actual < expected
        if cond_type == 'eq': return actual == expected
        if cond_type == 'neq': return actual != expected
        if cond_type == 'contains': return str(expected) in str(actual)
        return False

    def _execute_action(self, action):
        action_type = getattr(action, 'type', '') if hasattr(action, 'type') else action.get('type', '')
        target = getattr(action, 'target', '') if hasattr(action, 'target') else action.get('target', '')
        if action_type == 'set_variable':
            var_name = target.replace('character_state.', '')
            value = getattr(action, 'value', None) if hasattr(action, 'value') else action.get('value')
            if var_name in self.variables:
                self.variables[var_name] = value
        elif action_type == 'change_variable':
            var_name = target.replace('character_state.', '')
            delta = getattr(action, 'delta', 0) if hasattr(action, 'delta') else action.get('delta', 0)
            if var_name in self.variables and isinstance(self.variables[var_name], (int, float)):
                self.variables[var_name] += delta
        elif action_type == 'unlock_memory':
            if target in self.memories:
                self.memories[target]['unlocked'] = True
        elif action_type == 'lock_memory':
            if target in self.memories:
                self.memories[target]['unlocked'] = False

    def set_variable(self, name: str, value: Any):
        if name in self.variables:
            self.variables[name] = value
```

---

### 4.4 AI RuleCompiler (RuleCompiler) (v2.0)

#### 4.4.1 Design Purpose

Creators should never have to hand-write JSON rules. They use natural language to write character scripts, and the AI compiler generates the internal JSON.

#### 4.4.2 Workflow (Three Modes, v2.1 Upgrade)

**Mode A: Natural Language → JSON (For Beginners)**

1. Input: Creator enters natural language character description.
2. Compilation: System combines natural language with compilation Prompt template, sends to AI.
3. Output: AI generates structured JSON (`character_rules`, `conditional_memories`, `suggested_variables`).
4. Baking: Generated JSON populates a visual rule editor for the creator to modify.
5. Save: Confirmed rules are written to the character card's `character_rules` field.

**Mode B: Natural Language → DSL → JSON (Recommended, Provides Readable Intermediate Representation)**

1. Input: Creator enters natural language character description.
2. Compilation: System combines natural language with compilation Prompt template, sends to AI, specifying DSL format output.
3. Output: AI generates DSL source text (more readable, easier to review and fine-tune).
4. Baking: DSL source is handed to DSLCompiler (Section 4.5) to generate JSON, and populates the visual editor.
5. Save: Confirmed DSL source is written to `character_rules_dsl` field, JSON is written to `character_rules` field.

**Mode C: Hand-written DSL → JSON (Expert Mode)**

1. Input: Creator directly writes DSL source in the editor.
2. Compilation: DSLCompiler (Section 4.5) deterministically parses the source without AI involvement.
3. Output: Generated JSON directly populates the editor for confirmation.
4. Save: DSL source and JSON are written to the character card's corresponding fields.

#### 4.4.3 Compilation Prompt Template

Storage location: `/configs/rule_compiler_prompt.txt`. Contains detailed JSON Schema requirements and compilation rules.

#### 4.4.4 Relationship with Existing Architecture

- RuleCompiler is a creation tool, not a runtime engine. It is used during character card creation.
- Generated rules are executed by the runtime CharacterStateManager.
- Creators can also directly hand-write JSON rules, bypassing the compiler.

---

### 4.5 DSL Compiler (DSLCompiler) (v2.1 New)

#### 4.5.1 Responsibilities (v2.1 New)

- Parse DSL source text into `character_rules` JSON array.
- Perform semantic checks (variable declaration validation, type checking, rule ID uniqueness).
- Support reverse compilation: restore `character_rules` JSON to DSL source text.
- Collaborate with RuleCompiler: receive AI-generated DSL text, compile and validate.

#### 4.5.2 Core Interface (v2.1 New)

```python
class DSLCompiler:
    @staticmethod
    def compile(dsl_source: str, variable_definitions: dict) -> tuple[list, list]:
        """Compile DSL source into character_rules JSON.
        Returns (rules_list, errors_list).
        If errors_list is non-empty, rules_list may be a partial result."""

    @staticmethod
    def decompile(rules_json: list, variable_definitions: dict) -> str:
        """Decompile character_rules JSON back to DSL source text."""

    @staticmethod
    def validate(dsl_source: str, variable_definitions: dict) -> list:
        """Only validate DSL source, return error list without generating JSON."""
```

#### 4.5.3 Implementation Strategy (v2.1 New)

- Hand-written recursive descent parser, no third-party parsing libraries.
- Lexer uses regular expression tokenization.
- Error messages include line and column numbers, pointing to specific DSL source locations.
- Reverse compiler assembles DSL text using fixed templates to ensure consistent formatting.

---

### 4.6 FileService API (v2.3 New)

#### 4.6.1 Design Principles

The backend degenerates into a pure file relay service, completely independent of business logic. The frontend manages all resources through four generic APIs.

#### 4.6.2 Four Core APIs

| Method | Endpoint | Function | Idempotent |
|--------|----------|----------|------------|
| GET | /api/files/{path} | Read file or directory contents | Yes |
| POST | /api/files/{path} | Create new file or directory | No |
| DELETE | /api/files/{path} | Delete file or directory | Yes |
| PATCH | /api/files/{path} | Rename or move file | No |

#### 4.6.3 Fine Query Syntax

GET requests support GraphQL-like field selection syntax:

```
# Get complete DSL source
GET /api/files/character/innkeeper:character.dsl

# Get compiled rule JSON
GET /api/files/character/innkeeper:character_rules.json

# Get name field from character base data
GET /api/files/character/innkeeper:character_data.json.name

# Get last 3 rules from the ruleset
GET /api/files/character/innkeeper:character_rules.json.rules.[-3,-1]

# List all files in a directory
GET /api/files/character/innkeeper/
```

**Syntax rules:**
- `.` after `:` for file internal path (JSON field path or text line range).
- `.[n]` for array element access; `.[-n,-1]` for last n elements.
- Without `:`, returns entire file contents.

#### 4.6.4 Python Implementation Skeleton

```python
import os
import json
from pathlib import Path
from typing import Any

class FileService:
    """Minimal file service: four APIs cover all resource management"""

    def __init__(self, base_dir: str = "./"):
        self.base_dir = Path(base_dir).resolve()
        self._ensure_safe()

    def _ensure_safe(self):
        os.makedirs(self.base_dir, exist_ok=True)

    def _resolve_path(self, path: str) -> Path:
        """Resolve path, prevent directory traversal attacks"""
        resolved = (self.base_dir / path).resolve()
        if not str(resolved).startswith(str(self.base_dir)):
            raise ValueError(f"Path out of bounds: {path}")
        return resolved

    def get(self, path: str) -> Any:
        """Read file or directory. Supports fine queries."""
        parts = path.split(":", 1)
        file_path = self._resolve_path(parts[0])
        if file_path.is_dir():
            return {"type": "directory", "items": os.listdir(file_path)}
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        content = self._read_file(file_path)
        if len(parts) > 1:
            return self._query_content(content, parts[1], file_path.suffix)
        return content

    def post(self, path: str, content: Any = None) -> dict:
        """Create new file or directory"""
        file_path = self._resolve_path(path)
        if file_path.exists():
            raise FileExistsError(f"File already exists: {path}")
        if content is None:
            os.makedirs(file_path, exist_ok=True)
            return {"type": "directory", "created": path}
        os.makedirs(file_path.parent, exist_ok=True)
        self._write_file(file_path, content)
        return {"type": "file", "created": path}

    def delete(self, path: str) -> dict:
        """Delete file or directory"""
        file_path = self._resolve_path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if file_path.is_dir():
            import shutil
            shutil.rmtree(file_path)
            return {"type": "directory", "deleted": path}
        os.remove(file_path)
        return {"type": "file", "deleted": path}

    def patch(self, path: str, new_path: str) -> dict:
        """Rename or move file"""
        file_path = self._resolve_path(path)
        target_path = self._resolve_path(new_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        os.makedirs(target_path.parent, exist_ok=True)
        os.rename(file_path, target_path)
        return {"renamed": path, "to": new_path}

    def _read_file(self, path: Path) -> Any:
        suffix = path.suffix.lower()
        with open(path, 'r', encoding='utf-8') as f:
            if suffix == '.json':
                return json.load(f)
            return f.read()

    def _write_file(self, path: Path, content: Any):
        suffix = path.suffix.lower()
        with open(path, 'w', encoding='utf-8') as f:
            if suffix == '.json':
                json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                f.write(str(content))

    def _query_content(self, content: Any, query: str, suffix: str) -> Any:
        if suffix == '.json':
            return self._query_json(content, query)
        return self._query_text(content, query)

    def _query_json(self, data: Any, path: str) -> Any:
        current = data
        for segment in path.split('.'):
            if segment.startswith('[') and segment.endswith(']'):
                inner = segment[1:-1]
                if ',' in inner:
                    start, end = inner.split(',')
                    start = int(start) if start else 0
                    end = int(end) if end else len(current)
                    current = current[start:end]
                else:
                    current = current[int(inner)]
            else:
                current = current[segment]
        return current

    def _query_text(self, text: str, query: str) -> str:
        lines = text.split('\n')
        if ':' in query:
            start, end = query.split(':')
            start = int(start) if start else 0
            end = int(end) if end else len(lines)
            return '\n'.join(lines[start:end])
        return text
```

---

## V. System Console Commands — In-Game Support [v1.0, Multi-version Extensions]

To enable smooth switching between multiple characters and saves, as well as management of drafts, memory anchors, rules, and plugins, the main loop must intercept the following commands without entering the AI flow. All commands start with `/` and can be used at any time during dialogue. Normal text not starting with `/` enters the AI flow as player input.

### 5.1 Character & Session Management [v1.0]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /list or /ls | None | List all available character cards in /characters/ folder | v1.0 |
| /character | [name] | Switch current character. Engine immediately loads corresponding character card JSON from disk (Kernelsoul character reads character.dsl → character_rules.json), auto-loads most recent session for that character | v1.0 |
| /newgame | [name] | Start new playthrough. If character exists, creates new session_XX folder under its directory (auto-incrementing name), writes initial state.sav. Uses current character if name not specified | v1.0 |
| /load | [name] [sessionID] | Specific load. Directly jump to specified save folder. Auto-loads most recent session if only character name specified | v1.0 |

### 5.2 Preset Management [v1.0]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /preset | [name] | Load specified preset file from /configs/presets/, replace current system_prompt and meta_cognition.txt content. Kernelsoul characters can further use character-level preset (character_rules.json) | v1.0 |

### 5.3 Draft & Version Control [v1.2]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /roll | None | Only valid when current round has unconfirmed draft. Request AI to regenerate, new result appended as new draft (draft number increments), old draft retained | v1.2 |
| /select | [number] | Select a draft from existing drafts as the official response. Engine writes draft's narrative to history chain, applies state_changes to update game state, then clears entire /drafts/ folder. Defaults to newest draft | v1.2 |
| /drafts | None | List summaries (first 100 chars) of all current drafts, showing number and core content | v1.2 |

### 5.4 Draft Saving [v1.6]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /draft save | [number] | Save specified draft to /context/saved_drafts/, not cleared on submission | v1.6 |
| /saved | None | List all saved drafts (with summary and timestamp) | v1.6 |
| /saved load | [number] | Reload a saved draft as the current confirmation draft, making it submittable | v1.6 |

### 5.5 Memory Anchors [v1.5]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /memory add | [content] | Add text as permanent memory anchor, written to /context/manual_memory.json, directly injected into context packing | v1.5 |
| /memory list | None | List all manually added memory anchors | v1.5 |
| /memory delete | [number] | Delete specified manual memory anchor | v1.5 |

### 5.6 Rule Management [v1.5]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /rules export | [filename] | Export current global rules (rules.json) and character rules (character_rules.json) as packaged file | v1.5 |
| /rules import | [filename] | Import rules from packaged file, overwrite current config (auto-backup old rules before import) | v1.5 |

### 5.7 Plugin Management [v1.3]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /plugin list | None | List all loaded plugins with enabled/disabled status | v1.3 |
| /plugin reload | [pluginID] | Hot-reload specified plugin, no engine restart needed | v1.3 |
| /plugin enable | [pluginID] | Enable specified plugin, activate hooks and features | v1.3 |
| /plugin disable | [pluginID] | Disable specified plugin, deactivate its hooks and features | v1.3 |

### 5.8 Data Management [v1.5]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /export | None | Package current session's complete save (history, context, state, meta) as .zip | v1.5 |
| /import | [filepath] | Import save from .zip file, restore complete session state | v1.5 |

### 5.9 Debug & Control [v1.5/v2.0]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /debug on | None | Enable debug mode: show rule trigger chain, DSL trace info, variable change logs, token usage etc. per round | v2.0 |
| /debug off | None | Disable debug mode, restore standard output | v2.0 |
| /stop | None | Safely stop engine, save all current state then exit | v1.5 |

### 5.10 Help & Marketplace [v1.5/Reserved]

| Command | Parameters | Function | Version Introduced |
|---------|-----------|----------|-------------------|
| /help | [command] | Show command help. Without parameter, list all available commands. With command name, show detailed usage | v1.5 |
| /market list | None | List available plugins from community marketplace (requires network) | Reserved |
| /market install | [pluginID] | Install specified plugin from community marketplace to /plugins/ | Reserved |

### 5.11 Default Behavior [v1.2]

If the user directly enters normal text (not starting with "/"), the engine follows these rules:

1. If no unconfirmed draft exists: user input goes directly into AI flow as the new round's player input.
2. If unconfirmed draft exists: automatically acts as `/select latest`, first submits the latest draft, then uses the user input as the start of the next round.

This behavior ensures players can have natural continuous dialogue without confirming each draft, while preserving the precise control of `/select`. Players can override the default auto-submit logic using `/roll` to regenerate, `/select` to manually choose, or `/draft save` to preserve a draft.

### Command Quick Reference

| Command Group | Commands | Version Introduced |
|---------------|----------|-------------------|
| Character & Session | /list, /character, /newgame, /load | v1.0 |
| Preset Management | /preset | v1.0 |
| Draft & Version | /roll, /select, /drafts | v1.2 |
| Draft Saving | /draft save, /saved, /saved load | v1.6 |
| Memory Anchors | /memory add, /memory list, /memory delete | v1.5 |
| Rule Management | /rules export, /rules import | v1.5 |
| Plugin Management | /plugin list, /plugin reload, /plugin enable, /plugin disable | v1.3 |
| Data Management | /export, /import | v1.5 |
| Debug & Control | /debug on/off, /stop | v1.5/v2.0 |
| Help & Marketplace | /help, /market list, /market install | v1.5/Reserved |
| Default Behavior | Auto-submit normal text + new round | v1.2 |

---

## VI. Rule Engine Detailed Syntax

**rules.json file format example:**

```json
{
  "evolution_rules": [
    {
      "id": "phase_2_unlock",
      "condition": {
        "type": "gte",
        "field": "goodwill",
        "value": 80
      },
      "action": {
        "type": "set_phase",
        "target": 2
      }
    },
    {
      "id": "low_hp_buff",
      "condition": {
        "type": "lte",
        "field": "hp",
        "value": 20
      },
      "action": {
        "type": "set_max_hp",
        "target": 120
      }
    },
    {
      "id": "special_item_unlock",
      "condition": {
        "type": "contains",
        "field": "inventory",
        "value": "Demon Key"
      },
      "action": {
        "type": "set_phase",
        "target": 3
      }
    }
  ]
}
```

**Supported Operators:**
- `eq`, `neq`, `gt`, `gte`, `lt`, `lte`: Numeric comparison.
- `contains`: Check if a list (e.g., inventory) contains a specified string.

**Supported Action Types:**
- `set_phase`: Set evolution phase.
- `set_max_hp`: Modify max health.
- `add_item`: Add item to inventory.
- `remove_item`: Remove item from inventory.
- `set_bg`: Modify current background.
- More action types can be extended in future versions.

The evolution trigger checks rules in order after each round's submission. Once a condition is met, the corresponding action is immediately executed. Multiple non-conflicting rules may be triggered in the same round.

### Rule Flexibility & Exception Handling (v1.5)

The rule engine ensures determinism in game mechanics, but part of the charm of narrative games lies in "unexpectedness." To prevent the system from becoming mechanical and rigid, the following flexibility designs are introduced:

**1. Rule "Allow Override" Flag**

Add optional field `allow_override: false` (default) to each rule in rules.json:

```json
{
  "id": "phase_2_unlock",
  "condition": { "type": "gte", "field": "goodwill", "value": 80 },
  "action": { "type": "set_phase", "target": 2 },
  "allow_override": false
}
```

When `allow_override: true`, the AI can request to "temporarily ignore this rule" in JSON state changes. The engine generates a temporary exemption prompt displayed to the player, who decides whether to accept it.

**2. Plugin Rule Intervention Hook**

Add `on_rule_trigger` hook to the plugin lifecycle, called when a rule is about to trigger. Returns `None` for normal execution; returns a modified action to replace the original.

**3. Random Event Table (Future Extension):** Reserved `/configs/random_events.json` interface.

**Design Principle:** Determinism is the skeleton, flexibility is the flesh. AI cannot bypass rules, but creators and players can.

**Rule Set Sharing & Importing (v1.5):** `/rules export [filename]` to export; `/rules import [filename]` to import. Preset jailbreaks (`/presets/`) can also be shared via community index.

### Character-Level Rule Engine (v2.0)

Kernelsoul character cards can embed `character_rules`, forming a two-layer rule architecture:

| Layer | Location | Scope | Priority | Management Module |
|-------|----------|-------|----------|-------------------|
| Global Rules | /configs/rules.json | All characters | High | EvolutionTrigger |
| Character Rules | character_rules in card | Current character | Low | CharacterStateManager |

**Execution order (after each round submission):** Global rules → Character rules. If both modify the same variable, global rules take priority.

AI can request modification of character internal state by adding a `character_state` field in `state_changes` JSON, which is validated and executed by CharacterStateManager. The whitelist consists of variables defined in `character_state.variables`.

---

## VII. Kernelsoul Character Behavior DSL: Script Logic Language (SLL) (v2.1 New)

### 7.1 Design Goals (v2.1 New)

The core of the Kernelsoul architecture is "rigid kernel, flexible shell." Character cards evolve from "stories to be read" into "logic bodies to be executed." A specialized language is needed to describe character behavior logic — it must satisfy:

- **Human-readable and writable:** Creators don't need programming knowledge to write and understand.
- **Deterministically executable:** Compiles into precisely machine-executable instructions, eliminating LLM's probabilistic uncertainty.
- **Debuggable and traceable:** The execution engine can trace back to DSL source lines, highlighting triggered rules in UI.
- **Complementary to natural language:** Creators can either leave natural language to RuleCompiler for automatic compilation or directly hand-write DSL for precise control.

DSL serves as the intermediate representation between natural language and JSON rules, forming a complete creative pipeline:

```
Natural Language Script → (RuleCompiler) → DSL Source → (DSL Compiler) → JSON Rules → (CharacterStateManager) Execution
```

Simultaneously, the engine's debugging and auditing direction is reverse — AI's JSON rule changes output per round can be decompiled back to DSL source via DSLCompiler.decompile(), then translated into creator-readable natural language explanations. This ensures AI behavior is always traceable, auditable, and correctable, rather than a black box Prompt.

```
Reverse Debugging Chain:
AI Output JSON Rules → (decompile) → DSL Source → (interpretation) → Creator-Readable Natural Language
```

**Core Value of This Bidirectional Loop:**

| Direction | Path | Purpose |
|-----------|------|---------|
| Forward (Creation) | Natural Language → DSL → JSON → Execution | Deterministic compilation, controllable character behavior |
| Reverse (Debugging) | JSON → DSL → Natural Language | Traceable audit, transparent AI decisions |

DSL serves as the sole central format, with JSON and natural language symmetrically distributed on either side — neither is subordinate to the other, but neither can bypass DSL.

```
DSL (Central Format)
   ↕          ↕
JSON       Natural Language (Creator-readable)
↕
Machine Execution
```

Experienced creators can directly hand-write DSL, skipping the natural language compilation step for finer control.

### 7.2 Core Syntax (v2.1 New)

#### 7.2.1 Basic Structure: A Rule (v2.1 New)

A rule consists of four parts: trigger event, pre-condition, action list, and description.

```
WHEN <trigger event> IF <condition expression> THEN <action1> <action2> ... BECAUSE "<human-readable rule explanation>"
```

**Example:**

```
WHEN player mentions "king" or "royalty" IF mood < 0 THEN SET current_tone = "sarcastic" CHANGE suspicion BY +10 FORCE EMOTION "resentful" BECAUSE "Hearing praise of the king when in a bad mood triggers her defensiveness and resentment"
```

#### 7.2.2 Trigger Event (WHEN) (v2.1 New)

Defines when a rule is evaluated. It can be keyword matching, system events, or state changes.

**Keyword Matching:**
```
WHEN player mentions <keyword/phrase>
WHEN player mentions <word1>, <word2>, ... or <wordN>
```

**System Events:**
```
WHEN round_start
WHEN round_end
WHEN time_changes TO "midnight"
WHEN character_first_appears
WHEN character_dies
```

**State Change Events (Future Extension):**
```
WHEN trust_player CHANGED FROM <old> TO <new>
WHEN mood BECAME NEGATIVE
```

Keyword matching is case-insensitive by default; multiple keywords can be specified (logical OR).

**Special Trigger ALWAYS:** Evaluated unconditionally every round (only checks condition).
```
WHEN ALWAYS IF fatigue > 80 THEN SET current_tone = "tired"
```

#### 7.2.3 Condition Expression (IF) (v2.1 New)

Condition expressions use natural-language-like comparison syntax, supporting comparison with character state variables and global game state.

**Basic Comparison:**
```
<variable> <operator> <value>
```

**Operators:** `>`, `<`, `>=`, `<=`, `==`, `!=`

For strings: `==` for exact match, `CONTAINS` for substring.

**Examples:**
```
IF trust_player >= 60
IF current_tone == "angry"
IF mood <= -5
IF player_inventory CONTAINS "rose"
```

**Logical Combinations:**
```
IF <condition1> AND <condition2>
IF <condition1> OR <condition2>
IF NOT <condition>
```

Parentheses can be used for explicit priority:
```
IF (mood < 0) AND (trust_player > 50 OR suspicion < 30)
```

**Variable Paths:**
- Character internal state: Use variable name directly, e.g., mood, trust_player, fatigue.
- Global game state: Prefix with `game.`, e.g., game.hp, game.phase.
- Player state (future extension): Prefix with `player.`, e.g., player.gold.

**Special Conditions:**
```
IF time IS "midnight" — requires system time event.
IF round_count > 10
IF memory_unlocked "memoryID" — check if a conditional memory is unlocked.
```

#### 7.2.4 Action List (THEN) (v2.1 New)

Actions are operations forcibly executed when a rule triggers. Each action occupies one line.

**Variable Assignment:**
```
SET <variable> = <new_value>
SET mood = 5
SET current_tone = "gentle"
```

Values can be numbers, strings, or booleans.

**Variable Increment/Decrement:**
```
CHANGE <variable> BY <delta>
CHANGE suspicion BY +10
CHANGE fatigue BY -5
```

**Unlock/Lock Memory:**
```
UNLOCK MEMORY "memoryID"
LOCK MEMORY "memoryID"
```

**Force Tone/Emotion:**
```
FORCE TONE "sarcastic"
FORCE EMOTION "resentful"
```

These two actions inject strong hints into the next round's AI generation, requesting a specific tone or emotion.

**Send System Message (not shown to player):**
```
LOG "<message content>"
```

Used for debugging or internal recording.

**Trigger Global Rule (Advanced):**
```
TRIGGER RULE "global_rule_id"
```

Allows character rules to actively invoke specified rules in the global rule engine.

**Conditional Actions (Future Extension):** Not yet implemented. Keeping rules granular is recommended.

#### 7.2.5 Description (BECAUSE) (v2.1 New)

The BECAUSE clause is a comment explaining why this rule exists in human language. It is not executed but appears in the decision trace panel, helping creators and players understand character behavior logic.

### 7.3 Variable System (v2.1 New)

Variables manipulated in DSL must be predefined in the character card's `character_state.variables`.

```
VARIABLES:
  mood: int, range(-10,10), default 0, "Mood value"
  trust_player: int, range(0,100), default 20, "Trust in player"
  fatigue: int, range(0,100), default 0, "Fatigue level"
  suspicion: int, range(0,100), default 30, "Suspicion level"
  current_tone: string, default "neutral", "Current speaking tone"
```

Creators can declare variable tables in the character card. If DSL references undeclared variables, the compiler will report errors and hint.

### 7.4 Correspondence with JSON Rules (v2.1 New)

DSL source compiles into the `character_rules` JSON array defined in the Kernelsoul specification. The compilation process is deterministic. Reverse conversion is also achievable (for bidirectional sync in visual editors).

**JSON structure corresponding to a DSL rule:**

```json
{
  "id": "praise_king_trigger",
  "trigger": "player mentions king",
  "condition": { "type": "lt", "field": "character_state.mood", "value": 0 },
  "action": [
    { "type": "set_variable", "target": "character_state.current_tone", "value": "sarcastic" },
    { "type": "change_variable", "target": "character_state.suspicion", "delta": 10 },
    { "type": "force_emotion", "value": "resentful" }
  ],
  "description": "Hearing praise of the king when in a bad mood triggers her defensiveness and resentment"
}
```

**Mapping Relationship:**
- `trigger` field: For keyword matching in DSL, expanded into precise keyword list and matching pattern.
- `condition`: Condition expression parsed into operator and field path.
- `action`: Actions mapped to action object array.
- `description`: BECAUSE part stored here.

When creators modify JSON rules in the visual editor, the DSL source is also updated simultaneously, maintaining a single source of truth.

### 7.5 DSL Compiler Implementation Overview (v2.1 New)

The DSL Compiler is an independent module responsible for parsing DSL source text into `character_rules` JSON. It does not depend on AI; it is a deterministic parser.

**Implementation Steps:**
1. **Lexical Analysis:** Split source into token stream (WHEN, IF, SET, IDENTIFIER, STRING, NUMBER, etc.).
2. **Syntax Analysis:** Build abstract syntax tree (AST) according to grammar rules.
3. **Semantic Check:** Verify referenced variables are declared; verify operator-type matching; check rule ID uniqueness.
4. **Code Generation:** Traverse AST, generate corresponding JSON structure.

**Grammar Overview (Simplified EBNF):**

```
rule      := "WHEN" trigger "IF" condition "THEN" action+ "BECAUSE" string
trigger   := "ALWAYS" | "玩家提及" string_list | system_event_keyword
condition := expr (("AND"|"OR") expr)*
expr      := ("NOT")? (variable op value | "(" condition ")")
variable  := IDENTIFIER ("." IDENTIFIER)*
op        := ">" | "<" | ">=" | "<=" | "==" | "!=" | "CONTAINS"
action    := set_action | change_action | unlock_action | force_tone_action ...
set_action := "SET" variable "=" value
change_action := "CHANGE" variable "BY" ("+"|"-")? NUMBER
value     := NUMBER | STRING | BOOLEAN
```

Given the extremely simple syntax, a hand-written recursive descent parser can easily implement it without introducing third-party parsing libraries, keeping the engine lightweight.

#### 7.5.1 Python Implementation Code (v2.3)

```python
"""
Kernelsoul DSL Compiler — Python Implementation
Deterministic hand-written recursive descent parser, no AI dependency.
Same DSL input always produces the same JSON output.
"""

import re
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class VariableDefinition:
    type: str  # 'int' | 'string' | 'boolean'
    range: tuple = None
    default: Any = None
    description: str = ""


@dataclass
class RuleCondition:
    type: str  # 'gte' | 'lte' | 'gt' | 'lt' | 'eq' | 'neq' | 'contains'
    field: str
    value: Any


@dataclass
class RuleAction:
    type: str
    target: Optional[str] = None
    value: Any = None
    delta: int = 0
    description: str = ""


@dataclass
class CharacterRule:
    id: str
    trigger: str
    trigger_keywords: list = field(default_factory=list)
    condition: Optional[RuleCondition] = None
    actions: list = field(default_factory=list)
    description: str = ""


class DSLCompiler:
    """Kernelsoul DSL Compiler — Deterministic Recursive Descent Parser"""

    def compile(self, dsl_source: str,
                variables: dict[str, VariableDefinition]) -> tuple[list[CharacterRule], list[dict]]:
        """Compile DSL source into rule list. Returns (rules, errors)."""
        errors: list[dict] = []
        rules: list[CharacterRule] = []
        lines = [l.strip() for l in dsl_source.split('\n')
                 if l.strip() and not l.strip().startswith('//')]
        current_rule: Optional[dict] = None
        line_number = 0
        for raw_line in lines:
            line_number += 1
            line = raw_line.strip()
            if line.startswith('WHEN '):
                if current_rule:
                    self._finalize_rule(current_rule, rules)
                current_rule = {
                    'trigger': line.replace('WHEN ', ''),
                    'trigger_keywords': [],
                    'actions': [],
                    'description': ''
                }
                match = re.match(r'WHEN\s+玩家提及\s+(.+)', line)
                if match:
                    current_rule['trigger_keywords'] = [
                        k.strip().replace('"', '') for k in match.group(1).split(',')
                    ]
                continue
            if line.startswith('IF ') and current_rule:
                current_rule['condition'] = self._parse_condition(
                    line.replace('IF ', ''), variables, line_number, errors
                )
                continue
            if line == 'THEN' and current_rule:
                continue
            if current_rule:
                action = self._parse_action(line)
                if action:
                    current_rule['actions'].append(action)
                continue
            if line.startswith('BECAUSE ') and current_rule:
                current_rule['description'] = line.replace('BECAUSE ', '').strip('"')
                self._finalize_rule(current_rule, rules)
                current_rule = None
                continue
        if current_rule and current_rule.get('trigger'):
            self._finalize_rule(current_rule, rules)
        return rules, errors

    def _parse_condition(self, expr: str, variables: dict,
                         line: int, errors: list) -> Optional[RuleCondition]:
        parts = expr.strip().split()
        if len(parts) < 3:
            errors.append({'line': line, 'message': f'Condition expression syntax error: {expr}'})
            return None
        field = f"character_state.{parts[0]}"
        op = parts[1]
        value = self._parse_value(' '.join(parts[2:]))
        if parts[0] not in variables:
            errors.append({'line': line, 'message': f'Undeclared variable: {parts[0]}'})
        op_map = {
            '>=': 'gte', '<=': 'lte', '>': 'gt', '<': 'lt',
            '==': 'eq', '!=': 'neq', 'CONTAINS': 'contains'
        }
        return RuleCondition(type=op_map.get(op, 'eq'), field=field, value=value)

    def _parse_action(self, line: str) -> Optional[RuleAction]:
        if line.startswith('SET '):
            parts = line.replace('SET ', '').split('=', 1)
            return RuleAction(type='set_variable', target=parts[0].strip(),
                              value=self._parse_value(parts[1].strip() if len(parts) > 1 else ''))
        if line.startswith('CHANGE '):
            parts = line.replace('CHANGE ', '').split(' BY ')
            return RuleAction(type='change_variable', target=parts[0].strip(),
                              delta=int(parts[1].strip()) if len(parts) > 1 else 0)
        if line.startswith('FORCE TONE '):
            return RuleAction(type='force_tone', value=line.replace('FORCE TONE ', '').strip('"'))
        if line.startswith('FORCE EMOTION '):
            return RuleAction(type='force_emotion', value=line.replace('FORCE EMOTION ', '').strip('"'))
        if line.startswith('UNLOCK MEMORY '):
            return RuleAction(type='unlock_memory', target=line.replace('UNLOCK MEMORY ', '').strip('"'))
        if line.startswith('LOCK MEMORY '):
            return RuleAction(type='lock_memory', target=line.replace('LOCK MEMORY ', '').strip('"'))
        if line.startswith('LOG '):
            return RuleAction(type='log', value=line.replace('LOG ', ''))
        return None

    def _parse_value(self, raw: str) -> Any:
        trimmed = raw.strip().strip('"')
        if trimmed == 'true': return True
        if trimmed == 'false': return False
        try: return int(trimmed)
        except ValueError:
            try: return float(trimmed)
            except ValueError: return trimmed

    def _finalize_rule(self, raw: dict, rules: list):
        import time
        base = '_'.join(raw.get('trigger_keywords', ['always'])).replace(' ', '_').lower()
        rule_id = f"{base}_{int(time.time() * 1000) % 100000}"
        rules.append(CharacterRule(
            id=rule_id, trigger=raw['trigger'],
            trigger_keywords=raw.get('trigger_keywords', []),
            condition=raw.get('condition'),
            actions=raw.get('actions', []),
            description=raw.get('description', '')
        ))

    def validate(self, dsl_source: str, variables: dict[str, VariableDefinition]) -> list[dict]:
        _, errors = self.compile(dsl_source, variables)
        return errors

    def decompile(self, rules: list[CharacterRule], variables: dict[str, VariableDefinition]) -> str:
        lines = []
        if variables:
            lines.append('VARIABLES:')
            for name, var in variables.items():
                range_str = f"range({var.range[0]},{var.range[1]})" if var.range else ''
                lines.append(f'  {name}: {var.type}, {range_str}, default {var.default}, "{var.description}"')
            lines.append('')
        for rule in rules:
            lines.append(f'WHEN {rule.trigger}')
            if rule.condition:
                field = rule.condition.field.replace('character_state.', '')
                op = self._op_to_string(rule.condition.type)
                lines.append(f'IF {field} {op} {rule.condition.value}')
            lines.append('THEN')
            for action in rule.actions:
                lines.append(f'  {self._action_to_string(action)}')
            lines.append(f'BECAUSE "{rule.description}"')
            lines.append('')
        return '\n'.join(lines)

    def _op_to_string(self, op_type: str) -> str:
        return {'gte': '>=', 'lte': '<=', 'gt': '>', 'lt': '<',
                'eq': '==', 'neq': '!=', 'contains': 'CONTAINS'}.get(op_type, '==')

    def _action_to_string(self, action: RuleAction) -> str:
        if action.type == 'set_variable': return f'SET {action.target} = {action.value}'
        if action.type == 'change_variable': return f'CHANGE {action.target} BY {action.delta}'
        if action.type == 'unlock_memory': return f'UNLOCK MEMORY "{action.target}"'
        if action.type == 'lock_memory': return f'LOCK MEMORY "{action.target}"'
        if action.type == 'force_tone': return f'FORCE TONE "{action.value}"'
        if action.type == 'force_emotion': return f'FORCE EMOTION "{action.value}"'
        return f'LOG "{action.description}"'
```

### 7.6 Collaboration with RuleCompiler (AI Compiler) (v2.1 New)

With the introduction of DSL, RuleCompiler's workflow upgrades to three coexisting modes:

**Mode A: Natural Language → JSON (Existing Flow, for Beginners)**
- User inputs natural language description.
- RuleCompiler directly generates JSON rules and stores in character card.

**Mode B: Natural Language → DSL → JSON (Recommended Flow, Readable Intermediate Representation)**
- User inputs natural language description.
- RuleCompiler generates DSL source (instead of direct JSON), more readable, easier for user review and fine-tuning.
- DSL source handed to deterministic DSL compiler for final JSON.
- Users see DSL text in the visual editor, can manually modify at any time.

**Mode C: Hand-written DSL → JSON (Expert Mode)**
- Creator writes DSL source directly in the editor.
- Deterministic compiler generates JSON without AI involvement.

Three modes coexist, lowering the barrier for creators of different levels.

### 7.7 Decision Trace & DSL (v2.1 New)

The decision trace panel is the core of Kernelsoul's visual debugging layer. When the execution engine triggers a rule, it pushes a `rule_trace` object to the frontend, which includes DSL source references in addition to JSON rule information.

**Example display when the "Praise King Trigger" fires:**

```
[Orange] Character Rule: Praise King Trigger
  Source: WHEN player mentions "king" IF mood < 0 THEN SET current_tone = "sarcastic" ...
  Reason: Keyword "king" detected in player input, and current mood = -3 (< 0)
  Action: tone → sarcastic, suspicion +10
```

If the creator has enabled `/debug on`, the frontend displays the complete DSL list of all rules, with triggered rules highlighted and non-triggered ones grayed out, along with real-time variable values.

### 7.8 Complete Example: Lilith's DSL Rule Set (v2.1 New)

```
VARIABLES:
  mood: int, range(-10,10), default 0
  trust_player: int, range(0,100), default 20
  fatigue: int, range(0,100), default 0
  suspicion: int, range(0,100), default 30
  current_tone: string, default "neutral"

WHEN player mentions "king", "royalty", "your majesty" IF mood < 0 THEN
  SET current_tone = "sarcastic"
  CHANGE suspicion BY +10
  FORCE EMOTION "resentful"
BECAUSE "Hearing praise of the king when in a bad mood triggers her sarcasm and wariness toward authority"

WHEN time_changes TO "midnight" IF trust_player >= 60 THEN
  UNLOCK MEMORY "lilith_betrayal_night"
  SET current_tone = "vulnerable"
BECAUSE "In front of someone she trusts, the loneliness of midnight makes her drop her guard and reveal past pain"

WHEN player mentions "betrayal", "knight" IF trust_player < 40 THEN
  SET current_tone = "cold"
  CHANGE suspicion BY +15
  FORCE TONE "cold"
BECAUSE "When she doesn't yet trust the player, touching old wounds triggers defensiveness and distance"

WHEN ALWAYS IF fatigue > 80 THEN
  SET current_tone = "tired"
  CHANGE mood BY -2
BECAUSE "Extreme fatigue naturally worsens mood and drains vitality from the tone"

WHEN player mentions "Azazel" IF trust_player >= 90 THEN
  UNLOCK MEMORY "lilith_true_name"
  SET current_tone = "sacred"
BECAUSE "Only someone with absolute trust can learn her true name — at that moment, she reveals her authentic self"
```

### 7.9 Version Compatibility & Evolution (v2.1 New)

- Existing Kernelsoul JSON rules can be losslessly converted to DSL (via decompiler), so existing character cards are unaffected.
- On engine startup, if a character card only contains JSON rules without DSL source, CharacterCardLoader attempts to decompile and generate DSL text, storing it in the `character_rules_dsl` field (optional).
- If both exist and are inconsistent, the DSL source takes priority (recompile to overwrite JSON), ensuring a single source of truth.

---

## VIII. Compatibility: Early vs. Late Mode

- **Early form (no graphics):** When the engine scans `/assets/` and finds it empty, image rendering is disabled and only plain text dialog and status bar are displayed. Multiple Tavern character cards and associated lorebooks can be directly imported.
- **Late form (2D full version):** Once image assets are placed, 2D rendering is auto-activated with zero code modification.

### 8.1 UI Performance & Interaction Benchmarks

**8.1.1 Response Latency Targets**

| Operation | Target Latency | User Perception |
|-----------|----------------|-----------------|
| Command response (/list, /select, etc.) | <50ms | Instant |
| Draft preview start (first token appears) | <500ms | Smooth |
| Typewriter effect | 30ms/char (configurable) | Comfortable reading pace |
| Status bar update | <100ms | Instant |

**8.1.2 Multimodal Interaction Planning (Later Extension):** Reserved voice input, character portrait, and background music interfaces.

**8.1.3 SillyTavern Mode UI Layout Reference:** Left: character list/session selector; Center: dialog flow (typewriter effect); Right: status panel; Bottom: input box; Top: character name/plugin entry.

### Decision Trace Panel (v2.0)

**Design Purpose:** When a character speaks, the UI highlights the rule that triggered it, helping players and creators understand "why the character said that."

**UI Specifications:**
1. Location: Bottom of the right-side status panel, collapsible, collapsed by default.
2. Content: Triggered rule name, trigger condition, executed action. Displays "No rules triggered this round" when no rules fire.
3. Style: Triggered rules highlighted in light color; global rules with blue ribbon, character rules with orange ribbon. Hover shows full description.
4. Debug mode (/debug on): Shows all rules list (fired highlighted, non-fired grayed out), character state variable real-time values, conditional memory unlock status.

**Frontend Data Source:** After each round submission, a `rule_trace` object is pushed (containing `triggered_rules` array and `character_state` snapshot).

**DSL Source-Level Highlighting (v2.1):** The `rule_trace` object adds a `dsl_source_lines` field, recording DSL source line ranges for each triggered rule. The interface highlights corresponding DSL code lines, with hover showing full parsing. Rules without DSL source show decompiled inferred text.

### 8.2 Frontend Context Network Design Specification (v2.3)

**8.2.1 Design Philosophy**

The frontend uses an event and registration-based Context network to achieve high composability. The system is split into independent Context objects that collaborate through two mechanisms:

- **Events:** Determine "when to do what" — action signals for flow control.
- **Registrations:** Determine "where to get data when doing it" — data source declarations that establish dependency relationships.

**8.2.2 Context Network Core Concepts**

| Concept | Description |
|---------|-------------|
| Context | Independent functional unit with private state, communicates with the outside via events |
| Event | Named signal carrying data payload. Any Context can emit, any Context can subscribe |
| Registration | Context declares dependencies on global resources at startup, injected by the global container |
| GlobalContext | Registration hub and event bus for Contexts |

**8.2.3 KernelsoulEngineContext as a Standard Context Node**

The Kernelsoul engine is encapsulated as `KernelsoulEngineContext`, connecting to the frontend network as a standard Context:

```python
class KernelsoulEngineContext:
    """Kernelsoul Engine Context Wrapper"""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.dsl_compiler = DSLCompiler()
        self.state_manager = CharacterStateManager()
        self._compiled_rules: dict[str, list] = {}
        self._variable_defs: dict[str, dict] = {}

    def init(self, global_context):
        """Initialize: register dependencies and bind events"""
        self.file_service = global_context.get('file_service')
        self.event_bus.on('character.switched', self._on_character_switched)
        self.event_bus.on('message.received', self._on_message_received)

    def _on_character_switched(self, char_id: str):
        """Character switch → auto-load DSL and compile"""
        dsl_source = self.file_service.get(f"character/{char_id}:character.dsl")
        if not dsl_source:
            self.event_bus.emit('v4.dsl.not_found', {'char_id': char_id})
            return
        variables = self._load_variable_defs(char_id)
        rules, errors = self.dsl_compiler.compile(dsl_source, variables)
        if errors:
            self.event_bus.emit('v4.dsl.compile_error', {'char_id': char_id, 'errors': errors})
            return
        self._compiled_rules[char_id] = rules
        self.state_manager.init_variables(variables)
        self.state_manager.load_rules(rules)
        self.event_bus.emit('v4.dsl.loaded', {'char_id': char_id, 'rule_count': len(rules)})

    def _on_message_received(self, message: dict):
        """Message arrives → evaluate rules → emit decisions"""
        char_id = message.get('char_id')
        rules = self._compiled_rules.get(char_id)
        if not rules:
            return
        context = {'message': message, 'timestamp': message.get('timestamp', 0)}
        decisions = self.state_manager.evaluate(context)
        for decision in decisions:
            self.event_bus.emit('v4.decision', decision)
```

**8.2.4 Integration with Gradio/Web UI**

When using Gradio as the frontend during MVP, the Context network is simplified to Gradio's State and Event mechanisms:

```python
import gradio as gr

def create_v4_interface(v4_context: KernelsoulEngineContext):
    with gr.Blocks() as app:
        state = gr.State({"char_id": None, "decisions": []})

        @gr.render(inputs=state)
        def decision_panel(s):
            for d in s.get("decisions", []):
                gr.Markdown(f"**{d['rule_description']}** — {d['actions_executed']}")

        msg_input = gr.Textbox()
        msg_input.submit(
            lambda msg, s: v4_context._on_message_received(
                {"content": msg, "char_id": s["char_id"]}),
            [msg_input, state], [state]
        )
```

**8.2.5 Language Agnosticism**

The Context network is fundamentally a design pattern (Observer Pattern + Dependency Injection), not a language-specific implementation. A TypeScript version uses `EventEmitter` base class; a Python version uses `asyncio.Event` or simple callback lists. Both implementations follow the same event naming conventions and data payload formats.

---

## IX. Standard End-to-End Execution Flow

1. **Command Interception:** Get player input. If it starts with `/` (e.g., `/character demon_hotel`, `/roll`, `/select 2`, `/plugin list`), directly execute the corresponding dispatch without consuming a round or entering AI flow.

2. **Plugin Input Interception (v1.3):** Trigger `on_user_input` hook. Registered plugins can inspect, modify, or intercept user input. If a plugin returns alternative text, use it to continue; if a plugin requests interception, terminate this round.

**Step 2.5: Greeting Initialization (v1.6)**

**Trigger timing:** Only triggered when `/newgame [name]` or `/load [name] [sessionID]` loads an empty session. Sessions with pre-existing dialogue history are not triggered (greeting already in history).

**Process:**
1. Extract greeting: If character card has `first_mes` field and it's non-empty, use as greeting. If character card lacks this field, use engine default greeting template: `[System]: Welcome to the story of {character_name}. You stand in {scene_description}. {character_name} is before you.`
2. Inject history chain: Greeting, as a system-level first message, is written directly to `history/full_log.txt` and `context/recent_log.txt`. It bypasses the draft area — it's deterministic and cannot be re-rolled.
3. Frontend display: UI first shows the greeting text, then the input box. Greeting is marked with a special style (e.g., italics or left sidebar color) to distinguish from AI-generated narrative.
4. Relationship with normal rounds: Greeting is not counted in `total_rounds`, does not trigger memory compression count, and does not trigger evolution triggers.

**Design Advantage:** Compatible with Tavern character card ecosystem (`first_mes` is a community standard). Players get atmosphere immediately upon entering, eliminating "blank page anxiety." Future custom greeting logic can be extended via plugin hook `on_session_start`.

3. **Lorebook Retrieval:** The engine's pure code module performs keyword matching on player text against the `_lorebook.json` file for the current character card, extracting matched entries.

4. **Context Packing:** Assemble the Prompt in the following order:
   - Currently active preset jailbreak (`system_prompt`)
   - Current character card settings (name, description, personality, prompt)
   - Lorebook matched entries
   - Current GameState textification (status bar description, confirmed values only)
   - Summary chain from `working_memory.json` (last 3 history summaries)
   - Last 10 rounds of confirmed dialogue text from `recent_log.txt`

**Step 4.1: Token Budget Check & Auto-Trimming (v1.6)**

After context packing completes and before sending the AI request, the engine must perform a token budget check.

**Configuration:** Add fields to system.json:

```json
{
  "max_context_tokens": 28672,
  "token_estimation_method": "char_ratio",
  "char_to_token_ratio": 0.5
}
```

- `max_context_tokens`: 80% of the model's context window (e.g., 28672 for DeepSeek-V3's 32K window).
- `token_estimation_method`: Estimation method. `char_ratio` uses character count ratio; `tiktoken` uses exact counting (requires tiktoken library).
- `char_to_token_ratio`: Rough conversion ratio from characters to tokens (Chinese ~0.5 token/char, English ~0.25 token/char).

**Trimming Strategy (executed from lowest to highest priority, re-estimate after each step until total token count is below limit):**

| Step | Trim Target | Operation | User Perception |
|------|------------|-----------|-----------------|
| 1 | Dialogue text | Reduce recent_log.txt from 10 to 5 rounds | Transparent |
| 2 | Dialogue text | Reduce recent_log.txt from 5 to 3 rounds | Transparent |
| 3 | Auto summaries | Reduce working_memory.json from 3 to 1 entries | Transparent |
| 4 | Manual memory (non-pinned) | Delete `pinned: false` entries from oldest to newest | Logged |
| 5 | Manual memory (pinned) | Never touch `pinned: true`; log warning and notify player if still over budget | Frontend prompt |

**Code skeleton:**

```python
def enforce_token_budget(prompt: str, max_tokens: int, ratio: float = 0.5) -> str:
    """Check and trim Prompt to fit token budget"""
    estimated = int(len(prompt) * ratio)
    if estimated <= max_tokens:
        return prompt
    # Execute trimming strategy step by step...
    return trimmed prompt
```

**Collaboration with Memory Manager:** Token budget check does not modify any persistent files. Trimming of recent_log, working_memory, and manual_memory only affects this round's Prompt construction; disk files remain unchanged.

5. **AI Generation:** Call LLM API. The Prompt has explicit instructions: "You are {character name}. Naturally roleplay, advancing the story like writing a novel. If you believe the current narrative leads to a clear state change (e.g., taking damage, obtaining items, affection change), you may append a Markdown code block (```json) at the very end of your response describing these changes. If you're unsure, or the narrative has no clear change, feel free to omit it. Narrative comes first."

6. **Draft Generation:** The Parser Engine receives the AI's raw response text, uses a three-stage strategy to extract state changes (see Section 10.1), assembles into a Draft object (containing draft_id, raw_response, parsed), and saves to `drafts/draft_xxx.json` (auto-incrementing number). Triggers `on_draft_created` hook.

**Step 6.1: AI Narrative Lorebook Secondary Retrieval (v1.6)**

After the parser extracts the narrative, the engine performs an additional lorebook keyword match on the AI-generated narrative text.

**Search scope:** Only the `narrative` field (plain text portion), not `state_changes`.

**Match result handling:**
1. Calculate the difference between this match set and the Step 3 (player input retrieval) match set.
2. Keep only entries that are "newly triggered by AI narrative, not present in player input."
3. These new entries are not injected into the current round but temporarily stored in session memory.
4. During the next round's context packing (Step 4), new entries are appended at the top of the lorebook section with the tag: `[New World Info Unlocked by Previous Round's Narrative]: {entry name}: {entry content}`

**Design Advantage:** Makes lorebook revelation a "bidirectional exploration" — both the player's active choices and the AI's narrative progression can gradually reveal the world, greatly enhancing the sense of discovery. Secondary retrieval only performs keyword matching on narrative text, with minimal performance cost.

7. **Preview & Pending Confirmation:** The frontend displays the latest draft's narrative text. The game state has not been updated yet; the history archive has not been written. The system enters a "pending confirmation" state.

**7.1. Streaming Rendering & Typewriter Effect**

During the draft preview phase, the frontend must implement the following interaction standards:

1. Streaming display: When AI generates text, if the API supports streaming output (e.g., DeepSeek/GPT's `stream=True`), the frontend should render narrative text character-by-character or sentence-by-sentence.
2. Typewriter effect: Text appears with smooth per-character animation, speed configurable (default 30ms/char). Users can click to skip animation at any time to display full text.
3. Generating state indicator: Non-intrusive loading indicator (flashing cursor or pulsing dot).
4. Interrupt generation: Provide a "Stop Generating" button (or `/stop` command); already generated portion is automatically saved as a draft.

8. **User Decision Branch:**
   - User inputs `/roll` → Return to Step 5, generate new draft and append-save, preserving old draft.
   - User inputs `/select N` → Proceed to Step 9 (Submit), selecting the specified draft.
   - User inputs other normal text (not starting with `/`) → Auto-equivalent to `/select latest`, first submit the latest draft, then use this text as the next round's player input.

9. **Submit & Bake:**
   a. Trigger `on_draft_selected` hook with selected draft data.
   b. Append selected draft's raw text to `/history/full_log.txt`.
   c. Refresh `/context/recent_log.txt` (keep last 10 rounds of confirmed dialogue).
   d. Call `State Manager.apply_state_changes()` to update `state.sav`.
   e. Draft cleanup: Delete unsaved draft files in `/drafts/`. Drafts marked with `/draft save` are moved to `/context/saved_drafts/`.
   f. Execute evolution trigger scan: Check rules in `rules.json` in order, execute actions for satisfied conditions. If phase changes, trigger `on_phase_change` hook.
   g. Memory compression check (dual-layer):
      - If total rounds reached a multiple of 10, trigger lightweight compression: Read `compression_prompt_light.txt` template, compress last 10 rounds into ≤200-char summary, append to `/history/full_memory.json` with `compression_type: "light"`.
      - If total rounds reached a multiple of 50, trigger deep compression: Read `compression_prompt_deep.txt` template, compress all dialogue since last deep compression (~50 rounds) into ≤2000-char deep summary with `compression_type: "deep"`.
      - After completion, refresh `/context/working_memory.json`: inject latest 1 deep summary + latest 3 lightweight summaries.
      - Trigger `on_memory_compressed` hook.
   h. Trigger `on_round_end` hook.
   i. Update `session_meta.json` (increment `total_rounds`, update `last_saved_at`).

10. **Loop:** Ready to receive next round input.

---

## X. AI Enforcement Contract Whitelist & Preset Jailbreaks

### 10.1 AI-Modifiable Field Whitelist

- **AI-Modifiable Fields (Whitelist):** hp, energy, goodwill, money, inventory, bg, emotion, cg
- **AI-Protected Fields (Read-Only):** phase, max_hp

After extracting JSON, the Parser Engine discards any fields not in the whitelist, keeping only legal changes.

### 10.2 AI-Protected Fields

- Preset files are stored in `/configs/presets/` directory.
- Players can hot-switch the system preset via `/preset [name]` without restarting the engine or reloading the character.
- After switching, the next round will use the new preset.

**Preset Jailbreak Marketplace Interface (v1.5):** Similar to the plugin marketplace, preset jailbreaks (`/presets/`) can also be shared via community index. The future `/market` command will support discovery and installation of both plugins and presets.

### 10.3 Preset Hot-Switching: `/preset xxx`

**Design Purpose:** Inject a "director's consciousness" into characters, enabling self-monitoring of character consistency in long dialogues.

**Template Preset (`/configs/presets/meta_cognition_v4.txt`):**

```
[Meta-Cognition Instructions - Character Self-Correction System]
You are a trained method actor. Perform a self-check before each response:
1. Character Consistency Check: Do your word choice, sentence structure, and tone match the character?
2. State Sync Check: Have internal states been updated? Does your response reflect state changes?
3. Story Coherence Check: Do you remember previous key events?
4. Deviation Correction: If any of the above fails, naturally and imperceptibly steer the conversation back on track.
```

**Loading method:** Kernelsoul character card's `meta_cognition_prompt` field takes priority; if not provided, this default template is used. Can be manually enabled via `/preset meta_cognition_v4`.

**Relationship with Character Prompt:** The character prompt defines what the character is; the meta-cognition prompt defines how the character self-monitors. They are concatenated during context packing: System preset → Character prompt → Meta-cognition preset.

---

## XI. Anti-Crash & Fault Tolerance Mechanisms

### 11.1 AI Output Stability Fallback Strategy

When direct extraction of valid JSON state changes from AI response text fails, the Parser Engine uses the following three-stage smart extraction strategy:

**Stage 1: Extract Markdown JSON Code Block**

```python
import re
import json

def extract_json_code_block(raw_text: str) -> dict | None:
    """Extract JSON from Markdown ```json code block"""
    match = re.search(r'```json\s*\n(.*?)\n```', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None
```

**Stage 2: Max Brace Backtracking**

```python
def extract_json_fallback(raw_text: str) -> dict | None:
    """Scan backwards from text end, extract last complete JSON object"""
    last_brace = raw_text.rfind('}')
    if last_brace == -1:
        return None
    depth = 0
    start = -1
    for i in range(last_brace, -1, -1):
        if raw_text[i] == '}':
            depth += 1
        elif raw_text[i] == '{':
            depth -= 1
        if depth == 0:
            start = i
            break
    if start == -1:
        return None
    candidate = raw_text[start:last_brace + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None
```

**Stage 3: Natural Language Simple Rule Extraction**

When both stages above fail, use the simplest regex pattern matching to extract only the most obvious state changes:

```python
def extract_from_natural_language(text: str) -> dict:
    """Extract most obvious state change patterns from natural language"""
    changes = {}
    # Damage pattern: receive/lose/deduct + number + points + damage/HP
    damage_match = re.search(r'(?:receive|lose|deduct)(?:s|ed)?(\d+)(?: points? of)?(?: damage| HP)', text, re.IGNORECASE)
    if damage_match:
        changes['hp'] = -int(damage_match.group(1))
    # Item gain pattern: gain/pick up/get + item name
    gain_match = re.search(r'(?:gain|pick up|get)(?:s|ted|s)? (?:a|an|the)?(.{1,20})', text, re.IGNORECASE)
    if gain_match:
        item = gain_match.group(1).strip()
        if len(item) <= 20:
            changes['inventory_add'] = [item]
    return changes
```

**Graded Fault Tolerance Strategy Summary:**

| Attempt | Strategy | User Perception |
|---------|----------|-----------------|
| Stage 1 | Extract ```json code block, validate Schema | Transparent, no sensation |
| Stage 1 fails | Use max brace backtracking, validate Schema | Transparent, no sensation |
| Stage 2 fails | Use natural language simple rule extraction (damage/item gain only) | Transparent. If still no change, frontend may lightly prompt "No state change this round" |
| 2 consecutive empty parses | Auto-switch to degraded Prompt (from fallback_prompt.txt), re-request AI; frontend shows "Regenerating..." | Brief wait |
| 3 consecutive empty parses | Abandon state change extraction, keep only narrative text as plain story draft; notify user "AI response format abnormal, generated plain text story. Use /roll to retry" | Clear notification |

**Degraded Prompt Template (`/configs/fallback_prompt.txt`):**

```
{Original system preset}
Current game state:
{state_text}
Recent dialogue history:
{recent_log}
Please continue the story as {character name}. Append a short JSON tag at the end of your response in the following format:
{"hp":0, "energy":0}
Only modify values that have changed. Do NOT add explanations.
```

### 11.2 General Fault Tolerance Mechanisms

1. **AI Contract Encoding Fault Tolerance:** `try...except` protects the entire parsing process. Any parsing failure will not crash the engine, only degrade processing per the graded strategy.
2. **Value Capping Protection:** State Manager has built-in clamping logic. Single damage/recovery cap can be configured in `rules.json` (e.g., `max_damage_per_turn: 50`). Changes exceeding the cap are auto-truncated.
3. **Lorebook Missing Tolerance:** If the corresponding `_lorebook.json` is not found for the current character card, the engine logs a message and skips the lorebook retrieval step, continuing normal operation.
4. **Art Asset Degradation:** UI Observer checks for required image files before rendering. If missing, auto-degrades to plain text mode without errors.
5. **Cross-Character Context Isolation (Critical):**
   - When the player executes `/character` or `/load` to switch characters, before reading new character data, the engine must perform a "forced memory reset":
     - Destroy current GameState instance.
     - Clear all files in `context/` (including recent_log.txt, working_memory.json, and entire drafts/ folder).
     - Unbind current PathResolver, create new instance bound to new character/session.
     - Load default values from new character card's initial_state, create brand new GameState.
     - **Absolutely forbidden** to carry any worldview fragments, dialogue history, or draft data from the old character card into the new character's prompt.
6. **Auto-create Non-Existent Paths:** PathResolver automatically calls `os.makedirs(..., exist_ok=True)` during initialization and before any write operation. If the player starts chatting immediately after `/newgame` but before folders are generated, the engine won't crash — it auto-creates all necessary directories and initial files.
7. **Draft Area Exception Protection:**
   - If an exception occurs when clearing `drafts/` after submission (e.g., file locked by external process), the engine logs the error but doesn't interrupt the game flow. Old drafts will be cleaned up on the next successful submission.
   - If the user enters `/roll` or `/select` without any existing drafts, the engine returns a friendly prompt: "No pending drafts to confirm," without executing any operation.
8. **Plugin Exception Isolation (v1.3 New):** Plugin Manager wraps each hook callback execution in `try...except`. Any exception thrown by a plugin is caught and logged, never causing the main loop to crash or affecting other plugins' normal operation.

### 11.3 Save Version Management

The `data_version` field in `session_meta.json` is used to mark the save format version. When future data structures are upgraded, the engine can perform migration based on this:

```python
def load_state_with_migration(path_resolver) -> GameState:
    """Load save state; auto-migrate if version mismatch"""
    meta = json.load(open(path_resolver.get_meta_file(), encoding='utf-8'))
    version = meta.get("data_version", 1)
    raw_state = json.load(open(path_resolver.get_state_file(), encoding='utf-8'))
    if version == 1:
        # Current version, load directly
        return GameState(**raw_state)
    elif version == 2:
        # Future v2 example: inventory structure upgrade
        raw_state = migrate_v1_to_v2(raw_state)
        return GameState(**raw_state)
    else:
        raise ValueError(f"Unsupported data version: {version}")

def migrate_v1_to_v2(raw: dict) -> dict:
    """v1 -> v2 migration example: convert inventory from List[str] to List[Item]"""
    if "inventory" in raw and isinstance(raw["inventory"], list) and len(raw["inventory"]) > 0:
        if isinstance(raw["inventory"][0], str):
            raw["inventory"] = [{"name": item, "quantity": 1} for item in raw["inventory"]]
    return raw
```

### 11.4 Death & Failure State Handling (v1.6)

**Trigger Condition:** State Manager detects `GameState.hp <= 0` after each round submission (Step 9d).

**Processing Flow:**
1. **State Lock:** hp locked to 0; energy, inventory, goodwill, money locked to current values; bg, emotion, cg still modifiable by AI (for death scene description); phase can be set to special value (e.g., -1 for death ending).
2. **Auto Memory Injection:** Engine appends a system-level memory entry to `manual_memory.json` with content `[System Record]: Character died on round {N}.`, `pinned: true`, `source: "system"`.
3. **Rule Trigger:** Evolution trigger checks `rules.json` for death rules with `hp == 0`, executes corresponding actions (e.g., `set_phase: -1`).
4. **AI Prompt Injection:** In the next round's context packing, append at the end of the system preset: `[Important: The character has died. Please narrate the character's ending and epilogue in a closing narrative style. At the end of your response, remind the player they can enter /newgame to start a new playthrough, or /load to return to a previous save.]`
5. **Player Options:** Continue entering text (AI responds in "epilogue" mode); `/newgame` to start fresh; `/load [name] [sessionID]` to load save; if multi-timeline snapshots exist, use `/branches` to trace back to branch points.

**Design Principle:** Death is not a cold "Game Over" but a ritualistic narrative node. Locked states prevent AI from continuing to manipulate values after death, while preserving narrative space for the player to gracefully conclude the story.

---

## XII. Memory Compression Prompt Templates

### 12.1 Template Storage Locations [v2.3]

- `/configs/compression_prompt_light.txt` — Lightweight compression template (10 rounds, 200 char limit)
- `/configs/compression_prompt_deep.txt` — Deep compression template (50 rounds, 2500 char limit)
- `/configs/compression_prompt_merge.txt` — Lightweight summary merging template [v2.3.1]
- `/configs/compression_prompt_epic.txt` — Epic compression template (200 rounds, 5000 char limit) [v2.3.1]

### 12.2 Template Content [v2.3]

**12.2.1 Lightweight Compression Template (`/configs/compression_prompt_light.txt`):**

```
You are a game narrative summary generator. Compress the following dialogue history into a third-person summary.

Requirements:
1. Strictly limited to 200 characters or fewer.
2. Keep only the most core events and state changes.
3. Output plain text, no markers.

Dialogue history:
{chat_history}

Summary:
```

**12.2.2 Deep Compression Template (`/configs/compression_prompt_deep.txt`):**

```
You are a game narrative deep summary generator. Compress the following longer dialogue history into a detailed third-person summary.

Requirements:
1. Limited to 2000 characters or fewer.
2. Must preserve:
   - Core event chain and causal relationships
   - Character attitude and relationship evolution trajectory
   - Important item acquisitions and losses
   - Key state changes (injury, emotional shifts, etc.)
   - Important worldbuilding revelations
3. Organize chronologically, maintain narrative coherence.
4. Output plain text, no markers.

Dialogue history:
{chat_history}

Deep Summary:
```

**12.2.3 Epic Compression Template (`/configs/compression_prompt_epic.txt`):**

```
You are a game narrative epic summary generator. Merge the following multiple deep summaries into a macro-narrative summary.

Requirements:
1. Limited to 5000 characters or fewer.
2. Must distill:
   - Core themes and main narrative thread
   - Character arcs and relationship network evolution
   - Key item status changes
   - Unresolved foreshadowing and cliffhangers
3. Organize chronologically, maintain narrative coherence.
4. Output plain text, no markers.

Deep summary collection:
{combined_deep_summaries}

Epic Summary:
```

### Three-Layer Compression Architecture Overview

| Layer | Trigger Frequency | Input Source | Output Length | Purpose |
|-------|-----------------|-------------|---------------|---------|
| Light | Every 10 rounds | Last 10 rounds original text | ~200 chars | Recent details |
| Deep | Every 50 rounds | Light summary merge (layered) or original text (fallback) | ~2500 chars | Mid-range narrative arc |
| Epic | Every 200 rounds | Deep summary merge | ~5000 chars | Global story thread, character arcs, theme distillation |

### Layered Compression Principle

50 rounds of original dialogue (potentially 22,000+ chars, exceeding context window)
 → Split into 5 batches, 10 rounds each → 5 lightweight compressions (~200 chars each)
 → Concatenate lightweight summaries → AI merge → Deep summary (~2500 chars)

200 rounds of dialogue → 4 deep summaries → Concatenate → AI merge → Epic summary (~5000 chars)

**Key differences from old approach:**
- Old: 50 rounds original text → direct generation of deep summary (may exceed window)
- New: 50 rounds → 5 lightweight summaries → Concatenate → Merge into deep summary

### Context Injection Rules

Context = Latest 1 epic summary + Latest 1 deep summary + Latest 3 lightweight summaries + Last 10 rounds original text + Manual memory anchors (highest priority)

### Deep Compression Implementation

- **Layered Merge Mode (Preferred):** When ≥3 lightweight summaries exist, collect and concatenate into a segmented timeline, use `compression_prompt_merge.txt` to call AI for merging.
- **Original Text Fallback Mode:** When lightweight summaries are insufficient (<3), compress directly from `full_log.txt` original text using `compression_prompt_deep.txt`.

### Safe Truncation Mechanism

`_safe_truncate(text, max_chars)`:
- Truncate at periods/question marks/exclamation marks/newlines
- Truncation position must not be too early (keep at least 80% of max_chars)
- Hard truncate if no suitable position found

### Constants

```python
LIGHT_INTERVAL = 10
DEEP_INTERVAL = 50
EPIC_INTERVAL = 200
LIGHT_MAX_CHARS = 200
DEEP_MAX_CHARS = 2500
EPIC_MAX_CHARS = 5000
```

### working_memory.json Structure

```json
{
  "epic_summary": { "compression_id":1, "type":"epic", "round_range":"1-200", "summary":"..." },
  "deep_summaries": [ { "compression_id":4, "type":"deep", "round_range":"151-200", "summary":"..." } ],
  "light_summaries": [ { "compression_id":18, "type":"light", "round_range":"181-190", "summary":"..." } ]
}
```

### New Prompt Templates

- `compression_prompt_merge.txt`: For merging multiple lightweight summaries into a deep summary. Placeholder: `{combined_summaries}`
- `compression_prompt_epic.txt`: For merging multiple deep summaries into an epic summary. Placeholder: `{combined_deep_summaries}`. Requires distillation of core themes/protagonist arc/relationship network/key items/unresolved foreshadowing.

### 12.3 Working Memory Construction Rules [v2.3.1]

During context packing, filter from the summary chain in `/history/full_memory.json` to inject into `working_memory.json`:

```python
def build_working_memory(full_memory: dict) -> dict:
    entries = full_memory.get("entries", [])
    epic = [e for e in entries if e.get("compression_type") == "epic"]
    deep = [e for e in entries if e.get("compression_type") == "deep"]
    light = [e for e in entries if e.get("compression_type") == "light"]
    return {
        "epic_summary": epic[-1] if epic else None,         # Latest 1 epic summary
        "deep_summary": deep[-1] if deep else None,         # Latest 1 deep summary
        "light_summaries": light[-3:] if len(light) >= 3 else light  # Latest 3 lightweight summaries
    }
```

Epic summaries provide global story threads and character arcs (5000-char level); deep summaries provide mid-range narrative arcs (2500-char level); lightweight summaries provide recent details (200-char level).

### 12.4 full_memory.json Entry Structure Update [v2.3.1]

Each summary entry contains a `compression_type` field, distinguishing compression type ("light" | "deep" | "epic"):

```json
{
  "compression_id": 5,
  "compression_type": "light",
  "round_range": "41-50",
  "summary": "...",
  "timestamp": "2026-06-29T15:30:00Z"
}
```

### 12.5 Three-Layer Compression Architecture Overview [v2.3.1]

*(Duplicated in original, shown above)*

### 12.6 Layered Compression Principle [v2.3.1]
*(Duplicated in original, shown above)*

### 12.7 Context Injection Rules [v2.3.1]
*(Duplicated in original, shown above)*

### 12.8 Deep Compression Implementation [v2.3.1]
*(Duplicated in original, shown above)*

### 12.9 Safe Truncation Mechanism [v2.3.1]
*(Duplicated in original, shown above)*

### 12.10 Constants [v2.3.1]
*(Duplicated in original, shown above)*

### 12.11 working_memory.json Structure [v2.3.1]
*(Duplicated in original, shown above)*

---

## XIII. Plugin System Design Specification

### 13.1 Design Goals & Minimal Installation

1. **Open Ecosystem:** Allow third-party developers to write functional extensions for the engine without modifying core code.
2. **Secure Isolation:** Plugins run in a restricted sandbox environment, unable to freely access the filesystem or compromise engine stability.
3. **Deep Integration:** Through lifecycle hooks, plugins can intervene at various key nodes of the game flow.

**13.1.1 Minimal Installation Design**

Plugin installation follows the "drop in and use" principle:

1. User copies the plugin folder to `/plugins/` directory.
2. Engine automatically discovers and loads on next startup.
3. If engine is already running, user can hot-load via `/plugin reload [pluginID]`.
4. Plugin Python dependencies are declared in `manifest.json`'s `pip_dependencies` field; engine auto `pip install` on first load (requires user confirmation).

**New manifest fields:** `pip_dependencies`, `min_engine_version`, `homepage`, `license`.

### 13.2 Plugin Manifest Specification (manifest.json)

Each plugin must include `manifest.json` in its root directory:

```json
{
  "id": "stats_tracker",
  "name": "Statistics Tracking Panel",
  "version": "1.0.0",
  "author": "developer_name",
  "description": "Records and displays player death count, dialogue rounds, and other statistics across all playthroughs",
  "engine_version": ">=1.4.0",
  "dependencies": [],
  "hooks": [
    "on_session_start",
    "on_round_end",
    "on_session_end"
  ],
  "permissions": [
    "read_state",
    "write_file",
    "read_history"
  ]
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier, must match plugin folder name |
| name | string | Plugin display name |
| version | string | Plugin version, semver compliant |
| author | string | Author attribution |
| description | string | Brief plugin function description |
| engine_version | string | Minimum engine version required |
| dependencies | list | List of dependent plugin IDs (optional) |
| hooks | list | Registered lifecycle hooks list |
| permissions | list | Requested permissions list |

### 13.3 Permission System

| Permission | Level | Allowed Operations |
|------------|-------|-------------------|
| read_state | Low | Read snapshot of current GameState (no modification) |
| write_state | High | Directly modify GameState. Requires explicit user confirmation on first load. |
| read_history | Low | Read dialogue records and summaries in /history/ |
| write_file | Medium | Freely read/write within /plugins/<plugin_id>/ dedicated directory |
| network | High | Initiate external network requests. Requires manual user approval on first use. |
| ui_inject | Medium | Inject custom HTML panels, buttons, or styles into frontend interface |

### 13.4 Lifecycle Hook Definitions

```python
class PluginHooks:
    """All lifecycle hooks that a plugin can register.
    Each hook is an async method, default implementation is empty (no-op).
    Plugins only need to override the hooks they care about."""

    async def on_engine_start(self, config: dict) -> None:
        """Triggered on engine start. config contains complete system.json config."""

    async def on_session_start(self, character: str, session: str, state: GameState) -> None:
        """Triggered when entering a session (new game or loading save)."""

    async def on_user_input(self, text: str) -> str | None:
        """
        User input interception hook.
        Returns str to replace user input text and continue flow.
        Returns None to keep original input unchanged.
        Can be used for custom commands or input filtering.
        """

    async def on_draft_created(self, draft: dict) -> None:
        """Triggered after a new draft is generated. draft contains narrative and state_changes."""

    async def on_draft_selected(self, draft: dict) -> None:
        """Triggered after user confirms selection of a draft."""

    async def on_round_end(self, round_num: int, state: GameState) -> None:
        """Triggered after each round completes (after submission and history write)."""

    async def on_memory_compressed(self, summary: str) -> None:
        """Triggered when memory compression completes. summary is the newly generated summary text."""

    async def on_phase_change(self, old_phase: int, new_phase: int) -> None:
        """Triggered when evolution phase changes."""

    async def on_session_end(self, character: str, session: str) -> None:
        """Triggered when leaving a session (before switching character or closing engine)."""

    async def on_engine_stop(self) -> None:
        """Triggered before engine shutdown. Can be used to save plugin state, clean up resources."""
```

### 13.5 Plugin Manager Implementation

```python
import importlib
import json
import os

class PluginManager:
    """Plugin Manager: discovers, validates, loads plugins; manages lifecycle hooks."""

    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: dict[str, dict] = {}
        # Initialize callback lists for all hooks
        self.hooks: dict[str, list] = {
            hook: [] for hook in dir(PluginHooks)
            if hook.startswith("on_")
        }

    def discover_plugins(self):
        """Scan plugin directory, validate and load all valid plugins."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)
            return
        for folder in os.listdir(self.plugin_dir):
            manifest_path = os.path.join(self.plugin_dir, folder, "manifest.json")
            if not os.path.exists(manifest_path):
                continue
            with open(manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)
            # Permission audit: log high-risk permissions
            permissions = manifest.get("permissions", [])
            if "write_state" in permissions:
                print(f"[Plugin] {manifest['name']} requests write_state permission, user confirmation required")
            if "network" in permissions:
                print(f"[Plugin] {manifest['name']} requests network permission, user approval required")
            # Dynamic import of plugin module
            module = importlib.import_module(f"plugins.{folder}")
            self.plugins[manifest["id"]] = {
                "manifest": manifest,
                "module": module,
                "enabled": True
            }
            # Register hook callbacks
            for hook_name in manifest.get("hooks", []):
                if hasattr(module, hook_name):
                    self.hooks[hook_name].append(getattr(module, hook_name))
            print(f"[Plugin] Loaded: {manifest['name']} v{manifest['version']}")

    async def fire_hook(self, hook_name: str, *args, **kwargs):
        """Asynchronously trigger all registered callbacks for a specified hook."""
        for callback in self.hooks.get(hook_name, []):
            try:
                await callback(*args, **kwargs)
            except Exception as e:
                print(f"[Plugin] Hook {hook_name} execution error: {e}")
                # Isolate exception, does not affect engine or other plugins

    def reload_plugin(self, plugin_id: str):
        """Hot-reload specified plugin."""
        if plugin_id not in self.plugins:
            print(f"[Plugin] Plugin not found: {plugin_id}")
            return
        plugin_info = self.plugins[plugin_id]
        manifest = plugin_info["manifest"]
        # Remove old callbacks from hook list
        for hook_name in manifest.get("hooks", []):
            old_func = getattr(plugin_info["module"], hook_name, None)
            if old_func in self.hooks[hook_name]:
                self.hooks[hook_name].remove(old_func)
        # Reload module
        new_module = importlib.reload(plugin_info["module"])
        self.plugins[plugin_id]["module"] = new_module
        # Register new callbacks
        for hook_name in manifest.get("hooks", []):
            if hasattr(new_module, hook_name):
                self.hooks[hook_name].append(getattr(new_module, hook_name))
        print(f"[Plugin] {plugin_id} reloaded")
```

### 13.6 Plugin Sandbox Rules

1. **Filesystem Isolation:** Plugins can only write to the `/plugins/<plugin_id>/` directory. Read access is limited to that directory and `/saves/` (requires `read_history` permission). PathResolver does not expose system absolute paths to plugins.
2. **Exception Isolation:** As described in Section 11.2, item 8, any exception thrown by a plugin is silently caught by the engine, not affecting the main loop.
3. **Network Constraints:** Plugins requesting `network` permission require a popup for user approval on first network request. Users can revoke at any time via `/plugin disable`.
4. **State Modification Constraints:** Plugins requesting `write_state` permission require explicit user confirmation on load. It is recommended that such plugins implement their own secondary confirmation logic before modifying state.

### 13.7 Official Example Plugin: Stats Tracker

`/plugins/example_stats_tracker/__init__.py`:

```python
"""Stats Tracker: Records key player data across all sessions.
Demonstrates use of on_session_start, on_round_end hooks,
and write_file permission for data persistence."""

import json
import os

# Plugin private data
stats_file = os.path.join("plugins", "example_stats_tracker", "data.json")
stats = {"total_deaths": 0, "total_rounds": 0, "sessions_played": 0}

def _load_stats():
    global stats
    if os.path.exists(stats_file):
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

def _save_stats():
    os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

# Load existing stats on engine startup
_load_stats()

async def on_session_start(character, session, state):
    """Increment count on new session start."""
    stats["sessions_played"] += 1
    _save_stats()

async def on_round_end(round_num, state):
    """Update total rounds and detect death on each round end."""
    stats["total_rounds"] = round_num
    if state.hp <= 0:
        stats["total_deaths"] += 1
    _save_stats()
```

### 13.8 Plugin Marketplace Interface Planning (Future Extension)

**13.8.1 Marketplace Index Format**

`/plugins/market_index.json`:

```json
{
  "name": "Official Plugin Marketplace",
  "url": "https://plugins.example.com/index.json",
  "plugins": [
    {"id": "stats_tracker", "name": "Stats Tracking Panel", "version": "1.0.0", "author": "dev_name", "description": "..."}
  ]
}
```

**13.8.2 Reserved Commands:** `/market list`, `/market install`, `/market update`

---

## XIV. Optional Extension: Multi-Timeline Snapshots

The current design is "temporarily store within round, delete after confirmation." Future upgrades could develop into a branching story tree system:

- **Preserve Branches:** Unselected drafts in `/drafts/` are not deleted but automatically moved to `/history/branches/` directory, cataloged by branch point and timestamp.
- **Backtrack Command:** Provide `/branches` command to list all available branch points; provide `/branch [branchID]` command allowing players to return to a historical point and restart from another draft, creating a new parallel timeline session.
- **Visual Branch Tree:** Display branching history as a tree diagram in the frontend, allowing players to intuitively see how their choices affected the story direction.
- This extension is not in MVP scope, but the underlying data structures (draft file format, dual-track save system) are fully compatible and can be implemented without destructive modifications.

### Branch Tree Visualization Plan

1. **Branch Tree Panel:** Display all branch points as a tree diagram, showing player input summaries, creation timestamps, and highlighting active branches.
2. **Backtrack Operation:** Click on historical nodes to preview story; provide "Start New Worldline from This Branch Point" button.
3. **Branch Comparison:** After selecting two branch nodes, highlight state differences (HP, inventory, etc.).

---

## XV. MVP Development Priority Guide (Strict Order)

### Phase 1: Foundation
- Implement PathResolver class, ensure all path dynamic concatenation and auto directory creation.
- Implement GameState data class, test JSON serialization/deserialization.
- Implement State Manager basic read/write of state.sav.
- Implement read/write of session_meta.json and data_version marking.

### Phase 2: Connect AI Contract & Drafts
- Connect API (DeepSeek / GPT / Local Ollama), construct basic prompt.
- Implement Parser Engine's three-stage extraction strategy (Markdown JSON → Max brace backtrack → Natural language rules).
- Implement draft file generation and saving to /drafts/.
- Implement /roll, /select, /drafts commands and auto-submit logic.
- Test "hit me" scenario: Can AI correctly return optional JSON? Can parser correctly extract and deduct HP?

### Phase 3: Retriever Test
- Hardcode a lorebook keyword in code (e.g., "rooftop"), check if engine correctly extracts and assembles lorebook entry into Prompt.

### Phase 4: Evolution Test
- Write simple rules in rules.json (e.g., goodwill > 50 = phase 2).
- Test engine's auto-detection of thresholds and forced modification of phase field after submission.

### Phase 5: Memory Compression
- Implement dual-track writing: full_log.txt append, recent_log.txt refresh.
- Implement 50-round trigger compression logic, call AI to generate summary.
- Implement summary chain management (full_memory.json append, working_memory.json update with latest 3).

### Phase 6: Multi-Character & System Command Test
- Manually create two character folders in /saves/ (demon_hotel and cyber_elf) with initial saves.
- Test /character, /newgame, /load commands.
- Key validation: Does engine perform forced memory reset when switching characters? Does AI response tone change accordingly?
- Key validation: Are old character dialogue fragments completely isolated, not contaminating new character's context?

### Phase 7: Plugin System
- Implement CharacterStateManager (Section 4.3).
- Implement Kernelsoul character card extension field loading and initialization.
- Implement dual-layer rule execution order (Global rules → Character rules).
- Implement PluginManager class: scan, validate, load, hook registration.
- Implement sandbox isolation and exception capture.
- Implement /plugin list/reload/enable/disable commands.
- Write official example plugin (Stats Tracker) for end-to-end test.

### Phase 8: UI Mounting
- Replace command-line black box with Pygame or Web interface.
- Implement draft preview (display narrative), draft list, status bar display.
- Connect UI Observer, implement auto plain-text degradation when images are missing.
- Implement Decision Trace Panel.
- Implement /debug on/off commands.
- Status monitor supports real-time display of character state variables.

---

## XVI. Development Environment & Infrastructure

- **Programming Language:** Python 3.10+. Recommended to use asyncio to prevent API requests from blocking the main loop.
- **LLM Solutions:**
  - Online: DeepSeek API, OpenAI GPT API.
  - Local: Ollama (e.g., Qwen2.5-14B, Llama 3, etc.).
- **Core Strategy:**
  - All file paths dynamically concatenated through PathResolver; hardcoded absolute paths prohibited.
  - Any write operations to state (state.sav) or history (full_log.txt) only occur after user confirms draft submission. Draft phase never modifies confirmed data.

### Data Sovereignty Design Principles (v1.5)

1. All data stored locally, no cloud storage dependency.
2. Open format: saves, logs, and character cards are all human-readable plain text formats.
3. One-click export/import: `/export [sessionID]` and `/import [path]` commands, packaging as ZIP.
4. No forced internet connection: Local Ollama can fully replace online API.
5. No content censorship: The engine itself does not contain content filtering logic.

---

## Part V: Ecosystem Expansion Roadmap [v2.3]

*This section plans Kernelsoul Character OS expansion paths in game engine integration, development tools, SDK distribution, etc. All interfaces are design reserves that do not block MVP.*

---

## XVII. Unity / Unreal Integration

### 17.1 Integration Architecture

The Kernelsoul engine core runs independently as a Python process, exposing capabilities to game engines via inter-process communication (gRPC or WebSocket):

| Approach | Description | Recommended Scenario |
|----------|-------------|---------------------|
| **gRPC Service** | Python engine as independent process, gRPC bidirectional streaming | Production, cross-language |
| **WebSocket** | Engine starts WebSocket server | Rapid prototyping, web-friendly |
| **Python.NET Embedding** | Unity directly calls Python runtime | Low-latency requirement |

**Recommended path:** gRPC Service (language-agnostic, high performance, bidirectional streaming).

### 17.2 gRPC API Specification

```protobuf
service KernelsoulEngine {
  rpc LoadCharacter(LoadRequest) returns (LoadResponse);
  rpc GetResponse(DialogueRequest) returns (DialogueResponse);
  rpc GetState(StateRequest) returns (StateResponse);
  rpc GetUnlockedMemories(MemoryRequest) returns (MemoryResponse);
  rpc StreamDialogue(DialogueRequest) returns (stream DialogueChunk);
}

message DialogueRequest {
  string char_id = 1;
  string player_input = 2;
  map<string, string> game_context = 3; // Game world state
}

message DialogueResponse {
  string narrative = 1;
  repeated Action state_changes = 2;
  repeated Decision decisions = 3;
  map<string, string> character_state = 4;
}
```

### 17.3 Unity C# SDK

```csharp
public class KernelsoulNPC : MonoBehaviour {
    public string characterId;
    private KernelsoulClient client;

    public async Task<string> Talk(string playerInput);
    public Dictionary<string, object> GetCharacterState();
    public List<string> GetUnlockedMemories();
}

public class KernelsoulDialogueUI : MonoBehaviour {
    public KernelsoulNPC npc;
    public Text dialogueText;
    public DecisionPanel decisionPanel; // Decision trace
}

public class KernelsoulAnimationTrigger : MonoBehaviour {
    public KernelsoulNPC npc;
    // Listen for v4.decision → match force_tone/force_emotion → trigger animation
}
```

### 17.4 Prefab Components

| Component | Function |
|-----------|----------|
| `KernelsoulNPC` | Attach to GameObject, manage character lifecycle |
| `KernelsoulDialogueUI` | Auto-display dialogue text and decision trace panel |
| `KernelsoulAnimationTrigger` | Map `force_tone`/`force_emotion` to animation state machine |
| `KernelsoulMemoryInspector` | Debug panel, real-time display of character internal state and rule triggers |

### 17.5 Unreal C++ SDK

```cpp
UCLASS()
class UKernelsoulNPCComponent : public UActorComponent {
    FString CharacterId;
    UKernelsoulClient* Client;
public:
    void Talk(FString PlayerInput, FOnDialogueComplete Callback);
    TMap<FString, FString> GetCharacterState();
};
```

---

## XVIII. Kernelsoul Character Creation Workbench

### 18.1 Positioning

Independent web editor where creators generate Kernelsoul character cards using DSL or natural language, exportable as game assets.

### 18.2 Feature List

| Feature | Description |
|---------|-------------|
| Natural language input | Enter character description → RuleCompiler generates DSL preview |
| DSL editor | Syntax highlighting, real-time validation, error line hints |
| JSON rule visualization | Table/graphical editing, bidirectional DSL sync |
| Variable monitor | Real-time view of `character_state` changes |
| Dialogue test panel | Enter player text, view AI responses and triggered rules |
| One-click export | Character folder (.dsl + .json + .txt) → game assets |
| Version control | Character card change history with rollback support |

### 18.3 In-Game Hot Reload

Developers specify character folder path in Unity/Unreal. The `KernelsoulNPC` component monitors file changes, automatically recompiles DSL and hot-reloads the character without restarting the game.

---

## XIX. Kernelsoul Dialogue SDK

### 19.1 Positioning

Packaging the Kernelsoul engine as `pip install kernelsoul-character-os` — game developers integrate with one line of code.

### 19.2 Core Interface

```python
from kernelsoul import KernelsoulSession

session = KernelsoulSession(char_id="innkeeper", session_id="session_01")
response = session.send("Hello, traveler.")

# response: {
#   "dialogue": "Welcome to my inn...",
#   "actions": [...],
#   "state_changes": {...},
#   "decisions": [...],
#   "character_state": {"mood": 3, "trust_player": 25}
# }
```

### 19.3 pip Package Structure

```
kernelsoul-character-os/
├── v4/
│   ├── engine.py       # KernelsoulSession main class
│   ├── compiler.py     # DSLCompiler
│   ├── state_manager.py  # CharacterStateManager
│   ├── rules.py        # EvolutionTrigger
│   ├── memory.py       # MemoryManager (dual-layer compression)
│   ├── file_service.py # FileService
│   └── bridge.py       # AIBridge
├── pyproject.toml
└── README.md
```

### 19.4 Built-in Capabilities (Zero Configuration)

- Dual-layer memory compression (10-round lightweight + 50-round deep)
- Three-stage JSON fault tolerance
- Death state handling
- Evolution rule execution
- Manual memory anchors

---

## XX. Other Ecosystem Extensions

### 20.1 Godot / Custom Engine Integration

Kernelsoul engine's gRPC API natively supports any language. Godot (GDScript/C#) calls via gRPC client; custom C++ engines connect via gRPC C++ SDK.

### 20.2 Mod Tools

Kernelsoul engine is compiled into a standalone executable (PyInstaller). Mod authors place it in the game directory, communicating with the game through standard input/output.

**Applicable scenarios:**
- Skyrim/Fallout (SKSE/F4SE scripts calling external process)
- Minecraft (Forge/Fabric mods calling Python process)
- Any mod framework supporting external process calls

**Communication Protocol** (standard input/output, JSON lines):

```
→ {"cmd": "load", "char_id": "innkeeper"}
← {"status": "ok", "char_name": "Innkeeper"}

→ {"cmd": "send", "input": "Hello"}
← {"dialogue": "...", "actions": [...], "decisions": [...]}
```

### 20.3 Prototype Generator

Input a one-sentence description → RuleCompiler batch mode → Generate complete Kernelsoul character folder.

```bash
kernelsoul generate "A cold-on-the-outside but soft-hearted bounty hunter afraid of spiders who loves coffee" --output ./characters/bounty_hunter
```

**Generated output:** character.dsl, character_data.json, character_rules.json, meta_cognition.txt

---

## XXI. Semantic Narrative Rendering Engine [v2.4]

### 21.1 Problem Definition

Games are fundamentally driven by numbers, but what is presented to the player must be narrative text with texture. The simplest approach is handwritten conditional tables — output corresponding state descriptions as prompts when variable A > threshold α AND variable B < threshold β. However, when variables exceed a certain count, combinatorial explosion makes conditional tables unmaintainable.

Various solutions exist in modern games, but they fundamentally require pre-writing. In AI narrative games, conditional tables can be used alongside LLMs, but this introduces issues like insufficient factual consistency and narrative jumps between different ranges.

This engine proposes a rendering scheme based on a semantic state machine in embedding space, building a computable intermediate layer between the deterministic kernel and AI text generation.

**Boundary with existing architecture:** The semantic rendering engine is positioned after rule engine execution and before context packing. It does not replace any existing module but provides a more deterministic alternative for the "values → narrative" step. When rendering mode is `direct`, engine behavior is identical to v2.3.

### 21.2 Core Concepts

#### 21.2.1 Semantic Axis

A semantic axis describes the semantic direction of a state dimension from negative to positive pole. Let `e(x)` be a function that converts a phrase into an embedding vector. The semantic axis is defined as:

```
D_i = e(positive_anchor_phrase_i) - e(negative_anchor_phrase_i)
```

The positive and negative anchor phrases are defined by the game designer as needed. For example, for a dimension describing "stability," the positive anchor could be "completely stable" and the negative anchor "utterly collapsed," with specific wording depending on the game world's writing style.

#### 21.2.2 Semantic State Point

The representation of the current state in semantic space, consisting of a direction vector `p` and an intensity scalar `r`:

```
z = r × p
```
- `p`: Semantic direction of the current state (on a low-dimensional sphere).
- `r`: Narrative intensity of the current state (how "prominent" the combination is).

#### 21.2.3 Warp Function (Nonlinear Mapping from Values to Semantic Amplitude)

Game value changes are physical quantities; semantic changes are narrative quantities. A layer of nonlinear mapping is needed between them. When a variable changes from a to a + Δv, the same Δv may be just a "slight change" in a stable region but a "dramatic shift" in a critical region. The specific semantic description is freely defined by the designer according to writing style.

The Warp function converts value change Δv into semantic space amplitude change Δt:

```
Δt = semantic_warp(v, Δv)
```

#### 21.2.4 Semantic Momentum

The position of a state carries narrative information, but so does the speed of state change. Two paths with the same endpoint have completely different narrative meanings. Semantic momentum v_semantic records "where the state is heading."

### 21.3 Mathematical Framework

#### 21.3.1 Semantic Axis Construction

For each game dimension requiring narrative, define a pair of positive and negative anchor phrases and compute the semantic axis:

```
D_i = e(positive_phrase_i) - e(negative_phrase_i)
```

All semantic axes form the axis matrix:

```
A = [D_1, D_2, ..., D_m]
```

#### 21.3.2 Gram Matrix & Decoupled Readings

Semantic axes are typically not orthogonal. For example, "variable A (degree of risk)" and "variable B (degree of structural integrity)" may be highly correlated in embedding space. Direct dot-product reading of semantic components produces crosstalk.

The Gram matrix of axes is:

```
G = A^T A
```

For any text vector `e`, its decoupled readings on each semantic axis, eliminating axis crosstalk, are:

```
Φ(e) = G^(-1) A^T (e - c)
```

where `c` is the semantic center point, which can be the embedding mean of all anchor texts.

#### 21.3.3 Low-Dimensional Semantic Subspace

The full-dimensional embedding space contains many dimensions unrelated to game state (writing style, sentence structure, rhetorical style, etc.) that interfere with nearest-neighbor retrieval.

Construct a matrix spanned by semantic axes, narrative phase points, and their differences:

```
B = [D_i, S_n - c, S_(n+1) - S_n]
```

Perform SVD or QR decomposition on B, taking the first k directions (typically k = 10~30):

```
Q ∈ R^(d×k)
```

Any text vector projected to the low-dimensional subspace:

```
z = Q^T (e - c)
```

**Space division:**
- Full-dimensional embedding: raw semantic measurement only.
- Original semantic axes A: for interpretation and factual readings.
- Orthogonal computation basis Q: for state evolution and KNN retrieval.
- Gram matrix G: eliminates axis crosstalk.

#### 21.3.4 Warp Function Calibration

The Warp function should not be manually tuned but instead calibrated backward from narrative data.

Given a chronologically ordered set of narrative phase descriptions S_0, S_1, ..., S_{N-1} (covering key transition stages from one extreme state to another), convert them to embedding vectors. The wording of these phase descriptions is freely defined by the game designer according to the world's writing style.

The projection of each phase on the i-th semantic axis is:

```
proj_n_i = Φ_i(S_n)
```

The semantic displacement between adjacent phases is:

```
δ_n_i = proj_(n+1)_i - proj_n_i
```

Normalized semantic density within an axis:

```
ρ_n_i = |δ_n_i| / (Σ_k |δ_k_i| + ε)
```

Meaning: what proportion of the total semantic change along this axis occurs in segment n.

Each axis is assigned a design weight α_i (specified by the game designer to indicate the dimension's importance in the current gameplay). The semantic amplitude generated by an event is:

```
t_i = α_i × ∫[v to v+Δv] ρ_i(x) dx
```

Engineering implementation can use lookup tables with interpolation instead of integration.

A total semantic energy cap T_max can be set per frame to prevent a single dimension from occupying the entire narrative space:

```
Σ_i |t_i| ≤ T_max
```

#### 21.3.5 Semantic Thrust

A complete event thrust consists of both amplitude and direction.

Numerical changes first pass through the Warp function to become semantic amplitude Δt. The event semantic axis d_axis is projected onto the current state's tangent space:

```
d_perp = Normalize(d_raw - (d_raw · p) × p)
```

Complete semantic thrust:

```
ξ = Δt × d_perp
```

Multiple events within the same frame are first combined:

```
v_raw = Σ_i ξ_i
```

Then the combined thrust is projected onto the current tangent space:

```
v_perp = v_raw - (v_raw · p) × p
```

#### 21.3.6 State Update

```
θ = ||v_perp||
d_perp = v_perp / θ
```

Direction update (moving along a spherical arc using the great circle formula):

```
p_new = p × cos(θ) + d_perp × sin(θ)
```

Intensity update separately:

```
r_new = UpdateMagnitude(r, v_raw, state)
```

Final state:

```
z_new = r_new × p_new
```

For large steps, use spherical linear interpolation (SLERP) instead of tangent space approximation:

```
SLERP(p, p_target, t) = sin((1-t)θ)/sin(θ) × p + sin(tθ)/sin(θ) × p_target
```

where `t = semantic_warp(v)` and `p_target = Normalize(p + d_perp)`.

#### 21.3.7 Semantic Momentum

Semantic momentum accumulates the semantic thrust of recent frames, describing "where the state is heading":

```
v_semantic(t) = λ × v_semantic(t-1) + v_raw
```

where 0 < λ < 1 is the decay coefficient.

Since the state moves on the sphere and the tangent space changes, old momentum must be re-projected onto the current tangent space:

```
v_semantic ← v_semantic - (v_semantic · p_current) × p_current
```

Certain special events can actively modify momentum. For example, a designer could define an event that "clears an axis's momentum" or "freezes an axis from participating in state updates." The specific event types and corresponding momentum operations are defined by the game designer in rule configuration.

### 21.4 Rendering Pipeline

#### 21.4.1 Fact Signature Filtering

Before retrieving from the phrase library, perform fact compatibility checks to prevent KNN from selecting phrases that contradict current facts due to overall similarity.

For each candidate phrase `s`, precompute its fact signature offline:

```
Φ(s) = G^(-1) A^T (e(s) - c)
```

Each phrase's signature contains:
- `value_i`: Semantic direction and intensity on that axis.
- `salience_i`: Whether the sentence clearly expresses this axis.
- `confidence_i`: Reliability of the judgment.

When querying, if a candidate phrase clearly contradicts the current state on a key axis, directly discard it.

```
|ψ_i| > τ_state  AND  |φ_i(s)| > τ_phrase  AND  salience_i(s) > τ_salience  AND  φ_i(s) × ψ_i < -ε
```

If satisfied, it's a contradiction; delete the candidate.

**Principle:** Delete clear contradictions; keep unmentioned entries; leave degree deviations for subsequent sorting.

#### 21.4.2 Weighted KNN Phrase Retrieval

Filtered candidates are sorted by weighted distance:

```
d_fact(s) = Σ_i w_i × (φ_i(s) - ψ_i)^2
```

Weights w_i come from the semantic density curve obtained during Warp calibration — critical regions are sensitive, stable regions are tolerant.

Final scoring can comprehensively consider:

```
Score(s) = α×d_fact + β×d_style + γ×d_momentum + δ×d_history
```

- `d_fact`: Fact accuracy (deviation of variable values on each semantic axis).
- `d_style`: Style match (embedding distance between candidate and game writing style).
- `d_momentum`: Fit with current change direction (angle between candidate's semantic direction and v_semantic).
- `d_history`: Cohesion with previous sentence (coherence score between candidate and the last round's output text).

#### 21.4.3 Structured LLM Fallback

If candidates are insufficient after fact filtering (rare state combos, vocabulary gaps), switch to structured LLM generation.

Assemble the current state, change direction, forbidden items, and previous sentence summary into a ContextPacket for the LLM:

```json
{
  "current_state": {
    "variable_a": "Extremely high, but not out of control",
    "variable_b": "Highly stable",
    "variable_c": "Medium-low"
  },
  "change_direction": {
    "variable_a": "Still rising",
    "variable_b": "Forcibly maintained by external constraints"
  },
  "previous_line_summary": "State gradually approaching critical point, but still within controllable range",
  "forbidden_items": [
    "Do not describe [negative extreme state A]",
    "Do not describe [negative extreme state B]",
    "Do not imply [negative extreme state C]"
  ]
}
```

Note: Variable A/B/C, state description phrases, and forbidden item content are all defined by the game designer according to specific gameplay dimensions. The LLM's responsibility is to write the state as natural language within given factual boundaries, without making factual judgments.

### 21.5 Lexicon Management

#### 21.5.1 Precomputation of Phrase Fact Signatures

Each phrase in the lexicon has its fact signature `Φ(s)` computed upon entry, including axial readings, salience, confidence, and coverage range. Runtime queries only read precomputed results.

#### 21.5.2 Miss Buffer & Gap Detection

When the following situations occur, record the current state point in the Miss Buffer:
- Insufficient candidates after fact filtering.
- Top-K candidates don't cover complete axes.
- Candidate fact distances too large.
- Certain state types frequently trigger LLM fallback.

Periodically cluster state points in the Miss Buffer (e.g., DBSCAN) to discover high-frequency gap regions.

#### 21.5.3 Phrase Generation & Validation

Generate new phrases in batches for gap regions, but they must pass validation before entering the library:

1. **Landing validation:** Whether the embedding falls in the target region.
2. **Axis validation:** Whether it covers the axes it should cover.
3. **Reverse parsing:** Whether the original state can be inferred from the phrase.
4. **Conflict detection:** Whether any non-existent facts are written.
5. **Style detection:** Whether it conforms to the set writing style.

#### 21.5.4 Lexicon Closed-Loop Update

```
Uncommon states → Structured generation
High-frequency gaps → Cluster discovery
New phrases → Generate and validate
Common paths → Gradual caching
```

The lexicon is no longer a static text table but a quality cache that continuously optimizes with runtime.

### 21.6 Integration with Kernelsoul Engine

#### 21.6.0 Collaboration with Existing Modules

The semantic rendering engine is an optional enhancement module of the Kernelsoul engine, positioned between the rule engine and AI text generation. Its boundary with existing core logic:

| Module/Logic Unit | Handbook Section | Relationship with Semantic Renderer |
|-------------------|----------------|-------------------------------------|
| State Update Logic | Chapter IX Step 9 (Submit & Bake) | After state.sav write, trigger semantic renderer with changed variable values |
| CharacterStateManager | 4.3 | Character-specific variable (character_state) changes can also trigger semantic rendering |
| Rule Engine | Chapter VI (Rule Syntax) + Chapter VII (DSL Rule System) | Rule execution → State changes → Semantic renderer receives new values. Renderer does not participate in rule evaluation |
| Context Packing | Chapter IX Step 4 | Semantic renderer's output (narrative phrase descriptions) replaces the original "direct numeric textification" result, injected into Prompt's state description section |
| Model Call Logic | Chapter IX Step 5 (AI Generation) | Semantic renderer outputs ContextPacket → appended to final Prompt before LLM call |
| Lorebook Retrieval | Chapter IX Step 3 | Lorebook entries can serve as additional anchors for semantic axes, participating in fact signature filtering |

**Rendering mode switching does not affect the core behavior of the above logic units** — when rendering mode is `direct`, engine behavior is identical to v2.3.

#### 21.6.1 Data Flow

```
GameState variable changes Δv (triggered by state update logic in Chapter IX Step 9)
    → Semantic renderer receives variable changes Δv
    → Warp function + Semantic axes → Semantic thrust ξ
    → State update (p, r, v_semantic)
    → Fact signature filtering + KNN retrieval / Structured generation
    → ContextPacket → Merge into Prompt → Call LLM → AI text output
```

Note: The collaboration between the semantic renderer and the rule engine (Chapters VI/VII) is: Rule engine evaluates and executes actions → State update logic writes state.sav and character_state → Semantic renderer receives changed variable values → Generates narrative description. The semantic renderer is downstream of the rule engine and does not participate in rule evaluation logic.

#### 21.6.2 Axis Mapping Configuration in Character Cards

In Kernelsoul character cards, semantic rendering configuration can be provided through either an independent file or embedded fields.

**Storage location notes:** `semantic_config` can be stored in either of two locations:
1. **Independent file:** `/characters/{characterID}/character_semantic.json` (recommended). Co-located with .dsl and _rules.json, easy for version control and independent editing.
2. **Embedded in character card:** Add a `semantic_config` field at the top level of `character_data.json` (optional). If both the independent file and embedded config exist, the independent file takes precedence.

The GameState defined in Section 3.1 is flat and does not carry semantic rendering configuration. GameState only stores runtime variable values; semantic axis anchor phrases and Warp phase descriptions are design-time configuration and should not be mixed into runtime state.

**Configuration example** (content same for independent file or embedded field):

```json
{
  "variables": {
    "variable_x": {
      "type": "int",
      "range": [-100, 100],
      "default": 0,
      "semantic_config": {
        "axis_positive": "Positive anchor phrase freely defined by designer",
        "axis_negative": "Negative anchor phrase freely defined by designer",
        "design_weight": 0.3,
        "warp_stages": [
          "Narrative stage description 0 freely defined by designer",
          "Narrative stage description 1 freely defined by designer",
          "Narrative stage description 2 freely defined by designer",
          "Narrative stage description 3 freely defined by designer"
        ]
      }
    }
  }
}
```

Note: Content in `axis_positive`, `axis_negative`, and `warp_stages` is entirely filled in freely by the game designer according to the world's writing style. The engine makes no presets. If the character card does not provide `semantic_config`, the engine uses default configuration (linear mapping only, skipping Warp optimization).

#### 21.6.3 Rendering Mode Switching

The engine supports three rendering modes, switchable via the `/render_mode` command:

| Mode | Description |
|------|-------------|
| direct | Values directly textified and injected into Prompt (current default, zero overhead) |
| semantic | Enable semantic rendering pipeline (requires embedding model support) |
| hybrid | Common states use semantic rendering, rare states use direct mode |

### 21.7 Open Research Questions

The following questions are documented but not in the current MVP scope:

1. **Initial state vector calibration:** When a new character is first loaded, how to calibrate its initial position in semantic space from minimal description text? Possible approach: anchor using the character card's `description` and `personality` fields.

2. **Cross-scenario semantic axis reuse:** Different game scenarios (combat, social, exploration, romance, etc.) may require different semantic axis sets. How to design a reusable axis library?

3. **Real-time Warp function updates:** When player behavior significantly deviates from the preset narrative stage trajectory, should the Warp function be updated online? If so, how to ensure update stability?

4. **Cross-language embedding space consistency:** After defining semantic axes in Chinese embedding space, is recalibration needed when switching to an English model? Is cross-lingual semantic axis migration feasible?

5. **Integration with traditional dialogue systems:** In non-narrative-driven chat scenarios, is semantic rendering still meaningful?

---

## Version Change Log

- **v1.0** — Initial handbook: Basic architecture, module division, AI forced JSON contract, three-layer architecture
- **v1.1** — GameState strongly-typed definition, AI response schema, rule engine syntax, PathResolver implementation
- **v1.2** — Dual-track runtime mechanism, draft system (/roll /select /drafts), worldline snapshot extension
- **v1.3** — Graded fault tolerance strategy, memory compression system, session_meta save management, plugin system design specification
- **v1.4** — Design philosophy integrated into Part I (rigid kernel/flexible shell), natural language first protocol, three-stage parser upgrade
- **v1.5** — Quick start guide, manual memory anchors, CharacterCardLoader, UI performance baseline, data sovereignty principles
- **v1.6** — Sidecar initial state file, token budget check and trimming, death/failure state handling, draft saving, lorebook secondary retrieval, greeting initialization
- **v2.0** — Kernelsoul Character Operating System: character_state, character rules, conditional memories, CharacterStateManager, dual-layer rule engine, decision trace, meta-cognition preset
- **v2.1** — Kernelsoul Character Behavior DSL (SLL), DSL Compiler, character_rules_dsl/character_rules_source fields, RuleCompiler three modes
- **v2.3** — Three iron laws, Kernelsoul character file standard, FileService minimal backend API, DSL Compiler Python implementation, CharacterStateManager Python implementation, Context network design specification; memory compression upgraded to dual-layer: 10-round lightweight (200 chars) + 50-round deep (2000 chars); two new compression prompt templates (compression_prompt_light.txt / compression_prompt_deep.txt); working memory injection adjusted to "1 deep summary + 3 lightweight summaries"; full_memory.json entries add compression_type field; new Part V "Ecosystem Expansion Roadmap" (Chapters XVII-XX): Unity/Unreal integration (gRPC API, C# SDK, prefab components), Kernelsoul Character Creation Workbench, Kernelsoul Dialogue SDK (pip install kernelsoul-character-os), Godot/mod/prototype generator
- **v2.3.1** — [New] Three-layer compression (lightweight/deep/epic): compression_prompt_merge.txt & compression_prompt_epic.txt two new templates, layered merge algorithm, context injection rule upgrade. Three-layer compression architecture merged into Chapter XII.
- **v2.4** — New "Semantic Narrative Rendering Engine" (Chapter XXI): including semantic axis, semantic state point, Warp function, semantic momentum core concepts (21.2); Gram matrix decoupled readings, low-dimensional subspace projection, Warp calibration, semantic thrust synthesis, SLERP state update mathematical framework (21.3); fact signature filtering, weighted KNN retrieval, structured LLM fallback complete rendering pipeline (21.4); lexicon closed-loop management (precomputed signatures, Miss Buffer gap detection, phrase generation with five-point validation) (21.5); precise boundary definitions with existing handbook modules (21.6.0) and data flow specification (21.6.1); character card axis mapping configuration file character_semantic.json (21.6.2); /render_mode rendering mode switching command (direct/semantic/hybrid)
