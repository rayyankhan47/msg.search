"""Performance benchmarks for msg.search."""

from __future__ import annotations

import argparse
import random
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from core import database
from core.database import get_collection, insert_messages
from core.embedder import Embedder


WORDS = [
    "restaurant",
    "startup",
    "meeting",
    "address",
    "offer",
    "deadline",
    "airport",
    "reservation",
    "invoice",
    "project",
]


def generate_messages(count: int) -> list[dict]:
    random.seed(42)
    messages: list[dict] = []
    for i in range(count):
        content = " ".join(random.choices(WORDS, k=12))
        messages.append(
            {
                "id": f"bench:{i}",
                "content": content,
                "sender": f"user_{i % 25}",
                "timestamp": f"2024-01-{(i % 28) + 1:02d}T12:00:00+00:00",
                "platform": "benchmark",
                "conversation": f"thread_{i % 120}",
            }
        )
    return messages


def benchmark_embedding_speed(message_count: int, batch_size: int) -> None:
    messages = generate_messages(message_count)
    embedder = Embedder()

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "db"
        db_path.mkdir(parents=True, exist_ok=True)

        with patch.object(database, "DB_DIR", db_path), patch.object(
            database, "init_data_dir", lambda: None
        ):
            client = database.get_client()
            try:
                client.delete_collection(database.COLLECTION_NAME)
            except Exception:
                pass
            database.get_collection()

            started = time.perf_counter()
            inserted = insert_messages(
                messages,
                embedder=embedder,
                batch_size=batch_size,
                platform_label="benchmark",
            )
            elapsed = time.perf_counter() - started

    mps = inserted / elapsed if elapsed > 0 else 0.0
    print(f"Messages generated: {message_count}")
    print(f"Messages inserted: {inserted}")
    print(f"Elapsed: {elapsed:.2f}s")
    print(f"Throughput: {mps:.2f} messages/sec")


def benchmark_search_latency(
    message_count: int,
    batch_size: int,
    query_count: int,
    top_k: int,
) -> None:
    messages = generate_messages(message_count)
    embedder = Embedder()

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "db"
        db_path.mkdir(parents=True, exist_ok=True)

        with patch.object(database, "DB_DIR", db_path), patch.object(
            database, "init_data_dir", lambda: None
        ):
            client = database.get_client()
            try:
                client.delete_collection(database.COLLECTION_NAME)
            except Exception:
                pass
            get_collection()
            insert_messages(
                messages,
                embedder=embedder,
                batch_size=batch_size,
                platform_label="benchmark-search",
            )

            collection = get_collection()
            queries = [
                " ".join(random.choices(WORDS, k=3))
                for _ in range(query_count)
            ]

            latencies_ms: list[float] = []
            for query in queries:
                q_vec = embedder.embed([query])[0]
                started = time.perf_counter()
                collection.query(
                    query_embeddings=[q_vec],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"],
                )
                elapsed = (time.perf_counter() - started) * 1000
                latencies_ms.append(elapsed)

    avg_ms = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0
    print(f"Indexed messages: {message_count}")
    print(f"Queries run: {len(latencies_ms)}")
    print(f"Average query latency: {avg_ms:.2f} ms")
    print(f"Target: under 500ms for 50,000 messages")


def main() -> None:
    parser = argparse.ArgumentParser(description="msg.search benchmark tools")
    parser.add_argument("--mode", choices=["embed", "search"], default="embed")
    parser.add_argument("--messages", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--queries", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    if args.mode == "embed":
        benchmark_embedding_speed(args.messages, args.batch_size)
    elif args.mode == "search":
        benchmark_search_latency(
            message_count=args.messages,
            batch_size=args.batch_size,
            query_count=args.queries,
            top_k=args.top_k,
        )


if __name__ == "__main__":
    main()
