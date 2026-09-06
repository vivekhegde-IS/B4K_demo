"""Pydantic schemas for Inventory endpoints."""

from pydantic import BaseModel


class InventoryRecord(BaseModel):
    store_location: str
    aisle: str
    shelf: str
    stock_quantity: int

    model_config = {"from_attributes": True}


class InventoryResponse(BaseModel):
    product_id: str
    available: bool
    inventory: list[InventoryRecord]
