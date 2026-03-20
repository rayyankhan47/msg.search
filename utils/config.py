"""Config file manager for ~/.msgsearch/config.json."""

import json
from pathlib import Path
from typing import Any

from utils.storage import DATA_DIR


DEFAULT_CONFIG: dict[str, Any] = {
    "connected_platforms": [],
    "last_sync": {},
    "model_downloaded": False,
}


class Config:
    """Read and write user configuration."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (DATA_DIR / "config.json")
        self.data: dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        """Load config from disk, creating defaults when missing."""
        if not self.path.exists():
            self.save()
            return

        with self.path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)

        self.data = dict(DEFAULT_CONFIG)
        self.data.update(loaded)

    def save(self) -> None:
        """Persist config to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2, sort_keys=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value by key and save."""
        self.data[key] = value
        self.save()
