"""
MiniMax Code API 代理管理平台 (桌面版)
启动: python app.py
"""

import sys
from pathlib import Path

import yaml
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLabel, QLineEdit, QSystemTrayIcon, QMenu, QScrollArea,
)
from qfluentwidgets import (
    FluentWindow, FluentIcon as FIF, SubtitleLabel, BodyLabel,
    CaptionLabel, PrimaryPushButton, PushButton, LineEdit,
    PlainTextEdit, ComboBox, InfoBar, InfoBarPosition,
    Theme, setTheme, setThemeColor, TransparentPushButton,
    ToolButton, HeaderCardWidget, SwitchButton,
    StrongBodyLabel,
)

from patcher import DaemonPatcher
import log_manager
import config_backup

# ── 配置 ──────────────────────────────────────────────────────────────

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)


API_PRESETS = {
    "Mimo (SGP)": {
        "url": "https://token-plan-sgp.xiaomimimo.com/anthropic",
        "key": "tp-sdixcpi5ch8y24o5u0fdmd1f17euypf2o6bcgxajoz32vhwf",
        "type": "anthropic",
    },
    "Mimo (CN)": {
        "url": "https://token-plan-cn.xiaomimimo.com/anthropic",
        "key": "tp-civ3ul3w09m1divicib5gsirnkkyf0dxhme7s2ybqih4y6fm",
        "type": "anthropic",
    },
    "DeepSeek":    {"url": "https://api.deepseek.com/v1",      "type": "openai"},
    "OpenAI":      {"url": "https://api.openai.com/v1",         "type": "openai"},
    "SiliconFlow": {"url": "https://api.siliconflow.cn/v1",     "type": "openai"},
    "One API":     {"url": "http://localhost:3000/v1",           "type": "openai"},
    "Groq":        {"url": "https://api.groq.com/openai/v1",    "type": "openai"},
    "自定义":      {"url": "",                                    "type": "openai"},
}


# ── 后台线程 ──────────────────────────────────────────────────────────


class PatchWorker(QThread):
    finished = pyqtSignal(bool, str, list)

    def __init__(self, patcher, url, key, api_type="anthropic"):
        super().__init__()
        self.patcher = patcher
        self.url = url
        self.key = key
        self.api_type = api_type

    def run(self):
        try:
            result = self.patcher.patch(self.url, self.key, self.api_type)
            if result["patched"]:
                self.finished.emit(True, "补丁已应用", result["changes"])
            else:
                self.finished.emit(False, "没有需要修改的内容", [])
        except Exception as e:
            self.finished.emit(False, str(e), [])


class RestoreWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, patcher):
        super().__init__()
        self.patcher = patcher

    def run(self):
        try:
            if self.patcher.restore():
                self.finished.emit(True, "已恢复原始文件")
            else:
                self.finished.emit(False, "没有找到备份文件")
        except Exception as e:
            self.finished.emit(False, str(e))


# ── 主窗口 ────────────────────────────────────────────────────────────


