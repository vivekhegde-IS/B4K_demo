"""Product search routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductOut, ProductSearchResponse

router = APIRouter(prefix="/api/products", tags=["products"])


import re

PRODUCT_IMAGES = {
    "P001": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
    "P002": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80",
    "P003": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&auto=format&fit=crop&q=80",
    "P004": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
    "P005": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
    "P006": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
    "P007": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
    "P008": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
    "P009": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80",
    "P010": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
    "P011": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=80",
    "P012": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80",
    "P013": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80",
    "P014": "https://images.unsplash.com/photo-1585670149967-b4f4da88cc9f?w=600&auto=format&fit=crop&q=80",
}

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

    products = []
    for p in results:
        p_out = ProductOut.model_validate(p)
        p_out.image_url = PRODUCT_IMAGES.get(p.product_id, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80")
        products.append(p_out)

    return ProductSearchResponse(products=products)
