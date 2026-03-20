"""msgsearch CLI entrypoint."""

import typer

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
def search(query: str) -> None:
    """Search indexed messages."""
    typer.echo("not yet implemented")


@app.command()
def sync(platform: str) -> None:
    """Sync or import messages for a platform."""
    typer.echo("not yet implemented")


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

