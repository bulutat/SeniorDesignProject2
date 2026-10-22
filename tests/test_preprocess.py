import pandas as pd
import pytest

from greenchoice.preprocess.matching import merge_eprel, normalize_model_code
from greenchoice.preprocess.products import normalize_energy_class, parse_price
from greenchoice.preprocess.reviews import clean_reviews
from greenchoice.preprocess.tco import add_tco
from greenchoice.preprocess.text import normalize_text, tr_lower


def test_turkish_lowercase():
    assert tr_lower("IŞIK İĞNE") == "ışık iğne"
    assert normalize_text("  Çok   SESSİZ!!! https://x.com ") == "çok sessiz"


@pytest.mark.parametrize("raw,expected", [
    ("19.999,00 TL", 19999.0), ("12.499,90 TL", 12499.9), (24999, 24999.0), ("abc", None),
])
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected


def test_energy_class_old_scale_is_dropped():
    assert normalize_energy_class(" c ") == ("C", "C")
    assert normalize_energy_class("A++") == (None, "A++")


def test_clean_reviews_drops_spam_duplicates_and_short():
    df = pd.DataFrame({
        "review_id": ["1", "2", "3", "4"],
        "product_id": ["p", "p", "p", "p"],
        "rating": [5, 5, 1, 3],
        "text": ["Çok sessiz çalışıyor.", "Çok sessiz çalışıyor!",
                 "kötü kötü kötü kötü kötü kötü", "güzel"],
        "date": [None] * 4,
    })
    out = clean_reviews(df)
    assert out["review_id"].tolist() == ["1"]


def test_tco_refrigerator_and_washing_machine():
    cfg = {
        "defaults": {"electricity_price_tl_per_kwh": 2.0, "water_price_tl_per_m3": 10.0},
        "categories": {
            "refrigerator": {"lifetime_years": 10},
            "washing_machine": {"lifetime_years": 10, "annual_cycles": 200},
        },
    }
    df = pd.DataFrame([
        {"category": "refrigerator", "price_tl": 1000.0, "energy_kwh_per_year": 100.0,
         "energy_kwh_per_100_cycles": None, "water_l_per_cycle": None},
        {"category": "washing_machine", "price_tl": 1000.0, "energy_kwh_per_year": None,
         "energy_kwh_per_100_cycles": 50.0, "water_l_per_cycle": 50.0},
    ])
    out = add_tco(df, cfg)
    assert out["annual_kwh"].tolist() == [100.0, 100.0]
    # 1000 + 10 * (100 kWh * 2 TL) = 3000
    assert out.loc[0, "tco_tl"] == pytest.approx(3000.0)
    # 1000 + 10 * (100 * 2 + 10 m3 * 10 TL) = 4000
    assert out.loc[1, "tco_tl"] == pytest.approx(4000.0)


def test_eprel_merge_by_normalized_model_code():
    assert normalize_model_code("kz-nf 480/c") == "KZNF480C"
    products = pd.DataFrame({"product_id": ["p1", "p2"], "model_code": ["KZ-NF480C", "X-1"],
                             "energy_class": [None, "D"], "energy_kwh_per_year": [None, 250.0]})
    eprel = pd.DataFrame({"model_code": ["KZNF480C"], "energy_class": ["C"],
                          "energy_kwh_per_year": [182.0]})
    out = merge_eprel(products, eprel)
    assert out["energy_class"].tolist() == ["C", "D"]
    assert out["energy_kwh_per_year"].tolist() == [182.0, 250.0]
    assert out["eprel_matched"].tolist() == [True, False]
