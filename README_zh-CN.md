# Kernelsoul — 模块化 AI 角色扮演引擎

> **角色引擎** · 状态持久化 · 确定性规则 · 语义叙事渲染 · DSL 剧本语言 · 三层记忆 · SSE 流式对话

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-green)]()

---

## 概述

Kernelsoul（原名 V4 Character OS）是一个纯 Python 的 AI 角色扮演后端引擎。
它不是又一个"前端酒馆"——而是一个位于 LLM 下游的角色操作系统，将角色扮演拆解为多个独立子系统：

Kernelsoul 是一个纯代码驱动数据、AI 驱动文本、前端被动渲染的叙事游戏引擎。它不是一个 AI 聊天前端，而是一套完整的角色操作系统——定义了角色从创作、编译到运行、调试的完整生命周期。

核心哲学：自然语言是入口，JSON 是出口，代码是永远的主人。

为什么是 Kernelsoul
当前主流的 AI 角色扮演方案将一切托付给 Prompt。创作者写一段角色描述，祈祷 AI 不要忘记人设。当对话变长，角色开始漂移，创作者只能修改 Prompt 再次祈祷。

Kernelsoul 选择了另一条路：不靠祈祷，靠规则。角色的关键行为不由 AI 临时即兴决定，而是由创作者用 DSL 预先定义、由编译器确定性编译、由规则引擎精确执行。AI 仍然负责写出优美的对话，但角色“在什么情况下说什么话、做出什么反应”的逻辑，是代码决定的，不是概率决定的。

这是从“调教动物”到“操作机器”的本质跨越。

核心特性
刚性内核：确定性执行
强类型 GameState：HP、背包、好感度等所有游戏状态由纯代码管理，AI 只能通过 JSON 契约建议修改，代码做最终裁决

规则引擎：支持全局规则和角色专属规则的双层架构，条件→动作精确执行

进化触发器：状态达到阈值时自动触发阶段变异，无需 AI 参与

三级容错：AI 输出异常时自动降级，绝不崩溃

柔性外壳：自然语言优先
自然语言优先协议：AI 专注于写出好故事，状态变更 JSON 是可选的附加增强，而非强制枷锁

Prompt 编译层：人类模糊的创意描述 → AI 编译为结构化规则 → 确定性执行

元认知“超我”系统：角色自带导演意识，长对话中自我监控人设一致性

DSL 剧本逻辑语言（SLL）
人类可读：WHEN 玩家提及"国王" IF mood < 0 THEN SET current_tone = "讽刺"

确定性编译：手写递归下降解析器，相同输入永远产生相同 JSON 输出

双向可译：DSL ↔ JSON ↔ 自然语言，完整创作链路

三种模式：自然语言自动编译 / DSL 辅助创作 / 专家手写 DSL

双层（可扩展至三层）记忆压缩
轻量压缩：每 10 轮生成约 200 字摘要，保留近期细节

深度压缩：每 50 轮生成约 2500 字摘要，保留中程叙事弧

史诗压缩：每 200 轮生成约 5000 字摘要，保留全局故事脉络

上下文注入：手动记忆锚点 > 史诗摘要 > 深度摘要 > 轻量摘要 > 最近原文

多分支叙事
草稿机制：每轮 AI 回复进入待确认态，可多次重投（/roll）生成平行版本

选择提交：从多个草稿中选择最佳版本确认（/select），未选择的草稿可收藏

多世界线快照：未来可回溯任意分支点，从平行版本重新开始

语义叙事渲染引擎（v2.4 新增）
语义轴：为每个状态维度定义正负锚点，在嵌入空间中建立语义方向

Gram 矩阵解耦：消除语义轴间的串扰，精确读取多维状态的语义分量

Warp 函数：数值变化→语义幅度的非线性映射，临界区敏感、平稳区宽容

事实签名过滤：KNN 检索前剔除与当前事实矛盾的候选短语

词库闭环：Miss Buffer 检测缺口 → 批量生成 → 五项校验入库 → 质量缓存持续优化

插件系统与生态
极简安装：放入文件夹即启用，支持热重载

权限沙箱：六种权限级别，高危操作需用户确认

生命周期钩子：十个钩子覆盖引擎完整生命周期

生态扩展路线：Unity/Unreal 集成（gRPC SDK）、pip 包（pip install kernelsoul）、角色创作工作台、模组工具

数据主权
完全本地化：所有数据存储在用户设备，开放格式（JSON/TXT）

无强制联网：线上 API 可选，本地模型可完全替代

