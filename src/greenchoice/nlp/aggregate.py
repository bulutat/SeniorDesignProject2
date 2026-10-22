"""Yorum düzeyindeki aspect'leri ürün düzeyinde özelliklere çevirir (Aşama 2, Kişi B).

Her aspect için:
  <aspect>_pos / <aspect>_neg : o aspect'i olumlu / olumsuz anan yorum sayısı
  <aspect>_score              : (pos - neg) / (pos + neg + smoothing), [-1, 1] aralığında
Ek olarak:
  service_issue_rate          : servis veya arıza şikâyeti içeren yorumların oranı
"""

from __future__ import annotations

import pandas as pd

from greenchoice.config import aspects_config


def product_review_features(reviews: pd.DataFrame, review_aspects: pd.DataFrame,
                            smoothing: float = 2.0) -> pd.DataFrame:
    aspects = list(aspects_config()["aspects"].keys())

    base = reviews.groupby("product_id").agg(
        n_reviews=("review_id", "count"),
        review_rating_avg=("rating", "mean"),
    )

    ra = review_aspects.merge(reviews[["review_id", "product_id"]], on="review_id")
    if ra.empty:
        counts = pd.DataFrame(index=base.index)
    else:
        counts = (ra.groupby(["product_id", "aspect", "polarity"])["review_id"].nunique()
                    .unstack(["aspect", "polarity"], fill_value=0))
    for aspect in aspects:
        for pol in ("pos", "neg"):
            col = (aspect, pol)
            base[f"{aspect}_{pol}"] = (counts[col] if col in counts.columns
                                       else 0)
    base = base.fillna({f"{a}_{p}": 0 for a in aspects for p in ("pos", "neg")})
    for aspect in aspects:
        pos, neg = base[f"{aspect}_pos"], base[f"{aspect}_neg"]
        base[f"{aspect}_score"] = (pos - neg) / (pos + neg + smoothing)

    issues = ra[(ra["polarity"] == "neg") & ra["aspect"].isin(["service", "failure"])]
    issue_reviews = issues.groupby("product_id")["review_id"].nunique()
    base["service_issue_rate"] = issue_reviews.reindex(base.index, fill_value=0) / base["n_reviews"]

    int_cols = [f"{a}_{p}" for a in aspects for p in ("pos", "neg")]
    base[int_cols] = base[int_cols].astype(int)
    return base.reset_index()
