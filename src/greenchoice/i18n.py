"""Supported interface languages and the display names that depend on them.

Turkish is the source language: config names (`name`) and `contracts.LABELS` are Turkish and
stay unchanged. Other languages are added beside them (`names: {en: ..., de: ...}` in
config/categories.yaml, `LABEL_TEXTS` below). Data values (product names, prices in TL) are
never translated.
"""

from __future__ import annotations

from greenchoice.contracts import LABELS

LANGUAGES = ("tr", "en", "de")
DEFAULT_LANGUAGE = "tr"

LABEL_TEXTS = {
    "tr": LABELS,
    "en": {"recommended": "Recommended", "neutral": "Neutral", "not_recommended": "Not recommended"},
    "de": {"recommended": "Empfohlen", "neutral": "Neutral", "not_recommended": "Nicht empfohlen"},
}


def check_language(lang: str) -> str:
    if lang not in LANGUAGES:
        raise ValueError(f"Unsupported language {lang!r}; expected one of {LANGUAGES}")
    return lang


def label_text(label: str, lang: str = DEFAULT_LANGUAGE) -> str:
    return LABEL_TEXTS[check_language(lang)][label]


def display_name(entry: dict, lang: str = DEFAULT_LANGUAGE) -> str:
    """Name of a criterion or category from config: `name` for Turkish, `names[lang]` otherwise."""
    if check_language(lang) == "tr":
        return entry["name"]
    return entry["names"][lang]
