"""Türkçe metin normalizasyonu."""

from __future__ import annotations

import re
import unicodedata

_TR_UPPER = str.maketrans({"I": "ı", "İ": "i"})
_URL = re.compile(r"https?://\S+")
_NON_WORD = re.compile(r"[^\w\s]")
_SPACES = re.compile(r"\s+")


def tr_lower(text: str) -> str:
    """Türkçe kurallarıyla küçük harf: I -> ı, İ -> i."""
    return text.translate(_TR_UPPER).lower()


def normalize_text(text: str) -> str:
    """Küçük harf, URL ve noktalama temizliği, boşluk sadeleştirme. Türkçe karakterler korunur."""
    text = unicodedata.normalize("NFC", text)
    text = tr_lower(text)
    text = _URL.sub(" ", text)
    text = _NON_WORD.sub(" ", text)
    return _SPACES.sub(" ", text).strip()
