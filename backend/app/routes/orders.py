"""Order lookup routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.order import Order
from app.schemas.order_schema import OrderItemOut, OrderResponse

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={404: {"description": "Order not found"}},
    summary="Get order by ID",
    description="Returns the complete order including all order items with product names and prices.",
)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail={"error": True, "message": f"Order {order_id} not found."},
        )

    items = [
        OrderItemOut(
            product_id=item.product_id,
            product_name=item.product.name if item.product else "Unknown",
            quantity=item.quantity,
            price=item.price,
        )
        for item in order.items
    ]

    return OrderResponse(
        order_id=order.order_id,
        customer_id=order.customer_id,
        purchase_date=order.purchase_date,
        items=items,
    )
