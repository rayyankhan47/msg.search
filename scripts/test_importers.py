"""Quick smoke test for Meta importers."""

from __future__ import annotations

import argparse
import json

from importers.instagram import InstagramImporter
from importers.messenger import MessengerImporter


def run_test(name: str, importer: object, filepath: str) -> None:
    print(f"\n{name} importer")
    try:
        messages = importer.parse(filepath)  # type: ignore[attr-defined]
        print(f"- Parsed messages: {len(messages)}")
        for sample in messages[:3]:
            print(f"- Sample: {json.dumps(sample, ensure_ascii=False)[:220]}")
    except Exception as exc:  # noqa: BLE001
        print(f"- Error: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Instagram and Messenger importers.")
    parser.add_argument("--instagram", help="Path to Instagram export ZIP")
    parser.add_argument("--messenger", help="Path to Messenger export ZIP")
    args = parser.parse_args()

    if args.instagram:
        run_test("Instagram", InstagramImporter(), args.instagram)
    else:
        print("Instagram path not provided. Use --instagram /path/to/export.zip")

    if args.messenger:
        run_test("Messenger", MessengerImporter(), args.messenger)
    else:
        print("Messenger path not provided. Use --messenger /path/to/export.zip")
