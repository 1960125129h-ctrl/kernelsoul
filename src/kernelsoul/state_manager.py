"""
Kernelsoul - StateManager 状态管理器
手册 §3.2: 基于 PathResolver 读写 state.sav，提供 apply_state_changes()
方法，内部校验白名单、执行加减法/背包增删、内置容错逻辑。
"""
import json
import os
from typing import List, Optional
from game_state import GameState, load_state, save_state
from path_resolver import PathResolver


class StateManager:
    """游戏状态管理器。

    职责:
    - 从 state.sav 加载/保存 GameState
    - 应用 AI 返回的状态变更（白名单校验）
    - 背包增删（含容错逻辑）
    - 提供受控的字段修改方法（防越权）
    """

    # 手册定义: AI 可直接赋值的字段
    AI_WRITABLE_INT = {"hp", "energy", "goodwill", "money"}
    AI_WRITABLE_STR = {"bg", "emotion", "cg"}
    # 所有合法写入字段
    AI_WRITABLE = AI_WRITABLE_INT | AI_WRITABLE_STR

    def __init__(self, paths: PathResolver):
        self.paths = paths
        self.state = self._load()

    # ── 基础读写 ──
    def _load(self) -> GameState:
        """从 state.sav 加载，文件不存在则返回默认状态。"""
        f = self.paths.get_state_file()
        if os.path.exists(f):
            return load_state(f)
        return GameState()

    def save(self):
        """保存当前状态到 state.sav。"""
        save_state(self.state, self.paths.get_state_file())

    def reload(self):
        """重新从文件加载（丢弃内存中的未保存变更）。"""
        self.state = self._load()

    def reset(self):
        """重置为默认状态并保存。"""
        self.state = GameState()
        self.save()

    # ── 受控字段修改（防越权） ──
    def modify_hp(self, delta: int):
        """受控修改 HP，自动钳制到 [0, max_hp]。"""
        self.state.hp = max(0, min(self.state.max_hp, self.state.hp + delta))

    def modify_energy(self, delta: int):
        """受控修改能量。"""
        self.state.energy = max(0, min(100, self.state.energy + delta))

    def modify_goodwill(self, delta: int):
        self.state.goodwill += delta

    def modify_money(self, delta: int):
        """受控修改金币，不低于 0。"""
        self.state.money = max(0, self.state.money + delta)

    def set_bg(self, bg: str):
        self.state.bg = bg

    def set_emotion(self, emotion: str):
        self.state.emotion = emotion

    def set_cg(self, cg: str):
        self.state.cg = cg

    def set_phase(self, phase: int):
        """只读字段仅有特殊模块（进化触发器）可调用。"""
        self.state.phase = phase

    # ── 背包操作（容错逻辑） ──
    def add_item(self, item: str):
        """添加物品。"""
        if item and item not in self.state.inventory:
            self.state.inventory.append(item)

    def remove_item(self, item: str) -> bool:
        """移除物品。不存在时返回 False 并记录日志（不抛异常）。"""
        if item in self.state.inventory:
            self.state.inventory.remove(item)
            return True
        else:
            # 手册规定: remove 时物品不存在，忽略此条并写日志
            print(f"[StateManager.WARN] 背包中不存在 '{item}'，已忽略删除指令")
            return False

    def has_item(self, item: str) -> bool:
        return item in self.state.inventory

    # ── AI 状态变更应用（手册 §3.2 协议） ──
    def apply_state_changes(self, changes: dict) -> list:
        """执行 AI 返回的 state_changes 字典，返回操作日志。

        处理顺序严格按照手册:
        1. inventory_remove 先执行
        2. inventory_add 再执行
        3. 其他合法字段直接赋值/增量

        白名单校验: 非法字段直接丢弃，不抛异常。
        """
        log_lines = []

        # ── 1. 先移除物品 ──
        removes = changes.get("inventory_remove", [])
        if isinstance(removes, str):
            removes = [removes]
        for item in removes:
            if self.remove_item(item):
                log_lines.append(f"[OK] 背包移除: '{item}'")
            else:
                log_lines.append(f"[SKIP] 背包移除 '{item}' 失败: 不存在")

        # ── 2. 再添加物品 ──
        adds = changes.get("inventory_add", [])
        if isinstance(adds, str):
            adds = [adds]
        for item in adds:
            if item and item not in self.state.inventory:
                self.state.inventory.append(item)
                log_lines.append(f"[OK] 背包添加: '{item}'")
            else:
                log_lines.append(f"[SKIP] 背包添加 '{item}': 已存在")

        # ── 3. 其他字段 ──
        for key, value in changes.items():
            if key in ("inventory_add", "inventory_remove"):
                continue  # 已处理

            if key not in self.AI_WRITABLE:
                log_lines.append(f"[SKIP] {key} 不在 AI 可修改白名单")
                continue

            current = getattr(self.state, key, None)

            if key in self.AI_WRITABLE_INT and isinstance(current, int):
                # 数值字段: 增量模式
                new_val = current + int(value)
                setattr(self.state, key, new_val)
                log_lines.append(f"[OK] {key}: {current} -> {new_val}")

            elif key in self.AI_WRITABLE_STR and isinstance(current, str):
                # 字符串字段: 直接赋值
                if value and value != current:
                    setattr(self.state, key, str(value))
                    log_lines.append(f"[OK] {key}: '{current}' -> '{value}'")

            elif isinstance(current, list) and key == "inventory":
                # inventory 字段直接赋值（整表替换，谨慎使用）
                if isinstance(value, list):
                    self.state.inventory = value
                    log_lines.append(f"[OK] inventory: 整表替换为 {len(value)} 件物品")

        return log_lines

    # ── 状态摘要 ──
    def state_text(self) -> str:
        """生成可注入 Prompt 的状态文本。"""
        s = self.state
        inv = ", ".join(s.inventory) if s.inventory else "空"
        return (
            f"HP: {s.hp}/{s.max_hp} | 能量: {s.energy} | "
            f"好感度: {s.goodwill} | 金币: {s.money} | "
            f"情绪: {s.emotion} | 阶段: {s.phase} | "
            f"场景: {s.bg or '默认'} | "
            f"背包: [{inv}]"
        )

    def summary(self) -> str:
        return (
            f"StateManager(char={self.paths.char}, session={self.paths.session})\n"
            f"  {self.state_text()}"
        )