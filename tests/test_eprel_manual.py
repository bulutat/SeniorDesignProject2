import pandas as pd
import pytest

from greenchoice.collect.eprel_manual import load_manual_eprel
from greenchoice.config import SAMPLE_DIR
from greenchoice.pipeline import build
from greenchoice.preprocess.matching import merge_eprel

HEADER = ("model_code,product_group,energy_class,energy_kwh_per_year,energy_kwh_per_100_cycles,"
          "water_l_per_cycle,noise_db,eprel_url,collected_on,note")
URL = "https://eprel.ec.europa.eu/screen/product/refrigeratingappliances2019/1"


def write_csv(tmp_path, *rows, header=HEADER):
    path = tmp_path / "eprel_manual.csv"
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return path


def test_loads_and_normalizes_values(tmp_path):
    path = write_csv(tmp_path, f"KZ-NF480C,refrigeratingappliances2019, c ,\"182,5\",,,35,{URL},,")
    out = load_manual_eprel(path)
    assert out.loc[0, "model_code"] == "KZ-NF480C"
    assert out.loc[0, "energy_class"] == "C"
    assert out.loc[0, "energy_kwh_per_year"] == pytest.approx(182.5)
    assert out.loc[0, "noise_db"] == pytest.approx(35.0)
    assert pd.isna(out.loc[0, "water_l_per_cycle"])


def test_blank_numeric_fields_stay_missing(tmp_path):
    path = write_csv(tmp_path, f"X-1,g,B,,,,,{URL},,")
    out = load_manual_eprel(path)
    assert out[["energy_kwh_per_year", "noise_db"]].isna().all().all()


@pytest.mark.parametrize("energy_class", ["A++", "H", ""])
def test_rejects_invalid_or_missing_energy_class(tmp_path, energy_class):
    path = write_csv(tmp_path, f"X-1,g,{energy_class},100,,,,{URL},,")
    with pytest.raises(ValueError, match="row 2"):
        load_manual_eprel(path)


def test_rejects_value_without_eprel_source_url(tmp_path):
    path = write_csv(tmp_path, "X-1,g,C,100,,,,https://example.com/x,,")
    with pytest.raises(ValueError, match="eprel_url"):
        load_manual_eprel(path)


@pytest.mark.parametrize("bad", ["abc", "-5", "1.234,5"])
def test_rejects_bad_numbers(tmp_path, bad):
    path = write_csv(tmp_path, f"X-1,g,C,\"{bad}\",,,,{URL},,")
    with pytest.raises(ValueError, match="energy_kwh_per_year"):
        load_manual_eprel(path)


def test_conflicting_duplicates_fail_identical_ones_collapse(tmp_path):
    same = write_csv(tmp_path, f"KZ-NF480C,g,C,182,,,,{URL},,", f"kz nf480c,g,C,182,,,,{URL},,")
    assert len(load_manual_eprel(same)) == 1
    clash = write_csv(tmp_path, f"KZ-NF480C,g,C,182,,,,{URL},,", f"KZNF480C,g,D,182,,,,{URL},,")
    with pytest.raises(ValueError, match="conflicting"):
        load_manual_eprel(clash)


def test_missing_required_column_fails(tmp_path):
    path = write_csv(tmp_path, "X-1,C", header="model_code,energy_class")
    with pytest.raises(ValueError, match="eprel_url"):
        load_manual_eprel(path)


def test_output_feeds_merge_eprel(tmp_path):
    path = write_csv(tmp_path, f"KZ-NF480C,g,C,182,,,,{URL},,")
    products = pd.DataFrame({"product_id": ["p1", "p2"], "model_code": ["KZNF480C", "ZZ-9"],
                             "energy_class": [None, "D"], "energy_kwh_per_year": [None, 250.0]})
    out = merge_eprel(products, load_manual_eprel(path))
    assert out["eprel_matched"].tolist() == [True, False]
    assert out["energy_kwh_per_year"].tolist() == [182.0, 250.0]


def test_pipeline_accepts_manual_eprel_file(tmp_path):
    # Synthetic values for a synthetic sample product (s-rf-01, model KZ-NF480C)
    path = write_csv(tmp_path, f"KZ-NF480C,g,B,150,,,,{URL},,")
    summary = build(SAMPLE_DIR, tmp_path / "test.db", eprel_csv=path)
    assert summary["eprel_matched"] == 1
