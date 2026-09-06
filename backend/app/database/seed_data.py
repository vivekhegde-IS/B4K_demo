"""Seed data for the RetailMate backend.

Creates realistic demo data:
 - 15 products across 5 categories
 - Inventory across 3 Bengaluru stores (some with 0 stock)
 - 10 orders with deterministic demo scenarios
 - 1 pre-existing return ticket (for duplicate-return testing)

Demo scenarios:
  ORD001 → recent (5 days ago) → return eligible
  ORD002 → recent (3 days ago) → exchange eligible
  ORD003 → 45 days ago → return window EXPIRED
  ORD004 → recent (10 days ago) → product ALREADY RETURNED (RET-1001 exists)
  ORD005 → recent (7 days ago) → multi-item order
  ORD006 → recent (2 days ago) → eligible, different customer
  ORD007 → 60 days ago → expired
  ORD008 → recent (1 day ago) → eligible
  ORD009 → recent (15 days ago) → eligible, multiple items
  ORD010 → 35 days ago → barely expired
"""

from __future__ import annotations

import logging
from datetime import date, timedelta, datetime, timezone

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.ticket import SupportTicket

logger = logging.getLogger(__name__)

TODAY = date.today()


def seed(db: Session) -> None:
    """Populate the database with demo data. Idempotent — skips if data exists."""
    if db.query(Product).first():
        logger.info("Database already seeded — skipping.")
        return

    logger.info("Seeding database with demo data…")

    _seed_products(db)
    _seed_inventory(db)
    _seed_orders(db)
    _seed_tickets(db)

    db.commit()
    logger.info("Seed data committed successfully.")


# ------------------------------------------------------------------ #
# Products — 15 products across 5 categories
# ------------------------------------------------------------------ #
PRODUCTS_DATA = [
    # Shoes
    {"product_id": "P001", "name": "Nike Air Max 270", "category": "Shoes", "price": 4999, "description": "Black running shoes with Air Max cushioning for all-day comfort"},
    {"product_id": "P002", "name": "Adidas Ultraboost 22", "category": "Shoes", "price": 5999, "description": "White performance running shoes with Boost midsole"},
    {"product_id": "P003", "name": "Puma RS-X", "category": "Shoes", "price": 3499, "description": "Retro-style chunky sneakers in blue and white"},
    # Clothing
    {"product_id": "P004", "name": "Levi's 501 Original Jeans", "category": "Clothing", "price": 2499, "description": "Classic straight-fit blue denim jeans"},
    {"product_id": "P005", "name": "Nike Dri-FIT T-Shirt", "category": "Clothing", "price": 1299, "description": "Grey moisture-wicking performance t-shirt"},
    {"product_id": "P006", "name": "Allen Solly Formal Shirt", "category": "Clothing", "price": 1799, "description": "White slim-fit cotton formal shirt"},
    # Electronics
    {"product_id": "P007", "name": "Samsung Galaxy Buds FE", "category": "Electronics", "price": 6999, "description": "Wireless earbuds with active noise cancellation"},
    {"product_id": "P008", "name": "boAt Rockerz 450", "category": "Electronics", "price": 1499, "description": "Over-ear wireless headphones with 15-hour battery life"},
    {"product_id": "P009", "name": "Apple Watch SE", "category": "Electronics", "price": 29999, "description": "Smartwatch with GPS, heart rate monitor and fitness tracking"},
    # Accessories
    {"product_id": "P010", "name": "Fossil Leather Watch", "category": "Accessories", "price": 7999, "description": "Classic brown leather strap analog watch"},
    {"product_id": "P011", "name": "Ray-Ban Aviator Sunglasses", "category": "Accessories", "price": 5999, "description": "Gold frame aviator sunglasses with green lenses"},
    {"product_id": "P012", "name": "Wildcraft Backpack", "category": "Accessories", "price": 1999, "description": "45L hiking backpack with rain cover in navy blue"},
    # Home
    {"product_id": "P013", "name": "Philips LED Desk Lamp", "category": "Home", "price": 2499, "description": "Adjustable LED desk lamp with touch dimmer"},
    {"product_id": "P014", "name": "Prestige Electric Kettle", "category": "Home", "price": 1299, "description": "1.5L stainless steel electric kettle with auto shut-off"},
    # Non-returnable
    {"product_id": "P015", "name": "Amazon Gift Card ₹500", "category": "Gift Cards", "price": 500, "description": "₹500 denomination gift card"},
]


def _seed_products(db: Session) -> None:
    products = [Product(**p) for p in PRODUCTS_DATA]
    db.add_all(products)
    db.flush()


# ------------------------------------------------------------------ #
# Inventory — 3 stores, realistic aisles/shelves, some zero stock
# ------------------------------------------------------------------ #
STORES = [
    ("Bengaluru Central", "INV"),
    ("Bengaluru Mall", "INM"),
    ("Bengaluru Airport", "INA"),
]

