"""Pilot product list (task B0.2): the hand-built list of products that Person A's review
scraper starts from, and a report on how well it is covered by EPREL data.

The list uses the products.csv contract columns (contracts.PRODUCT_COLUMNS), so the same
rows can later seed data/interim/products.csv.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from greenchoice.config import categories_config
from greenchoice.contracts import PRODUCT_COLUMNS, conform, require_columns
from greenchoice.preprocess.matching import normalize_model_code
from greenchoice.preprocess.products import clean_products

REQUIRED_COLUMNS = ["product_id", "source", "url", "category", "model_code", "name"]
PRODUCT_ID = re.compile(r"^[a-z]+-[A-Za-z0-9]+$")  # source prefix + id, e.g. "ty-123456"


def _fail(row_no: int, message: str) -> None:
    raise ValueError(f"pilot list, row {row_no}: {message}")


def _check_row(record: dict, row_no: int, categories: set[str]) -> None:
    for column in REQUIRED_COLUMNS:
        if not record[column].strip():
            _fail(row_no, f"{column} is empty")
    if not PRODUCT_ID.match(record["product_id"].strip()):
        _fail(row_no, f"product_id must look like 'ty-123456', got {record['product_id']!r}")
    if record["category"].strip() not in categories:
        _fail(row_no, f"category must be one of {sorted(categories)}, got {record['category']!r}")
    if not record["url"].strip().startswith("https://"):
        _fail(row_no, f"url must start with https://, got {record['url']!r}")


def _check_unique(raw: pd.DataFrame) -> None:
    for column in ("product_id", "url"):
        dupes = raw[column].str.strip().loc[lambda s: s.duplicated()].tolist()
        if dupes:
            raise ValueError(f"pilot list: duplicate {column}: {dupes}")


def load_pilot_list(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    require_columns(raw, REQUIRED_COLUMNS, "pilot list")
    categories = set(categories_config()["categories"])
    for i, record in enumerate(raw.to_dict("records")):
        _check_row(record, i + 2, categories)
    _check_unique(raw)
    return clean_products(conform(raw, PRODUCT_COLUMNS))


def pilot_report(products: pd.DataFrame, eprel: pd.DataFrame | None = None,
                 target_per_category: int = 10) -> dict:
    counts = products["category"].value_counts()
    per_category = {c: int(counts.get(c, 0)) for c in categories_config()["categories"]}
    report = {
        "per_category": per_category,
        "below_target": [c for c, n in per_category.items() if n < target_per_category],
        "eprel_matched": None,
        "eprel_missing": None,
    }
    if eprel is not None:
        known = set(eprel["model_code"].map(normalize_model_code).dropna())
        keys = products["model_code"].map(normalize_model_code)
        report["eprel_matched"] = int(keys.isin(known).sum())
        report["eprel_missing"] = list(dict.fromkeys(products.loc[~keys.isin(known), "model_code"]))
    return report
