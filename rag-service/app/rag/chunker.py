"""Text chunker with configurable size and overlap.

Preserves metadata across chunks and attempts to respect section boundaries
for policy documents containing tabular category/window/action relationships.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

DocChunk = dict[str, Any]


# ---------------------------------------------------------------------------
# Section-aware splitting helpers
# ---------------------------------------------------------------------------
_SECTION_SEPARATORS = re.compile(
    r"\n(?=#{1,3}\s)|"               # Markdown headers
    r"\n(?=\d+\.\s)|"               # Numbered sections
    r"\n(?=[A-Z][A-Z\s]{4,}:?\n)|"  # ALL-CAPS headings
    r"\n{3,}",                       # Triple+ blank lines
    re.MULTILINE,
)


def _split_into_sections(text: str) -> list[str]:
    """Split text at natural section boundaries."""
    sections = _SECTION_SEPARATORS.split(text)
    return [s.strip() for s in sections if s and s.strip()]


# ---------------------------------------------------------------------------
# Core chunker
# ---------------------------------------------------------------------------
def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split *text* into overlapping chunks of approximately *chunk_size* chars.

    The algorithm first tries section-aware splitting.  Each section that fits
    within *chunk_size* is kept as-is (preserving tabular relationships such as
    ``Category → Return Window → Allowed Action``).  Sections larger than
    *chunk_size* are further split at sentence/paragraph boundaries.
    """
    if not text:
        return []

    sections = _split_into_sections(text)
    raw_chunks: list[str] = []

    for section in sections:
        if len(section) <= chunk_size:
            raw_chunks.append(section)
        else:
            # Sub-split long sections at paragraph then sentence boundaries
            raw_chunks.extend(_subsplit(section, chunk_size, chunk_overlap))

    # Merge very small consecutive chunks to avoid degenerate fragments
    merged = _merge_small_chunks(raw_chunks, chunk_size)
    return merged


def _subsplit(text: str, size: int, overlap: int) -> list[str]:
    """Character-level sliding window with paragraph/sentence preference."""
    # Try paragraph split first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if all(len(p) <= size for p in paragraphs):
        return paragraphs

    # Fall back to sliding window
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        # Try to break at the last sentence-ending punctuation
        if end < len(text):
            last_period = max(chunk.rfind(". "), chunk.rfind(".\n"), chunk.rfind("\n\n"))
            if last_period > size // 3:
                end = start + last_period + 1
                chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap if end < len(text) else len(text)
    return [c for c in chunks if c]


def _merge_small_chunks(chunks: list[str], max_size: int) -> list[str]:
    """Merge consecutive chunks that are each below 30 % of *max_size*."""
    threshold = max_size * 0.3
    merged: list[str] = []
    buffer = ""
    for chunk in chunks:
        if len(chunk) < threshold and len(buffer) + len(chunk) + 1 <= max_size:
            buffer = (buffer + "\n\n" + chunk).strip() if buffer else chunk
        else:
            if buffer:
                merged.append(buffer)
                buffer = ""
            if len(chunk) < threshold:
                buffer = chunk
            else:
                merged.append(chunk)
    if buffer:
        merged.append(buffer)
    return merged


# ---------------------------------------------------------------------------
# Public API – chunk a document dict preserving metadata
# ---------------------------------------------------------------------------
def chunk_document(
    doc: DocChunk,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[DocChunk]:
    """Chunk a single document dict and propagate its metadata."""
    text = doc.get("text", "")
    metadata = dict(doc.get("metadata", {}))
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    result: list[DocChunk] = []
    for i, chunk in enumerate(chunks):
        chunk_meta = {**metadata, "chunk_index": i}
        result.append({"text": chunk, "metadata": chunk_meta})
    return result


def chunk_documents(
    docs: list[DocChunk],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[DocChunk]:
    """Chunk a list of document dicts."""
    all_chunks: list[DocChunk] = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, chunk_size, chunk_overlap))
    logger.info("Chunked %d documents into %d chunks", len(docs), len(all_chunks))
    return all_chunks
