"""Keeps delivery remarks from counting as statements about the product.

"Sorunsuz ulaştı" praises the delivery, not durability. Dropping whole clauses or reviews lost
real product information (measured on the pilot reviews, docs/yorum-toplama.md), so only the
ambiguous words are removed, and only next to delivery or installation context. The raw text is
never changed. Word lists: config/aspects.yaml (logistics).
"""

from __future__ import annotations

import re
from functools import lru_cache

from greenchoice.config import aspects_config


def _word_start(words: list[str]) -> re.Pattern:
    return re.compile("^(?:" + "|".join(re.escape(w) for w in words) + ")")


@lru_cache
def _rules() -> dict:
    cfg = aspects_config()["logistics"]
    return {
        "ambiguous": _word_start(cfg["ambiguous"]),
        "context": _word_start(cfg["terms"] + cfg["context"]),
        "product_use": _word_start(cfg["product_use"]),
        "terms": re.compile(r"(?<!\w)(?:" + "|".join(cfg["terms"]) + ")"),
        "window": cfg["window"],
    }


def mentions_logistics(text_clean: str) -> bool:
    return bool(_rules()["terms"].search(text_clean))


def product_text(text_clean: str) -> str:
    """text_clean without ambiguous words that describe the delivery."""
    rules = _rules()
    tokens = text_clean.split()
    window = rules["window"]
    kept = []
    for i, token in enumerate(tokens):
        if rules["ambiguous"].match(token):
            next_token = tokens[i + 1] if i + 1 < len(tokens) else ""
            nearby = tokens[max(0, i - window):i] + tokens[i + 1:i + 1 + window]
            if not rules["product_use"].match(next_token) and any(
                    rules["context"].match(t) for t in nearby):
                continue
        kept.append(token)
    return " ".join(kept)
