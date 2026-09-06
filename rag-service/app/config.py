"""Centralized configuration for the RetailMate RAG service.

All environment variables are loaded once and exposed as module-level constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
RAG_HOST: str = os.getenv("RAG_HOST", "0.0.0.0")
RAG_PORT: int = int(os.getenv("RAG_PORT", "8001"))

# ---------------------------------------------------------------------------
# Backend integration (Member 3)
# ---------------------------------------------------------------------------
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8002")
BACKEND_TIMEOUT: float = float(os.getenv("BACKEND_TIMEOUT", "10.0"))

# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------
CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")
CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "retailmate")

# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
TOP_K: int = int(os.getenv("TOP_K", "5"))
RELEVANCE_THRESHOLD: float = float(os.getenv("RELEVANCE_THRESHOLD", "1.5"))

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "75"))

# ---------------------------------------------------------------------------
# Knowledge base paths
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE_DIR: str = os.getenv(
    "KNOWLEDGE_BASE_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base"),
)
PRODUCT_CATALOG_PATH: str = os.getenv(
    "PRODUCT_CATALOG_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "shared",
        "sample_data",
        "products.json",
    ),
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080,*"
).split(",")
