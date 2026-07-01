# Kernelsoul — Modular AI Character Roleplay Engine

> **Character Engine** · Persistent State · Deterministic Rules · Semantic Narrative Rendering · DSL Scripting · 3-Tier Memory · SSE Streaming

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-green)]()

---

> **⚠️ Translation Notice**: The author is not a native English speaker. This English README was machine-translated and may contain awkward phrasing or terminology errors. Corrections and pull requests are warmly welcomed. The [Chinese version](README.md) is the authoritative reference.

---

## What is Kernelsoul?

Kernelsoul (formerly V4 Character OS) is a **pure Python backend engine** for AI-driven character roleplay. Unlike conventional "chat frontends" that simply stitch prompts and call LLM APIs, Kernelsoul inserts a dedicated operating system layer between the character card and the LLM, decomposing character roleplay into five independent subsystems:

Kernelsoul
Narrative Game Engine · Rigid Kernel, Flexible Shell

Overview
Kernelsoul is a narrative game engine driven by pure code for data, AI for text, and passive rendering for the frontend. It is not an AI chat frontend — it is a complete Character Operating System that defines the entire lifecycle of a character: from authoring and compilation to execution and debugging.

Core Philosophy: Natural language is the entrance. JSON is the exit. Code is the eternal master.

Why Kernelsoul
Mainstream AI roleplaying solutions entrust everything to prompts. Creators write a character description and pray the AI doesn't forget the persona. As conversations grow longer, characters drift, and creators can only modify prompts and pray again.

Kernelsoul takes a different path: don't pray, use rules. A character's key behaviors are not improvised by AI on the spot. They are pre-defined by creators using DSL, deterministically compiled by a compiler, and precisely executed by a rule engine. AI still writes beautiful dialogue, but the logic of "what a character says and how they react under what circumstances" is decided by code, not probability.

This is the essential leap from "training an animal" to "operating a machine."

Core Features
Rigid Kernel: Deterministic Execution
Strongly-Typed GameState: All game states — HP, inventory, affinity — are managed by pure code. AI can only suggest changes through a JSON contract; code makes the final ruling.

Rule Engine: Dual-layer architecture supporting both global rules and character-specific rules. Conditions → Actions, executed with precision.

Evolution Trigger: Automatically triggers phase mutations when states reach thresholds, with zero AI involvement.

Three-Tier Fault Tolerance: Graceful degradation when AI output is abnormal. Never crashes.

Flexible Shell: Natural Language First
Natural Language First Protocol: AI focuses on writing great stories. State-change JSON is an optional enhancement, not a mandatory shackle.

Prompt Compilation Layer: Vague human creative descriptions → AI compiles into structured rules → deterministic execution.

Meta-Cognition "Superego" System: Characters carry a director's awareness, self-monitoring persona consistency throughout long conversations.

DSL: Scenario Logic Language (SLL)
Human-Readable: WHEN player mentions "king" IF mood < 0 THEN SET current_tone = "sarcastic"

Deterministic Compilation: Hand-written recursive descent parser. Same input always produces the same JSON output.

Bidirectional Translation: DSL ↔ JSON ↔ Natural Language. A complete authoring pipeline.

Three Modes: Auto-compile from natural language / DSL-assisted authoring / Expert hand-written DSL

Three-Tier Memory Compression
Light Compression: Every 10 rounds, generates ~200-word summary. Preserves recent details.

Deep Compression: Every 50 rounds, generates ~2500-word summary. Preserves mid-range narrative arcs.

Epic Compression: Every 200 rounds, generates ~5000-word summary. Preserves global story脉络.

Context Injection Priority: Manual memory anchors > Epic summaries > Deep summaries > Light summaries > Recent transcripts

Multi-Branch Narrative
Draft Mechanism: Each round's AI response enters a pending state. Re-roll (/roll) multiple times to generate parallel versions.

Select & Commit: Choose the best version from multiple drafts (/select). Unselected drafts can be saved.

Multi-Timeline Snapshots: Future support for回溯 to any branch point and restarting from a parallel version.

Semantic Narrative Rendering Engine (v2.4 new)
Semantic Axes: Define positive/negative anchor phrases for each state dimension, establishing semantic directions in embedding space.

Gram Matrix Decoupling: Eliminates crosstalk between semantic axes for precise multi-dimensional semantic readings.

Warp Function: Nonlinear mapping from numeric changes to semantic magnitude — sensitive in critical zones, tolerant in stable zones.

Fact-Signature Filtering: Eliminates candidate phrases that contradict current facts before KNN retrieval.

Lexicon Closed Loop: Miss Buffer detects gaps → batch generation → five-check validation →入库 → continuously optimizing quality cache.

Plugin System & Ecosystem
Zero-Friction Install: Drop a folder in, it works. Hot-reloading supported.

Permission Sandbox: Six permission levels. High-risk operations require user confirmation.

Lifecycle Hooks: Ten hooks covering the engine's complete lifecycle.

