《Kernelsoul（Kernelsoul 角色操作系统）》开发执行手册 v2.4
---
快速开始（5 分钟上手）

第一步：安装依赖

```bash
pip install -r requirements.txt
```

第二步：配置 API

编辑 /configs/system.json，填入你的 API 密钥：

```json
{
  "api_type": "deepseek",或者其他，
  "api_key": "sk-your-key-here",
  "model": "deepseek-chat",
  "max_tokens": 4096
}
```

第三步：放入角色卡

将下载的角色卡 JSON 文件放入 /characters/ 目录。支持酒馆格式。

第四步：启动引擎

```bash
python core_engine.py
```
Kernelsoul/
├── /configs/                        # 【配置层】
│   ├── system.json                  # API 密钥、模型名称、Token 窗口
│   ├── rules.json                   # 核心算法与进化规则
│   ├── compression_prompt_light.txt  # 轻量压缩模板（10轮，200字上限）[v2.3]
│   ├── compression_prompt_deep.txt   # 深度压缩模板（50轮，2500字上限）[v2.3]
│   ├── compression_prompt_merge.txt  # 轻量摘要合并模板 [v2.3.1]
│   ├── compression_prompt_epic.txt   # 史诗压缩模板（200轮，5000字上限）[v2.3.1]
│   ├── fallback_prompt.txt          # JSON 解析连续失败时的简化提示词 [v1.3]
│   ├── rule_compiler_prompt.txt     # AI 规则编译器模板 [v2.0]
│   └── /presets/                    # 预设破限池
├── /characters/                     # 【角色与世界观层】
│   │
│   │   # === Kernelsoul 角色文件夹 ===
│   └── /{character_id}/             # Kernelsoul 角色文件夹（标准）
│       ├── character.dsl            # DSL 源码（单一事实来源）
│       ├── character_rules.json     # 编译产物
│       ├── character_data.json      # 角色基础数据
│       ├── character_lorebook.json  # 世界书（可选）
│       ├── character_initstate.json # 旁挂初始状态（可选）
│       ├── character_semantic.json  # 语义渲染配置（可选）[v2.4]
│       ├── meta_cognition.txt       # 元认知提示
│       └── /assets/                 # 角色专属美术（可选）
│   │
│   │   # === 旧版兼容角色卡（V3 过渡格式）===
│   ├── demon_hotel.json             # 角色卡示例1（小恶魔，含名字、描述、性格、提示词、初始状态）
│   ├── demon_hotel_lorebook.json    # 角色卡1的世界书
│   └── cyber_elf.json               # 角色卡示例2（赛博精灵）
├── /assets/                         # 【美术资源层】(初期可留空，自动降级纯文本)
├── /saves/                          # 【多角色多会话存档池】
│   │
│   │   # === 通用存档结构 ===
│   └── /{character_name}/{session_id}/
│       ├── /history/                # 完整历史档案馆（只追加，永久保存）[v1.2]
│       │   ├── full_log.txt         # 创世以来所有已确认对话原文，只追加不删除
│       │   └── full_memory.json     # 历次压缩产生的摘要链，只追加不删除
│       ├── /context/                # 运行时工作区（动态删节）[v1.2]
│       │   ├── recent_log.txt       # 最近10轮已确认对话原文，供打包使用
│       │   ├── working_memory.json  # 从档案馆筛选出的本轮摘要集合
│       │   ├── manual_memory.json   # 手动记忆锚点（持续注入上下文）
│       │   ├── /drafts/             # 临时草稿区（回合级，待确认态暂存）[v1.2]
│       │   └── /saved_drafts/       # 收藏草稿区（手动保存的草稿，提交不清除）[v1.6]
│       ├── state.sav                # 精确游戏状态（仅在提交时更新）
│       └── session_meta.json        # 元数据（含数据版本号，用于存档迁移）[v1.3]
│   │
│   │   # === 具体示例：小恶魔角色第一周目 ===
│   └── /demon_hotel/                # 【小恶魔的角色专属存档文件夹】
│       └── /session_01/             # 第一周目
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
├── /plugins/                        # 插件生态系统 [v1.3]
│   │
│   │   # === 通用插件结构 ===
│   └── /{plugin_id}/
│       ├── manifest.json            # 插件清单（必需）
│       └── __init__.py              # 插件入口（必需）
│   │
│   │   # === 官方示例插件 ===
│   ├── /example_stats_tracker/      # 统计追踪器
│   │   ├── manifest.json
│   │   └── __init__.py
│   └── /example_auto_save/          # 定时存档
│       ├── manifest.json
│       └── __init__.py
└── core_engine.py                   # 引擎主入口```

Kernelsoul 角色文件标准约定（v2.3）

在 /characters/ 目录下，每个角色以文件夹形式组织，包含以下标准文件：

```
/characters/
└── /innkeeper/          # 以角色 ID 命名的文件夹
    ├── character.dsl             # DSL 源码（可版本控制，单一事实来源）
    ├── character_rules.json      # 编译产物（由 DSLCompiler 从 .dsl 编译生成）
    ├── character_data.json       # 角色基础数据（名称、描述、性格、提示词等）
    ├── character_lorebook.json   # 世界书（可选）
    ├── character_initstate.json  # 旁挂初始状态文件（可选）
    ├── meta_cognition.txt        # 元认知提示（自然语言）
    └── /assets/                  # 角色专属美术资源（可选）
        ├── avatar.png            # 头像
        └── full_body.png         # 立绘
```

文件职责：

| 文件 | 类型 | 职责 | 版本控制 |
|------|------|------|----------|
| character.dsl | 源码 | 角色行为逻辑的 DSL 源码。单一事实来源。 | 是 |
| character_rules.json | 编译产物 | 由 DSLCompiler 从 .dsl 编译生成的 JSON 规则。不应手动编辑。 | 否（由编译生成） |
| character_data.json | 数据 | 角色基础属性：name、description、personality、prompt、first_mes 等。 | 是 |
| character_lorebook.json | 数据 | 世界书条目。 | 是 |
| character_initstate.json | 数据 | 旁挂初始游戏状态。 | 是 |
| meta_cognition.txt | 源码 | 元认知"超我"提示词。 | 是 |

加载优先级（引擎启动时）：
1. 若 character.dsl 存在且比 character_rules.json 更新，自动重新编译。
2. 若仅有 character_rules.json 而无 .dsl，引擎尝试反编译生成 .dsl（通过 DSLCompiler.decompile()）。
3. 若两者同时存在且 .dsl 更新，以 .dsl 编译结果覆盖 character_rules.json。
4. character_data.json 为必需文件，其余为可选。

注：引擎启动时，从 system.json 读取 last_character 和 last_session，自动载入上次关闭时的进度。

多角色场景支持（V2.0 规划，v1.6 设计预留）

以下内容不进入 MVP 开发范围，仅为 V2.0 预留数据结构和接口设计。

预留字段：session_meta.json 可包含 active_characters（在场角色ID列表）和 primary_character（当前对话主要角色）。

预留模块：未来可增加"场景角色管理器"，职责包括为每个在场角色维护独立子状态块、管理角色间自动互动和插话逻辑、处理入场/退场事件。

预留 AI 提示词结构：
```
当前场景中的角色：
- {角色1名}：{角色1当前情绪}，正在与玩家对话。
- {角色2名}：{角色2当前情绪}，在旁观察。
{角色2名}可能在适当时机插话。
```

当前兼容策略：MVP 阶段，active_characters 默认仅包含当前角色。用户可通过 /memory add 模拟其他角色的存在。

---
三、核心数据模型与通信协议
3.1 游戏状态强类型定义（GameState）
所有模块共享同一个 GameState 实例，使用 Python @dataclass 定义，字段白名单严格限制：
```python
from dataclasses import dataclass， field
from typing import List
@dataclass
class GameState:
# AI 可修改的字段（白名单）
hp: int = 100
energy: int = 100
goodwill: int = 0
money: int = 0
inventory: List[str] = field(default_factory=list)
bg: str = ““             # 当前背景描述
emotion: str = “neutral“ # 情绪标签
cg: str = ““             # 当前触发CG名称
# 只读字段（AI不可修改）
phase: int = 1
max_hp: int = 100
```
· 序列化：state.sav 以 JSON 格式存储（人类可读）。
· 加载时从 JSON 重建 GameState，缺失字段使用默认值。
· 任何模块修改 GameState 前需通过状态管理器提供的受控方法（如 modify_hp(delta)），防止越权。
3.2 AI 响应协议（自然语言优先，JSON 可选增强）
AI 被要求以自然语言叙事为主，专注于写出引人入胜的剧情。当且仅当 AI 认为剧情导致了明确的状态变化时，可以在回复末尾附加一个 Markdown 代码块（用  ```json  包裹）来描述这些变化。格式如下：
```json
{
“hp“: -5，
“energy“: -10，
“goodwill“: 2，
“money“: 0，
“inventory_add“: [“发霉的面包“]，
“inventory_remove“: [“小恶魔的契约书“]，
“bg“: “阴暗的走廊“，
“emotion“: “愤怒“，
“cg“: “cg_door_open“
}
```
· state_changes 中的所有 key 必须属于 AI 可修改白名单。解析器会进行严格校验：非法字段直接丢弃，只保留合法变更。
· inventory_add/remove 的处理顺序：先执行 remove 再执行 add，避免依赖冲突。
· 背包容错逻辑：remove 时若物品不存在，忽略此条删除指令并写入日志，不报错、不中断。
· 若 AI 未提供 JSON，或解析器提取失败，则本回合仅推进剧情，游戏状态保持不变。叙事本身永远是第一位的。

**新增段落内容**：
【推荐的系统 Prompt 模板】

在构建 AI 请求时，建议使用以下硬指令风格的 Prompt 模板
（存放于 /configs/system_prompt_template.txt）：

你是{角色名}，一个沉浸式叙事游戏中的角色。

【核心规则】
你唯一的任务是写出引人入胜的叙事，像小说家一样推进剧情。
当且仅当本轮剧情导致了明确的状态变化时，
你必须在回复末尾附加一个 JSON 状态块。

【JSON 格式要求】
如果附加 JSON，用 json 代码块包裹，放在回复的最末尾。
格式：{"hp": -5, "energy": 0}

字段说明（只写有变化的字段）：

hp: 生命值变化（负数为受伤，正数为恢复）

energy: 精力变化

goodwill: 好感度变化

money: 金钱变化

inventory_add: 获得物品列表

inventory_remove: 失去物品列表

character_state: 角色内部状态变化，如 {"current_tone": "讽刺"}

【严格禁止】

禁止在自然语言段落中输出 JSON

禁止使用"我无法判断"、"作为 AI 我不确定"等破坏沉浸感的话术

禁止为了凑 JSON 而编造不存在的状态变化。
如果剧情没有变化，只输出叙事，不输出 JSON

注：此模板与 /configs/fallback_prompt.txt 形成两级体系——
正式对话使用此模板，JSON 连续失败时自动切换为降级模板。

---

**与已有内容的关系**：

- 3.2 节前面的白名单规则、背包逻辑、容错说明**全部保留不变**
- 新增的 Prompt 模板是**实现建议**，告诉开发者和创作者“怎么让 AI 遵守这个协议”
- 模板本身放在 `/configs/system_prompt_template.txt`，3.2 节只引用并说明其设计意图

这个插入不改变任何已有规则，只是把抽象协议转化为了可直接使用的 Prompt 文本。
3.3 草稿文件结构（Draft）
每个草稿文件 draft_xxx.json 存储一次 AI 生成的完整数据包：
```json
{
“draft_id“: 1，
“raw_response“: “AI 返回的原始文本（含 narrative 及可能存在的尾部 JSON 代码块）“，
“parsed“: {
“narrative“: “提取出的纯文本剧情“，
“state_changes“: { ... }
}，
“timestamp“: “2026-06-28T14:00:00“
}
```
· state_changes 可能为空对象 {}，表示本回合无状态变更。
3.4 会话元数据结构（session_meta.json）
```json
{
“data_version“: 1，
“created_at“: “2026-06-28T14:00:00“，
“last_saved_at“: “2026-06-28T15:45:00“，
“total_rounds“: 67，
“character_name“: “demon_hotel“，
“session_id“: “session_01“
}
```
3.5 历史摘要链结构（full_memory.json）
```json
{
“data_version“: 1，
“entries“: [
{
“compression_id“: 1，
“round_range“: “1-50“，
“summary“: “玩家在小恶魔旅馆醒来，遇到了前台接待员莉莉丝...“，
“timestamp“: “2026-06-28T14:00:00“
}，
{
“compression_id“: 2，
“round_range“: “51-100“，
“summary“: “玩家前往天台调查，发现隐藏的传送门...“，
“timestamp“: “2026-06-28T15:30:00“
}
]
}
```
==3.6 Kernelsoul 角色卡扩展结构（v2.0）

Kernelsoul 角色卡由 spec: "chara_card_v4" 标识，在 V2/V3 兼容字段基础上增加三个核心扩展块：character_state（角色专属动态变量）、character_rules（行为状态机）、conditional_memories（条件化知识）。

完整结构：

```json
{
  "spec": "chara_card_v4",
  "name": "小恶魔莉莉丝",
  "character_state": {
    "variables": {
      "mood": { "type": "int", "range": [-10, 10], "default": 0, "description": "心情值" },
      "trust_player": { "type": "int", "range": [0, 100], "default": 20, "description": "对玩家的信任度" },
      "fatigue": { "type": "int", "range": [0, 100], "default": 0, "description": "疲劳度" },
      "suspicion": { "type": "int", "range": [0, 100], "default": 30, "description": "怀疑度" },
      "current_tone": { "type": "string", "default": "neutral", "description": "当前说话语气" }
    }
  },
  "character_rules": [
    {
      "id": "praise_king_trigger",
      "trigger": "玩家提及或赞美国王",
      "condition": { "type": "lt", "field": "character_state.mood", "value": 0 },
      "action": [
        { "type": "set_variable", "target": "character_state.current_tone", "value": "讽刺" },
        { "type": "set_variable_delta", "target": "character_state.suspicion", "delta": 10 },
        { "type": "force_emotion", "value": "resentful" }
      ],
      "description": "心情低落时听到赞美国王，强制使用讽刺语气"
    }
  ],
  "conditional_memories": [
    {
      "id": "lilith_betrayal_night",
      "content": "一百年前，莉莉丝被最信任的骑士背叛，在月圆之夜失去了左翼。",
      "unlock_condition": { "type": "gte", "field": "character_state.trust_player", "value": 60 },
      "unlocked": false
    }
  ],
  "meta_cognition_prompt": "你是一个方法派演员，正在扮演{name}。时刻检查自己是否偏离角色设定。如果感觉即将出戏，自然地用符合角色的方式把话题拉回来。",
  "initial_state": { "hp": 100, "max_hp": 100 },
  "character_rules_dsl": "WHEN 玩家提及 \"国王\" IF mood < 0 THEN SET current_tone = \"讽刺\" ...",
  "character_rules_source": "dsl"
}
```

字段说明：
- character_state.variables：角色专属动态变量，独立于 GameState。AI 可读写，引擎代码可读取和强制执行。
- character_rules：角色行为状态机。trigger 为触发描述，condition 为判定条件，action 为强制执行动作。
- conditional_memories：条件化知识。unlocked: false 时不会注入 Prompt，直到满足 unlock_condition。
- meta_cognition_prompt：角色的"超我"提示词，注入在系统预设末尾。
- character_rules_dsl（可选，v2.1）：DSL 源码文本。若存在，引擎优先以此为准编译生成 character_rules。
- character_rules_source（可选，v2.1）：标记规则来源。"dsl" 表示手写 DSL，"ai" 表示 AI 编译生成，"mixed" 表示混合。

与 GameState 的关系：GameState 是跨角色的游戏世界状态；character_state 是角色内部的心理状态。二者由不同管理器维护，在上下文打包时合并注入。

向下兼容：V2/V3 角色卡加载时自动补充默认值，不影响现有角色卡的使用。

---
四、核心引擎模块职责划分
模块类 职责与特殊设定 依赖 AI？
配置管理器 加载 system.json、rules.json、压缩提示词模板、降级提示词模板、预设列表，并读取 last_character、last_session 初始化路径。 否
角色卡加载器（CharacterCardLoader） 自动识别并解析多种角色卡格式（酒馆格式优先），提取名字、描述、性格、提示词、初始状态、开场白（first_mes）等字段，映射到引擎内部结构。支持世界书关联加载。 否
路径管理器（PathResolver） 动态拼接所有路径（包括历史、上下文、草稿区、插件数据），自动创建不存在的文件夹。切换角色/会话时重新绑定新实例。 否
状态管理器 基于 PathResolver 读写 state.sav；提供 apply_state_changes(changes_dict) 方法，内部校验白名单并执行加减法/背包增删。内置背包容错逻辑：remove 物品不存在时忽略并写日志。仅在用户确认提交时调用。 绝对否
记忆管理器 维护双轨档案：日常追加 history/full_log.txt；刷新 context/recent_log.txt；执行双层压缩机制：
- 轻量压缩（每10轮触发）：将最近10轮对话压缩为约200字摘要，追加到 full_memory.json 摘要链。
- 深度压缩（每50轮触发）：将自上次深度压缩以来的所有对话（约50轮）压缩为约2000字深度摘要，包含更完整的事件链、角色态度变化轨迹和关键转折点。
- 上下文打包时，工作记忆（working_memory.json）注入：最近1条深度摘要（2000字级）+ 最近3条轻量摘要（200字级）。深度摘要提供历史脉络，轻量摘要提供近期细节。维护手动记忆锚点列表，存储在 /context/manual_memory.json。上下文打包时，手动记忆锚点置于自动摘要之前，确保优先级最高。仅在提交草稿后执行写入。 是（摘要生成）
世界书检索器 纯代码模块，根据当前角色卡对应的 _lorebook.json，对玩家输入进行关键词匹配，返回匹配到的条目列表。 绝对否
AI 桥接器 将当前预设、角色卡设定、世界书条目、GameState 文本化、working_memory（最近3条摘要）、recent_log（最近10轮对话）拼接成最终 Prompt，调用大模型 API。生成结果暂存为草稿，不直接写入历史。支持 JSON 连续提取失败时自动切换降级提示词模板。 是
解析器引擎 从 AI 返回文本中智能提取状态变更。采用三段式策略：① 提取  ```json  代码块；② 最大括号回溯法；③ 自然语言简单规则匹配。校验字段白名单，失败则返回空变更。绝不崩溃。 否
进化触发器 主循环中在用户确认提交后自动扫描 rules.json 中的进化规则，若条件满足则强制修改 GameState 的只读字段（如 phase）。 绝对否
UI 观察者 监控 GameState 变化；草稿预览阶段展示 narrative；管理流式渲染缓冲区，将 AI 桥接器传来的 token 流拼接为 narrative 片段；控制打字机动画速度和状态；监测用户是否触发跳过动画或停止生成。若 /assets/ 目录为空或缺失指定图片，则自动降级为纯文本展示。 否
插件管理器 扫描 /plugins/ 目录，验证 manifest.json，注册生命周期钩子，提供沙箱隔离和 /plugin 热重载指令。 否
主循环入口 异步事件驱动，拦截以 / 开头的系统指令进行调度，管理草稿生成/选择/提交流程，在关键节点触发插件钩子。 否

