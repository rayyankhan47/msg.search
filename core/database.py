"""ChromaDB helpers for persistent local storage."""

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

from core.embedder import Embedder
from utils.storage import DB_DIR, init_data_dir


COLLECTION_NAME = "messages"


def get_client() -> PersistentClient:
    """Return a persistent ChromaDB client under ~/.msgsearch/db."""
    init_data_dir()
    return PersistentClient(path=str(DB_DIR))


def get_collection() -> Collection:
    """Get or create the default messages collection."""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def insert_messages(
    messages: list[dict],
    embedder: Embedder | None = None,
    batch_size: int = 128,
) -> int:
    """Insert message documents, metadata, and embeddings into ChromaDB."""
    if not messages:
        return 0

    collection = get_collection()
    active_embedder = embedder or Embedder()
    inserted = 0

    for start in range(0, len(messages), batch_size):
        batch = messages[start : start + batch_size]
        batch = [m for m in batch if m.get("content")]
        if not batch:
            continue

        ids = [str(m["id"]) for m in batch]
        documents = [str(m["content"]) for m in batch]
        embeddings = active_embedder.embed(documents)
        metadatas = [
            {
                "sender": str(m.get("sender", "")),
                "timestamp": str(m.get("timestamp", "")),
                "platform": str(m.get("platform", "")),
                "conversation": str(m.get("conversation", "")),
            }
            for m in batch
        ]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        inserted += len(batch)

    return inserted
