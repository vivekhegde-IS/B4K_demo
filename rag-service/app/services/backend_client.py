"""Async HTTP client for Member 3's backend API.

All backend communication is via HTTP — never direct DB access.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.config import BACKEND_URL, BACKEND_TIMEOUT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared client (reused across requests)
# ---------------------------------------------------------------------------
_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=BACKEND_URL,
            timeout=BACKEND_TIMEOUT,
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


# ---------------------------------------------------------------------------
# Product APIs
# ---------------------------------------------------------------------------
async def search_products(query: str) -> list[dict[str, Any]]:
    """GET /api/products/search?q=<query>"""
    try:
        client = get_client()
        resp = await client.get("/api/products/search", params={"q": query})
        resp.raise_for_status()
        data = resp.json()
        # Backend may return a list or {"products": [...]}
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "products" in data:
            return data["products"]
        return []
    except httpx.HTTPStatusError as exc:
        logger.warning("Backend product search failed (%s): %s", exc.response.status_code, exc)
        return []
    except httpx.RequestError as exc:
        logger.error("Backend connection error (product search): %s", exc)
        return []


async def get_inventory(product_id: str) -> dict[str, Any] | None:
    """GET /api/inventory/{product_id}"""
    try:
        client = get_client()
        resp = await client.get(f"/api/inventory/{product_id}")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("Backend inventory lookup failed (%s): %s", exc.response.status_code, exc)
        return None
    except httpx.RequestError as exc:
        logger.error("Backend connection error (inventory): %s", exc)
        return None


# ---------------------------------------------------------------------------
# Order APIs
# ---------------------------------------------------------------------------
async def get_order(order_id: str) -> dict[str, Any] | None:
    """GET /api/orders/{order_id}"""
    try:
        client = get_client()
        resp = await client.get(f"/api/orders/{order_id}")
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.info("Order not found: %s", order_id)
        else:
            logger.warning("Backend order lookup failed (%s): %s", exc.response.status_code, exc)
        return None
    except httpx.RequestError as exc:
        logger.error("Backend connection error (order): %s", exc)
        return None


# ---------------------------------------------------------------------------
# Return APIs
# ---------------------------------------------------------------------------
async def check_return(order_id: str, product_id: str) -> dict[str, Any] | None:
    """POST /api/returns/check"""
    try:
        client = get_client()
        resp = await client.post(
            "/api/returns/check",
            json={"order_id": order_id, "product_id": product_id},
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("Return check failed (%s): %s", exc.response.status_code, exc)
        return {"eligible": False, "message": f"Return check failed: {exc.response.status_code}"}
    except httpx.RequestError as exc:
        logger.error("Backend connection error (return check): %s", exc)
        return None


async def initiate_return(order_id: str, product_id: str) -> dict[str, Any] | None:
    """POST /api/returns/initiate"""
    try:
        client = get_client()
        resp = await client.post(
            "/api/returns/initiate",
            json={"order_id": order_id, "product_id": product_id},
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("Return initiation failed (%s): %s", exc.response.status_code, exc)
        return None
    except httpx.RequestError as exc:
        logger.error("Backend connection error (return initiate): %s", exc)
        return None


# ---------------------------------------------------------------------------
# Exchange APIs
# ---------------------------------------------------------------------------
async def check_exchange(
    order_id: str,
    product_id: str,
    replacement_product_id: str,
) -> dict[str, Any] | None:
    """POST /api/exchanges/check"""
    try:
        client = get_client()
        resp = await client.post(
            "/api/exchanges/check",
            json={
                "order_id": order_id,
                "product_id": product_id,
                "replacement_product_id": replacement_product_id,
            },
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("Exchange check failed (%s): %s", exc.response.status_code, exc)
        return {"eligible": False, "message": f"Exchange check failed: {exc.response.status_code}"}
    except httpx.RequestError as exc:
        logger.error("Backend connection error (exchange check): %s", exc)
        return None


async def initiate_exchange(
    order_id: str,
    product_id: str,
    replacement_product_id: str,
) -> dict[str, Any] | None:
    """POST /api/exchanges/initiate"""
    try:
        client = get_client()
        resp = await client.post(
            "/api/exchanges/initiate",
            json={
                "order_id": order_id,
                "product_id": product_id,
                "replacement_product_id": replacement_product_id,
            },
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("Exchange initiation failed (%s): %s", exc.response.status_code, exc)
        return None
    except httpx.RequestError as exc:
        logger.error("Backend connection error (exchange initiate): %s", exc)
        return None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
async def backend_health() -> bool:
    """Check backend health via GET /health."""
    try:
        client = get_client()
        resp = await client.get("/health")
        return resp.status_code == 200
    except Exception:
        return False
