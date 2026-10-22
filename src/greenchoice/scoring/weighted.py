"""Baseline: kategoriye özel ağırlıklı toplam (weighted_v0)."""

from __future__ import annotations

import pandas as pd

from greenchoice.config import categories_config


class WeightedScorer:
    method = "weighted_v0"

    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or categories_config()

    def weights_for(self, category: str, override: dict[str, float] | None = None) -> dict[str, float]:
        weights = dict(self.cfg["categories"][category]["weights"])
        if override:
            weights.update({k: float(v) for k, v in override.items() if k in weights})
        weights = {k: max(v, 0.0) for k, v in weights.items()}
        total = sum(weights.values())
        if total <= 0:
            raise ValueError("Ağırlıkların toplamı sıfırdan büyük olmalı")
        return {k: v / total for k, v in weights.items()}

    def label_for(self, score: float) -> str:
        t = self.cfg["defaults"]["label_thresholds"]
        if score >= t["recommended"]:
            return "recommended"
        if score >= t["neutral"]:
            return "neutral"
        return "not_recommended"

    def score(self, crit: pd.DataFrame, weights_override: dict[str, float] | None = None) -> pd.DataFrame:
        """crit: product_id, category ve c_<kriter> kolonları.

        Dönüş: product_id, category, method, score (0-100), label, sub_scores (0-100),
        contributions (kategori ortalamasına göre puan etkisi), weights.
        """
        rows = []
        for category, g in crit.groupby("category", sort=False):
            w = self.weights_for(category, weights_override)
            cols = {k: f"c_{k}" for k in w}
            means = {k: g[c].mean() for k, c in cols.items()}
            for _, r in g.iterrows():
                score = 100 * sum(w[k] * r[c] for k, c in cols.items())
                rows.append({
                    "product_id": r["product_id"],
                    "category": category,
                    "method": self.method,
                    "score": round(score, 1),
                    "label": self.label_for(score),
                    "sub_scores": {k: round(100 * r[c], 1) for k, c in cols.items()},
                    "contributions": {k: 100 * w[k] * (r[c] - means[k]) for k, c in cols.items()},
                    "weights": w,
                })
        return pd.DataFrame(rows)
