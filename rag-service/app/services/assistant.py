"""RetailMate AI Assistant — the main orchestration layer.

Combines intent detection, RAG retrieval, and backend API calls
to produce structured ``QueryResponse`` objects.

Source-of-truth separation
--------------------------
- **Policy knowledge** → RAG / ChromaDB (from the policy PDF)
- **Transactional data** → Member 3 backend HTTP APIs
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from app.models.schemas import (
    Action,
    ActionStatus,
    ActionType,
    Intent,
    ProductInfo,
    ProductLocation,
    QueryRequest,
    QueryResponse,
    Source,
)
from app.rag.retriever import retrieve, RetrievalResult
from app.services import intent_detector as detector
from app.services import backend_client as backend

logger = logging.getLogger(__name__)


# ======================================================================== #
#                            PUBLIC ENTRY POINT                             #
# ======================================================================== #
async def handle_query(request: QueryRequest) -> QueryResponse:
    """Process a user query end-to-end and return a structured response."""
    query = request.query.strip()
    intent = detector.detect_intent(query)

    logger.info("Query: %r → intent=%s", query, intent.value)

    try:
        handler = _HANDLERS.get(intent, _handle_general)
        response = await handler(query, request, intent)
        response.session_id = request.session_id
        response.language = request.language or "en"
        return response
    except Exception:
        logger.exception("Unhandled error processing query")
        return QueryResponse(
            intent=intent.value,
            answer="I'm sorry, I encountered an error processing your request. Please try again.",
            confidence=0.0,
            session_id=request.session_id,
            language=request.language or "en",
        )


# ======================================================================== #
#                         INTENT-SPECIFIC HANDLERS                          #
# ======================================================================== #

# ---------------------------------------------------------------------- #
# POLICY_QUERY
# ---------------------------------------------------------------------- #
async def _handle_policy(
    query: str, request: QueryRequest, intent: Intent
) -> QueryResponse:
    """Answer policy questions using RAG retrieval only."""
    results = retrieve(query, document_type="policy")
    if not results:
        # Fall back to all document types
        results = retrieve(query)

    if not results:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I couldn't find specific policy information for your question. "
                "Please refer to the Order Cancellation and Return Policy document "
                "or contact customer support for assistance."
            ),
            confidence=0.3,
        )

    context = _build_context(results)
    answer = _generate_policy_answer(query, context, results)
    sources = _build_sources(results)

    return QueryResponse(
        intent=intent.value,
        answer=answer,
        sources=sources,
        confidence=_avg_relevance(results),
    )


def _generate_policy_answer(
    query: str, context: str, results: list[RetrievalResult]
) -> str:
    """Construct a policy answer from retrieved context.

    This is a context-passthrouth approach: we present the most relevant
    retrieved text as the answer, prefixed with a natural-language preamble.
    We do NOT invent policy rules.
    """
    q_lower = query.lower()
    preamble = "Based on the Order Cancellation and Return Policy:\n\n"

    # Select the most relevant chunk(s)
    best = results[0]
    answer_text = best.text.strip()

    # If the user is asking about a specific category, try to find it
    if any(
        w in q_lower
        for w in ["footwear", "shoe", "shoes", "sneaker", "sandal"]
    ):
        cat_chunk = _find_category_chunk(results, ["footwear", "lifestyle"])
        if cat_chunk:
            answer_text = cat_chunk.text.strip()

    elif any(w in q_lower for w in ["electronics", "mobile", "laptop", "phone", "tablet"]):
        cat_chunk = _find_category_chunk(results, ["electronics", "mobile", "laptop"])
        if cat_chunk:
            answer_text = cat_chunk.text.strip()

    elif any(w in q_lower for w in ["cancel", "cancellation"]):
        cat_chunk = _find_category_chunk(results, ["cancel", "cancellation"])
        if cat_chunk:
            answer_text = cat_chunk.text.strip()

    elif any(
        w in q_lower for w in ["condition", "pickup", "undamaged", "unused", "packaging"]
    ):
        cat_chunk = _find_category_chunk(
            results, ["pickup", "condition", "unused", "undamaged", "packaging"]
        )
        if cat_chunk:
            answer_text = cat_chunk.text.strip()

    elif any(w in q_lower for w in ["non-returnable", "cannot be returned", "not returnable"]):
        cat_chunk = _find_category_chunk(results, ["non-returnable", "non returnable", "no return"])
        if cat_chunk:
            answer_text = cat_chunk.text.strip()

    return preamble + answer_text


def _find_category_chunk(
    results: list[RetrievalResult], keywords: list[str]
) -> RetrievalResult | None:
    """Find the chunk whose text best matches the given keywords."""
    for r in results:
        text_lower = r.text.lower()
        if any(kw in text_lower for kw in keywords):
            return r
    return None


# ---------------------------------------------------------------------- #
# INVENTORY_QUERY
# ---------------------------------------------------------------------- #
async def _handle_inventory(
    query: str, request: QueryRequest, intent: Intent
) -> QueryResponse:
    """Check product availability via backend APIs."""
    search_term = detector.extract_product_query(query)
    products = await backend.search_products(search_term)

    if not products:
        # Try RAG for product info
        rag_results = retrieve(search_term, document_type="product")
        if rag_results:
            return QueryResponse(
                intent=intent.value,
                answer=(
                    f"I found product information for '{search_term}' in our catalog, "
                    "but I'm unable to verify live inventory at the moment. "
                    "The backend service may be unavailable."
                ),
                sources=_build_sources(rag_results),
                confidence=0.5,
            )
        return QueryResponse(
            intent=intent.value,
            answer=f"I couldn't find any products matching '{search_term}'. Please try a different search term.",
            confidence=0.4,
        )

    # Enrich with inventory data
    enriched_products: list[ProductInfo] = []
    answer_parts: list[str] = []

    for p in products[:5]:  # Limit to top 5
        pid = p.get("product_id", p.get("id", ""))
        inv = await backend.get_inventory(pid) if pid else None

        stock = None
        if inv:
            stock = inv.get("stock_quantity", inv.get("quantity", inv.get("stock")))

        location = None
        loc_data = p.get("location")
        if loc_data and isinstance(loc_data, dict):
            location = ProductLocation(**{k: v for k, v in loc_data.items() if k in ProductLocation.model_fields})

        product_info = ProductInfo(
            product_id=str(pid),
            name=p.get("name", "Unknown"),
            brand=p.get("brand"),
            category=p.get("category"),
            color=p.get("color"),
            size=str(p.get("size", "")) if p.get("size") else None,
            price=p.get("price"),
            image_url=p.get("image_url", ""),
            stock_quantity=stock,
            location=location,
            description=p.get("description"),
        )
        enriched_products.append(product_info)

        name = product_info.name
        if stock is not None:
            status = f"in stock ({stock} available)" if stock > 0 else "currently out of stock"
            answer_parts.append(f"• {name}: {status}")
        else:
            answer_parts.append(f"• {name}: found in catalog")

    answer = "Here's what I found:\n\n" + "\n".join(answer_parts)

    return QueryResponse(
        intent=intent.value,
        answer=answer,
        products=enriched_products,
        confidence=0.85,
    )


# ---------------------------------------------------------------------- #
# PRODUCT_LOCATION
# ---------------------------------------------------------------------- #
async def _handle_product_location(
    query: str, request: QueryRequest, intent: Intent
) -> QueryResponse:
    """Answer product-location questions using backend + RAG store info."""
    search_term = detector.extract_product_query(query)

    # Try backend product search first
    products = await backend.search_products(search_term)
    if products:
        product_infos: list[ProductInfo] = []
        answer_parts: list[str] = []
        for p in products[:5]:
            loc_data = p.get("location")
            location = None
            loc_str = "location information unavailable"
            if loc_data and isinstance(loc_data, dict):
                location = ProductLocation(**{k: v for k, v in loc_data.items() if k in ProductLocation.model_fields})
                parts = []
                if loc_data.get("store"):
                    parts.append(f"Store: {loc_data['store']}")
                if loc_data.get("aisle"):
                    parts.append(f"Aisle {loc_data['aisle']}")
                if loc_data.get("shelf"):
                    parts.append(f"Shelf {loc_data['shelf']}")
                loc_str = ", ".join(parts) if parts else "location information unavailable"

            pid = p.get("product_id", p.get("id", ""))
            product_infos.append(
                ProductInfo(
                    product_id=str(pid),
                    name=p.get("name", "Unknown"),
                    brand=p.get("brand"),
                    category=p.get("category"),
                    color=p.get("color"),
                    size=str(p.get("size", "")) if p.get("size") else None,
                    price=p.get("price"),
                    location=location,
                )
            )
            answer_parts.append(f"• {p.get('name', 'Unknown')}: {loc_str}")

        answer = "Here's where you can find the products:\n\n" + "\n".join(answer_parts)
        return QueryResponse(
            intent=intent.value,
            answer=answer,
            products=product_infos,
            confidence=0.85,
        )

    # Fall back to RAG (product catalog + store info)
    results = retrieve(search_term)
    if results:
        context_text = results[0].text
        return QueryResponse(
            intent=intent.value,
            answer=f"Based on our store information:\n\n{context_text}",
            sources=_build_sources(results),
            confidence=_avg_relevance(results),
        )

    return QueryResponse(
        intent=intent.value,
        answer=f"I couldn't find location information for '{search_term}'. Please ask a store associate for help.",
        confidence=0.3,
    )


# ---------------------------------------------------------------------- #
# RETURN_REQUEST
# ---------------------------------------------------------------------- #
async def _handle_return(
    query: str, request: QueryRequest, intent: Intent
) -> QueryResponse:
    """Orchestrate a return request via backend APIs."""
    order_id = detector.extract_order_id(query)
    product_id = detector.extract_product_id(query)

    # Missing information
    missing: list[str] = []
    if not order_id:
        missing.append("order_id")
    if not product_id:
        # We'll try to get it from the order
        pass

    if not order_id:
        return QueryResponse(
            intent=intent.value,
            answer="I'd be happy to help you with your return. Could you please provide your order ID (e.g. ORD001)?",
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.PENDING,
                required_information=["order_id"],
            ),
            missing_information=["order_id"],
            confidence=0.7,
        )

    # Fetch order details
    order = await backend.get_order(order_id)
    if not order:
        return QueryResponse(
            intent=intent.value,
            answer=f"I couldn't find order {order_id}. Please check the order ID and try again.",
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message=f"Order {order_id} not found",
            ),
            confidence=0.6,
        )

    # Extract product_id from order if not provided
    if not product_id:
        product_id = _extract_product_from_order(order)
        if not product_id:
            return QueryResponse(
                intent=intent.value,
                answer=(
                    f"I found order {order_id}. Which product would you like to return? "
                    "Please provide the product ID."
                ),
                action_required=True,
                action=Action(
                    type=ActionType.RETURN,
                    status=ActionStatus.PENDING,
                    required_information=["product_id"],
                ),
                missing_information=["product_id"],
                confidence=0.7,
            )

    # Get policy context for additional info
    policy_results = retrieve("return policy conditions", document_type="policy", top_k=2)
    policy_sources = _build_sources(policy_results) if policy_results else []

    # Check return eligibility
    check_result = await backend.check_return(order_id, product_id)
    if check_result is None:
        return QueryResponse(
            intent=intent.value,
            answer=(
                f"I'm unable to check return eligibility for order {order_id} right now. "
                "The backend service may be unavailable. Please try again later."
            ),
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message="Backend service unavailable",
            ),
            sources=policy_sources,
            confidence=0.4,
        )

    if not check_result.get("eligible", False):
        reasons = check_result.get("reasons", [])
        message = check_result.get("message", "This product is not eligible for return.")
        reasons_text = ""
        if reasons:
            reasons_text = "\n\nReasons: " + ", ".join(str(r) for r in reasons)

        return QueryResponse(
            intent=intent.value,
            answer=f"Return for order {order_id} (product {product_id}) is not eligible. {message}{reasons_text}",
            action_required=False,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message=message,
            ),
            sources=policy_sources,
            confidence=0.8,
        )

    # Eligible — initiate return
    initiate_result = await backend.initiate_return(order_id, product_id)
    if not initiate_result:
        return QueryResponse(
            intent=intent.value,
            answer=f"Your return for order {order_id} is eligible, but I was unable to initiate it. Please try again.",
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message="Return initiation failed",
            ),
            sources=policy_sources,
            confidence=0.6,
        )

    ticket_id = initiate_result.get("ticket_id")
    status = initiate_result.get("status", "")

    if status == "RETURN_INITIATED" or ticket_id:
        return QueryResponse(
            intent=intent.value,
            answer=(
                f"Your return for order {order_id} (product {product_id}) has been successfully initiated! "
                f"Your return ticket ID is: {ticket_id}. "
                "Please keep the product in its original condition and packaging for pickup."
            ),
            action_required=False,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.COMPLETED,
                ticket_id=ticket_id,
            ),
            sources=policy_sources,
            confidence=0.95,
        )

    # Unexpected backend response
    return QueryResponse(
        intent=intent.value,
        answer=f"Return request for order {order_id} has been submitted. Status: {status}",
        action_required=True,
        action=Action(
            type=ActionType.RETURN,
            status=ActionStatus.PENDING,
            message=str(initiate_result),
        ),
        sources=policy_sources,
        confidence=0.6,
    )


# ---------------------------------------------------------------------- #
# EXCHANGE_REQUEST
# ---------------------------------------------------------------------- #
async def _handle_exchange(
    query: str, request: QueryRequest, intent: Intent
) -> QueryResponse:
    """Orchestrate an exchange request via backend APIs."""
    order_id = detector.extract_order_id(query)
    product_id = detector.extract_product_id(query)

    # Try to extract replacement product ID (second P-ID in the query)
    all_pids = re.findall(r"\b(P\d{3,})\b", query, re.IGNORECASE)
    replacement_pid = None
    if len(all_pids) >= 2:
        product_id = all_pids[0].upper()
        replacement_pid = all_pids[1].upper()
    elif len(all_pids) == 1 and product_id:
        # Only one P-ID found, need replacement
        pass

    missing: list[str] = []
    if not order_id:
        missing.append("order_id")
    if not product_id:
        missing.append("product_id")
    if not replacement_pid:
        missing.append("replacement_product_id")

    if missing:
        info_needed = ", ".join(missing)
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I'd be happy to help you with an exchange. "
                f"I need the following information: {info_needed}. "
                "For example: 'Exchange order ORD001 product P001 for P002'."
            ),
            action_required=True,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.PENDING,
                required_information=missing,
            ),
            missing_information=missing,
            confidence=0.6,
        )

    # Check exchange eligibility
    check_result = await backend.check_exchange(order_id, product_id, replacement_pid)
    if check_result is None:
        return QueryResponse(
            intent=intent.value,
            answer="I'm unable to check exchange eligibility right now. The backend service may be unavailable.",
            action_required=True,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.FAILED,
                message="Backend service unavailable",
            ),
            confidence=0.4,
        )

    if not check_result.get("eligible", False):
        message = check_result.get("message", "This exchange is not eligible.")
        reasons = check_result.get("reasons", [])
        reasons_text = ""
        if reasons:
            reasons_text = "\n\nReasons: " + ", ".join(str(r) for r in reasons)

        return QueryResponse(
            intent=intent.value,
            answer=f"Exchange for order {order_id} is not eligible. {message}{reasons_text}",
            action_required=False,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.FAILED,
                message=message,
            ),
            confidence=0.8,
        )

    # Eligible — initiate exchange
    initiate_result = await backend.initiate_exchange(order_id, product_id, replacement_pid)
    if not initiate_result:
        return QueryResponse(
            intent=intent.value,
            answer=f"Exchange for order {order_id} is eligible, but I couldn't initiate it. Please try again.",
            action_required=True,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.FAILED,
                message="Exchange initiation failed",
            ),
            confidence=0.6,
        )

    ticket_id = initiate_result.get("ticket_id")
    status = initiate_result.get("status", "")

    if status == "EXCHANGE_INITIATED" or ticket_id:
        return QueryResponse(
            intent=intent.value,
            answer=(
                f"Your exchange for order {order_id} has been successfully initiated! "
                f"Product {product_id} will be exchanged for {replacement_pid}. "
                f"Your exchange ticket ID is: {ticket_id}."
            ),
            action_required=False,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.COMPLETED,
                ticket_id=ticket_id,
            ),
            confidence=0.95,
        )

    return QueryResponse(
        intent=intent.value,
        answer=f"Exchange request submitted for order {order_id}. Status: {status}",
        action_required=True,
        action=Action(
            type=ActionType.EXCHANGE,
            status=ActionStatus.PENDING,
            message=str(initiate_result),
        ),
        confidence=0.6,
    )


# ---------------------------------------------------------------------- #
# GENERAL_QUERY
# ---------------------------------------------------------------------- #
async def _handle_general(
    query: str, request: QueryRequest, intent: Intent
) -> QueryResponse:
    """Handle general queries via RAG retrieval."""
    results = retrieve(query)
    if results:
        answer = results[0].text.strip()
        return QueryResponse(
            intent=intent.value,
            answer=answer,
            sources=_build_sources(results),
            confidence=_avg_relevance(results),
        )

    return QueryResponse(
        intent=intent.value,
        answer=(
            "I'm RetailMate, your shopping assistant. I can help you with:\n\n"
            "• Product search and availability\n"
            "• Product locations in store\n"
            "• Return and exchange policies\n"
            "• Initiating returns or exchanges\n"
            "• General store information\n\n"
            "How can I assist you today?"
        ),
        confidence=0.5,
    )


# ======================================================================== #
#                              HANDLER MAP                                  #
# ======================================================================== #
_HANDLERS = {
    Intent.POLICY_QUERY: _handle_policy,
    Intent.INVENTORY_QUERY: _handle_inventory,
    Intent.PRODUCT_LOCATION: _handle_product_location,
    Intent.RETURN_REQUEST: _handle_return,
    Intent.EXCHANGE_REQUEST: _handle_exchange,
    Intent.GENERAL_QUERY: _handle_general,
}


# ======================================================================== #
#                              HELPERS                                      #
# ======================================================================== #
def _build_context(results: list[RetrievalResult]) -> str:
    return "\n\n---\n\n".join(r.text for r in results)


def _build_sources(results: list[RetrievalResult]) -> list[Source]:
    sources = []
    seen = set()
    for r in results:
        key = (r.metadata.get("source", ""), r.metadata.get("page"))
        if key in seen:
            continue
        seen.add(key)
        source_name = r.metadata.get("source", "unknown")
        title = "Order Cancellation and Return Policy" if "policy" in source_name.lower() else source_name
        page = r.metadata.get("page")
        sources.append(
            Source(
                title=title,
                source=source_name,
                page=int(page) if page and str(page).isdigit() else None,
                relevance=r.relevance,
            )
        )
    return sources


def _avg_relevance(results: list[RetrievalResult]) -> float:
    if not results:
        return 0.0
    return round(sum(r.relevance for r in results) / len(results), 4)


def _extract_product_from_order(order: dict) -> str | None:
    """Try to extract a product_id from an order response."""
    # Order may have: product_id, products, items, line_items
    if order.get("product_id"):
        return str(order["product_id"])
    for key in ("products", "items", "line_items", "order_items"):
        items = order.get(key)
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                return str(first.get("product_id", first.get("id", "")))
            return str(first)
    return None
