"""Search command wiring."""

from __future__ import annotations

import re

from rich.panel import Panel
from rich.text import Text

from search.query import search_messages
from utils.colors import PLATFORM_COLORS
from utils.console import console


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


def _highlight_content(content: str, query: str) -> str:
    terms = [term for term in re.findall(r"\w+", query) if len(term) >= 3]
    if not terms:
        return content
    pattern = re.compile("|".join(re.escape(term) for term in terms), flags=re.IGNORECASE)
    return pattern.sub(lambda m: f"[bold yellow]{m.group(0)}[/bold yellow]", content)


def display_results(results: list[dict], query: str) -> None:
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
            f"{_highlight_content(str(result.get('content', '')), query)}\n"
            f"[dim]Score: {result.get('score', 0):.4f}[/dim]"
        )
        console.print(Panel(body, title=header, border_style=color))