角色状态管理器（CharacterStateManager） 维护当前角色的 character_state 变量，执行 character_rules 规则，管理 conditional_memories 的解锁。仅在提交草稿后运行。 绝对否
AI 规则编译器（RuleCompiler） 将创作者的自然语言角色剧本编译为 Kernelsoul 角色卡的 character_rules 和 conditional_memories JSON。仅在角色卡创作阶段使用，非运行时模块。
DSL 编译器（DSLCompiler） 将 SLL 剧本逻辑语言源码确定性编译为 character_rules JSON。支持反向编译（JSON → DSL）。不依赖 AI。 绝对否
未来模块预留（V2.0）：场景角色管理器——为每个在场角色维护独立子状态块，管理角色间自动互动和插话逻辑，处理入场/退场事件。

4.1 路径管理器（PathResolver）完整实现
```python
import os
class PathResolver:
def __init__(self， base_saves: str， base_configs: str， active_char: str， active_session: str):
self.base_saves = base_saves
self.base_configs = base_configs
self.char = active_char
self.session = active_session
self._ensure_dirs()
def _ensure_dirs(self):
os.makedirs(self.get_session_dir()， exist_ok=True)
os.makedirs(self.get_history_dir()， exist_ok=True)
os.makedirs(self.get_context_dir()， exist_ok=True)
os.makedirs(self.get_drafts_dir()， exist_ok=True)
def get_session_dir(self):
return os.path.join(self.base_saves， self.char， self.session)
def get_history_dir(self):
return os.path.join(self.get_session_dir()， “history“)
def get_context_dir(self):
return os.path.join(self.get_session_dir()， “context“)
def get_drafts_dir(self):
return os.path.join(self.get_context_dir()， “drafts“)
def get_state_file(self):
return os.path.join(self.get_session_dir()， “state.sav“)
def get_meta_file(self):
return os.path.join(self.get_session_dir()， “session_meta.json“)
def get_full_log(self):
return os.path.join(self.get_history_dir()， “full_log.txt“)
def get_full_memory(self):
return os.path.join(self.get_history_dir()， “full_memory.json“)
def get_recent_log(self):
return os.path.join(self.get_context_dir()， “recent_log.txt“)
def get_working_memory(self):
return os.path.join(self.get_context_dir()， “working_memory.json“)
def get_compression_prompt(self):
return os.path.join(self.base_configs， “compression_prompt.txt“)
def get_fallback_prompt(self):
return os.path.join(self.base_configs， “fallback_prompt.txt“)
```
---
4.2 角色卡加载器（CharacterCardLoader）

4.2.1 设计目的

SillyTavern（酒馆）的 JSON 角色卡格式已成为 AI 角色扮演社区的通用标准。本引擎必须实现对此格式的一等兼容，让社区海量角色资源可以零摩擦导入。

4.2.2 支持的格式
格式	优先级	识别方式
SillyTavern V3 Spec	1	JSON 中包含 spec 字段，值为 "chara_card_v3"，数据嵌套在 data 对象中
SillyTavern V2 Spec	2	JSON 中包含 spec 字段，值为 "chara_card_v2"
SillyTavern V1	3	JSON 中包含 name、description 等字段，无 spec 字段
引擎原生 Kernelsoul 格式（v4）	4	文件夹包含 character.dsl + character_data.json + character_rules.json

4.2.3 字段映射逻辑

```python
class CharacterCardLoader:
    """角色卡加载器：将外部格式映射到引擎内部结构"""
    FIELD_MAPPING = {
        "name": "name", "description": "description", "personality": "personality",
        "first_message": "first_mes", "scenario": "scenario", "prompt": "system_prompt",
    }
    @classmethod
    def load(cls， file_path: str) -> dict:
        with open(file_path，'r'， encoding='utf-8') as f:
            raw = json.load(f)
        spec = raw.get("spec"， "")
        if spec == "chara_card_v2": return cls._load_tavern_v2(raw)
        elif "name" in raw: return cls._load_tavern_v1(raw)
        else: return cls._load_native(raw)
    @classmethod
    def _load_tavern_v2(cls， raw: dict) -> dict:
        data = raw.get("data"， {})
        return {"name": data.get("name"，""), "description": data.get("description"，""), "personality": data.get("personality"，""), "prompt": data.get("system_prompt"，""), "first_message": data.get("first_mes"，""), "scenario": data.get("scenario"，""), "initial_state": cls._extract_initial_state(data), "lorebook_file": cls._find_lorebook(os.path.dirname(file_path)，data.get("name"，""))}
    @classmethod
    def _extract_initial_state(cls， data: dict) -> dict:
        ext = data.get("extensions"， {})
        es = ext.get("engine_state"， {})
        return {"hp": es.get("hp"，100), "max_hp": es.get("max_hp"，100), "energy": es.get("energy"，100), "goodwill": es.get("goodwill"，0), "phase": es.get("phase"，1)}
    @classmethod
    def _find_lorebook(cls， char_dir: str， char_name: str) -> str | None:
        for c in [f"{char_name}_lorebook.json", f"{char_name}_worldbook.json", "worldbook.json", "lorebook.json"]:
            p = os.path.join(char_dir， c)
            if os.path.exists(p): return p
        return None
```

4.2.4 导入流程

1. 玩家将酒馆角色卡 JSON 文件放入 /characters/ 目录。
2. 引擎启动时，CharacterCardLoader 自动扫描并识别格式。
3. 若角色卡附带世界书，Loader 自动关联加载。
4. 引擎为每个角色卡生成缺失的默认字段。
5. 角色列表（/list）中正常显示。

4.2.5 兼容性承诺

- 引擎不会修改原始角色卡文件。所有映射和补充数据仅在内存和存档中进行。
- 未来酒馆格式升级时，Loader 通过版本号适配，保持向后兼容。

4.2.6 旁挂初始状态文件（v1.6）

酒馆角色卡通常不包含游戏状态定义。引擎在加载角色卡时，同步检查同目录下是否存在旁挂初始状态文件。

文件命名约定：{角色卡文件名（不含扩展名）}_initstate.json

例如：
· 角色卡：/characters/demon_hotel.json
· 初始状态：/characters/demon_hotel_initstate.json

文件格式：

```json
{
  "hp": 80,
  "max_hp": 80,
  "energy": 50,
  "goodwill": -10,
  "money": 200,
  "phase": 1,
  "inventory": ["生锈的匕首", "破旧的地图"],
  "bg": "昏暗的旅馆大厅",
  "emotion": "警惕"
}
```

加载优先级（由高到低）：
1. 旁挂 _initstate.json 文件（若存在）
2. 角色卡内 extensions.engine_state 字段（若存在）
3. 引擎默认值（GameState 类定义的默认值）

实现逻辑：

```python
@classmethod
def _load_initial_state(cls, char_file_path: str, char_data: dict) -> dict:
    """按优先级加载初始状态"""
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

设计优势：玩家无需修改原始角色卡文件，即可为每个角色定制初始游戏状态。旁挂文件可独立分享、备份，不破坏原角色卡的跨平台兼容性。

4.2.7 角色卡版本识别（v2.0，v2.3 修正）
CharacterCardLoader 通过 spec 字段和文件结构自动识别角色卡版本：

spec 值	版本	特征
"chara_card_v3"	V3	data 嵌套结构；含 alternate_greetings、tags、creator、mes_example 等字段；extensions 对象可含 engine_state
"chara_card_v2"	V2	扁平 JSON 结构；静态角色描述；无 data 嵌套；无状态扩展字段
无 spec，有 name + description	V1	最简角色卡；仅含基础描述字段；无任何状态或规则扩展
文件夹含 character.dsl + character_data.json + character_rules.json	Kernelsoul 原生	含 character_state、character_rules、conditional_memories、meta_cognition_prompt；DSL 源码为单一事实来源
升级填充逻辑：

V1/V2/V3 角色卡加载时，引擎自动补充 Kernelsoul 字段的默认值（空 character_state、空 character_rules、空 conditional_memories、默认 meta_cognition_prompt）。

运行时 CharacterStateManager 对无规则的角色卡不做任何操作，开销为零。

V3 角色卡的 extensions.engine_state 字段会被自动提取为初始游戏状态。

创作者可随时将任意版本角色卡升级到 Kernelsoul（v4）：在编辑器中添加 character_state 和 character_rules 扩展字段，或创建 character.dsl 文件，修改 spec 即可。

4.2.8 V3 角色卡格式支持（v2.3）

**V3 格式识别**

V3 角色卡通过 `"spec"` 字段标识：

```json
{
  "spec": "chara_card_v3",
  "data": {
    "name": "角色名",
    "description": "描述",
    "personality": "性格",
    "scenario": "场景",
    "first_mes": "开场白",
    "mes_example": "对话示例",
    "system_prompt": "系统提示词",
    "creator_notes": "创作者笔记",
    "character_version": "1.0",
    "alternate_greetings": ["开场白1", "开场白2"],
    "tags": ["标签1", "标签2"],
    "creator": "创作者名",
    "extensions": {}
  }
}
```

**V2 与 V3 的关键差异**

| 特性 | V2 | V3 |
|------|----|----|
| 数据结构 | 扁平 JSON | `data` 嵌套结构 |
| 角色版本 | 无 | `character_version` 字段 |
| 多开场白 | 无 | `alternate_greetings` 数组 |
| 标签系统 | 无 | `tags` 数组 |
| 创作者署名 | 无 | `creator` 字段 |
| 对话示例 | 无 | `mes_example` 字段 |
| 扩展字段 | 无标准 | `extensions` 对象（可含 `engine_state`） |

**字段映射逻辑**

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

**CharacterCardLoader 补充实现**

```python
@classmethod
def _load_tavern_v3(cls, raw: dict, file_path: str = "") -> dict:
    """加载 SillyTavern V3 格式"""
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
    
    # 尝试关联世界书
    lorebook = cls._find_lorebook(os.path.dirname(file_path) if file_path else "", data.get("name", ""))
    if lorebook:
        char_data["lorebook_file"] = lorebook
    
    return char_data

@classmethod
def _extract_initial_state_v3(cls, data: dict) -> dict:
    """从 V3 角色卡中提取初始状态"""
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
    
    # 检查顶层扩展字段
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

**V3 特有功能支持**

1. **多开场白**：加载时优先使用 `first_mes`。若 `alternate_greetings` 非空且用户未指定，默认使用第一条；可通过 `/greeting [序号]` 切换（此指令为预留，不在 MVP 范围）。
2. **对话示例**：`mes_example` 字段注入系统 Prompt 的对话风格参考部分，帮助 AI 模仿角色语气。
3. **标签与版本**：加载后在角色信息面板展示，方便管理多个版本的角色卡。

**版本识别矩阵更新**

| `spec` 值 | 版本 | 加载方法 |
|-----------|------|----------|
| `"chara_card_v3"` | V3 | `_load_tavern_v3()` |
| `"chara_card_v2"` | V2 | `_load_tavern_v2()` |
| 无 `spec` 但有 `name` + `description` | V1 | `_load_tavern_v1()` |
| 无 `spec`，有 `character.dsl` + `character_data.json` | Kernelsoul 原生 | `_load_native_v4()` |

4.3 角色状态管理器（CharacterStateManager）（v2.0）

4.3.1 职责
1. 加载角色卡时初始化 character_state 变量表。
2. 每轮提交后，扫描 character_rules，检查触发条件，执行匹配的动作。
3. 管理 conditional_memories 的解锁状态。
4. 将当前角色状态注入上下文打包。

4.3.2 核心实现骨架

```python
class CharacterStateManager:
    def __init__(self, character_card: dict):
        self.variables = {}
        self.memories = {}
        self.rules = character_card.get("character_rules", [])
        for var_name, var_def in character_card.get("character_state", {}).get("variables", {}).items():
            self.variables[var_name] = var_def["default"]
        for mem in character_card.get("conditional_memories", []):
            self.memories[mem["id"]] = {"content": mem["content"], "unlock_condition": mem["unlock_condition"], "unlocked": mem.get("unlocked", False)}

    def evaluate_condition(self, condition: dict, game_state=None) -> bool:
        field = condition["field"]; target = condition["value"]
        if field.startswith("character_state."):
            actual = self.variables.get(field.split(".", 1)[1])
        else: return False
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
            if action["target"] in self.memories: self.memories[action["target"]]["unlocked"] = True

    def check_rules(self, user_input: str, ai_response: str, game_state) -> list:
        triggered = []
        for rule in self.rules:
            if rule.get("trigger", "") and rule["trigger"] in user_input + ai_response:
                if self.evaluate_condition(rule.get("condition", {}), game_state):
                    triggered.append(rule)
        return triggered

    def get_unlocked_memories(self) -> str:
        return "
".join([m["content"] for m in self.memories.values() if m["unlocked"]])

    def get_state_text(self) -> str:
        lines = ["【内部状态】"]
        for var_name, value in self.variables.items():
            lines.append(f"- {var_name}: {value}")
        return "
".join(lines)
```

4.3.3 与现有模块的协作
- CharacterStateManager 在每轮提交后与全局 StateManager 先后运行，互不干扰。
- 角色规则和全局规则在同一个提交周期内先后执行——先全局规则，后角色规则。
- get_state_text() 和 get_unlocked_memories() 的结果注入 Prompt，位于全局状态之后、世界书条目之前。

4.3.3 Python 完整实现（v2.3）

