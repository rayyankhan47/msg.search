"""Status command helpers."""

from __future__ import annotations

from rich.table import Table

from core.database import get_collection
from utils.config import Config
from utils.console import console
from utils.colors import PLATFORM_COLORS


SUPPORTED_PLATFORMS = [
    "telegram",
    "whatsapp",
    "imessage",
    "instagram",
    "messenger",
    "discord",
]


def show_status(config: Config) -> None:
    """Render sync and index status for all supported platforms."""
    connected = set(config.get("connected_platforms", []))
    last_sync = dict(config.get("last_sync", {}))
    collection = get_collection()

    table = Table(title="msg.search platform status")
    table.add_column("Platform")
    table.add_column("Connected")
    table.add_column("Last Synced")
    table.add_column("Indexed Messages", justify="right")

    for platform in SUPPORTED_PLATFORMS:
        is_connected = "[green]✓[/green]" if platform in connected else "[grey58]-[/grey58]"
        last = last_sync.get(platform, "-")
        result = collection.get(where={"platform": {"$eq": platform}}, include=[])
        count = len(result.get("ids", []))
        color = PLATFORM_COLORS.get(platform, "white")
        table.add_row(f"[{color}]{platform}[/{color}]", is_connected, last, str(count))

    console.print(table)
