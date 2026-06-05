"""
配置备份管理器
- 每次应用补丁前自动备份 config.yaml
- 备份存储为 backups/YYYY-MM-DD_HHMMSS_config.7z（或 .zip）
- 提供列表和还原功能
"""

import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / "backups"
CONFIG_FILE = Path(__file__).parent / "config.yaml"


def _ensure_dir():
    BACKUP_DIR.mkdir(exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def _compress(src: Path, dst: Path) -> bool:
    """优先 7z，失败则 zip"""
    for cmd in ["7z", "7za", r"C:\Program Files\7-Zip\7z.exe"]:
        try:
            subprocess.run(
                [cmd, "a", "-t7z", str(dst), str(src)],
                capture_output=True, check=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    # fallback zip
    try:
        with zipfile.ZipFile(dst.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(src, src.name)
        return True
    except Exception:
        return False


def _decompress(src: Path, dst_dir: Path) -> bool:
    """解压 7z 或 zip"""
    if src.suffix == ".7z":
        for cmd in ["7z", "7za", r"C:\Program Files\7-Zip\7z.exe"]:
            try:
                subprocess.run(
                    [cmd, "e", "-y", "-o" + str(dst_dir), str(src)],
                    capture_output=True, check=True,
                )
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
    if src.suffix == ".zip":
        try:
            with zipfile.ZipFile(src, "r") as zf:
                zf.extractall(dst_dir)
            return True
        except Exception:
            return False
    return False


def backup() -> str | None:
    """备份当前 config.yaml，返回备份文件名，失败返回 None"""
    _ensure_dir()
    if not CONFIG_FILE.exists():
        return None

    name = f"{_timestamp()}_config"
    # 尝试 7z
    dst7z = BACKUP_DIR / f"{name}.7z"
    if _compress(CONFIG_FILE, dst7z) and dst7z.exists():
        return dst7z.name
    # 尝试 zip
    dstzip = BACKUP_DIR / f"{name}.zip"
    if dstzip.exists():
        return dstzip.name
    return None


def list_backups() -> list[str]:
    """列出所有备份文件，按时间倒序"""
    _ensure_dir()
    files = []
    for f in BACKUP_DIR.iterdir():
        if f.suffix in (".7z", ".zip") and "config" in f.name:
            files.append(f.name)
    return sorted(files, reverse=True)


def restore(filename: str) -> bool:
    """从备份还原 config.yaml"""
    _ensure_dir()
    src = BACKUP_DIR / filename
    if not src.exists():
        return False

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        if not _decompress(src, tmp):
            return False
        # 找到解压出来的 config.yaml
        for f in tmp.rglob("config.yaml"):
            import shutil
            shutil.copy2(f, CONFIG_FILE)
            return True
        # 如果文件名不是 config.yaml，找第一个 yaml 文件
        for f in tmp.rglob("*.yaml"):
            import shutil
            shutil.copy2(f, CONFIG_FILE)
            return True
    return False


def open_backup_folder():
    """打开备份目录"""
    _ensure_dir()
    os.startfile(str(BACKUP_DIR))