Ecosystem Roadmap: Unity/Unreal integration (gRPC SDK), pip package (pip install kernelsoul), Character Authoring Workbench, modding tools.

Data Sovereignty
Fully Local: All data stored on user's device in open formats (JSON/TXT).

No Forced Connectivity: Online APIs are optional. Local models can fully替代.

One-Click Import/Export: Package complete sessions as ZIP. Direct compatibility with SillyTavern character cards.



- **State Layer** — Strongly-typed GameState with AI-writable whitelist variables
- **Rule Layer** — SLL (Kernelsoul Logic Language), a deterministic DSL compiled and executed at every turn
- **Semantic Layer** — Semantic axes, Warp mapping, Gram matrices, SLERP momentum, KNN phrase retrieval
- **Memory Layer** — 3-tier hierarchical compression: Light (10 turns) → Deep (50 turns) → Epic (200 turns)
- **Ecosystem Layer** — Sandboxed plugin system, gRPC API, SillyTavern plugin integration

Every subsystem can be tested, replaced, and extended independently.

Unable to write the UI due to capability limitations
---

## Directory Structure

```
Kernelsoul/
├── src/kernelsoul/              # Engine source code
│   ├── core_engine.py           # Main engine loop, module assembly
│   ├── api_server.py            # FastAPI REST server
│   ├── game_state.py            # Strongly-typed GameState
│   ├── state_manager.py         # State persistence manager
│   ├── memory_manager.py        # 3-tier hierarchical memory compression
│   ├── parser_engine.py         # AI response parserural language)
├── dsl_compiler.py              # SLL recursive-descent parser
├── rule_compiler.py             # AI-assisted rule compiler
├── worldbook_retriever.py       # 3D lorebook retrieval (keyword/regex/subkey)
├── evolution_trigger.py         # Rule evolution system
├── character_card_loader.py     # V1-V4 character card loader
├── plugin_manager.py            # Sandboxed plugin manager
├── ai_bridge.py                 # API bridge (DeepSeek / OpenAI compatible)
├── context.py                   # Context assembly
├── context_wrappers.py          # Context wrappers
├── session_meta.py              # Session metadata
├── path_resolver.py             # 41 path resolution methods
├── draft_manager.py             # Draft & version management
│
├── semantic_engine.py           # Semantic engine (axes/Warp/momentum/Gram) — v2.4
├── semantic_renderer.py         # Semantic renderer (3 modes) — v2.4
├── phrase_library.py            # KNN phrase corpus — v2.4
│
├── configs/
│   ├── system.json              # API config
│   ├── system.json.example      # Config template
│   ├── rules.json               # Global rules
│   ├── compression_prompt_light.txt
│   ├── compression_prompt_deep.txt
│   ├── compression_prompt_epic.txt
│   ├── compression_prompt_merge.txt
│   ├── fallback_prompt.txt
│   ├── rule_compiler_prompt.txt
│   └── presets/
│       ├── meta_cognition_v4.txt
│       └── preset_index.json
│
├── characters/
│   ├── night_hunter/            # Night City Hunter: Frost (full example)
│   ├── cyber_test/              # CyberSprite-7 (lightweight example)
│   └── demon_test/              # Fallen Princess Lucy (lightweight example)
│
├── plugins/
│   ├── example_auto_save/
│   ├── example_broken/
│   └── example_stats_tracker/
│
├── saves/                       # Runtime saves
├── assets/                      # Character assets
├── tests/e2e/                   # End-to-end test records (50-turn dialogs)
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md
```

---

## Quick Start

### Requirements

- Python 3.10+
- A DeepSeek or OpenAI-compatible API key

### 1. Install Dependencies

```bash
cd in-dev
pip install -r requirements.txt
```

Dependencies: `openai>=1.0.0`, `httpx>=0.27.0`, `fastapi`+`uvicorn`, `numpy`

### 2. Configure API Key

```bash
cp configs/system.json.example configs/system.json
```

Edit `configs/system.json`:

```json
{
    "api_type": "deepseek",
    "api_key": "sk-your-api-key",
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "max_tokens": 4096,
    "temperature": 0.8,
    "max_context_tokens": 28672
}
```

> `system.json` is excluded by `.gitignore`.

### 3. Launch

```bash
# API mode
python api_server.py
# → Kernelsoul API running at http://127.0.0.1:8000

# CLI mode
python core_engine.py
```

### 4. Run Tests

```bash
python -m pytest test_parser.py test_phase1.py test_memory.py test_dsl_compiler.py test_rule_compiler.py test_evolution_trigger.py test_character_loader.py test_worldbook.py test_plugin.py test_saved_drafts.py test_semantic.py -v
```

---

## Architecture

```
User Input → Plugin Hooks → Worldbook Retrieval → Memory Compression → Context Assembly → AI Bridge → LLM
                                                                                                            ↓
AI Response → Parser ← Semantic Renderer(direct/semantic/hybrid) → State Update → Rule Check → Evolution Trigger
                  ↓
            State Persist → Save
```

