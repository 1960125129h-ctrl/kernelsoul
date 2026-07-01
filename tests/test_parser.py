"""Kernelsoul - ParserEngine 三段式解析测试

覆盖:
  阶段一: extract_json_code_block() — [```json```] 标记提取
  阶段二: extract_json_fallback()   — 最大括号回溯
  阶段三: extract_from_natural_language() — 自然语言正则匹配
  集成:   parse() 主入口三段式优先级
"""
import json
import sys
import os
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'kernelsoul'))

from parser_engine import ParserEngine, parse_ai_response


# ═══════════════════════════════════════════════
# 阶段一: JSON 代码块提取
# ═══════════════════════════════════════════════
class TestPhase1_JsonCodeBlock(unittest.TestCase):
    """测试: extract_json_code_block()"""

    def test_standard_json_block(self):
        raw = '''玩家推开了沉重的铁门。

```json
{"hp": -5, "energy": -10, "bg": "阴暗走廊"}
```'''
        narrative, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes["hp"], -5)
        self.assertEqual(changes["energy"], -10)
        self.assertEqual(changes["bg"], "阴暗走廊")
        self.assertIn("沉重的铁门", narrative)
        self.assertNotIn("```", narrative)

    def test_json_block_with_inventory(self):
        raw = '''你捡起了地上的东西。

```json
{"inventory_add": ["生锈的钥匙"], "money": 50, "goodwill": 2}
```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes["inventory_add"], ["生锈的钥匙"])
        self.assertEqual(changes["money"], 50)
        self.assertEqual(changes["goodwill"], 2)

    def test_json_block_with_emotion_and_cg(self):
        raw = '''怪物从阴影中现身。

```json
{"emotion": "恐惧", "cg": "cg_monster_appear"}
```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes["emotion"], "恐惧")
        self.assertEqual(changes["cg"], "cg_monster_appear")

    def test_json_block_uppercase_tag(self):
        """```JSON 大写也应匹配"""
        raw = '''测试。

```JSON
{"hp": -10}
```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes["hp"], -10)

    def test_json_block_extra_whitespace(self):
        """```json 前后空白应被容忍"""
        raw = '''测试文本。

```json

{"hp": -3}

```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes["hp"], -3)

    def test_no_json_block_returns_empty(self):
        raw = "这是一段没有任何代码块的普通叙事文本。"
        narrative, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes, {})
        self.assertEqual(narrative, raw)

    def test_malformed_json_block(self):
        """格式错误的 JSON 应返回空变更，不抛异常"""
        raw = '''文本。

```json
{hp: -5, energy: -10
}```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes, {})  # 解析失败，不影响叙事

    def test_json_block_not_dict(self):
        """JSON 是数组而非对象时应返回空"""
        raw = '''文本。

```json
[{"hp": -5}]
```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes, {})

    def test_multiple_json_blocks_first_wins(self):
        """多个代码块时取第一个 JSON 块"""
        raw = '''第一段。

```json
{"hp": -5}
```

第二段。

```json
{"hp": -99}
```'''
        _, changes = ParserEngine.extract_json_code_block(raw)
        self.assertEqual(changes["hp"], -5)  # 第一个生效


