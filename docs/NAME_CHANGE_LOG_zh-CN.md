# 改名记录 / Name Change Log

## 2026-07-01

### 更名历史

| 阶段 | 项目名 | 用途 |
|---|---|---|
| v1.0 – v2.3.1 | V4 Character OS | 原始项目名 |
| 2026-07-01 | **Soulscript**（灵魂脚本） | 第一次更名（发现 GitHub 重名 114 个仓库） |
| 2026-07-01 终版 | **Kernelsoul**（灵魂内核） | 当前项目名（GitHub 0 冲突） |

### 改名原因

`Soulscript` 在 GitHub 上存在 114 个同名仓库，其中最严重的是 `DrTHunter/SoulScript-Engine`（5 stars，同一赛道：AI identity 引擎），为避免混淆决定放弃该名称。

`Kernelsoul` 在 GitHub 搜索结果中为 0 个仓库，完全无冲突。

### 更名范围

本次更名覆盖以下目录和文件：

- **D:\Kernelsoul\** — GitHub 发布版仓库（原名 D:\Soulscript\）
  - `README.md` / `README_EN.md` — 项目说明（保留"原名 V4 Character OS"历史注释）
  - `LICENSE` — Copyright (c) 2026 Kernelsoul Contributors
  - `src/kernelsoul/` — 21 个 Python 模块（模块头部 docstring、API 标题、健康检查响应）
  - `tests/` — 测试文件头部注释
  - `docs/` — 7 篇 HTML 报告（文件名和内容）
  - `.gitignore`、配置、示例、日志
  - 所有文件中 "Soulscript" → "Kernelsoul"

- **D:\V4-Character-OS-开源版\** — 开源版归档
  - 顶层 README、HTML 报告、LICENSE
  - `in-dev v2.3.1/` 和 `in-dev v2.4/` 历史存档源码

- **D:\V4-Character-OS\** — 开发主仓库
  - `in-dev/` 活跃源码 24 个 `.py` 文件（docstring/注释）
  - `Kernelsoul-角色引擎开发手册/` 目录名和手册内容
  - 配置文件、插件 manifest、preset 索引

### 保留不变的内容

- 根目录名 `D:\V4-Character-OS\` — 保留所有引用依赖
- 小写 `v4` 格式版本标识：`chara_card_v4`、`_load_v4_folder`、`meta_cognition_v4` 等
- 模型名 `deepseek-v4-flash`
- README 中的 "(formerly V4 Character OS)" 历史注释

### 回归验证

- 181 项单模块测试全部通过（9 个测试模块）
- API 服务器启动正常，`/api/health` 返回 `{"status":"ok","engine":"Kernelsoul"}`
- 零残留扫描通过（三个目录无 "Soulscript" / "soulscript" / 过期项目名引用）
