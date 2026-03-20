"""Telegram export importer."""

from __future__ import annotations

import json
from pathlib import Path


class TelegramImporter:
    """Parse Telegram export JSON files."""

    def parse(self, filepath: str) -> list[dict]:
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        messages: list[dict] = []
        chats = payload.get("chats", {}).get("list", [])
        for chat in chats:
            conversation = chat.get("name", "Unknown chat")
            chat_id = str(chat.get("id", conversation))
            for message in chat.get("messages", []):
                messages.append(
                    {
                        "chat_id": chat_id,
                        "conversation": conversation,
                        "id": message.get("id"),
                        "text": message.get("text"),
                        "sender": message.get("from", "Unknown"),
                        "timestamp": message.get("date"),
                    }
                )

        return messages
