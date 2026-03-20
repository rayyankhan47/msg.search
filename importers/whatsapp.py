"""WhatsApp export importer."""

from __future__ import annotations

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

    def _parse_lines(self, lines: list[str], conversation: str) -> list[dict]:
        return [{"line": line, "conversation": conversation} for line in lines if line.strip()]
