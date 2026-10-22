"""Yorum temizleme (Aşama 1, Kişi A)."""

from __future__ import annotations

import pandas as pd

from greenchoice.contracts import REVIEW_COLUMNS, require_columns
from greenchoice.preprocess.text import normalize_text


def _looks_like_spam(text_clean: str) -> bool:
    words = text_clean.split()
    # "çok iyi çok iyi çok iyi ..." gibi tekrarlar
    return len(words) >= 6 and len(set(words)) / len(words) < 0.3


def clean_reviews(df: pd.DataFrame, min_chars: int = 10) -> pd.DataFrame:
    require_columns(df, REVIEW_COLUMNS, "reviews")
    out = df.dropna(subset=["text"]).copy()
    out["text"] = out["text"].astype(str).str.strip()
    out["text_clean"] = out["text"].map(normalize_text)
    out["rating"] = pd.to_numeric(out["rating"], errors="coerce")

    out = out[out["text_clean"].str.len() >= min_chars]
    out = out[~out["text_clean"].map(_looks_like_spam)]
    out = out.drop_duplicates(subset=["product_id", "text_clean"])
    out = out.drop_duplicates(subset=["review_id"])
    return out.reset_index(drop=True)
