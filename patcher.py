"""
daemon.js 补丁管理器
负责备份、修补、恢复 MiniMax Code 的 daemon.js
"""

import os
import re
import shutil
from pathlib import Path


class DaemonPatcher:
    def __init__(self, daemon_js_path: str):
        self.daemon_js = Path(daemon_js_path)
        self.backup = self.daemon_js.with_suffix(".js.bak")

    def is_patched(self) -> bool:
        """检查是否已经打过补丁"""
        if not self.daemon_js.exists():
            return False
        content = self.daemon_js.read_text(encoding="utf-8", errors="ignore")
        return "/* PATCHED BY MODEL-PROXY */" in content

    def has_backup(self) -> bool:
        """检查是否有备份"""
        return self.backup.exists()

    def backup_original(self) -> str:
        """备份原始文件，返回备份路径"""
        if not self.daemon_js.exists():
            raise FileNotFoundError(f"找不到 daemon.js: {self.daemon_js}")
        if self.backup.exists():
            return str(self.backup)
        shutil.copy2(self.daemon_js, self.backup)
        return str(self.backup)

    def restore(self) -> bool:
        """从备份恢复原始文件"""
        if not self.backup.exists():
            return False
        shutil.copy2(self.backup, self.daemon_js)
        return True

    def get_current_urls(self) -> dict:
        """获取当前 daemon.js 中的 API URL"""
        if not self.daemon_js.exists():
            return {}
        content = self.daemon_js.read_text(encoding="utf-8", errors="ignore")

        urls = {}
        patterns = [
            (r'"cn-prod":\s*"(https://[^"]+)"', "cn-prod"),
            (r'"en-prod":\s*"(https://[^"]+)"', "en-prod"),
            (r'"cn-test":\s*"(https://[^"]+)"', "cn-test"),
            (r'"cn-staging":\s*"(https://[^"]+)"', "cn-staging"),
        ]
        for pattern, key in patterns:
            m = re.search(pattern, content)
            if m:
                urls[key] = m.group(1)
        return urls

    def patch(self, target_url: str, target_key: str = "") -> dict:
        """
        修补 daemon.js，替换 API URL
        返回 {"patched": bool, "changes": list}
        """
        if not self.daemon_js.exists():
            raise FileNotFoundError(f"找不到 daemon.js: {self.daemon_js}")

        # 先备份
        self.backup_original()

        content = self.daemon_js.read_text(encoding="utf-8", errors="ignore")
        original = content

        changes = []

        # 1. 替换 PRESET_BASE_URLS 中的所有 prod URL
        url_replacements = [
            (r'"cn-prod":\s*"https://[^"]+"', f'"cn-prod": "{target_url}"'),
            (r'"en-prod":\s*"https://[^"]+"', f'"en-prod": "{target_url}"'),
        ]
        for pattern, replacement in url_replacements:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                key = re.search(r'"(\w+-\w+)":', pattern).group(1)
                changes.append(f"替换 {key} URL → {target_url}")
                content = new_content

        # 2. 替换 test/staging URL（可选，保持一致）
        staging_replacements = [
            (r'"cn-test":\s*"https://[^"]+"', f'"cn-test": "{target_url}"'),
            (r'"cn-dev":\s*"https://[^"]+"', f'"cn-dev": "{target_url}"'),
            (r'"cn-staging":\s*"https://[^"]+"', f'"cn-staging": "{target_url}"'),
            (r'"en-test":\s*"https://[^"]+"', f'"en-test": "{target_url}"'),
            (r'"en-dev":\s*"https://[^"]+"', f'"en-dev": "{target_url}"'),
            (r'"en-staging":\s*"https://[^"]+"', f'"en-staging": "{target_url}"'),
        ]
        for pattern, replacement in staging_replacements:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append("替换 staging/test URL")
                content = new_content

        # 3. 替换 API Key 占位符
        if target_key:
            new_content = content.replace('apiKey: "sk-xxx"', f'apiKey: "{target_key}"')
            if new_content != content:
                changes.append("替换 API Key")
                content = new_content

        # 4. 禁用 syncManagedPresetBaseUrl（防止启动时重置 URL）
        # 将 isManagedPresetBaseUrl 函数改为始终返回 false
        old_func = "function isManagedPresetBaseUrl(baseURL) {"
        if old_func in content:
            # 在函数开头插入 return false
            new_func = 'function isManagedPresetBaseUrl(baseURL) {\n    /* PATCHED BY MODEL-PROXY */\n    return false;\n    if (false) {'
            new_content = content.replace(
                "function isManagedPresetBaseUrl(baseURL) {\n  if (MANAGED_PRESET_BASE_URLS.has(baseURL))",
                new_func,
                1
            )
            if new_content != content:
                changes.append("禁用 URL 同步保护")
                content = new_content

        # 标记已打补丁
        if changes and "/* PATCHED BY MODEL-PROXY */" not in content:
            content = "/* PATCHED BY MODEL-PROXY */\n" + content

        if content == original:
            return {"patched": False, "changes": []}

        self.daemon_js.write_text(content, encoding="utf-8")
        return {"patched": True, "changes": changes}

    def status(self) -> dict:
        """获取当前状态"""
        return {
            "daemon_exists": self.daemon_js.exists(),
            "is_patched": self.is_patched(),
            "has_backup": self.has_backup(),
            "current_urls": self.get_current_urls(),
            "daemon_path": str(self.daemon_js),
            "backup_path": str(self.backup),
        }
