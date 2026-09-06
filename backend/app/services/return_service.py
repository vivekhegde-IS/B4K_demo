"""Return and Exchange service — eligibility validation and transaction initiation.

All eligibility rules are deterministic and documented:
  1. Order must exist.
  2. Product must belong to the order (in OrderItems).
  3. Within 30-day return/exchange window.
  4. No duplicate return/exchange for the same order+product.
  5. Product category must be returnable.
  6. (Exchange only) Replacement product must have stock > 0.

Non-returnable categories (explicit):
  - Gift Cards
  - Innerwear
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import NamedTuple

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.inventory import Inventory
from app.models.ticket import SupportTicket
from app.models.product import Product

# ------------------------------------------------------------------ #
# Configuration
# ------------------------------------------------------------------ #
RETURN_WINDOW_DAYS = 30

NON_RETURNABLE_CATEGORIES: set[str] = {
    "Gift Cards",
    "Innerwear",
}


# ------------------------------------------------------------------ #
# Result container
# ------------------------------------------------------------------ #
class EligibilityResult(NamedTuple):
    eligible: bool
    message: str
    reasons: list[str]


# ------------------------------------------------------------------ #
# Core eligibility checker (shared by check and initiate)
# ------------------------------------------------------------------ #
def check_eligibility(
    db: Session,
    order_id: str,
    product_id: str,
    ticket_type: str = "RETURN",
) -> EligibilityResult:
    """Run all deterministic eligibility rules.

    ``ticket_type`` should be ``"RETURN"`` or ``"EXCHANGE"``.
    """
    # Rule 1 — Order exists
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        return EligibilityResult(
            eligible=False,
            message=f"Order {order_id} not found.",
            reasons=["ORDER_NOT_FOUND"],
        )

    # Rule 2 — Product belongs to order
    order_item = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id, OrderItem.product_id == product_id)
        .first()
    )
    if not order_item:
        return EligibilityResult(
            eligible=False,
            message=f"Product {product_id} is not part of order {order_id}.",
            reasons=["PRODUCT_NOT_IN_ORDER"],
        )

    # Rule 3 — 30-day window
    today = date.today()
    purchase = order.purchase_date
    if (today - purchase) > timedelta(days=RETURN_WINDOW_DAYS):
        return EligibilityResult(
            eligible=False,
            message=f"This order is outside the {RETURN_WINDOW_DAYS}-day {ticket_type.lower()} window.",
            reasons=["RETURN_WINDOW_EXPIRED"],
        )

    # Rule 4 — No duplicate ticket for this order+product
    existing = (
        db.query(SupportTicket)
        .filter(
            SupportTicket.order_id == order_id,
            SupportTicket.product_id == product_id,
            SupportTicket.type == ticket_type,
            SupportTicket.status.in_(["COMPLETED", "CREATED"]),
        )
        .first()
    )
    if existing:
        action = "returned" if ticket_type == "RETURN" else "exchanged"
        reason = (
            "PRODUCT_ALREADY_RETURNED"
            if ticket_type == "RETURN"
            else "PRODUCT_ALREADY_EXCHANGED"
        )
        return EligibilityResult(
            eligible=False,
            message=f"This product has already been {action}.",
            reasons=[reason],
        )

    # Rule 5 — Category eligibility
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product and product.category in NON_RETURNABLE_CATEGORIES:
        return EligibilityResult(
            eligible=False,
            message=f"Products in the '{product.category}' category are not eligible for {ticket_type.lower()}.",
            reasons=["CATEGORY_NOT_RETURNABLE"],
        )

    return EligibilityResult(
        eligible=True,
        message=f"Your product is eligible for {ticket_type.lower()}.",
        reasons=[],
    )


def check_exchange_replacement(
    db: Session,
    replacement_product_id: str,
) -> EligibilityResult:
    """Additional checks specific to exchanges: replacement product exists and is in stock."""
    product = (
        db.query(Product)
        .filter(Product.product_id == replacement_product_id)
        .first()
    )
    if not product:
        return EligibilityResult(
            eligible=False,
            message=f"Replacement product {replacement_product_id} not found.",
            reasons=["REPLACEMENT_NOT_FOUND"],
        )

    # Check total stock across all stores
    total_stock = (
        db.query(Inventory)
        .filter(Inventory.product_id == replacement_product_id)
        .all()
    )
    total_qty = sum(r.stock_quantity for r in total_stock)

    if total_qty <= 0:
        return EligibilityResult(
            eligible=False,
            message=f"Replacement product {replacement_product_id} is out of stock.",
            reasons=["REPLACEMENT_OUT_OF_STOCK"],
        )

    return EligibilityResult(
        eligible=True,
        message="Replacement product is available.",
        reasons=[],
    )


# ------------------------------------------------------------------ #
# Ticket ID generation
# ------------------------------------------------------------------ #
def _next_ticket_id(db: Session, prefix: str) -> str:
    """Generate the next human-friendly ticket ID (e.g. RET-1001, EXC-1001)."""
    last = (
        db.query(SupportTicket)
        .filter(SupportTicket.ticket_id.startswith(prefix))
        .order_by(SupportTicket.ticket_id.desc())
        .first()
    )
    if last:
        num = int(last.ticket_id.split("-")[1]) + 1
    else:
        num = 1001
    return f"{prefix}-{num}"


# ------------------------------------------------------------------ #
# Initiation (transactional)
# ------------------------------------------------------------------ #
def initiate_return(
    db: Session,
    order_id: str,
    product_id: str,
) -> tuple[bool, str, str | None, list[str]]:
    """Validate and create a return ticket atomically.

    Returns ``(eligible, message, ticket_id, reasons)``.
    """
    result = check_eligibility(db, order_id, product_id, "RETURN")
    if not result.eligible:
        return False, result.message, None, result.reasons

    # Create ticket inside the caller's transaction
    ticket_id = _next_ticket_id(db, "RET")
    ticket = SupportTicket(
        ticket_id=ticket_id,
        order_id=order_id,
        product_id=product_id,
        type="RETURN",
        status="COMPLETED",
    )
    db.add(ticket)
    db.flush()  # ensure ID conflict detection before commit

    return True, "Your return has been initiated successfully.", ticket_id, []


def initiate_exchange(
    db: Session,
    order_id: str,
    product_id: str,
    replacement_product_id: str,
) -> tuple[bool, str, str | None, list[str]]:
    """Validate and create an exchange ticket atomically.

    Also decrements replacement product inventory.

    Returns ``(eligible, message, ticket_id, reasons)``.
    """
    # Base eligibility
    result = check_eligibility(db, order_id, product_id, "EXCHANGE")
    if not result.eligible:
        return False, result.message, None, result.reasons

    # Replacement product checks
    repl_result = check_exchange_replacement(db, replacement_product_id)
    if not repl_result.eligible:
        return False, repl_result.message, None, repl_result.reasons

    # Create ticket
    ticket_id = _next_ticket_id(db, "EXC")
    ticket = SupportTicket(
        ticket_id=ticket_id,
        order_id=order_id,
        product_id=product_id,
        replacement_product_id=replacement_product_id,
        type="EXCHANGE",
        status="COMPLETED",
    )
    db.add(ticket)

    # Decrement replacement inventory (first store with stock > 0)
    inv_record = (
        db.query(Inventory)
        .filter(
            Inventory.product_id == replacement_product_id,
            Inventory.stock_quantity > 0,
        )
        .first()
    )
    if inv_record:
        inv_record.stock_quantity -= 1

    db.flush()

    return True, "Your exchange has been initiated successfully.", ticket_id, []
