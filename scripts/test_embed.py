"""Quick smoke test for the local embedding model."""

from __future__ import annotations

import math

from core.embedder import Embedder


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


if __name__ == "__main__":
    sample_texts = [
        "That Italian restaurant on Saint Laurent is amazing.",
        "You should try the pasta place on St-Laurent.",
        "I need to renew my driver's license next week.",
        "Let's meet at 6 PM near the metro station.",
        "The startup sent me a job offer this morning.",
    ]

    embedder = Embedder()
    vectors = embedder.embed(sample_texts)

    print(f"Embedded {len(vectors)} sentences")
    print(f"Vector dimension: {len(vectors[0]) if vectors else 0}")

    sim = cosine_similarity(vectors[0], vectors[1])
    print(f"Similarity between related sentences: {sim:.4f}")
