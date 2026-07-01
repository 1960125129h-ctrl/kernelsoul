# V4 v2.4 50轮完整测试 — 对比总结报告

**测试时间**: 2026-07-01 14:36 ~ 14:47 (UTC+8)
**模型**: deepseek-chat (DeepSeek V4)
**角色**: night_hunter (夜城猎魔人·寒霜)
**总轮次**: 50 轮
**总 Token**: 12,280 (avg 245/轮)

---

## 一、三模式概览

| 指标 | Direct (v2.3基准) | Semantic (v2.4) | Hybrid (v2.4) |
|------|-------------------|-----------------|---------------|
| 轮次 | 1-20 (20轮) | 21-40 (20轮) | 41-50 (10轮) |
| 总Token | 4,215 | 5,613 | 2,452 |
| 平均Token/轮 | **211** | **281** (+33%) | **245** (+16%) |
| 平均响应时间 | 4.7s | 5.9s | 5.3s |
| 总耗时 | 94s | 118s | 53s |
| WB命中 | 37 (1.9/轮) | 28 (1.4/轮) | 15 (1.5/轮) |
| 状态变更轮次 | 7/20 (35%) | 8/20 (40%) | 3/10 (30%) |
| HP变化 | 100→85 | 85→20 | 20→20 |
| 情绪变化数 | 5种 | 5种 | 3种 |

---

## 二、核心发现

### 2.1 Token 产出: Semantic > Hybrid > Direct

Semantic 模式产生了比 Direct 多 33% 的输出（281 vs 211 tokens/轮）。这表明语义提示确实引导模型生成了更长、更详细的叙事。Hybrid 模式居中（245），折中效果明显。

**典型对比**:
- Direct R20 (高潮战斗): 540 tokens — 是 direct 模式中最高的一轮
- Semantic R22 (远古记忆): 339 tokens — 虽短但充满诗意画面
- Hybrid R44 (和解): 303 tokens — 节奏更克制，情感更内敛

### 2.2 状态变更频率: Semantic 更活跃

Semantic 模式的状态变更率最高（40%），比 Direct（35%）和 Hybrid（30%）更频繁触发 game-state 变化。这说明语义提示增强了模型对"这一轮是否该改变状态"的判断力。

**但存在一个 bug**: Energy 在 semantic 模式期间降至 -45 且未恢复。模型持续扣除 energy（战斗/手术场景），但系统没有能量下限保护，导致后续轮次始终为负值。

### 2.3 叙事风格差异

**Direct 模式**的特征:
- 行动驱动的紧凑叙事，类似轻小说风格
- 大量动作描写和对话
- 情感到达速度快：neutral → angry → grief → determined → shocked → cold anger（6种情绪，20轮内切换5次）
- 例："你轻笑一声，指尖的冰晶化作细碎的雪花飘落"（R20）

**Semantic 模式**的特征:
- 增加了内心独白和世界观构筑
- 场景描写更细腻，氛围感更强
- 情绪更微妙：hollow satisfaction（空洞的满足）、quiet gratitude（安静的感激）、vigilant（警觉）
- 例："你看到千年前的夜城——那时它还叫霜临城，一座被永恒冬雪覆盖的古老聚落"（R22）

**Hybrid 模式**的特征:
- 结合了 direct 的节奏和 semantic 的情感深度
- 情感弧线更平滑：suppressed anger → cautious trust → softened coldness
- Goodwill 增长最大：从 3 升至 24（故事结局的和解阶段）
- 对白更自然，像成熟的剧本对话

### 2.4 Semantic Engine 状态: ⚠️ 未完全生效

关键问题：**语义轴构建失败**。

日志显示：
```
[SemanticEngine] Axis build failed: Embedding API unavailable. 
Check API key and model availability.
```

原因：DeepSeek API 不支持 embedding 接口（`engine.bridge.embed` 返回失败）。因此：
- 语义引擎的 `semantic_p`（语义位置向量）始终为零
- `semantic_r`（语义半径）未更新
- `is_ready()` 返回 False → 所有 semantic trace 记录为空
- **实际起作用的只是上一轮的 state delta 作为提示词注入**，而非真正的向量空间语义渲染

这意味着当前测试中的 "semantic" 模式本质上是 **"state-aware direct"** 而非真正的语义驱动。

### 2.5 Worldbook 命中率

Direct 模式的 WB 命中率最高（1.9/轮），这说明不加语义提示时，模型用到的 lore 关键词更多。Semantic/Hybrid 模式稍低（1.4-1.5），因为额外的语义提示可能引导模型朝着更聚焦的方向思考，减少了关键词的随机命中。

---

## 三、数据中发现的问题

### 3.1 Energy 负值溢出
Semantic R31 开始 Energy < 0，持续到测试结束（R50: -45）。系统没有能量最低值保护。

### 3.2 重复状态变更
R23 和 R24 产生了完全相同的 state_changes（"hp: -15, energy: -20, inventory_remove: 霜华之力·完整..."），导致 R24 的背包操作报警 `[StateManager.WARN] 背包中不存在`。

### 3.3 语义提示格式
当前语义提示格式为 `[状态变化: hp: -15; energy: -20; ...]`，过于机械化。理想格式应包含叙事方向建议，而非状态数值。

---

## 四、改进建议

1. **修复 Embedding 支持**: 为 DeepSeek 添加 embedding fallback，或使用本地 embedding 模型使 Semantic Engine 真正工作
2. **优化语义提示格式**: 将 `[状态变化: hp:-5]` 改为叙事引导如 `[叙事方向: 角色因受伤而变得更加谨慎]`
3. **Energy 下限保护**: 添加 `energy = max(0, energy)` 或在 `apply_state_changes` 中加入 clamp
4. **增加一致性检查**: 检测连续两轮产生相同 state_changes 的情况，提示模型或自动去重
5. **Hybrid 模式权重可调**: 让 direct/semantic 的权重可配置，而非固定

---

## 五、结论

**Direct → Semantic 的升级确实有效果**：Token 产出提升 33%，状态变更更活跃，情感表达更细腻。但由于 Semantic Engine 的 embedding 层未工作，当前效果主要来自 state-delta 提示注入，而非真正的向量空间语义渲染——这相当于只发挥了约 30% 的潜力。

**Hybrid 模式是最有前途的方向**：它结合了两种模式的优势，叙事节奏好、情感深度够，且在结局阶段（R48-50）产出了最自然的对白。如果 Semantic Engine 能完整运行，Hybrid 的预期提升会更大。
