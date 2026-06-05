<div align="center">

# MiniMax Code API Proxy

**Replace the built-in API of MiniMax Code with your own external API**

A desktop GUI tool that patches MiniMax Code's `daemon.js` to redirect API calls to any OpenAI / Anthropic compatible endpoint.

![Platform](https://img.shields.io/badge/platform-Windows%2011-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-green?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)

</div>

---

## Features

- **One-click switch** — Toggle between MiniMax default and custom API with a single switch
- **Built-in presets** — Mimo, DeepSeek, OpenAI, SiliconFlow, Groq, One API pre-configured
- **Auto backup** — Original `daemon.js` is backed up before patching, one-click restore
- **Fluent UI** — Native Windows 11 style with dark theme, powered by PyQt6 + PyQt-Fluent-Widgets
- **Dashboard** — Real-time status overview with patch state, backup info, and file paths
- **Grid layout** — Clean, responsive interface with proper alignment and spacing

## Quick Start

### Install

```bash
pip install PyQt6 PyQt6-Fluent-Widgets pyyaml
```

### Run

```bash
python app.py
```

### Usage

1. Close MiniMax Code
2. Open this tool, go to **Dashboard** to check status
3. Go to **Control**, select a preset (e.g. Mimo, DeepSeek)
4. Fill in your API Key
5. Toggle the switch **ON** — patch applied automatically
6. Reopen MiniMax Code — it now uses your custom API

Toggle **OFF** to restore the original MiniMax API at any time.

## Screenshots

```
┌─ Dashboard ─────────────────────────────┐
│  总览                                    │
│  ┌──────────┐  ┌──────────┐             │
│  │ 补丁状态  │  │ 备份状态  │             │
│  │ 已打补丁  │  │ 有备份    │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ 当前预设  │  │ 目标 URL  │             │
│  │ Mimo SGP │  │ token... │             │
│  └──────────┘  └──────────┘             │
│                                          │
│  文件路径                                │
│  daemon.js:  C:/.../daemon.js            │
│  备份文件:   C:/.../daemon.js.bak        │
│  配置文件:   ./config.yaml               │
└──────────────────────────────────────────┘

┌─ Control ────────────────────────────────┐
│  API 切换                                │
│  Mimo (SGP) API              [ ====== ]  │
│                                          │
│  API 配置                                │
│  预设  [ Mimo (SGP)                ▼ ]   │
│  URL   [ https://token-plan-sgp...    ]   │
│  Key   [ tp-sdixcpi5ch8y...        👁 ]  │
│                                          │
│  [ 应用补丁 ]  [ 恢复原始 ]              │
└──────────────────────────────────────────┘
```

## Supported Presets

| Preset | Base URL | API Key |
|--------|----------|---------|
| **Mimo (SGP)** | `token-plan-sgp.xiaomimimo.com/anthropic` | Pre-filled |
| **Mimo (CN)** | `token-plan-cn.xiaomimimo.com/anthropic` | Pre-filled |
| **DeepSeek** | `api.deepseek.com/v1` | Manual |
| **OpenAI** | `api.openai.com/v1` | Manual |
| **SiliconFlow** | `api.siliconflow.cn/v1` | Manual |
| **Groq** | `api.groq.com/openai/v1` | Manual |
| **One API** | `localhost:3000/v1` | Manual |

## How It Works

The tool patches MiniMax Code's `daemon.js` file:

1. **Backs up** the original `daemon.js` → `daemon.js.bak`
2. **Replaces** `PRESET_BASE_URLS` with your target API URL
3. **Disables** `syncManagedPresetBaseUrl()` to prevent URL reset on startup
4. **Replaces** the API key placeholder

The patch is reversible — toggle OFF or click "Restore" to undo.

## Project Structure

```
model-proxy/
├── app.py           # PyQt6 desktop GUI
├── patcher.py       # daemon.js patch/restore logic
├── config.yaml      # User configuration
├── requirements.txt # Python dependencies
└── README.md
```

## Notes

- Close MiniMax Code before applying patches
- After MiniMax Code updates, re-apply the patch (the update overwrites `daemon.js`)
- The tool auto-detects patch state on startup

## License

MIT

---

<div align="center">

**Built by Claude** — An AI assistant by Anthropic

</div>
