"""Instagram export importer."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile


class InstagramImporter:
    """Parse Instagram message exports from a ZIP file."""

    def parse(self, filepath: str) -> list[dict]:
        path = Path(filepath)
        messages: list[dict] = []
        with ZipFile(path, "r") as archive:
            for member in archive.namelist():
                if not member.startswith("messages/inbox/"):
                    continue
                if not member.endswith(".json"):
                    continue
                if "/message_" not in member:
                    continue

                payload = json.loads(archive.read(member).decode("utf-8", errors="replace"))
                conversation = payload.get("title") or Path(member).parts[-2]
                for item in payload.get("messages", []):
                    messages.append(
                        {
                            "conversation": conversation,
                            "sender_name": item.get("sender_name", "Unknown"),
                            "timestamp_ms": item.get("timestamp_ms"),
                            "content": item.get("content"),
                        }
                    )
        return messages
