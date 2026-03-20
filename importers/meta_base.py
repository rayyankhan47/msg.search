"""Shared parsing logic for Meta message exports."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from zipfile import ZipFile


class MetaZipImporterBase:
    """Base parser for Meta ZIP exports with message_*.json files."""

    platform = "meta"
    inbox_prefixes = ("messages/inbox/",)

    @staticmethod
    def _decode_meta_text(value: str) -> str:
        try:
            return value.encode("latin1").decode("utf-8")
        except UnicodeError:
            return value

    def parse(self, filepath: str) -> list[dict]:
        path = Path(filepath)
        messages: list[dict] = []
        seen_ids: set[str] = set()

        with ZipFile(path, "r") as archive:
            members = sorted(
                [
                    name
                    for name in archive.namelist()
                    if any(name.startswith(prefix) for prefix in self.inbox_prefixes)
                    and name.endswith(".json")
                    and "/message_" in name
                ]
            )

            for member in members:
                try:
                    payload = json.loads(archive.read(member).decode("utf-8", errors="replace"))
                except json.JSONDecodeError:
                    # Skip malformed files and continue parsing other conversations.
                    continue
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
                    message_id = (
                        f"{self.platform}:{conversation_key}:{timestamp_ms}:{sender_key}:{content_hash}"
                    )
                    if message_id in seen_ids:
                        continue
                    seen_ids.add(message_id)

                    messages.append(
                        {
                            "id": message_id,
                            "content": content,
                            "sender": sender,
                            "timestamp": timestamp_iso,
                            "platform": self.platform,
                            "conversation": conversation,
                        }
                    )
        return messages
