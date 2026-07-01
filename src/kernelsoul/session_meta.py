"""
Kernelsoul - SessionMeta 会话元数据
手册 §3.4: 会话元数据结构，含数据版本号用于存档迁移。
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


# 当前数据格式版本（用于存档迁移判断）
CURRENT_DATA_VERSION = 1


@dataclass
class SessionMeta:
    """会话元数据，持久化到 session_meta.json。

    手册约定:
    - data_version: 数据格式版本号，用于存档迁移兼容性判断
    - created_at: 会话创建时间 (ISO 8601 UTC)
    - last_saved_at: 最后保存时间
    - total_rounds: 已完成回合总数
    - character_name: 当前角色名称
    - session_id: 会话标识符
    """

    data_version: int = CURRENT_DATA_VERSION
    created_at: str = ""
    last_saved_at: str = ""
    total_rounds: int = 0
    character_name: str = ""
    session_id: str = "session_01"

    # V2.0 预留字段（手册 §3.4 末尾）
    active_characters: list = None
    primary_character: str = ""

    def __post_init__(self):
        if self.active_characters is None:
            self.active_characters = []

    def touch(self):
        """更新最后保存时间为当前 UTC 时间。"""
        self.last_saved_at = datetime.now(timezone.utc).isoformat()

    def increment_rounds(self, n: int = 1):
        """增加回合计数。"""
        self.total_rounds += n
        self.touch()

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}

    @classmethod
    def create(cls, character_name: str = "", session_id: str = "session_01") -> "SessionMeta":
        """创建新会话元数据（自动填充 created_at）。"""
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            data_version=CURRENT_DATA_VERSION,
            created_at=now,
            last_saved_at=now,
            character_name=character_name,
            session_id=session_id,
        )

    @classmethod
    def from_dict(cls, d: dict) -> "SessionMeta":
        """从字典重建，处理版本迁移。"""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in valid_fields}

        version = filtered.get("data_version", 0)
        if version < CURRENT_DATA_VERSION:
            filtered = cls._migrate(filtered, version)

        return cls(**filtered)

    @classmethod
    def _migrate(cls, d: dict, from_version: int) -> dict:
        """存档版本迁移（预留）。"""
        # v0 → v1: 无变化（首次正式化）
        return d


# ── 便捷读写 ──

def load_meta(path: str) -> SessionMeta:
    """从 session_meta.json 加载。文件不存在返回新的默认实例。"""
    import json, os
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            return SessionMeta.from_dict(json.load(f))
    return SessionMeta()


def save_meta(meta: SessionMeta, path: str):
    """保存 SessionMeta 到 session_meta.json。"""
    import json, os
    meta.touch()  # 自动更新时间戳
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta.to_dict(), f, ensure_ascii=False, indent=2)

