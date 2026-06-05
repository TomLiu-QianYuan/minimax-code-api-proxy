<div align="center">

# MiniMax Code API Proxy

**将 MiniMax Code 的内置 API 替换为你自己的外部 API**

桌面 GUI 工具，一键修补 MiniMax Code 的 `daemon.js`，将 API 请求重定向到任意 OpenAI / Anthropic 兼容端点。

[English](#english) | 中文

![Platform](https://img.shields.io/badge/platform-Windows%2011-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-green?style=flat-square)
![Model](https://img.shields.io/badge/model-mimo--v2.5--pro-purple?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)

</div>

---

## 功能特性

- **一键切换** — 开关拨一下，即刻在 MiniMax 原版和自定义 API 之间切换
- **内置预设** — Mimo、DeepSeek、OpenAI、SiliconFlow、Groq、One API 开箱即用
- **自动备份** — 修改前自动备份原始 `daemon.js`，一键恢复
- **Fluent 风格** — Windows 11 原生深色主题，PyQt6 + PyQt-Fluent-Widgets
- **Dashboard** — 实时状态总览：补丁状态、备份状态、当前预设、目标 URL
- **网格布局** — 标签右对齐，输入框整齐排列，不拥挤不重叠

## 快速开始

### 安装依赖

```bash
pip install PyQt6 PyQt6-Fluent-Widgets pyyaml
```

### 启动

```bash
python app.py
```

### 使用步骤

1. 关闭 MiniMax Code
2. 打开本工具，查看 **Dashboard** 确认状态
3. 切到 **控制台**，选择预设（如 Mimo、DeepSeek）
4. 填入 API Key
5. 将开关拨到 **ON** — 补丁自动应用
6. 重新打开 MiniMax Code — 现在它用你的 API 了

随时拨回 **OFF** 即可恢复原版。

## 支持的预设

| 预设 | Base URL | API Key |
|------|----------|---------|
| **Mimo (SGP)** | `token-plan-sgp.xiaomimimo.com/anthropic` | 自动填入 |
| **Mimo (CN)** | `token-plan-cn.xiaomimimo.com/anthropic` | 自动填入 |
| **DeepSeek** | `api.deepseek.com/v1` | 手动填写 |
| **OpenAI** | `api.openai.com/v1` | 手动填写 |
| **SiliconFlow** | `api.siliconflow.cn/v1` | 手动填写 |
| **Groq** | `api.groq.com/openai/v1` | 手动填写 |
| **One API** | `localhost:3000/v1` | 手动填写 |

## 界面预览

```
┌─ Dashboard ──────────────────────────────┐
│  总览                                     │
│  ┌───────────┐  ┌───────────┐            │
│  │ 补丁状态   │  │ 备份状态   │            │
│  │ 已打补丁   │  │ 有备份     │            │
│  └───────────┘  └───────────┘            │
│  ┌───────────┐  ┌───────────┐            │
│  │ 当前预设   │  │ 目标 URL   │            │
│  │ Mimo SGP  │  │ token...  │            │
│  └───────────┘  └───────────┘            │
│                                           │
│  文件路径                                 │
│  daemon.js:   C:/.../daemon.js            │
│  备份文件:    C:/.../daemon.js.bak        │
│  配置文件:    ./config.yaml               │
└───────────────────────────────────────────┘

┌─ 控制台 ─────────────────────────────────┐
│  API 切换                                 │
│  Mimo (SGP) API               [ ====== ]  │
│                                           │
│  API 配置                                 │
│  预设  [ Mimo (SGP)                 ▼ ]   │
│  URL   [ https://token-plan-sgp...     ]   │
│  Key   [ tp-sdixcpi5ch8y...         👁 ]  │
│                                           │
│  [ 应用补丁 ]  [ 恢复原始 ]               │
└───────────────────────────────────────────┘
```

## 工作原理

工具修补 MiniMax Code 的 `daemon.js` 文件：

1. **备份**原始 `daemon.js` → `daemon.js.bak`
2. **替换** `PRESET_BASE_URLS` 为目标 API 地址
3. **禁用** `syncManagedPresetBaseUrl()` 防止启动时重置
4. **替换** API Key 占位符

补丁可逆 — 拨回 OFF 或点「恢复」即可还原。

## 项目结构

```
model-proxy/
├── app.py           # PyQt6 桌面 GUI (Dashboard / 控制台 / 日志)
├── patcher.py       # daemon.js 补丁/恢复逻辑
├── config.yaml      # 用户配置
├── requirements.txt # Python 依赖
├── README.md        # 本文档
├── LICENSE          # MIT 许可证
└── .gitignore
```

## 注意事项

- 打补丁前请关闭 MiniMax Code
- MiniMax Code 更新会覆盖 `daemon.js`，需重新打补丁
- 工具启动时自动检测补丁状态

## 许可证

MIT

---

<div align="center">

**由 Claude 构建** — Anthropic AI 助手

</div>

---

<a id="english"></a>

## English

### What is this?

A desktop GUI tool that replaces MiniMax Code's built-in API endpoint with your own external API (DeepSeek, OpenAI, Mimo, etc.).

### Features

- **One-click toggle** — Switch between MiniMax default and custom API instantly
- **Built-in presets** — Mimo, DeepSeek, OpenAI, SiliconFlow, Groq, One API
- **Auto backup** — Original file backed up before patching, one-click restore
- **Fluent UI** — Windows 11 native dark theme, PyQt6 + PyQt-Fluent-Widgets
- **Dashboard** — Real-time status overview
- **Grid layout** — Clean, aligned interface

### Quick Start

```bash
pip install PyQt6 PyQt6-Fluent-Widgets pyyaml
python app.py
```

1. Close MiniMax Code
2. Open this tool, check **Dashboard** for status
3. Go to **Control**, select a preset
4. Fill in your API Key
5. Toggle switch **ON** — patch applied
6. Reopen MiniMax Code

Toggle **OFF** to restore original at any time.

### Supported Presets

| Preset | Base URL | API Key |
|--------|----------|---------|
| **Mimo (SGP)** | `token-plan-sgp.xiaomimimo.com/anthropic` | Pre-filled |
| **Mimo (CN)** | `token-plan-cn.xiaomimimo.com/anthropic` | Pre-filled |
| **DeepSeek** | `api.deepseek.com/v1` | Manual |
| **OpenAI** | `api.openai.com/v1` | Manual |
| **SiliconFlow** | `api.siliconflow.cn/v1` | Manual |
| **Groq** | `api.groq.com/openai/v1` | Manual |
| **One API** | `localhost:3000/v1` | Manual |

### How It Works

1. Backs up `daemon.js` → `daemon.js.bak`
2. Replaces `PRESET_BASE_URLS` with your target URL
3. Disables `syncManagedPresetBaseUrl()` to prevent reset
4. Replaces API key placeholder

Patch is reversible — toggle OFF or click "Restore".

### License

MIT

---

<div align="center">

**Built by Claude** — AI assistant by Anthropic

</div>
