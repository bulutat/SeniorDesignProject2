"""Sensitivity of the ranking to assumptions (task B3.3).

Each scenario changes one assumption (electricity price, lifetime, one criterion weight),
recomputes TCO, criteria and scores from the same product features, and compares the ranking
inside each category with the baseline: Kendall tau, overlap of the top 10 and how many labels
change. `breakeven_prices` answers "when does the cheap but inefficient product cost more?":
for every pair in a category where the cheaper product uses more energy, the electricity price
at which their lifetime costs are equal.
"""

from __future__ import annotations

import copy
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from greenchoice.config import categories_config, criteria_ids
from greenchoice.preprocess.tco import add_tco, annual_water_m3
from greenchoice.scoring.criteria import compute_criteria
from greenchoice.scoring.weighted import WeightedScorer

RAW_COLUMNS = ["product_id", "category", "price_tl", "energy_class", "energy_kwh_per_year",
               "energy_kwh_per_100_cycles", "water_l_per_cycle", "rating_avg", "rating_count",
               "n_reviews", "review_rating_avg", "durability_score", "service_issue_rate"]


def scores_for(features: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    base = add_tco(features[RAW_COLUMNS], cfg)
    crit = pd.concat([base, compute_criteria(base, cfg)], axis=1)
    return WeightedScorer(cfg).score(crit)[["product_id", "category", "score", "label"]]


def scenarios(cfg: dict) -> dict[str, dict]:
    out = {}
    price = cfg["defaults"]["electricity_price_tl_per_kwh"]
    for name, value in [("elektrik -%50", price * 0.5), ("elektrik +%50", price * 1.5),
                        ("elektrik yüksek kademe (4,321)", 4.321)]:
        c = copy.deepcopy(cfg)
        c["defaults"]["electricity_price_tl_per_kwh"] = value
        out[name] = c
    for years in (8, 15):
        c = copy.deepcopy(cfg)
        for cat in c["categories"].values():
            cat["lifetime_years"] = years
        out[f"ömür {years} yıl"] = c
    for crit in criteria_ids():
        for factor, tag in ((1.5, "+%50"), (0.5, "-%50")):
            c = copy.deepcopy(cfg)
            for cat in c["categories"].values():
                w = cat["weights"]
                w[crit] *= factor
                total = sum(w.values())
                cat["weights"] = {k: v / total for k, v in w.items()}
            out[f"ağırlık {crit} {tag}"] = c
    c = copy.deepcopy(cfg)
    for cat in c["categories"].values():
        cat["weights"] = {k: 1 / len(cat["weights"]) for k in cat["weights"]}
    out["eşit ağırlıklar"] = c
    return out


def compare(base: pd.DataFrame, other: pd.DataFrame) -> list[dict]:
    rows = []
    merged = base.merge(other, on=["product_id", "category"], suffixes=("", "_s"))
    for category, g in merged.groupby("category"):
        tau = kendalltau(g["score"], g["score_s"]).statistic
        top = len(set(g.nlargest(10, "score")["product_id"]) & set(g.nlargest(10, "score_s")["product_id"]))
        rows.append({"category": category, "kendall_tau": round(float(tau), 3), "top10_overlap": top,
                     "labels_changed": int((g["label"] != g["label_s"]).sum())})
    return rows


def sensitivity(features: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or categories_config()
    base = scores_for(features, cfg)
    rows = []
    for name, c in scenarios(cfg).items():
        rows += [{"scenario": name, **r} for r in compare(base, scores_for(features, c))]
    return pd.DataFrame(rows)


def breakeven_prices(features: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Pairs where the cheaper product uses more energy -> price per kWh that equalises TCO."""
    cfg = cfg or categories_config()
    water = cfg["defaults"]["water_price_tl_per_m3"]
    data = add_tco(features[RAW_COLUMNS], cfg).dropna(subset=["annual_kwh", "price_tl"])
    rows = []
    for category, g in data.groupby("category"):
        cat_cfg = cfg["categories"][category]
        years = cat_cfg["lifetime_years"]
        water_m3 = g.apply(lambda r, c=cat_cfg: annual_water_m3(r, c), axis=1)
        for i, j in combinations(g.index, 2):
            cheap, dear = (i, j) if g.at[i, "price_tl"] < g.at[j, "price_tl"] else (j, i)
            extra_kwh = g.at[cheap, "annual_kwh"] - g.at[dear, "annual_kwh"]
            if extra_kwh <= 0:
                continue  # the cheaper one is also the more efficient one: no trade-off
            gap = (g.at[dear, "price_tl"] - g.at[cheap, "price_tl"]
                   - years * water * (water_m3[cheap] - water_m3[dear]))
            rows.append({"category": category, "cheap": g.at[cheap, "product_id"],
                         "efficient": g.at[dear, "product_id"],
                         "price_gap_tl": round(float(g.at[dear, "price_tl"] - g.at[cheap, "price_tl"]), 0),
                         "extra_kwh_per_year": round(float(extra_kwh), 1),
                         "breakeven_tl_per_kwh": round(float(gap / (years * extra_kwh)), 2)})
    return pd.DataFrame(rows)


def breakeven_summary(pairs: pd.DataFrame, current_price: float) -> pd.DataFrame:
    if pairs.empty:
        return pd.DataFrame()
    out = []
    for category, g in pairs.groupby("category"):
        b = g["breakeven_tl_per_kwh"]
        out.append({"category": category, "pairs": len(g),
                    "already_pays_off": int((b <= current_price).sum()),
                    "pays_off_at_+50%": int((b <= current_price * 1.5).sum()),
                    "median_breakeven": round(float(np.median(b)), 2)})
    return pd.DataFrame(out)
