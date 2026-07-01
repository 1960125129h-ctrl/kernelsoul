# Changelog

All notable changes to Kernelsoul (formerly V4 Character OS, formerly Soulscript) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.4.0] — 2026-07-01

### Added

- **Semantic Rendering Engine** (Chapter 21)
  - `SemanticEngine` — Semantic axes via embedding projection, Warp functions for nonlinear mapping, Gram matrix for axis decorrelation, SVD subspace reduction (k=20), SLERP momentum interpolation
  - `SemanticRenderer` — Three rendering modes: `direct` (numeric, v2.3 compatible), `semantic` (fully narrated, +33% tokens), `hybrid` (high-weight axes semantic, low-weight numeric, +16% tokens)
  - `PhraseLibrary` — KNN phrase retrieval with multi-factor ranking (factual · style · momentum · dedup), LLM fallback synthesis, miss buffer clustering
  - Admission audit: 5 checks, LLM regeneration on failure
- **API endpoints**: `GET /api/render_mode`, `POST /api/render_mode`
- **E2E test data**: 50-round test session with full log

### Changed

- Project renamed: `V4 Character OS` → `Soulscript` → `Kernelsoul` (GitHub-ready name)
- All source file docstrings, module headers, and LICENSE updated to `Kernelsoul`
- Documentation: handbook v2.4, 7 HTML reports, README (CN + EN)
- README restructured with directory tree, architecture diagram, API table, and test status
- Dependencies bumped: `openai>=1.0.0`, `httpx>=0.27.0`

### Fixed

- Character card `_load_v4_folder` / `_upgrade_to_v4` method names preserved for backward compatibility after rename
- Zero residual scan: no outdated project name references in any directory

### Legacy

- `V4 Character OS` (v1.0–v2.3.1) archives preserved in `D:\V4-Character-OS\` and `D:\V4-Character-OS-开源版\`

---

## [2.3.1] — 2026-06-30

### Added

- **Three-tier memory compression** (light: 10 turns / deep: 50 turns / epic: 200 turns)
- `system.json.example` — configuration template without API keys

### Changed

- Compression prompts separated into `compression_prompt_light.txt`, `compression_prompt_deep.txt`, `compression_prompt_epic.txt`
- `configs/system.json` added to `.gitignore`

---

## [2.3.0] — 2026-06-29

### Added

- **SLL (Scripting Language Layer)** — declarative DSL for character behavior
- `DSLCompiler` — recursive descent parser compiling SLL into executable decision trees
- **Configuration/preset system** — `configs/presets/` with `meta_cognition_v4.txt` and `preset_index.json`
- `PathResolver` — 41 path methods for repository-wide file access
- `ContextWrappers` — context assembly utilities

### Changed

- `CoreEngine` refactored to orchestrate all subsystems via the new Context system
- Preset management moved from hardcoded paths to `preset_index.json`

### Fixed

- JSON parsing edge cases in `ParserEngine`
- Round count reset on character switch

---

## [2.1.0] — 2026-06-20

### Added

- **Dual-layer rule engine** — deterministic rules + AI-assisted compilation
- `RuleCompiler` — AI-prompted rule generation and validation
- `EvolutionTrigger` — automatic rule evolution from user corrections
- Decision trace logging for rule execution

---

## [2.0.0] — 2026-06-15

### Added

- `CharacterCardLoader` — V1–V4 character card format support
- `WorldBookRetriever` — keyword-based lorebook retrieval
- `SessionMeta` — session metadata management
- `DraftManager` — draft and version management for saves
- `PluginManager` — sandbox plugin system with 6 hook points
- `AIBridge` — unified API bridge (DeepSeek / OpenAI)
- `ApiServer` — FastAPI REST server with SSE streaming
- SSE streaming dialogue endpoint: `POST /api/chat/stream`
- Plugin hooks: `on_user_input`, `on_ai_response`, `on_engine_init`, `on_before_turn`, `on_after_turn`, `filter`

---

## [1.6.0] — 2026-06-10

### Added

- Character card loading (`chara_card_v4` format)
- Worldbook keyword retrieval
- Session save/load with draft management

---

## [1.5.0] — 2026-06-05

### Added

- GameState strong typing with whitelist variable control
- State persistence (`StateManager`)
- Parser engine for AI response extraction (JSON block → bare JSON → natural language fallback)
- Tiered error recovery (3-level fallback)

---

## [1.4.0] — 2026-06-01

### Added

- Memory compression system
- Summary-based context management

---

## [1.1.0–1.3.0] — 2026-05

### Added

- AI JSON protocol refinement
- GameState iteration
- Parser engine development
- Memory compression exploration

---

## [1.0.0] — 2026-04

### Added

- Initial project architecture
- Basic AI dialogue loop with JSON protocol
- Foundation for state management and response parsing

---

*For earlier development history, see [NAME_CHANGE_LOG.md](docs/NAME_CHANGE_LOG.md).*
