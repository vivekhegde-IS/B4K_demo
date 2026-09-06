"""Sentence-Transformer embedding manager.

Loads the model once at module level and reuses it for all requests.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton model holder
# ---------------------------------------------------------------------------
_model = None


def _get_model():
    """Lazily load the SentenceTransformer model (once)."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s (this may take a moment)…", EMBEDDING_MODEL)
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _model


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts and return a list of float vectors."""
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]


def get_embedding_dimension() -> int:
    """Return the dimensionality of the loaded model's embeddings."""
    model = _get_model()
    return model.get_sentence_embedding_dimension()
