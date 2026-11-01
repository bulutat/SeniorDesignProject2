"""Product facts from a Trendyol product page (docs/kaynak-inceleme.md).

The page embeds a schema.org "Product" block (application/ld+json). It is read instead of HTML
selectors: name, brand, sku, price, aggregate rating and technical properties. Checked on a real
page on 2026-11-02 (washing machine). Reviews and their authors are in the same block and are
deliberately never returned. Values that cannot be read become warnings, not guesses.
"""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
MODEL_TOKEN = re.compile(r"[A-Za-z0-9-]{6,}")


def _product_block(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except json.JSONDecodeError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and item.get("@type") == "Product":
                return item
    raise ValueError("sayfada schema.org Product verisi yok (sayfa engellenmiş veya değişmiş olabilir)")


def _first_number(text: str) -> float | None:
    found = NUMBER.search(text or "")
    return float(found.group(0).replace(",", ".")) if found else None


def _warranty_years(text: str) -> float | None:
    value = _first_number(text)
    if value is None:
        return None
    unit = text.lower()
    if "yıl" in unit:
        return value
    return value / 12 if "ay" in unit else None


def _model_candidates(name: str) -> list[str]:
    return [t for t in MODEL_TOKEN.findall(name)
            if any(c.isdigit() for c in t) and any(c.isalpha() for c in t)]


def parse_product(html: str, category: str) -> dict:
    item = _product_block(html)
    offers = item.get("offers")
    offer = offers[0] if isinstance(offers, list) and offers else offers or {}
    url = offer.get("url") or item.get("@id") or ""
    sku = item.get("sku") or (re.search(r"-p-(\d+)", url) or [None, None])[1]
    if not sku or offer.get("price") is None:
        raise ValueError(f"{url or 'sayfa'}: ürün numarası veya fiyat okunamadı")

    props = {p.get("name"): p.get("unitText") or "" for p in item.get("additionalProperty") or []}
    warnings = []
    capacity = _first_number(props.get("Kapasite", ""))
    if capacity is None:
        warnings.append(f"Kapasite okunamadı: {props.get('Kapasite')!r}")
    warranty = _warranty_years(props.get("Garanti Süresi", ""))
    if warranty is None:
        warnings.append(f"Garanti Süresi okunamadı: {props.get('Garanti Süresi')!r}")

    rating = item.get("aggregateRating") or {}
    name = item.get("name") or ""
    return {
        "product_id": f"ty-{sku}", "source": "trendyol", "url": url, "category": category,
        "brand": (item.get("brand") or {}).get("name"), "model_code": None,
        "model_code_candidates": _model_candidates(name), "name": name,
        "price_tl": float(offer["price"]), "capacity": capacity, "warranty_years": warranty,
        "rating_avg": rating.get("ratingValue"), "rating_count": rating.get("ratingCount"),
        "review_count": rating.get("reviewCount"), "warnings": warnings,
    }
