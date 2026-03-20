"""ChromaDB helpers for persistent local storage."""

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

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
