"""Pydantic schemas for Return/Exchange endpoints."""

from pydantic import BaseModel


class ReturnCheckRequest(BaseModel):
    order_id: str
    product_id: str


class ExchangeCheckRequest(BaseModel):
    order_id: str
    product_id: str
    replacement_product_id: str


class ReturnCheckResponse(BaseModel):
    eligible: bool
    message: str
    order_id: str
    product_id: str
    reasons: list[str] = []
    ticket_id: str | None = None
    status: str


class ReturnInitiateRequest(BaseModel):
    order_id: str
    product_id: str


class ExchangeInitiateRequest(BaseModel):
    order_id: str
    product_id: str
    replacement_product_id: str


class ReturnInitiateResponse(BaseModel):
    eligible: bool
    message: str
    order_id: str
    product_id: str
    ticket_id: str | None = None
    status: str
    reasons: list[str] = []


class ExchangeCheckResponse(BaseModel):
    eligible: bool
    message: str
    order_id: str
    product_id: str
    replacement_product_id: str | None = None
    reasons: list[str] = []
    ticket_id: str | None = None
    status: str


class ExchangeInitiateResponse(BaseModel):
    eligible: bool
    message: str
    order_id: str
    product_id: str
    replacement_product_id: str | None = None
    ticket_id: str | None = None
    status: str
    reasons: list[str] = []


class ErrorResponse(BaseModel):
    error: bool = True
    message: str
