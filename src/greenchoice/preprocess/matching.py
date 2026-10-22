"""E-ticaret ürünlerini EPREL kayıtlarıyla model kodu üzerinden eşleştirme (Aşama 1, Kişi B)."""

from __future__ import annotations

import re

import pandas as pd

# EPREL'den gelen değer varsa e-ticaret değerinin yerine geçen alanlar
EPREL_PRIORITY_FIELDS = [
    "energy_class", "energy_kwh_per_year", "energy_kwh_per_100_cycles",
    "water_l_per_cycle", "noise_db",
]


def normalize_model_code(code) -> str | None:
    if code is None or (isinstance(code, float) and pd.isna(code)):
        return None
    s = re.sub(r"[\s\-_/\.]", "", str(code).upper())
    return s or None


def merge_eprel(products: pd.DataFrame, eprel: pd.DataFrame) -> pd.DataFrame:
    """eprel: en az 'model_code' ve EPREL_PRIORITY_FIELDS'ten bazılarını içeren tablo."""
    p = products.copy()
    e = eprel.copy()
    p["_key"] = p["model_code"].map(normalize_model_code)
    e["_key"] = e["model_code"].map(normalize_model_code)
    e = e.dropna(subset=["_key"]).drop_duplicates(subset=["_key"])

    fields = [f for f in EPREL_PRIORITY_FIELDS if f in e.columns]
    merged = p.merge(e[["_key", *fields]], on="_key", how="left", suffixes=("", "_eprel"))
    for f in fields:
        merged[f] = merged[f"{f}_eprel"].combine_first(merged[f])
    merged["eprel_matched"] = merged[f"{fields[0]}_eprel"].notna() if fields else False
    return merged.drop(columns=["_key", *[f"{f}_eprel" for f in fields]])
