"""Canonical language handling for the Agent service."""

from __future__ import annotations


LANGUAGE_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "kn": "kn-IN",
}


def normalize_language(language: str | None) -> str:
    """Return the supported two-letter UI/API language code."""

    value = (language or "en").strip().lower().split("-")[0]
    return value if value in LANGUAGE_CODES else "en"


def speech_language(language: str | None) -> str:
    """Return the locale expected by Indian-language speech services."""

    return LANGUAGE_CODES[normalize_language(language)]
