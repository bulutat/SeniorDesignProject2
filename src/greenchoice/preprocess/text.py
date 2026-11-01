"""Türkçe metin normalizasyonu."""

from __future__ import annotations

import re
import unicodedata

_TR_UPPER = str.maketrans({"I": "ı", "İ": "i"})
_URL = re.compile(r"https?://\S+")
_NON_WORD = re.compile(r"[^\w\s]")
_SPACES = re.compile(r"\s+")
_ELONGATED = re.compile(r"([^\W\d_])\1{2,}")  # Türkçede üç aynı harf yan yana gelmez


def tr_lower(text: str) -> str:
    """Türkçe kurallarıyla küçük harf: I -> ı, İ -> i."""
    return text.translate(_TR_UPPER).lower()


def normalize_text(text: str) -> str:
    """Küçük harf, URL, noktalama ve emoji temizliği, uzatılmış harfleri kısaltma ("çoook" -> "çok")."""
    text = unicodedata.normalize("NFC", text)
    text = tr_lower(text)
    text = _URL.sub(" ", text)
    text = _NON_WORD.sub(" ", text)
    text = _ELONGATED.sub(r"\1", text)
    return _SPACES.sub(" ", text).strip()
