"""
Kernelsoul - ParserEngine 解析器引擎
手册 §3.2-§3.3: 从 AI 响应中智能提取状态变更。

三段式策略（优先级递减）:
  阶段一: extract_json_code_block()    — 提取 ```json``` 标记内的 JSON
  阶段二: extract_json_fallback()      — 从文本末尾向前最大括号回溯
  阶段三: extract_from_natural_language() — 正则匹配自然语言中的数值变化

白名单校验: 非法字段直接丢弃，绝不崩溃。
"""
from __future__ import annotations
import json
import re
from typing import Tuple, Optional


class ParserEngine:
    """AI 响应解析器。输入原始文本，返回 (narrative, state_changes)。

    设计原则（手册 §3.2 末尾）:
    - AI 未提供 JSON 或解析失败 → 仅推进剧情，状态不变
    - 叙事永远是第一位的
    """

    # ── 阶段一: JSON 代码块提取 ──
    JSON_BLOCK_RE = re.compile(
        r"```json\s*([\s\S]*?)\s*```",
        re.IGNORECASE
    )

    # ── 阶段三: 自然语言模式 ──
    # 手册规范的可修改字段映射表
    NL_PATTERNS = [
        # HP 变化: "受到了 5 点伤害" / "恢复了 20 点生命"
        (re.compile(r"(?:受到|损失|失去|扣除)了?\s*(\d+)\s*点?\s*(?:伤害|生命|HP|hp)"), "hp", -1),
        (re.compile(r"(?:恢复|回复|治疗|治愈|获得)了?\s*(\d+)\s*点?\s*(?:生命|HP|hp|血量)"), "hp", 1),
        # 能量变化
        (re.compile(r"(?:消耗|失去|减少)了?\s*(\d+)\s*点?\s*(?:能量|体力|精力)"), "energy", -1),
        (re.compile(r"(?:恢复|回复|获得)了?\s*(\d+)\s*点?\s*(?:能量|体力|精力)"), "energy", 1),
        # 好感度
        (re.compile(r"好感度\s*(?:增加|提升|上升)了?\s*(\d+)"), "goodwill", 1),
        (re.compile(r"好感度\s*(?:降低|减少|下降)了?\s*(\d+)"), "goodwill", -1),
        # 金币 (带单位词，先于物品匹配)
        (re.compile(r"(?:获得|得到|赚|捡到)了?\s*(\d+)\s*枚?\s*(?:金币|铜币|银币)"), "money", 1),
        (re.compile(r"(?:花费|支付|损失|花掉|用掉)了?\s*(\d+)\s*枚?\s*(?:金币|铜币|银币)"), "money", -1),
        (re.compile(r"(?:获得了?|得到了?|赚了?|收到了?)\s*(\d+)\s*(?:枚)?\s*(?:金币|铜币|银币)"), "money", 1),
        # 情绪
        (re.compile(r"(?:变得|感到|陷入|显得)了?\s*(愤怒|悲伤|恐惧|喜悦|惊讶|厌恶|好奇|平静|警惕|放松|困惑|害羞|傲慢|失望|希望)"), "emotion", None),
        # 场景 (支持「」或无括号)
        (re.compile(r"(?:来到|进入|到达|出现在|身处)了?\s*\u300c?([^\uff0c\u3002\uff1b\uff01\uff1f\n\u300c\u300d\u300e\u300f\u3001、]{2,20})\u300d?"), "bg", None),
        # 物品获得 (排除以数字开头)
        (re.compile(r"(?:获得|得到|捡起|拾取|接收|收到)了\s*\u300c?((?!\d)[^\uff0c\u3002\uff1b\uff01\uff1f\n\u300c\u300d\u300e\u300f\u3001、]{1,20})\u300d?"), "inventory_add", None),
        # 物品失去 (排除以数字开头)
        (re.compile(r"(?:失去|丢弃|使用|交出|摧毁|消耗)了\s*\u300c?((?!\d)[^\uff0c\u3002\uff1b\uff01\uff1f\n\u300c\u300d\u300e\u300f\u3001、]{1,20})\u300d?"), "inventory_remove", None),
    ]

    @classmethod
    def parse(cls, raw: str) -> dict:
        """主入口: 三段式解析，返回 {narrative, state_changes}。"""
        result = {"narrative": raw.strip(), "state_changes": {}, "method": "none"}

        # 阶段一: JSON 代码块
        narrative, changes = cls.extract_json_code_block(raw)
        if changes:
            result["narrative"] = narrative
            result["state_changes"] = changes
            result["method"] = "codeblock"
            return result

        # 阶段二: 最大括号回溯
        narrative, changes = cls.extract_json_fallback(raw)
        if changes:
            result["narrative"] = narrative
            result["state_changes"] = changes
            result["method"] = "json_fallback"
            return result

        # 阶段三: 自然语言规则
        narrative, changes = cls.extract_from_natural_language(raw)
        if changes:
            result["narrative"] = narrative
            result["state_changes"] = changes
            result["method"] = "natural"

        return result

    # ════════════════════════════════════════
    # 阶段一: JSON 代码块
    # ════════════════════════════════════════
    @classmethod
    def extract_json_code_block(cls, raw: str) -> Tuple[str, dict]:
        """从 ```json ... ``` 代码块中提取状态变更。

        Returns:
            (narrative, state_changes)
            - narrative: 去除 JSON 块后的纯文本
            - state_changes: 解析出的变更字典，失败时为空 {}
        """
        match = cls.JSON_BLOCK_RE.search(raw)
        if not match:
            return raw.strip(), {}

        json_str = match.group(1).strip()
        narrative = raw[:match.start()].strip()

        try:
            changes = json.loads(json_str)
            if isinstance(changes, dict):
                return narrative, changes
        except json.JSONDecodeError:
            pass

        return raw.strip(), {}

    # ════════════════════════════════════════
    # 阶段二: 最大括号回溯
    # ════════════════════════════════════════
    @classmethod
    def extract_json_fallback(cls, raw: str) -> Tuple[str, dict]:
        """从文本末尾向前搜索最大合法 JSON 对象（{}）。

        算法:
        1. 从文本末尾向前扫描，找到最后一个 '}'
        2. 从该位置向前配对 '{'，记录最大合法 JSON 对象的起止位置
        3. 尝试解析该段为 JSON

        Returns:
            (narrative, state_changes)
        """
        text = raw.rstrip()

        # 找最后一个 }
        last_brace = text.rfind("}")
        if last_brace < 0:
            return raw.strip(), {}

        # 从末尾向前配对花括号
        depth = 0
        json_end = last_brace + 1
        json_start = -1

        for i in range(last_brace, -1, -1):
            ch = text[i]
            if ch == "}":
                depth += 1
            elif ch == "{":
                depth -= 1
                if depth == 0:
                    json_start = i
                    break

        if json_start < 0:
            return raw.strip(), {}

        json_str = text[json_start:json_end]
        narrative = text[:json_start].strip()

        try:
            changes = json.loads(json_str)
            if isinstance(changes, dict):
                return narrative, changes
        except json.JSONDecodeError:
            pass

        # 尝试更宽松的匹配：从找到的位置向后找完整对象
        for end in range(last_brace, max(last_brace - 500, 0), -1):
            if text[end] != "}":
                continue
            depth = 0
            for i in range(end, -1, -1):
                if text[i] == "}":
                    depth += 1
                elif text[i] == "{":
                    depth -= 1
                    if depth == 0:
                        candidate = text[i:end + 1]
                        try:
                            changes = json.loads(candidate)
                            if isinstance(changes, dict):
                                return text[:i].strip(), changes
                        except json.JSONDecodeError:
                            pass
                        break

        return raw.strip(), {}

    # ════════════════════════════════════════
    # 阶段三: 自然语言
    # ════════════════════════════════════════
    @classmethod
    def extract_from_natural_language(cls, raw: str) -> Tuple[str, dict]:
        """用正则匹配自然语言中的明确数值变化。

        匹配模式（手册规范字段）:
        - "受到 5 点伤害" → hp: -5
        - "好感度增加 10" → goodwill: +10
        - "获得了「古老的钥匙」" → inventory_add: ["古老的钥匙"]
        - "变得愤怒" → emotion: "愤怒"
        - 等等

        Returns:
            (narrative, state_changes)
        """
        changes = {}
        matched_spans = []

        for pattern, field, sign in cls.NL_PATTERNS:
            for m in pattern.finditer(raw):
                # 检查是否与已匹配的区域重叠
                overlap = any(
                    m.start() < end and m.end() > start
                    for start, end in matched_spans
                )
                if overlap:
                    continue

                matched_spans.append((m.start(), m.end()))
                value = m.group(1)

                if field in ("emotion", "bg"):
                    # 直接赋值
                    if field not in changes:
                        changes[field] = value
                elif field in ("inventory_add", "inventory_remove"):
                    # 物品列表
                    if field not in changes:
                        changes[field] = []
                    if value not in changes[field]:
                        changes[field].append(value)
                else:
                    # 数值字段: sign 决定正负，value 是绝对值
                    delta = int(value)
                    if sign == -1:
                        delta = -delta
                    changes[field] = changes.get(field, 0) + delta

        return raw.strip(), changes


# ── 便捷函数 ──

def parse_ai_response(raw: str) -> dict:
    """便捷入口: 解析 AI 响应，返回 {narrative, state_changes}。"""
    return ParserEngine.parse(raw)

