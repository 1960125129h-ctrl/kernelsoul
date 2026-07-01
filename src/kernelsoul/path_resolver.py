"""
Kernelsoul - PathResolver 路径管理器
手册 §4.1: 动态拼接所有路径，自动创建不存在文件夹，支持角色/会话热切换。
"""
import os
from typing import Optional


class PathResolver:
    """动态路径管理器。

    所有路径由 base_saves、base_configs、active_char、active_session 四要素
    动态拼接。切换角色或会话时调用 bind() 重新绑定。
    """

    def __init__(
        self,
        base_root: str,
        active_char: str = "",
        active_session: str = "",
    ):
        self.base_root = os.path.abspath(base_root)
        self.base_saves = os.path.join(self.base_root, "saves")
        self.base_configs = os.path.join(self.base_root, "configs")
        self.base_characters = os.path.join(self.base_root, "characters")
        self.base_assets = os.path.join(self.base_root, "assets")
        self.base_plugins = os.path.join(self.base_root, "plugins")

        self.char = active_char
        self.session = active_session
        self._ensure_dirs()

    # ── 绑定与切换 ──
    def bind(self, char: str = None, session: str = None) -> "PathResolver":
        """切换角色/会话绑定，返回新实例（或修改自身）。"""
        if char is not None:
            self.char = char
        if session is not None:
            self.session = session
        self._ensure_dirs()
        return self

    def _ensure_dirs(self):
        """确保所有运行时目录存在。"""
        dirs = [
            self.get_session_dir(),
            self.get_history_dir(),
            self.get_context_dir(),
            self.get_drafts_dir(),
            self.get_saved_drafts_dir(),
        ]
        for d in dirs:
            if d:  # char/session 可能为空
                os.makedirs(d, exist_ok=True)

    # ── 基础目录 ──
    def get_root_dir(self) -> str:
        return self.base_root

    def get_saves_dir(self) -> str:
        return self.base_saves

    def get_configs_dir(self) -> str:
        return self.base_configs

    def get_characters_dir(self) -> str:
        return self.base_characters

    def get_assets_dir(self) -> str:
        return self.base_assets

    def get_plugins_dir(self) -> str:
        return self.base_plugins

    # ── 会话路径 ──
    def get_session_dir(self) -> str:
        return os.path.join(self.base_saves, self.char, self.session)

    def get_history_dir(self) -> str:
        return os.path.join(self.get_session_dir(), "history")

    def get_context_dir(self) -> str:
        return os.path.join(self.get_session_dir(), "context")

    def get_drafts_dir(self) -> str:
        return os.path.join(self.get_context_dir(), "drafts")

    def get_saved_drafts_dir(self) -> str:
        return os.path.join(self.get_context_dir(), "saved_drafts")

    # ── 核心文件路径 ──
    def get_state_file(self) -> str:
        return os.path.join(self.get_session_dir(), "state.sav")

    def get_meta_file(self) -> str:
        return os.path.join(self.get_session_dir(), "session_meta.json")

    def get_full_log(self) -> str:
        return os.path.join(self.get_history_dir(), "full_log.txt")

    def get_full_memory(self) -> str:
        return os.path.join(self.get_history_dir(), "full_memory.json")

    def get_recent_log(self) -> str:
        return os.path.join(self.get_context_dir(), "recent_log.txt")

    def get_working_memory(self) -> str:
        return os.path.join(self.get_context_dir(), "working_memory.json")

    def get_manual_memory(self) -> str:
        return os.path.join(self.get_context_dir(), "manual_memory.json")

    # ── 配置路径 ──
    def get_system_config(self) -> str:
        return os.path.join(self.base_configs, "system.json")

    def get_rules_config(self) -> str:
        return os.path.join(self.base_configs, "rules.json")

    def get_compression_prompt_light(self) -> str:
        return os.path.join(self.base_configs, "compression_prompt_light.txt")

    def get_compression_prompt_deep(self) -> str:
        return os.path.join(self.base_configs, "compression_prompt_deep.txt")

    def get_fallback_prompt(self) -> str:
        return os.path.join(self.base_configs, "fallback_prompt.txt")

    def get_rule_compiler_prompt(self) -> str:
        return os.path.join(self.base_configs, "rule_compiler_prompt.txt")

    def get_preset_dir(self) -> str:
        return os.path.join(self.base_configs, "presets")

    # ── 角色卡路径 ──
    def get_character_dir(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid)

    def get_character_data(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "character_data.json")

    def get_character_rules(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "character_rules.json")

    def get_character_dsl(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "character.dsl")

    def get_character_lorebook(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "character_lorebook.json")

    def get_character_initstate(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "character_initstate.json")

    def get_character_meta_cognition(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "meta_cognition.txt")

    def get_character_assets_dir(self, char_id: str = None) -> str:
        cid = char_id or self.char
        return os.path.join(self.base_characters, cid, "assets")

    # ── 便利方法 ──
    def resolve_draft_path(self, draft_id: int) -> str:
        """获取指定草稿文件路径。"""
        return os.path.join(self.get_drafts_dir(), f"draft_{draft_id:03d}.json")

    def get_plugin_dir(self, plugin_id: str) -> str:
        """获取插件目录。"""
        return os.path.join(self.base_plugins, plugin_id)

    def get_plugin_manifest(self, plugin_id: str) -> str:
        """获取插件清单文件。"""
        return os.path.join(self.get_plugin_dir(plugin_id), "manifest.json")

    def list_drafts(self) -> list:
        """列出所有草稿 ID（按数字排序）。"""
        drafts_dir = self.get_drafts_dir()
        if not os.path.isdir(drafts_dir):
            return []
        ids = []
        for fname in os.listdir(drafts_dir):
            if fname.startswith("draft_") and fname.endswith(".json"):
                try:
                    ids.append(int(fname.replace("draft_", "").replace(".json", "")))
                except ValueError:
                    pass
        return sorted(ids)

    def summary(self) -> str:
        """打印路径结构概览。"""
        lines = [
            f"PathResolver @ {self.base_root}",
            f"  char: {self.char or '(unset)'}",
            f"  session: {self.session or '(unset)'}",
            f"  saves → {self.base_saves}",
            f"  configs → {self.base_configs}",
            f"  characters → {self.base_characters}",
            f"  session_dir → {self.get_session_dir()}",
        ]
        return "\n".join(lines)