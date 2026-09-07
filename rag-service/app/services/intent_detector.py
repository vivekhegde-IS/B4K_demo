"""Rule-based intent detector for RetailMate.

Classifies user queries into one of the supported intents using
keyword/pattern matching. This is a deterministic classifier suitable
for MVP — it is not an LLM.

Supported intents
-----------------
- INVENTORY_QUERY   — stock / availability questions
- PRODUCT_LOCATION  — "where can I find ..." questions
- POLICY_QUERY      — return / cancellation / exchange policy
- RETURN_REQUEST    — user wants to initiate a return
- EXCHANGE_REQUEST  — user wants to initiate an exchange
- GENERAL_QUERY     — catch-all fallback
"""

from __future__ import annotations

import re

from app.models.schemas import Intent


# ---------------------------------------------------------------------------
# Pattern groups
# Pattern order matters — first match wins.
# ---------------------------------------------------------------------------

_RETURN_REQUEST_PATTERNS = [
    r"\breturn\b.*\border\b",
    r"\bi\s+want\s+to\s+return\b",
    r"\breturn\s+(my|this|order|product|item)",
    r"\binitiate\s+(a\s+)?return\b",
    r"\bprocess\s+(a\s+)?return\b",
    r"\breturn\s+request\b",
    r"\breturn\s+ord\d+",
]

_EXCHANGE_REQUEST_PATTERNS = [
    r"\bexchange\b.*\border\b",
    r"\bi\s+want\s+to\s+exchange\b",
    r"\bexchange\s+(my|this|order|product|item)",
    r"\binitiate\s+(an?\s+)?exchange\b",
    r"\bexchange\s+(it|this)\s+for\b",
    r"\bexchange\s+ord\d+",
    r"\bswap\b.*\b(product|order|item)\b",
]

_POLICY_PATTERNS = [
    r"\breturn\s+policy\b",
    r"\bexchange\s+policy\b",
    r"\bcancellation\s+policy\b",
    r"\bcancel\s+(my\s+)?order\b",
    r"\bcan\s+i\s+cancel\b",
    r"\breturn\s+window\b",
    r"\bhow\s+(long|many\s+days)\s+(can|do)\s+(i|we)\s+(have\s+to\s+)?return\b",
    r"\breturn\s+period\b",
    r"\breturn\s+condition\b",
    r"\bnon[\-\s]?returnable\b",
    r"\bcannot\s+be\s+returned\b",
    r"\bwhat\s+(are|is)\s+the\s+return\b",
    r"\breturn\s+rules?\b",
    r"\brefund\s+policy\b",
    r"\breplacement\s+policy\b",
    r"\bwhat\s+happens\s+if\s+(the\s+)?(product|item)\s+is\s+damaged\b",
    r"\bdamaged\s+(product|item).*return\b",
    r"\bwrong\s+(product|item).*return\b",
    r"\bpickup\s+requirement\b",
    r"\bproduct\s+condition\s+for\s+return\b",
    r"\bhow\s+to\s+return\b",
    r"\bcan\s+i\s+return\b",
    r"\bis\s+.*\breturnable\b",
    r"\breturn\b.*\beligib",
    r"\bcancel\s+before\s+dispatch\b",
    r"\bcancel\s+after\s+dispatch\b",
]

_PRODUCT_LOCATION_PATTERNS = [
    r"\bwhere\s+(can\s+i\s+find|is|are|do\s+you\s+keep)\b",
    r"\bwhich\s+aisle\b",
    r"\bwhich\s+shelf\b",
    r"\bwhich\s+section\b",
    r"\blocation\s+of\b",
    r"\blocate\b",
    r"\bwhere\s+.*\b(shoe|shirt|jeans|belt|speaker|headphone|earbuds|footwear|clothing)\b",
    r"\bfind\s+.*\b(in\s+store|in\s+the\s+store)\b",
    r"\bstore\s+location\b",
    r"\bdepartment\s+for\b",
    r"ನೈಕ್.*ಎಲ್ಲಿ",
    r"ಎಲ್ಲಿ.*(?:ಉತ್ಪನ್ನ|ಶರ್ಟ್|ಟೀ ಶರ್ಟ್)",
    r"ನೈಕ್.*ಎಲ್ಲಿದೆ",
    r"ಎಲ್ಲಿದೆ.*(?:ನೈಕ್|ಶರ್ಟ್|ಟೀ ಶರ್ಟ್)",
    r"ಎಲ್ಲಿ.*(?:ನೈಕ್|ಶರ್ಟ್|ಟೀ ಶರ್ಟ್)",
    r"नाइके.*कहाँ",
    r"कहाँ.*(?:उत्पाद|शर्ट|टी[- ]?शर्ट)",
    r"नाइके.*कहाँ है",
    r"कहाँ है.*(?:नाइके|शर्ट|टी[- ]?शर्ट)",
]

