"""Document loader for PDF, TXT, and JSON product catalog files.

Normalises every source into a list of dicts::

    {"text": "...", "metadata": {"source": "...", "document_type": "...", ...}}
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal representation
# ---------------------------------------------------------------------------
DocChunk = dict[str, Any]  # {"text": str, "metadata": dict}


# ---------------------------------------------------------------------------
# PDF loader (uses PyMuPDF)
# ---------------------------------------------------------------------------
def load_pdf(path: str, document_type: str = "policy") -> list[DocChunk]:
    """Load a PDF file and return one document chunk per page.

    PyMuPDF preserves reading order reasonably well for table-heavy PDFs.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise ImportError("PyMuPDF is required for PDF loading: pip install PyMuPDF") from exc

    docs: list[DocChunk] = []
    filename = os.path.basename(path)
    logger.info("Loading PDF: %s", path)

    pdf = fitz.open(path)
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text("text")
        if not text or not text.strip():
            continue
        docs.append(
            {
                "text": text.strip(),
                "metadata": {
                    "source": filename,
                    "document_type": document_type,
                    "page": page_num + 1,  # 1-indexed
                },
            }
        )
    pdf.close()
    logger.info("Loaded %d pages from %s", len(docs), filename)
    return docs


# ---------------------------------------------------------------------------
# TXT loader
# ---------------------------------------------------------------------------
def load_txt(path: str, document_type: str = "general") -> list[DocChunk]:
    """Load a plain-text file as a single document chunk."""
    filename = os.path.basename(path)
    logger.info("Loading TXT: %s", path)
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read().strip()
    if not text:
        logger.warning("Empty TXT file: %s", path)
        return []
    return [
        {
            "text": text,
            "metadata": {
                "source": filename,
                "document_type": document_type,
            },
        }
    ]


# ---------------------------------------------------------------------------
# JSON product-catalog loader
# ---------------------------------------------------------------------------
def load_product_catalog(path: str) -> list[DocChunk]:
    """Load a JSON product catalog and produce one document per product.

    Each product is converted to a natural-language description so that
    semantic search can match user queries like "blue Nike shoes".
    """
    filename = os.path.basename(path)
    logger.info("Loading product catalog: %s", path)
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read().strip()
    if not content:
        logger.warning("Empty product catalog: %s", path)
        return []

    products = json.loads(content)
    if not isinstance(products, list):
        logger.warning("Product catalog is not a list: %s", path)
        return []

    docs: list[DocChunk] = []
    for product in products:
        pid = product.get("product_id", "unknown")
        parts: list[str] = []
        if product.get("name"):
            parts.append(f"Product: {product['name']}")
        if product.get("brand"):
            parts.append(f"Brand: {product['brand']}")
        if product.get("category"):
            parts.append(f"Category: {product['category']}")
        if product.get("subcategory"):
            parts.append(f"Subcategory: {product['subcategory']}")
        if product.get("color"):
            parts.append(f"Color: {product['color']}")
        if product.get("size"):
            parts.append(f"Size: {product['size']}")
        if product.get("price") is not None:
            parts.append(f"Price: ₹{product['price']}")
        if product.get("description"):
            parts.append(f"Description: {product['description']}")
        if product.get("location"):
            loc = product["location"]
            loc_parts = []
            if loc.get("store"):
                loc_parts.append(f"Store: {loc['store']}")
            if loc.get("aisle"):
                loc_parts.append(f"Aisle: {loc['aisle']}")
            if loc.get("shelf"):
                loc_parts.append(f"Shelf: {loc['shelf']}")
            if loc_parts:
                parts.append("Location: " + ", ".join(loc_parts))
        text = "\n".join(parts) if parts else json.dumps(product)
        docs.append(
            {
                "text": text,
                "metadata": {
                    "source": filename,
                    "document_type": "product",
                    "product_id": pid,
                },
            }
        )
    logger.info("Loaded %d products from %s", len(docs), filename)
    return docs


# ---------------------------------------------------------------------------
# Auto-detect loader
# ---------------------------------------------------------------------------
def load_document(path: str, document_type: str | None = None) -> list[DocChunk]:
    """Auto-detect file type and load accordingly."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf(path, document_type=document_type or "policy")
    elif ext == ".txt":
        return load_txt(path, document_type=document_type or "general")
    elif ext == ".json":
        return load_product_catalog(path)
    else:
        logger.warning("Unsupported file type: %s", ext)
        return []
