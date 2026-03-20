"""Search command wiring."""

from __future__ import annotations

from search.query import search_messages


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
