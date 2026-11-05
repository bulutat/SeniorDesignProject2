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
from greenchoice.preprocess.products import clean_products, parse_price

REQUIRED_COLUMNS = ["product_id", "source", "url", "category", "model_code", "name"]  # must exist
REQUIRED_VALUES = ["product_id", "source", "url", "category", "name"]  # model_code may be empty
PRODUCT_ID = re.compile(r"^[a-z]+-[A-Za-z0-9]+$")  # source prefix + id, e.g. "ty-123456"


def _fail(row_no: int, message: str) -> None:
    raise ValueError(f"pilot list, row {row_no}: {message}")


def _check_row(record: dict, row_no: int, categories: set[str]) -> None:
    for column in REQUIRED_VALUES:
        if not record[column].strip():
            _fail(row_no, f"{column} is empty")
    if not PRODUCT_ID.match(record["product_id"].strip()):
        _fail(row_no, f"product_id must look like 'ty-123456', got {record['product_id']!r}")
    if record["category"].strip() not in categories:
        _fail(row_no, f"category must be one of {sorted(categories)}, got {record['category']!r}")
    if not record["url"].strip().startswith("https://"):
        _fail(row_no, f"url must start with https://, got {record['url']!r}")


# Optional numeric columns: (minimum, maximum). Text that does not parse must fail loudly,
# because clean_products would otherwise turn it into an empty value without a trace.
NUMERIC_LIMITS = {
    "energy_kwh_per_year": (0, None), "energy_kwh_per_100_cycles": (0, None),
    "water_l_per_cycle": (0, None), "capacity": (0, None), "noise_db": (0, 200),
    "warranty_years": (0, 30), "rating_avg": (1, 5), "rating_count": (0, None),
}
MIN_PRICE_TL = 1000  # refrigerators and washing machines; catches "42.218" typed for 42,218 TL
WHOLE_NUMBER_COLUMNS = {"rating_count"}  # "1.197" would silently become 1.197


def _check_numbers(record: dict, row_no: int) -> dict[str, str]:
    """Validates the numeric fields; returns them with '.' as decimal separator."""
    if record["price_tl"].strip():
        price = parse_price(record["price_tl"])
        if price is None:
            _fail(row_no, f"price_tl is not a number: {record['price_tl']!r}")
        if price < MIN_PRICE_TL:
            _fail(row_no, f"price_tl {record['price_tl']!r} is below {MIN_PRICE_TL} TL; "
                          "a thousands separator may have been read as a decimal point")
    normalized = {}
    for column, (low, high) in NUMERIC_LIMITS.items():
        text = record[column].strip().replace(",", ".")
        if not text:
            continue
        try:
            value = float(text)
        except ValueError:
            _fail(row_no, f"{column} is not a number: {record[column]!r}")
        if value < low or (high is not None and value > high):
            _fail(row_no, f"{column} must be between {low} and {high or 'any'}, got {text!r}"
                          " (leave the cell empty when the value is unknown)")
        if column in WHOLE_NUMBER_COLUMNS and not value.is_integer():
            _fail(row_no, f"{column} must be a whole number, got {record[column]!r}")
        normalized[column] = text
    return normalized


def _check_unique(raw: pd.DataFrame) -> None:
    for column in ("product_id", "url"):
        dupes = raw[column].str.strip().loc[lambda s: s.duplicated()].tolist()
        if dupes:
            raise ValueError(f"pilot list: duplicate {column}: {dupes}")


def load_pilot_list(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    require_columns(raw, REQUIRED_COLUMNS, "pilot list")
    categories = set(categories_config()["categories"])
    raw = conform(raw, PRODUCT_COLUMNS)
    for i, record in enumerate(raw.to_dict("records")):
        _check_row(record, i + 2, categories)
        for column, text in _check_numbers(record, i + 2).items():
            raw.loc[i, column] = text
    _check_unique(raw)
    return clean_products(raw)


def pilot_report(products: pd.DataFrame, eprel: pd.DataFrame | None = None,
                 target_per_category: int = 10) -> dict:
    counts = products["category"].value_counts()
    per_category = {c: int(counts.get(c, 0)) for c in categories_config()["categories"]}
    keys = products["model_code"].map(normalize_model_code)
    report = {
        "per_category": per_category,
        "below_target": [c for c, n in per_category.items() if n < target_per_category],
        "no_model_code": int(keys.isna().sum()),
        "eprel_matched": None,
        "eprel_missing": None,
    }
    if eprel is not None:
        known = set(eprel["model_code"].map(normalize_model_code).dropna())
        matched = keys.isin(known)
        report["eprel_matched"] = int(matched.sum())
        report["eprel_missing"] = list(dict.fromkeys(products.loc[keys.notna() & ~matched, "model_code"]))
    return report
