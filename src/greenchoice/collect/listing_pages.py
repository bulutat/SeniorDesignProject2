"""Candidate products from Hepsiburada search pages a person saved in a browser.

Hepsiburada answers automated requests with a CAPTCHA (decision 17), so nothing is fetched: this
reads local HTML only. Structure checked on 8 real saved pages on 2026-11-02: product cards are
`div.productCard-module_productCardRoot*` with the title on the link, the price in the
"Sepete ekle, fiyat: ..." label and "Ürün puanı X, N değerlendirme" text. Cards of the other class
(`horizontalProductCard`) are advertisements and are skipped and counted. A page with no cards or
a card missing its address, title or price fails with the file name instead of being skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from greenchoice.collect.model_codes import model_code_candidates
from greenchoice.preprocess.text import tr_lower

CARD = re.compile(r"^productCard-module_productCardRoot")
AD = re.compile(r"^horizontalProductCard-module_article")
PRODUCT_NUMBER = re.compile(r"-pm?-(HB[A-Za-z0-9]+)")
PRICE = re.compile(r"Sepete ekle, fiyat:\s*([\d.,]+)\s*TL")
RATING = re.compile(r"Ürün puanı\s*([\d.,]+),\s*([\d.]+)\s*değerlendirme")
COLUMNS = ["product_id", "source", "url", "category", "brand_guess", "name", "price_tl",
           "rating_avg", "rating_count", "model_code_candidates", "source_file"]
BUNDLE = re.compile(r"paket|\bset\b|\+|'l[iıuü]\b|\bikili|\büçlü")  # "3'lü Beyaz Eşya Paketi"
MIN_APPLIANCE_PRICE_TL = 5000  # filters, cleaners and other accessories that carry the same words


def _turkish_price(text: str) -> float:
    """"28.493,10" -> 28493.1 and "47.930" -> 47930.0: on these pages the dot is a thousands mark."""
    return float(text.replace(".", "").replace(",", "."))


def _category(title: str, price: float) -> str | None:
    lowered = tr_lower(title)
    if BUNDLE.search(lowered) or price < MIN_APPLIANCE_PRICE_TL:
        return None
    if "buzdolabı" in lowered:
        return "refrigerator"
    if "çamaşır makinesi" in lowered and "kurutma" not in lowered:
        return "washing_machine"
    return None  # dishwashers, dryers, washer-dryers and everything else


def _parse_card(card, name: str, index: int) -> dict:
    where = f"{name}: kart {index}"
    link = card.find("a", href=PRODUCT_NUMBER)
    if link is None:
        raise ValueError(f"{where}: ürün adresi yok")
    title = (link.get("title") or "").strip()
    if not title:
        raise ValueError(f"{where}: ürün adı yok")
    label = card.find(attrs={"aria-label": PRICE})
    if label is None:
        raise ValueError(f"{where} ({title[:40]}): fiyat okunamadı")
    price = _turkish_price(PRICE.search(label["aria-label"]).group(1))
    url = link["href"].split("?")[0]
    rating = RATING.search(card.get_text(" ", strip=True))
    return {
        "product_id": f"hb-{PRODUCT_NUMBER.findall(url)[-1]}", "source": "hepsiburada", "url": url,
        "category": _category(title, price), "brand_guess": title.split()[0], "name": title,
        "price_tl": price,
        "rating_avg": float(rating.group(1).replace(",", ".")) if rating else None,
        "rating_count": int(rating.group(2).replace(".", "")) if rating else None,
        "model_code_candidates": model_code_candidates(title), "source_file": name,
    }


def parse_listing(html: str, name: str) -> tuple[list[dict], dict]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_=CARD)
    ads = soup.find_all("article", class_=AD)
    if not cards:
        raise ValueError(f"{name}: ürün kartı bulunamadı. Sayfa 'Web Sayfası, Tamamı' olarak mı "
                         "kaydedildi, arama sonuçları yüklendi mi?")
    parsed = [_parse_card(card, name, i) for i, card in enumerate(cards, start=1)]
    items = [p for p in parsed if p["category"]]
    report = {"cards": len(cards), "ads_skipped": len(ads), "products": len(items),
              "skipped_other_category": len(parsed) - len(items)}
    return items, report


def _model_key(item: dict) -> tuple:
    candidates = item["model_code_candidates"]
    return (item["category"], candidates[0].upper()) if candidates else (item["product_id"],)


def import_listings(folder: Path) -> tuple[pd.DataFrame, dict]:
    """Reads every saved page. The same model listed twice keeps the entry with most ratings."""
    paths = sorted(folder.glob("*.htm*"))
    if not paths:
        raise ValueError(f"{folder}: html dosyası yok")
    items, files = [], {}
    for path in paths:
        page_items, files[path.name] = parse_listing(
            path.read_text(encoding="utf-8", errors="replace"), path.name)
        items += page_items
    best: dict[tuple, dict] = {}
    for item in sorted(items, key=lambda i: -(i["rating_count"] or 0)):
        best.setdefault(_model_key(item), item)
    table = pd.DataFrame(list(best.values()), columns=COLUMNS)
    table["model_code_candidates"] = table["model_code_candidates"].map(" | ".join)
    table = table.sort_values(["category", "rating_count"], ascending=[True, False],
                              na_position="last").reset_index(drop=True)
    return table, {"files": files, "candidates": len(table), "duplicates_dropped": len(items) - len(table)}
