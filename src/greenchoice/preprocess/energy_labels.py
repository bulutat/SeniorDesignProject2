"""Energy data for products that EPREL does not cover.

Order of trust, highest first, and the value written to `energy_source`:
1. `eprel`: matched EPREL record (preprocess/matching.py).
2. `label`: the manufacturer's official EU energy label, read by hand
   (data/manual/energy_labels.csv, one row per product with the label URL).
3. `shop`: the class given in the collected product data.
4. `title`: the class written in the store's product title ("E Enerji Sınıfı").
   Seller text, so the least reliable; no kWh comes with it.
A lower source only fills fields that are still empty. Classes from the pre-2021 scale
(A+++ ... D) are never used: they cannot be converted to the A-G scale.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from greenchoice.preprocess.products import NEW_SCALE_CLASSES

LABEL_FIELDS = ["energy_class", "energy_kwh_per_year", "energy_kwh_per_100_cycles",
                "water_l_per_cycle", "capacity"]
REQUIRED = ["product_id", "energy_class", "source_url", "checked_on"]

# "E Enerji Sınıfı", "Enerji Sınıfı F", "Enerji Sınıfı: A". A letter followed by "+" is the old scale.
_TITLE_CLASS = re.compile(
    r"(?:enerji\s*s[ıi]n[ıi]f[ıi]\s*:?\s*([A-G])(?![\w+])|(?<![\w+])([A-G])\s*enerji\s*s[ıi]n[ıi]f)",
    re.IGNORECASE)


def class_from_title(name) -> str | None:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return None
    found = _TITLE_CLASS.search(str(name))
    if not found:
        return None
    cls = (found.group(1) or found.group(2)).upper()
    return cls if cls in NEW_SCALE_CLASSES else None


def load_energy_labels(path: Path) -> pd.DataFrame:
    table = pd.read_csv(path, dtype={"product_id": str, "energy_class": str})
    missing = [c for c in REQUIRED if c not in table.columns]
    if missing:
        raise ValueError(f"{path.name}: eksik kolonlar {missing}")
    for row_no, record in zip(table.index + 2, table.itertuples(), strict=True):
        where = f"{path.name} satır {row_no}"
        if str(record.energy_class).strip().upper() not in NEW_SCALE_CLASSES:
            raise ValueError(f"{where}: enerji sınıfı A-G olmalı, {record.energy_class!r} yazılmış")
        if not str(record.source_url).startswith("https://"):
            raise ValueError(f"{where}: source_url https:// ile başlamalı")
    if table["product_id"].duplicated().any():
        raise ValueError(f"{path.name}: aynı ürün iki kez var")
    table["energy_class"] = table["energy_class"].str.strip().str.upper()
    for col in LABEL_FIELDS[1:]:
        if col in table.columns:
            table[col] = pd.to_numeric(table[col], errors="raise")
    return table


def apply_energy_sources(products: pd.DataFrame, labels: pd.DataFrame | None = None) -> pd.DataFrame:
    """Fills empty energy fields from labels, then the class from the title; sets energy_source."""
    out = products.copy()
    eprel = out["eprel_matched"].fillna(False).astype(bool) if "eprel_matched" in out else False
    source = pd.Series(pd.NA, index=out.index, dtype="object")
    source[eprel & out["energy_class"].notna()] = "eprel"
    source[source.isna() & out["energy_class"].notna()] = "shop"

    if labels is not None and not labels.empty:
        by_id = labels.set_index("product_id")
        rows = out["product_id"].isin(by_id.index) & ~eprel
        for col in LABEL_FIELDS:
            if col not in by_id.columns:
                continue
            value = out.loc[rows, "product_id"].map(by_id[col])
            if col not in out.columns:
                out[col] = pd.NA
            out.loc[rows, col] = out.loc[rows, col].where(out.loc[rows, col].notna(), value)
        # The official label outranks the shop's class
        has_label_class = rows & out["product_id"].map(by_id["energy_class"]).notna()
        out.loc[has_label_class, "energy_class"] = out.loc[has_label_class, "product_id"].map(
            by_id["energy_class"])
        source[has_label_class] = "label"

    from_title = out["name"].map(class_from_title)
    fill = out["energy_class"].isna() & from_title.notna()
    out.loc[fill, "energy_class"] = from_title[fill]
    source[fill] = "title"
    out["energy_source"] = source
    for col in LABEL_FIELDS[1:]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out
