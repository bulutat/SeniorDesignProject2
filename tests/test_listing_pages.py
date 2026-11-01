import json

import pytest

from greenchoice.collect.listing_pages import import_listings, parse_listing
from greenchoice.pipeline import main

HB = "https://www.hepsiburada.com"


def card(n, title, code, price="28.493,10", rating="Ürün puanı 4.7, 137 değerlendirme", path=None):
    """Synthetic card with the structure seen in saved Hepsiburada listing pages (2026-11-02)."""
    path = path or f"{title.lower().replace(' ', '-')}-pm-{code}"
    rating_html = f"<span>{rating}</span>" if rating else ""
    return (f'<div class="productCard-module_productCardRoot__Yf7qs">'
            f'<a href="{HB}/{path}?magaza=Hepsiburada" title="{title}"></a>'
            f'<h2 data-test-id="title-{n}">{title}</h2>{rating_html}'
            f'<button aria-label="Sepete ekle, fiyat: {price} TL, {title}"></button></div>')


def page(*cards, ads="", footer=""):
    return ("<html><head><link rel=\"canonical\" href=\"https://www.hepsiburada.com/ara?q=x\">"
            f"</head><body>{ads}{''.join(cards)}{footer}</body></html>")


WASHER = card(1, "Bosch WGA25203TR 10 kg 1200 Devir Çamaşır Makinesi", "HBC0000E8D2XF")
FRIDGE = card(2, "Siemens KG55NCWE0N Kombi No Frost Buzdolabı", "HBC000039FZBL", price="47.025,00",
              rating="Ürün puanı 4.5, 1.197 değerlendirme")
AD = ('<article class="horizontalProductCard-module_article__mzi-M">'
      f'<a href="{HB}/samsung-bulasik-makinesi-p-HBCV00006JOJ6K" title="Samsung Bulaşık Makinesi"></a></article>')


def test_parses_title_url_price_rating_and_counts():
    items, report = parse_listing(page(WASHER, FRIDGE, ads=AD), "bosch.html")
    washer, fridge = items
    assert washer["product_id"] == "hb-HBC0000E8D2XF"
    assert washer["url"] == f"{HB}/bosch-wga25203tr-10-kg-1200-devir-çamaşır-makinesi-pm-HBC0000E8D2XF"
    assert washer["price_tl"] == pytest.approx(28493.10)
    assert (washer["rating_avg"], washer["rating_count"]) == (4.7, 137)
    assert washer["category"] == "washing_machine" and fridge["category"] == "refrigerator"
    assert fridge["rating_count"] == 1197  # Turkish thousands separator
    assert "WGA25203TR" in washer["model_code_candidates"]
    assert report["cards"] == 2 and report["ads_skipped"] == 1


def test_non_target_products_are_counted_not_returned():
    dryer = card(3, "Arçelik Kurutmalı Çamaşır Makinesi 9 kg", "HBC0000DRYER")
    dishwasher = card(4, "Bosch Bulaşık Makinesi 6 Programlı", "HBC00000DISH1")
    items, report = parse_listing(page(WASHER, dryer, dishwasher), "x.html")
    assert [i["product_id"] for i in items] == ["hb-HBC0000E8D2XF"]
    assert report["skipped_other_category"] == 2


def test_product_numbers_that_do_not_start_with_hb_are_accepted():
    """Seen on a real page: .../buzdolabi-...-pm-mtsamrt46k6000s8tr (merchant-style number)."""
    odd = card(7, "Samsung RT46K6000S8/TR No-Frost Çift Kapılı Buzdolabı 468 lt", "mtsamrt46k6000s8tr",
               price="56.998")
    items, _ = parse_listing(page(odd), "x.html")
    assert items[0]["product_id"] == "hb-mtsamrt46k6000s8tr"
    assert "RT46K6000S8" in items[0]["model_code_candidates"]


def test_prices_without_decimals_keep_their_thousands_separator():
    """Real pages show both "28.493,10" and "47.930"; the dot is always a thousands separator."""
    items, _ = parse_listing(page(card(1, "Bosch WGA142Z0TR 9 kg Çamaşır Makinesi", "HBC0000NODEC",
                                       price="47.930")), "x.html")
    assert items[0]["price_tl"] == pytest.approx(47930.0)


