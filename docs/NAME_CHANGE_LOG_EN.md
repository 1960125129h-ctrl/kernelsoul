# Name Change Log

## 2026-07-01

### Naming History

| Phase | Name | Notes |
|---|---|---|
| v1.0 – v2.3.1 | **V4 Character OS** | Original project name |
| 2026-07-01 (early) | **Soulscript** | First rename attempt; 114 conflicts on GitHub |
| 2026-07-01 (final) | **Kernelsoul** | Current name; zero conflicts on GitHub |

### Why Kernelsoul?

`Soulscript` had 114 matching repositories on GitHub. The most concerning collision was `DrTHunter/SoulScript-Engine` (5 stars) — a project in the same space (AI identity/character engine). To avoid confusion and potential trademark issues, the name was abandoned.

`Kernelsoul` returned **0 results** on GitHub search, making it entirely unique.

### Scope of Rename

All occurrences of the project name were updated across these directories:

**D:\\Kernelsoul\\** — GitHub release repository (renamed from D:\\Soulscript\\)
- `README.md` / `README_EN.md` — All project name references (historical "formerly V4 Character OS" notes preserved)
- `LICENSE` — `Copyright (c) 2026 Kernelsoul Contributors`
- `src/kernelsoul/` — 21 Python modules (docstring headers, API title, health check response)
- `tests/` — Test file docstrings
- `docs/` — 7 HTML reports (filenames and content)
- `.gitignore`, configuration files, examples, test logs

**D:\\V4-Character-OS-开源版\\** — Open-source distribution archive
- Top-level README, HTML reports, LICENSE
- `in-dev v2.3.1/` and `in-dev v2.4/` historical source snapshots

**D:\\V4-Character-OS\\** — Active development repository
- `in-dev/` — 24 Python source files (docstrings/comments)
- Handbook directory renamed to `Kernelsoul-角色引擎开发手册\\`
- Configuration files, plugin manifests, preset index

### Preserved Identifiers

- Root dev directory `D:\\V4-Character-OS\\` — kept unchanged to maintain all import paths and references
- Lowercase `v4` format identifiers: `chara_card_v4`, `_load_v4_folder`, `meta_cognition_v4`, etc.
- Model name `deepseek-v4-flash`
- Historical "(formerly V4 Character OS)" notes in READMEs

### Regression Verification

All tests pass after the rename:

- **181 unit tests** across 9 modules — All passed
- **API server** starts normally — `/api/health` returns `{"status":"ok","engine":"Kernelsoul"}`
- **Zero residual scan** — No remaining "Soulscript" / outdated project name references in any of the three repositories
