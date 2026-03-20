"""Reset command helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer

from core.database import get_collection
from utils.config import Config
from utils.console import console
from utils.storage import RAW_DIR


def reset_platform(config: Config, platform: str) -> None:
    """Delete one platform's indexed data and cached raw files."""
    confirmed = typer.prompt(
        f"This will permanently delete all {platform} messages and embeddings. "
        "Type 'yes' to confirm"
    )
    if confirmed.strip().lower() != "yes":
        console.print("[yellow]Cancelled.[/yellow]")
        return

    collection = get_collection()
    collection.delete(where={"platform": {"$eq": platform}})

    platform_raw_dir = RAW_DIR / platform
    if platform_raw_dir.exists():
        shutil.rmtree(platform_raw_dir)
    platform_raw_dir.mkdir(parents=True, exist_ok=True)

    connected = [p for p in config.get("connected_platforms", []) if p != platform]
    config.set("connected_platforms", connected)

    last_sync = dict(config.get("last_sync", {}))
    last_sync.pop(platform, None)
    config.set("last_sync", last_sync)

    last_paths = dict(config.get("last_import_path", {}))
    last_paths.pop(platform, None)
    config.set("last_import_path", last_paths)

    console.print(
        f"[green]{platform.capitalize()} data deleted. All other platforms are untouched.[/green]"
    )


def reset_all(data_dir: Path) -> None:
    """Delete and recreate the whole ~/.msgsearch data directory."""
    confirmed = typer.prompt(
        "This will permanently delete all indexed messages and embeddings in ~/.msgsearch/. "
        "Type 'yes' to confirm"
    )
    if confirmed.strip().lower() != "yes":
        console.print("[yellow]Cancelled.[/yellow]")
        return

    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    console.print("[green]All data deleted.[/green]")
