"""RetailMate AI Assistant — the main orchestration layer.

Combines intent detection, RAG retrieval, and backend API calls
to produce structured QueryResponse objects.

Source-of-truth separation
--------------------------
- Policy knowledge → RAG / ChromaDB
- Transactional data → Member 3 backend HTTP APIs
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
from app.services.language import (
    localize_inventory_answer,
    localize_location_answer,
    normalize_language,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------- #
# MAIN QUERY HANDLER
# ---------------------------------------------------------------------- #

async def handle_query(request: QueryRequest) -> QueryResponse:
    """Main entry point for processing an assistant query."""

    query = request.query.strip()
    request.language = normalize_language(request.language)

    if not query:
        return QueryResponse(
            intent=Intent.GENERAL_QUERY.value,
            answer="Please provide a question or request.",
            confidence=0.0,
            session_id=request.session_id,
            language=request.language or "en",
        )

    intent = detector.detect_intent(query)

    if intent == Intent.POLICY_QUERY:
        return await _handle_policy(query, request, intent)

    if intent == Intent.INVENTORY_QUERY:
        return await _handle_inventory(query, request, intent)

    if intent == Intent.PRODUCT_LOCATION:
        return await _handle_product_location(query, request, intent)

    if intent == Intent.RETURN_REQUEST:
        return await _handle_return(query, request, intent)

    if intent == Intent.EXCHANGE_REQUEST:
        return await _handle_exchange(query, request, intent)

    return await _handle_general(query, request, intent)


# ---------------------------------------------------------------------- #
# COMMON HELPERS
# ---------------------------------------------------------------------- #

def _build_sources(results: list[RetrievalResult]) -> list[Source]:
    """Convert RAG retrieval results into API response sources."""

    sources: list[Source] = []

    for result in results:
        metadata = result.metadata or {}

        source_name = (
            metadata.get("source")
            or metadata.get("file")
            or metadata.get("filename")
            or "knowledge_base"
        )

        title = (
            metadata.get("title")
            or metadata.get("document")
            or source_name
        )

        page = metadata.get("page")

        try:
            page_value = int(page) if page is not None else None
        except (TypeError, ValueError):
            page_value = None

        relevance = getattr(result, "relevance", None)

        if relevance is None:
            relevance = getattr(result, "score", None)

        try:
            relevance_value = (
                float(relevance)
                if relevance is not None
                else None
            )
        except (TypeError, ValueError):
            relevance_value = None

        sources.append(
            Source(
                title=str(title) if title else None,
                source=str(source_name),
                page=page_value,
                relevance=relevance_value,
            )
        )

    return sources


def _find_category_chunk(
    results: list[RetrievalResult],
    keywords: list[str],
) -> RetrievalResult | None:
    """Find the first retrieval result matching one of the keywords."""

    for result in results:
        text_lower = result.text.lower()

        if any(keyword.lower() in text_lower for keyword in keywords):
            return result

    return None


def _extract_order_id(query: str) -> Optional[str]:
    """Extract an order ID such as ORD001 from a natural-language query."""

    patterns = [
        r"\border\s*(?:id|number)?\s*[:#-]?\s*(ORD\d+)\b",
        r"\b(ORD\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            query,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

    return None


def _extract_product_id(query: str) -> Optional[str]:
    """Extract a product ID such as P005 from a query."""

    patterns = [
        r"\bproduct\s*(?:id|number)?\s*[:#-]?\s*(P\d+)\b",
        r"\b(P\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            query,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

    return None


def _extract_replacement_product_id(query: str) -> Optional[str]:
    """Extract replacement product ID for exchange requests."""

    patterns = [
        r"\breplacement\s+(?:product\s*)?(?:id|number)?\s*[:#-]?\s*(P\d+)\b",
        r"\breplace(?:ment)?\s+(?:with|by)\s+(P\d+)\b",
        r"\bexchange\s+(?:for|with)\s+(P\d+)\b",
        r"\bfor\s+(P\d+)\b",
        r"\bto\s+(P\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            query,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

    return None


# ---------------------------------------------------------------------- #
# PRODUCT SEARCH VARIANTS
# ---------------------------------------------------------------------- #

def _product_search_variants(search_term: str) -> list[str]:
    """Generate conservative singular/plural product-name variants.

    The original search term is always attempted first.

    Examples:
        Nike Dri-FIT T-Shirts -> Nike Dri-FIT T-Shirt
        Nike Shoes            -> Nike Shoe
        Wireless Headphones   -> Wireless Headphone
        Water Bottles         -> Water Bottle
    """

    term = search_term.strip()

    if not term:
        return []

    variants: list[str] = []

    replacements = [
        (r"\bt-shirts\b", "T-Shirt"),
        (r"\btshirt(s)?\b", "T-Shirt"),
        (r"\bshirts\b", "Shirt"),
        (r"\bshoes\b", "Shoe"),
        (r"\bheadphones\b", "Headphone"),
        (r"\bbottles\b", "Bottle"),
        (r"\bjackets\b", "Jacket"),
        (r"\bwatches\b", "Watch"),
    ]

    for pattern, replacement in replacements:
        variant = re.sub(
            pattern,
            replacement,
            term,
            flags=re.IGNORECASE,
        )

        if variant.lower() != term.lower():
            variants.append(variant)

    # Conservative generic singularization of the final word.
    words = term.split()

    if words:
        last_word = words[-1]

        lower_word = last_word.lower()

        if (
            len(last_word) > 3
            and lower_word.endswith("s")
            and not lower_word.endswith(("ss", "us", "is"))
        ):
            generic_words = words.copy()
            generic_words[-1] = last_word[:-1]

            generic_variant = " ".join(generic_words)

            if generic_variant.lower() != term.lower():
                variants.append(generic_variant)

    # Remove duplicates.
    result: list[str] = []
    seen: set[str] = set()

    for variant in variants:
        variant = variant.strip()

        if not variant:
            continue

        key = variant.lower()

        if key not in seen:
            seen.add(key)
            result.append(variant)

    return result


async def _search_products_with_variants(
    search_term: str,
) -> tuple[str, list[dict[str, Any]]]:
    """Search the backend using the original term and natural-language variants."""

    products = await backend.search_products(search_term)

    if products:
        return search_term, products

    variants = _product_search_variants(search_term)

    for variant in variants:
        logger.info(
            "No backend product match for '%s'; trying '%s'",
            search_term,
            variant,
        )

        products = await backend.search_products(variant)

        if products:
            return variant, products

    return search_term, []


# ---------------------------------------------------------------------- #
# POLICY_QUERY
# ---------------------------------------------------------------------- #

async def _handle_policy(
    query: str,
    request: QueryRequest,
    intent: Intent,
) -> QueryResponse:
    """Answer policy questions using RAG."""

    results = retrieve(
        query,
        document_type="policy",
    )

    if not results:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I couldn't find relevant information in the store policy."
            ),
            confidence=0.2,
            session_id=request.session_id,
            language=request.language or "en",
        )

    answer_text = results[0].text.strip()

    q_lower = query.lower()

    # Prefer more relevant policy chunks for common policy topics.
    if any(
        word in q_lower
        for word in [
            "return",
            "refund",
            "money back",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "return",
                "refund",
                "eligible",
                "days",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    elif any(
        word in q_lower
        for word in [
            "exchange",
            "replacement",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "exchange",
                "replacement",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    elif any(
        word in q_lower
        for word in [
            "footwear",
            "shoe",
            "shoes",
            "sneaker",
            "sandal",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "footwear",
                "lifestyle",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    elif any(
        word in q_lower
        for word in [
            "electronics",
            "mobile",
            "laptop",
            "phone",
            "tablet",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "electronics",
                "mobile",
                "laptop",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    elif any(
        word in q_lower
        for word in [
            "cancel",
            "cancellation",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "cancel",
                "cancellation",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    elif any(
        word in q_lower
        for word in [
            "condition",
            "pickup",
            "undamaged",
            "unused",
            "packaging",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "pickup",
                "condition",
                "unused",
                "undamaged",
                "packaging",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    elif any(
        word in q_lower
        for word in [
            "non-returnable",
            "cannot be returned",
            "not returnable",
        ]
    ):
        chunk = _find_category_chunk(
            results,
            [
                "non-returnable",
                "non returnable",
                "no return",
            ],
        )

        if chunk:
            answer_text = chunk.text.strip()

    return QueryResponse(
        intent=intent.value,
        answer=answer_text,
        sources=_build_sources(results),
        confidence=0.9,
        session_id=request.session_id,
        language=request.language or "en",
    )


# ---------------------------------------------------------------------- #
# INVENTORY_QUERY
# ---------------------------------------------------------------------- #

async def _handle_inventory(
    query: str,
    request: QueryRequest,
    intent: Intent,
) -> QueryResponse:
    """Check product availability via backend APIs."""

    search_term = detector.extract_product_query(query)

    # Original search first, followed by singular/plural variants.
    search_term, products = await _search_products_with_variants(
        search_term
    )

    if not products:
        # Backend did not return a product.
        # Try RAG for product information as a fallback.
        rag_results = retrieve(
            search_term,
            document_type="product",
        )

        if rag_results:
            return QueryResponse(
                intent=intent.value,
                answer=(
                    f"I found product information for '{search_term}' "
                    "in our catalog, but I'm unable to verify live "
                    "inventory at the moment. The backend service "
                    "may be unavailable."
                ),
                sources=_build_sources(rag_results),
                confidence=0.5,
                session_id=request.session_id,
                language=request.language or "en",
            )

        return QueryResponse(
            intent=intent.value,
            answer=(
                f"I couldn't find any products matching "
                f"'{search_term}'. Please try a different search term."
            ),
            confidence=0.4,
            session_id=request.session_id,
            language=request.language or "en",
        )

    # ---------------------------------------------------------------
    # Enrich products with live inventory.
    # ---------------------------------------------------------------

    enriched_products: list[ProductInfo] = []
    answer_parts: list[str] = []

    for product in products[:5]:
        pid = product.get(
            "product_id",
            product.get("id", ""),
        )

        inventory_response = (
            await backend.get_inventory(pid)
            if pid
            else None
        )

        stock: Optional[int] = None

        if inventory_response:
            # Current Member 3 format:
            #
            # {
            #   "product_id": "P005",
            #   "available": true,
            #   "inventory": [
            #       {
            #           "store_location": "...",
            #           "aisle": "...",
            #           "shelf": "...",
            #           "stock_quantity": 14
            #       }
            #   ]
            # }
            #
            # Sum stock across all stores.

            inventory_records = inventory_response.get(
                "inventory",
                []
            )

            if isinstance(inventory_records, list):
                quantities: list[int] = []

                for record in inventory_records:
                    if not isinstance(record, dict):
                        continue

                    quantity = record.get("stock_quantity")

                    if quantity is None:
                        continue

                    try:
                        quantities.append(int(quantity))
                    except (TypeError, ValueError):
                        continue

                if quantities:
                    stock = sum(quantities)

            # Fallback for flat inventory response formats.
            if stock is None:
                flat_stock = inventory_response.get(
                    "stock_quantity",
                    inventory_response.get(
                        "quantity",
                        inventory_response.get("stock"),
                    ),
                )

                if flat_stock is not None:
                    try:
                        stock = int(flat_stock)
                    except (TypeError, ValueError):
                        stock = None

        # -----------------------------------------------------------
        # Product location.
        # -----------------------------------------------------------

        location: Optional[ProductLocation] = None

        loc_data = product.get("location")

        if loc_data and isinstance(loc_data, dict):
            try:
                location = ProductLocation(
                    **{
                        key: value
                        for key, value in loc_data.items()
                        if key in ProductLocation.model_fields
                    }
                )
            except Exception:
                location = None

        # If the backend inventory response contains locations,
        # use the first one when product data does not already have
        # a location.
        if location is None and inventory_response:
            inventory_records = inventory_response.get(
                "inventory",
                []
            )

            if (
                isinstance(inventory_records, list)
                and inventory_records
            ):
                first_record = inventory_records[0]

                if isinstance(first_record, dict):
                    location = ProductLocation(
                        store=first_record.get("store_location"),
                        aisle=first_record.get("aisle"),
                        shelf=first_record.get("shelf"),
                    )

        product_info = ProductInfo(
            product_id=str(pid),
            name=product.get(
                "name",
                "Unknown",
            ),
            brand=product.get("brand"),
            category=product.get("category"),
            color=product.get("color"),
            size=(
                str(product.get("size"))
                if product.get("size")
                else None
            ),
            price=product.get("price"),
            image_url=product.get(
                "image_url",
                "",
            ),
            stock_quantity=stock,
            location=location,
            description=product.get("description"),
        )

        enriched_products.append(product_info)

        # -----------------------------------------------------------
        # Human-readable answer.
        # -----------------------------------------------------------

        answer_parts.append(
            localize_inventory_answer(
                name=product_info.name,
                stock=stock,
                language=request.language,
            )
        )

    return QueryResponse(
        intent=intent.value,
        answer=" ".join(answer_parts),
        products=enriched_products,
        confidence=0.95,
        session_id=request.session_id,
        language=request.language or "en",
    )


# ---------------------------------------------------------------------- #
# PRODUCT_LOCATION
# ---------------------------------------------------------------------- #

async def _handle_product_location(
    query: str,
    request: QueryRequest,
    intent: Intent,
) -> QueryResponse:
    """Find where a product is located in the store."""

    search_term = detector.extract_product_query(query)

    search_term, products = await _search_products_with_variants(
        search_term
    )

    if not products:
        return QueryResponse(
            intent=intent.value,
            answer=(
                f"I couldn't find a product matching "
                f"'{search_term}' in our catalog."
            ),
            confidence=0.35,
            session_id=request.session_id,
            language=request.language or "en",
        )

    enriched_products: list[ProductInfo] = []
    answer_parts: list[str] = []

    for product in products[:5]:
        pid = product.get(
            "product_id",
            product.get("id", ""),
        )

        inventory_response = (
            await backend.get_inventory(pid)
            if pid
            else None
        )

        location: Optional[ProductLocation] = None

        loc_data = product.get("location")

        if loc_data and isinstance(loc_data, dict):
            try:
                location = ProductLocation(
                    **{
                        key: value
                        for key, value in loc_data.items()
                        if key in ProductLocation.model_fields
                    }
                )
            except Exception:
                location = None

        if location is None and inventory_response:
            records = inventory_response.get(
                "inventory",
                [],
            )

            if isinstance(records, list) and records:
                first = records[0]

                if isinstance(first, dict):
                    location = ProductLocation(
                        store=first.get("store_location"),
                        aisle=first.get("aisle"),
                        shelf=first.get("shelf"),
                    )

        product_info = ProductInfo(
            product_id=str(pid),
            name=product.get(
                "name",
                "Unknown",
            ),
            brand=product.get("brand"),
            category=product.get("category"),
            color=product.get("color"),
            size=(
                str(product.get("size"))
                if product.get("size")
                else None
            ),
            price=product.get("price"),
            image_url=product.get(
                "image_url",
                "",
            ),
            location=location,
            description=product.get("description"),
        )

        enriched_products.append(product_info)

        if location:
            location_parts: list[str] = []

            if location.store:
                location_parts.append(location.store)

            if location.aisle:
                location_parts.append(
                    f"Aisle {location.aisle}"
                )

            if location.shelf:
                location_parts.append(
                    f"Shelf {location.shelf}"
                )

            answer_parts.append(
                localize_location_answer(
                    name=product_info.name,
                    store=location.store,
                    aisle=location.aisle,
                    shelf=location.shelf,
                    language=request.language,
                )
            )

        else:
            answer_parts.append(
                f"I found {product_info.name}, but I couldn't "
                "verify its store location."
            )

    return QueryResponse(
        intent=intent.value,
        answer=" ".join(answer_parts),
        products=enriched_products,
        confidence=0.95,
        session_id=request.session_id,
        language=request.language or "en",
    )


# ---------------------------------------------------------------------- #
# RETURN_REQUEST
# ---------------------------------------------------------------------- #

async def _handle_return(
    query: str,
    request: QueryRequest,
    intent: Intent,
) -> QueryResponse:
    """Check and initiate product returns."""

    order_id = _extract_order_id(query)
    product_id = _extract_product_id(query)

    missing_information: list[str] = []

    if not order_id:
        missing_information.append("order_id")

    if not product_id:
        missing_information.append("product_id")

    if not order_id:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I can help you with the return. "
                "Please provide your order ID and product ID."
            ),
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.PENDING,
                required_information=["order_id"],
            ),
            missing_information=["order_id"],
            confidence=0.8,
            session_id=request.session_id,
            language=request.language or "en",
        )

    if order_id and not product_id:
        order = await backend.get_order(order_id)
        product_id = (
            order.get("product_id")
            if order
            else None
        )

        if product_id:
            missing_information = []
        else:
            missing_information.append("product_id")

    if missing_information:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I can help you with the return, but I couldn't find "
                "the product linked to that order. Please provide the "
                "product ID."
            ),
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.PENDING,
                required_information=missing_information,
            ),
            missing_information=missing_information,
            confidence=0.7,
            session_id=request.session_id,
            language=request.language or "en",
        )

    eligibility = await backend.check_return(
        order_id,
        product_id,
    )

    if not eligibility:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I couldn't verify the return eligibility right now."
            ),
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message="Return eligibility could not be verified.",
            ),
            confidence=0.4,
            session_id=request.session_id,
            language=request.language or "en",
        )

    eligible = eligibility.get(
        "eligible",
        eligibility.get(
            "is_eligible",
            False,
        ),
    )

    if not eligible:
        return QueryResponse(
            intent=intent.value,
            answer=eligibility.get(
                "message",
                "This item is not eligible for return.",
            ),
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message=eligibility.get("message"),
            ),
            confidence=0.9,
            session_id=request.session_id,
            language=request.language or "en",
        )

    result = await backend.initiate_return(
        order_id,
        product_id,
    )

    if not result:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "The return is eligible, but I couldn't create "
                "the return request right now."
            ),
            action_required=True,
            action=Action(
                type=ActionType.RETURN,
                status=ActionStatus.FAILED,
                message="Return request could not be created.",
            ),
            confidence=0.7,
            session_id=request.session_id,
            language=request.language or "en",
        )

    ticket_id = (
        result.get("ticket_id")
        or result.get("return_id")
        or result.get("id")
    )

    return QueryResponse(
        intent=intent.value,
        answer=(
            "Your return has been initiated successfully."
            + (
                f" Your return ticket is {ticket_id}."
                if ticket_id
                else ""
            )
        ),
        action_required=False,
        action=Action(
            type=ActionType.RETURN,
            status=ActionStatus.COMPLETED,
            ticket_id=ticket_id,
            message=result.get("message"),
        ),
        confidence=0.98,
        session_id=request.session_id,
        language=request.language or "en",
    )


# ---------------------------------------------------------------------- #
# EXCHANGE_REQUEST
# ---------------------------------------------------------------------- #

async def _handle_exchange(
    query: str,
    request: QueryRequest,
    intent: Intent,
) -> QueryResponse:
    """Check and initiate product exchanges."""

    order_id = _extract_order_id(query)
    product_id = _extract_product_id(query)
    replacement_product_id = _extract_replacement_product_id(query)

    missing_information: list[str] = []

    if not order_id:
        missing_information.append("order_id")

    if not product_id:
        missing_information.append("product_id")

    if not replacement_product_id:
        missing_information.append(
            "replacement_product_id"
        )

    if missing_information:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I can help you with the exchange. "
                "Please provide the order ID, current product ID, "
                "and replacement product ID."
            ),
            action_required=True,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.PENDING,
                required_information=missing_information,
            ),
            missing_information=missing_information,
            confidence=0.8,
            session_id=request.session_id,
            language=request.language or "en",
        )

    eligibility = await backend.check_exchange(
        order_id,
        product_id,
        replacement_product_id,
    )

    if not eligibility:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I couldn't verify the exchange eligibility right now."
            ),
            action_required=True,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.FAILED,
                message="Exchange eligibility could not be verified.",
            ),
            confidence=0.4,
            session_id=request.session_id,
            language=request.language or "en",
        )

    eligible = eligibility.get(
        "eligible",
        eligibility.get(
            "is_eligible",
            False,
        ),
    )

    if not eligible:
        return QueryResponse(
            intent=intent.value,
            answer=eligibility.get(
                "message",
                "This exchange is not currently eligible.",
            ),
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.FAILED,
                message=eligibility.get("message"),
            ),
            confidence=0.9,
            session_id=request.session_id,
            language=request.language or "en",
        )

    result = await backend.initiate_exchange(
        order_id,
        product_id,
        replacement_product_id,
    )

    if not result:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "The exchange is eligible, but I couldn't create "
                "the exchange request right now."
            ),
            action_required=True,
            action=Action(
                type=ActionType.EXCHANGE,
                status=ActionStatus.FAILED,
                message="Exchange request could not be created.",
            ),
            confidence=0.7,
            session_id=request.session_id,
            language=request.language or "en",
        )

    ticket_id = (
        result.get("ticket_id")
        or result.get("exchange_id")
        or result.get("id")
    )

    return QueryResponse(
        intent=intent.value,
        answer=(
            "Your exchange has been initiated successfully."
            + (
                f" Your exchange ticket is {ticket_id}."
                if ticket_id
                else ""
            )
        ),
        action_required=False,
        action=Action(
            type=ActionType.EXCHANGE,
            status=ActionStatus.COMPLETED,
            ticket_id=ticket_id,
            message=result.get("message"),
        ),
        confidence=0.98,
        session_id=request.session_id,
        language=request.language or "en",
    )


# ---------------------------------------------------------------------- #
# GENERAL_QUERY
# ---------------------------------------------------------------------- #

async def _handle_general(
    query: str,
    request: QueryRequest,
    intent: Intent,
) -> QueryResponse:
    """Handle general questions using the RAG knowledge base."""

    results = retrieve(query)

    if not results:
        return QueryResponse(
            intent=intent.value,
            answer=(
                "I'm sorry, I couldn't find relevant information "
                "to answer that question."
            ),
            confidence=0.2,
            session_id=request.session_id,
            language=request.language or "en",
        )

    answer = results[0].text.strip()

    return QueryResponse(
        intent=intent.value,
        answer=answer,
        sources=_build_sources(results),
        confidence=0.8,
        session_id=request.session_id,
        language=request.language or "en",
    )