# ═══════════════════════════════════════════════
# 阶段二: 最大括号回溯
# ═══════════════════════════════════════════════
class TestPhase2_JsonFallback(unittest.TestCase):
    """测试: extract_json_fallback()"""

    def test_bare_json_at_end(self):
        """文本末尾有裸 JSON 对象（无 ``` 标记）"""
        raw = '''莉莉丝微微一笑，递给你一杯冒着热气的茶。
{"hp": 5, "goodwill": 3, "inventory_add": ["热茶"]}'''
        narrative, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes["hp"], 5)
        self.assertEqual(changes["goodwill"], 3)
        self.assertEqual(changes["inventory_add"], ["热茶"])
        self.assertIn("莉莉丝", narrative)
        self.assertNotIn("{", narrative)

    def test_nested_json(self):
        """嵌套 JSON 对象应被正确回溯"""
        raw = '''战斗结束了。
{"hp": -20, "effects": {"bleeding": true, "stun": false}, "bg": "战场废墟"}'''
        _, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes["hp"], -20)
        self.assertEqual(changes["bg"], "战场废墟")

    def test_multiline_json(self):
        """多行 JSON"""
        raw = '''你打开了宝箱。

{
  "money": 200,
  "inventory_add": ["金色戒指", "古老地图"],
  "bg": "宝藏室"
}'''
        _, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes["money"], 200)
        self.assertEqual(changes["inventory_add"], ["金色戒指", "古老地图"])
        self.assertEqual(changes["bg"], "宝藏室")

    def test_json_without_code_block_marker(self):
        """AI 可能忘记 ``` 但 JSON 结构完整"""
        raw = '少女点了点头。{"hp": -5, "energy": -10, "emotion": "悲伤"}'
        _, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes["hp"], -5)
        self.assertEqual(changes["emotion"], "悲伤")

    def test_no_braces(self):
        """没有任何花括号时应返回空"""
        raw = "这是一段完全没有花括号的文本。句号。"
        _, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes, {})

    def test_unbalanced_braces(self):
        """花括号不平衡时应返回空（不崩溃）"""
        raw = '''文本。{"hp": -5'''
        _, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes, {})

    def test_text_after_json(self):
        """JSON 后还有文本时，应正确分割"""
        raw = '''冒险继续。{"hp": -3}少女转身离去。'''
        narrative, changes = ParserEngine.extract_json_fallback(raw)
        self.assertEqual(changes["hp"], -3)

    def test_json_mid_text_not_at_end(self):
        """JSON 不在末尾但在文本中（不应提取或应提取最末尾的）"""
        raw = '''{"hp": -99}中间文本。{"hp": -10}'''
        _, changes = ParserEngine.extract_json_fallback(raw)
        # 应提取最后一个有效 JSON
        self.assertEqual(changes["hp"], -10)


# ═══════════════════════════════════════════════
# 阶段三: 自然语言匹配
# ═══════════════════════════════════════════════
class TestPhase3_NaturalLanguage(unittest.TestCase):
    """测试: extract_from_natural_language()"""

    def test_damage_pattern(self):
        raw = "你受到了 15 点伤害，生命值急剧下降。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["hp"], -15)

    def test_heal_pattern(self):
        raw = "牧师为你恢复了 20 点生命，伤口逐渐愈合。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["hp"], 20)

    def test_energy_drain(self):
        raw = "长时间的奔跑消耗了 30 点体力。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["energy"], -30)

    def test_energy_restore(self):
        raw = "喝下能量药水后，恢复了 25 点体力。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["energy"], 25)

    def test_goodwill_increase(self):
        raw = "好感度增加 5。少女对你露出了真诚的微笑。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["goodwill"], 5)

    def test_goodwill_decrease(self):
        raw = "好感度降低 8。她皱起了眉头，转过身去。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["goodwill"], -8)

    def test_money_gain(self):
        raw = "你从怪物尸体上获得了 100 枚金币。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["money"], 100)

    def test_money_spend(self):
        raw = "你在酒馆花费了 50 枚金币，点了一桌丰盛的晚餐。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["money"], -50)

    def test_emotion_anger(self):
        raw = "听到这个消息，她变得愤怒，拳头紧紧攥起。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["emotion"], "愤怒")

    def test_emotion_sad(self):
        raw = "看着远去的背影，她感到悲伤，泪水无声滑落。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["emotion"], "悲伤")

    def test_bg_change(self):
        raw = "穿过蜿蜒的小径，你来到了「古老的祭坛」。四周静得可怕。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["bg"], "古老的祭坛")

    def test_bg_change_alt(self):
        raw = "你进入了王座大厅，两排卫兵齐刷刷地看向你。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        # "来到/进入" 后跟场景
        self.assertIn("bg", changes)

    def test_item_gain(self):
        raw = "打开宝箱，你获得了「古老的钥匙」和一把「生锈的剑」。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertIn("inventory_add", changes)
        self.assertIn("古老的钥匙", changes["inventory_add"])
        # "生锈的剑" 可能也被匹配
        self.assertGreaterEqual(len(changes.get("inventory_add", [])), 1)

    def test_item_lose(self):
        raw = "为了通过关卡，你交出了「通行证」。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertIn("inventory_remove", changes)
        self.assertIn("通行证", changes["inventory_remove"])

    def test_combined_patterns(self):
        """一句话中多个模式同时匹配"""
        raw = "你受到了 5 点伤害，但获得了 50 枚金币。好感度增加 3。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["hp"], -5)
        self.assertEqual(changes["money"], 50)
        self.assertEqual(changes["goodwill"], 3)

    def test_no_patterns_match(self):
        raw = "少女静静地看着你，什么都没说。微风拂过她的长发。"
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes, {})

    def test_overlap_prevention(self):
        """重叠匹配不应重复计数"""
        raw = "你受到了 10 点伤害。"  # 只有一处伤害描述
        _, changes = ParserEngine.extract_from_natural_language(raw)
        self.assertEqual(changes["hp"], -10)  # 只计一次


