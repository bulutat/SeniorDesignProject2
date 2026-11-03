"""Appends selected products (select-candidates output) and the hand-read EPREL records to a
copy of the data collection workbook. The base workbook is never changed; a new file is written.

EPREL values are never guessed here: they come from a records file that a person filled by
reading the EPREL record pages (`data/toplanan/eprel_kayitlari.json`).
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from greenchoice.collect.sheets import (
    FIRST_DATA_ROW,
    SHEET_EPREL,
    SHEET_PRODUCTS,
    format_sheet,
)
from greenchoice.collect.sheets_layout import CATEGORY_LABELS, EPREL_COLUMNS, PILOT_COLUMNS

EPREL_SCREEN = "https://eprel.ec.europa.eu/screen/product"
GROUPS = {"washing_machine": "washingmachines2019", "refrigerator": "refrigeratingappliances2019"}
LABEL_OF = {value: label for label, value in CATEGORY_LABELS.items()}
OLD_MODEL_NOTE = "EPREL notu: model AB pazarında artık satılmıyor, mağazalarda stok bitene kadar bulunabilir."
RECORD_KEYS = {"model_code", "store_codes", "category", "group", "record_id", "capacity", "water_l_per_cycle",
               "energy_kwh_per_100_cycles", "energy_kwh_per_year", "noise_db", "energy_class", "off_market",
               "collected_on"}
SELECTION_KEYS = {"product_id", "source", "url", "category", "brand", "name", "price_tl", "rating_avg",
                  "rating_count", "model_codes"}


def _key(code: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", code.upper())


def load_records(path: Path) -> list[dict]:
    """Strict loader: a malformed record stops the run with its position, nothing is repaired."""
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    seen: dict[str, str] = {}
    for n, rec in enumerate(records, start=1):
        where = f"{path}: record {n}"
        if set(rec) != RECORD_KEYS:
            raise ValueError(f"{where}: keys differ from the expected ones: {sorted(set(rec) ^ RECORD_KEYS)}")
        if rec["category"] not in GROUPS or rec["group"] != GROUPS[rec["category"]]:
            raise ValueError(f"{where}: category/group mismatch ({rec['category']}, {rec['group']})")
        if rec["energy_class"] not in tuple("ABCDEFG"):
            raise ValueError(f"{where}: energy_class must be one of A-G, got {rec['energy_class']!r}")
        if not isinstance(rec["record_id"], int) or not rec["model_code"]:
            raise ValueError(f"{where}: record_id must be an integer and model_code must not be empty")
        datetime.date.fromisoformat(rec["collected_on"])
        for code in [rec["model_code"], *rec["store_codes"]]:
            if _key(code) in seen:
                raise ValueError(f"{where}: duplicate identifier {code!r} (also used by {seen[_key(code)]})")
            seen[_key(code)] = rec["model_code"]
    return records


def _first_empty_row(ws, ncols: int) -> int:
    row = FIRST_DATA_ROW
    while any(ws.cell(row, c).value not in (None, "") for c in range(1, ncols + 1)):
        row += 1
    return row


def _put(ws, columns, row: int, values: dict) -> None:
    for i, col in enumerate(columns, start=1):
        ws.cell(row, i).value = values.get(col.name)


def _clean(value):
    return None if pd.isna(value) else value


def _read_selection(path: Path) -> list[dict]:
    frame = pd.read_csv(path)
    missing = SELECTION_KEYS - set(frame.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    rows = [{k: _clean(v) for k, v in row.items()} for row in frame.to_dict("records")]
    for n, row in enumerate(rows, start=2):
        if row["category"] not in LABEL_OF:
            raise ValueError(f"{path}: row {n}: unknown category {row['category']!r}")
    return rows


def _eprel_values(rec: dict) -> dict | None:
    """Sheet values of a record, or None when the record carries no energy value to write."""
    if rec["category"] == "washing_machine":
        keys = ("energy_kwh_per_100_cycles", "water_l_per_cycle")
    else:
        keys = ("energy_kwh_per_year",)
    if rec[keys[0]] is None:
        return None
    return {k: rec[k] for k in keys} | {"noise_db": rec["noise_db"], "energy_class": rec["energy_class"]}


def _eprel_note(rec: dict, store_code: str | None) -> str | None:
    notes = []
    if store_code and _key(store_code) != _key(rec["model_code"]):
        notes.append(f"Mağaza kodu {store_code}, EPREL kodu eksiz/farklı.")
    if rec["off_market"]:
        notes.append(OLD_MODEL_NOTE)
    if rec["category"] == "refrigerator":
        notes.append(f"Toplam hacim {rec['capacity']} L (EPREL).")
    return " ".join(notes) or None


def append_selection(base: Path, selection: Path, records: Path, out: Path) -> dict:
    recs = load_records(records)
    by_code = {_key(c): rec for rec in recs for c in [rec["model_code"], *rec["store_codes"]]}
    chosen = _read_selection(selection)
    wb = load_workbook(base)
    products, eprel = wb[SHEET_PRODUCTS], wb[SHEET_EPREL]
    p_row, e_row = _first_empty_row(products, len(PILOT_COLUMNS)), _first_empty_row(eprel, len(EPREL_COLUMNS))
    known_ids = {products.cell(r, 1).value for r in range(FIRST_DATA_ROW, p_row)}
    in_sheet = {_key(str(eprel.cell(r, 1).value)) for r in range(FIRST_DATA_ROW, e_row)}
    summary = {"products": 0, "matched": 0, "unmatched_with_code": 0, "no_code": 0,
               "skipped_existing": 0, "eprel_rows_added": 0}
    for row in chosen:
        if row["product_id"] in known_ids:
            summary["skipped_existing"] += 1
            continue
        codes = row["model_codes"].split(" | ") if row["model_codes"] else []
        store_code = codes[0].upper() if codes else None
        rec = by_code.get(_key(store_code)) if store_code else None
        if rec and rec["category"] != row["category"]:
            raise ValueError(f"{row['product_id']}: category {row['category']} but EPREL record "
                             f"{rec['model_code']} is {rec['category']}")
        _put(products, PILOT_COLUMNS, p_row, {
            **{k: row[k] for k in ("product_id", "source", "url", "brand", "name", "price_tl",
                                   "rating_avg", "rating_count")},
            "category": LABEL_OF[row["category"]], "model_code": rec["model_code"] if rec else store_code,
            "capacity": rec["capacity"] if rec else None})
        p_row += 1
        summary["products"] += 1
        summary["matched" if rec else "unmatched_with_code" if store_code else "no_code"] += 1
        values = _eprel_values(rec) if rec else None
        if values and _key(rec["model_code"]) not in in_sheet:
            in_sheet.add(_key(rec["model_code"]))
            _put(eprel, EPREL_COLUMNS, e_row, values | {
                "model_code": rec["model_code"], "product_group": rec["group"],
                "eprel_url": f"{EPREL_SCREEN}/{rec['group']}/{rec['record_id']}",
                "collected_on": datetime.date.fromisoformat(rec["collected_on"]),
                "note": _eprel_note(rec, store_code)})
            e_row += 1
            summary["eprel_rows_added"] += 1
    format_sheet(products, PILOT_COLUMNS)
    format_sheet(eprel, EPREL_COLUMNS)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return summary
