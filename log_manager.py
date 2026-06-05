"""
日志管理器
- 按日期保存日志（logs/YYYY-MM-DD.log）
- 超过 3 天的日志自动压缩为 .7z
- 提供日志列表和打开备份文件夹功能
"""

import os
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path


LOG_DIR = Path(__file__).parent / "logs"
ARCHIVE_DIR = LOG_DIR / "archive"
KEEP_DAYS = 3


def _ensure_dirs():
    LOG_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)


def _today_str():
    return datetime.now().strftime("%Y-%m-%d")


def _log_path(date_str: str) -> Path:
    return LOG_DIR / f"{date_str}.log"


def write_log(msg: str):
    """写入今天的日志"""
    _ensure_dirs()
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(_log_path(_today_str()), "a", encoding="utf-8") as f:
        f.write(line)


def read_log(date_str: str = None) -> str:
    """读取指定日期的日志，默认今天"""
    _ensure_dirs()
    if date_str is None:
        date_str = _today_str()
    p = _log_path(date_str)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def list_log_dates() -> list[str]:
    """列出所有有日志的日期（不含已归档）"""
    _ensure_dates = []
    if LOG_DIR.exists():
        for f in sorted(LOG_DIR.glob("*.log"), reverse=True):
            _ensure_dates.append(f.stem)
    return _ensure_dates


def list_archives() -> list[str]:
    """列出所有 .7z 归档文件"""
    _ensure_dirs()
    return sorted(
        [f.name for f in ARCHIVE_DIR.glob("*.7z")],
        reverse=True,
    )


def archive_old_logs() -> list[str]:
    """将超过 KEEP_DAYS 天的日志压缩为 .7z，返回归档的文件名列表"""
    _ensure_dirs()
    archived = []
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)

    for log_file in sorted(LOG_DIR.glob("*.log")):
        try:
            date = datetime.strptime(log_file.stem, "%Y-%m-%d")
        except ValueError:
            continue
        if date >= cutoff:
            continue

        # 归档
        archive_name = f"{log_file.stem}.7z"
        archive_path = ARCHIVE_DIR / archive_name
        if archive_path.exists():
            log_file.unlink()
            continue

        # 尝试用 7z，失败则用 zip
        if _compress_7z(log_file, archive_path):
            log_file.unlink()
            archived.append(archive_name)
        elif _compress_zip(log_file, ARCHIVE_DIR / f"{log_file.stem}.zip"):
            log_file.unlink()
            archived.append(f"{log_file.stem}.zip")

    return archived


def _compress_7z(src: Path, dst: Path) -> bool:
    """用 7z 压缩"""
    for cmd in ["7z", "7za", r"C:\Program Files\7-Zip\7z.exe"]:
        try:
            subprocess.run(
                [cmd, "a", "-t7z", str(dst), str(src)],
                capture_output=True, check=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return False


def _compress_zip(src: Path, dst: Path) -> bool:
    """备用：用 Python zipfile"""
    import zipfile
    try:
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(src, src.name)
        return True
    except Exception:
        return False


def open_log_folder():
    """用系统文件管理器打开日志文件夹"""
    _ensure_dirs()
    os.startfile(str(LOG_DIR))


def open_archive_folder():
    """用系统文件管理器打开归档文件夹"""
    _ensure_dirs()
    os.startfile(str(ARCHIVE_DIR))