# ═══════════════════════════════════════════════
# 集成测试: parse() 三段式优先级
# ═══════════════════════════════════════════════
class TestParseIntegration(unittest.TestCase):
    """测试: parse() 主入口 + 三段式优先级"""

    def test_phase1_has_priority(self):
        """阶段一 JSON 块应优先于自然语言"""
        raw = '''你受到了 999 点伤害，但魔法护盾挡下了大部分。

```json
{"hp": -5, "emotion": "警惕"}
```'''
        result = ParserEngine.parse(raw)
        # 应使用 JSON 块的值，而非自然语言匹配的 -999
        self.assertEqual(result["state_changes"]["hp"], -5)
        self.assertEqual(result["state_changes"]["emotion"], "警惕")

    def test_phase2_fallback_when_no_block(self):
        """无 ``` 标记但有裸 JSON 时走阶段二"""
        raw = '''对话结束。{"hp": -5, "goodwill": 2}'''
        result = ParserEngine.parse(raw)
        self.assertEqual(result["state_changes"]["hp"], -5)
        self.assertEqual(result["state_changes"]["goodwill"], 2)

    def test_phase3_as_last_resort(self):
        """无 JSON 时走阶段三自然语言"""
        raw = "你受到了 10 点伤害，获得了 30 枚金币。好感度增加 2。"
        result = ParserEngine.parse(raw)
        self.assertEqual(result["state_changes"]["hp"], -10)
        self.assertEqual(result["state_changes"]["money"], 30)
        self.assertEqual(result["state_changes"]["goodwill"], 2)

    def test_empty_changes_on_pure_narrative(self):
        """纯叙事无状态变化"""
        raw = "月光洒在湖面上，波光粼粼。远处传来夜莺的歌声。"
        result = ParserEngine.parse(raw)
        self.assertEqual(result["state_changes"], {})
        self.assertEqual(result["narrative"], raw)

    def test_narrative_preserved(self):
        """叙事文本应被正确保留"""
        raw = '''你小心翼翼地推开了那扇沉重的橡木门。

门后是一个宽敞的大厅，烛光摇曳。

```json
{"bg": "烛光大厅", "emotion": "好奇"}
```'''
        result = ParserEngine.parse(raw)
        self.assertIn("橡木门", result["narrative"])
        self.assertIn("烛光", result["narrative"])
        self.assertNotIn("```", result["narrative"])

    def test_json_block_with_double_hp(self):
        """自然语言和 JSON 块都提到 HP 时，以 JSON 为准"""
        raw = '''光芒闪过，你受到了 50 点伤害！

```json
{"hp": -20}
```'''
        result = ParserEngine.parse(raw)
        self.assertEqual(result["state_changes"]["hp"], -20)

    def test_convenience_function(self):
        """parse_ai_response 便捷函数"""
        raw = '''少女微微一笑。{"goodwill": 5}'''
        result = parse_ai_response(raw)
        self.assertEqual(result["state_changes"]["goodwill"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)