```python
"""
Kernelsoul CharacterStateManager — Python 实现
负责变量初始化、规则评估、条件判断、动作执行。
"""

from typing import Any, Optional


class CharacterStateManager:
    """角色状态管理器 — 运行时核心"""

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
        lines = ["【角色内部状态】"]
        for name, value in self.variables.items():
            lines.append(f"- {name}: {value}")
        unlocked = self.get_unlocked_memories()
        if unlocked:
            lines.append("\n【已解锁记忆】")
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


4.4 AI 规则编译器（RuleCompiler）（v2.0）

4.4.1 设计目的
创作者绝不手写 JSON 规则。他们用自然语言写角色剧本，由 AI 编译器生成内核 JSON。

4.4.2 工作流程（三种模式，v2.1 升级）

模式 A：自然语言 → JSON（适合初学者）
1. 输入：创作者输入自然语言角色描述。
2. 编译：系统将自然语言与编译 Prompt 模板组合，发送给 AI。
3. 输出：AI 生成结构化 JSON（character_rules、conditional_memories、suggested_variables）。
4. 烘焙：生成的 JSON 填充到可视化规则编辑器中供创作者修改。
5. 保存：经确认的规则写入角色卡的 character_rules 字段。

模式 B：自然语言 → DSL → JSON（推荐，提供可读中间表示）
1. 输入：创作者输入自然语言角色描述。
2. 编译：系统将自然语言与编译 Prompt 模板组合，发送给 AI，指定输出 DSL 格式。
3. 输出：AI 生成 DSL 源码文本（更具可读性，便于审查和微调）。
4. 烘焙：DSL 源码交由 DSL 编译器（4.5 节）生成 JSON，并填充到可视化编辑器。
5. 保存：经确认的 DSL 源码写入 character_rules_dsl 字段，JSON 写入 character_rules 字段。

模式 C：手写 DSL → JSON（专家模式）
1. 输入：创作者直接在编辑器中编写 DSL 源码。
2. 编译：DSL 编译器（4.5 节）确定性解析源码，无需 AI 参与。
3. 输出：生成的 JSON 直接填充到编辑器供确认。
4. 保存：DSL 源码和 JSON 分别写入角色卡的对应字段。

4.4.3 编译 Prompt 模板
存放位置：/configs/rule_compiler_prompt.txt。包含详细的 JSON Schema 要求和编译规则。

4.4.4 与现有架构的关系
- RuleCompiler 是创作工具，不是运行时引擎。它在角色卡制作阶段使用。
- 生成的规则由运行时 CharacterStateManager 执行。
- 创作者也可以直接手写 JSON 规则，绕过编译器。

4.5 DSL 编译器（DSLCompiler）（v2.1 新增）

4.5.1 职责（v2.1 新增）
- 将 DSL 源码文本解析为 character_rules JSON 数组。
- 执行语义检查（变量声明验证、类型检查、规则 ID 唯一性）。
- 支持反向编译：将 character_rules JSON 还原为 DSL 源码文本。
- 与 RuleCompiler 协作：接收 AI 生成的 DSL 文本并编译验证。

4.5.2 核心接口（v2.1 新增）

```python
class DSLCompiler:
    @staticmethod
    def compile(dsl_source: str, variable_definitions: dict) -> tuple[list, list]:
        """编译 DSL 源码为 character_rules JSON。
        返回 (rules_list, errors_list)。
        若 errors_list 非空，rules_list 可能为部分编译结果。"""
        pass

    @staticmethod
    def decompile(rules_json: list, variable_definitions: dict) -> str:
        """将 character_rules JSON 反编译为 DSL 源码文本。"""
        pass

    @staticmethod
    def validate(dsl_source: str, variable_definitions: dict) -> list:
        """仅校验 DSL 源码，返回错误列表，不生成 JSON。"""
        pass
```

4.5.3 实现策略（v2.1 新增）
- 手写递归下降解析器，不引入第三方解析库。
- 词法分析器使用正则表达式分词。
- 错误信息包含行号和列号，指向具体 DSL 源码位置。
- 反向编译器按固定模板拼接 DSL 文本，保证格式一致。

4.6 文件服务 API（FileService）（v2.3 新增）

4.6.1 设计原则
后端退化为纯粹的文件中转服务，与业务逻辑完全无关。前端通过四个通用 API 完成所有资源管理，将"如何操作数据"的逻辑从前端剥离。

4.6.2 四个核心 API

| 方法 | 端点 | 功能 | 幂等 |
|------|------|------|------|
| GET | /api/files/{path} | 读取文件或目录内容 | 是 |
| POST | /api/files/{path} | 创建新文件或目录 | 否 |
| DELETE | /api/files/{path} | 删除文件或目录 | 是 |
| PATCH | /api/files/{path} | 重命名或移动文件 | 否 |

4.6.3 精细查询语法

GET 请求支持类 GraphQL 的字段选择语法，允许前端精确获取文件的特定部分：

```
# 获取完整 DSL 源码
GET /api/files/character/innkeeper:character.dsl

# 获取编译后的规则 JSON
GET /api/files/character/innkeeper:character_rules.json

# 获取角色基础数据中的名称字段
GET /api/files/character/innkeeper:character_data.json.name

# 获取规则集中的最后 3 条规则
GET /api/files/character/innkeeper:character_rules.json.rules.[-3,-1]

# 列出某个目录下的所有文件
GET /api/files/character/innkeeper/
```

语法规则：
- : 之后为文件内部路径（JSON 字段路径或文本行范围）。
- .[n] 访问数组元素，.[-n,-1] 表示倒数 n 个元素。
- 无 : 时返回整个文件内容。

4.6.4 Python 实现骨架

```python
import os
import json
from pathlib import Path
from typing import Any

