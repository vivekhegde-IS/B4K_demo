"""Canonical language handling and short answer localization."""

from __future__ import annotations


LANGUAGE_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "kn": "kn-IN",
}


def normalize_language(language: str | None) -> str:
    """Return the supported two-letter UI/API language code."""

    value = (language or "en").strip().lower()
    value = value.split("-")[0]
    return value if value in LANGUAGE_CODES else "en"


def speech_language(language: str | None) -> str:
    """Return the locale expected by Indian-language speech services."""

    return LANGUAGE_CODES[normalize_language(language)]


def localize_inventory_answer(
    name: str,
    stock: int | None,
    language: str | None,
) -> str:
    """Render verified inventory facts in the requested language."""

    code = normalize_language(language)

    if stock is None:
        messages = {
            "en": f"{name} was found, but I couldn't verify its live inventory.",
            "hi": f"{name} मिला, लेकिन मैं इसका लाइव स्टॉक सत्यापित नहीं कर सका।",
            "kn": f"{name} ಕಂಡುಬಂದಿದೆ, ಆದರೆ ಲೈವ್ ಸ್ಟಾಕ್ ಅನ್ನು ಪರಿಶೀಲಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        }
    elif stock == 0:
        messages = {
            "en": f"{name} is currently out of stock.",
            "hi": f"{name} का स्टॉक अभी उपलब्ध नहीं है।",
            "kn": f"{name} ಪ್ರಸ್ತುತ ಸ್ಟಾಕ್‌ನಲ್ಲಿ ಇಲ್ಲ.",
        }
    elif stock == 1:
        messages = {
            "en": f"{name} has 1 unit available.",
            "hi": f"{name} की 1 इकाई उपलब्ध है।",
            "kn": f"{name} 1 ಘಟಕ ಲಭ್ಯವಿದೆ.",
        }
    else:
        messages = {
            "en": f"{name} has {stock} units available.",
            "hi": f"{name} की {stock} इकाइयाँ उपलब्ध हैं।",
            "kn": f"{name} {stock} ಘಟಕಗಳು ಲಭ್ಯವಿವೆ.",
        }

    return messages[code]


def localize_location_answer(
    name: str,
    store: str | None,
    aisle: str | None,
    shelf: str | None,
    language: str | None,
) -> str:
    """Render verified store location facts in the requested language."""

    location_parts = [part for part in (store,) if part]
    if aisle:
        location_parts.append(f"Aisle {aisle}")
    if shelf:
        location_parts.append(f"Shelf {shelf}")
    location = ", ".join(location_parts)
    code = normalize_language(language)

    messages = {
        "en": f"{name} is located at {location}.",
        "hi": f"{name} यहाँ स्थित है: {location}।",
        "kn": f"{name} ಇಲ್ಲಿ ಇದೆ: {location}.",
    }
    return messages[code]