"""Search functions over embedded messages."""

from core.database import get_collection
from core.embedder import Embedder


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

    embedder = Embedder()
    query_embedding = embedder.embed([query])[0]
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output: list[dict] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        output.append(
            {
                "content": document,
                "sender": metadata.get("sender", ""),
                "timestamp": metadata.get("timestamp", ""),
                "platform": metadata.get("platform", ""),
                "conversation": metadata.get("conversation", ""),
                "score": 1 - float(distance),
            }
        )

    return output
