"""Tests for document loading and chunking."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.rag.loader import load_txt, load_product_catalog, load_pdf
from app.rag.chunker import chunk_text, chunk_document, chunk_documents


# ===================================================================== #
#  Loader tests
# ===================================================================== #
class TestTxtLoader:
    def test_load_nonempty_txt(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("Hello world\nLine two", encoding="utf-8")
        docs = load_txt(str(p), document_type="test")
        assert len(docs) == 1
        assert docs[0]["text"] == "Hello world\nLine two"
        assert docs[0]["metadata"]["source"] == "test.txt"
        assert docs[0]["metadata"]["document_type"] == "test"

    def test_load_empty_txt(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("", encoding="utf-8")
        docs = load_txt(str(p))
        assert len(docs) == 0


class TestProductCatalogLoader:
    def test_load_valid_catalog(self, tmp_path):
        catalog = [
            {
                "product_id": "P001",
                "name": "Test Shoe",
                "brand": "Nike",
                "category": "Footwear",
                "price": 4999,
            }
        ]
        p = tmp_path / "products.json"
        p.write_text(json.dumps(catalog), encoding="utf-8")
        docs = load_product_catalog(str(p))
        assert len(docs) == 1
        assert docs[0]["metadata"]["product_id"] == "P001"
        assert docs[0]["metadata"]["document_type"] == "product"
        assert "Nike" in docs[0]["text"]
        assert "4999" in docs[0]["text"]

    def test_load_empty_catalog(self, tmp_path):
        p = tmp_path / "empty.json"
        p.write_text("", encoding="utf-8")
        docs = load_product_catalog(str(p))
        assert len(docs) == 0


class TestPdfLoader:
    def test_load_actual_policy_pdf(self):
        """Test loading the actual policy PDF if present."""
        pdf_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "knowledge_base",
            "order_cancellation_return_policy.pdf",
        )
        if not os.path.isfile(pdf_path):
            import pytest
            pytest.skip("Policy PDF not found")

        docs = load_pdf(pdf_path, document_type="policy")
        assert len(docs) > 0
        # PDF has 13 pages
        assert len(docs) >= 10
        # Check metadata
        assert docs[0]["metadata"]["source"] == "order_cancellation_return_policy.pdf"
        assert docs[0]["metadata"]["document_type"] == "policy"
        assert docs[0]["metadata"]["page"] == 1


# ===================================================================== #
#  Chunker tests
# ===================================================================== #
class TestChunker:
    def test_chunk_short_text(self):
        chunks = chunk_text("Short text", chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_chunk_long_text(self):
        # Create text longer than chunk_size
        text = "This is a sentence. " * 100  # ~2000 chars
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
        assert len(chunks) > 1
        # Each chunk should be <= ~chunk_size (with some tolerance for boundary)
        for c in chunks:
            assert len(c) <= 600  # Allow some slack

    def test_chunk_preserves_metadata(self):
        doc = {
            "text": "Hello world. " * 100,
            "metadata": {"source": "test.pdf", "page": 3, "document_type": "policy"},
        }
        chunks = chunk_document(doc, chunk_size=200)
        assert len(chunks) > 1
        for c in chunks:
            assert c["metadata"]["source"] == "test.pdf"
            assert c["metadata"]["page"] == 3
            assert "chunk_index" in c["metadata"]

    def test_chunk_documents_batch(self):
        docs = [
            {"text": "Doc one content", "metadata": {"source": "a.txt"}},
            {"text": "Doc two content", "metadata": {"source": "b.txt"}},
        ]
        result = chunk_documents(docs, chunk_size=500)
        assert len(result) == 2
        assert result[0]["metadata"]["source"] == "a.txt"
        assert result[1]["metadata"]["source"] == "b.txt"

    def test_empty_text(self):
        assert chunk_text("") == []
