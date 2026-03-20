"""Instagram export importer."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from zipfile import ZipFile


class InstagramImporter:
    """Parse Instagram message exports from a ZIP file."""

    @staticmethod
    def _decode_meta_text(value: str) -> str:
        try:
            return value.encode("latin1").decode("utf-8")
        except UnicodeError:
            return value

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
                conversation_key = re.sub(r"\s+", "_", conversation.lower())
                for item in payload.get("messages", []):
                    content = item.get("content")
                    if not isinstance(content, str):
                        continue
                    content = self._decode_meta_text(content).strip()
                    if not content:
                        continue

                    sender = str(item.get("sender_name", "Unknown"))
                    timestamp_ms = int(item.get("timestamp_ms", 0))
                    timestamp_iso = datetime.fromtimestamp(
                        timestamp_ms / 1000, tz=timezone.utc
                    ).isoformat()
                    sender_key = re.sub(r"\s+", "_", sender.lower())
                    content_hash = sha1(content.encode("utf-8")).hexdigest()[:10]
                    messages.append(
                        {
                            "id": (
                                "instagram:"
                                f"{conversation_key}:{timestamp_ms}:{sender_key}:{content_hash}"
                            ),
                            "content": content,
                            "sender": sender,
                            "timestamp": timestamp_iso,
                            "platform": "instagram",
                            "conversation": conversation,
                        }
                    )
        return messages
