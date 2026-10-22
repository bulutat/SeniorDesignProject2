"""Skor + açıklama üretiminin tek kod yolu. Pipeline ve API (özel ağırlıklar) bunu kullanır."""

from __future__ import annotations

import pandas as pd

from greenchoice.config import categories_config
from greenchoice.explain.templates import build_explanations
from greenchoice.scoring.weighted import WeightedScorer


def score_products(features: pd.DataFrame, weights_override: dict[str, float] | None = None,
                   cfg: dict | None = None) -> pd.DataFrame:
    """features: product_features tablosu (ham özellikler + c_<kriter> + imputed).

    Dönüş: WeightedScorer çıktısı + explanations (liste) kolonu.
    """
    cfg = cfg or categories_config()
    scored = WeightedScorer(cfg).score(features, weights_override)
    by_id = features.set_index("product_id")
    explanations = []
    for _, s in scored.iterrows():
        row = by_id.loc[s["product_id"]].to_dict()
        imputed = [c for c in str(row.get("imputed") or "").split(",") if c]
        explanations.append(build_explanations(
            row, s["contributions"], imputed, cfg["criteria"],
            cfg["categories"][s["category"]]["lifetime_years"]))
    scored["explanations"] = explanations
    return scored
