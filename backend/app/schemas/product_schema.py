"""Pydantic schemas for Product endpoints."""

from pydantic import BaseModel


class ProductOut(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    description: str | None = None

    model_config = {"from_attributes": True}


class ProductSearchResponse(BaseModel):
    products: list[ProductOut]
