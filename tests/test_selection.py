import json

import pandas as pd
import pytest

from greenchoice.collect.selection import pool_from_sources, select_products
from greenchoice.pipeline import main


def row(pid, brand, count, model="", category="washing_machine", source="hepsiburada"):
    return {"product_id": pid, "source": source, "url": f"https://x/{pid}", "category": category,
            "brand": brand, "name": f"{brand} {model} test", "price_tl": 30000.0, "rating_avg": 4.5,
            "rating_count": count, "model_codes": [model] if model else []}


def existing(*models, brand="Bosch", category="washing_machine"):
    return pd.DataFrame([{"product_id": f"e{i}", "category": category, "brand": brand, "model_code": m}
                         for i, m in enumerate(models)])


def pick(pool, have, **kw):
    kw.setdefault("target", 3)
    kw.setdefault("brand_cap", 10)
    return select_products(pd.DataFrame(pool), have, **kw)


def test_takes_the_most_rated_products_and_skips_those_below_the_minimum():
    pool = [row("a", "Samsung", 500, "AAA111"), row("b", "LG", 40, "BBB222"),
            row("c", "Beko", 10, "CCC333"), row("d", "Bosch", 300, "DDD444")]
    chosen, report = pick(pool, existing(), target=3)
    assert chosen["product_id"].tolist() == ["a", "d", "b"]  # "c" has fewer than 30 ratings
    assert report["washing_machine"]["shortfall"] == 0


def test_models_we_already_hold_are_excluded_and_count_toward_the_target():
    pool = [row("a", "Bosch", 900, "WGA25203TR"), row("b", "LG", 100, "BBB222"),
            row("c", "Samsung", 90, "CCC333")]
    chosen, report = pick(pool, existing("wga25203tr"), target=3)  # case-insensitive
    assert chosen["product_id"].tolist() == ["b", "c"]
    assert report["washing_machine"] == {"have": 1, "need": 2, "chosen": 2, "shortfall": 0}


def test_brand_cap_keeps_the_sample_diverse_and_existing_products_count():
    pool = [row(f"s{i}", "Samsung", 1000 - i, f"SAM{i:03d}") for i in range(5)] + [row("l", "LG", 50, "LLL111")]
    chosen, _ = pick(pool, existing("X1", "X2", brand="Samsung"), target=5, brand_cap=3)
    assert chosen["brand"].tolist() == ["Samsung", "LG"]  # two Samsungs held, only one more fits


def test_same_model_on_two_sites_keeps_the_entry_with_more_ratings():
    pool = [row("h1", "Bosch", 80, "KDN55NWE0N"),
            row("t1", "Bosch", 206, "kdn55nwe0n", source="trendyol")]
    chosen, _ = pick(pool, existing(), target=2)
    assert chosen["product_id"].tolist() == ["t1"]


@pytest.mark.parametrize("name", [
    "Kumtel 93L Beyaz Büro Tipi Buzdolabı HMB-110",
    "KUMTEL 87L MİNİ BUZDOLABI BEYAZ HTMF-90EW",
    "Altus Al 305 Be E Enerji Sınıfı 85 L Tezgah Altı Buzdolabı",
    "Vestel Otel Tipi Minibar 40 L",
])
def test_compact_fridges_are_not_comparable_with_household_fridges(name):
    compact = {**row("c", "Kumtel", 500, "HMB110", category="refrigerator"), "name": name}
    chosen, report = pick([compact, row("h", "Bosch", 100, "KGN55CWE0N", category="refrigerator")],
                          existing(), target=2)
    assert chosen["product_id"].tolist() == ["h"]
    assert report["refrigerator"]["excluded_compact"] == 1


def test_market_suffix_variants_are_one_model_whatever_the_order():
    pool = [row("a", "Samsung", 136, "RT47CG6636WW"), row("b", "Samsung", 92, "RT47CG6636WWTR", source="trendyol"),
            row("c", "LG", 50, "LLL111")]
    chosen, _ = pick(pool, existing(), target=3)
    assert chosen["product_id"].tolist() == ["a", "c"]
    flipped = [row("a", "Samsung", 92, "RT47CG6636WW"), row("b", "Samsung", 136, "RT47CG6636WWTR")]
    assert pick(flipped, existing(), target=2)[0]["product_id"].tolist() == ["b"]


