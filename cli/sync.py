"""Sync command helpers."""

from __future__ import annotations

from pathlib import Path

import typer

from core.database import insert_messages
from importers.discord import DiscordImporter, InvalidFormatError
from importers.imessage import iMessageImporter
from importers.telegram import TelegramImporter
from importers.telegram_client import TelegramAuthError, TelegramClientManager
from importers.whatsapp import WhatsAppImporter
from utils.console import console


DISCORD_TOS_DISCLAIMER = (
    "⚠️ Exporting Discord messages using third-party tools may violate Discord's Terms "
    "of Service. The creator of msg.search does not promote or facilitate ToS "
    "violations. By proceeding, you confirm you take full responsibility for how you "
    "obtained this file."
)


def sync_discord(file_path: str | None = None) -> list[dict] | None:
    """Interactive Discord sync flow."""
    typer.echo(DISCORD_TOS_DISCLAIMER)

    if not file_path:
        ready = typer.confirm(
            "Have you already exported your Discord messages to a JSON file?",
            default=False,
        )
        if not ready:
            typer.echo("Come back once you have your export file ready.")
            return None
        file_path = typer.prompt("Path to your Discord export JSON")

    path = Path(file_path)
    if not path.exists():
        typer.echo(
            "File not found or invalid format. Please ensure you have a valid Discord "
            "JSON export and try again."
        )
        return None

    importer = DiscordImporter()
    try:
        return importer.parse(str(path))
    except InvalidFormatError:
        typer.echo(
            "File not found or invalid format. Please ensure you have a valid Discord "
            "JSON export and try again."
        )
        return None


def _prompt_export_path(platform: str) -> str:
    return typer.prompt(f"Path to your {platform} export file")


def sync_primary_platforms(platform: str, file_path: str | None = None) -> list[dict]:
    """Sync Telegram, WhatsApp, and iMessage."""
    platform = platform.lower().strip()

    if platform == "telegram":
        try:
            manager = TelegramClientManager()
            messages = manager.fetch_messages()
            if messages:
                return messages
            console.print(
                "[yellow]No Telegram messages fetched via auto-connect. "
                "Falling back to export parser.[/yellow]"
            )
        except TelegramAuthError as exc:
            console.print(f"[yellow]{exc}[/yellow]")
            console.print("[yellow]Falling back to Telegram export import.[/yellow]")

        export_path = file_path or _prompt_export_path("Telegram")
        return TelegramImporter().parse(export_path)

    if platform == "whatsapp":
        export_path = file_path or _prompt_export_path("WhatsApp")
        return WhatsAppImporter().parse(export_path)

    if platform == "imessage":
        return iMessageImporter().parse()

    raise ValueError(f"Unsupported primary platform: {platform}")


def sync_and_index_primary(platform: str, file_path: str | None = None) -> int:
    """Sync one primary platform and insert its new messages."""
    messages = sync_primary_platforms(platform, file_path=file_path)
    inserted = insert_messages(messages)
    console.print(f"[green]Synced {platform}: indexed {inserted} new messages.[/green]")
    return inserted
