"""
Kernelsoul - GameState 数据类
手册 §3.1: 所有模块共享的强类型游戏状态，字段白名单严格限制。
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class GameState:
    """跨模块共享的单一实例游戏状态。

    序列化: state.sav 以 JSON 格式存储（人类可读）。
    加载规则: 从 JSON 重建时，缺失字段使用默认值。
    """

    # ── AI 可修改字段（白名单） ──
    hp: int = 100
    energy: int = 100
    goodwill: int = 0
    money: int = 0
    inventory: List[str] = field(default_factory=list)
    bg: str = ""           # 当前背景描述
    emotion: str = "neutral"  # 情绪标签
    cg: str = ""           # 当前触发 CG 名称

    # ── 只读字段（AI 不可修改） ──
    phase: int = 1
    max_hp: int = 100

    # 非序列化字段标记（不含序列化时跳过）
    

    def to_dict(self) -> dict:
        """导出为 JSON 可序列化字典。"""
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "GameState":
        """从字典重建 GameState，缺失字段用默认值。"""
        valid_fields = cls.__dataclass_fields__
        filtered = {}
        for k, v in d.items():
            if k in valid_fields:
                filtered[k] = v
        return cls(**filtered)

    @classmethod
    def default_state(cls, **overrides) -> "GameState":
        """创建带覆盖的默认状态。"""
        params = {
            "hp": 100, "energy": 100, "goodwill": 0, "money": 0,
            "inventory": [], "bg": "", "emotion": "neutral", "cg": "",
            "phase": 1, "max_hp": 100,
        }
        params.update(overrides)
        return cls(**params)

    def reset(self):
        """重置所有字段为默认值。"""
        self.hp = 100
        self.energy = 100
        self.goodwill = 0
        self.money = 0
        self.inventory.clear()
        self.bg = ""
        self.emotion = "neutral"
        self.cg = ""
        self.phase = 1
        self.max_hp = 100

    def __repr__(self) -> str:
        inv = ", ".join(self.inventory) if self.inventory else "空"
        return (
            f'GameState(hp={self.hp}/{self.max_hp}, energy={self.energy}, '
            f'goodwill={self.goodwill}, money={self.money}, '
            f'emotion={self.emotion}, bg={self.bg!r}, cg={self.cg!r}, '
            f'phase={self.phase}, inventory=[{inv}])'
        )


# 便捷函数
def load_state(path: str) -> GameState:
    """从 state.sav 文件加载 GameState。"""
    import json, os
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            return GameState.from_dict(json.load(f))
    return GameState()


def save_state(state: GameState, path: str):
    """将 GameState 保存到 state.sav 文件。"""
    import json, os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)