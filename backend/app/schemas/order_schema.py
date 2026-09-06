"""Pydantic schemas for Order endpoints."""

from pydantic import BaseModel
from datetime import date


class OrderItemOut(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    purchase_date: date
    items: list[OrderItemOut]
