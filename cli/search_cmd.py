"""Search command wiring."""

from __future__ import annotations

from rich.panel import Panel
from rich.text import Text

from search.query import search_messages
from utils.console import console


PLATFORM_COLORS = {
    "telegram": "cyan",
    "whatsapp": "green",
    "imessage": "blue",
    "instagram": "magenta",
    "messenger": "bright_blue",
    "discord": "purple",
}


def run_search(
    query: str,
    platform: str | None = None,
    from_: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Run search with CLI args mapped to search engine parameters."""
    return search_messages(
        query=query,
        platform=platform,
        sender=from_,
        after=after,
        before=before,
        limit=limit,
    )


def display_results(results: list[dict]) -> None:
    """Render search results in Rich panels."""
    for idx, result in enumerate(results, start=1):
        platform = str(result.get("platform", "unknown")).lower()
        color = PLATFORM_COLORS.get(platform, "white")
        header = Text()
        header.append(f"{idx}. ", style="bold")
        header.append(platform, style=f"bold {color}")
        header.append(f" • {result.get('sender', 'Unknown')}", style="bold")
        header.append(f" • {result.get('timestamp', '')}", style="dim")

        body = (
            f"[bold]Conversation:[/bold] {result.get('conversation', 'Unknown')}\n"
            f"{result.get('content', '')}\n"
            f"[dim]Score: {result.get('score', 0):.4f}[/dim]"
        )
        console.print(Panel(body, title=header, border_style=color))
