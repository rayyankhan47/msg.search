"""Embedding model wrapper for semantic search."""

from sentence_transformers import SentenceTransformer

from utils.console import console


MODEL_NAME = "all-MiniLM-L6-v2"


class Embedder:
    """Load and run the local sentence-transformers model."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        self.model = self._load_model()

    def _load_model(self) -> SentenceTransformer:
        try:
            # Fast path: use only local cache if already downloaded.
            return SentenceTransformer(self.model_name, local_files_only=True)
        except Exception:
            pass

        with console.status(
            "Downloading embedding model (one-time, ~80MB)...",
            spinner="dots",
        ):
            return SentenceTransformer(self.model_name)

    def embed(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """Embed input texts and return vectors as plain lists."""
        if not texts:
            return []

        vectors = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vectors.tolist()
