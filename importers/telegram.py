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
        if isinstance(value, list):
            parts: list[str] = []
            for chunk in value:
                if isinstance(chunk, str):
                    parts.append(chunk)
                elif isinstance(chunk, dict):
                    text = chunk.get("text")
                    if isinstance(text, str):
                        parts.append(text)
            return "".join(parts).strip()
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
                if message_id is None:
                    continue
                content = self._extract_text(message.get("text"))
                if not content:
                    continue

                forward_from = message.get("forwarded_from")
                if isinstance(forward_from, str) and forward_from.strip():
                    content = f"[Forwarded from {forward_from}] {content}"

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