一键导入/导出：完整会话打包为 ZIP，酒馆角色卡直接兼容



**状态层** — 强类型 GameState，AI 可控白名单变量  
**规则层** — SLL 确定性剧本语言，回合级条件判断  
**语义层** — 语义轴 · Warp 映射 · Gram 矩阵 · SLERP 动量 · KNN 短语检索  
**记忆层** — 轻量(10轮) → 深度(50轮) → 史诗(200轮) 三级分级压缩  
**生态层** — 沙箱插件系统 · gRPC API · SillyTavern 插件

每个子系统可独立测试、替换、扩展。

因为能力原因无法写出ui 

---

## 目录结构

```
in-dev/
├── core_engine.py               # 引擎核心（总装所有模块）
├── api_server.py                # FastAPI REST 服务器
│
├── game_state.py                # GameState 强类型状态
├── state_manager.py             # 状态持久化管理器
├── memory_manager.py            # 三层分级压缩记忆
├── parser_engine.py             # AI 响应解析器（JSON / 自然语言）
├── dsl_compiler.py              # SLL 递归下降解析器
├── rule_compiler.py             # AI 协作规则编译器
├── worldbook_retriever.py       # 世界书三维检索
├── evolution_trigger.py         # 规则进化触发器
├── character_card_loader.py     # V1-V4 角色卡加载器
├── plugin_manager.py            # 沙箱插件管理器
├── ai_bridge.py                 # API 桥接（DeepSeek / OpenAI）
├── context.py                   # 上下文组装
├── context_wrappers.py          # 上下文包装器
├── session_meta.py              # 会话元数据
├── path_resolver.py             # 41 条路径方法
├── draft_manager.py             # 草稿与版本管理
│
├── semantic_engine.py           # 语义引擎（轴/Warp/动量/Gram矩阵）
├── semantic_renderer.py         # 语义渲染器（三模式）
├── phrase_library.py            # KNN 短语语料库
│
├── test_parser.py               # 解析器测试
├── test_phase1.py               # Phase 1 回归（48 用例）
├── test_memory.py               # 记忆系统（27 用例）
├── test_dsl_compiler.py         # DSL 编译器（11 用例）
├── test_rule_compiler.py        # 规则编译器（10 用例）
├── test_evolution_trigger.py    # 进化触发器
├── test_character_loader.py     # 角色卡加载
├── test_worldbook.py            # 世界书
├── test_plugin.py               # 插件系统
├── test_saved_drafts.py         # 草稿/会话（12 用例）
├── test_semantic.py             # 语义引擎（17+ 用例）
│
├── configs/
│   ├── system.json              # API 配置
│   ├── system.json.example      # 配置模板（不含 Key）
│   ├── rules.json               # 全局规则
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
│   ├── night_hunter/            # 夜城猎魔人·寒霜（完整示例）
│   │   ├── character_data.json
│   │   ├── character_rules.json
│   │   ├── character_lorebook.json
│   │   ├── character_initstate.json
│   │   ├── character.dsl
│   │   ├── meta_cognition.txt
│   │   └── character_semantic.json
│   ├── cyber_test/              # CyberSprite-7（轻量示例）
│   └── demon_test/              # 堕魔公主 Lucy（轻量示例）
│
├── plugins/
│   ├── example_auto_save/
│   ├── example_broken/
│   └── example_stats_tracker/
│
├── saves/
├── assets/
├── tests/e2e/                   # 端到端测试记录（含 50 轮数据）
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.10+
- DeepSeek / OpenAI 兼容 API Key

### 1. 安装依赖

```bash
cd in-dev
pip install -r requirements.txt
```

依赖：`openai>=1.0.0`、`httpx>=0.27.0`、`fastapi`+`uvicorn`、`numpy`

### 2. 配置 API Key

```bash
cp configs/system.json.example configs/system.json
```

编辑 `configs/system.json`：

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

> `system.json` 已被 `.gitignore` 排除。

### 3. 启动

```bash
# API 模式
python api_server.py
# → Kernelsoul API: http://127.0.0.1:8000

# CLI 模式
python core_engine.py
```

### 4. 运行测试

```bash
python -m pytest test_parser.py test_phase1.py test_memory.py test_dsl_compiler.py test_rule_compiler.py test_evolution_trigger.py test_character_loader.py test_worldbook.py test_plugin.py test_saved_drafts.py test_semantic.py -v
```

---

## 引擎架构

```
用户输入 → 插件钩子 → 世界书检索 → 记忆压缩 → 上下文构建 → AI Bridge → LLM
                                                                          ↓
