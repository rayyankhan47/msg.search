"""Telegram auto-connect client for message sync."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from utils.storage import DATA_DIR


class TelegramAuthError(RuntimeError):
    """Raised when Telegram auth/session cannot be established."""


class TelegramClientManager:
    """Manage local Telegram auth and history fetching."""

    def __init__(self) -> None:
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        session_dir = DATA_DIR / "telegram_session"
        session_dir.mkdir(parents=True, exist_ok=True)
        self.session_path = str(session_dir / "msgsearch")

    def _validate_credentials(self) -> tuple[int, str]:
        if not self.api_id or not self.api_hash:
            raise TelegramAuthError(
                "Missing Telegram credentials. Set TELEGRAM_API_ID and "
                "TELEGRAM_API_HASH environment variables."
            )
        try:
            api_id = int(self.api_id)
        except ValueError as exc:
            raise TelegramAuthError("TELEGRAM_API_ID must be an integer.") from exc
        return api_id, self.api_hash

    async def _fetch_messages_async(
        self, limit_per_chat: int = 2000, max_dialogs: int | None = None
    ) -> list[dict[str, Any]]:
        api_id, api_hash = self._validate_credentials()

        try:
            from telethon import TelegramClient
            from telethon.errors import SessionPasswordNeededError
        except ImportError as exc:  # pragma: no cover
            raise TelegramAuthError(
                "Telethon is not installed. Install dependencies to enable Telegram auto-connect."
            ) from exc

        client = TelegramClient(self.session_path, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            phone = input("Telegram phone number (international format): ").strip()
            if not phone:
                await client.disconnect()
                raise TelegramAuthError("Telegram login cancelled.")

            sent = await client.send_code_request(phone)
            code = input("Telegram OTP code: ").strip()
            try:
                await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
            except SessionPasswordNeededError:
                password = input("Telegram 2FA password: ").strip()
                await client.sign_in(password=password)

        output: list[dict[str, Any]] = []
        dialog_count = 0
        async for dialog in client.iter_dialogs():
            if max_dialogs is not None and dialog_count >= max_dialogs:
                break
            dialog_count += 1
            chat_id = str(getattr(dialog.entity, "id", dialog.name))
            conversation = dialog.name or "Telegram chat"
            async for message in client.iter_messages(dialog.entity, limit=limit_per_chat):
                text = (message.message or "").strip()
                if not text:
                    continue
                if message.id is None:
                    continue
                sender = "Unknown"
                if message.sender:
                    sender = (
                        getattr(message.sender, "username", None)
                        or getattr(message.sender, "first_name", None)
                        or getattr(message.sender, "title", None)
                        or "Unknown"
                    )
                output.append(
                    {
                        "id": f"telegram:{chat_id}:{message.id}",
                        "content": text,
                        "sender": sender,
                        "timestamp": message.date.isoformat() if message.date else "",
                        "platform": "telegram",
                        "conversation": conversation,
                    }
                )

        output.sort(key=lambda m: (m.get("timestamp", ""), m.get("id", "")))
        await client.disconnect()
        return output

    def fetch_messages(
        self, limit_per_chat: int = 2000, max_dialogs: int | None = None
    ) -> list[dict[str, Any]]:
        """Authenticate if needed and fetch Telegram history."""
        return asyncio.run(
            self._fetch_messages_async(limit_per_chat=limit_per_chat, max_dialogs=max_dialogs)
        )