# (product_id, store_index, aisle, shelf, qty)
INVENTORY_DATA = [
    # P001 — Nike Air Max (in stock at 2 stores)
    ("P001", 0, "B", "4", 5),
    ("P001", 1, "A", "2", 3),
    # P002 — Adidas Ultraboost (in stock)
    ("P002", 0, "B", "5", 4),
    ("P002", 2, "C", "1", 2),
    # P003 — Puma RS-X (in stock)
    ("P003", 0, "B", "6", 7),
    # P004 — Levi's Jeans (in stock)
    ("P004", 0, "D", "2", 10),
    ("P004", 1, "C", "3", 6),
    # P005 — Nike T-Shirt (in stock)
    ("P005", 0, "D", "4", 15),
    ("P005", 1, "C", "5", 8),
    ("P005", 2, "B", "2", 4),
    # P006 — Allen Solly Shirt (in stock)
    ("P006", 0, "D", "5", 12),
    # P007 — Samsung Buds (in stock)
    ("P007", 0, "E", "1", 8),
    ("P007", 1, "D", "1", 5),
    # P008 — boAt headphones (OUT OF STOCK at all stores)
    ("P008", 0, "E", "2", 0),
    ("P008", 1, "D", "2", 0),
    # P009 — Apple Watch (low stock)
    ("P009", 0, "E", "3", 2),
    # P010 — Fossil Watch (in stock)
    ("P010", 0, "F", "1", 6),
    # P011 — Ray-Ban (in stock)
    ("P011", 0, "F", "2", 4),
    ("P011", 2, "A", "1", 3),
    # P012 — Wildcraft Backpack (in stock)
    ("P012", 0, "G", "1", 9),
    # P013 — Desk Lamp (in stock)
    ("P013", 0, "H", "1", 7),
    # P014 — Kettle (OUT OF STOCK)
    ("P014", 0, "H", "2", 0),
    # P015 — Gift Card (in stock — but non-returnable)
    ("P015", 0, "A", "1", 50),
]


def _seed_inventory(db: Session) -> None:
    counter = 1
    for pid, store_idx, aisle, shelf, qty in INVENTORY_DATA:
        store_name, prefix = STORES[store_idx]
        inv = Inventory(
            inventory_id=f"{prefix}{counter:03d}",
            product_id=pid,
            store_location=store_name,
            aisle=aisle,
            shelf=shelf,
            stock_quantity=qty,
        )
        db.add(inv)
        counter += 1
    db.flush()


# ------------------------------------------------------------------ #
# Orders + OrderItems — 10 deterministic demo orders
# ------------------------------------------------------------------ #
def _seed_orders(db: Session) -> None:
    orders_data = [
        # ORD001 — recent, single item, return eligible
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "purchase_date": TODAY - timedelta(days=5),
            "items": [("P001", 1, 4999)],
        },
        # ORD002 — recent, exchange eligible
        {
            "order_id": "ORD002",
            "customer_id": "CUST001",
            "purchase_date": TODAY - timedelta(days=3),
            "items": [("P004", 1, 2499)],
        },
        # ORD003 — 45 days old → EXPIRED
        {
            "order_id": "ORD003",
            "customer_id": "CUST002",
            "purchase_date": TODAY - timedelta(days=45),
            "items": [("P007", 1, 6999)],
        },
        # ORD004 — recent, but product already returned (RET-1001 exists)
        {
            "order_id": "ORD004",
            "customer_id": "CUST002",
            "purchase_date": TODAY - timedelta(days=10),
            "items": [("P005", 2, 1299)],
        },
        # ORD005 — recent, multi-item order
        {
            "order_id": "ORD005",
            "customer_id": "CUST003",
            "purchase_date": TODAY - timedelta(days=7),
            "items": [("P001", 1, 4999), ("P004", 2, 2499), ("P010", 1, 7999)],
        },
        # ORD006 — very recent, eligible
        {
            "order_id": "ORD006",
            "customer_id": "CUST004",
            "purchase_date": TODAY - timedelta(days=2),
            "items": [("P002", 1, 5999)],
        },
        # ORD007 — 60 days old → EXPIRED
        {
            "order_id": "ORD007",
            "customer_id": "CUST004",
            "purchase_date": TODAY - timedelta(days=60),
            "items": [("P009", 1, 29999)],
        },
        # ORD008 — yesterday, eligible
        {
            "order_id": "ORD008",
            "customer_id": "CUST005",
            "purchase_date": TODAY - timedelta(days=1),
            "items": [("P006", 1, 1799), ("P012", 1, 1999)],
        },
        # ORD009 — 15 days, eligible, multiple items
        {
            "order_id": "ORD009",
            "customer_id": "CUST003",
            "purchase_date": TODAY - timedelta(days=15),
            "items": [("P003", 1, 3499), ("P008", 1, 1499), ("P013", 1, 2499)],
        },
        # ORD010 — 35 days → barely expired
        {
            "order_id": "ORD010",
            "customer_id": "CUST005",
            "purchase_date": TODAY - timedelta(days=35),
            "items": [("P011", 1, 5999)],
        },
        # ORD011 — Gift card order (non-returnable category)
        {
            "order_id": "ORD011",
            "customer_id": "CUST001",
            "purchase_date": TODAY - timedelta(days=5),
            "items": [("P015", 1, 500)],
        },
    ]

    for od in orders_data:
        order = Order(
            order_id=od["order_id"],
            customer_id=od["customer_id"],
            purchase_date=od["purchase_date"],
        )
        db.add(order)
        for pid, qty, price in od["items"]:
            item = OrderItem(
                order_id=od["order_id"],
                product_id=pid,
                quantity=qty,
                price=price,
            )
            db.add(item)

    db.flush()


# ------------------------------------------------------------------ #
# Pre-existing tickets — for duplicate-return testing
# ------------------------------------------------------------------ #
def _seed_tickets(db: Session) -> None:
    # ORD004 + P005 already returned
    ticket = SupportTicket(
        ticket_id="RET-1001",
        order_id="ORD004",
        product_id="P005",
        type="RETURN",
        status="COMPLETED",
        created_at=datetime.now(timezone.utc),
    )
    db.add(ticket)
    db.flush()
