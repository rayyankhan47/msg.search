"""Integration tests for indexing + search query flow."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core import database
from core.database import insert_messages
from importers.discord import DiscordImporter
from importers.telegram import TelegramImporter
from importers.whatsapp import WhatsAppImporter
from search import query as search_query


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class DummyEmbedder:
    """Deterministic tiny embedder for fast, offline tests."""

    KEYWORDS = ("pasta", "offer", "address", "link")

    def embed(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            lowered = text.lower()
            vec = [1.0 if keyword in lowered else 0.0 for keyword in self.KEYWORDS]
            if not any(vec):
                vec = [0.1, 0.1, 0.1, 0.1]
            vectors.append(vec)
        return vectors


class SearchIntegrationTests(unittest.TestCase):
    def test_search_by_content_sender_date_and_platform(self) -> None:
        telegram = TelegramImporter().parse(str(FIXTURES / "telegram_export.json"))
        whatsapp = WhatsAppImporter().parse(str(FIXTURES / "whatsapp_export.zip"))
        discord = DiscordImporter().parse(str(FIXTURES / "discord_export.json"))
        all_messages = telegram + whatsapp + discord

        with tempfile.TemporaryDirectory() as tmpdir:
            test_db = Path(tmpdir) / "db"
            test_db.mkdir(parents=True, exist_ok=True)

            with patch.object(database, "DB_DIR", test_db), patch.object(
                database, "init_data_dir", lambda: None
            ), patch.object(search_query, "Embedder", DummyEmbedder):
                # Recreate clean collection in temporary DB.
                client = database.get_client()
                try:
                    client.delete_collection(database.COLLECTION_NAME)
                except Exception:
                    pass
                database.get_collection()

                insert_messages(all_messages, embedder=DummyEmbedder(), platform_label="test")

                by_content = search_query.search_messages("pasta place", limit=5)
                self.assertTrue(any("pasta" in row["content"].lower() for row in by_content))

                by_sender = search_query.search_messages("new year", sender="Sarah", limit=5)
                self.assertTrue(all(row["sender"] == "Sarah" for row in by_sender))

                by_platform = search_query.search_messages(
                    "meeting link", platform="discord", limit=5
                )
                self.assertTrue(all(row["platform"] == "discord" for row in by_platform))

                by_date = search_query.search_messages(
                    "charger",
                    after="2023-12-31T21:00:00",
                    before="2023-12-31T22:00:00",
                    limit=5,
                )
                self.assertTrue(all("2023-12-31" in row["timestamp"] for row in by_date))


if __name__ == "__main__":
    unittest.main()