def detect_minimax_dir() -> Path | None:
    """自动检测 MiniMax Code 安装目录"""
    candidates = [
        Path.home() / "AppData/Local/Programs/MiniMax Code",
        Path.home() / "AppData/Local/Programs/minimax-code",
        Path(r"C:\Program Files\MiniMax Code"),
        Path(r"C:\Program Files (x86)\MiniMax Code"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()

        # 自动检测安装目录
        install_dir = self.config.get("minimax", {}).get("install_dir", "")
        if not install_dir:
            detected = detect_minimax_dir()
            if detected:
                install_dir = str(detected)
                self.config.setdefault("minimax", {})["install_dir"] = install_dir
                save_config(self.config)

        daemon_js = self.config.get("minimax", {}).get(
            "daemon_js", "resources/resources/daemon/daemon.js"
        )
        self.patcher = DaemonPatcher(Path(install_dir) / daemon_js)

        self.setWindowTitle("MiniMax Code API 代理")
        self.resize(620, 480)
        self.setMinimumSize(500, 400)

        # Tab 1: Dashboard
        self.page_dash = QWidget()
        self.page_dash.setObjectName("dash")
        self._build_dashboard()
        self.addSubInterface(self.page_dash, FIF.HOME, "Dashboard")

        # Tab 2: 控制台
        self.page_control = QWidget()
        self.page_control.setObjectName("control")
        self._build_control()
        self.addSubInterface(self.page_control, FIF.PLAY, "控制台")

        # Tab 3: 日志
        self.page_log = QWidget()
        self.page_log.setObjectName("log")
        self._build_log()
        self.addSubInterface(self.page_log, FIF.CHAT, "日志")

        # Tab 4: 帮助
        self.page_help = QWidget()
        self.page_help.setObjectName("help")
        self._build_help()
        self.addSubInterface(self.page_help, FIF.HELP, "帮助")

        # ── 系统托盘 ──
        self._setup_tray()

        self._load_config()
        self._refresh()
        self._refresh_dash()

        # 启动时自动归档旧日志
        archived = log_manager.archive_old_logs()
        if archived:
            self._log(f"[归档] 已归档 {len(archived)} 个旧日志")
        self._refresh_log_list()

    # ── Dashboard ─────────────────────────────────────────────────────

    def _build_dashboard(self):
        root = QVBoxLayout(self.page_dash)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(18)

        # ── 状态概览（2列网格卡片） ──
        overview = HeaderCardWidget(self)
        overview.setTitle("总览")
        g = QGridLayout()
        g.setContentsMargins(16, 12, 16, 16)
        g.setHorizontalSpacing(16)
        g.setVerticalSpacing(12)

        self.dash_patch = QLabel()
        self.dash_backup = QLabel()
        self.dash_preset = QLabel()
        self.dash_url = QLabel()
        self.dash_format = QLabel()

        self._dash_cell(g, 0, 0, "补丁状态", self.dash_patch)
        self._dash_cell(g, 0, 1, "备份状态", self.dash_backup)
        self._dash_cell(g, 1, 0, "当前预设", self.dash_preset)
        self._dash_cell(g, 1, 1, "API 格式", self.dash_format)
        self._dash_cell(g, 2, 0, "目标 URL", self.dash_url)

        g.setColumnStretch(0, 1)
        g.setColumnStretch(1, 1)
        g.setRowMinimumHeight(0, 56)
        g.setRowMinimumHeight(1, 56)
        g.setRowMinimumHeight(2, 56)

        overview.viewLayout.addLayout(g)
        root.addWidget(overview)

        # ── 文件信息 ──
        info = HeaderCardWidget(self)
        info.setTitle("文件路径")
        ig = QGridLayout()
        ig.setContentsMargins(16, 12, 16, 16)
        ig.setHorizontalSpacing(12)
        ig.setVerticalSpacing(8)

        paths = [
            ("daemon.js", str(self.patcher.daemon_js)),
            ("备份文件", str(self.patcher.backup)),
            ("配置文件", str(CONFIG_PATH)),
        ]
        for i, (label, path) in enumerate(paths):
            ig.addWidget(self._label(label), i, 0)
            val = CaptionLabel(path)
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val.setStyleSheet("color:#a5b4fc;font-family:Consolas,monospace;font-size:11px;")
            ig.addWidget(val, i, 1)

        ig.setColumnStretch(1, 1)
        info.viewLayout.addLayout(ig)
        root.addWidget(info)

        # ── 快捷操作 ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn1 = TransparentPushButton("刷新")
        btn1.setMinimumHeight(34)
        btn1.clicked.connect(self._refresh_dash)
        btn_row.addWidget(btn1)
        root.addLayout(btn_row)

    def _dash_cell(self, grid, row, col, title, value_label):
        """Dashboard 状态单元格"""
        cell = QVBoxLayout()
        t = CaptionLabel(title)
        t.setStyleSheet("color:#666;")
        cell.addWidget(t)
        value_label.setStyleSheet("font-size:14px;font-weight:600;color:#888;")
        cell.addWidget(value_label)
        grid.addLayout(cell, row, col)

    def _refresh_dash(self):
        s = self.patcher.status()

        # 补丁
        if s["is_patched"]:
            self.dash_patch.setText("已打补丁")
            self.dash_patch.setStyleSheet("font-size:14px;font-weight:600;color:#4ade80;")
        else:
            self.dash_patch.setText("未修改")
            self.dash_patch.setStyleSheet("font-size:14px;font-weight:600;color:#888;")

        # 备份
        if s["has_backup"]:
            self.dash_backup.setText("有备份")
            self.dash_backup.setStyleSheet("font-size:14px;font-weight:600;color:#4ade80;")
        else:
            self.dash_backup.setText("无备份")
            self.dash_backup.setStyleSheet("font-size:14px;font-weight:600;color:#888;")

        # 预设
        preset = self.combo.currentData() or "未选择"
        self.dash_preset.setText(preset)
        self.dash_preset.setStyleSheet("font-size:14px;font-weight:600;color:#a5b4fc;")

        # API 格式
        fmt = self.combo_format.currentData() or "anthropic"
        self.dash_format.setText("Anthropic" if fmt == "anthropic" else "OpenAI")
        self.dash_format.setStyleSheet("font-size:14px;font-weight:600;color:#a5b4fc;")

        # URL
        url = self.input_url.text().strip()
        self.dash_url.setText(url[:50] + "..." if len(url) > 50 else (url or "未设置"))
        self.dash_url.setStyleSheet("font-size:14px;font-weight:600;color:#a5b4fc;font-family:Consolas,monospace;")
        self.dash_url.setWordWrap(True)

    # ── 控制台 ────────────────────────────────────────────────────────

    def _build_control(self):
        root = QVBoxLayout(self.page_control)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(18)

        # ── 开关卡片 ──
        card1 = HeaderCardWidget(self)
        card1.setTitle("API 切换")
        row = QHBoxLayout()
        row.setContentsMargins(16, 10, 16, 10)

        col = QVBoxLayout()
        self.lbl_status = StrongBodyLabel("MiniMax 原版 API")
        self.lbl_status.setStyleSheet("color:#888;")
        col.addWidget(self.lbl_status)
        hint = CaptionLabel("关闭 = 原版  |  开启 = 自定义")
        hint.setStyleSheet("color:#555;")
        col.addWidget(hint)
        row.addLayout(col, 1)

        self.switch_btn = SwitchButton()
        self.switch_btn.checkedChanged.connect(self._on_switch)
        row.addWidget(self.switch_btn)
        card1.viewLayout.addLayout(row)
        root.addWidget(card1)

        # ── 配置卡片（网格） ──
        card2 = HeaderCardWidget(self)
        card2.setTitle("API 配置")
        g = QGridLayout()
        g.setContentsMargins(16, 10, 16, 14)
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(12)

        L = 0  # 行号

        # 预设
        g.addWidget(self._label("预设"), L, 0)
        self.combo = ComboBox()
        self.combo.setMinimumHeight(38)
        for name in API_PRESETS:
            self.combo.addItem(name, userData=name)
        self.combo.currentIndexChanged.connect(self._on_preset)
        g.addWidget(self.combo, L, 1, 1, 3)
        L += 1

        # URL
        g.addWidget(self._label("URL"), L, 0)
        self.input_url = LineEdit()
        self.input_url.setMinimumHeight(38)
        self.input_url.setPlaceholderText("https://api.deepseek.com/v1")
        g.addWidget(self.input_url, L, 1, 1, 3)
        L += 1

        # Key
        g.addWidget(self._label("Key"), L, 0)
        self.input_key = LineEdit()
        self.input_key.setMinimumHeight(38)
        self.input_key.setPlaceholderText("sk-...")
        self.input_key.setEchoMode(QLineEdit.EchoMode.Password)
        g.addWidget(self.input_key, L, 1, 1, 2)

        self.btn_eye = ToolButton(FIF.VIEW)
        self.btn_eye.setFixedSize(38, 38)
        self.btn_eye.clicked.connect(self._toggle_vis)
        g.addWidget(self.btn_eye, L, 3)
        L += 1

        # API 格式
        g.addWidget(self._label("格式"), L, 0)
        self.combo_format = ComboBox()
        self.combo_format.setMinimumHeight(38)
        self.combo_format.addItem("Anthropic (/messages)", userData="anthropic")
        self.combo_format.addItem("OpenAI (/chat/completions)", userData="openai")
        g.addWidget(self.combo_format, L, 1, 1, 3)

        # 列比例：标签固定，输入拉伸
        g.setColumnMinimumWidth(0, 36)
        g.setColumnStretch(1, 1)
        g.setColumnStretch(2, 0)
        g.setColumnStretch(3, 0)

        card2.viewLayout.addLayout(g)
        root.addWidget(card2)

        # ── 设置卡片 ──
        card3 = HeaderCardWidget(self)
        card3.setTitle("设置")
        srow = QHBoxLayout()
        srow.setContentsMargins(16, 10, 16, 10)

        slabel = QVBoxLayout()
        self.lbl_tray = StrongBodyLabel("关闭时最小化到托盘")
        self.lbl_tray.setStyleSheet("color:#ccc;")
        slabel.addWidget(self.lbl_tray)
        sdesc = CaptionLabel("关闭窗口后程序继续运行，可通过托盘图标操作")
        sdesc.setStyleSheet("color:#555;")
        slabel.addWidget(sdesc)
        srow.addLayout(slabel, 1)

        self.switch_tray = SwitchButton()
        self.switch_tray.checkedChanged.connect(self._on_tray_setting)
        srow.addWidget(self.switch_tray)
        card3.viewLayout.addLayout(srow)
        root.addWidget(card3)

        # ── 按钮 ──
        brow = QHBoxLayout()
        brow.setSpacing(10)

        self.btn_apply = PrimaryPushButton("应用补丁")
        self.btn_apply.setFixedHeight(36)
        self.btn_apply.clicked.connect(self._apply)
        brow.addWidget(self.btn_apply)

        self.btn_restore = PushButton("恢复原始")
        self.btn_restore.setFixedHeight(36)
        self.btn_restore.clicked.connect(self._restore)
        brow.addWidget(self.btn_restore)

        root.addLayout(brow)

        # ── 底部提示 ──
        tip = CaptionLabel("使用前请关闭 MiniMax Code  |  软件更新后需重新打补丁")
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip.setStyleSheet("color:#555;")
        root.addWidget(tip)

    # ── 日志页 ────────────────────────────────────────────────────────

    def _build_log(self):
        root = QVBoxLayout(self.page_log)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(18)

        # ── 日期选择 + 操作按钮 ──
        top = QHBoxLayout()
        top.setSpacing(10)

        self.combo_date = ComboBox()
        self.combo_date.setMinimumHeight(34)
        self.combo_date.currentIndexChanged.connect(self._on_date_changed)
        top.addWidget(self.combo_date, 1)

        btn_open_log = TransparentPushButton("打开日志目录")
        btn_open_log.setMinimumHeight(34)
        btn_open_log.setIcon(FIF.FOLDER)
        btn_open_log.clicked.connect(log_manager.open_log_folder)
        top.addWidget(btn_open_log)

        btn_open_arc = TransparentPushButton("打开归档目录")
        btn_open_arc.setMinimumHeight(34)
        btn_open_arc.setIcon(FIF.FOLDER)
        btn_open_arc.clicked.connect(log_manager.open_archive_folder)
        top.addWidget(btn_open_arc)

        root.addLayout(top)

        # ── 日志内容 ──
        card = HeaderCardWidget(self)
        card.setTitle("日志内容")
        self.log_text = PlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "QPlainTextEdit{background:#111;color:#aaa;border:1px solid #222;"
            "border-radius:6px;font-family:Consolas,monospace;font-size:12px;padding:8px;}"
        )
        card.viewLayout.addWidget(self.log_text)
        root.addWidget(card, 1)

        # ── 配置备份 ──
        bk_card = HeaderCardWidget(self)
        bk_card.setTitle("配置备份")
        bk_grid = QGridLayout()
        bk_grid.setContentsMargins(16, 10, 16, 10)
        bk_grid.setHorizontalSpacing(10)
        bk_grid.setVerticalSpacing(8)

        self.combo_backup = ComboBox()
        self.combo_backup.setMinimumHeight(34)
        bk_grid.addWidget(self.combo_backup, 0, 0)

        btn_restore_bk = PushButton("还原选中备份")
        btn_restore_bk.setMinimumHeight(34)
        btn_restore_bk.clicked.connect(self._restore_config_backup)
        bk_grid.addWidget(btn_restore_bk, 0, 1)

        btn_open_bk = TransparentPushButton("打开备份目录")
        btn_open_bk.setMinimumHeight(34)
        btn_open_bk.setIcon(FIF.FOLDER)
        btn_open_bk.clicked.connect(config_backup.open_backup_folder)
        bk_grid.addWidget(btn_open_bk, 0, 2)

        bk_grid.setColumnStretch(0, 1)
        bk_card.viewLayout.addLayout(bk_grid)
        root.addWidget(bk_card)

        # ── 归档列表 ──
        arc_card = HeaderCardWidget(self)
        arc_card.setTitle("日志归档 (.7z)")
        self.lbl_archives = CaptionLabel("无")
        self.lbl_archives.setWordWrap(True)
        self.lbl_archives.setStyleSheet("color:#666;font-size:12px;")
        arc_card.viewLayout.addWidget(self.lbl_archives)
        root.addWidget(arc_card)

    # ── 帮助页 ────────────────────────────────────────────────────────

    def _build_help(self):
        root = QVBoxLayout(self.page_help)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        root.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("""
            QWidget { background:#1e1e1e; }
            HeaderCardWidget { background:#252525; border:1px solid #333; border-radius:8px; }
            HeaderCardWidget QLabel { color:#aaa; }
        """)
        scroll.setWidget(container)
        cl = QVBoxLayout(container)
        cl.setContentsMargins(24, 16, 24, 16)
        cl.setSpacing(10)

        # ── 简介 ──
        intro_card = HeaderCardWidget(self)
        intro_card.setTitle("简介")
        intro_inner = QVBoxLayout()
        intro_inner.setSpacing(8)

        lines = [
            ("功能", "将 MiniMax Code 内置 API 替换为任意外部 API"),
            ("支持", "DeepSeek / Mimo / OpenAI / SiliconFlow / Groq 等"),
            ("原理", "修改 daemon.js 中的预设地址和 npm 包引用"),
            ("安全", "自动备份原始文件，一键还原，不留痕迹"),
        ]
        for label, desc in lines:
            row = QHBoxLayout()
            tag = CaptionLabel(label)
            tag.setFixedWidth(40)
            tag.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tag.setStyleSheet("color:#60a5fa;font-weight:600;")
            row.addWidget(tag)
            txt = BodyLabel(desc)
            txt.setStyleSheet("color:#aaa;")
            txt.setWordWrap(True)
            row.addWidget(txt, 1)
            intro_inner.addLayout(row)

        intro_card.viewLayout.addLayout(intro_inner)
        cl.addWidget(intro_card)

        # ── 使用步骤 ──
        steps_card = HeaderCardWidget(self)
        steps_card.setTitle("使用步骤")
        steps_inner = QVBoxLayout()
        steps_inner.setSpacing(6)

        steps = [
            "关闭 MiniMax Code",
            "打开本工具，进入「控制台」",
            "选择预设（Mimo / DeepSeek / OpenAI...）",
            "填入 API Key（Mimo 预设已自动填入）",
            "确认 API 格式（预设会自动匹配）",
            "点击「应用补丁」或拨开开关",
            "重新打开 MiniMax Code，即可使用新 API",
        ]
        for i, step in enumerate(steps, 1):
            row = QHBoxLayout()
            num = CaptionLabel(str(i))
            num.setFixedSize(22, 22)
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num.setStyleSheet("background:#2563eb;color:white;border-radius:11px;font-weight:600;font-size:11px;")
            row.addWidget(num)
            txt = BodyLabel(step)
            txt.setStyleSheet("color:#aaa;")
            txt.setWordWrap(True)
            row.addWidget(txt, 1)
            steps_inner.addLayout(row)

        steps_card.viewLayout.addLayout(steps_inner)
        cl.addWidget(steps_card)

        # ── API 格式说明 ──
        fmt_card = HeaderCardWidget(self)
        fmt_card.setTitle("API 格式说明")
        fmt_inner = QVBoxLayout()
        fmt_inner.setSpacing(8)

        fmts = [
            ("Anthropic", "/messages", "Mimo、Claude 等", "@ai-sdk/anthropic"),
            ("OpenAI", "/chat/completions", "DeepSeek、OpenAI、SiliconFlow 等", "@ai-sdk/openai"),
        ]
        for name, endpoint, providers, pkg in fmts:
            row = QHBoxLayout()
            tag = CaptionLabel(name)
            tag.setFixedWidth(70)
            tag.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tag.setStyleSheet("color:#60a5fa;font-weight:600;")
            row.addWidget(tag)
            desc = BodyLabel(f"{endpoint}  ·  {providers}")
            desc.setStyleSheet("color:#aaa;")
            desc.setWordWrap(True)
            row.addWidget(desc, 1)
            fmt_inner.addLayout(row)

        fmt_card.viewLayout.addLayout(fmt_inner)
        cl.addWidget(fmt_card)

        # ── 常见问题 ──
        faq_card = HeaderCardWidget(self)
        faq_card.setTitle("常见问题")
        faq_inner = QVBoxLayout()
        faq_inner.setSpacing(10)

        faqs = [
            ("打补丁后 MiniMax Code 报错？", "确认 URL 和 Key 正确，且 API 支持对应格式"),
            ("MiniMax Code 更新后补丁失效？", "更新会覆盖 daemon.js，重新打一次补丁即可"),
            ("怎么完全恢复？", "拨回 OFF 或点「恢复原始」，自动还原 daemon.js"),
            ("配置文件搞乱了？", "日志页 → 配置备份 → 选择之前的备份 → 还原"),
        ]
        for q, a in faqs:
            q_lbl = BodyLabel(f"Q: {q}")
            q_lbl.setStyleSheet("color:#60a5fa;font-weight:600;")
            q_lbl.setWordWrap(True)
            faq_inner.addWidget(q_lbl)
            a_lbl = BodyLabel(f"A: {a}")
            a_lbl.setStyleSheet("color:#999;")
            a_lbl.setWordWrap(True)
            faq_inner.addWidget(a_lbl)

        faq_card.viewLayout.addLayout(faq_inner)
        cl.addWidget(faq_card)

        # ── 项目信息 ──
        info_card = HeaderCardWidget(self)
        info_card.setTitle("项目信息")
        info_lbl = BodyLabel(
            "GitHub  TomLiu-QianYuan/minimax-code-api-proxy\n"
            "版本    v1.2.0\n"
            "协议    MIT\n"
            "作者    Made with Claude · Anthropic AI Assistant"
        )
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("color:#888;font-family:Consolas,monospace;line-height:1.6;")
        info_card.viewLayout.addWidget(info_lbl)
        cl.addWidget(info_card)

        cl.addStretch()

    # ── 系统托盘 ──────────────────────────────────────────────────────

    def _setup_tray(self):
        """初始化系统托盘图标和菜单"""
        self.tray = QSystemTrayIcon(self)
        # 使用标准图标（齿轮/设置图标）
        from PyQt6.QtWidgets import QStyle
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.setWindowIcon(icon)
        self.tray.setToolTip("MiniMax Code API 代理")

        menu = QMenu()

        # 快速切换预设子菜单
        switch_menu = menu.addMenu("快速切换")
        for name in API_PRESETS:
            if name == "自定义":
                continue
            action = QAction(name, self)
            action.triggered.connect(lambda checked, n=name: self._tray_switch(n))
            switch_menu.addAction(action)

        menu.addSeparator()

        # 恢复原始
        act_restore = QAction("恢复原始 API", self)
        act_restore.triggered.connect(self._tray_restore)
        menu.addAction(act_restore)

        menu.addSeparator()

        # 打开主窗口
        act_show = QAction("打开主窗口", self)
        act_show.triggered.connect(self._tray_show)
        menu.addAction(act_show)

        menu.addSeparator()

        # 退出
        act_quit = QAction("退出", self)
        act_quit.triggered.connect(QApplication.quit)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._tray_show()

    def _tray_show(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _tray_switch(self, preset_name):
        """从托盘快速切换到指定预设"""
        if preset_name not in API_PRESETS:
            return
        p = API_PRESETS[preset_name]
        url = p.get("url", "")
        key = p.get("key", "")
        api_type = p.get("type", "openai")
        if not url:
            return

        self.config["target"] = {
            "base_url": url,
            "api_key": key,
            "name": preset_name,
            "api_type": api_type,
            "enabled": True,
        }
        save_config(self.config)
        config_backup.backup()

        self._log(f"[托盘] 切换到 {preset_name}")
        self._pw = PatchWorker(self.patcher, url, key, api_type)
        self._pw.finished.connect(lambda ok, msg, ch: self._on_tray_patched(ok, msg, ch, preset_name))
        self._pw.start()

    def _on_tray_patched(self, ok, msg, changes, preset_name):
        if ok:
            self._log(f"[托盘] 切换成功: {preset_name}")
            for c in changes:
                self._log(f"  · {c}")
            self.tray.showMessage("切换成功", f"已切换到 {preset_name}", QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            self._log(f"[托盘] 切换失败: {msg}")
            self.tray.showMessage("切换失败", msg, QSystemTrayIcon.MessageIcon.Warning, 3000)
        self._refresh()
        self._load_config()

    def _tray_restore(self):
        """从托盘恢复原始 API"""
        self._log("[托盘] 恢复原始 API...")
        self._rw = RestoreWorker(self.patcher)
        self._rw.finished.connect(self._on_tray_restored)
        self._rw.start()

    def _on_tray_restored(self, ok, msg):
        if ok:
            self.config.setdefault("target", {})["enabled"] = False
            save_config(self.config)
            self._log("[托盘] 已恢复原始 API")
            self.tray.showMessage("已恢复", "已恢复原始 API", QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            self._log(f"[托盘] 恢复失败: {msg}")
            self.tray.showMessage("恢复失败", msg, QSystemTrayIcon.MessageIcon.Warning, 3000)
        self._refresh()
        self._load_config()

    def closeEvent(self, event):
        """关闭窗口时根据设置决定最小化到托盘或直接退出"""
        if self.config.get("minimize_to_tray", False):
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "MiniMax Code API 代理",
                "已最小化到系统托盘，右键图标可切换 API 或退出",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        else:
            # 直接退出
            self.tray.hide()
            event.accept()

    def _refresh_log_list(self):
        """刷新日期下拉列表"""
        self.combo_date.blockSignals(True)
        self.combo_date.clear()
        dates = log_manager.list_log_dates()
        if not dates:
            self.combo_date.addItem("（无日志）", userData=None)
        else:
            for d in dates:
                self.combo_date.addItem(d, userData=d)
        self.combo_date.blockSignals(False)
        if dates:
            self._load_log_content(dates[0])

        # 归档列表
        arcs = log_manager.list_archives()
        self.lbl_archives.setText("  ".join(arcs) if arcs else "无归档文件")

        # 配置备份列表
        self._refresh_backup_list()

    def _refresh_backup_list(self):
        """刷新配置备份下拉列表"""
        self.combo_backup.blockSignals(True)
        self.combo_backup.clear()
        backups = config_backup.list_backups()
        if not backups:
            self.combo_backup.addItem("（无备份）", userData=None)
        else:
            for b in backups:
                self.combo_backup.addItem(b, userData=b)
        self.combo_backup.blockSignals(False)

    def _restore_config_backup(self):
        """还原选中的配置备份"""
        name = self.combo_backup.currentData()
        if not name:
            InfoBar.warning("提示", "没有可还原的备份", parent=self, position=InfoBarPosition.TOP)
            return
        ok = config_backup.restore(name)
        if ok:
            self._log(f"[还原] config ← {name}")
            InfoBar.success("成功", f"已还原: {name}", parent=self, position=InfoBarPosition.TOP)
            # 重新加载配置
            self.config = load_config()
            self._load_config()
        else:
            InfoBar.error("失败", "还原失败", parent=self, position=InfoBarPosition.TOP)

        # 归档列表
        arcs = log_manager.list_archives()
        self.lbl_archives.setText("  ".join(arcs) if arcs else "无归档文件")

    def _on_date_changed(self, idx):
        date = self.combo_date.currentData()
        if date:
            self._load_log_content(date)

    def _load_log_content(self, date_str):
        content = log_manager.read_log(date_str)
        self.log_text.setPlainText(content if content else "（该日期无日志）")

    # ── 工具方法 ──────────────────────────────────────────────────────

    def _label(self, text):
        lbl = BodyLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setStyleSheet("color:#999;")
        return lbl

    def _log(self, msg):
        log_manager.write_log(msg)
        # 如果当前查看的是今天的日志，实时更新显示
        current_date = self.combo_date.currentData()
        if current_date == log_manager._today_str():
            self.log_text.appendPlainText(msg)

    # ── 数据加载 ──────────────────────────────────────────────────────

    def _load_config(self):
        t = self.config.get("target", {})
        url = t.get("base_url", "")
        key = t.get("api_key", "")
        api_type = t.get("api_type", "")
        enabled = t.get("enabled", False)

        if url:
            self.input_url.setText(url)
            for i, (name, info) in enumerate(API_PRESETS.items()):
                if info["url"] == url:
                    self.combo.setCurrentIndex(i)
                    break
            else:
                self.combo.setCurrentIndex(len(API_PRESETS) - 1)

        if key:
            self.input_key.setText(key)

        # 恢复 API 格式
        if api_type:
            fmt_idx = 0 if api_type == "anthropic" else 1
            self.combo_format.setCurrentIndex(fmt_idx)

        self.switch_btn.blockSignals(True)
        self.switch_btn.setChecked(enabled)
        self.switch_btn.blockSignals(False)
        self._update_label(enabled)

        # 恢复托盘设置
        minimize_to_tray = self.config.get("minimize_to_tray", False)
        self.switch_tray.blockSignals(True)
        self.switch_tray.setChecked(minimize_to_tray)
        self.switch_tray.blockSignals(False)

    def _on_preset(self, idx):
        name = self.combo.currentData()
        if name in API_PRESETS:
            p = API_PRESETS[name]
            if p.get("url"):
                self.input_url.setText(p["url"])
            if p.get("key"):
                self.input_key.setText(p["key"])
            self.input_url.setReadOnly(name != "自定义")
            # 设置 API 格式
            api_type = p.get("type", "openai")
            fmt_idx = 0 if api_type == "anthropic" else 1
            self.combo_format.setCurrentIndex(fmt_idx)
            # 自定义允许切换格式，预设锁定
            self.combo_format.setEnabled(name == "自定义")

    def _update_label(self, on):
        if on:
            n = self.combo.currentData() or "自定义"
            self.lbl_status.setText(f"{n} API")
            self.lbl_status.setStyleSheet("color:#4ade80;font-weight:600;")
        else:
            self.lbl_status.setText("MiniMax 原版 API")
            self.lbl_status.setStyleSheet("color:#888;")

    def _on_switch(self, on):
        if on:
            self._apply()
        else:
            self._restore()
        self._update_label(on)
        self.config.setdefault("target", {})["enabled"] = on
        save_config(self.config)

    def _on_tray_setting(self, on):
        self.config["minimize_to_tray"] = on
        save_config(self.config)
        self._log(f"[设置] 关闭时最小化到托盘 = {'开' if on else '关'}")

    def _toggle_vis(self):
        if self.input_key.echoMode() == QLineEdit.EchoMode.Password:
            self.input_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_eye.setIcon(FIF.HIDE)
        else:
            self.input_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_eye.setIcon(FIF.VIEW)

    def _refresh(self):
        s = self.patcher.status()
        self._log(f"[状态] 补丁={'是' if s['is_patched'] else '否'}  备份={'是' if s['has_backup'] else '否'}")
        self._refresh_dash()

    def _apply(self):
        url = self.input_url.text().strip()
        key = self.input_key.text().strip()
        if not url:
            InfoBar.warning("提示", "请填写 URL", parent=self, position=InfoBarPosition.TOP)
            return

        # 应用前先保存当前配置并备份
        self.config["target"] = {
            "base_url": url,
            "api_key": key,
            "name": self.combo.currentData() or "custom",
            "api_type": self.combo_format.currentData() or "anthropic",
            "enabled": True,
        }
        save_config(self.config)
        bk = config_backup.backup()
        if bk:
            self._log(f"[备份] config → {bk}")
            self._refresh_backup_list()

        self.btn_apply.setEnabled(False)
        self.btn_apply.setText("应用中...")
        api_type = self.combo_format.currentData() or "anthropic"
        self._log(f"[补丁] {url}  格式={api_type}")
        self._pw = PatchWorker(self.patcher, url, key, api_type)
        self._pw.finished.connect(self._on_applied)
        self._pw.start()

    def _on_applied(self, ok, msg, changes):
        self.btn_apply.setEnabled(True)
        self.btn_apply.setText("应用补丁")
        if ok:
            self.config["target"] = {
                "base_url": self.input_url.text().strip(),
                "api_key": self.input_key.text().strip(),
                "name": self.combo.currentData() or "custom",
                "api_type": self.combo_format.currentData() or "anthropic",
                "enabled": True,
            }
            save_config(self.config)
            self._log(f"[成功] {msg}")
            for c in changes:
                self._log(f"  · {c}")
            InfoBar.success("成功", msg, parent=self, position=InfoBarPosition.TOP)
            self._update_label(True)
        else:
            self.switch_btn.blockSignals(True)
            self.switch_btn.setChecked(False)
            self.switch_btn.blockSignals(False)
            self._update_label(False)
            self.config.setdefault("target", {})["enabled"] = False
            save_config(self.config)
            self._log(f"[失败] {msg}")
            InfoBar.error("失败", msg, parent=self, position=InfoBarPosition.TOP)
        self._refresh()

    def _restore(self):
        self.btn_restore.setEnabled(False)
        self.btn_restore.setText("恢复中...")
        self._log("[恢复] 还原原始文件...")
        self._rw = RestoreWorker(self.patcher)
        self._rw.finished.connect(self._on_restored)
        self._rw.start()

    def _on_restored(self, ok, msg):
        self.btn_restore.setEnabled(True)
        self.btn_restore.setText("恢复原始")
        if ok:
            self.config.setdefault("target", {})["enabled"] = False
            save_config(self.config)
            self._update_label(False)
            self._log(f"[成功] {msg}")
            InfoBar.success("成功", msg, parent=self, position=InfoBarPosition.TOP)
        else:
            self.switch_btn.blockSignals(True)
            self.switch_btn.setChecked(True)
            self.switch_btn.blockSignals(False)
            self._update_label(True)
            self._log(f"[失败] {msg}")
            InfoBar.error("失败", msg, parent=self, position=InfoBarPosition.TOP)
        self._refresh()


# ── 启动 ──────────────────────────────────────────────────────────────

def main():
    setTheme(Theme.DARK)
    setThemeColor("#2563eb")

    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 9))

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
