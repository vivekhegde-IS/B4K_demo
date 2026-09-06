"""Inventory service — read-only inventory lookups."""

from sqlalchemy.orm import Session
from app.models.inventory import Inventory


def get_inventory_for_product(db: Session, product_id: str) -> list[Inventory]:
    """Return all inventory records for a product."""
    return (
        db.query(Inventory)
        .filter(Inventory.product_id == product_id)
        .all()
    )


def get_total_stock(db: Session, product_id: str) -> int:
    """Return total stock across all stores for a product."""
    records = get_inventory_for_product(db, product_id)
    return sum(r.stock_quantity for r in records)


def is_product_available(db: Session, product_id: str) -> bool:
    """Check if a product has stock > 0 in any store."""
    return get_total_stock(db, product_id) > 0
