"""msgsearch CLI entrypoint."""

import typer

from cli.search_cmd import display_results, run_search
from cli.sync import sync_all_connected, sync_single_platform
from utils.config import Config
from utils.console import console
from utils.storage import DATA_DIR, init_data_dir

app = typer.Typer(help="Search your personal messages locally.")
config: Config | None = None


@app.callback()
def startup() -> None:
    """Initialize storage/config before running any command."""
    global config  # pylint: disable=global-statement

    first_run = not (DATA_DIR / "config.json").exists()
    init_data_dir()
    config = Config()

    if first_run:
        console.print("[bold cyan]Welcome to msg.search![/bold cyan]")
        console.print("Run [bold]msgsearch sync <platform>[/bold] to get started.")


@app.command()
def search(
    query: str,
    platform: str = typer.Option(None, "--platform"),
    from_: str = typer.Option(None, "--from"),
    after: str = typer.Option(None, "--after"),
    before: str = typer.Option(None, "--before"),
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
    display_results(results)


@app.command()
def sync(platform: str, file: str = typer.Option(None, "--file", "--path")) -> None:
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
    typer.echo("not yet implemented")


@app.command()
def reset(platform: str = typer.Option(None, "--platform")) -> None:
    """Reset indexed data."""
    typer.echo("not yet implemented")


if __name__ == "__main__":
    app()

