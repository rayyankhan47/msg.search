"""msgsearch CLI entrypoint."""

import shutil

from rich.panel import Panel
import typer

from core.database import get_collection
from cli.search_cmd import display_results, run_search
from cli.reset_cmd import reset_all, reset_platform
from cli.status_cmd import show_status
from cli.sync import sync_all_connected, sync_single_platform
from utils.config import Config
from utils.console import console
from utils.storage import DATA_DIR, DB_DIR, init_data_dir

app = typer.Typer(help="Search your personal messages locally.")
config: Config | None = None


@app.callback()
def startup() -> None:
    """Initialize storage/config before running any command."""
    global config  # pylint: disable=global-statement

    first_run = not (DATA_DIR / "config.json").exists()
    init_data_dir()
    config = Config()
    _ensure_database_health()

    if first_run:
        console.print("[bold cyan]Welcome to msg.search![/bold cyan]")
        console.print("Run [bold]msgsearch sync <platform>[/bold] to get started.")


def _ensure_database_health() -> None:
    """Detect broken Chroma DB state and offer reset."""
    try:
        get_collection()
    except Exception as exc:  # noqa: BLE001
        console.print(
            f"[red]Warning:[/red] ChromaDB could not be opened ({exc}). "
            "Your DB may be corrupted."
        )
        should_reset = typer.confirm(
            "Do you want to reset the local database now? You can re-import afterward.",
            default=False,
        )
        if not should_reset:
            return
        if DB_DIR.exists():
            shutil.rmtree(DB_DIR)
        DB_DIR.mkdir(parents=True, exist_ok=True)
        get_collection()
        console.print("[green]Database reset complete.[/green]")


@app.command()
def search(
    query: str,
    platform: str | None = typer.Option(None, "--platform"),
    from_: str | None = typer.Option(None, "--from"),
    after: str | None = typer.Option(None, "--after"),
    before: str | None = typer.Option(None, "--before"),
    limit: int = typer.Option(20, "--limit"),
) -> None:
    """Search indexed messages."""
    results = run_search(
        query=query,
        platform=platform,
        from_=from_,
        after=after,
        before=before,
        limit=limit,
    )
    if not results:
        if config and not config.get("connected_platforms", []):
            console.print("[yellow]No data indexed yet. Run msgsearch sync <platform> first.[/yellow]")
        else:
            console.print(
                "[yellow]No messages found. Try broader terms, removing filters, "
                "or syncing more platforms.[/yellow]"
            )
        return
    display_results(results, query=query)


@app.command()
def sync(platform: str, file: str | None = typer.Option(None, "--file", "--path")) -> None:
    """Sync or import messages for a platform."""
    if config is None:
        raise RuntimeError("Config not loaded.")
    if platform == "all":
        sync_all_connected(config)
    else:
        sync_single_platform(config, platform=platform, file_path=file)


@app.command()
def status() -> None:
    """Show platform sync status."""
    if config is None:
        raise RuntimeError("Config not loaded.")
    show_status(config)


@app.command()
def reset(platform: str = typer.Option(None, "--platform")) -> None:
    """Reset indexed data."""
    global config  # pylint: disable=global-statement
    if config is None:
        raise RuntimeError("Config not loaded.")
    if platform:
        reset_platform(config, platform.lower().strip())
        return
    reset_all(DATA_DIR)
    # Re-load empty config file after full reset.
    config = Config()


def run() -> None:
    """Run CLI with top-level error handling."""
    try:
        app()
    except Exception as exc:  # noqa: BLE001
        console.print(
            Panel(
                (
                    f"[bold red]Unexpected error:[/bold red] {exc}\n\n"
                    "Please file an issue on GitHub with the command you ran."
                ),
                title="msg.search error",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    run()

