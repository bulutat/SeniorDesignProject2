import datetime
import json
from pathlib import Path

import pandas as pd
import pytest
from openpyxl import load_workbook

from greenchoice.collect.eprel_manual import load_manual_eprel
from greenchoice.collect.pilot import load_pilot_list, pilot_report
from greenchoice.collect.sheets import build_template, export_csvs
from greenchoice.collect.workbook_append import append_selection, load_records
from greenchoice.pipeline import main

EPREL = "https://eprel.ec.europa.eu/screen/product"


def record(model, rid, category="washing_machine", **extra):
    base = {"model_code": model, "store_codes": [], "category": category,
            "group": "washingmachines2019" if category == "washing_machine" else "refrigeratingappliances2019",
            "record_id": rid, "capacity": 9, "water_l_per_cycle": 50, "energy_kwh_per_100_cycles": 49,
            "energy_kwh_per_year": None, "noise_db": 71, "energy_class": "A", "off_market": False,
            "collected_on": "2026-11-02"}
    return base | extra


def selected(pid, category, codes, name="Test", brand="Bosch", count=100):
    return {"product_id": pid, "source": "hepsiburada", "url": f"https://www.hepsiburada.com/{pid}",
            "category": category, "brand": brand, "name": name, "price_tl": 30000.0, "rating_avg": 4.5,
            "rating_count": count, "model_codes": codes, "has_model_code": bool(codes)}


@pytest.fixture
def files(tmp_path):
    base = tmp_path / "base.xlsx"
    build_template(base)
    wb = load_workbook(base)
    wb["EPREL"].append([None] * 0)  # keep the hint row intact; data starts in row 3
    wb["EPREL"].cell(3, 1, "OLD-1")  # a record that is already in the workbook
    for col, val in zip(range(2, 9), ["washingmachines2019", "A", None, 50, 40, 70, f"{EPREL}/x/1"], strict=True):
        wb["EPREL"].cell(3, col, val)
    wb.save(base)
    records = [
        record("WGA252Z0TR", 111, off_market=True),
        record("WW90CGC04DAE", 222, store_codes=["WW90CGC04DAEAH"], capacity=9),
        record("OLD-1", 333),
        record("KGN55CIE0N", 444, category="refrigerator", capacity=483, energy_kwh_per_100_cycles=None,
               water_l_per_cycle=None, energy_kwh_per_year=261, noise_db=40, energy_class="E"),
    ]
    (tmp_path / "records.json").write_text(json.dumps(records), encoding="utf-8")
    rows = [
        selected("hb-1", "washing_machine", "WGA252Z0TR | 1200"),
        selected("hb-2", "washing_machine", "WW90CGC04DAEAH"),
        selected("hb-3", "washing_machine", "OLD-1"),
        selected("hb-4", "refrigerator", "KGN55CIE0N"),
        selected("hb-5", "washing_machine", "UNKNOWN123"),
        selected("hb-6", "washing_machine", ""),
    ]
    pd.DataFrame(rows).to_csv(tmp_path / "selection.csv", index=False)
    return tmp_path


def run(files):
    out = files / "out.xlsx"
    summary = append_selection(files / "base.xlsx", files / "selection.csv", files / "records.json", out)
    return out, summary


def test_products_are_appended_with_the_eprel_identifier_and_capacity(files):
    out, summary = run(files)
    ws = load_workbook(out)["Ürünler"]
    rows = {ws.cell(r, 1).value: [c.value for c in ws[r]] for r in range(3, 12) if ws.cell(r, 1).value}
    assert rows["hb-1"][5] == "WGA252Z0TR" and rows["hb-1"][9] == 9  # model_code, capacity from the record
    assert rows["hb-2"][5] == "WW90CGC04DAE"                        # store code ...AH -> EPREL identifier
    assert rows["hb-4"][3] == "buzdolabı" and rows["hb-4"][9] == 483
    assert rows["hb-5"][5] == "UNKNOWN123" and rows["hb-5"][9] is None  # code kept, no record
    assert rows["hb-6"][5] is None                                      # no code in the title
    assert summary["products"] == 6 and summary["matched"] == 4
    assert summary["unmatched_with_code"] == 1 and summary["no_code"] == 1


def test_only_records_missing_from_the_workbook_are_added_with_notes(files):
    out, summary = run(files)
    ws = load_workbook(out)["EPREL"]
    models = [ws.cell(r, 1).value for r in range(3, 12) if ws.cell(r, 1).value]
    assert models == ["OLD-1", "WGA252Z0TR", "WW90CGC04DAE", "KGN55CIE0N"]  # OLD-1 is not duplicated
    assert summary["eprel_rows_added"] == 3
    notes = {ws.cell(r, 1).value: ws.cell(r, 10).value for r in range(3, 12)}
    assert "artık satılmıyor" in notes["WGA252Z0TR"]
    assert "WW90CGC04DAEAH" in notes["WW90CGC04DAE"]
    assert "Toplam hacim 483 L" in notes["KGN55CIE0N"]
    assert ws.cell(4, 9).value == datetime.datetime(2026, 11, 2)


def test_the_result_passes_the_real_loaders_and_reports_the_match_rate(files):
    out, _ = run(files)
    paths = export_csvs(out, files / "csv")
    products = load_pilot_list(paths["pilot"])
    eprel = load_manual_eprel(paths["eprel"])
    report = pilot_report(products, eprel)
    assert len(products) == 6 and report["eprel_matched"] == 4 and report["no_model_code"] == 1
    assert report["eprel_missing"] == ["UNKNOWN123"]


def test_products_already_in_the_workbook_are_not_added_twice(files):
    out, _ = run(files)
    again = files / "again.xlsx"
    summary = append_selection(out, files / "selection.csv", files / "records.json", again)
    assert summary["products"] == 0 and summary["skipped_existing"] == 6 and summary["eprel_rows_added"] == 0


def test_a_record_with_an_invalid_energy_class_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([record("X-1", 1, energy_class="A++")]), encoding="utf-8")
    with pytest.raises(ValueError, match="energy_class"):
        load_records(bad)


def test_duplicate_eprel_identifiers_are_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([record("X-1", 1), record("x 1", 2)]), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_records(bad)


def test_committed_eprel_records_pass_the_strict_loader():
    path = Path(__file__).parents[1] / "data" / "toplanan" / "eprel_kayitlari.json"
    records = load_records(path)
    assert len(records) == 22 and sum(r["category"] == "refrigerator" for r in records) == 8
    assert all(r["collected_on"] >= "2026-10-30" for r in records)


def test_cli_refuses_to_overwrite_the_base_workbook(files):
    with pytest.raises(SystemExit, match="differ"):
        main(["append-selection", "--base", str(files / "base.xlsx"), "--selection", str(files / "selection.csv"),
              "--records", str(files / "records.json"), "--out", str(files / "base.xlsx")])


def test_cli_appends_and_prints_the_summary(files, capsys):
    out = files / "cli.xlsx"
    main(["append-selection", "--base", str(files / "base.xlsx"), "--selection", str(files / "selection.csv"),
          "--records", str(files / "records.json"), "--out", str(out)])
    assert out.exists() and json.loads(capsys.readouterr().out)["products"] == 6
