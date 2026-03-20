"""Discord export importer."""

from __future__ import annotations

import json
from pathlib import Path


class InvalidFormatError(Exception):
    """Raised when the provided Discord export file format is invalid."""


class DiscordImporter:
    """Parse DiscordChatExporter JSON files."""

    def parse(self, filepath: str) -> list[dict]:
        payload = self._load_payload(filepath)
        return payload["messages"]

    def _load_payload(self, filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists() or not path.is_file():
            raise InvalidFormatError("File not found or invalid format.")

        try:
            with path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
        except Exception as exc:  # noqa: BLE001
            raise InvalidFormatError("File not found or invalid format.") from exc

        if not isinstance(payload, dict):
            raise InvalidFormatError("File not found or invalid format.")
        if "channel" not in payload or "messages" not in payload:
            raise InvalidFormatError("File not found or invalid format.")
        if not isinstance(payload.get("messages"), list):
            raise InvalidFormatError("File not found or invalid format.")

        return payload
