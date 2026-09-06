"""Product search routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductOut, ProductSearchResponse

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get(
    "/search",
    response_model=ProductSearchResponse,
    summary="Search products",
    description="Search products by name, category or description. Case-insensitive partial match.",
)
def search_products(
    q: str = Query(..., description="Search query string"),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"
    results = (
        db.query(Product)
        .filter(
            or_(
                Product.name.ilike(pattern),
                Product.category.ilike(pattern),
                Product.description.ilike(pattern),
            )
        )
        .all()
    )
    products = [ProductOut.model_validate(p) for p in results]
    return ProductSearchResponse(products=products)
