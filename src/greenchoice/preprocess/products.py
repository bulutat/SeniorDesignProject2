"""Ürün verisi temizleme (Aşama 1, Kişi B)."""

from __future__ import annotations

import re

import pandas as pd

from greenchoice.contracts import PRODUCT_COLUMNS, require_columns

NUMERIC_COLUMNS = [
    "price_tl", "energy_kwh_per_year", "energy_kwh_per_100_cycles", "water_l_per_cycle",
    "capacity", "noise_db", "warranty_years", "rating_avg", "rating_count",
]
NEW_SCALE_CLASSES = set("ABCDEFG")


def parse_price(value) -> float | None:
    """'12.499,90 TL' -> 12499.9. Zaten sayıysa olduğu gibi döner."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = re.sub(r"[^\d,\.]", "", str(value))
    if "," in s:  # Türkçe biçim: binlik '.', ondalık ','
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def normalize_energy_class(value) -> tuple[str | None, str | None]:
    """(yeni ölçek sınıfı, ham değer) döner.

    2021 öncesi etiketler (A+++ ...) yeni A-G ölçeğine birebir çevrilemez; bu ürünlerde
    sınıf boş bırakılır ve EPREL'den doldurulması beklenir.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None, None
    raw = str(value).strip().upper().replace(" ", "")
    if raw in NEW_SCALE_CLASSES:
        return raw, raw
    return None, raw


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, PRODUCT_COLUMNS, "products")
    out = df.copy()
    out["price_tl"] = out["price_tl"].map(parse_price)
    for col in NUMERIC_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    classes = out["energy_class"].map(normalize_energy_class)
    out["energy_class"] = classes.map(lambda t: t[0])
    out["energy_class_raw"] = classes.map(lambda t: t[1])

    for col in ("brand", "model_code", "name"):
        out[col] = out[col].astype("string").str.strip()

    out = out.dropna(subset=["product_id", "category"])
    out = out.drop_duplicates(subset=["product_id"])
    return out.reset_index(drop=True)