### Five Layers

| Layer | Key Modules | Responsibility |
|-------|-------------|----------------|
| Engine Core | `CoreEngine` · `GameState` · `StateManager` | Main loop, state management, bootstrap |
| Character & Rules | `CharacterCardLoader` · `DSLCompiler` · `RuleCompiler` | Card loading, DSL parsing, rule execution |
| Semantic Pipeline | `SemanticEngine` · `SemanticRenderer` · `PhraseLibrary` | Vector projection, Warp, 3-mode render, KNN |
| Memory & Context | `MemoryManager` · `Context` · `PathResolver` | 3-tier compression, summary merge, context assembly |
| Ecosystem | `PluginManager` · `AIBridge` · `api_server` · `WorldBookRetriever` | Hooks, API bridge, REST endpoints, lorebook |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/characters` | GET | List characters |
| `/api/switch` | POST | Switch/load character |
| `/api/state` | GET | Current game state |
| `/api/chat/stream` | POST | SSE streaming dialog |
| `/api/sessions` | GET | List sessions |
| `/api/session/switch` | POST | Switch session |
| `/api/session/new` | POST | Create new session |
| `/api/history` | GET | Chat history |
| `/api/render_mode` | GET | Query render mode (v2.4) |
| `/api/render_mode` | POST | Switch render mode (v2.4) |

### Render Modes (v2.4)

| Mode | Behavior | Token Overhead |
|------|----------|----------------|
| `direct` | Raw numeric state (v2.3 compatible) | Baseline |
| `semantic` | Full semantic narrative descriptions | +33% |
| `hybrid` | Semantic for high-weight dims, numeric for others | +16% |

---

## DSL Rule Engine (SLL Language)

```
WHEN hp < 30：
    IF has_potion：
        USE potion
        THEN "She uncorks a potion and drinks it in one gulp"
        BECAUSE "Character uses healing items when in danger"
    ELSE：
        THEN "Her teeth clench as blood seeps through her fingers"
        BECAUSE "Without resources, the character toughs it out"
```

Rules are compiled by a recursive-descent parser into executable decision trees, checked automatically every turn.

---

## Semantic Narrative Engine (v2.4)

A brand-new subsystem introduced in Chapter 21 that maps GameState numeric values into narrative descriptions:

**Math Framework:**
- Semantic axis: Dᵢ = embed(pos_anchor) − embed(neg_anchor)
- Warp function: non-linear mapping from value changes to semantic deltas
- Gram matrix: G = AᵀA for axis decoupling
- Subspace SVD reduction (k=20)
- SLERP spherical linear interpolation for state updates

**Rendering Pipeline:**
- Fact label precomputation with conflict detection
- KNN multi-factor ranking retrieval (fact · style · momentum · dedup)
- LLM fallback generation → admission audit (5 checks)
- Miss Buffer cluster analysis for corpus gap detection

> **⚠️ Note:** Vector-space projection requires an external embedding model (OpenAI text-embedding-3-small or local BGE-Large-ZH). DeepSeek currently does not support embeddings endpoints. When no embedding is available, semantic/hybrid modes fall back to state-delta text prompts (~30% of designed capability).

---

## Plugin System

```
plugins/my_plugin/
├── manifest.json    # {"id":"my_plugin","name":"...","hooks":[...],"permissions":[...]}
└── __init__.py      # Hook function implementations
```

**Supported hooks:** `on_user_input`, `on_ai_response`, `filter`, `on_engine_init`, `on_before_turn`, `on_after_turn`

---

## Test Status

| Test File | Cases | Status |
|-----------|-------|--------|
| `test_phase1.py` | 48 | ✅ |
| `test_memory.py` | 27 | ✅ |
| `test_parser.py` | 41 | ✅ |
| `test_dsl_compiler.py` | 11 | ✅ |
| `test_rule_compiler.py` | 10 | ✅ |
| `test_evolution_trigger.py` | | ✅ |
| `test_character_loader.py` | | ✅ |
| `test_worldbook.py` | | ✅ |
| `test_plugin.py` | | ✅ |
| `test_saved_drafts.py` | 12 | ✅ |
| `test_semantic.py` | 17 | ✅ |
| **Total** | **181+** | **All passed** |

---

## Version History

| Version | Milestone |
|---------|-----------|
| v1.0 | Base architecture, AI JSON protocol |
| v1.1-1.4 | GameState typing, parser, memory compression, fault tolerance |
| v1.5-1.6 | Character card loader, worldbook retrieval, drafts |
| v2.0 | Kernelsoul system, dual rules engine, decision traceability |
| v2.1 | SLL language, recursive-descent parser |
| v2.3 | Engineering production, Context specification |
| v2.3.1 | 3-tier memory compression (Light/Deep/Epic) |
| **v2.4** | **Semantic rendering engine** |

---

## License

MIT © Kernelsoul Contributors