_INVENTORY_PATTERNS = [
    r"\bin\s+stock\b",
    r"\bavailab(le|ility)\b",
    r"\bdo\s+you\s+have\b",
    r"\bhave\s+you\s+got\b",
    r"\bgot\s+any\b",
    r"\bstock\b",
    r"\bhow\s+many\s+.*\b(left|remain|available)\b",
    r"\bcheck\s+(if|whether)\b.*\bavailab",
    r"\bshow\s+me\b",
    r"\bsearch\s+for\b",
    r"\blooking\s+for\b",
    r"\bany\s+.*\b(under|below|less\s+than)\s+[₹$]?\d+",
    r"\bfind\s+(me\s+)?(a\s+)?\b",
    r"(?:ನೈಕ್|ಲಭ್ಯ|ಸ್ಟಾಕ್|ಎಷ್ಟು).*(?:ಲಭ್ಯ|ಸ್ಟಾಕ್|ಎಷ್ಟು)",
    r"(?:ನೈಕ್|ಶರ್ಟ್|ಟೀ ಶರ್ಟ್).*(?:ಎಷ್ಟು|ಲಭ್ಯವಿದೆ|ಲಭ್ಯವಿವೆ|ಸ್ಟಾಕ್)",
    r"(?:ಎಷ್ಟು|ಲಭ್ಯವಿದೆ|ಲಭ್ಯವಿವೆ|ಸ್ಟಾಕ್).*(?:ನೈಕ್|ಶರ್ಟ್|ಟೀ ಶರ್ಟ್)",
    r"(?:नाइके|उपलब्ध|स्टॉक|कितनी|कितने).*(?:उपलब्ध|स्टॉक|कितनी|कितने)",
    r"(?:नाइके|शर्ट|टी[- ]?शर्ट).*(?:कितनी|कितने|उपलब्ध|स्टॉक)",
    r"(?:कितनी|कितने|उपलब्ध|स्टॉक).*(?:नाइके|शर्ट|टी[- ]?शर्ट)",
]


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def _match(query_lower: str, patterns: list[str]) -> bool:
    """Return True if any pattern matches the query."""
    return any(re.search(pattern, query_lower) for pattern in patterns)


def detect_intent(query: str) -> Intent:
    """Classify a query into one of the supported RetailMate intents.

    Returns GENERAL_QUERY as the fallback — never UNKNOWN.
    """
    q = query.lower().strip()

    # Most specific intents first.
    if _match(q, _RETURN_REQUEST_PATTERNS):
        return Intent.RETURN_REQUEST

    if _match(q, _EXCHANGE_REQUEST_PATTERNS):
        return Intent.EXCHANGE_REQUEST

    if _match(q, _POLICY_PATTERNS):
        return Intent.POLICY_QUERY

    if _match(q, _PRODUCT_LOCATION_PATTERNS):
        return Intent.PRODUCT_LOCATION

    if _match(q, _INVENTORY_PATTERNS):
        return Intent.INVENTORY_QUERY

    return Intent.GENERAL_QUERY


# ---------------------------------------------------------------------------
# Entity extraction
# ---------------------------------------------------------------------------

_ORDER_ID_RE = re.compile(
    r"\b(ORD[-_]?\d+)\b",
    re.IGNORECASE,
)

_PRODUCT_ID_RE = re.compile(
    r"\b(P\d{3,})\b",
    re.IGNORECASE,
)


def extract_order_id(query: str) -> str | None:
    """Extract an order ID such as ORD001 from the query."""
    match = _ORDER_ID_RE.search(query)

    if match:
        return match.group(1).upper()

    return None


def extract_product_id(query: str) -> str | None:
    """Extract a product ID such as P001 from the query."""
    match = _PRODUCT_ID_RE.search(query)

    if match:
        return match.group(1).upper()

    return None


def extract_product_query(query: str) -> str:
    """Extract the product search term from a natural-language query.

    Examples
    --------
    "Do you have Nike shoes?"
        -> "Nike shoes"

    "Where is the Nike Air Max 270?"
        -> "Nike Air Max 270"

    "How many Nike Dri-FIT T-Shirts are available?"
        -> "Nike Dri-FIT T-Shirts"

    "Are Nike shoes in stock?"
        -> "Nike shoes"
    """
    q = query.strip()

    # Preserve the demo product identity when an Indian-language query
    # uses a transliterated Nike/T-shirt name.
    if re.search(r"नाइके|नाइक|नाइकी|ನೈಕ್", q, flags=re.IGNORECASE):
        return "Nike Dri-FIT T-Shirt"

    # Remove common leading phrases.
    q = re.sub(
        r"^(do you have|have you got|is there|are there|show me|find me|"
        r"search for|looking for|i('m| am) looking for|"
        r"where (can i find|is|are)|check if|can i get|how many)\s+",
        "",
        q,
        flags=re.IGNORECASE,
    )

    # Remove leading articles.
    q = re.sub(
        r"^(the|a|an)\s+",
        "",
        q,
        flags=re.IGNORECASE,
    )

    # Remove trailing availability phrases.
    q = re.sub(
        r"\s+(are|is)\s+(available|in\s+stock)\s*[?.!]*$",
        "",
        q,
        flags=re.IGNORECASE,
    )

    # Handle:
    # "Nike shoes available"
    # "Nike shoes in stock"
    q = re.sub(
        r"\s+(available|in\s+stock)\s*[?.!]*$",
        "",
        q,
        flags=re.IGNORECASE,
    )

    # Remove trailing punctuation.
    q = q.rstrip("?.!").strip()

    return q if q else query.strip()