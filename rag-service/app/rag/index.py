"""Indexing script for the RetailMate RAG knowledge base.

Usage::

    cd rag-service
    python -m app.rag.index

Processes:
  1. Policy PDF  → chunks → ChromaDB
  2. Store information TXT → chunks → ChromaDB
  3. Product catalog JSON → per-product docs → ChromaDB

Idempotent: running multiple times does not create duplicate chunks
because the vector store uses deterministic IDs and upsert semantics.
"""

from __future__ import annotations

import logging
import os
import sys

# Ensure the rag-service root is on sys.path so `app.*` imports work
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SERVICE_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir, os.pardir))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

from app.config import KNOWLEDGE_BASE_DIR, PRODUCT_CATALOG_PATH  # noqa: E402
from app.rag.loader import load_pdf, load_txt, load_product_catalog  # noqa: E402
from app.rag.chunker import chunk_documents  # noqa: E402
from app.rag.vector_store import upsert_documents, collection_count  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("indexer")


def run_indexing() -> None:
    """Run the full indexing pipeline."""
    all_chunks = []

    # ----- 1. Policy PDF -----
    pdf_path = os.path.join(KNOWLEDGE_BASE_DIR, "order_cancellation_return_policy.pdf")
    if os.path.isfile(pdf_path):
        logger.info("Indexing policy PDF: %s", pdf_path)
        docs = load_pdf(pdf_path, document_type="policy")
        chunks = chunk_documents(docs)
        all_chunks.extend(chunks)
        logger.info("  → %d chunks from policy PDF", len(chunks))
    else:
        logger.warning("Policy PDF not found at %s — skipping.", pdf_path)

    # ----- 2. Store information TXT -----
    store_path = os.path.join(KNOWLEDGE_BASE_DIR, "store_information.txt")
    if os.path.isfile(store_path):
        logger.info("Indexing store information: %s", store_path)
        docs = load_txt(store_path, document_type="store_info")
        chunks = chunk_documents(docs)
        all_chunks.extend(chunks)
        logger.info("  → %d chunks from store info", len(chunks))
    else:
        logger.warning("Store information not found at %s — skipping.", store_path)

    # ----- 3. Product catalog JSON -----
    catalog_path = PRODUCT_CATALOG_PATH
    if not os.path.isfile(catalog_path):
        # Try relative to knowledge_base
        catalog_path = os.path.join(
            os.path.dirname(KNOWLEDGE_BASE_DIR),
            "..",
            "shared",
            "sample_data",
            "products.json",
        )
    if os.path.isfile(catalog_path):
        logger.info("Indexing product catalog: %s", catalog_path)
        docs = load_product_catalog(catalog_path)
        # Product docs are typically small — no need to re-chunk
        all_chunks.extend(docs)
        logger.info("  → %d product documents", len(docs))
    else:
        logger.warning("Product catalog not found — skipping.")

    # ----- Upsert into ChromaDB -----
    if all_chunks:
        texts = [c["text"] for c in all_chunks]
        metas = [c["metadata"] for c in all_chunks]
        upsert_documents(texts, metas)
        logger.info(
            "Indexing complete. Total collection size: %d documents.",
            collection_count(),
        )
    else:
        logger.warning("No documents found to index.")


if __name__ == "__main__":
    run_indexing()
