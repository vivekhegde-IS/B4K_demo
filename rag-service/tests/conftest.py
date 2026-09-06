"""Shared test fixtures."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


@pytest.fixture(scope="session", autouse=True)
def preload_embedding_model():
    """Pre-load the embedding model once before all tests.
    
    This prevents respx from intercepting HuggingFace HTTP requests
    during model loading inside mocked test contexts.
    """
    try:
        from app.rag.embeddings import _get_model
        _get_model()
    except Exception:
        pass  # Model may not be available in CI; tests that need it will skip
