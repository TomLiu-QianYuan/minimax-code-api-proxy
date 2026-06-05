"""
daemon.js 补丁管理器
支持两种 API 格式：
- anthropic: Anthropic 兼容（/messages），用于 Mimo、Claude 等
- openai:    OpenAI 兼容（/chat/completions），用于 DeepSeek、OpenAI、SiliconFlow 等
"""

import re
import shutil
from pathlib import Path


class DaemonPatcher:
    def __init__(self, daemon_js_path: str):
        self.daemon_js = Path(daemon_js_path)
        self.backup = self.daemon_js.with_suffix(".js.bak")

    def is_patched(self) -> bool:
        if not self.daemon_js.exists():
            return False
        content = self.daemon_js.read_text(encoding="utf-8", errors="ignore")
        return "/* PATCHED BY MODEL-PROXY */" in content

    def has_backup(self) -> bool:
        return self.backup.exists()

    def backup_original(self) -> str:
        if not self.daemon_js.exists():
            raise FileNotFoundError(f"找不到 daemon.js: {self.daemon_js}")
        if self.backup.exists():
            return str(self.backup)
        shutil.copy2(self.daemon_js, self.backup)
        return str(self.backup)

    def restore(self) -> bool:
        if not self.backup.exists():
            return False
        shutil.copy2(self.backup, self.daemon_js)
        return True

    def get_current_urls(self) -> dict:
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

    def patch(self, target_url: str, target_key: str = "",
              api_type: str = "anthropic") -> dict:
        """
        修补 daemon.js
        api_type: "anthropic" 或 "openai"
        返回 {"patched": bool, "changes": list}
        """
        if not self.daemon_js.exists():
            raise FileNotFoundError(f"找不到 daemon.js: {self.daemon_js}")

        self.backup_original()

        content = self.daemon_js.read_text(encoding="utf-8", errors="ignore")
        original = content
        changes = []

        # 1. 替换所有 prod/test/staging URL
        env_keys = ["cn-prod", "en-prod", "cn-test", "cn-dev",
                    "cn-staging", "en-test", "en-dev", "en-staging"]
        for key in env_keys:
            pattern = rf'"{key}":\s*"https://[^"]+"'
            replacement = f'"{key}": "{target_url}"'
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                if key in ("cn-prod", "en-prod"):
                    changes.append(f"替换 {key} URL")
                content = new_content

        # 2. 替换 npm provider（anthropic ↔ openai）
        if api_type == "openai":
            new_content = content.replace(
                'npm: "@ai-sdk/anthropic"',
                'npm: "@ai-sdk/openai"',
            )
            if new_content != content:
                changes.append("切换为 OpenAI 格式 (@ai-sdk/openai)")
                content = new_content
        else:
            # 确保是 anthropic 格式
            new_content = content.replace(
                'npm: "@ai-sdk/openai"',
                'npm: "@ai-sdk/anthropic"',
            )
            if new_content != content:
                changes.append("切换为 Anthropic 格式 (@ai-sdk/anthropic)")
                content = new_content

        # 3. 替换 API Key
        if target_key:
            new_content = content.replace('apiKey: "sk-xxx"', f'apiKey: "{target_key}"')
            if new_content != content:
                changes.append("替换 API Key")
                content = new_content
            # 也替换之前的 key
            old_keys = re.findall(r'apiKey:\s*"tp-[a-z0-9]+"', content)
            for old_key in old_keys:
                new_content = content.replace(old_key, f'apiKey: "{target_key}"')
                if new_content != content:
                    changes.append("替换已有 API Key")
                    content = new_content

        # 4. 禁用 URL 同步保护
        old_func = "function isManagedPresetBaseUrl(baseURL) {"
        if old_func in content:
            new_func = 'function isManagedPresetBaseUrl(baseURL) {\n    /* PATCHED BY MODEL-PROXY */\n    return false;\n    if (false) {'
            new_content = content.replace(
                "function isManagedPresetBaseUrl(baseURL) {\n  if (MANAGED_PRESET_BASE_URLS.has(baseURL))",
                new_func,
                1
            )
            if new_content != content:
                changes.append("禁用 URL 同步保护")
                content = new_content

        # 5. 标记已打补丁
        if changes and "/* PATCHED BY MODEL-PROXY */" not in content:
            content = "/* PATCHED BY MODEL-PROXY */\n" + content

        if content == original:
            return {"patched": False, "changes": []}

        self.daemon_js.write_text(content, encoding="utf-8")
        return {"patched": True, "changes": changes}

    def status(self) -> dict:
        return {
            "daemon_exists": self.daemon_js.exists(),
            "is_patched": self.is_patched(),
            "has_backup": self.has_backup(),
            "current_urls": self.get_current_urls(),
            "daemon_path": str(self.daemon_js),
            "backup_path": str(self.backup),
        }
