"""ChromaDB vector store wrapper.

Provides persistent storage with deterministic IDs and upsert semantics
so that re-indexing the same documents does not create duplicates.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import CHROMA_PERSIST_DIRECTORY, CHROMA_COLLECTION_NAME
from app.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton client / collection
# ---------------------------------------------------------------------------
_client: Optional[chromadb.ClientAPI] = None
_collection = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        logger.info("Initialising ChromaDB client (persist=%s)…", CHROMA_PERSIST_DIRECTORY)
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
    return _client


def get_collection():
    """Return (or create) the default ChromaDB collection."""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB collection '%s' ready (%d documents).",
            CHROMA_COLLECTION_NAME,
            _collection.count(),
        )
    return _collection


# ---------------------------------------------------------------------------
# Deterministic ID generation
# ---------------------------------------------------------------------------
def _make_id(source: str, chunk_index: int, extra: str = "", page: str = "") -> str:
    """Create a stable, deterministic ID for a chunk."""
    raw = f"{source}::page{page}::{chunk_index}::{extra}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------
def upsert_documents(
    texts: list[str],
    metadatas: list[dict[str, Any]],
    ids: list[str] | None = None,
    batch_size: int = 100,
) -> int:
    """Upsert documents into ChromaDB.  Returns the number of documents stored."""
    collection = get_collection()

    if ids is None:
        ids = [
            _make_id(
                m.get("source", "unknown"),
                m.get("chunk_index", i),
                f"{m.get('product_id', '')}_{i}",
                str(m.get("page", "")),
            )
            for i, m in enumerate(metadatas)
        ]

    # Embed in batches
    total = len(texts)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_texts = texts[start:end]
        batch_ids = ids[start:end]
        batch_metas = metadatas[start:end]

        # ChromaDB metadata values must be str/int/float/bool
        clean_metas = [_clean_metadata(m) for m in batch_metas]

        embeddings = embed_texts(batch_texts)

        collection.upsert(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=clean_metas,
        )
        logger.info("Upserted batch %d–%d / %d", start, end, total)

    logger.info("Upsert complete. Collection now has %d documents.", collection.count())
    return total


def _clean_metadata(meta: dict) -> dict:
    """Ensure all metadata values are ChromaDB-compatible scalars."""
    clean = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)):
            clean[k] = v
        elif v is None:
            clean[k] = ""
        else:
            clean[k] = str(v)
    return clean


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------
def query_similar(
    query_embedding: list[float],
    n_results: int = 5,
    where: dict | None = None,
) -> dict:
    """Search for the top-k most similar documents.

    Returns a dict with keys: ids, documents, metadatas, distances.
    """
    collection = get_collection()
    kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": min(n_results, collection.count()) if collection.count() > 0 else 1,
    }
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    return results


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def collection_count() -> int:
    return get_collection().count()


def reset_collection() -> None:
    """Delete and recreate the collection (for testing)."""
    global _collection
    client = _get_client()
    try:
        client.delete_collection(CHROMA_COLLECTION_NAME)
    except Exception:
        pass
    _collection = None
    get_collection()
