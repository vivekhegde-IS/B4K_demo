"""Product search routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductOut, ProductSearchResponse

router = APIRouter(prefix="/api/products", tags=["products"])


import re

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
    clean_q = q.strip()
    pattern = f"%{clean_q}%"
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

    if not results:
        # Smart token-based fuzzy matching for queries like "Nike shoes in size 9"
        STOP_WORDS = {"in", "size", "a", "an", "the", "for", "with", "do", "you", "have", "are", "is", "of", "to", "me", "show", "find", "get", "any", "some", "looking"}
        tokens = [w for w in re.findall(r'\w+', clean_q.lower()) if w not in STOP_WORDS and len(w) > 1 and not w.isdigit()]
        
        if tokens:
            filters = []
            for token in tokens:
                t_pattern = f"%{token}%"
                filters.append(Product.name.ilike(t_pattern))
                filters.append(Product.category.ilike(t_pattern))
                filters.append(Product.description.ilike(t_pattern))
            
            candidates = db.query(Product).filter(or_(*filters)).all()
            
            def score(prod):
                text = f"{prod.name} {prod.category} {prod.description}".lower()
                return sum(1 for t in tokens if t in text)
            
            candidates.sort(key=score, reverse=True)
            results = candidates

    products = [ProductOut.model_validate(p) for p in results]
    return ProductSearchResponse(products=products)
