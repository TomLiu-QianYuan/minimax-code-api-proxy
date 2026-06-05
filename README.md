<div align="center">

<img src="https://img.shields.io/badge/MiniMax%20Code-API%20Proxy-blue?style=for-the-badge&logo=minimax" alt="MiniMax Code API Proxy">

<br>

# MiniMax Code API Proxy

**你的 MiniMax Code，你做主。**

将 MiniMax Code 内置 API 替换为任意外部 API — DeepSeek、Mimo、OpenAI、SiliconFlow、Groq... 一键切换，想用哪个用哪个。

<br>

![Windows](https://img.shields.io/badge/Windows%2011-0078D4?style=flat-square&logo=windows11&logoColor=white)
![Python](https://img.shields.io/badge/Python%203.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6%20Fluent-41CD52?style=flat-square&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Release](https://img.shields.io/github/v/release/TomLiu-QianYuan/minimax-code-api-proxy?style=flat-square)

<br>

[English](#english) · [中文](#中文) · [下载](https://github.com/TomLiu-QianYuan/minimax-code-api-proxy/releases) · [Issues](https://github.com/TomLiu-QianYuan/minimax-code-api-proxy/issues)

</div>

---

<a id="中文"></a>

## 为什么需要这个？

MiniMax Code 绑定了自家 API，无法切换到其他模型。这个工具帮你：

- **省钱** — 用 DeepSeek / Mimo 等更便宜的 API
- **自由** — 想用什么模型就用什么模型
- **安全** — 自动备份原始文件，随时一键还原
- **方便** — 最小化到系统托盘，右键快速切换

## 效果预览

```
┌─ Dashboard ───────────────────────────────────┐
│                                                │
│   ┌─────────────┐    ┌─────────────┐          │
│   │ 补丁状态     │    │ 备份状态     │          │
│   │ ● 已打补丁   │    │ ● 有备份     │          │
│   └─────────────┘    └─────────────┘          │
│   ┌─────────────┐    ┌─────────────┐          │
│   │ 当前预设     │    │ API 格式     │          │
│   │ Mimo (SGP)  │    │ Anthropic   │          │
│   └─────────────┘    └─────────────┘          │
│                                                │
│   文件路径                                     │
│   daemon.js    C:/.../daemon.js                │
│   配置文件      ./config.yaml                  │
└────────────────────────────────────────────────┘

┌─ 控制台 ──────────────────────────────────────┐
│                                                │
│   API 切换                        [ OFF / ON ] │
│   MiniMax 原版 API                               │
│                                                │
│   API 配置                                     │
│   预设  [ Mimo (SGP) ▼          ]              │
│   URL   [ https://token-plan-sgp...       ]    │
│   Key   [ tp-sdixcpi5ch8y24o5u...     👁 ]    │
│   格式  [ Anthropic (/messages) ▼     ]        │
│                                                │
│   [ 应用补丁 ]        [ 恢复原始 ]             │
└────────────────────────────────────────────────┘

┌─ 系统托盘 ────────────────────────────────────┐
│                                                │
│   ● MiniMax Code API 代理                      │
│   ├─ 切换为 Mimo (SGP)                         │
│   ├─ 切换为 Mimo (CN)                          │
│   ├─ 切换为 DeepSeek                           │
│   ├─ ─────────────                             │
│   ├─ 恢复原始 API                              │
│   ├─ 打开主窗口                                │
│   └─ 退出                                      │
│                                                │
└────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 安装依赖
pip install PyQt6 PyQt6-Fluent-Widgets pyyaml

# 2. 启动
python app.py
```

**使用步骤：**

1. 关闭 MiniMax Code
2. 打开本工具
3. 在「控制台」选择预设（Mimo / DeepSeek / OpenAI...）
4. 填入 API Key
5. 点击「应用补丁」或拨开开关
6. 重新打开 MiniMax Code

完成！MiniMax Code 现在用的是你选的 API。

**最小化到托盘：** 关闭窗口时自动最小化到系统托盘，右键托盘图标可快速切换 API 或恢复原始。

## 支持的 API

| 预设 | 格式 | 说明 | Key |
|:-----|:-----|:-----|:----|
| **Mimo (SGP)** | Anthropic | 小米 Mimo v2.5 Pro · 新加坡节点 | 自动填入 |
| **Mimo (CN)** | Anthropic | 小米 Mimo v2.5 Pro · 国内节点 | 自动填入 |
| **DeepSeek** | OpenAI | DeepSeek V3 / R1 | 手动 |
| **OpenAI** | OpenAI | GPT-4o / GPT-4o-mini | 手动 |
| **SiliconFlow** | OpenAI | 国产模型聚合 | 手动 |
| **Groq** | OpenAI | 高速推理 | 手动 |
| **One API** | OpenAI | 自建中转 | 手动 |
| **自定义** | 可选 | 任意 OpenAI / Anthropic 兼容 API | 手动 |

## 功能特性

| 功能 | 说明 |
|:-----|:-----|
| 一键切换 | 开关拨一下，即刻切换 API |
| API 格式选择 | 支持 Anthropic (`/messages`) 和 OpenAI (`/chat/completions`) 两种格式 |
| 系统托盘 | 最小化到托盘，右键快速切换预设 / 恢复原始 |
| 自动备份 | daemon.js 和 config.yaml 双重备份 |
| 一键还原 | 随时恢复原版，不留痕迹 |
| Dashboard | 实时状态总览 |
| 帮助文档 | 内置使用说明和常见问题 |
| 日志管理 | 按日期保存，3 天自动归档 .7z |
| 配置备份 | 每次打补丁自动备份 config，UI 直接还原 |
| 自动检测 | 自动查找 MiniMax Code 安装路径 |
| Fluent UI | Windows 11 原生深色主题 |

## 工作原理

```
MiniMax Code 启动
       │
       ▼
读取 daemon.js 中的 PRESET_BASE_URLS
       │
       ▼ (已打补丁)
请求发送到你配置的 API ──→ DeepSeek / Mimo / OpenAI ...
       │
       ▼ (未打补丁)
请求发送到 MiniMax 官方 API
```

补丁修改 `daemon.js` 中的 3 处：
1. `PRESET_BASE_URLS` → 替换为目标 API 地址
2. `isManagedPresetBaseUrl()` → 禁用 URL 同步保护
3. `npm` 包引用 → 根据格式切换 `@ai-sdk/anthropic` 或 `@ai-sdk/openai`

## 项目结构

```
model-proxy/
├── app.py              # 主程序 (PyQt6 GUI + 系统托盘)
├── patcher.py          # daemon.js 补丁引擎
├── config_backup.py    # 配置备份管理
├── log_manager.py      # 日志管理 (按日期 + .7z 归档)
├── config.yaml         # 用户配置
├── requirements.txt    # Python 依赖
├── LICENSE             # MIT
└── README.md
```

## 常见问题

**Q: 打补丁后 MiniMax Code 报错？**
A: 确认你选的 API 地址和 Key 正确，且 API 支持对应格式（Anthropic / OpenAI）。

**Q: MiniMax Code 更新后补丁失效？**
A: 更新会覆盖 `daemon.js`，重新打一次补丁即可。

**Q: 怎么完全恢复？**
A: 拨回 OFF、点「恢复原始」、或右键托盘图标选「恢复原始 API」。

**Q: 配置文件搞乱了？**
A: 日志页 → 配置备份 → 选择之前的备份 → 还原。

**Q: 怎么彻底退出？**
A: 右键系统托盘图标 → 退出。或在主窗口关闭后从托盘退出。

## Star History

如果这个项目帮到了你，请点个 Star 支持一下！

---

<div align="center">

**Made with Claude** · Anthropic AI Assistant

</div>

---

<a id="english"></a>

## English

### What is this?

Replaces MiniMax Code's built-in API with any external API endpoint (DeepSeek, Mimo, OpenAI, etc.). One-click switch, auto backup, system tray, Fluent UI.

### Quick Start

```bash
pip install PyQt6 PyQt6-Fluent-Widgets pyyaml
python app.py
```

1. Close MiniMax Code
2. Open this tool, select a preset
3. Fill in your API Key
4. Toggle ON
5. Reopen MiniMax Code

### Features

- One-click API switching with toggle
- API format selector: Anthropic (`/messages`) and OpenAI (`/chat/completions`)
- System tray: minimize to tray, right-click to quick-switch presets or restore original
- Built-in presets: Mimo, DeepSeek, OpenAI, SiliconFlow, Groq, One API
- Auto backup daemon.js + config.yaml before patching
- One-click restore
- Dashboard with real-time status
- Built-in help and FAQ
- Log management with date-based archiving (.7z)
- Config backup/restore from UI
- Auto-detect MiniMax Code installation
- Windows 11 Fluent dark theme

### Supported APIs

| Preset | Format | Description | Key |
|:-------|:-------|:------------|:----|
| **Mimo (SGP)** | Anthropic | Xiaomi Mimo v2.5 Pro (Singapore) | Pre-filled |
| **Mimo (CN)** | Anthropic | Xiaomi Mimo v2.5 Pro (China) | Pre-filled |
| **DeepSeek** | OpenAI | DeepSeek V3 / R1 | Manual |
| **OpenAI** | OpenAI | GPT-4o / GPT-4o-mini | Manual |
| **SiliconFlow** | OpenAI | Chinese model aggregator | Manual |
| **Groq** | OpenAI | High-speed inference | Manual |
| **One API** | OpenAI | Self-hosted relay | Manual |
| **Custom** | Choose | Any OpenAI / Anthropic compatible | Manual |

### License

MIT

---

<div align="center">

**Made with Claude** · Anthropic AI Assistant

</div>
