"""Manuel etiketlerle uyum ölçümleri (Aşama 2-3, ortak).

Ürün etiketleri dosyası (data/annotations/product_labels.csv):
    product_id, annotator, label      # label: recommended | neutral | not_recommended
"""

from __future__ import annotations

import pandas as pd
from scipy.stats import kendalltau, spearmanr
from sklearn.metrics import cohen_kappa_score

LABEL_ORDER = {"not_recommended": 0, "neutral": 1, "recommended": 2}


def annotator_kappa(labels: pd.DataFrame, a: str, b: str) -> float:
    """İki etiketleyici arasında Cohen's kappa (sıralı etiketler için quadratic ağırlıklı)."""
    wide = labels.pivot_table(index="product_id", columns="annotator", values="label",
                              aggfunc="first").dropna(subset=[a, b])
    return cohen_kappa_score(wide[a].map(LABEL_ORDER), wide[b].map(LABEL_ORDER),
                             weights="quadratic")


def consensus_labels(labels: pd.DataFrame) -> pd.Series:
    """Etiketleyicilerin sıralı ortalamasına en yakın etiket. Uyuşmazlıklar ayrıca konuşulmalı."""
    mean = labels.assign(v=labels["label"].map(LABEL_ORDER)).groupby("product_id")["v"].mean()
    inv = {v: k for k, v in LABEL_ORDER.items()}
    return mean.round().astype(int).map(inv)


def score_agreement(scores: pd.Series, manual: pd.Series) -> dict[str, float]:
    """Sistem skoru ile manuel etiket sırası arasındaki sıralama korelasyonu."""
    df = pd.concat([scores.rename("score"), manual.map(LABEL_ORDER).rename("manual")],
                   axis=1).dropna()
    return {
        "n": len(df),
        "spearman": spearmanr(df["score"], df["manual"]).statistic,
        "kendall": kendalltau(df["score"], df["manual"]).statistic,
    }
