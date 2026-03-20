"""Unit tests for platform importers."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from importers.discord import DiscordImporter, InvalidFormatError
from importers.imessage import iMessageImporter
from importers.instagram import InstagramImporter
from importers.messenger import MessengerImporter
from importers.telegram import TelegramImporter
from importers.whatsapp import WhatsAppImporter


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ImporterTests(unittest.TestCase):
    def test_telegram_importer(self) -> None:
        data = TelegramImporter().parse(str(FIXTURES / "telegram_export.json"))
        self.assertEqual(len(data), 3)  # 1 empty text message skipped
        self.assertEqual(data[0]["platform"], "telegram")
        self.assertTrue(data[0]["id"].startswith("telegram:"))
        self.assertIn("[Forwarded from Liam]", data[2]["content"])

    def test_whatsapp_importer(self) -> None:
        data = WhatsAppImporter().parse(str(FIXTURES / "whatsapp_export.zip"))
        self.assertEqual(len(data), 2)  # system encrypted line skipped
        self.assertEqual(data[0]["platform"], "whatsapp")
        self.assertTrue(data[0]["id"].startswith("whatsapp:"))
        self.assertIn("T", data[0]["timestamp"])

    def test_instagram_importer(self) -> None:
        data = InstagramImporter().parse(str(FIXTURES / "instagram_export.zip"))
        self.assertEqual(len(data), 3)  # one duplicate across message_1/2 removed
        self.assertEqual(data[0]["platform"], "instagram")
        self.assertTrue(data[0]["id"].startswith("instagram:"))

    def test_messenger_importer(self) -> None:
        data = MessengerImporter().parse(str(FIXTURES / "messenger_export.zip"))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["platform"], "messenger")
        self.assertTrue(data[0]["id"].startswith("messenger:"))

    def test_discord_importer_and_invalid_format(self) -> None:
        data = DiscordImporter().parse(str(FIXTURES / "discord_export.json"))
        self.assertEqual(len(data), 1)  # empty content skipped
        self.assertEqual(data[0]["platform"], "discord")
        self.assertTrue(data[0]["id"].startswith("discord:"))

        with self.assertRaises(InvalidFormatError):
            DiscordImporter().parse(str(FIXTURES / "does_not_exist.json"))

    def test_imessage_importer_with_temp_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "chat.db"
            self._build_imessage_fixture_db(db_path)
            data = iMessageImporter().parse(str(db_path))

        self.assertEqual(len(data), 1)  # null text row skipped
        row = data[0]
        self.assertEqual(row["platform"], "imessage")
        self.assertTrue(row["id"].startswith("imessage:"))
        self.assertIn("T", row["timestamp"])
        self.assertEqual(row["sender"], "bob@example.com")

    @staticmethod
    def _build_imessage_fixture_db(db_path: Path) -> None:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE message (ROWID INTEGER PRIMARY KEY, guid TEXT, text TEXT, "
            "is_from_me INTEGER, handle_id INTEGER, date INTEGER)"
        )
        cur.execute("CREATE TABLE handle (ROWID INTEGER PRIMARY KEY, id TEXT)")
        cur.execute("CREATE TABLE chat (ROWID INTEGER PRIMARY KEY, display_name TEXT)")
        cur.execute("CREATE TABLE chat_message_join (chat_id INTEGER, message_id INTEGER)")

        cur.execute("INSERT INTO handle (ROWID, id) VALUES (1, 'bob@example.com')")
        cur.execute("INSERT INTO chat (ROWID, display_name) VALUES (1, 'iMessage Test')")
        cur.execute(
            "INSERT INTO message (ROWID, guid, text, is_from_me, handle_id, date) "
            "VALUES (1, 'GUID-1', 'Hey there', 0, 1, 1000000000)"
        )
        cur.execute(
            "INSERT INTO message (ROWID, guid, text, is_from_me, handle_id, date) "
            "VALUES (2, 'GUID-2', NULL, 1, 1, 2000000000)"
        )
        cur.execute("INSERT INTO chat_message_join (chat_id, message_id) VALUES (1, 1)")
        cur.execute("INSERT INTO chat_message_join (chat_id, message_id) VALUES (1, 2)")
        conn.commit()
        conn.close()


if __name__ == "__main__":
    unittest.main()
