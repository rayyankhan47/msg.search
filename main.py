"""msgsearch CLI entrypoint."""

import typer


app = typer.Typer(help="Search your personal messages locally.")


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

