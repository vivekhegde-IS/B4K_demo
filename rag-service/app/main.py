"""RetailMate RAG Service — FastAPI application.

Endpoints
---------
- ``GET  /health``              → service health check
- ``POST /api/assistant/query`` → main AI assistant endpoint
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, RAG_HOST, RAG_PORT
from app.models.schemas import (
    ErrorResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)
from app.services.assistant import handle_query
from app.services.backend_client import close_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RetailMate RAG Service",
    description="RAG-based AI assistant for retail queries, returns, and exchanges.",
    version="1.0.0",
)

# CORS — configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Pre-load heavy resources (embedding model, vector store) on startup."""
    logger.info("RetailMate RAG service starting up…")
    # Lazily initialised on first use, but we can trigger the load here
    # to avoid cold-start latency on the first request.
    try:
        from app.rag.embeddings import embed_query as _warm  # noqa: F401
        from app.rag.vector_store import get_collection

        collection = get_collection()
        logger.info("ChromaDB collection ready with %d documents.", collection.count())
        if collection.count() == 0:
            logger.warning(
                "The vector store is empty. Run `python -m app.rag.index` to populate it."
            )
    except Exception:
        logger.exception("Error during startup pre-loading (non-fatal)")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources."""
    await close_client()
    logger.info("RetailMate RAG service shut down.")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    return HealthResponse(status="ok", service="retailmate-rag")


# ---------------------------------------------------------------------------
# Main query endpoint
# ---------------------------------------------------------------------------
@app.post(
    "/api/assistant/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["assistant"],
)
async def assistant_query(request: QueryRequest):
    """Process a natural-language query and return a structured AI response."""
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        response = await handle_query(request)
        return response
    except Exception as exc:
        logger.exception("Error processing query: %s", request.query)
        raise HTTPException(
            status_code=500,
            detail="Unable to process your request. Please try again later.",
        ) from exc


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=RAG_HOST, port=RAG_PORT, reload=True)
