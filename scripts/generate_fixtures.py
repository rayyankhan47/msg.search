"""Generate synthetic fixture exports for importer tests."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def make_telegram_fixture() -> None:
    payload = {
        "chats": {
            "list": [
                {
                    "id": 1001,
                    "name": "Weekend Plans",
                    "messages": [
                        {
                            "id": 1,
                            "date": "2024-01-10T12:34:00",
                            "from": "Ava",
                            "text": "Try that pasta place downtown.",
                        },
                        {
                            "id": 2,
                            "date": "2024-01-11T09:00:00",
                            "from": "Noah",
                            "text": [{"type": "plain", "text": "Meet "}, "at 7?"],
                        },
                        {
                            "id": 3,
                            "date": "2024-01-11T10:00:00",
                            "from": "Noah",
                            "text": "Forwarded tip",
                            "forwarded_from": "Liam",
                        },
                        {
                            "id": 4,
                            "date": "2024-01-11T10:05:00",
                            "from": "Noah",
                            "text": "",
                        },
                    ],
                }
            ]
        }
    }
    write_json(FIXTURES / "telegram_export.json", payload)


def make_whatsapp_fixture() -> None:
    whatsapp_text = (
        "12/31/23, 9:45 PM - John: Bring the charger please\n"
        "1/1/24, 08:10 - Sarah: Happy new year\n"
        "1/1/24, 08:11 - Messages and calls are end-to-end encrypted.\n"
    )
    zip_path = FIXTURES / "whatsapp_export.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("Family Chat.txt", whatsapp_text)


def _meta_message(sender: str, timestamp_ms: int, content: str) -> dict:
    return {"sender_name": sender, "timestamp_ms": timestamp_ms, "content": content}


def make_instagram_fixture() -> None:
    zip_path = FIXTURES / "instagram_export.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        payload1 = {
            "title": "Road Trip Crew",
            "messages": [
                _meta_message("Mia", 1704067200000, "Book the cabin tonight"),
                _meta_message("Ethan", 1704067300000, "I found one near the lake"),
            ],
        }
        payload2 = {
            "title": "Road Trip Crew",
            "messages": [
                _meta_message("Ethan", 1704067300000, "I found one near the lake"),
                _meta_message("Mia", 1704067400000, "Perfect, send the link"),
            ],
        }
        zf.writestr(
            "messages/inbox/road_trip_crew_123/message_1.json",
            json.dumps(payload1),
        )
        zf.writestr(
            "messages/inbox/road_trip_crew_123/message_2.json",
            json.dumps(payload2),
        )


def make_messenger_fixture() -> None:
    zip_path = FIXTURES / "messenger_export.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        payload = {
            "title": "Startup Friends",
            "messages": [
                _meta_message("Olivia", 1704153600000, "Did they send the offer?"),
                _meta_message("Kai", 1704153660000, "Yes, got it this morning."),
            ],
        }
        zf.writestr(
            "your_facebook_activity/messages/inbox/startup_friends_999/message_1.json",
            json.dumps(payload),
        )


def make_discord_fixture() -> None:
    payload = {
        "channel": {"id": "123", "name": "direct-messages"},
        "messages": [
            {
                "id": "111111111111111111",
                "timestamp": "2024-02-01T10:00:00+00:00",
                "content": "Need that meeting link",
                "author": {"name": "Aria"},
            },
            {
                "id": "222222222222222222",
                "timestamp": "2024-02-01T10:01:00+00:00",
                "content": "",
                "author": {"name": "Aria"},
            },
        ],
    }
    write_json(FIXTURES / "discord_export.json", payload)


def main() -> None:
    make_telegram_fixture()
    make_whatsapp_fixture()
    make_instagram_fixture()
    make_messenger_fixture()
    make_discord_fixture()
    print(f"Fixtures generated in {FIXTURES}")


if __name__ == "__main__":
    main()
