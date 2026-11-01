"""Yorum temizleme (Aşama 1, Kişi A)."""

from __future__ import annotations

import pandas as pd

from greenchoice.contracts import REVIEW_COLUMNS, require_columns
from greenchoice.preprocess.scope import mentions_logistics, product_text
from greenchoice.preprocess.text import normalize_text


def _looks_like_spam(text_clean: str) -> bool:
    words = text_clean.split()
    # "çok iyi çok iyi çok iyi ..." gibi tekrarlar
    return len(words) >= 6 and len(set(words)) / len(words) < 0.3


def clean_reviews(df: pd.DataFrame, min_chars: int = 10) -> pd.DataFrame:
    require_columns(df, REVIEW_COLUMNS, "reviews")
    out = df.dropna(subset=["text"]).copy()
    if out.empty:  # boolean masks on an empty object Series would select columns, not rows
        out["text_clean"] = pd.Series(dtype="object")
        out["text_product"] = pd.Series(dtype="object")
        out["mentions_logistics"] = pd.Series(dtype=bool)
        return out.reset_index(drop=True)
    out["text"] = out["text"].astype(str).str.strip()
    out["text_clean"] = out["text"].map(normalize_text)
    out["rating"] = pd.to_numeric(out["rating"], errors="coerce")

    out = out[out["text_clean"].str.len() >= min_chars]
    out = out[~out["text_clean"].map(_looks_like_spam)]
    out = out.drop_duplicates(subset=["product_id", "text_clean"])
    out = out.drop_duplicates(subset=["review_id"])
    out["text_product"] = out["text_clean"].map(product_text)
    out["mentions_logistics"] = out["text_clean"].map(mentions_logistics)
    return out.reset_index(drop=True)
