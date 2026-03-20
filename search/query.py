"""Search functions over embedded messages."""

from core.database import get_collection
from core.embedder import Embedder


def _build_where_clause(
    platform: str | None,
    sender: str | None,
    after: str | None,
    before: str | None,
) -> dict | None:
    clauses: list[dict] = []

    if platform:
        clauses.append({"platform": {"$eq": platform}})
    if sender:
        clauses.append({"sender": {"$eq": sender}})
    if after:
        clauses.append({"timestamp": {"$gte": after}})
    if before:
        clauses.append({"timestamp": {"$lte": before}})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


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
    where_clause = _build_where_clause(platform, sender, after, before)

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
        output.append(
            {
                "content": document,
                "sender": metadata.get("sender", ""),
                "timestamp": metadata.get("timestamp", ""),
                "platform": metadata.get("platform", ""),
                "conversation": metadata.get("conversation", ""),
                "score": score,
            }
        )

    output.sort(key=lambda item: item["score"], reverse=True)
    return output[:limit]
