"""WhatsApp export importer."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile


class WhatsAppImporter:
    """Parse WhatsApp TXT or ZIP exports."""

    def parse(self, filepath: str) -> list[dict]:
        path = Path(filepath)
        if path.suffix.lower() == ".zip":
            return self._parse_zip(path)
        return self._parse_txt(path, conversation=path.stem)

    def _parse_zip(self, zip_path: Path) -> list[dict]:
        messages: list[dict] = []
        with ZipFile(zip_path, "r") as archive:
            for member in archive.namelist():
                if not member.lower().endswith(".txt"):
                    continue
                content = archive.read(member).decode("utf-8", errors="replace")
                messages.extend(
                    self._parse_lines(content.splitlines(), conversation=Path(member).stem)
                )
        return messages

    def _parse_txt(self, txt_path: Path, conversation: str) -> list[dict]:
        content = txt_path.read_text(encoding="utf-8", errors="replace")
        return self._parse_lines(content.splitlines(), conversation=conversation)

    _LINE_PATTERN = re.compile(
        r"^(?:\[)?(?P<date>\d{1,2}/\d{1,2}/\d{2,4})(?:,|\s)\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)"
        r"(?:\s?(?P<ampm>AM|PM|am|pm))?(?:\])?(?:\s*-\s*|\s+)\s*(?P<sender>[^:]+):\s(?P<message>.*)$"
    )

    def _parse_lines(self, lines: list[str], conversation: str) -> list[dict]:
        parsed: list[dict] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = self._LINE_PATTERN.match(line)
            if not match:
                continue

            date_part = match.group("date")
            time_part = match.group("time")
            ampm = match.group("ampm")
            sender = match.group("sender").strip()
            message = match.group("message").strip()

            timestamp = self._parse_datetime(date_part, time_part, ampm)
            if not timestamp:
                continue

            parsed.append(
                {
                    "conversation": conversation,
                    "sender": sender,
                    "message": message,
                    "timestamp": timestamp,
                }
            )

        return parsed

    @staticmethod
    def _parse_datetime(date_part: str, time_part: str, ampm: str | None) -> str | None:
        value = f"{date_part} {time_part}{(' ' + ampm) if ampm else ''}".strip()
        formats = (
            "%d/%m/%y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%y %H:%M",
            "%d/%m/%Y %H:%M",
            "%m/%d/%y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%y %H:%M",
            "%m/%d/%Y %H:%M",
            "%d/%m/%y %I:%M:%S %p",
            "%d/%m/%Y %I:%M:%S %p",
            "%d/%m/%y %I:%M %p",
            "%d/%m/%Y %I:%M %p",
            "%m/%d/%y %I:%M:%S %p",
            "%m/%d/%Y %I:%M:%S %p",
            "%m/%d/%y %I:%M %p",
            "%m/%d/%Y %I:%M %p",
        )
        for pattern in formats:
            try:
                return datetime.strptime(value, pattern).isoformat()
            except ValueError:
                continue
        return None