AI 回复 → 解析引擎 ← 语义渲染(direct/semantic/hybrid) → 状态更新 → 规则检查 → 进化触发
                ↓
          状态持久化 → 存档写入
```

### 五层职责

| 层级 | 主要模块 | 核心职责 |
|------|----------|----------|
| 引擎核心 | `CoreEngine` · `GameState` · `StateManager` | 主循环、状态管理、模块总装 |
| 角色规则 | `CharacterCardLoader` · `DSLCompiler` · `RuleCompiler` | 角色加载、DSL 解析、规则执行 |
| 语义管线 | `SemanticEngine` · `SemanticRenderer` · `PhraseLibrary` | 向量空间投影、Warp、三模式渲染、KNN |
| 记忆上下文 | `MemoryManager` · `Context` · `PathResolver` | 三层压缩、摘要合并、上下文组装 |
| 生态集成 | `PluginManager` · `AIBridge` · `api_server` · `WorldBookRetriever` | 插件、API 桥接、REST、世界书 |

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/characters` | GET | 列出角色 |
| `/api/switch` | POST | 切换/加载角色 |
| `/api/state` | GET | 当前状态 |
| `/api/chat/stream` | POST | SSE 流式对话 |
| `/api/sessions` | GET | 会话列表 |
| `/api/session/switch` | POST | 切换会话 |
| `/api/session/new` | POST | 新会话 |
| `/api/history` | GET | 对话历史 |
| `/api/render_mode` | GET | 查询渲染模式 (v2.4) |
| `/api/render_mode` | POST | 切换渲染模式 (v2.4) |

### 渲染模式 (v2.4)

| 模式 | 说明 | Token 开销 |
|------|------|-----------|
| `direct` | 数值直出（v2.3 向下兼容） | 基准 |
| `semantic` | 全量语义叙事描述 | +33% |
| `hybrid` | 高权重维度语义 + 低权重数值 | +16% |

---

## DSL 规则引擎 (SLL 语言)

```
WHEN hp < 30：
    IF has_potion：
        USE potion
        THEN "她摸出药水一饮而尽"
        BECAUSE "角色危险时使用治疗道具"
    ELSE：
        THEN "她咬紧牙关，血从指缝渗出"
        BECAUSE "无治疗资源时硬撑"
```

递归下降解析器编译为可执行决策树，回合级自动检查所有 WHEN 条件。

---

## 语义叙事渲染引擎 (v2.4)

第21章新增子系统，将 GameState 数值映射为叙事描述：

**数学框架：**
- 语义轴 Dᵢ = embed(正锚) - embed(负锚)
- Warp 函数：数值变化到语义变化的非线性映射
- Gram 矩阵：G = AᵀA 解耦坐标轴
- 子空间 SVD 降维 (k=20)
- SLERP 球面线性插值更新

**渲染管线：**
- 事实标签预计算 + 冲突检测
- KNN 多因子排序检索（事实·风格·动量·去重）
- LLM 降级生成 → 准入审计（5 项校验）
- Miss Buffer 聚类分析补缺口

**依赖说明：** 语义轴向量空间投影需要外部 embedding 模型（OpenAI text-embedding-3-small 或 BGE-Large-ZH）。当前 DeepSeek 不支持 embeddings 端点，semantic/hybrid 模式回退为 state-delta 文本提示。

---

## 插件系统

```
plugins/my_plugin/
├── manifest.json    # {"id":"my_plugin","name":"...","hooks":[...],"permissions":[...]}
└── __init__.py      # 钩子函数实现
```

**支持钩子：** `on_user_input`、`on_ai_response`、`filter`、`on_engine_init`、`on_before_turn`、`on_after_turn`

---

## 测试状态

| 测试文件 | 用例数 | 状态 |
|----------|--------|------|
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
| **总计** | **181+** | **全部通过** |

---

## 版本演进

| 版本 | 更新简述 |
|------|--------|
| v1.0 | 基础架构、AI JSON 协议 |
| v1.1-1.4 | GameState 强类型、解析器、记忆压缩、分级容错 |
| v1.5-1.6 | 角色卡加载器、世界书检索、草稿管理 |
| v2.0 | Kernelsoul 系统、双层规则引擎、决策溯源 |
| v2.1 | SLL 语言、递归下降解析器 |
| v2.3 | 工程化落地、Context 规范 |
| v2.3.1 | 三层记忆压缩（轻/深/史诗） |
| **v2.4** | **语义渲染引擎** |

---

## License

MIT © Kernelsoul Contributors
