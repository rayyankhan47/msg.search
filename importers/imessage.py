"""iMessage local database importer."""

from __future__ import annotations

import platform
import sqlite3
from pathlib import Path


class iMessageImporter:
    """Parse messages from the local macOS iMessage database."""

    DB_PATH = Path.home() / "Library" / "Messages" / "chat.db"

    def parse(self, filepath: str | None = None) -> list[dict]:
        if platform.system() != "Darwin":
            raise RuntimeError("iMessage is only available on macOS.")

        db_path = Path(filepath) if filepath else self.DB_PATH
        connection = sqlite3.connect(str(db_path))
        try:
            return self._query_messages(connection)
        finally:
            connection.close()

    def _query_messages(self, connection: sqlite3.Connection) -> list[dict]:
        cursor = connection.cursor()
        cursor.execute("SELECT text FROM message LIMIT 10;")
        rows = cursor.fetchall()
        return [{"content": row[0] or ""} for row in rows]