class FileService:
    """极简文件服务：四个 API 覆盖所有资源管理"""

    def __init__(self, base_dir: str = "./"):
        self.base_dir = Path(base_dir).resolve()
        self._ensure_safe()

    def _ensure_safe(self):
        os.makedirs(self.base_dir, exist_ok=True)

    def _resolve_path(self, path: str) -> Path:
        """解析路径，禁止路径遍历攻击"""
        resolved = (self.base_dir / path).resolve()
        if not str(resolved).startswith(str(self.base_dir)):
            raise ValueError(f"路径越界: {path}")
        return resolved

    def get(self, path: str) -> Any:
        """读取文件或目录。支持精细查询。"""
        parts = path.split(":", 1)
        file_path = self._resolve_path(parts[0])
        if file_path.is_dir():
            return {"type": "directory", "items": os.listdir(file_path)}
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        content = self._read_file(file_path)
        if len(parts) > 1:
            return self._query_content(content, parts[1], file_path.suffix)
        return content

    def post(self, path: str, content: Any = None) -> dict:
        """创建新文件或目录"""
        file_path = self._resolve_path(path)
        if file_path.exists():
            raise FileExistsError(f"文件已存在: {path}")
        if content is None:
            os.makedirs(file_path, exist_ok=True)
            return {"type": "directory", "created": path}
        os.makedirs(file_path.parent, exist_ok=True)
        self._write_file(file_path, content)
        return {"type": "file", "created": path}

    def delete(self, path: str) -> dict:
        """删除文件或目录"""
        file_path = self._resolve_path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        if file_path.is_dir():
            import shutil
            shutil.rmtree(file_path)
            return {"type": "directory", "deleted": path}
        os.remove(file_path)
        return {"type": "file", "deleted": path}

    def patch(self, path: str, new_path: str) -> dict:
        """重命名或移动文件"""
        file_path = self._resolve_path(path)
        target_path = self._resolve_path(new_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
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
        lines = text.split('
')
        if ':' in query:
            start, end = query.split(':')
            start = int(start) if start else 0
            end = int(end) if end else len(lines)
            return '
'.join(lines[start:end])
        return text
```


五、系统控制台指令——游戏内支持 [v1.0，多版本扩展]

为了在多个角色和多个存档之间丝滑切换，以及管理草稿、记忆锚点、规则和插件，主循环必须拦截以下指令，且不进入 AI 流程。所有指令以 "/" 开头，可在对话中随时使用。未被拦截的普通文本进入 AI 流程作为玩家输入。

---

5.1 角色与会话管理 [v1.0]

提供角色切换、新周目创建和存档加载的核心功能。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /list 或 /ls | 无 | 列出 /characters/ 文件夹下所有可用的角色卡 | v1.0 |
| /character | [角色名] | 切换当前角色。引擎立刻去硬盘加载对应的角色卡 JSON（Kernelsoul 角色读取 character.dsl → character_rules.json），并自动读取该角色名下最近的会话 | v1.0 |
| /newgame | [角色名] | 开新周目。如果角色存在，引擎在其专属文件夹下新建一个 session_XX（命名自动递增），并写入初始状态的 state.sav。未指定角色名时使用当前角色 | v1.0 |
| /load | [角色名] [会话ID] | 指定加载。直接跳转到指定的存档文件夹读取数据。仅指定角色名时自动加载最近会话 | v1.0 |

5.2 预设管理 [v1.0]

快速切换角色的行为模式（system_prompt / 元认知）。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /preset | [预设名] | 从 /configs/presets/ 读取指定预设文件，替换当前 system_prompt 和 meta_cognition.txt 内容。Kernelsoul 角色可进一步使用角色层预设（character_rules.json） | v1.0 |

5.3 草稿与版本控制 [v1.2]

每次 AI 生成回复后，结果作为草稿保存。用户可以查看、重投（重新生成）或选定最终回复。确认后草稿被提交为正式历史并清空草稿区。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /roll | 无 | 仅在当前回合未确认时有效。请求 AI 重新生成，新结果追加为新草稿（draft 编号递增），不清除旧草稿 | v1.2 |
| /select | [序号] | 从现有草稿中选择一个作为正式回复。引擎将该草稿的 narrative 写入历史链、应用其 state_changes 更新游戏状态，然后清空整个 /drafts/ 文件夹。未指定序号时默认选择最新草稿 | v1.2 |
| /drafts | 无 | 列出当前所有草稿的摘要（前100字），展示编号和核心内容，方便查看选择 | v1.2 |

5.4 草稿收藏 [v1.6]

将草稿手动保存到收藏区，防止自动清空时丢失。适合标记有趣的 AI 回复、备选走向或暂时不提交的分支。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /draft save | [序号] | 将指定序号的草稿保存到 /context/saved_drafts/ 目录，提交时不清除 | v1.6 |
| /saved | 无 | 列出所有已保存的草稿（含摘要和时间戳） | v1.6 |
| /saved load | [序号] | 将一份已保存草稿重新载入为当前确认草稿，进入可提交状态 | v1.6 |

5.5 记忆锚点 [v1.5]

手动添加永久记忆锚点，这些锚点会在每次上下文打包时持续注入，不受压缩和摘要流程影响。适合记录重要事件、角色承诺或长期叙事线索。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /memory add | [内容] | 将一段文本作为永久记忆锚点，写入 /context/manual_memory.json，直接注入到每次上下文打包中 | v1.5 |
| /memory list | 无 | 列出当前所有手动添加的记忆锚点 | v1.5 |
| /memory delete | [序号] | 删除指定序号的手动记忆锚点 | v1.5 |

5.6 规则管理 [v1.5]

支持导出和导入规则配置，用于社区分享或版本迁移。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /rules export | [文件名] | 将当前全局规则（rules.json）和角色规则（character_rules.json）导出为打包文件 | v1.5 |
| /rules import | [文件名] | 从打包文件导入规则，覆盖当前规则配置（导入前自动备份旧规则） | v1.5 |

5.7 插件管理 [v1.3]

管理插件的加载、启用和热重载。插件存放在 /plugins/ 目录下，每个插件一个子文件夹，含 manifest.json 和 __init__.py。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /plugin list | 无 | 列出所有已加载的插件及其启用/禁用状态 | v1.3 |
| /plugin reload | [插件ID] | 热重载指定插件，无需重启引擎。修改插件代码后使用 | v1.3 |
| /plugin enable | [插件ID] | 启用指定插件，使其钩子和功能生效 | v1.3 |
| /plugin disable | [插件ID] | 禁用指定插件，其钩子和功能停止生效 | v1.3 |

5.8 数据管理 [v1.5]

完整存档数据的导出和导入，用于备份、跨设备迁移或分享存档。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /export | 无 | 将当前会话的完整存档（history、context、state、meta）打包导出为 .zip 文件 | v1.5 |
| /import | [文件路径] | 从 .zip 打包文件导入存档，恢复完整会话状态 | v1.5 |

5.9 调试与控制 [v1.5/v2.0]

开发者调试模式和安全停止引擎。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /debug on | 无 | 开启调试模式：在每轮输出中显示规则触发链、DSL 溯源信息、变量变更日志、Token 用量等调试信息 | v2.0 |
| /debug off | 无 | 关闭调试模式，恢复标准输出 | v2.0 |
| /stop | 无 | 安全停止引擎，保存当前所有状态后退出 | v1.5 |

5.10 帮助与市场 [v1.5/预留]

快速查阅指令和访问社区插件市场。

| 指令 | 参数 | 作用 | 引入版本 |
|------|------|------|----------|
| /help | [指令名] | 显示指令帮助。无参数时列出所有可用指令；指定指令名时显示该指令的详细用法 | v1.5 |
| /market list | 无 | 列出社区插件市场中可用的插件（需联网） | 预留 |
| /market install | [插件ID] | 从社区市场安装指定插件到 /plugins/ 目录 | 预留 |

---

5.11 默认行为说明 [v1.2]

若用户直接输入普通文本（非 "/" 开头），引擎按以下规则处理：

1. 若当前不存在未确认草稿：用户输入直接进入 AI 流程，作为新回合的玩家输入。
2. 若当前存在未确认草稿：自动等同于 /select latest，先提交最新草稿，再将用户输入作为下一回合的开始。

此行为确保玩家可以连续自然对话而不必每次确认草稿，同时保留 /select 的精确控制能力。玩家可通过 /roll 重新生成、/select 手动选择、或 /draft save 保存草稿，覆盖默认自动提交逻辑。

---

命令速查表

| 命令分组 | 包含指令 | 引入版本 |
|----------|----------|----------|
| 角色与会话管理 | /list、/character、/newgame、/load | v1.0 |
| 预设管理 | /preset | v1.0 |
| 草稿与版本控制 | /roll、/select、/drafts | v1.2 |
| 草稿收藏 | /draft save、/saved、/saved load | v1.6 |
| 记忆锚点 | /memory add、/memory list、/memory delete | v1.5 |
| 规则管理 | /rules export、/rules import | v1.5 |
| 插件管理 | /plugin list、/plugin reload、/plugin enable、/plugin disable | v1.3 |
| 数据管理 | /export、/import | v1.5 |
| 调试与控制 | /debug on/off、/stop | v1.5/v2.0 |
| 帮助与市场 | /help、/market list、/market install | v1.5/预留 |
| 默认行为 | 普通文本自动提交 + 新回合 | v1.2 |

---

六、规则引擎详细语法
rules.json 文件格式示例：
```json
{
“evolution_rules“: [
{
“id“: “phase_2_unlock“，
“condition“: {
“type“: “gte“，
“field“: “goodwill“，
“value“: 80
}，
“action“: {
“type“: “set_phase“，
“target“: 2
}
}，
{
“id“: “low_hp_buff“，
“condition“: {
“type“: “lte“，
“field“: “hp“，
“value“: 20
}，
“action“: {
“type“: “set_max_hp“，
“target“: 120
}
}，
{
“id“: “special_item_unlock“，
“condition“: {
“type“: “contains“，
“field“: “inventory“，
“value“: “恶魔钥匙“
}，
“action“: {
“type“: “set_phase“，
“target“: 3
}
}
]
}
```
支持的操作符：
· eq、neq、gt、gte、lt、lte：数值比较。
· contains：检测列表（如 inventory）是否包含指定字符串。
支持的动作类型：
· set_phase：设置进化阶段。
· set_max_hp：修改最大生命值。
· add_item：向背包添加物品。
· remove_item：从背包移除物品。
· set_bg：修改当前背景。
· 更多动作类型可在后续版本中扩展。
进化触发器在每回合提交后，按规则顺序依次检查。一旦条件满足，立即执行对应动作。同一回合可能触发多个不冲突的规则。

规则弹性与例外处理（v1.5）

规则引擎保证游戏机制的确定性，但叙事游戏的魅力部分在于"意料之外"。为防止系统变得机械僵化，引入以下弹性设计：

1. 规则的"允许例外"标记

在 rules.json 的每条规则中增加可选字段 allow_override: false（默认）：

```json
{
  "id": "phase_2_unlock",
  "condition": { "type": "gte", "field": "goodwill", "value": 80 },
  "action": { "type": "set_phase", "target": 2 },
  "allow_override": false
}
```

当 allow_override: true 时，AI 可以在 JSON 状态变更中请求"暂时无视此规则"，引擎会生成一个临时豁免提示显示给玩家，由玩家决定是否接受。

2. 插件的规则介入钩子

在插件生命周期中增加 on_rule_trigger 钩子，规则即将触发时调用。返回 None 则正常执行；返回修改后的 action 则替换原动作。

3. 随机事件表（未来扩展）：预留 /configs/random_events.json 接口。

设计原则：确定性是骨架，弹性是血肉。AI 不能绕过规则，但创作者和玩家可以。

规则集分享与导入（v1.5）：/rules export [文件名] 导出；/rules import [文件名] 导入。预设破限（/presets/）也可通过社区索引分享。

角色层规则引擎（v2.0）

Kernelsoul 角色卡可内嵌 character_rules，形成双层规则架构：

| 层级 | 位置 | 作用域 | 优先级 | 管理模块 |
|------|------|--------|--------|----------|
| 全局规则 | /configs/rules.json | 所有角色 | 高 | EvolutionTrigger |
| 角色规则 | 角色卡内 character_rules | 当前角色 | 低 | CharacterStateManager |

执行顺序（每轮提交后）：全局规则 → 角色规则。若二者修改同一变量，全局规则优先。

AI 可通过 state_changes JSON 中增加 character_state 字段请求修改角色内部状态，由 CharacterStateManager 校验后执行，白名单为 character_state.variables 中定义的变量。

---

七、Kernelsoul 角色行为 DSL：剧本逻辑语言（SLL）（v2.1 新增）

7.1 设计目标（v2.1 新增）

Kernelsoul 架构的核心是"刚性内核，柔性外壳"。角色卡从"被阅读的故事"升级为"被执行的逻辑体"。为此，需要一种专门的语言来描述角色行为的逻辑——它必须满足：

- 人类可读可写：创作者无需学习编程就能书写和理解。
- 确定性可执行：编译为机器可精确执行的指令，消除 LLM 的概率不确定性。
- 可调试可溯源：执行引擎能回溯到 DSL 源码行，在 UI 中高亮显示触发规则。
- 与自然语言互补：创作者既可以用纯自然语言交给 RuleCompiler 自动编译，也可以直接手写 DSL 精确控制。

DSL 将作为自然语言与 JSON 规则之间的中间表示，形成完整的创作链路：

```
自然语言剧本 → (RuleCompiler) → DSL 源码 → (DSL 编译器) → JSON 规则 → (CharacterStateManager) 执行
```

与此同时，引擎的调试与审计方向是逆向的——AI 在每回合输出的 JSON 规则变更，
可以通过 DSLCompiler.decompile() 反编译回 DSL 源码，再翻译为创作者可读的自然语言解释。
这确保了 AI 的行为永远可被追溯、审计和修正，而非黑盒 Prompt。

```
逆向调试链路：
AI 输出的 JSON 规则 → (decompile) → DSL 源码 → (解释) → 创作者可读的自然语言
```

这个双向闭环的核心价值：

| 方向 | 路径 | 目的 |
|------|------|------|
| 正向（创作） | 自然语言 → DSL → JSON → 执行 | 确定性编译，角色行为可控 |
| 逆向（调试） | JSON → DSL → 自然语言 | 可溯源审计，AI 决策透明 |

DSL 作为唯一的中枢格式，JSON 和自然语言对称地分布在其两侧——
谁也不是谁的附属，但谁也绕不开 DSL。

```

熟练的创作者可直接手写 DSL，跳过自然语言编译环节，获得更精细的控制力。

7.2 核心语法（v2.1 新增）

7.2.1 基本结构：一条规则（v2.1 新增）

一条规则由四个部分组成：触发事件、前置条件、动作列表、描述。

```
WHEN <触发事件描述> IF <条件表达式> THEN <动作1> <动作2> ... BECAUSE "<人类可读的规则说明>"
```

示例：

```
WHEN 玩家提及"国王"或"王室" IF mood < 0 THEN SET current_tone = "讽刺" CHANGE suspicion BY +10 FORCE EMOTION "resentful" BECAUSE "心情不好时听到赞美国王，会激起她的戒备和反感"
```

7.2.2 触发事件（WHEN）（v2.1 新增）

触发事件定义了规则何时被评估。它可以是关键词匹配、系统事件或状态变化。

关键词匹配：
```
WHEN 玩家提及 <关键词/短语>
WHEN 玩家提及 <词1>、<词2>、... 或 <词N>
```

系统事件：
```
WHEN 回合开始
WHEN 回合结束
WHEN 时间变化 TO "深夜"
WHEN 角色首次登场
WHEN 角色死亡
```

状态变化事件（未来扩展）：
```
WHEN trust_player CHANGED FROM <旧值> TO <新值>
WHEN mood BECAME NEGATIVE
```

关键词匹配默认不区分大小写，可同时指定多个关键词（逻辑"或"）。

特殊触发器 ALWAYS：表示每回合无条件评估（仅检查条件）。
```
WHEN ALWAYS IF fatigue > 80 THEN SET current_tone = "疲惫"
```

7.2.3 条件表达式（IF）（v2.1 新增）

条件表达式使用类似自然语言的比较语法，支持与角色状态变量和全局游戏状态的比较。

基础比较：
```
<变量名> <操作符> <值>
```

操作符：>、<、>=、<=、==、!=

对于字符串：== 精确匹配，CONTAINS 包含子串

示例：
```
IF trust_player >= 60
IF current_tone == "愤怒"
IF mood <= -5
IF player_inventory CONTAINS "玫瑰花"
```

逻辑组合：
```
IF <条件1> AND <条件2>
IF <条件1> OR <条件2>
IF NOT <条件>
```

可用括号明确优先级：
```
IF (mood < 0) AND (trust_player > 50 OR suspicion < 30)
```

变量路径：
- 角色内部状态：直接使用变量名，如 mood、trust_player、fatigue。
- 全局游戏状态：以 game. 为前缀，如 game.hp、game.phase。
- 玩家状态（未来扩展）：以 player. 为前缀，如 player.gold。

特殊条件：
```
IF 时间是 "深夜" —— 需配合系统时间事件。
IF 回合数 > 10
IF 记忆已解锁 "记忆ID" —— 检查某条条件记忆是否已解锁。
```

7.2.4 动作列表（THEN）（v2.1 新增）

动作是规则触发后强制执行的操作。每个动作独占一行。

变量赋值：
```
SET <变量名> = <新值>
SET mood = 5
SET current_tone = "温柔"
```
值可以是数字、字符串或布尔值。

变量增减：
```
CHANGE <变量名> BY <增量>
CHANGE suspicion BY +10
CHANGE fatigue BY -5
```

解锁/锁定记忆：
```
UNLOCK MEMORY "记忆ID"
LOCK MEMORY "记忆ID"
```

强制语气/情绪：
```
FORCE TONE "讽刺"
FORCE EMOTION "resentful"
```
这两个动作会向下一轮 AI 生成注入强提示，要求以特定语气或情绪回应。

发送系统消息（不显示给玩家）：
```
LOG "<消息内容>"
```
用于调试或内部记录。

触发全局规则（高级）：
```
TRIGGER RULE "全局规则ID"
```
允许角色规则主动调用全局规则引擎中的指定规则。

条件动作（未来扩展）：暂不实现。建议保持规则粒度细小。

7.2.5 描述（BECAUSE）（v2.1 新增）

BECAUSE 子句是规则的注释，用人类语言解释这条规则存在的理由。它不会被执行，但会出现在决策溯源面板中，帮助创作者和玩家理解角色行为逻辑。

7.3 变量系统（v2.1 新增）

DSL 中操作的变量必须在角色卡的 character_state.variables 中预先定义。

```
VARIABLES:
  mood: int, range(-10,10), default 0, "心情值"
  trust_player: int, range(0,100), default 20, "对玩家的信任度"
  fatigue: int, range(0,100), default 0, "疲劳度"
  suspicion: int, range(0,100), default 30, "怀疑度"
  current_tone: string, default "neutral", "当前说话语气"
```

创作者可以在角色卡中声明变量表。如果 DSL 中引用了未声明变量，编译器将报错并提示。

7.4 与 JSON 规则的对应关系（v2.1 新增）

DSL 源码将编译为 Kernelsoul 规范中定义的 character_rules JSON 数组。编译过程是确定性的，反向转换也可实现（用于在可视化编辑器中双向同步）。

一条 DSL 规则对应的 JSON 结构：

```json
{
  "id": "praise_king_trigger",
  "trigger": "玩家提及国王",
  "condition": { "type": "lt", "field": "character_state.mood", "value": 0 },
  "action": [
    { "type": "set_variable", "target": "character_state.current_tone", "value": "讽刺" },
    { "type": "change_variable", "target": "character_state.suspicion", "delta": 10 },
    { "type": "force_emotion", "value": "resentful" }
  ],
  "description": "心情不好时听到赞美国王，会激起她的戒备和反感"
}
```

映射关系：
- trigger 字段：在 DSL 中为关键词匹配时，展开为精确的关键词列表和匹配模式。
- condition：条件表达式被解析为操作符和字段路径。
- action：动作映射为 action 对象数组。
- description：BECAUSE 部分存入此字段。

当创作者在可视化编辑器中修改 JSON 规则时，DSL 源码也将同步更新，确保单一事实来源。

7.5 DSL 编译器实现概要（v2.1 新增）

DSL 编译器是一个独立模块，负责将 DSL 源码文本解析为 character_rules JSON。它不依赖 AI，是一个确定性解析器。

实现步骤：
1. 词法分析：将源码分割为 Token 流（WHEN、IF、SET、IDENTIFIER、STRING、NUMBER 等）。
2. 语法分析：根据文法规则构建抽象语法树（AST）。
3. 语义检查：验证引用的变量是否已声明；验证操作符与变量类型匹配；检查规则 ID 唯一性。
4. 代码生成：遍历 AST，生成对应的 JSON 结构。

文法概要（简化 EBNF）：

```
rule      := "WHEN" trigger "IF" condition "THEN" action+ "BECAUSE" string
trigger   := "ALWAYS" | "玩家提及" string_list | 系统事件关键字
condition := expr (("AND"|"OR") expr)*
expr      := ("NOT")? (variable op value | "(" condition ")")
variable  := IDENTIFIER ("." IDENTIFIER)*
op        := ">" | "<" | ">=" | "<=" | "==" | "!=" | "CONTAINS"
action    := set_action | change_action | unlock_action | force_tone_action ...
set_action := "SET" variable "=" value
change_action := "CHANGE" variable "BY" ("+"|"-")? NUMBER
value     := NUMBER | STRING | BOOLEAN
```

由于语法极为简单，可以用手写递归下降解析器轻松实现，无需引入第三方解析库，保持引擎的轻量。

7.5.1 Python 实现代码（v2.3）

```python
"""
Kernelsoul DSL 编译器 — Python 实现
确定性手写递归下降解析器，不依赖 AI。
相同 DSL 输入永远产生相同 JSON 输出。
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
    """Kernelsoul DSL 编译器 — 确定性递归下降解析器"""

    def compile(self, dsl_source: str,
                variables: dict[str, VariableDefinition]) -> tuple[list[CharacterRule], list[dict]]:
        """编译 DSL 源码为规则列表。返回 (rules, errors)。"""
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
                match = re.match(r'WHEN\\s+玩家提及\\s+(.+)', line)
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
            errors.append({'line': line, 'message': f'条件表达式语法错误: {expr}'})
            return None
        field = f"character_state.{parts[0]}"
        op = parts[1]
        value = self._parse_value(' '.join(parts[2:]))
        if parts[0] not in variables:
            errors.append({'line': line, 'message': f'未声明变量: {parts[0]}'})
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


7.6 与 RuleCompiler（AI 编译器）的协作（v2.1 新增）

引入 DSL 后，RuleCompiler 的工作流升级为三种模式共存：

模式 A：自然语言 → JSON（现有流程，适合初学者）
- 用户输入自然语言描述。
- RuleCompiler 直接生成 JSON 规则，并存入角色卡。

模式 B：自然语言 → DSL → JSON（推荐流程，提供可读中间表示）
- 用户输入自然语言描述。
- RuleCompiler 生成 DSL 源码（而非直接 JSON），更具可读性，便于用户审查和微调。
- DSL 源码交由确定性 DSL 编译器生成最终 JSON。
- 用户在可视化编辑器中看到的将是 DSL 文本，可随时手动修改。

模式 C：手写 DSL → JSON（专家模式）
- 创作者直接在编辑器中编写 DSL 源码。
- 确定性编译器生成 JSON，无需 AI 参与。

三种模式共存，降低不同层次创作者的门槛。

7.7 决策溯源与 DSL（v2.1 新增）

决策溯源面板是 Kernelsoul 可视化调试层的核心。当执行引擎触发规则后，会向前端推送 rule_trace 对象，其中除了 JSON 规则信息外，还包含 DSL 源码引用。

例如，当"赞美国王触发器"触发时，前端显示的调试信息：

```
[橙色] 角色规则：赞美国王触发器
  源码：WHEN 玩家提及"国王" IF mood < 0 THEN SET current_tone = "讽刺" ...
  原因：玩家输入中检测到关键词"国王"，且当前 mood = -3 (< 0)
  动作：语气 → 讽刺，怀疑度 +10
```

如果创作者开启了 /debug on，前端会完整显示所有规则的 DSL 列表，已触发的规则高亮，未触发的置灰，并实时展示变量值。

7.8 完整示例：小恶魔莉莉丝的 DSL 规则集（v2.1 新增）

```
VARIABLES:
  mood: int, range(-10,10), default 0
  trust_player: int, range(0,100), default 20
  fatigue: int, range(0,100), default 0
  suspicion: int, range(0,100), default 30
  current_tone: string, default "neutral"

WHEN 玩家提及 "国王"、"王室"、"陛下" IF mood < 0 THEN
  SET current_tone = "讽刺"
  CHANGE suspicion BY +10
  FORCE EMOTION "resentful"
BECAUSE "心情低落时听到赞美国王，会激发她对权力者的讽刺和警惕"

WHEN 时间变化 TO "深夜" IF trust_player >= 60 THEN
  UNLOCK MEMORY "lilith_betrayal_night"
  SET current_tone = "脆弱"
BECAUSE "在信任的人面前，深夜的孤独会让她卸下心防，吐露过去的伤痛"

WHEN 玩家提及 "背叛"、"骑士" IF trust_player < 40 THEN
  SET current_tone = "冷漠"
  CHANGE suspicion BY +15
  FORCE TONE "冷漠"
BECAUSE "尚未信任玩家时，触及她的旧伤会激起防御和疏离"

WHEN ALWAYS IF fatigue > 80 THEN
  SET current_tone = "疲惫"
  CHANGE mood BY -2
BECAUSE "极度疲劳时，心情自然会变差，语气也会失去活力"

WHEN 玩家提及 "阿撒兹勒" IF trust_player >= 90 THEN
  UNLOCK MEMORY "lilith_true_name"
  SET current_tone = "神圣"
BECAUSE "只有获得绝对信任的人，才能得知她的真名，那一刻她会展现真实的一面"
```

7.9 版本兼容与演进（v2.1 新增）

- 现有的 Kernelsoul JSON 规则可以无损转换为 DSL（通过反编译器），因此已有角色卡不受影响。
- 引擎启动时，如果角色卡仅包含 JSON 规则而未包含 DSL 源码，CharacterCardLoader 会尝试反编译生成 DSL 文本，并存入角色卡的 character_rules_dsl 字段（可选），方便后续编辑。
- 如果两者同时存在且不一致，以 DSL 源码为准（重新编译覆盖 JSON），确保单一事实来源。



---
八、初期与后期模式的兼容定义
· 初期形态（无画面）：引擎扫描 /assets/ 目录为空时，禁用图片渲染，仅展示纯文本对话框和状态栏。可直接导入多张酒馆角色卡及配套世界书。
· 后期形态（2D 完整版）：放入图片资产后自动激活 2D 渲染，引擎零代码修改。

---

8.1 节：UI 性能与交互基准

8.1.1 响应延迟目标

| 操作 | 目标延迟 | 用户感知 |
|------|----------|----------|
| 指令响应（/list、/select 等） | <50ms | 即时 |
| 草稿预览开始（首个 token 出现） | <500ms | 流畅 |
| 打字机效果 | 30ms/字（可配置） | 舒适的阅读节奏 |
| 状态栏更新 | <100ms | 即时 |

8.1.2 多模态交互规划（后期扩展）：预留语音输入、角色立绘、背景音乐接口。

8.1.3 SillyTavern 模式 UI 布局参考：左侧角色列表/会话选择器，中央对话流（打字机效果），右侧状态面板，底部输入框，顶部角色名/插件入口。

决策溯源面板（v2.0）

设计目的：当角色说出一句话，界面高亮显示触发它的那条规则，让玩家和创作者理解"角色为什么这么说"。

UI 规格：
1. 位置：右侧状态面板底部，可折叠，默认折叠。
2. 内容：触发规则名称、触发条件、执行动作。无规则时显示"本回合无规则触发"。
3. 样式：触发的规则浅色高亮；全局规则用蓝色色带，角色规则用橙色色带。悬停显示完整描述。
4. 调试模式（/debug on）：显示所有规则列表（已触发高亮，未触发置灰）、角色状态变量实时值、条件记忆解锁状态。

前端数据来源：每轮提交后推送 rule_trace 对象（含 triggered_rules 数组和 character_state 快照）。

DSL 源码级高亮（v2.1）：rule_trace 对象新增 dsl_source_lines 字段，记录每条触发规则对应的 DSL 源码行范围。界面高亮相应 DSL 代码行，悬停显示完整解析。无 DSL 源码的规则显示反编译推测文本。

8.2 前端 Context 网络设计规范（v2.3）

8.2.1 设计哲学
前端采用基于事件和注册的 Context 网络实现高度可组合性。系统被拆分为独立的 Context 对象，通过两种机制协作：

- 事件：决定"什么时候做什么"，是流程控制的"行动信号"。
- 注册：决定"做的时候从哪拿数据"，是建立依赖关系的"数据来源声明"。

8.2.2 Context 网络核心概念

| 概念 | 说明 |
|------|------|
| Context | 独立的功能单元，拥有私有状态，通过事件与外界通信 |
| 事件（Event） | 命名信号，携带数据负载。任何 Context 可发出，任何 Context 可订阅 |
| 注册（Registration） | Context 启动时声明对全局资源的依赖，由全局容器注入 |
| 全局容器（GlobalContext） | Context 的注册中心和事件总线 |

8.2.3 KernelsoulEngineContext 作为标准 Context 节点

Kernelsoul 引擎被封装为 KernelsoulEngineContext，作为标准 Context 接入前端网络：

```python
class KernelsoulEngineContext:
    """Kernelsoul 引擎的 Context 封装"""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.dsl_compiler = DSLCompiler()
        self.state_manager = CharacterStateManager()
        self._compiled_rules: dict[str, list] = {}
        self._variable_defs: dict[str, dict] = {}

    def init(self, global_context):
        """初始化：注册依赖并绑定事件"""
        self.file_service = global_context.get('file_service')
        self.event_bus.on('character.switched', self._on_character_switched)
        self.event_bus.on('message.received', self._on_message_received)

    def _on_character_switched(self, char_id: str):
        """角色切换 → 自动加载 DSL 并编译"""
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
        """消息到达 → 评估规则 → 发出决策"""
        char_id = message.get('char_id')
        rules = self._compiled_rules.get(char_id)
        if not rules:
            return
        context = {'message': message, 'timestamp': message.get('timestamp', 0)}
        decisions = self.state_manager.evaluate(context)
        for decision in decisions:
            self.event_bus.emit('v4.decision', decision)
```

8.2.4 与 Gradio/Web UI 的对接

当 MVP 阶段使用 Gradio 作为前端时，Context 网络简化为 Gradio 的 State 和 Event 机制：

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

8.2.5 语言无关性说明
Context 网络的核心是设计模式（观察者模式 + 依赖注入），而非特定语言实现。TypeScript 版本使用 EventEmitter 基类，Python 版本可使用 asyncio.Event 或简单回调列表。两种实现遵循相同的事件命名约定和数据负载格式。


---
九、标准端到端执行流程
1. 系统指令拦截：获取玩家输入。若以 / 开头（如 /character demon_hotel、/roll、/select 2、/plugin list），直接执行对应调度，不消耗回合，不进入 AI 流程。
2. 插件输入拦截（v1.3）：触发 on_user_input 钩子，已注册插件可检查、修改或拦截用户输入。若插件返回了替代文本，则使用替代文本继续；若插件要求拦截，则终止本回合。

步骤2.5：开场白初始化（v1.6）

触发时机：仅在 /newgame [角色名] 或 /load [角色名] [会话ID] 加载空白会话时触发。加载已有对话历史的会话时不触发（开场白已在历史中）。

处理流程：
1. 提取开场白：若角色卡包含 first_mes 字段且非空，以其内容作为开场白。若角色卡无此字段，使用引擎默认开场白模板：【系统】：欢迎来到{角色名}的故事。你站在{场景描述}。{角色名}就在你面前。
2. 注入历史链：开场白作为系统级首条消息，直接写入 history/full_log.txt 和 context/recent_log.txt。不经过草稿区——它是确定的、不可重投的。
3. 前端展示：UI 首先展示开场白文本，然后显示输入框。开场白在对话流中以特殊样式标记（如斜体或左侧色条），区分于 AI 生成的剧情。
4. 与正常回合的关系：开场白不计入 total_rounds，不触发记忆压缩计数，不触发进化触发器。

设计优势：兼容酒馆角色卡生态（first_mes 是社区标准），玩家一进入游戏即有氛围，消除"空白恐惧"。未来可通过插件钩子 on_session_start 扩展自定义开场白逻辑。

3. 世界书检索：引擎的纯代码模块对玩家文本进行关键词匹配，从当前角色卡对应的 _lorebook.json 中提取匹配条目。
4. 上下文打包：按以下顺序拼接 Prompt：
· 当前激活的预设破限（system_prompt）
· 当前角色卡设定（名字、描述、性格、提示词）
· 世界书匹配条目
· 当前 GameState 文本化（状态栏描述，仅包含已确认的数值）
· working_memory.json 中的摘要链（最近3条历史摘要）
· recent_log.txt 中的最近10轮已确认对话原文

步骤4.1：Token 预算检查与自动裁剪（v1.6）

在上下文打包完成后、发送 AI 请求前，引擎必须执行 Token 预算检查。

配置：system.json 中增加字段：

```json
{
  "max_context_tokens": 28672,
  "token_estimation_method": "char_ratio",
  "char_to_token_ratio": 0.5
}
```

max_context_tokens：模型上下文窗口的 80%（例如 DeepSeek-V3 的 32K 窗口，设为 28672）。
token_estimation_method：估算方法。char_ratio 为字符数比例法；tiktoken 为精确计数（需安装 tiktoken 库）。
char_to_token_ratio：字符数到 Token 的粗略换算比（中文约 0.5 token/字符，英文约 0.25 token/字符）。

裁剪策略（按优先级从低到高依次执行，每次裁剪后重新估算，直到总 Token 低于上限）：

| 步骤 | 裁剪目标 | 操作 | 用户感知 |
|------|----------|------|----------|
| 1 | 对话原文 | 将 recent_log.txt 从最近10轮降至最近5轮 | 透明 |
| 2 | 对话原文 | 将 recent_log.txt 从最近5轮降至最近3轮 | 透明 |
| 3 | 自动摘要 | 将 working_memory.json 从3条降至1条 | 透明 |
| 4 | 手动记忆（非固定） | 从旧到新删除 pinned: false 条目 | 日志记录 |
| 5 | 手动记忆（固定） | 绝不动 pinned: true；若仍超限，记录警告并通知玩家 | 前端提示 |

代码骨架：

```python
def enforce_token_budget(prompt: str, max_tokens: int, ratio: float = 0.5) -> str:
    """检查并裁剪 Prompt 以符合 Token 预算"""
    estimated = int(len(prompt) * ratio)
    if estimated <= max_tokens:
        return prompt
    # 按裁剪策略逐步执行...
    # 返回裁剪后的 prompt
```

与记忆管理器的协作：Token 预算检查不修改任何持久化文件。recent_log、working_memory、manual_memory 的裁剪仅影响本轮 Prompt 构建，磁盘文件保持不变。

5. AI 生成：调用大模型 API。Prompt 中明确指令：“你是{角色名}。请自然地进行角色扮演，像写小说一样推进剧情。如果你认为当前剧情导致了明显的状态变化（例如受伤、获得物品、好感度变化），你可以在回复的最末尾，用一个 Markdown 代码块（```json）来描述这些变化。如果你不确定，或者剧情没有明显变化，完全可以不写。叙事本身是第一位的。”
6. 生成草稿：解析器引擎接收 AI 返回的原始文本，采用三段式策略提取状态变更（详见第十节 10.1），组装为 Draft 对象（包含 draft_id、raw_response、parsed 三部分），保存至 drafts/draft_xxx.json（自动编号递增）。触发 on_draft_created 钩子。

步骤6.1：AI 叙事的世界书二次检索（v1.6）

在解析器提取 narrative 后，引擎对 AI 生成的叙事文本执行一次额外的世界书关键词匹配。

检索范围：仅检索 narrative 字段（纯文本部分），不检索 state_changes。

匹配结果处理：
1. 将本次匹配到的条目与步骤3（玩家输入检索）的结果做差集。
2. 仅保留"AI 叙事中新触发的、玩家输入中未出现的"条目。
3. 这些新条目不注入当前回合，而是暂存到会话内存中。
4. 下一回合的上下文打包（步骤4）时，在世界书段落的顶部追加新条目，附带标记：【新解锁的世界信息（由上回合剧情触发）】：{条目名称}：{条目内容}

设计优势：让世界书的揭示变为"双向探索"——玩家的主动选择和 AI 的叙事推进都能逐步揭开世界，极大增强探索感。二次检索仅对 narrative 文本执行关键词匹配，性能开销极小。

7. 预览与待确认：前端展示最新草稿的 narrative 文本。此时游戏状态尚未更新，历史档案馆尚未写入。系统进入“待确认态”。

7.1. 流式渲染与打字机效果

在草稿预览阶段，前端必须实现以下交互标准：

1. 流式展示：AI 生成文本时，若 API 支持流式输出（如 DeepSeek/GPT 的 stream=True），前端应逐字/逐句渲染 narrative 文本。

2. 打字机效果：文本出现时带有平滑的逐字动画，速度可配置（默认 30ms/字）。用户可随时点击跳过动画直接显示全文。

3. 生成中状态指示：非侵入式加载指示器（闪烁光标或脉动圆点）。

4. 中断生成：提供"停止生成"按钮（或 /stop 指令），已生成部分自动保存为草稿。
8. 用户决策分支：
· 用户输入 /roll → 回到步骤5，生成新草稿并追加保存，旧草稿保留。
· 用户输入 /select N → 进入步骤9（提交），选中指定编号的草稿。
· 用户输入其他普通文本（不以 / 开头）→ 自动等同于 /select latest，先提交最新草稿，再将此文本作为下一回合的玩家输入。
9. 提交与烘焙：
a. 触发 on_draft_selected 钩子，传入被选中的草稿数据。
b. 将选中草稿的原始文本追加写入 /history/full_log.txt。
c. 刷新 /context/recent_log.txt（保留最近10轮已确认对话原文）。
d. 调用 状态管理器.apply_state_changes() 更新 state.sav。
e. 草稿清理：删除 /drafts/ 下未被收藏的草稿文件。已被 /draft save 标记的草稿移动到 /context/saved_drafts/。
f. 执行进化触发器扫描：按 rules.json 中规则顺序依次检查，执行满足条件的动作。若阶段（phase）发生变化，触发 on_phase_change 钩子。
g. 检查记忆压缩条件：若当前会话总轮数
g. 记忆压缩检查（双层）：
   - 若当前会话总轮数达到 10 的倍数，触发轻量压缩：读取 compression_prompt_light.txt 模板，将最近10轮对话压缩为≤200字摘要，追加到 /history/full_memory.json，条目标记 compression_type: "light"。
   - 若当前会话总轮数
g. 记忆压缩检查（双层）：
   - 若当前会话总轮数达到 10 的倍数，触发轻量压缩：读取 compression_prompt_light.txt 模板，将最近10轮对话压缩为≤200字摘要，追加到 /history/full_memory.json，条目标记 compression_type: "light"。
   - 若当前会话总轮数达到 50 的倍数，触发深度压缩：读取 compression_prompt_deep.txt 模板，将自上次深度压缩以来的所有对话（约50轮）压缩为≤2000字深度摘要，条目标记 compression_type: "deep"。
   - 完成后刷新 /context/working_memory.json：注入最近 1 条深度摘要 + 最近 3 条轻量摘要。
   - 触发 on_memory_compressed 钩子。
   - 完成后刷新 /context/working_memory.json：注入最近 1 条深度摘要 + 最近 3 条轻量摘要。
   - 触发 on_memory_compressed 钩子。
h. 触发 on_round_end 钩子。
i. 更新 session_meta.json（递增 total_rounds，更新 last_saved_at）。
10. 循环：准备接收下一回合输入。
---
十、AI 强制契约白名单与预设破限
10.1 AI 可修改字段白名单

· AI 可修改字段（白名单）：hp， energy， goodwill， money， inventory， bg， emotion， cg
· AI 禁止修改字段（只读）：phase， max_hp
解析器引擎在提取 JSON 后，会丢弃任何不在白名单内的字段，仅保留合法变更。
10.2 AI 禁止修改字段
· 预设文件存放于 /configs/presets/ 目录。
· 玩家可通过 /preset [预设名] 指令热切换当前系统预设，无需重启引擎或重新加载角色。
· 切换后，下一轮对话将使用新预设。

预设破限市场接口（v1.5）：与插件市场类似，预设破限（/presets/）也可通过社区索引分享。未来 /market 指令将同时支持插件和预设的发现与安装。

10.3 预设热切换：/preset xxx

设计目的：给角色注入一个"导演意识"，在长对话中自我监控人设一致性。

模板预设（/configs/presets/meta_cognition_v4.txt）：
【元认知指令 - 角色自校正系统】
你是一名受过严格训练的方法派演员。在每次回复前执行自检：
1. 角色一致性检查：用词、句式、语气是否与角色匹配？
2. 状态同步检查：内部状态是否已更新？回应是否反映状态变化？
3. 剧情连贯性检查：是否记得之前的关键事件？
4. 偏离修正：上述任何一项未通过时，自然地、不被察觉地将话题拉回正轨。

加载方式：Kernelsoul 角色卡的 meta_cognition_prompt 字段优先；若未提供则使用此默认模板；可通过 /preset meta_cognition_v4 手动启用。

与角色 Prompt 的关系：角色 prompt 定义角色是什么，元认知 prompt 定义角色如何自我监控。二者在上下文打包时拼接：系统预设 → 角色 prompt → 元认知预设。

---
十一、防崩坏与容错机制
11.1 AI 输出稳定性兜底策略
当 AI 返回的文本中无法直接提取到有效的 JSON 状态变更时，解析器引擎采用以下三段式智能提取策略：
阶段 1：提取 Markdown JSON 代码块
```python
import re
import json
def extract_json_code_block(raw_text: str) -> dict | None:
“““从 Markdown ```json 代码块中提取 JSON“““
match = re.search(r'```json\s*\n(.*?)\n```'， raw_text， re.DOTALL)
if match:
try:
return json.loads(match.group(1))
except json.JSONDecodeError:
pass
return None
```
阶段 2：最大括号回溯法
```python
def extract_json_fallback(raw_text: str) -> dict | None:
“““从文本末尾向前扫描，提取最后一个完整 JSON 对象“““
last_brace = raw_text.rfind('}')
if last_brace == -1:
return None
depth = 0
start = -1
for i in range(last_brace， -1， -1):
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
阶段 3：自然语言简单规则提取
当以上两阶段均失败时，使用最简单的正则模式匹配，仅提取最明显的状态变化：
```python
def extract_from_natural_language(text: str) -> dict:
“““从自然语言中提取最明显的状态变化模式“““
changes = {}
# 伤害模式：受到/损失/扣除 + 数字 + 点 + 伤害/生命
damage_match = re.search(r'(?:受到|损失|扣除)[了]?(\d+)[点]?(?:伤害|生命)'， text)
if damage_match:
changes['hp'] = -int(damage_match.group(1))
# 获得物品模式：获得/捡起/拿到 + 物品名（最长20字符）
gain_match = re.search(r'(?:获得|捡起|拿到)[了]?(?:一个|一把|一件|一些)?(.{1，20})'， text)
if gain_match:
item = gain_match.group(1).strip()
if len(item) <= 20:
changes['inventory_add'] = [item]
return changes
```
分级容错策略汇总：
尝试次数 策略 用户感知
阶段 1 提取  ```json  代码块，校验 Schema 透明，无感
阶段 1 失败 使用最大括号回溯法，校验 Schema 透明，无感
阶段 2 失败 使用自然语言简单规则提取（仅伤害/获得物品模式） 透明。若仍无变更，前端可轻量提示“本回合无状态变化”
连续 2 回合解析均为空 自动切换为降级 Prompt（从 fallback_prompt.txt 读取），重新请求 AI；前端显示“正在重新生成…” 短暂等待
连续 3 回合解析仍为空 放弃状态变更提取，仅保留 narrative 文本作为纯剧情草稿；通知用户“本次 AI 返回格式异常，已生成纯文本剧情，可 /roll 重试” 明确提示
降级 Prompt 模板（/configs/fallback_prompt.txt）：
```
{原系统预设}
当前游戏状态：
{state_text}
最近对话历史：
{recent_log}
请作为{角色名}继续剧情。在回复末尾附上一个简短的 JSON 标记，格式如下：
{“hp“:0，“energy“:0}
只需修改有变化的数值。不要添加解释。
```
11.2 常规容错机制
1. AI 契约乱码容错：try...except 保护整个解析过程。任何解析失败都不会导致引擎崩溃，仅按分级策略降级处理。
2. 数值封顶保护：状态管理器内置钳制逻辑。单次伤害/恢复上限可在 rules.json 中配置（如 max_damage_per_turn: 50）。任何超出上限的变更自动截断。
3. 世界书缺失容错：若当前角色卡找不到对应 _lorebook.json 文件，引擎记录一条日志并跳过世界书检索步骤，继续正常运行。
4. 美术资源降级：UI 观察者在渲染前检查所需图片文件是否存在。若缺失，自动降级为纯文字模式，不报错。
5. 跨角色切换的上下文隔离（极重要）：
· 当玩家执行 /character 或 /load 切换角色时，引擎在读取新角色数据前，必须执行一次“强制内存重置”：
· 销毁当前 GameState 实例。
· 清空 context/ 下所有文件（包括 recent_log.txt、working_memory.json 和整个 drafts/ 文件夹）。
· 解绑当前 PathResolver，创建新实例绑定新角色/会话。
· 然后从新角色卡中的 initial_state 加载默认值，创建全新的 GameState。
· 绝对禁止将旧角色卡的世界观碎片、对话历史或草稿数据带入新角色的提示词中。
6. 不存在的路径自动创建：PathResolver 在初始化时，以及在任何写操作前，都会自动调用 os.makedirs(...， exist_ok=True) 确保目录存在。如果玩家在 /newgame 后直接开始聊天，但文件夹尚未生成，引擎不会报错闪退，而是自动创建所有必要目录和初始文件。
7. 草稿区异常保护：
· 若提交后清空 drafts/ 时发生异常（如文件被外部进程锁定），引擎记录错误日志，但不中断游戏流程。旧草稿将在下次提交成功时一并清理。
· 若用户在没有草稿的情况下输入 /roll 或 /select，引擎返回友好提示：“当前没有待确认的草稿”，不执行任何操作。
8. 插件异常隔离（v1.3 新增）：插件管理器在触发每个钩子时，用 try...except 包裹回调执行。任何插件抛出的异常都会被捕获并记录日志，绝不会导致主循环崩溃或影响其他插件的正常运行。
11.3 存档版本管理
session_meta.json 中的 data_version 字段用于标记存档格式版本。当未来数据结构升级时，引擎可据此执行迁移：
```python
def load_state_with_migration(path_resolver) -> GameState:
“““加载存档，若版本不匹配则自动迁移“““
meta = json.load(open(path_resolver.get_meta_file()， encoding='utf-8'))
version = meta.get(“data_version“， 1)
raw_state = json.load(open(path_resolver.get_state_file()， encoding='utf-8'))
if version == 1:
# 当前版本，直接加载
return GameState(**raw_state)
elif version == 2:
# 未来 v2 示例：背包结构升级
raw_state = migrate_v1_to_v2(raw_state)
return GameState(**raw_state)
else:
raise ValueError(f“不支持的数据版本: {version}“)
def migrate_v1_to_v2(raw: dict) -> dict:
“““v1 -> v2 迁移示例：将 inventory 从 List[str] 转为 List[Item]“““
if “inventory“ in raw and isinstance(raw[“inventory“]， list) and len(raw[“inventory“]) > 0:
if isinstance(raw[“inventory“][0]， str):
raw[“inventory“] = [{“name“: item， “quantity“: 1} for item in raw[“inventory“]]
return raw
```

11.4 死亡与失败状态处理（v1.6）

触发条件：状态管理器在每轮提交（步骤9d）后，检测 GameState.hp <= 0。

处理流程：
1. 状态锁定：hp 锁定为 0；energy、inventory、goodwill、money 锁定当前值；bg、emotion、cg 仍可由 AI 修改（用于死亡场景描述）；phase 允许设为特殊值（如 -1 表示死亡结局）。
2. 自动记忆注入：引擎向 manual_memory.json 追加系统级记忆条目，内容为"【系统记录】角色于第{N}轮死亡。"，pinned: true，source: "system"。
3. 规则触发：进化触发器检查 rules.json 中是否存在 hp == 0 的死亡规则，执行对应动作（如 set_phase: -1）。
4. AI 提示词注入：下一轮上下文打包时，在系统预设末尾追加"【重要：角色已死亡。请以终局叙事的方式描述角色的结局与后日谈。在回复末尾提示玩家可以输入 /newgame 开始新的周目，或输入 /load 回溯到之前的存档。】"
5. 玩家可选操作：继续输入文本（AI 以"后日谈"模式回应）；/newgame 开始新周目；/load [角色名] [会话ID] 加载存档；若有多世界线快照，可通过 /branches 回溯分支点。

设计原则：死亡不是冰冷的"游戏结束"，而是有仪式感的叙事节点。锁定的状态防止 AI 在死亡后继续操作数值，但保留叙事空间让玩家体面地结束故事。

---
十二、记忆压缩提示词模板
12.1 模板存放位置 [v2.3]

/configs/compression_prompt_light.txt — 轻量压缩模板（10轮，200字上限）
/configs/compression_prompt_deep.txt — 深度压缩模板（50轮，2500字上限）
/configs/compression_prompt_merge.txt — 轻量摘要合并模板 [v2.3.1]
/configs/compression_prompt_epic.txt — 史诗压缩模板（200轮，5000字上限）[v2.3.1]

12.2 模板内容 [v2.3]

**12.2.1 轻量压缩模板**（`/configs/compression_prompt_light.txt`）：

```
你是一个游戏叙事摘要生成器。请将以下对话历史压缩为一段第三人称摘要。

要求：
1. 字数严格限制在200字以内。
2. 仅保留最核心的事件和状态变化。
3. 输出纯中文，不要任何标记。

对话历史：
{chat_history}

摘要：
```

**12.2.2 深度压缩模板**（`/configs/compression_prompt_deep.txt`）：

```
你是一个游戏叙事深度摘要生成器。请将以下较长对话历史压缩为详细的第三人称摘要。

要求：
1. 字数限制在2000字以内。
2. 必须保留：
   - 核心事件链及其因果关系
   - 角色态度和关系的演变轨迹
   - 重要物品的获得与失去
   - 关键状态变化（受伤、情绪转折等）
   - 重要世界设定的揭示
3. 按时间顺序组织，保持叙事连贯性。
4. 输出纯中文，不要任何标记。

对话历史：
{chat_history}

深度摘要：
```

**12.2.3 史诗压缩模板**（`/configs/compression_prompt_epic.txt`）：

```
你是一个游戏叙事史诗摘要生成器。请将以下多条深度摘要合并为一份宏观叙事总结。

要求：
1. 字数限制在5000字以内。
2. 必须提炼：
   - 核心主题与主线脉络
   - 角色弧光与关系网络演变
   - 关键物品的地位变化
   - 未解伏笔与悬念
3. 按时间顺序组织，保持叙事连贯性。
4. 输出纯中文，不要任何标记。

深度摘要集合：
{combined_deep_summaries}

史诗摘要：
```

## 三层压缩架构总览

| 层级 | 触发频率 | 输入来源 | 输出字数 | 用途 |
|------|---------|---------|---------|------|
| 轻量 | 每10轮 | 最近10轮原文 | ~200字 | 近期细节 |
| 深度 | 每50轮 | 轻量摘要合并(分层模式) 或 原文直接压缩(回退) | ~2500字 | 中程叙事弧 |
| 史诗 | 每200轮 | 深度摘要合并 | ~5000字 | 全局故事脉络、角色弧光、主题提炼 |

## 分层压缩原理

50轮对话原文 (可能22000+字，超出上下文窗口)
 -> 分5批,每批10轮 -> 5次轻量压缩(~200字 each)
 -> 拼接轻量摘要 -> AI合并 -> 深度摘要(~2500字)

200轮对话 -> 4条深度摘要 -> 拼接 -> AI合并 -> 史诗摘要(~5000字)

关键差异:
- 旧方案: 50轮原文 -> 直接生成深度摘要 (可能超窗口)
- 新方案: 50轮 -> 5份轻量摘要 -> 拼接 -> 合并为深度摘要

## 上下文注入规则

上下文 = 最新1条史诗摘要 + 最新1条深度摘要 + 最新3条轻量摘要 + 最近10轮原文 + 手动记忆锚点(优先级最高)

## 深度压缩实现

分层合并模式(优先): 当有>=3条轻量摘要时,收集并拼接为分段时间线,使用compression_prompt_merge.txt调AI合并
原文回退模式: 轻量摘要不足(<3条)时,从full_log.txt原文使用compression_prompt_deep.txt直接压缩

## 安全截断机制

_safe_truncate(text, max_chars):
- 在句号/问号/感叹号/换行处截断
- 截断位置不能太靠前 (至少保留max_chars的80%)
- 实在找不到合适位置则硬截

## 常量定义

LIGHT_INTERVAL=10, DEEP_INTERVAL=50, EPIC_INTERVAL=200
LIGHT_MAX_CHARS=200, DEEP_MAX_CHARS=2500, EPIC_MAX_CHARS=5000

## working_memory.json 结构

{
  "epic_summary": { "compression_id":1, "type":"epic", "round_range":"1-200", "summary":"..." },
  "deep_summaries": [ { "compression_id":4, "type":"deep", "round_range":"151-200", "summary":"..." } ],
  "light_summaries": [ { "compression_id":18, "type":"light", "round_range":"181-190", "summary":"..." } ]
}

## 新增提示词模板

compression_prompt_merge.txt: 用于将多条轻量摘要合并为深度摘要。占位符 {combined_summaries}
compression_prompt_epic.txt: 用于将多条深度摘要合并为史诗摘要。占位符 {combined_deep_summaries}，要求提炼核心主题/主角弧光/关系网络/关键物品/未解伏笔

================================================================================

12.3 工作记忆构建规则 [v2.3.1]

上下文打包时，从 /history/full_memory.json 的摘要链中筛选注入 working_memory.json：

```python
def build_working_memory(full_memory: dict) -> dict:
    entries = full_memory.get("entries", [])
    epic = [e for e in entries if e.get("compression_type") == "epic"]
    deep = [e for e in entries if e.get("compression_type") == "deep"]
    light = [e for e in entries if e.get("compression_type") == "light"]
    return {
        "epic_summary": epic[-1] if epic else None,         # 最近 1 条史诗摘要
        "deep_summary": deep[-1] if deep else None,         # 最近 1 条深度摘要
        "light_summaries": light[-3:] if len(light) >= 3 else light  # 最近 3 条轻量摘要
    }
```

史诗摘要提供全局故事脉络与角色弧光（5000字级），深度摘要提供中程叙事弧（2500字级），轻量摘要提供近期细节（200字级）。

12.4 full_memory.json 条目结构更新 [v2.3.1]

每个摘要条目包含 `compression_type` 字段，区分压缩类型（"light" | "deep" | "epic"）：

```json
{
  "compression_id": 5,
  "compression_type": "light",
  "round_range": "41-50",
  "summary": "...",
  "timestamp": "2026-06-29T15:30:00Z"
}
```

12.5 三层压缩架构总览 [v2.3.1]

| 层级 | 触发频率 | 输入来源 | 输出字数 | 用途 |
|------|---------|---------|---------|------|
| 轻量 | 每10轮 | 最近10轮原文 | ~200字 | 近期细节 |
| 深度 | 每50轮 | 轻量摘要合并(分层模式) 或 原文直接压缩(回退) | ~2500字 | 中程叙事弧 |
| 史诗 | 每200轮 | 深度摘要合并 | ~5000字 | 全局故事脉络、角色弧光、主题提炼 |

12.6 分层压缩原理 [v2.3.1]

50轮对话原文（可能22000+字，超出上下文窗口）
  → 分5批，每批10轮 → 5次轻量压缩（~200字 each）
  → 拼接轻量摘要 → AI合并 → 深度摘要（~2500字）

200轮对话 → 4条深度摘要 → 拼接 → AI合并 → 史诗摘要（~5000字）

关键差异：
- 旧方案：50轮原文 → 直接生成深度摘要（可能超窗口）
- 新方案：50轮 → 5份轻量摘要 → 拼接 → 合并为深度摘要

12.7 上下文注入规则 [v2.3.1]

上下文 = 最新1条史诗摘要 + 最新1条深度摘要 + 最新3条轻量摘要 + 最近10轮原文 + 手动记忆锚点（优先级最高）

12.8 深度压缩实现 [v2.3.1]

分层合并模式（优先）：当有≥3条轻量摘要时，收集并拼接为分段时间线，使用 compression_prompt_merge.txt 调 AI 合并。
原文回退模式：轻量摘要不足（<3条）时，从 full_log.txt 原文使用 compression_prompt_deep.txt 直接压缩。

12.9 安全截断机制 [v2.3.1]

_safe_truncate(text, max_chars)：
- 在句号/问号/感叹号/换行处截断
- 截断位置不能太靠前（至少保留 max_chars 的 80%）
- 实在找不到合适位置则硬截

12.10 常量定义 [v2.3.1]

LIGHT_INTERVAL=10，DEEP_INTERVAL=50，EPIC_INTERVAL=200
LIGHT_MAX_CHARS=200，DEEP_MAX_CHARS=2500，EPIC_MAX_CHARS=5000

12.11 working_memory.json 结构 [v2.3.1]

```json
{
  "epic_summary": { "compression_id":1, "type":"epic", "round_range":"1-200", "summary":"..." },
  "deep_summaries": [ { "compression_id":4, "type":"deep", "round_range":"151-200", "summary":"..." } ],
  "light_summaries": [ { "compression_id":18, "type":"light", "round_range":"181-190", "summary":"..." } ]
}
```

十三、插件系统设计规范
13.1 设计目标与极简安装
1. 开放生态：允许第三方开发者为引擎编写功能扩展，无需修改核心代码。
2. 安全隔离：插件在受限的沙盒环境中运行，不能随意访问文件系统或破坏引擎稳定性。
3. 深度集成：通过生命周期钩子，插件可以介入游戏流程的各个关键节点。

13.1.1 极简安装设计

插件安装遵循"放入即启用"原则：

1. 用户将插件文件夹复制到 /plugins/ 目录。
2. 引擎下次启动时自动发现并加载。
3. 若引擎已在运行，用户可通过 /plugin reload [插件ID] 热加载。
4. 插件依赖的 Python 包在 manifest.json 的 pip_dependencies 中声明，引擎首次加载时自动 pip install（需用户确认）。

manifest 新增字段：pip_dependencies、min_engine_version、homepage、license。
13.2 插件清单规范（manifest.json）
每个插件必须在其根目录下包含 manifest.json：
```json
{
“id“: “stats_tracker“，
“name“: “统计追踪面板“，
“version“: “1.0.0“，
“author“: “developer_name“，
“description“: “记录并展示玩家在所有周目中的死亡次数、对话轮数等统计信息“，
“engine_version“: “>=1.4.0“，
“dependencies“: []，
“hooks“: [
“on_session_start“，
“on_round_end“，
“on_session_end“
]，
“permissions“: [
“read_state“，
“write_file“，
“read_history“
]
}
```
字段说明：
字段 类型 说明
id string 唯一标识符，必须与插件文件夹名一致
name string 插件显示名称
version string 插件版本号，遵循语义化版本规范
author string 作者署名
description string 简要描述插件功能
engine_version string 要求的引擎最低版本
dependencies list 依赖的其他插件 ID 列表（可选）
hooks list 注册的生命周期钩子列表
permissions list 申请的权限列表（见权限表）
13.3 权限系统
权限名 级别 允许的操作
read_state 低 读取当前 GameState 的快照（不可修改）
write_state 高 直接修改 GameState。需用户在首次加载时明确确认。
read_history 低 读取 /history/ 下的对话记录和摘要
write_file 中 在 /plugins/<plugin_id>/ 专属目录内自由读写文件
network 高 发起外部网络请求。需用户首次使用时手动批准。
ui_inject 中 向前端界面注入自定义 HTML 面板、按钮或样式
13.4 生命周期钩子定义
```python
class PluginHooks:
“““插件可注册的所有生命周期钩子。
每个钩子均为异步方法，默认实现为空（无操作）。
插件只需覆写其关心的钩子即可。
“““
async def on_engine_start(self， config: dict) -> None:
“““引擎启动时触发。config 包含 system.json 的完整配置。“““
pass
async def on_session_start(self， character: str， session: str， state: GameState) -> None:
“““进入某个会话时触发（含新游戏和加载存档）。“““
pass
async def on_user_input(self， text: str) -> str | None:
“““
用户输入拦截钩子。
返回 str 则替换用户输入文本继续流程。
返回 None 则保持原输入不变。
可用于实现自定义指令或输入过滤。
“““
pass
async def on_draft_created(self， draft: dict) -> None:
“““新草稿生成后触发。draft 包含 narrative 和 state_changes。“““
pass
async def on_draft_selected(self， draft: dict) -> None:
“““用户确认选择某个草稿后触发。“““
pass
async def on_round_end(self， round_num: int， state: GameState) -> None:
“““每一轮完整结束后触发（提交并写入历史后）。“““
pass
async def on_memory_compressed(self， summary: str) -> None:
“““记忆压缩完成时触发。summary 为新生成的摘要文本。“““
pass
async def on_phase_change(self， old_phase: int， new_phase: int) -> None:
“““进化阶段发生变化时触发。“““
pass
async def on_session_end(self， character: str， session: str) -> None:
“““离开会话时触发（切换角色或关闭引擎前）。“““
pass
async def on_engine_stop(self) -> None:
“““引擎关闭前触发。可用于保存插件状态、清理资源。“““
pass
```
13.5 插件管理器实现
```python
import importlib
import json
import os
class PluginManager:
“““插件管理器：发现、验证、加载插件，管理生命周期钩子“““
def __init__(self， plugin_dir: str = “./plugins“):
self.plugin_dir = plugin_dir
self.plugins: dict[str， dict] = {}
# 初始化所有钩子的回调列表
self.hooks: dict[str， list] = {
hook: [] for hook in dir(PluginHooks)
if hook.startswith(“on_“)
}
def discover_plugins(self):
“““扫描插件目录，验证并加载所有有效插件“““
if not os.path.exists(self.plugin_dir):
os.makedirs(self.plugin_dir， exist_ok=True)
return
for folder in os.listdir(self.plugin_dir):
manifest_path = os.path.join(self.plugin_dir， folder， “manifest.json“)
if not os.path.exists(manifest_path):
continue
with open(manifest_path， encoding='utf-8') as f:
manifest = json.load(f)
# 权限审查：高危权限记录日志
permissions = manifest.get(“permissions“， [])
if “write_state“ in permissions:
print(f“[插件] {manifest['name']} 申请了 write_state 权限，需用户确认“)
if “network“ in permissions:
print(f“[插件] {manifest['name']} 申请了 network 权限，需用户批准“)
# 动态导入插件模块
module = importlib.import_module(f“plugins.{folder}“)
self.plugins[manifest[“id“]] = {
“manifest“: manifest，
“module“: module，
“enabled“: True
}
# 注册钩子回调
for hook_name in manifest.get(“hooks“， []):
if hasattr(module， hook_name):
self.hooks[hook_name].append(getattr(module， hook_name))
print(f“[插件] 已加载: {manifest['name']} v{manifest['version']}“)
async def fire_hook(self， hook_name: str， *args， **kwargs):
“““异步触发指定钩子的所有已注册回调“““
for callback in self.hooks.get(hook_name， []):
try:
await callback(*args， **kwargs)
except Exception as e:
print(f“[插件] 钩子 {hook_name} 执行异常: {e}“)
# 隔离异常，不影响引擎和其他插件
def reload_plugin(self， plugin_id: str):
“““热重载指定插件“““
if plugin_id not in self.plugins:
print(f“[插件] 未找到插件: {plugin_id}“)
return
plugin_info = self.plugins[plugin_id]
manifest = plugin_info[“manifest“]
# 从钩子列表中移除旧回调
for hook_name in manifest.get(“hooks“， []):
old_func = getattr(plugin_info[“module“]， hook_name， None)
if old_func in self.hooks[hook_name]:
self.hooks[hook_name].remove(old_func)
# 重新加载模块
new_module = importlib.reload(plugin_info[“module“])
self.plugins[plugin_id][“module“] = new_module
# 注册新回调
for hook_name in manifest.get(“hooks“， []):
if hasattr(new_module， hook_name):
self.hooks[hook_name].append(getattr(new_module， hook_name))
print(f“[插件] {plugin_id} 已重新加载“)
```
13.6 插件沙箱规则
1. 文件系统隔离：插件只能写入 /plugins/<plugin_id>/ 目录。读取权限仅限于该目录和 /saves/（需 read_history 权限）。路径管理器不会向插件暴露系统绝对路径。
2. 异常隔离：如 10.2 节第 8 条所述，插件抛出的任何异常由引擎静默捕获，不影响主循环。
3. 网络约束：申请了 network 权限的插件，引擎在首次触发网络请求时需弹窗获取用户批准。用户可随时通过 /plugin disable 撤销。
4. 状态修改约束：申请了 write_state 权限的插件，引擎在加载时需用户明确确认。建议此类插件在修改状态前自行实现二次确认逻辑。
13.7 官方示例插件：统计追踪器
/plugins/example_stats_tracker/__init__.py：
```python
“““统计追踪器：记录玩家在所有会话中的关键数据。
演示了如何使用 on_session_start、on_round_end 钩子，
以及 write_file 权限进行数据持久化。
“““
import json
import os
# 插件私有数据
stats_file = os.path.join(“plugins“， “example_stats_tracker“， “data.json“)
stats = {“total_deaths“: 0， “total_rounds“: 0， “sessions_played“: 0}
def _load_stats():
global stats
if os.path.exists(stats_file):
with open(stats_file， “r“， encoding=“utf-8“) as f:
stats = json.load(f)
def _save_stats():
os.makedirs(os.path.dirname(stats_file)， exist_ok=True)
with open(stats_file， “w“， encoding=“utf-8“) as f:
json.dump(stats， f， indent=2， ensure_ascii=False)
# 引擎启动时加载已有统计数据
_load_stats()
async def on_session_start(character， session， state):
“““新会话开始时递增计数“““
stats[“sessions_played“] += 1
_save_stats()
async def on_round_end(round_num， state):
“““每轮结束时更新总轮数，并检测死亡“““
stats[“total_rounds“] = round_num
if state.hp <= 0:
stats[“total_deaths“] += 1
_save_stats()
```

13.8 插件市场接口规划（未来扩展）

13.8.1 市场索引格式

/plugins/market_index.json：

```json
{
  "name": "官方插件市场",
  "url": "https://plugins.example.com/index.json",
  "plugins": [
    {"id": "stats_tracker", "name": "统计追踪面板", "version": "1.0.0", "author": "dev_name", "description": "..."}
  ]
}
```

13.8.2 预留指令：/market list、/market install、/market update

---
十四、可选扩展：多世界线快照
当前设计为“回合内暂存，确认后删除”。未来可升级为分支剧情树系统：
· 保留分支：将 /drafts/ 中未被用户选择的草稿不删除，而是自动移动到 /history/branches/ 目录下，按分支点和时间戳编目。
· 回溯指令：提供 /branches 指令列出所有可用分支点，提供 /branch [分支ID] 指令让玩家回到历史某一点，从另一个草稿重新开始，创建一个新的平行世界线会话。
· 可视化分支树：在前端界面中展示分支历史的树状图，让玩家直观看到自己的选择如何影响了故事走向。
· 此扩展不在 MVP 范围内，但底层数据结构（草稿文件格式、双轨制存档）已完全兼容，无需破坏性修改即可实现。

分支树可视化规划

1. 分支树面板：以树状图展示所有分支点，显示玩家输入摘要、创建时间、活跃分支高亮标记。
2. 回溯操作：点击历史节点可预览剧情，提供"从此分支点开始新世界线"按钮。
3. 分支对比：选择两个分支节点后高亮显示状态差异（HP、背包等）。

---
十五、MVP 开发优先级指导（绝对严格的顺序）
1. 第一阶段：地基
· 实现 PathResolver 类，确保所有路径动态拼接和目录自动创建。
· 实现 GameState 数据类，测试 JSON 序列化/反序列化。
· 实现状态管理器基础读写 state.sav。
· 实现 session_meta.json 的读写和 data_version 版本标记。
2. 第二阶段：连 AI 契约与草稿
· 接入 API（DeepSeek / GPT / 本地 Ollama），构建基础提示词。
· 实现解析器引擎的三段式提取策略（Markdown JSON → 最大括号回溯 → 自然语言规则）。
· 实现草稿文件生成、保存至 /drafts/。
· 实现 /roll、/select、/drafts 指令及自动提交逻辑。
· 测试“打我”场景：AI 是否能正确返回可选 JSON，解析器是否能正确提取并扣血。
3. 第三阶段：检索器测试
· 在代码中写死一条世界书关键字（如“天台”），看引擎能否正确提取并拼装世界书设定条目到 Prompt 中。
4. 第四阶段：进化测试
· 在 rules.json 中写入简单规则（如好感度 >50 则 phase=2）。
· 测试引擎在提交后自动检测阈值并强制修改 phase 字段。
5. 第五阶段：记忆压缩
· 实现双轨制写入：full_log.txt 追加，recent_log.txt 刷新。
· 实现 50 轮触发压缩逻辑，调用 AI 生成摘要。
· 实现摘要链管理（full_memory.json 追加，working_memory.json 更新最近3条）。
6. 第六阶段：多角色与系统指令测试
· 在 /saves/ 手动创建两个角色（demon_hotel 和 cyber_elf）的文件夹及初始存档。
· 测试 /character、/newgame、/load 指令。
· 重点验证：切换角色时，引擎是否执行了强制内存重置，AI 的回复语调是否随之改变。
· 重点验证：旧角色的对话碎片是否被彻底隔离，不会污染新角色的上下文。
7. 第七阶段：插件系统
· 实现 CharacterStateManager（4.3 节）。
· 实现 Kernelsoul 角色卡扩展字段的加载和初始化。
· 实现双层规则执行顺序（全局规则 → 角色规则）。

· 实现 PluginManager 类：扫描、验证、加载、钩子注册。
· 实现沙箱隔离和异常捕获。
· 实现 /plugin list/reload/enable/disable 指令。
· 编写官方示例插件（统计追踪器）进行端到端测试。
8. 第八阶段：UI 挂载
· 将命令行黑框替换为 Pygame 或 Web 界面。
· 实现草稿预览（展示 narrative）、草稿列表、状态栏显示。
· 对接 UI 观察者，实现图片缺失自动降级纯文本。
· 实现决策溯源面板（7.1 节追加内容）。
· 实现 /debug on/off 指令。
· 状态监视器支持角色状态变量实时展示。
---
十六、开发环境与底层基建
· 编程语言：Python 3.10+。推荐使用 asyncio 防止 API 请求阻塞主循环。
· 大模型方案：
· 线上：DeepSeek API、OpenAI GPT API。
· 本地：Ollama（如 Qwen2.5-14B、Llama 3 等）。
· 核心策略：
· 所有文件路径通过 PathResolver 动态拼接，禁止硬编码绝对路径。
· 任何对状态（state.sav）或历史（full_log.txt）的写入操作，仅在用户确认提交草稿后发生。草稿阶段绝不修改已确认数据。

数据主权设计原则（v1.5）

1. 所有数据存储在本地，不依赖任何云端存储。
2. 开放格式：存档、日志、角色卡均为人类可读的纯文本格式。
3. 一键导出/导入：/export [会话ID] 和 /import [路径] 指令，打包为 ZIP。
4. 无强制联网：本地 Ollama 可完全替代线上 API。
5. 无内容审查：引擎本身不包含内容过滤逻辑。

---

---

## 第五部分：生态扩展路线图 [v2.3]

*本部分规划 Kernelsoul Character OS 在游戏引擎集成、开发工具、SDK 分发等方向的扩展路径。所有接口均为设计预留，不阻塞 MVP。*

---

十七、Unity / Unreal 集成

### 17.1 集成架构

Kernelsoul 引擎核心保持 Python 独立运行，通过进程间通信（gRPC 或 WebSocket）向游戏引擎暴露能力。

| 方案 | 描述 | 推荐场景 |
|------|------|----------|
| **gRPC 服务** | Python 引擎作为独立进程，gRPC 双向流 | 生产环境，跨语言 |
| **WebSocket** | 引擎启动 WebSocket 服务端 | 快速原型，Web 友好 |
| **Python.NET 嵌入** | Unity 直接调用 Python 运行时 | 低延迟需求场景 |

**推荐路径**：gRPC 服务（语言无关、性能高、支持双向流）。

### 17.2 gRPC API 规范

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
  map<string, string> game_context = 3; // 游戏世界状态
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
    public DecisionPanel decisionPanel; // 决策溯源
}

public class KernelsoulAnimationTrigger : MonoBehaviour {
    public KernelsoulNPC npc;
    // 监听 v4.decision → 匹配 force_tone/force_emotion → 触发动画
}
```

### 17.4 预制组件

| 组件 | 功能 |
|------|------|
| `KernelsoulNPC` | 挂载到 GameObject，管理角色生命周期 |
| `KernelsoulDialogueUI` | 自动显示对话文本和决策溯源面板 |
| `KernelsoulAnimationTrigger` | 将 `force_tone`/`force_emotion` 映射到动画状态机 |
| `KernelsoulMemoryInspector` | 调试面板，实时显示角色内部状态和规则触发 |

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

十八、Kernelsoul 角色创作工作台

### 18.1 定位

独立 Web 编辑器，创作者用 DSL 或自然语言生成 Kernelsoul 角色卡，导出为游戏资产。

### 18.2 功能清单

| 功能 | 说明 |
|------|------|
| 自然语言输入 | 输入角色描述 → RuleCompiler 生成 DSL 预览 |
| DSL 编辑器 | 语法高亮、实时校验、错误行号提示 |
| JSON 规则可视化 | 表格/图形化编辑，双向同步 DSL |
| 变量监视器 | 实时查看 `character_state` 变化 |
| 对话测试面板 | 输入玩家文本，查看 AI 响应和触发的规则 |
| 一键导出 | 角色文件夹（.dsl + .json + .txt）→ 游戏资产 |
| 版本控制 | 角色卡变更历史，支持回滚 |

### 18.3 游戏内热加载

开发者在 Unity/Unreal 中指定角色文件夹路径，`KernelsoulNPC` 组件监听文件变化，自动重新编译 DSL 并热重载角色，无需重启游戏。

---

十九、Kernelsoul 对话 SDK

### 19.1 定位

将 Kernelsoul 引擎封装为 `pip install kernelsoul-character-os`，游戏开发者一行代码接入。

### 19.2 核心接口

```python
from kernelsoul import KernelsoulSession

session = KernelsoulSession(char_id="innkeeper", session_id="session_01")
response = session.send("你好，旅人。")

# response: {
#   "dialogue": "欢迎来到我的旅馆...",
#   "actions": [...],
#   "state_changes": {...},
#   "decisions": [...],
#   "character_state": {"mood": 3, "trust_player": 25}
# }
```

### 19.3 pip 包结构

```
kernelsoul-character-os/
├── v4/
│   ├── engine.py       # KernelsoulSession 主类
│   ├── compiler.py     # DSLCompiler
│   ├── state_manager.py  # CharacterStateManager
│   ├── rules.py        # EvolutionTrigger
│   ├── memory.py       # MemoryManager（双层压缩）
│   ├── file_service.py # FileService
│   └── bridge.py       # AIBridge
├── pyproject.toml
└── README.md
```

### 19.4 内置能力（零配置）

- 双层记忆压缩（10轮轻量 + 50轮深度）
- 三段式 JSON 容错
- 死亡状态处理
- 进化规则执行
- 手动记忆锚点

---

二十、其他生态扩展

### 20.1 Godot / 自定义引擎集成

Kernelsoul 引擎的 gRPC API 天然支持任何语言。Godot（GDScript/C#）通过 gRPC 客户端调用，自定义 C++ 引擎通过 gRPC C++ SDK 接入。

### 20.2 模组工具

Kernelsoul 引擎编译为独立可执行文件（PyInstaller），模组作者放入游戏目录，通过标准输入/输出与游戏通信。

适用场景：
- Skyrim/Fallout（SKSE/F4SE 脚本调用外部进程）
- Minecraft（Forge/Fabric 模组调用 Python 进程）
- 任何支持外部进程调用的模组框架

**通信协议**（标准输入/输出，JSON 行）：

```
→ {"cmd": "load", "char_id": "innkeeper"}
← {"status": "ok", "char_name": "旅店老板"}

→ {"cmd": "send", "input": "你好"}
← {"dialogue": "...", "actions": [...], "decisions": [...]}
```

### 20.3 原型生成器

输入一句话描述 → `RuleCompiler` 批量模式 → 生成完整 Kernelsoul 角色文件夹。

```bash
kernelsoul generate "一个外表冷酷但内心柔软的赏金猎人，害怕蜘蛛，喜欢咖啡" --output ./characters/bounty_hunter
```

生成物：character.dsl、character_data.json、character_rules.json、meta_cognition.txt

第二十一章 语义叙事渲染引擎 [v2.4]
### 21.1 问题定义
游戏底层由数值驱动，但呈现给玩家的必须是具有质感的叙事文字。最朴素的方式是手写条件表——当 变量A > 阈值α 且 变量B < 阈值β 时输出对应的状态描述作为提示词。然而当变量超过一定数量时，组合爆炸会让条件表无法维护。

在现代游戏中存在多种解决方式，但本质上仍需预写。在 AI 叙事游戏中，也可使用条件表配合 LLM，但这会引入事实一致性不足、不同档位间叙事跳变等问题。

本引擎提出一套基于嵌入空间语义状态机的渲染方案，在确定性内核与 AI 文本生成之间构建一个可计算的中间层。

与现有架构的边界：语义渲染引擎位于规则引擎执行之后、上下文打包之前。它不替代任何现有模块，而是在“数值→叙事”这一环节提供确定性更强的替代方案。当渲染模式为 direct 时，引擎行为与 V2.3 完全一致。

### 21.2 核心概念
### 21.2.1 语义轴（Semantic Axis）
语义轴描述一个状态维度从负极到正极的语义方向。设 e(x) 为将短语转成嵌入向量的函数，则语义轴定义为：

text
D_i = e(正极锚点短语_i) - e(负极锚点短语_i)
其中正极锚点短语和负极锚点短语由游戏设计师按需定义。例如，对于某个描述“稳定性”的维度，正极锚点可选“完全稳定”，负极锚点可选“彻底崩溃”，具体措辞取决于游戏世界观的文风设定。

### 21.2.2 语义状态点（Semantic State Point）
当前状态在语义空间中的表示，由一个方向向量 p 和一个强度标量 r 组成：

text
z = r × p
p：当前状态的语义方向（在低维球面上）

r：当前状态的叙事强度（该组合有多“显著”）

### 21.2.3 Warp 函数（数值→语义幅度的非线性映射）
游戏数值变化是物理量，语义变化是叙事量。两者之间需要一层非线性映射。同样是变量值从 a 变化到 a + Δv，在平稳区可能只是“轻微变化”，在临界区则可能是“剧烈转变”。具体的语义描述由设计者按文风需求自由定义。

Warp 函数的作用是将数值变化 Δv 转换为语义空间中的变化幅度 Δt：

text
Δt = semantic_warp(v, Δv)
### 21.2.4 语义动量（Semantic Momentum）
状态的位置是叙事信息，状态的变化速度也是叙事信息。终点相同的两条路径，叙事意义完全不同。语义动量 v_semantic 记录状态“正在往哪里走”。

### 21.3 数学框架
### 21.3.1 语义轴的构建
对每一个需要叙事的游戏维度，定义一对正负锚点短语，计算语义轴：

text
D_i = e(正极短语_i) - e(负极短语_i)
所有语义轴组成轴矩阵：

text
A = [D_1, D_2, ..., D_m]
### 21.3.2 Gram 矩阵与解耦读数
语义轴之间通常不正交。例如，“变量A（描述风险程度）”和“变量B（描述结构完整度）”在嵌入空间中可能高度相关。直接用点积读取语义分量会产生串扰。

轴的 Gram 矩阵为：

text
G = A^T A
对任意文本向量 e，其在各语义轴上的解耦读数通过 Gram 矩阵消除轴间串扰：

text
Φ(e) = G^(-1) A^T (e - c)
其中 c 是语义中心点，可取所有锚点文本的嵌入均值。

### 21.3.3 低维语义子空间
全维嵌入空间中有大量与游戏状态无关的维度（文风、句式、修辞风格等），会干扰最近邻检索。

构造由语义轴、叙事阶段点及其差分共同张成的矩阵：

text
B = [D_i, S_n - c, S_(n+1) - S_n]
对 B 做 SVD 或 QR 分解，取前 k 个方向（通常 k = 10~30）：

text
Q ∈ R^(d×k)
任意文本向量投影到低维子空间：

text
z = Q^T (e - c)
空间分工：

全维嵌入：仅做原始语义测量

原始语义轴 A：用于解释和事实读数

正交计算基 Q：用于状态演化和 KNN 检索

Gram 矩阵 G：消除轴间串扰

### 21.3.4 Warp 函数的标定
Warp 函数不应手工调参，而应从叙事数据中反向标定。

给定一组按时间顺序排列的叙事阶段描述 S_0, S_1, ..., S_{N-1}（覆盖从某个极端状态到另一个极端状态的关键转折阶段），将其转为嵌入向量。这些阶段描述的措辞由游戏设计师根据世界观文风自由定义。

每个阶段在第 i 条语义轴上的投影为：

text
proj_n_i = Φ_i(S_n)
相邻阶段的语义位移为：

text
δ_n_i = proj_(n+1)_i - proj_n_i
轴内归一化语义密度：

text
ρ_n_i = |δ_n_i| / (Σ_k |δ_k_i| + ε)
含义：在这条轴的整个语义变化中，有多大比例发生在第 n 段。

每条轴赋予设计权重 α_i（由游戏设计师指定该维度在当前玩法中的重要性），则事件产生的语义幅度为：

text
t_i = α_i × ∫[v 到 v+Δv] ρ_i(x) dx
工程实现中可用查表加插值替代积分。

每帧可设置总语义能量上限 T_max，防止单一维度占据全部叙事空间：

text
Σ_i |t_i| ≤ T_max
### 21.3.5 语义推力
一次完整的事件推力由幅度和方向共同构成。

数值变化先经过 Warp 函数转化为语义幅度 Δt。事件语义轴 d_axis 投影到当前状态的切空间：

text
d_perp = Normalize(d_raw - (d_raw · p) × p)
完整语义推力：

text
ξ = Δt × d_perp
同一帧内多个事件先合成：

text
v_raw = Σ_i ξ_i
再将合成推力投影到当前切空间：

text
v_perp = v_raw - (v_raw · p) × p
### 21.3.6 状态更新
令：

text
θ = ||v_perp||
d_perp = v_perp / θ
方向更新（沿球面弧线移动，使用大圆公式）：

text
p_new = p × cos(θ) + d_perp × sin(θ)
强度单独更新：

text
r_new = UpdateMagnitude(r, v_raw, state)
最终状态：

text
z_new = r_new × p_new
对于大步变化，使用球面线性插值（SLERP）替代切空间近似：

text
SLERP(p, p_target, t) = sin((1-t)θ)/sin(θ) × p + sin(tθ)/sin(θ) × p_target
其中 t = semantic_warp(v)，p_target = Normalize(p + d_perp)。

### 21.3.7 语义动量
语义动量累积最近几帧的语义推力，用于描述状态“正在往哪里走”：

text
v_semantic(t) = λ × v_semantic(t-1) + v_raw
其中 0 < λ < 1 为衰减系数。

因状态在球面上移动，切空间变化，旧动量需重新投影到当前切空间：

text
v_semantic ← v_semantic - (v_semantic · p_current) × p_current
某些特殊事件可主动修改动量。例如，设计者可定义某事件“清空某轴动量”，或“冻结某轴使其暂不参与状态更新”。具体事件类型和对应的动量操作由游戏设计师在规则配置中定义。

### 21.4 渲染管线
### 21.4.1 事实签名过滤
在短语库中检索之前，先进行事实兼容性检查，防止 KNN 因整体相似而选中与当前事实矛盾的短语。

对每条候选短语 s，离线预计算其事实签名：

text
Φ(s) = G^(-1) A^T (e(s) - c)
每条短语的签名含：

value_i：该轴上语义方向和强度

salience_i：该句是否明确表达此轴

confidence_i：该判断的可靠程度

查询时，若某候选短语在关键轴上与当前状态明确矛盾，直接剔除：

text
|ψ_i| > τ_state  AND  |φ_i(s)| > τ_phrase  AND  salience_i(s) > τ_salience  AND  φ_i(s) × ψ_i < -ε
满足即矛盾，删除候选。

原则：明确矛盾删除，未提及保留，程度偏差留待后续排序处理。

21.4.2 加权 KNN 短语检索
过滤后的候选按加权距离排序：

text
d_fact(s) = Σ_i w_i × (φ_i(s) - ψ_i)^2
权重 w_i 来自 Warp 函数标定阶段获得的语义密度曲线——临界区敏感，平稳区宽容。

最终评分可综合考虑：

text
Score(s) = α×d_fact + β×d_style + γ×d_momentum + δ×d_history
d_fact：事实准确度（变量值在各个语义轴上的读数偏差）

d_style：风格匹配度（候选短语与游戏文风的嵌入距离）

d_momentum：是否契合当前变化方向（候选短语的语义方向与 v_semantic 的夹角）

d_history：与上一句的衔接度（候选短语与上一轮已输出文本的连贯性得分）

### 21.4.3 结构化 LLM 兜底生成
事实过滤后若候选不足（稀有状态组合、词库缺口），切换为结构化 LLM 生成。

将当前状态、变化方向、禁止项、上一句摘要组装为 ContextPacket，交给 LLM：

json
{
  "当前状态": {
    "变量A": "极高，但未失控",
    "变量B": "高度稳定",
    "变量C": "中低"
  },
  "变化方向": {
    "变量A": "仍在上升",
    "变量B": "被外部约束强行维持"
  },
  "上一句摘要": "状态逐渐趋近临界，但仍在可控范围",
  "禁止项": [
    "不要描述[负面极端状态A]",
    "不要描述[负面极端状态B]",
    "不要暗示[负面极端状态C]"
  ]
}
注：变量A/B/C、状态描述短语、禁止项内容均由游戏设计师根据具体玩法维度定义。LLM 的职责是在给定事实边界内将状态写成自然语言，不做事实判断。

### 21.5 词库管理
### 21.5.1 短语库的事实签名预计算
词库中每条短语在入库时计算其事实签名 Φ(s)，包含轴向读数、显著性、置信度和覆盖区间。运行时查询仅读取预计算结果。

### 21.5.2 Miss Buffer 与缺口检测
当以下情况发生时，将当前状态点记录到 Miss Buffer：

事实过滤后候选不足

Top-K 候选覆盖轴不完整

候选事实距离过大

某类状态频繁触发 LLM 兜底生成

后台定期对 Miss Buffer 中的状态点做聚类（如 DBSCAN），发现高频缺口区域。

### 21.5.3 短语生成与校验
对缺口区域批量生成新短语，但需通过校验才能入库：

落点校验：嵌入后是否落在目标区域

轴向校验：是否覆盖应覆盖的轴

反向解析：从短语能否反推出原状态

冲突检测：有无写出不存在的事实

风格检测：是否符合设定的文风

### 21.5.4 词库闭环更新
text
冷门状态 → 结构化生成
高频缺口 → 聚类发现
新短语 → 生成并校验
常见路径 → 逐步缓存
词库不再是静态文案表，而是一个随运行不断优化的质量缓存。

### 21.6 与 Kernelsoul 引擎的集成
### 21.6.0 与现有模块的协作关系
语义渲染引擎作为 Kernelsoul 引擎的可选增强模块，位于规则引擎与 AI 文本生成之间。其与现有核心逻辑的边界如下：

模块/逻辑单元	手册位置	与语义渲染器的关系
状态更新逻辑	第九章步骤9（提交与烘焙）	state.sav 写入后触发语义渲染器，接收变更后的变量值
CharacterStateManager	4.3	角色专属变量（character_state）变更后同样可触发语义渲染
规则引擎	第六章（规则语法）+ 第七章（DSL 规则系统）	规则执行 → 状态变更 → 语义渲染器接收新值。渲染器不参与规则评估
上下文打包	第九章步骤4	语义渲染器的输出（叙事描述短语）替代原有“数值直接文本化”的结果，注入 Prompt 的状态描述部分
模型调用逻辑	第九章步骤5（AI 生成）	语义渲染器输出 ContextPacket → 拼入最终 Prompt 后调用大模型
世界书检索	第九章步骤3	世界书条目可作为语义轴的附加锚点，参与事实签名过滤
渲染模式切换不影响上述逻辑单元的核心行为——当渲染模式为 direct 时，引擎行为与 V2.3 完全一致。

### 21.6.1 数据流
text
GameState 变量变化 Δv（由第九章步骤9的状态更新逻辑触发）
    → 语义渲染器接收变量变化 Δv
    → Warp 函数 + 语义轴 → 语义推力 ξ
    → 状态更新 (p, r, v_semantic)
    → 事实签名过滤 + KNN 检索 / 结构化生成
    → ContextPacket → 拼入 Prompt → 调用大模型 → AI 文本输出
注：语义渲染器与规则引擎（第六/七章）的协作关系为：规则引擎评估并执行动作 → 状态更新逻辑写入 state.sav 和 character_state → 语义渲染器接收变更后的变量值 → 生成叙事描述。语义渲染器位于规则引擎的下游，不参与规则评估逻辑。
### 21.6.2 角色卡中的轴向映射配置
在 Kernelsoul 角色卡中，语义渲染配置可通过独立文件或内嵌字段提供。

存储位置说明：semantic_config 可存储于以下两种位置之一：

独立文件：/characters/{角色ID}/character_semantic.json（推荐）。与 .dsl 和 _rules.json 并列，便于版本控制和独立编辑。

内嵌于角色卡：在 character_data.json 的顶层增加 semantic_config 字段（可选）。若同时存在独立文件和内嵌配置，以独立文件为准。

引擎 3.1 节定义的 GameState 为扁平结构，不承载语义渲染配置。GameState 仅存储运行时变量值，语义轴的锚点短语和 Warp 阶段描述属于设计时配置，不应混入运行时状态。

配置示例（独立文件或内嵌字段的内容相同）：

json
{
  "variables": {
    "variable_x": {
      "type": "int",
      "range": [-100, 100],
      "default": 0,
      "semantic_config": {
        "axis_positive": "由设计者自由定义的正极锚点短语",
        "axis_negative": "由设计者自由定义的负极锚点短语",
        "design_weight": 0.3,
        "warp_stages": [
          "由设计者自由定义的叙事阶段描述0",
          "由设计者自由定义的叙事阶段描述1",
          "由设计者自由定义的叙事阶段描述2",
          "由设计者自由定义的叙事阶段描述3"
        ]
      }
    }
  }
}
注：axis_positive、axis_negative 和 warp_stages 中的内容完全由游戏设计师根据世界观文风自由填写。引擎不做任何预设。若角色卡未提供 semantic_config，引擎使用默认配置（仅做线性映射，跳过 Warp 优化）。

### 21.6.3 渲染模式切换
引擎支持三种渲染模式，通过 /render_mode 指令切换：

模式	说明
direct	数值直接文本化注入 Prompt（当前默认行为，零开销）
semantic	启用语义渲染管线（需要嵌入模型支持）
hybrid	常用状态走语义渲染，稀有状态走直接模式
### 21.7 开放研究问题
以下问题已在设计文档中记录，但不在当前 MVP 范围内：

初始状态向量的标定：新角色首次加载时，如何从少量描述文本标定其在语义空间中的初始位置？可能的方案包括用角色卡中的 description 和 personality 字段做锚定。

跨场景语义轴复用：不同游戏场景（战斗、社交、探索、恋爱、等各种交互时）可能需要不同的语义轴集合。如何设计可复用的轴库？

实时 Warp 函数更新：当玩家行为显著偏离预设的叙事阶段轨迹时，Warp 函数是否需要在线更新？如果需要，如何保证更新的稳定性？

多语言嵌入空间的一致性：语义轴在中文嵌入空间中定义后，切换到英文模型时是否需要重新标定？跨语言的语义轴迁移是否可行？

与传统对话系统的融合：在非叙事驱动的聊天场景中，语义渲染是否仍有意义？

版本变更记录

v1.0 ─ 初始手册：基础架构、模块划分、AI 强制 JSON 契约、三层架构
v1.1 ─ GameState 强类型定义、AI 响应 Schema、规则引擎语法、PathResolver 实现
v1.2 ─ 双轨制运行机制、草稿机制（/roll /select /drafts）、世界线快照扩展
v1.3 ─ 分级容错策略、记忆压缩系统、session_meta 存档管理、插件系统设计规范
v1.4 ─ 设计哲学融入第一部分（刚性内核/柔性外壳）、自然语言优先协议、三段式解析器升级
v1.5 ─ 快速开始引导、手动记忆锚点、角色卡加载器（CharacterCardLoader）、UI 性能基准、数据主权原则
v1.6 ─ 旁挂初始状态文件、Token 预算检查与裁剪、死亡/失败状态处理、草稿收藏、世界书二次检索、开场白初始化
v2.0 ─ Kernelsoul 角色操作系统：character_state、角色规则、条件记忆、CharacterStateManager、双层规则引擎、决策溯源、元认知预设
v2.1 ─ Kernelsoul 角色行为 DSL（SLL）、DSL 编译器、character_rules_dsl/character_rules_source 字段、RuleCompiler 三种模式
v2.3 ─ 三条铁律、Kernelsoul 角色文件标准、FileService 极简后端 API、DSL 编译器 Python 实现、CharacterStateManager Python 实现、Context 网络设计规范
v2.3 ─ 记忆压缩升级为双层机制：10轮轻量压缩（200字）+ 50轮深度压缩（2000字）；新增两份压缩提示词模板（compression_prompt_light.txt / compression_prompt_deep.txt）；工作记忆注入调整为"1条深度摘要 + 3条轻量摘要"；full_memory.json 条目新增 compression_type 字段；新增第五部分"生态扩展路线图"（第十七至二十章）：Unity/Unreal 集成（gRPC API、C# SDK、预制组件）、Kernelsoul 角色创作工作台、Kernelsoul 对话 SDK（pip install kernelsoul-character-os）、Godot/模组/原型生成器
v2.3.1─ [新增] 三层分层压缩（轻量/深度/史诗）：compression_prompt_merge.txt & compression_prompt_epic.txt 两份新模板、分层合并算法、上下文注入规则升级。三层压缩架构已合并至第十二章。
v2.4 ─ 新增"语义叙事渲染引擎"（第二十一章）：包括语义轴、语义状态点、Warp函数、语义动量的核心概念（21.2）；Gram矩阵解耦读数、低维子空间投影、Warp标定、语义推力合成、SLERP状态更新的数学框架（21.3）；事实签名过滤、加权KNN检索、结构化LLM兜底生成的完整渲染管线（21.4）；词库闭环管理（预计算签名、Miss Buffer缺口检测、短语生成与五项校验）（21.5）；与现有手册模块的精确边界定义（21.6.0）和数据流规范（21.6.1）；角色卡轴向映射配置文件 character_semantic.json（21.6.2）；/render_mode 渲染模式切换指令（direct/semantic/hybrid）；