"""Comprehensive tests for RetailMate Backend (Member 3).

Tests all required functionality:
  1. Product search (by name, category, empty, case-insensitive)
  2. Inventory lookup (in-stock, out-of-stock, 404 for nonexistent)
  3. Order lookup (valid order with items, 404 for nonexistent)
  4. Return eligibility checks (eligible, expired, not in order, duplicate, non-returnable category, order not found)
  5. Return initiation (successful ticket creation, duplicate blocking, atomicity)
  6. Exchange eligibility checks (eligible, out of stock replacement, non-existent replacement)
  7. Exchange initiation (successful ticket creation, inventory decrement, duplicate blocking)
  8. Health endpoint
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app.database.seed_data import seed
from app.main import app


from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database with StaticPool for isolated test execution
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh in-memory tables and seed for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==================================================================== #
# Health Check Tests
# ==================================================================== #
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "retailmate-backend"


# ==================================================================== #
# Product Search Tests
# ==================================================================== #
def test_search_products_by_name(client):
    response = client.get("/api/products/search?q=Nike")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) >= 2
    names = [p["name"] for p in data["products"]]
    assert any("Nike Air Max" in name for name in names)


def test_search_products_by_category(client):
    response = client.get("/api/products/search?q=Shoes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) >= 3
    for p in data["products"]:
        assert p["category"] == "Shoes" or "Shoes" in p["description"]


def test_search_products_case_insensitive(client):
    response = client.get("/api/products/search?q=adidas")
    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) >= 1
    assert data["products"][0]["product_id"] == "P002"


def test_search_products_not_found(client):
    response = client.get("/api/products/search?q=NonExistentProduct12345")
    assert response.status_code == 200
    data = response.json()
    assert data["products"] == []


# ==================================================================== #
# Inventory Lookup Tests
# ==================================================================== #
def test_get_inventory_in_stock(client):
    response = client.get("/api/inventory/P001")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "P001"
    assert data["available"] is True
    assert len(data["inventory"]) >= 2
    total_stock = sum(inv["stock_quantity"] for inv in data["inventory"])
    assert total_stock > 0
    # verify location details
    assert "store_location" in data["inventory"][0]
    assert "aisle" in data["inventory"][0]
    assert "shelf" in data["inventory"][0]


def test_get_inventory_out_of_stock(client):
    response = client.get("/api/inventory/P008")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "P008"
    assert data["available"] is False
    total_stock = sum(inv["stock_quantity"] for inv in data["inventory"])
    assert total_stock == 0


def test_get_inventory_not_found(client):
    response = client.get("/api/inventory/P999")
    assert response.status_code == 404


# ==================================================================== #
# Order Lookup Tests
# ==================================================================== #
def test_get_order_valid(client):
    response = client.get("/api/orders/ORD001")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "ORD001"
    assert data["customer_id"] == "CUST001"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "P001"
    assert data["items"][0]["product_name"] == "Nike Air Max 270"
    assert data["items"][0]["quantity"] == 1
    assert data["items"][0]["price"] == 4999


def test_get_order_multi_item(client):
    response = client.get("/api/orders/ORD005")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "ORD005"
    assert len(data["items"]) == 3


def test_get_order_not_found(client):
    response = client.get("/api/orders/ORD999")
    assert response.status_code == 404


# ==================================================================== #
# Return Eligibility Checks
# ==================================================================== #
def test_return_check_eligible(client):
    response = client.post(
        "/api/returns/check",
        json={"order_id": "ORD001", "product_id": "P001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is True
    assert data["status"] == "ELIGIBLE"
    assert data["ticket_id"] is None
    assert data["reasons"] == []


def test_return_check_expired_window(client):
    response = client.post(
        "/api/returns/check",
        json={"order_id": "ORD003", "product_id": "P007"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "RETURN_WINDOW_EXPIRED" in data["reasons"]


def test_return_check_product_not_in_order(client):
    response = client.post(
        "/api/returns/check",
        json={"order_id": "ORD001", "product_id": "P002"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "PRODUCT_NOT_IN_ORDER" in data["reasons"]


def test_return_check_already_returned(client):
    # ORD004 has P005 and RET-1001 was pre-seeded
    response = client.post(
        "/api/returns/check",
        json={"order_id": "ORD004", "product_id": "P005"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "PRODUCT_ALREADY_RETURNED" in data["reasons"]


def test_return_check_non_returnable_category(client):
    response = client.post(
        "/api/returns/check",
        json={"order_id": "ORD011", "product_id": "P015"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "CATEGORY_NOT_RETURNABLE" in data["reasons"]


def test_return_check_order_not_found(client):
    response = client.post(
        "/api/returns/check",
        json={"order_id": "ORD999", "product_id": "P001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "ORDER_NOT_FOUND" in data["reasons"]


# ==================================================================== #
# Return Initiation Tests
# ==================================================================== #
def test_return_initiate_success(client):
    response = client.post(
        "/api/returns/initiate",
        json={"order_id": "ORD001", "product_id": "P001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is True
    assert data["status"] == "RETURN_INITIATED"
    assert data["ticket_id"] is not None
    assert data["ticket_id"].startswith("RET-")

    # Re-initiating the same return must fail (duplicate return prevention)
    response_dup = client.post(
        "/api/returns/initiate",
        json={"order_id": "ORD001", "product_id": "P001"},
    )
    assert response_dup.status_code == 200
    data_dup = response_dup.json()
    assert data_dup["eligible"] is False
    assert data_dup["ticket_id"] is None
    assert "PRODUCT_ALREADY_RETURNED" in data_dup["reasons"]


def test_return_initiate_ineligible(client):
    response = client.post(
        "/api/returns/initiate",
        json={"order_id": "ORD003", "product_id": "P007"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["ticket_id"] is None
    assert "RETURN_WINDOW_EXPIRED" in data["reasons"]


# ==================================================================== #
# Exchange Eligibility & Initiation Tests
# ==================================================================== #
def test_exchange_check_eligible(client):
    response = client.post(
        "/api/exchanges/check",
        json={
            "order_id": "ORD002",
            "product_id": "P004",
            "replacement_product_id": "P001",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is True
    assert data["status"] == "ELIGIBLE"
    assert data["ticket_id"] is None


def test_exchange_check_out_of_stock_replacement(client):
    response = client.post(
        "/api/exchanges/check",
        json={
            "order_id": "ORD002",
            "product_id": "P004",
            "replacement_product_id": "P008",  # P008 has 0 stock
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "REPLACEMENT_OUT_OF_STOCK" in data["reasons"]


def test_exchange_check_nonexistent_replacement(client):
    response = client.post(
        "/api/exchanges/check",
        json={
            "order_id": "ORD002",
            "product_id": "P004",
            "replacement_product_id": "P999",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is False
    assert data["status"] == "NOT_ELIGIBLE"
    assert "REPLACEMENT_NOT_FOUND" in data["reasons"]


def test_exchange_initiate_success_and_inventory_decrement(client):
    # Initial inventory for P001
    inv_before = client.get("/api/inventory/P001").json()
    total_before = sum(r["stock_quantity"] for r in inv_before["inventory"])

    # Initiate exchange
    response = client.post(
        "/api/exchanges/initiate",
        json={
            "order_id": "ORD002",
            "product_id": "P004",
            "replacement_product_id": "P001",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] is True
    assert data["status"] == "EXCHANGE_INITIATED"
    assert data["ticket_id"] is not None
    assert data["ticket_id"].startswith("EXC-")

    # Verify inventory was decremented by 1
    inv_after = client.get("/api/inventory/P001").json()
    total_after = sum(r["stock_quantity"] for r in inv_after["inventory"])
    assert total_after == total_before - 1

    # Duplicate exchange must fail
    response_dup = client.post(
        "/api/exchanges/initiate",
        json={
            "order_id": "ORD002",
            "product_id": "P004",
            "replacement_product_id": "P001",
        },
    )
    assert response_dup.status_code == 200
    data_dup = response_dup.json()
    assert data_dup["eligible"] is False
    assert data_dup["ticket_id"] is None
    assert "PRODUCT_ALREADY_EXCHANGED" in data_dup["reasons"]
