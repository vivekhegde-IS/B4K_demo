"""Tests for Pydantic schemas."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.schemas import (
    Action,
    ActionStatus,
    ActionType,
    Intent,
    ProductInfo,
    ProductLocation,
    QueryRequest,
    QueryResponse,
    Source,
    HealthResponse,
    ErrorResponse,
)


class TestQueryRequest:
    def test_valid_request(self):
        r = QueryRequest(query="Hello", user_id="u1", session_id="s1")
        assert r.query == "Hello"
        assert r.language == "en"

    def test_defaults(self):
        r = QueryRequest(query="test")
        assert r.user_id is None
        assert r.session_id is None
        assert r.language == "en"


class TestQueryResponse:
    def test_minimal_response(self):
        r = QueryResponse(intent="GENERAL_QUERY", answer="Hello!")
        assert r.intent == "GENERAL_QUERY"
        assert r.products == []
        assert r.sources == []
        assert r.action_required is False
        assert r.action is None
        assert r.missing_information == []

    def test_full_response(self):
        r = QueryResponse(
            intent="RETURN_REQUEST",
            answer="Return initiated",
            products=[
                ProductInfo(product_id="P001", name="Shoe")
            ],
            sources=[
                Source(source="policy.pdf", page=3, relevance=0.9)
            ],
            action_required=False,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.COMPLETED,
                ticket_id="RET-1001",
            ),
            confidence=0.95,
            session_id="s1",
        )
        assert r.action.ticket_id == "RET-1001"
        assert r.action.status == ActionStatus.COMPLETED
        assert r.products[0].product_id == "P001"


class TestAction:
    def test_action_is_object_not_string(self):
        """Action must be an object, not a string like 'RETURN_CREATED'."""
        a = Action(type=ActionType.RETURN, status=ActionStatus.COMPLETED, ticket_id="RET-001")
        assert isinstance(a, Action)
        assert a.type == ActionType.RETURN
        assert a.status == ActionStatus.COMPLETED

    def test_pending_with_required_info(self):
        a = Action(
            type=ActionType.RETURN,
            status=ActionStatus.PENDING,
            required_information=["order_id"],
        )
        assert a.required_information == ["order_id"]
        assert a.ticket_id is None


class TestProductInfo:
    def test_with_location(self):
        p = ProductInfo(
            product_id="P001",
            name="Nike Air Max",
            brand="Nike",
            price=4999,
            location=ProductLocation(store="Demo Store", aisle="B", shelf="4"),
        )
        assert p.location.aisle == "B"

    def test_without_optional_fields(self):
        p = ProductInfo(product_id="P002", name="Test")
        assert p.brand is None
        assert p.stock_quantity is None


class TestHealthResponse:
    def test_defaults(self):
        h = HealthResponse()
        assert h.status == "ok"
        assert h.service == "retailmate-rag"


class TestErrorResponse:
    def test_error(self):
        e = ErrorResponse(message="Something went wrong")
        assert e.error is True


class TestIntentEnum:
    def test_all_intents(self):
        expected = {
            "INVENTORY_QUERY",
            "PRODUCT_LOCATION",
            "POLICY_QUERY",
            "RETURN_REQUEST",
            "EXCHANGE_REQUEST",
            "GENERAL_QUERY",
        }
        actual = {i.value for i in Intent}
        assert actual == expected

    def test_no_unknown_intent(self):
        """UNKNOWN must NOT be an intent — fallback is GENERAL_QUERY."""
        values = {i.value for i in Intent}
        assert "UNKNOWN" not in values
