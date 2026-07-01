# V4 v2.4 50-Round Full Test — Comparison Report
 
 **⚠️ Translation Notice**: The author is not a native English speaker. This English README was machine-translated and may contain awkward phrasing or terminology errors. Corrections and pull requests are warmly welcomed. The [Chinese version](README.md) is the authoritative reference.

**Test Time**: 2026-07-01 14:36 ~ 14:47 (UTC+8)
**Model**: deepseek-chat (DeepSeek V4)
**Character**: night_hunter (Night City Demon Hunter - Frost)
**Total Rounds**: 50
**Total Tokens**: 12,280 (avg 245/round)

---

## I. Three-Mode Overview

| Metric | Direct (v2.3 baseline) | Semantic (v2.4) | Hybrid (v2.4) |
|--------|------------------------|-----------------|----------------|
| Rounds | 1-20 (20 rounds) | 21-40 (20 rounds) | 41-50 (10 rounds) |
| Total Tokens | 4,215 | 5,613 | 2,452 |
| Avg Tokens/Round | **211** | **281** (+33%) | **245** (+16%) |
| Avg Response Time | 4.7s | 5.9s | 5.3s |
| Total Duration | 94s | 118s | 53s |
| WB Hits | 37 (1.9/round) | 28 (1.4/round) | 15 (1.5/round) |
| State Change Rounds | 7/20 (35%) | 8/20 (40%) | 3/10 (30%) |
| HP Change | 100->85 | 85->20 | 20->20 |
| Emotion Changes | 5 types | 5 types | 3 types |

---

## II. Core Findings

### 2.1 Token Output: Semantic > Hybrid > Direct

Semantic mode produced 33% more output than Direct (281 vs 211 tokens/round). This shows that semantic prompting guides the model to generate longer, more detailed narratives. Hybrid mode sits in the middle (245), demonstrating a clear trade-off.

**Typical Comparison**:
- Direct R20 (climax battle): 540 tokens
- Semantic R22 (ancient memory): 339 tokens - poetic imagery
- Hybrid R44 (reconciliation): 303 tokens - emotionally introspective

### 2.2 State Change Frequency: Semantic More Active

Semantic mode has the highest state change rate (40%), more frequent than Direct (35%) and Hybrid (30%). This suggests semantic prompting enhances the model's judgment of "whether this round should trigger a state change."

**Bug**: Energy dropped to -45 during Semantic mode and never recovered. No energy floor protection.

### 2.3 Narrative Style Differences

**Direct mode**: Action-driven compact narrative (light novel style). Heavy on action and dialogue. Rapid emotional shifts: neutral -> angry -> grief -> determined -> shocked -> cold anger.

**Semantic mode**: More inner monologue and world-building. Detailed scene descriptions, stronger atmosphere. Nuanced emotions: hollow satisfaction, quiet gratitude, vigilant.

**Hybrid mode**: Combines Direct's pacing with Semantic's emotional depth. Smoother emotional arc. Natural dialogue. Largest goodwill increase: 3 -> 24.

### 2.4 Semantic Engine Status: NOT Fully Active

Key issue: **Semantic axis construction failed**.

Logs show:
```
[SemanticEngine] Axis build failed: Embedding API unavailable.
```

DeepSeek API does not support embedding. Therefore:
- `semantic_p` (position vector) stays at zero
- `semantic_r` (radius) not updated
- `is_ready()` returns False
- What actually worked was **state-delta prompt injection**, not true vector-space rendering

The "semantic" mode was essentially **"state-aware direct"** mode.

### 2.5 Worldbook Hit Rate

Direct mode highest (1.9/round). Without semantic prompts, the model uses more lore keywords. Semantic/Hybrid slightly lower (1.4-1.5).

---

## III. Issues Found

### 3.1 Energy Negative Overflow (-45)
Energy < 0 from R31 until test end. System lacks minimum energy protection.

### 3.2 Duplicate State Changes
R23 and R24 produced identical state_changes, causing inventory operation warnings.

### 3.3 Semantic Prompt Format Too Mechanical
Current format: `[State Change: hp: -15; energy: -20]` - should use narrative guidance instead.

---

## IV. Improvement Suggestions

1. **Fix Embedding**: Add fallback or local embedding model
2. **Optimize Prompt Format**: Narrative guidance instead of raw state values
3. **Energy Floor**: Add energy clamp protection
4. **Consistency Check**: Detect duplicate state changes
5. **Configurable Hybrid Weights**

---

## V. Conclusion

**Direct -> Semantic upgrade is effective**: +33% token output, more active state changes, richer emotion. But with embedding layer non-functional, only about 30% of potential is realized.

**Hybrid mode is the most promising direction**: Best balance of pacing and emotional depth. With full Semantic Engine, expected improvement would be significantly greater.
