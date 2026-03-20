"""Search functions over embedded messages."""

from datetime import datetime, timezone

from core.database import get_collection
from core.embedder import Embedder


def _build_where_clause(
    platform: str | None,
    sender: str | None,
) -> dict | None:
    clauses: list[dict] = []

    if platform:
        clauses.append({"platform": {"$eq": platform}})
    if sender:
        clauses.append({"sender": {"$eq": sender}})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _within_date_range(timestamp: str, after: str | None, before: str | None) -> bool:
    if not (after or before):
        return True
    if not timestamp:
        return False

    try:
        ts = datetime.fromisoformat(timestamp)
        after_dt = datetime.fromisoformat(after) if after else None
        before_dt = datetime.fromisoformat(before) if before else None

        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if after_dt and after_dt.tzinfo is None:
            after_dt = after_dt.replace(tzinfo=timezone.utc)
        if before_dt and before_dt.tzinfo is None:
            before_dt = before_dt.replace(tzinfo=timezone.utc)
        if after_dt and ts < after_dt:
            return False
        if before_dt and ts > before_dt:
            return False
        return True
    except ValueError:
        # Fallback to lexical compare for non-standard but sortable values.
        if after and timestamp < after:
            return False
        if before and timestamp > before:
            return False
        return True


def search_messages(
    query: str,
    platform: str | None = None,
    sender: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Run semantic search over indexed messages."""
    if not query.strip():
        return []
    limit = max(1, limit)

    embedder = Embedder()
    query_embedding = embedder.embed([query])[0]
    collection = get_collection()
    where_clause = _build_where_clause(platform, sender)

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": limit,
        "include": ["documents", "metadatas", "distances"],
    }
    if where_clause:
        query_kwargs["where"] = where_clause

    results = collection.query(**query_kwargs)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output: list[dict] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        score = 1 - float(distance)
        row = {
            "content": document,
            "sender": metadata.get("sender", ""),
            "timestamp": metadata.get("timestamp", ""),
            "platform": metadata.get("platform", ""),
            "conversation": metadata.get("conversation", ""),
            "score": score,
        }
        if _within_date_range(str(row["timestamp"]), after, before):
            output.append(row)

    output.sort(key=lambda item: item["score"], reverse=True)
    return output[:limit]
