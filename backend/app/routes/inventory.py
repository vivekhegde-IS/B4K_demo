"""Inventory lookup routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product
from app.schemas.inventory_schema import InventoryRecord, InventoryResponse
from app.schemas.return_schema import ErrorResponse
from app.services.inventory_service import get_inventory_for_product

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get inventory for a product",
    description="Returns all inventory records across stores for the given product_id. "
    "Availability is true if any store has stock_quantity > 0.",
)
def get_inventory(product_id: str, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail={"error": True, "message": f"Product {product_id} not found."},
        )

    records = get_inventory_for_product(db, product_id)
    inventory_out = [InventoryRecord.model_validate(r) for r in records]
    available = any(r.stock_quantity > 0 for r in records)

    return InventoryResponse(
        product_id=product_id,
        available=available,
        inventory=inventory_out,
    )
