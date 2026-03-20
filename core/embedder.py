"""Embedding model wrapper for semantic search."""

from sentence_transformers import SentenceTransformer

from utils.console import console


MODEL_NAME = "all-MiniLM-L6-v2"


class Embedder:
    """Load and run the local sentence-transformers model."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        self.model = self._load_model()

    def _is_model_cached(self) -> bool:
        try:
            SentenceTransformer(self.model_name, local_files_only=True)
            return True
        except Exception:
            return False

    def _load_model(self) -> SentenceTransformer:
        if self._is_model_cached():
            return SentenceTransformer(self.model_name)

        with console.status(
            "Downloading embedding model (one-time, ~80MB)...",
            spinner="dots",
        ):
            return SentenceTransformer(self.model_name)
