"""Sync command helpers."""

from __future__ import annotations

from pathlib import Path
import webbrowser
from datetime import datetime, timezone
import time

import typer

from core.database import insert_messages
from importers.discord import DiscordImporter, InvalidFormatError
from importers.imessage import iMessageImporter
from importers.instagram import InstagramImporter
from importers.messenger import MessengerImporter
from importers.telegram import TelegramImporter
from importers.telegram_client import TelegramAuthError, TelegramClientManager
from importers.whatsapp import WhatsAppImporter
from utils.console import console
from utils.config import Config


DISCORD_TOS_DISCLAIMER = (
    "⚠️ Exporting Discord messages using third-party tools may violate Discord's Terms "
    "of Service. The creator of msg.search does not promote or facilitate ToS "
    "violations. By proceeding, you confirm you take full responsibility for how you "
    "obtained this file."
)
EXPORT_BASED_PLATFORMS = {"whatsapp", "instagram", "messenger"}


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
    started = time.perf_counter()
    messages = sync_primary_platforms(platform, file_path=file_path)
    inserted = insert_messages(messages, platform_label=platform)
    elapsed = time.perf_counter() - started
    console.print(
        f"[green]Synced {platform}: parsed {len(messages)}, indexed {inserted}, "
        f"time {elapsed:.1f}s.[/green]"
    )
    return inserted


def _guided_meta_flow(platform: str) -> None:
    if platform == "instagram":
        url = "https://www.instagram.com/accounts/privacy_and_security/"
        typer.echo("To sync Instagram messages, request a new Meta data export (JSON, Messages).")
    else:
        url = "https://www.facebook.com/dyi/"
        typer.echo("To sync Messenger messages, request a new Meta data export (JSON, Messages).")

    open_browser = typer.confirm("Open settings page in browser now?", default=True)
    if open_browser:
        webbrowser.open(url)


def sync_guided_platforms(platform: str, file_path: str | None = None) -> list[dict] | None:
    """Sync Instagram, Messenger, or Discord via guided file flow."""
    platform = platform.lower().strip()

    if platform == "instagram":
        if not file_path:
            _guided_meta_flow("instagram")
            has_file = typer.confirm("Do you already have the Instagram export ZIP?", default=False)
            if not has_file:
                return None
            file_path = typer.prompt("Path to your Instagram export ZIP")
        return InstagramImporter().parse(file_path)

    if platform == "messenger":
        if not file_path:
            _guided_meta_flow("messenger")
            has_file = typer.confirm("Do you already have the Messenger export ZIP?", default=False)
            if not has_file:
                return None
            file_path = typer.prompt("Path to your Messenger export ZIP")
        return MessengerImporter().parse(file_path)

    if platform == "discord":
        return sync_discord(file_path=file_path)

    raise ValueError(f"Unsupported guided platform: {platform}")


def sync_and_index_guided(platform: str, file_path: str | None = None) -> int:
    """Sync guided platform and index parsed messages."""
    started = time.perf_counter()
    messages = sync_guided_platforms(platform, file_path=file_path)
    if not messages:
        console.print(f"[yellow]No new data synced for {platform}.[/yellow]")
        return 0
    inserted = insert_messages(messages, platform_label=platform)
    elapsed = time.perf_counter() - started
    console.print(
        f"[green]Synced {platform}: parsed {len(messages)}, indexed {inserted}, "
        f"time {elapsed:.1f}s.[/green]"
    )
    return inserted


def update_config_after_sync(config: Config, platform: str) -> None:
    """Mark platform connected and update last sync timestamp."""
    connected = list(config.get("connected_platforms", []))
    if platform not in connected:
        connected.append(platform)
        config.set("connected_platforms", connected)

    last_sync = dict(config.get("last_sync", {}))
    last_sync[platform] = datetime.now(timezone.utc).isoformat()
    config.set("last_sync", last_sync)


def _resolve_export_file_path(config: Config, platform: str, provided: str | None) -> str | None:
    if platform not in EXPORT_BASED_PLATFORMS:
        return provided
    if provided:
        return provided

    last_paths = dict(config.get("last_import_path", {}))
    previous = last_paths.get(platform)
    if previous and Path(previous).exists():
        return typer.prompt(
            f"Path to your {platform} export file",
            default=previous,
            show_default=True,
        )
    return typer.prompt(f"Path to your {platform} export file")


def sync_all_connected(config: Config) -> dict[str, int]:
    """Sync all previously connected platforms."""
    connected = config.get("connected_platforms", [])
    if not connected:
        console.print("[yellow]No connected platforms yet. Run msgsearch sync <platform> first.[/yellow]")
        return {}

    summary: dict[str, int] = {}
    primary = {"telegram", "whatsapp", "imessage"}
    guided = {"instagram", "messenger", "discord"}

    for platform in connected:
        try:
            if platform in primary:
                summary[platform] = sync_and_index_primary(platform)
            elif platform in guided:
                summary[platform] = sync_and_index_guided(platform)
            else:
                console.print(f"[yellow]Skipping unknown platform: {platform}[/yellow]")
                continue
            update_config_after_sync(config, platform)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Failed syncing {platform}: {exc}[/red]")
            summary[platform] = 0

    console.print("[bold]Sync summary:[/bold]")
    for platform, count in summary.items():
        console.print(f"- {platform}: {count} new messages")
    return summary


def sync_single_platform(config: Config, platform: str, file_path: str | None = None) -> int:
    """Sync one platform and persist config updates."""
    platform = platform.lower().strip()
    if platform == "all":
        raise ValueError("Use sync_all_connected for 'all'.")

    resolved_file_path = _resolve_export_file_path(config, platform, file_path)

    primary = {"telegram", "whatsapp", "imessage"}
    guided = {"instagram", "messenger", "discord"}
    if platform in primary:
        inserted = sync_and_index_primary(platform, file_path=resolved_file_path)
    elif platform in guided:
        inserted = sync_and_index_guided(platform, file_path=resolved_file_path)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    update_config_after_sync(config, platform)
    if platform in EXPORT_BASED_PLATFORMS and resolved_file_path:
        last_paths = dict(config.get("last_import_path", {}))
        last_paths[platform] = resolved_file_path
        config.set("last_import_path", last_paths)
    return inserted
