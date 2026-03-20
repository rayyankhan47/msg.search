"""Data directory creation and path helpers."""

from pathlib import Path


DATA_DIR = Path.home() / ".msgsearch"
RAW_DIR = DATA_DIR / "raw"
DB_DIR = DATA_DIR / "db"
LOGS_DIR = DATA_DIR / "logs"
PLATFORMS = ("telegram", "whatsapp", "imessage", "instagram", "messenger", "discord")


def init_data_dir() -> Path:
    """Create ~/.msgsearch and required subdirectories if missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    for platform in PLATFORMS:
        (RAW_DIR / platform).mkdir(parents=True, exist_ok=True)

    return DATA_DIR
