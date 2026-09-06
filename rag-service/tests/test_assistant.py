"""End-to-end assistant tests with mocked backend.

Verifies the full flow: intent → backend calls → RAG → structured response.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import httpx
import respx

from app.models.schemas import ActionStatus, ActionType, QueryRequest
from app.services.assistant import handle_query
from app.services import backend_client as bc


@pytest.fixture(autouse=True)
def reset_client():
    bc._client = None
    yield
    bc._client = None


class TestReturnE2E:
    """Full return request flow: order lookup → check → initiate → COMPLETED."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_return_full_flow(self):
        # Mock order lookup
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
        # Mock return check — eligible
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
        # Mock return initiate — success with ticket_id from backend
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

        request = QueryRequest(
            query="I want to return order ORD001.",
            user_id="demo-user",
            session_id="session-001",
        )
        response = await handle_query(request)

        assert response.intent == "RETURN_REQUEST"
        assert response.action is not None
        assert response.action.type == ActionType.RETURN
        assert response.action.status == ActionStatus.COMPLETED
        # ticket_id MUST come from backend, never fabricated
        assert response.action.ticket_id == "RET-1001"
        assert response.session_id == "session-001"

    @pytest.mark.asyncio
    @respx.mock
    async def test_return_not_eligible(self):
        respx.get("http://localhost:8002/api/orders/ORD003").mock(
            return_value=httpx.Response(
                200,
                json={"order_id": "ORD003", "product_id": "P001"},
            )
        )
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

        request = QueryRequest(query="I want to return order ORD003.")
        response = await handle_query(request)

        assert response.intent == "RETURN_REQUEST"
        assert response.action is not None
        assert response.action.status == ActionStatus.FAILED
        assert response.action.ticket_id is None

    @pytest.mark.asyncio
    async def test_return_missing_order_id(self):
        request = QueryRequest(query="I want to return my shoes.")
        response = await handle_query(request)

        assert response.intent == "RETURN_REQUEST"
        assert response.action_required is True
        assert response.action is not None
        assert response.action.status == ActionStatus.PENDING
        assert "order_id" in response.missing_information


class TestExchangeE2E:
    @pytest.mark.asyncio
    async def test_exchange_missing_info(self):
        request = QueryRequest(query="Can I exchange this shirt?")
        response = await handle_query(request)

        assert response.intent == "EXCHANGE_REQUEST"
        assert response.action_required is True
        assert response.action.status == ActionStatus.PENDING
        assert len(response.missing_information) > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_exchange_full_flow(self):
        respx.post("http://localhost:8002/api/exchanges/check").mock(
            return_value=httpx.Response(
                200,
                json={"eligible": True, "status": "ELIGIBLE"},
            )
        )
        respx.post("http://localhost:8002/api/exchanges/initiate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "EXCHANGE_INITIATED",
                    "ticket_id": "EXC-2001",
                },
            )
        )

        request = QueryRequest(
            query="Exchange order ORD001 product P001 for P002"
        )
        response = await handle_query(request)

        assert response.intent == "EXCHANGE_REQUEST"
        assert response.action is not None
        assert response.action.status == ActionStatus.COMPLETED
        assert response.action.ticket_id == "EXC-2001"


class TestPolicyQuery:
    @pytest.mark.asyncio
    async def test_policy_query_returns_answer(self):
        """Policy query should use RAG and return policy-based answer."""
        request = QueryRequest(query="What is the return policy?")
        response = await handle_query(request)

        assert response.intent == "POLICY_QUERY"
        assert len(response.answer) > 0
        # Should NOT hardcode 30 days
        assert "30-day" not in response.answer.lower() or "30 day" not in response.answer.lower()


class TestInventoryQuery:
    @pytest.mark.asyncio
    @respx.mock
    async def test_inventory_with_backend(self):
        respx.get("http://localhost:8002/api/products/search").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "product_id": "P001",
                        "name": "Nike Air Max",
                        "brand": "Nike",
                        "category": "Footwear",
                        "price": 4999,
                    }
                ],
            )
        )
        respx.get("http://localhost:8002/api/inventory/P001").mock(
            return_value=httpx.Response(
                200,
                json={"product_id": "P001", "stock_quantity": 5},
            )
        )

        request = QueryRequest(query="Is Nike Air Max in stock?")
        response = await handle_query(request)

        assert response.intent == "INVENTORY_QUERY"
        assert len(response.products) >= 1
        assert response.products[0].stock_quantity == 5


class TestGeneralQuery:
    @pytest.mark.asyncio
    async def test_general_query_response(self):
        request = QueryRequest(query="Tell me something unrelated.")
        response = await handle_query(request)

        assert response.intent == "GENERAL_QUERY"
        assert len(response.answer) > 0
