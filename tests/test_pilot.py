import pandas as pd
import pytest

from greenchoice.collect.pilot import load_pilot_list, pilot_report
from greenchoice.contracts import PRODUCT_COLUMNS
from greenchoice.pipeline import main

HEADER = ",".join(PRODUCT_COLUMNS)


def row(product_id="ty-1", source="trendyol", url="https://example.com/u/1", category="refrigerator",
        model_code="KZ-1", name="Test product", price="12.499,90 TL", energy_class="C", **extra):
    values = dict.fromkeys(PRODUCT_COLUMNS, "")
    values.update(product_id=product_id, source=source, url=url, category=category,
                  model_code=model_code, name=name, price_tl=price, energy_class=energy_class)
    values.update(extra)
    return ",".join(f'"{values[c]}"' for c in PRODUCT_COLUMNS)


def write_csv(tmp_path, *rows, header=HEADER, name="pilot.csv"):
    path = tmp_path / name
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


def test_loads_and_cleans_values(tmp_path):
    out = load_pilot_list(write_csv(tmp_path, row(), row("ty-2", url="https://example.com/u/2",
                                                         energy_class="A++")))
    assert out["price_tl"].tolist() == [12499.9, 12499.9]
    assert out.loc[0, "energy_class"] == "C"
    assert pd.isna(out.loc[1, "energy_class"])  # old A+++ scale is not mapped to A-G
    assert out["energy_class_raw"].tolist() == ["C", "A++"]


@pytest.mark.parametrize("bad_row,message", [
    (row(product_id=""), "row 2.*product_id"),
    (row(product_id="123"), "row 2.*product_id"),
    (row(category="toaster"), "row 2.*category"),
    (row(url="http://example.com/x"), "row 2.*url"),
    (row(model_code=" "), "row 2.*model_code"),
])
def test_rejects_bad_rows(tmp_path, bad_row, message):
    with pytest.raises(ValueError, match=message):
        load_pilot_list(write_csv(tmp_path, bad_row))


@pytest.mark.parametrize("field,value", [
    ("capacity", "10.0 kg"), ("rating_avg", "4 nokta 6"), ("rating_count", "107 adet"),
    ("rating_avg", "6"), ("price_tl", "pahalı"), ("noise_db", "-3"),
    ("rating_avg", "0"),       # 0 means "no ratings yet": leave the cell empty instead
    ("price_tl", "42.218"),    # thousands separator read as a decimal point: 42.2 TL
    ("price_tl", "500"),       # no refrigerator or washing machine costs less than 1000 TL
])
def test_rejects_text_or_out_of_range_numbers_instead_of_dropping_them(tmp_path, field, value):
    with pytest.raises(ValueError, match=f"row 2.*{field}"):
        load_pilot_list(write_csv(tmp_path, row(**{field: value})))


def test_accepts_decimal_comma_in_numeric_fields(tmp_path):
    out = load_pilot_list(write_csv(tmp_path, row(rating_avg="4,6", capacity="10")))
    assert out.loc[0, "rating_avg"] == pytest.approx(4.6)
    assert out.loc[0, "capacity"] == pytest.approx(10.0)


def test_rejects_duplicate_id_and_url(tmp_path):
    dup_id = write_csv(tmp_path, row(), row(url="https://example.com/u/2"))
    with pytest.raises(ValueError, match="duplicate product_id"):
        load_pilot_list(dup_id)
    dup_url = write_csv(tmp_path, row(), row("ty-2"))
    with pytest.raises(ValueError, match="duplicate url"):
        load_pilot_list(dup_url)


def test_missing_required_column_fails(tmp_path):
    path = write_csv(tmp_path, "ty-1,trendyol", header="product_id,source")
    with pytest.raises(ValueError, match="url"):
        load_pilot_list(path)


def test_report_counts_and_eprel_coverage():
    products = pd.DataFrame({
        "category": ["refrigerator", "refrigerator", "washing_machine"],
        "model_code": ["KZ-NF480C", "AY-500D", "KP-9014A"],
    })
    eprel = pd.DataFrame({"model_code": ["kz nf480c"]})
    rep = pilot_report(products, eprel, target_per_category=2)
    assert rep["per_category"] == {"refrigerator": 2, "washing_machine": 1}
    assert rep["below_target"] == ["washing_machine"]
    assert rep["eprel_matched"] == 1
    assert rep["eprel_missing"] == ["AY-500D", "KP-9014A"]
    assert pilot_report(products)["eprel_matched"] is None


def test_cli_check_pilot_reports_a_bad_row_without_a_traceback(tmp_path):
    pilot = write_csv(tmp_path, row(price="42.218"))
    with pytest.raises(SystemExit, match="row 2.*price_tl"):
        main(["check-pilot", "--products", str(pilot)])


def test_cli_check_pilot_prints_report_and_writes_handoff(tmp_path, capsys):
    pilot = write_csv(tmp_path, row(), row("ty-2", url="https://example.com/u/2", model_code="KZ-2"))
    eprel = tmp_path / "eprel.csv"
    eprel.write_text("model_code,energy_class,eprel_url\n"
                     "KZ-1,C,https://eprel.ec.europa.eu/screen/product/x/1\n", encoding="utf-8")
    out = tmp_path / "handoff.csv"
    main(["check-pilot", "--products", str(pilot), "--eprel", str(eprel), "--out", str(out)])
    printed = capsys.readouterr().out
    assert '"refrigerator": 2' in printed and '"eprel_matched": 1' in printed
    handoff = pd.read_csv(out)
    assert list(handoff.columns) == ["product_id", "url", "category"]
    assert handoff["product_id"].tolist() == ["ty-1", "ty-2"]
