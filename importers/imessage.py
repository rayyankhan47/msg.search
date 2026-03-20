"""iMessage local database importer."""

from __future__ import annotations

import platform
import sqlite3
from datetime import datetime, timedelta, timezone
from hashlib import sha1
from pathlib import Path


class iMessageImporter:
    """Parse messages from the local macOS iMessage database."""

    DB_PATH = Path.home() / "Library" / "Messages" / "chat.db"

    def parse(self, filepath: str | None = None) -> list[dict]:
        if platform.system() != "Darwin":
            raise RuntimeError("iMessage is only available on macOS.")

        db_path = Path(filepath) if filepath else self.DB_PATH
        try:
            connection = sqlite3.connect(str(db_path))
        except sqlite3.OperationalError as exc:
            if "permission" in str(exc).lower():
                raise RuntimeError(
                    "Permission denied. Go to System Preferences -> Privacy & Security "
                    "-> Full Disk Access and add your terminal."
                ) from exc
            raise
        try:
            return self._query_messages(connection)
        finally:
            connection.close()

    def _query_messages(self, connection: sqlite3.Connection) -> list[dict]:
        query = """
        SELECT
            m.guid,
            m.text,
            m.is_from_me,
            h.id AS handle_id,
            m.date,
            c.display_name
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
        LEFT JOIN chat c ON c.ROWID = cmj.chat_id
        ORDER BY m.date ASC
        """
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        messages: list[dict] = []
        for guid, text, is_from_me, handle_id, raw_date, display_name in rows:
            if not text:
                continue

            timestamp = self._apple_time_to_iso(raw_date)
            sender = "Me" if is_from_me else (handle_id or "Unknown")
            fallback_hash = sha1(f"{sender}|{timestamp}|{text}".encode("utf-8")).hexdigest()[:12]
            message_id = guid or f"imessage:{fallback_hash}"
            messages.append(
                {
                    "id": (
                        f"imessage:{message_id}"
                        if not str(message_id).startswith("imessage:")
                        else str(message_id)
                    ),
                    "content": text,
                    "sender": sender,
                    "timestamp": timestamp,
                    "platform": "imessage",
                    "conversation": display_name or "iMessage",
                }
            )
        return messages

    @staticmethod
    def _apple_time_to_iso(raw_date: int | float | None) -> str:
        if raw_date in (None, 0):
            return ""

        # message.date is often nanoseconds since Apple epoch (2001-01-01 UTC)
        seconds = float(raw_date) / 1_000_000_000
        apple_epoch = datetime(2001, 1, 1, tzinfo=timezone.utc)
        return (apple_epoch + timedelta(seconds=seconds)).isoformat()
