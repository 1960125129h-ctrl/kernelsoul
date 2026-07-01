# 贡献指南 / Contributing Guide

欢迎为 Kernelsoul 项目做出贡献！以下指南帮助你快速上手。  
Welcome to Kernelsoul! We appreciate your interest in contributing.

---

## 目录 / Table of Contents

- [行为准则 / Code of Conduct](#行为准则--code-of-conduct)
- [如何贡献 / How to Contribute](#如何贡献--how-to-contribute)
- [开发环境 / Development Setup](#开发环境--development-setup)
- [代码风格 / Code Style](#代码风格--code-style)
- [测试 / Testing](#测试--testing)
- [提交 PR / Submitting a PR](#提交-pr--submitting-a-pr)
- [命名规范 / Naming Conventions](#命名规范--naming-conventions)
- [项目架构 / Architecture Overview](#项目架构--architecture-overview)

---

## 行为准则 / Code of Conduct

**中文：** 本项目遵循开放、包容的原则。我们不允许任何形式的骚扰、歧视或不尊重行为。请保持建设性和友善。

**English:** This project is open and inclusive. Harassment, discrimination, or disrespectful behavior of any kind will not be tolerated. Be constructive and be kind.

---

## 如何贡献 / How to Contribute

### 中文

1. **报告 Bug** — 在 GitHub Issues 提交，包含：
   - Python 版本、操作系统
   - 复现步骤
   - 期望行为 vs 实际行为
   - 相关日志或错误输出
2. **提出功能请求** — 先搜索现有 Issue 避免重复，清晰描述使用场景和期望
3. **提交代码** — Fork 仓库 → 创建分支 → 提交修改 → 发起 Pull Request
4. **改进文档** — 修复错别字、补充遗漏、翻译不准确、增加示例

### English

1. **Report Bugs** — Open a GitHub Issue with:
   - Python version, OS
   - Reproduction steps
   - Expected vs actual behavior
   - Relevant logs or error output
2. **Feature Requests** — Search existing issues first. Clearly describe the use case and expected outcome.
3. **Submit Code** — Fork → Branch → Commit → Pull Request
4. **Improve Docs** — Fix typos, fill gaps, correct translations, add examples.

---

## 开发环境 / Development Setup

### 中文

```bash
# 克隆仓库
git clone https://github.com/1960125129h-ctrl/Kernelsoul.git
cd Kernelsoul

# 安装依赖
pip install -r requirements.txt
# 或: pip install openai httpx fastapi uvicorn numpy

# 配置 API Key
cp configs/system.json.example configs/system.json
# 编辑 system.json 填入你的 API Key

# 运行测试（确保修改不破坏已有功能）
python -m pytest tests/ -v
```

### English

```bash
# Clone the repo
git clone https://github.com/1960125129h-ctrl/Kernelsoul.git
cd Kernelsoul

# Install dependencies
pip install -r requirements.txt
# Or: pip install openai httpx fastapi uvicorn numpy

# Configure API key
cp configs/system.json.example configs/system.json
# Edit system.json with your API key

# Run tests to verify nothing is broken
python -m pytest tests/ -v
```

---

## 代码风格 / Code Style

### 中文

- **Python**: 遵循 PEP 8，行宽 100 字符
- **f-string**: 外双引号、内单引号（如 `f"Value: {item['name']}"`）
- **编码**: 所有 `.py` 文件使用 UTF-8 without BOM
- **类型提示**: 关键函数请加类型注解
- **导入顺序**: 标准库 → 第三方库 → 本地模块，分组用空行隔开
- **注释**: 公共 API 和核心逻辑用英文写 docstring；中文注释用于复杂逻辑补充说明
- **命名**: 类用 `PascalCase`，函数/变量用 `snake_case`，常量用 `UPPER_SNAKE_CASE`

### English

- **Python**: PEP 8 compliant, 100-char line width
- **f-strings**: Outer double quotes, inner single quotes (e.g., `f"Value: {item['name']}"`)
- **Encoding**: All `.py` files use UTF-8 without BOM
- **Type hints**: Add type annotations to critical functions
- **Import order**: Standard library → Third-party → Local modules, grouped with blank lines
- **Comments**: Public APIs and core logic use English docstrings; Chinese comments for complex logic clarifications
- **Naming**: `PascalCase` for classes, `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants

---

## 测试 / Testing

### 中文

所有新功能或 Bug 修复**必须包含测试**。测试使用 `pytest` 框架。

```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_memory.py -v

# 运行特定测试用例
python -m pytest tests/test_memory.py::TestMemoryManager::test_light_compress_trigger_at_10 -v
```

**测试原则：**
- 单模块测试放在 `tests/` 目录，以 `test_` 开头
- 同层测试不需要 mock 真实 API 调用
- 测试数据文件放在 `test_data/` 目录
- 端到端测试放在 `tests/e2e/` 目录

### English

All new features or bug fixes **must include tests**. We use `pytest`.

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_memory.py -v

# Run a specific test case
python -m pytest tests/test_memory.py::TestMemoryManager::test_light_compress_trigger_at_10 -v
```

**Testing principles:**
- Unit tests go in `tests/`, prefixed with `test_`
- Unit tests should not mock real API calls
- Test data goes in `test_data/`
- End-to-end tests go in `tests/e2e/`

---

## 提交 PR / Submitting a PR

### 中文

1. **Fork 本仓库**，在 fork 中创建功能分支：`feature/my-feature` 或 `fix/issue-123`
2. **保持小提交**，每次提交只做一个逻辑变更
3. **写清晰的 commit message**，参考以下格式：
   ```
   feat: add semantic rendering hybrid mode
   fix: correct memory compression threshold
   docs: update API endpoint documentation
   refactor: simplify DSL compiler parse loop
   test: add evolution trigger edge cases
   ```
4. **发起 PR 前**：
   - 运行全部测试，确保通过
   - 确保你的分支基于最新的 `main`
5. **PR 描述包含**：
   - 变更摘要
   - 关联 Issue 编号（如 `Closes #123`）
   - 测试步骤（如果适用）

### English

1. **Fork the repo**, create a feature branch in your fork: `feature/my-feature` or `fix/issue-123`
2. **Keep commits small** — one logical change per commit
3. **Write clear commit messages** following this convention:
   ```
   feat: add semantic rendering hybrid mode
   fix: correct memory compression threshold
   docs: update API endpoint documentation
   refactor: simplify DSL compiler parse loop
   test: add evolution trigger edge cases
   ```
4. **Before opening a PR**:
   - Run all tests — they must pass
   - Rebase your branch onto latest `main`
5. **PR description should include**:
   - Summary of changes
   - Related issue number (e.g., `Closes #123`)
   - Test steps (if applicable)

---

## 命名规范 / Naming Conventions

### 中文

Kernelsoul 项目经历过改名，请理解以下命名规则：

| 应使用 | 不应使用 |
|--------|---------|
| `Kernelsoul`（项目名） | `Soulscript`, `V4 Character OS` |
| `v4`（版本标识，小写） | `V4`（大写作为项目名） |
| `chara_card_v4` | `chara_card_soulscript` |
| `meta_cognition_v4` | `meta_cognition_kernelsoul` |

**规则：** 大写 `V4` 作为项目名已不再使用；小写 `v4` 版本标识保留不变。

### English

Kernelsoul was renamed from its previous names. Please follow these conventions:

| Use | Don't Use |
|-----|-----------|
| `Kernelsoul` (project name) | `Soulscript`, `V4 Character OS` |
| `v4` (version identifier, lowercase) | `V4` (uppercase as project name) |
| `chara_card_v4` | `chara_card_soulscript` |
| `meta_cognition_v4` | `meta_cognition_kernelsoul` |

**Rule:** Uppercase `V4` as a project name is deprecated. Lowercase `v4` version identifiers are preserved.

---

## 项目架构 / Architecture Overview

### 中文

```
src/kernelsoul/
├── core_engine.py          # 引擎主循环，总装所有模块
├── api_server.py           # FastAPI REST 服务 + SSE 流式对话
├── game_state.py           # 强类型 GameState
├── state_manager.py        # 状态持久化
├── memory_manager.py       # 三层记忆压缩（轻/深/史诗）
├── parser_engine.py        # AI 响应解析（JSON 块 → 裸 JSON → 自然语言）
├── dsl_compiler.py         # SLL 递归下降解析器
├── rule_compiler.py        # AI 协作规则编译器
├── evolution_trigger.py    # 规则进化触发器
├── worldbook_retriever.py  # 世界书关键词检索
├── character_card_loader.py# V1-V4 角色卡加载
├── plugin_manager.py       # 沙箱插件系统
├── ai_bridge.py            # LLM API 桥接
├── context.py              # 上下文组装
├── session_meta.py         # 会话元数据
├── path_resolver.py        # 路径解析
├── draft_manager.py        # 草稿管理
├── semantic_engine.py      # 语义引擎（v2.4）
├── semantic_renderer.py    # 语义渲染器（v2.4）
└── phrase_library.py       # KNN 短语库（v2.4）
```

### English

```
src/kernelsoul/
├── core_engine.py          # Engine main loop, orchestration
├── api_server.py           # FastAPI REST server + SSE streaming
├── game_state.py           # Strongly-typed GameState
├── state_manager.py        # State persistence
├── memory_manager.py       # 3-tier memory compression (light/deep/epic)
├── parser_engine.py        # AI response parser (JSON block → bare JSON → NL)
├── dsl_compiler.py         # SLL recursive descent parser
├── rule_compiler.py        # AI-assisted rule compiler
├── evolution_trigger.py    # Rule evolution trigger
├── worldbook_retriever.py  # Worldbook keyword retrieval
├── character_card_loader.py# V1-V4 character card loader
├── plugin_manager.py       # Sandbox plugin system
├── ai_bridge.py            # LLM API bridge
├── context.py              # Context assembly
├── session_meta.py         # Session metadata
├── path_resolver.py        # Path resolution
├── draft_manager.py        # Draft management
├── semantic_engine.py      # Semantic engine (v2.4)
├── semantic_renderer.py    # Semantic renderer (v2.4)
└── phrase_library.py       # KNN phrase library (v2.4)
```

---

*Thank you for contributing to Kernelsoul! / 感谢你对 Kernelsoul 的贡献！*
