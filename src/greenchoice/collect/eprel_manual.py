"""Loader for EPREL values collected by hand from public EPREL product pages.

The EPREL public API needs a key (docs/kaynak-inceleme.md), so values are typed into a CSV
while reading the product page (guide: docs/eprel-manual-toplama.md). This module checks
that file strictly, so a typing mistake fails loudly instead of reaching the scores.

The result feeds preprocess.matching.merge_eprel.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from greenchoice.contracts import require_columns
from greenchoice.preprocess.matching import EPREL_PRIORITY_FIELDS, normalize_model_code

URL_PREFIX = "https://eprel.ec.europa.eu/"
REQUIRED_COLUMNS = ["model_code", "energy_class", "eprel_url"]
NUMERIC_FIELDS = [f for f in EPREL_PRIORITY_FIELDS if f != "energy_class"]
VALID_CLASSES = set("ABCDEFG")
OUTPUT_COLUMNS = ["model_code", *EPREL_PRIORITY_FIELDS, "eprel_url"]


def _fail(row_no: int, message: str) -> None:
    raise ValueError(f"EPREL manual file, row {row_no}: {message}")


def _parse_number(raw: str, row_no: int, field: str) -> float | None:
    text = raw.strip().replace(",", ".")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        _fail(row_no, f"{field} is not a number: {raw!r}")
    if value < 0:
        _fail(row_no, f"{field} is negative: {raw!r}")
    return value


def _parse_row(record: dict, row_no: int) -> dict:
    model_code = record["model_code"].strip()
    energy_class = record["energy_class"].strip().upper()
    if energy_class not in VALID_CLASSES:
        _fail(row_no, f"energy_class must be one of A-G (2021 scale), got {energy_class!r}")
    url = record["eprel_url"].strip()
    if not url.startswith(URL_PREFIX):
        _fail(row_no, f"eprel_url must start with {URL_PREFIX}, got {url!r}")
    row = {"model_code": model_code, "energy_class": energy_class, "eprel_url": url}
    for field in NUMERIC_FIELDS:
        row[field] = _parse_number(record.get(field, ""), row_no, field)
    return row


def _collapse_duplicates(rows: list[dict]) -> list[dict]:
    kept: dict[str, dict] = {}
    for row in rows:
        key = normalize_model_code(row["model_code"])
        first = kept.setdefault(key, row)
        if first is not row and any(first[f] != row[f] for f in EPREL_PRIORITY_FIELDS):
            raise ValueError(f"EPREL manual file: conflicting values for model {row['model_code']!r}")
    return list(kept.values())


def load_manual_eprel(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    require_columns(raw, REQUIRED_COLUMNS, "eprel_manual")
    records = raw.to_dict("records")
    rows = [_parse_row(rec, i + 2) for i, rec in enumerate(records) if rec["model_code"].strip()]
    return pd.DataFrame(_collapse_duplicates(rows), columns=OUTPUT_COLUMNS)