@pytest.mark.parametrize("title,category", [
    ("Samsung RB58DS75EWW/TR 580 Lt Alttan Donduruculu İkili Soğutma No-Frost Buzdolabı", "refrigerator"),
    ("Bosch WGB264A0TR Serie 8, 11 Kg, Maks. 1400 Dev./dak. 20+ Program Sayısı Çamaşır Makinesi",
     "washing_machine"),
    ("Arçelik 9100 DMX 9 Kg Çamaşır Makinesi Enerji Sınıfı A+++ 1000 Devir", "washing_machine"),
])
def test_feature_words_that_look_like_bundle_marks_do_not_drop_real_appliances(title, category):
    """"İkili Soğutma", "20+ Program" and "A+++" were wrongly read as bundles on real pages."""
    items, report = parse_listing(page(card(6, title, "HBC0000REAL01", price="52.199")), "x.html")
    assert [i["category"] for i in items] == [category] and report["skipped_other_category"] == 0


@pytest.mark.parametrize("title,price", [
    ("Bosch WGK264ZRTR ÇAMAŞIR MK.+WQJ2520RTR KURUTMA MK.", "94.499"),
    ("Arçelik 10121 10 kg Çamaşır Makinesi + A 710 B Bulaşık Makinesi Paketi", "44.188"),
])
def test_bundles_written_with_a_plus_sign_are_still_skipped(title, price):
    items, report = parse_listing(page(card(6, title, "HBC0000BNDL02", price=price)), "x.html")
    assert items == [] and report["skipped_other_category"] == 1


@pytest.mark.parametrize("title,price", [
    ("Lg 3'lü Beyaz Eşya Paketi (Buzdolabı + 9 kg Çamaşır Makinesi + Bulaşık Makinesi)", "160.198,20"),
    ("Samsung Buzdolabı + Çamaşır Makinesi Seti", "90.000,00"),
    ("Çamaşır Makinesi Filtresi ve Temizleyici", "1.628"),
])
def test_bundles_and_accessories_are_not_appliances(title, price):
    items, report = parse_listing(page(WASHER, card(5, title, "HBC0000BUNDLE", price=price)), "x.html")
    assert [i["product_id"] for i in items] == ["hb-HBC0000E8D2XF"]
    assert report["skipped_other_category"] == 1


def test_card_without_ratings_keeps_empty_rating_fields():
    items, _ = parse_listing(page(card(1, "Beko CM 10121 10 kg Çamaşır Makinesi", "HBC0000NEW01",
                                       rating=None)), "x.html")
    assert items[0]["rating_avg"] is None and items[0]["rating_count"] is None


def test_page_without_product_cards_fails_with_the_file_name():
    with pytest.raises(ValueError, match="bozuk.html"):
        parse_listing("<html><body>captcha</body></html>", "bozuk.html")


def test_card_missing_its_price_fails_instead_of_being_dropped():
    broken = WASHER.replace("Sepete ekle, fiyat: 28.493,10 TL, ", "")
    with pytest.raises(ValueError, match="fiyat"):
        parse_listing(page(broken), "x.html")


def test_import_keeps_the_best_listing_per_model_and_reports_per_file(tmp_path):
    duplicate = card(1, "Bosch WGA25203TR 10 kg Çamaşır Makinesi", "HBC00000OTHER",
                     rating="Ürün puanı 4.6, 20 değerlendirme")
    (tmp_path / "a.html").write_text(page(WASHER, FRIDGE), encoding="utf-8")
    (tmp_path / "b.html").write_text(page(duplicate), encoding="utf-8")
    table, report = import_listings(tmp_path)
    assert set(table["product_id"]) == {"hb-HBC0000E8D2XF", "hb-HBC000039FZBL"}
    assert table.set_index("product_id").loc["hb-HBC0000E8D2XF", "rating_count"] == 137
    assert report["files"]["a.html"]["products"] == 2 and report["duplicates_dropped"] == 1


def test_empty_folder_fails(tmp_path):
    with pytest.raises(ValueError, match="html dosyası yok"):
        import_listings(tmp_path)


def test_cli_writes_the_candidate_table(tmp_path, capsys):
    (tmp_path / "a.html").write_text(page(WASHER, FRIDGE), encoding="utf-8")
    out = tmp_path / "out" / "aday.csv"
    main(["import-listings", "--pages", str(tmp_path), "--out", str(out)])
    assert out.exists()
    assert json.loads(capsys.readouterr().out)["candidates"] == 2