def test_codeless_products_with_the_same_title_words_are_one_model():
    """Beko CMX 10120 listed on both shops, no model code in either title."""
    a = {**row("hb", "Beko", 146), "name": "Beko CMX 10120 10 Kg Çamaşır Makinesi A Enerji Sınıfı 1200 Devir"}
    b = {**row("ty", "Beko", 132, source="trendyol"), "name": "Beko CMX 10120 Çamaşır Makinesi"}
    other = {**row("o", "Beko", 120), "name": "Beko CMXD 9100 9 Kg Çamaşır Makinesi"}
    chosen, _ = pick([a, b, other], existing(), target=3)
    assert chosen["product_id"].tolist() == ["hb", "o"]


def test_products_without_a_model_code_stay_in_the_pool():
    """Turkish-brand titles often carry no code; dropping them would bias the sample to EPREL."""
    pool = [row("a", "Arçelik", 400), row("b", "Arçelik", 300), row("c", "Bosch", 100, "BBB222")]
    chosen, _ = pick(pool, existing(), target=3)
    assert chosen["product_id"].tolist() == ["a", "b", "c"]
    assert chosen["has_model_code"].tolist() == [False, False, True]


def test_a_pool_that_is_too_small_reports_the_shortfall():
    chosen, report = pick([row("a", "LG", 100, "AAA111")], existing(), target=4)
    assert len(chosen) == 1 and report["washing_machine"]["shortfall"] == 3  # target 4, one found


def test_each_category_is_filled_separately():
    pool = [row("w", "LG", 100, "WWW111"), row("f", "LG", 100, "FFF111", category="refrigerator")]
    chosen, report = pick(pool, existing(), target=1)
    assert sorted(chosen["category"]) == ["refrigerator", "washing_machine"]
    assert set(report) == {"washing_machine", "refrigerator"}


def test_pool_from_sources_merges_listing_rows_and_trendyol_dicts():
    listings = pd.DataFrame([{
        "product_id": "hb-X1", "source": "hepsiburada", "url": "https://hb/x1", "category": "refrigerator",
        "brand_guess": "Wgk252Zstr-Bosch", "name": "Wgk252Zstr-Bosch 9 kg Çamaşır Makinesi",
        "price_tl": 40000.0, "rating_avg": 4.6, "rating_count": 50,
        "model_code_candidates": "WGK252ZSTR | 1400", "source_file": "a.html"}])
    trendyol = [{"product_id": "ty-1", "source": "trendyol", "url": "https://ty/1", "category": "refrigerator",
                 "brand": "VESTEL", "name": "Vestel NF 52111", "price_tl": 34400.0, "rating_avg": 4.6,
                 "rating_count": 264, "model_code_candidates": [], "warnings": []}]
    pool = pool_from_sources(listings, trendyol)
    assert pool["brand"].tolist() == ["Bosch", "Vestel"]  # brand found in the title, then normalised
    assert pool.loc[0, "model_codes"] == ["WGK252ZSTR", "1400"]
    assert pool.loc[1, "model_codes"] == []


def test_cli_writes_the_selection(tmp_path, capsys):
    listing = pd.DataFrame([{
        "product_id": "hb-A", "source": "hepsiburada", "url": "https://hb/a", "category": "washing_machine",
        "brand_guess": "Samsung", "name": "Samsung WW90 test", "price_tl": 30000.0, "rating_avg": 4.5,
        "rating_count": 200, "model_code_candidates": "WW90CGC04DAEAH", "source_file": "a.html"}])
    listing.to_csv(tmp_path / "listings.csv", index=False)
    existing(*[], brand="Bosch").assign(model_code=[]).to_csv(tmp_path / "pilot.csv", index=False)
    (tmp_path / "ty.json").write_text(json.dumps([]), encoding="utf-8")
    out = tmp_path / "chosen.csv"
    main(["select-candidates", "--listings", str(tmp_path / "listings.csv"), "--trendyol",
          str(tmp_path / "ty.json"), "--existing", str(tmp_path / "pilot.csv"), "--out", str(out),
          "--target", "1"])
    assert pd.read_csv(out)["product_id"].tolist() == ["hb-A"]
    assert json.loads(capsys.readouterr().out)["washing_machine"]["chosen"] == 1


def test_target_and_cap_must_be_positive():
    with pytest.raises(ValueError, match="target"):
        pick([row("a", "LG", 100, "AAA111")], existing(), target=0)
