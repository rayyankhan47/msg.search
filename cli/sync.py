"""Sync command helpers."""

from __future__ import annotations

from pathlib import Path

import typer

from importers.discord import DiscordImporter, InvalidFormatError


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
