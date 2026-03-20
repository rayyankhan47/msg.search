"""ChromaDB helpers for persistent local storage."""

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

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
    platform_label: str = "messages",
) -> int:
    """Insert new messages only, skipping IDs that already exist."""
    if not messages:
        return 0

    collection = get_collection()
    active_embedder = embedder or Embedder()
    inserted = 0
    skipped = 0
    seen_ids: set[str] = set()

    with Progress(
        TextColumn(f"Indexing {platform_label}..."),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("• {task.completed}/{task.total}"),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task("index", total=len(messages))

        for start in range(0, len(messages), batch_size):
            raw_batch = messages[start : start + batch_size]
            deduped_batch: list[dict] = []
            for message in raw_batch:
                message_id = str(message.get("id", ""))
                if not message_id or message_id in seen_ids:
                    skipped += 1
                    continue
                seen_ids.add(message_id)
                deduped_batch.append(message)

            batch = deduped_batch
            batch = [m for m in batch if m.get("content")]
            skipped += len(deduped_batch) - len(batch)
            if not batch:
                progress.advance(task_id, len(raw_batch))
                continue

            batch_ids = [str(m["id"]) for m in batch]
            existing = collection.get(ids=batch_ids, include=[])
            existing_ids = set(existing.get("ids", []))
            new_batch = [m for m in batch if str(m["id"]) not in existing_ids]
            skipped += len(batch) - len(new_batch)
            if not new_batch:
                progress.advance(task_id, len(raw_batch))
                continue

            ids = [str(m["id"]) for m in new_batch]
            documents = [str(m["content"]) for m in new_batch]
            embeddings = active_embedder.embed(documents)
            metadatas = [
                {
                    "sender": str(m.get("sender", "")),
                    "timestamp": str(m.get("timestamp", "")),
                    "platform": str(m.get("platform", "")),
                    "conversation": str(m.get("conversation", "")),
                }
                for m in new_batch
            ]

            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            inserted += len(new_batch)
            progress.advance(task_id, len(raw_batch))

    print(f"Indexed {inserted} new messages, skipped {skipped} already indexed.")
    return inserted
