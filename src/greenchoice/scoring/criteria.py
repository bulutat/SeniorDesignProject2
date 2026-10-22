"""Ham özelliklerden 0-1 aralığında kriter alt skorları.

Yapılandırılmış özellikler (fiyat, TCO, kWh) kategori içinde min-max ile göreli hale
getirilir: "benzer ürünlere göre" karşılaştırma budur. Enerji sınıfı ve yorum tabanlı
özellikler ise mutlak ölçekte kalır. Eksik değer, kategori medyanıyla doldurulur ve
hangi kriterlerin doldurulduğu "imputed" kolonunda tutulur.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from greenchoice.config import categories_config, criteria_ids

ENERGY_CLASS_SCORE = {"A": 1.0, "B": 5 / 6, "C": 4 / 6, "D": 3 / 6, "E": 2 / 6, "F": 1 / 6, "G": 0.0}


def _minmax(s: pd.Series, higher_is_better: bool) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or hi == lo:
        out = pd.Series(0.5, index=s.index)
    else:
        out = (s - lo) / (hi - lo)
        if not higher_is_better:
            out = 1 - out
    return out.where(s.notna())


def _bayes_rating(g: pd.DataFrame, prior_count: float) -> pd.Series:
    avg = pd.to_numeric(g["rating_avg"], errors="coerce").fillna(g["review_rating_avg"])
    count = pd.to_numeric(g["rating_count"], errors="coerce").fillna(g["n_reviews"]).fillna(0)
    prior = avg.mean()
    if pd.isna(prior):
        return pd.Series(np.nan, index=g.index)
    return (prior_count * prior + count * avg) / (prior_count + count)


def compute_criteria(features: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """features: ürün + yorum özellikleri. Dönüş: aynı index, c_<kriter> kolonları ve imputed."""
    cfg = cfg or categories_config()
    prior_count = cfg["defaults"]["rating_prior_count"]
    crits = criteria_ids()
    parts = []
    for _, g in features.groupby("category", sort=False):
        c = pd.DataFrame(index=g.index)
        energy_cls = g["energy_class"].map(ENERGY_CLASS_SCORE).astype(float)
        kwh = _minmax(g["annual_kwh"], higher_is_better=False)
        c["energy_efficiency"] = pd.concat([energy_cls, kwh], axis=1).mean(axis=1)
        c["lifetime_cost"] = _minmax(g["tco_tl"], higher_is_better=False)
        c["durability"] = (g["durability_score"] + 1) / 2
        c["service"] = 1 - g["service_issue_rate"]
        c["price_advantage"] = _minmax(g["price_tl"], higher_is_better=False)
        c["satisfaction"] = (_bayes_rating(g, prior_count) - 1) / 4
        c = c[crits].astype(float)

        missing = c.isna()
        c = c.fillna(c.median()).fillna(0.5).clip(0, 1)
        c["imputed"] = [",".join(m.index[m]) for _, m in missing.iterrows()]
        parts.append(c)

    out = pd.concat(parts).loc[features.index]
    return out.rename(columns={k: f"c_{k}" for k in crits})
