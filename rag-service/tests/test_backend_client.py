"""Tests for the backend client and assistant with mocked backend responses.

Uses respx to mock httpx calls so no real backend is needed.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import httpx
import respx

from app.services import backend_client as bc
from app.models.schemas import ActionStatus, ActionType


# ===================================================================== #
#  Backend client unit tests (mocked HTTP)
# ===================================================================== #
@pytest.fixture(autouse=True)
def reset_client():
    """Ensure a fresh client for each test."""
    bc._client = None
    yield
    bc._client = None


class TestBackendClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_search_products_success(self):
        respx.get("http://localhost:8002/api/products/search").mock(
            return_value=httpx.Response(
                200,
                json=[{"product_id": "P001", "name": "Nike Air Max"}],
            )
        )
        products = await bc.search_products("Nike")
        assert len(products) == 1
        assert products[0]["product_id"] == "P001"

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_products_empty(self):
        respx.get("http://localhost:8002/api/products/search").mock(
            return_value=httpx.Response(200, json=[])
        )
        products = await bc.search_products("nonexistent")
        assert products == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_products_connection_error(self):
        respx.get("http://localhost:8002/api/products/search").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        products = await bc.search_products("Nike")
        assert products == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_inventory_success(self):
        respx.get("http://localhost:8002/api/inventory/P001").mock(
            return_value=httpx.Response(
                200,
                json={"product_id": "P001", "stock_quantity": 5},
            )
        )
        inv = await bc.get_inventory("P001")
        assert inv is not None
        assert inv["stock_quantity"] == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_order_success(self):
        respx.get("http://localhost:8002/api/orders/ORD001").mock(
            return_value=httpx.Response(
                200,
                json={
                    "order_id": "ORD001",
                    "product_id": "P001",
                    "status": "delivered",
                },
            )
        )
        order = await bc.get_order("ORD001")
        assert order is not None
        assert order["order_id"] == "ORD001"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_order_not_found(self):
        respx.get("http://localhost:8002/api/orders/ORD999").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )
        order = await bc.get_order("ORD999")
        assert order is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_return_eligible(self):
        respx.post("http://localhost:8002/api/returns/check").mock(
            return_value=httpx.Response(
                200,
                json={
                    "eligible": True,
                    "message": "Eligible for return",
                    "order_id": "ORD001",
                    "product_id": "P001",
                    "reasons": [],
                    "ticket_id": None,
                    "status": "ELIGIBLE",
                },
            )
        )
        result = await bc.check_return("ORD001", "P001")
        assert result is not None
        assert result["eligible"] is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_return_not_eligible(self):
        respx.post("http://localhost:8002/api/returns/check").mock(
            return_value=httpx.Response(
                200,
                json={
                    "eligible": False,
                    "message": "Return window expired",
                    "reasons": ["RETURN_WINDOW_EXPIRED"],
                    "status": "NOT_ELIGIBLE",
                },
            )
        )
        result = await bc.check_return("ORD003", "P001")
        assert result is not None
        assert result["eligible"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_initiate_return_success(self):
        respx.post("http://localhost:8002/api/returns/initiate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "RETURN_INITIATED",
                    "ticket_id": "RET-1001",
                    "order_id": "ORD001",
                    "product_id": "P001",
                },
            )
        )
        result = await bc.initiate_return("ORD001", "P001")
        assert result is not None
        assert result["ticket_id"] == "RET-1001"
        assert result["status"] == "RETURN_INITIATED"

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_exchange_eligible(self):
        respx.post("http://localhost:8002/api/exchanges/check").mock(
            return_value=httpx.Response(
                200,
                json={
                    "eligible": True,
                    "message": "Eligible for exchange",
                    "status": "ELIGIBLE",
                },
            )
        )
        result = await bc.check_exchange("ORD001", "P001", "P002")
        assert result is not None
        assert result["eligible"] is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_initiate_exchange_success(self):
        respx.post("http://localhost:8002/api/exchanges/initiate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "EXCHANGE_INITIATED",
                    "ticket_id": "EXC-1001",
                },
            )
        )
        result = await bc.initiate_exchange("ORD001", "P001", "P002")
        assert result is not None
        assert result["ticket_id"] == "EXC-1001"

    @pytest.mark.asyncio
    @respx.mock
    async def test_backend_health_ok(self):
        respx.get("http://localhost:8002/health").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        assert await bc.backend_health() is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_backend_health_down(self):
        respx.get("http://localhost:8002/health").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        assert await bc.backend_health() is False
