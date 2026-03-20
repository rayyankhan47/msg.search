"""Telegram export importer."""

from __future__ import annotations

import json
from pathlib import Path


class TelegramImporter:
    """Parse Telegram export JSON files."""

    @staticmethod
    def _extract_text(value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        return ""

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
                message_id = message.get("id")
                content = self._extract_text(message.get("text"))
                messages.append(
                    {
                        "id": f"telegram:{chat_id}:{message_id}",
                        "content": content,
                        "sender": message.get("from", "Unknown"),
                        "timestamp": message.get("date", ""),
                        "platform": "telegram",
                        "conversation": conversation,
                    }
                )

        return messages
