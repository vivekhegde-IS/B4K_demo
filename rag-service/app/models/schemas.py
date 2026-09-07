"""Pydantic models for the RetailMate RAG service API."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class Intent(str, Enum):
    INVENTORY_QUERY = "INVENTORY_QUERY"
    PRODUCT_LOCATION = "PRODUCT_LOCATION"
    POLICY_QUERY = "POLICY_QUERY"
    RETURN_REQUEST = "RETURN_REQUEST"
    EXCHANGE_REQUEST = "EXCHANGE_REQUEST"
    GENERAL_QUERY = "GENERAL_QUERY"


class ActionType(str, Enum):
    RETURN = "RETURN"
    EXCHANGE = "EXCHANGE"


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------
class ProductLocation(BaseModel):
    store: Optional[str] = None
    aisle: Optional[str] = None
    shelf: Optional[str] = None


class ProductInfo(BaseModel):
    product_id: str
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = ""
    stock_quantity: Optional[int] = None
    location: Optional[ProductLocation] = None
    description: Optional[str] = None


class Source(BaseModel):
    title: Optional[str] = None
    source: str
    page: Optional[int] = None
    relevance: Optional[float] = None


class Action(BaseModel):
    type: ActionType
    status: ActionStatus
    ticket_id: Optional[str] = None
    required_information: Optional[list[str]] = None
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# Request / Response
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's natural-language query")
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    language: Optional[str] = "en"


class QueryResponse(BaseModel):
    intent: str
    answer: str
    products: list[ProductInfo] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    action_required: bool = False
    action: Optional[Action] = None
    confidence: float = 0.0
    missing_information: list[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    language: Optional[str] = "en"
    timing: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: bool = True
    message: str


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "retailmate-rag"
