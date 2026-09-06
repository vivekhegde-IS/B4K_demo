"""Semantic retriever over the ChromaDB vector store.

Embeds the user query, searches ChromaDB, and returns ranked chunks
with metadata and relevance scores.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.config import TOP_K, RELEVANCE_THRESHOLD
from app.rag.embeddings import embed_query
from app.rag.vector_store import query_similar

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------
class RetrievalResult:
    """A single retrieved chunk with text, metadata, and distance."""

    __slots__ = ("text", "metadata", "distance")

    def __init__(self, text: str, metadata: dict[str, Any], distance: float):
        self.text = text
        self.metadata = metadata
        self.distance = distance  # lower = more similar (cosine distance)

    @property
    def relevance(self) -> float:
        """Convert cosine distance to a 0-1 relevance score."""
        return round(max(0.0, 1.0 - self.distance), 4)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "metadata": self.metadata,
            "distance": self.distance,
            "relevance": self.relevance,
        }

    def __repr__(self) -> str:
        src = self.metadata.get("source", "?")
        return f"<RetrievalResult src={src} rel={self.relevance:.2f}>"


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------
def retrieve(
    query: str,
    top_k: int = TOP_K,
    document_type: str | None = None,
    relevance_threshold: float | None = None,
) -> list[RetrievalResult]:
    """Retrieve the most relevant chunks for *query*.

    Parameters
    ----------
    query : str
        The user's natural-language question.
    top_k : int
        Maximum number of results to return.
    document_type : str | None
        If given, restrict results to this document_type metadata.
    relevance_threshold : float | None
        Minimum relevance score (0–1). Defaults to config value.
    """
    if not query.strip():
        return []

    threshold = relevance_threshold if relevance_threshold is not None else (1.0 - RELEVANCE_THRESHOLD)
    # RELEVANCE_THRESHOLD in config is max cosine *distance*; convert to min relevance.
    # e.g. distance threshold 1.5 → relevance threshold -0.5 → effectively no filter
    # We'll use a generous default and filter post-query.

    embedding = embed_query(query)

    where_filter = None
    if document_type:
        where_filter = {"document_type": document_type}

    raw = query_similar(embedding, n_results=top_k, where=where_filter)

    results: list[RetrievalResult] = []
    if not raw.get("ids") or not raw["ids"][0]:
        return results

    for doc_id, doc_text, meta, dist in zip(
        raw["ids"][0],
        raw["documents"][0],
        raw["metadatas"][0],
        raw["distances"][0],
    ):
        result = RetrievalResult(text=doc_text, metadata=meta, distance=dist)
        # Only include results above a reasonable relevance bar
        if result.relevance >= 0.1:
            results.append(result)

    logger.info(
        "Retrieved %d results for query (top_k=%d, type=%s)",
        len(results),
        top_k,
        document_type,
    )
    return results
