"""Gold labels + review text -> training data shared by the learned extractors.

Labels are "aspect:polarity" pairs from config/aspects.yaml; failure has no positive label
(annotation guideline). Text is cleaned exactly as in `build`, and the models read
`text_product`, the same column the rule-based extractor reads.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from greenchoice.config import aspects_config
from greenchoice.contracts import REVIEW_COLUMNS, conform
from greenchoice.nlp.labels import NEG_ONLY
from greenchoice.preprocess.reviews import clean_reviews

TEXT_COLUMN = "text_product"


def label_names() -> list[str]:
    return [f"{aspect}:{pol}" for aspect in aspects_config()["aspects"]
            for pol in ("pos", "neg") if not (aspect in NEG_ONLY and pol == "pos")]


def split_data(gold: pd.DataFrame, reviews: pd.DataFrame, split: str) -> tuple[pd.DataFrame, np.ndarray]:
    """One split -> (cleaned reviews in a fixed order, 0/1 matrix with one column per label)."""
    part = gold[gold["split"] == split]
    ids = part["review_id"].drop_duplicates().tolist()
    cleaned = clean_reviews(conform(reviews[reviews["review_id"].isin(ids)], REVIEW_COLUMNS))
    lost = sorted(set(ids) - set(cleaned["review_id"]))
    if lost:
        raise ValueError(f"{split}: {len(lost)} etiketli yorumun metni yok veya temizlikte düştü: {lost[:5]}")
    cleaned = cleaned.set_index("review_id").loc[ids].reset_index()
    names = label_names()
    y = np.zeros((len(ids), len(names)), dtype=np.float32)
    position = {rid: i for i, rid in enumerate(ids)}
    for record in part.dropna(subset=["aspect"]).itertuples():
        y[position[record.review_id], names.index(f"{record.aspect}:{record.polarity}")] = 1
    return cleaned, y


def to_review_aspects(review_ids: list[str], predicted: np.ndarray, method: str) -> pd.DataFrame:
    """0/1 matrix -> review_aspects rows (the shape the scoring and evaluation code read)."""
    from greenchoice.contracts import REVIEW_ASPECT_COLUMNS

    names = label_names()
    rows = [{"review_id": rid, "aspect": names[j].split(":")[0], "polarity": names[j].split(":")[1],
             "method": method, "evidence": None}
            for rid, row in zip(review_ids, predicted, strict=True) for j in np.flatnonzero(row)]
    return pd.DataFrame(rows, columns=REVIEW_ASPECT_COLUMNS)
