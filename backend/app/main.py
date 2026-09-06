"""RetailMate Backend — FastAPI application.

Transactional backend for the RetailMate retail assistant.
Manages products, inventory, orders, returns, exchanges, and support tickets.

Endpoints:
  GET  /health                    → service health check
  GET  /api/products/search?q=    → product search
  GET  /api/inventory/{id}        → inventory lookup
  GET  /api/orders/{id}           → order lookup
  POST /api/returns/check         → return eligibility check
  POST /api/returns/initiate      → initiate return (transactional)
  POST /api/exchanges/check       → exchange eligibility check
  POST /api/exchanges/initiate    → initiate exchange (transactional)
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine, SessionLocal
from app.database.seed_data import seed

# Import all models so Base.metadata is populated
from app.models.product import Product        # noqa: F401
from app.models.inventory import Inventory    # noqa: F401
from app.models.order import Order            # noqa: F401
from app.models.order_item import OrderItem   # noqa: F401
from app.models.ticket import SupportTicket   # noqa: F401

from app.routes.products import router as products_router
from app.routes.inventory import router as inventory_router
from app.routes.orders import router as orders_router
from app.routes.returns import router as returns_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

# ------------------------------------------------------------------ #
# Lifespan — create tables and seed data
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RetailMate Backend starting up…")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    # Seed demo data
    db = SessionLocal()
    try:
        seed(db)
    except Exception:
        db.rollback()
        logger.exception("Error seeding database")
    finally:
        db.close()

    logger.info("RetailMate Backend ready.")
    yield
    logger.info("RetailMate Backend shutting down…")


# ------------------------------------------------------------------ #
# App
# ------------------------------------------------------------------ #
app = FastAPI(
    title="RetailMate Backend",
    description=(
        "Transactional backend for the RetailMate retail assistant. "
        "Provides product search, inventory lookup, order management, "
        "and return/exchange processing with deterministic eligibility rules."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend and other services during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server (Member 1)
        "http://localhost:3000",    # Alternate frontend
        "http://localhost:8001",    # RAG service (Member 2)
        "http://localhost:8003",    # Agent service (Member 4)
        "*",                        # Allow all for hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
# Routes
# ------------------------------------------------------------------ #
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(returns_router)


# ------------------------------------------------------------------ #
# Health
# ------------------------------------------------------------------ #
@app.get("/health", tags=["health"], summary="Service health check")
def health():
    return {"status": "ok", "service": "retailmate-backend"}


# ------------------------------------------------------------------ #
# Run directly
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
