"""Return and Exchange routes.

All initiation endpoints re-validate eligibility before creating tickets.
Ticket creation and inventory mutation happen in a single DB transaction.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.return_schema import (
    ReturnCheckRequest,
    ReturnCheckResponse,
    ReturnInitiateRequest,
    ReturnInitiateResponse,
    ExchangeCheckRequest,
    ExchangeCheckResponse,
    ExchangeInitiateRequest,
    ExchangeInitiateResponse,
)
from app.services.return_service import (
    check_eligibility,
    check_exchange_replacement,
    initiate_return,
    initiate_exchange,
)

router = APIRouter(tags=["returns & exchanges"])


# ------------------------------------------------------------------ #
# Returns
# ------------------------------------------------------------------ #
@router.post(
    "/api/returns/check",
    response_model=ReturnCheckResponse,
    summary="Check return eligibility",
    description=(
        "Validates whether a product from an order is eligible for return. "
        "Rules: order exists, product in order, within 30-day window, "
        "not already returned, category is returnable."
    ),
)
def return_check(req: ReturnCheckRequest, db: Session = Depends(get_db)):
    result = check_eligibility(db, req.order_id, req.product_id, "RETURN")
    return ReturnCheckResponse(
        eligible=result.eligible,
        message=result.message,
        order_id=req.order_id,
        product_id=req.product_id,
        reasons=result.reasons,
        ticket_id=None,
        status="ELIGIBLE" if result.eligible else "NOT_ELIGIBLE",
    )


@router.post(
    "/api/returns/initiate",
    response_model=ReturnInitiateResponse,
    summary="Initiate a return",
    description=(
        "Re-validates eligibility and atomically creates a return support ticket. "
        "The ticket_id is only returned after the DB transaction commits."
    ),
)
def return_initiate(req: ReturnInitiateRequest, db: Session = Depends(get_db)):
    eligible, message, ticket_id, reasons = initiate_return(
        db, req.order_id, req.product_id
    )
    if eligible:
        db.commit()
        return ReturnInitiateResponse(
            eligible=True,
            message=message,
            order_id=req.order_id,
            product_id=req.product_id,
            ticket_id=ticket_id,
            status="RETURN_INITIATED",
            reasons=[],
        )
    else:
        db.rollback()
        return ReturnInitiateResponse(
            eligible=False,
            message=message,
            order_id=req.order_id,
            product_id=req.product_id,
            ticket_id=None,
            status="NOT_ELIGIBLE",
            reasons=reasons,
        )


# ------------------------------------------------------------------ #
# Exchanges
# ------------------------------------------------------------------ #
@router.post(
    "/api/exchanges/check",
    response_model=ExchangeCheckResponse,
    summary="Check exchange eligibility",
    description=(
        "Validates exchange eligibility including replacement product availability. "
        "Same base rules as returns plus replacement stock check."
    ),
)
def exchange_check(req: ExchangeCheckRequest, db: Session = Depends(get_db)):
    # Base eligibility
    result = check_eligibility(db, req.order_id, req.product_id, "EXCHANGE")
    if not result.eligible:
        return ExchangeCheckResponse(
            eligible=False,
            message=result.message,
            order_id=req.order_id,
            product_id=req.product_id,
            replacement_product_id=req.replacement_product_id,
            reasons=result.reasons,
            ticket_id=None,
            status="NOT_ELIGIBLE",
        )

    # Replacement product check
    repl_result = check_exchange_replacement(db, req.replacement_product_id)
    if not repl_result.eligible:
        return ExchangeCheckResponse(
            eligible=False,
            message=repl_result.message,
            order_id=req.order_id,
            product_id=req.product_id,
            replacement_product_id=req.replacement_product_id,
            reasons=repl_result.reasons,
            ticket_id=None,
            status="NOT_ELIGIBLE",
        )

    return ExchangeCheckResponse(
        eligible=True,
        message="Your product is eligible for exchange.",
        order_id=req.order_id,
        product_id=req.product_id,
        replacement_product_id=req.replacement_product_id,
        reasons=[],
        ticket_id=None,
        status="ELIGIBLE",
    )


@router.post(
    "/api/exchanges/initiate",
    response_model=ExchangeInitiateResponse,
    summary="Initiate an exchange",
    description=(
        "Re-validates eligibility, creates an exchange ticket, and decrements "
        "replacement product inventory — all in a single database transaction."
    ),
)
def exchange_initiate(req: ExchangeInitiateRequest, db: Session = Depends(get_db)):
    eligible, message, ticket_id, reasons = initiate_exchange(
        db, req.order_id, req.product_id, req.replacement_product_id
    )
    if eligible:
        db.commit()
        return ExchangeInitiateResponse(
            eligible=True,
            message=message,
            order_id=req.order_id,
            product_id=req.product_id,
            replacement_product_id=req.replacement_product_id,
            ticket_id=ticket_id,
            status="EXCHANGE_INITIATED",
            reasons=[],
        )
    else:
        db.rollback()
        return ExchangeInitiateResponse(
            eligible=False,
            message=message,
            order_id=req.order_id,
            product_id=req.product_id,
            replacement_product_id=req.replacement_product_id,
            ticket_id=None,
            status="NOT_ELIGIBLE",
            reasons=reasons,
        )
