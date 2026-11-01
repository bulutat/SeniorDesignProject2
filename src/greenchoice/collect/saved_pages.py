"""Reviews from pages a person saved in their browser (docs/yorum-toplama.md).

The sites do not allow automated review collection (docs/kaynak-inceleme.md), so this module
makes no network requests: it only reads local HTML files. Usernames are never extracted.
Selectors were checked against real saved pages on 2026-11-01. They will break if the sites
change, and a page that yields nothing fails with its file name instead of being skipped.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup, Tag

from greenchoice.contracts import REVIEW_COLUMNS, conform

TRENDYOL_STAR_PX = 16.7143  # padding on the star bar per missing star, measured on saved pages
MONTHS = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6, "Temmuz": 7,
          "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}
ASPECT_HEADING = "Değerlendirilen özellikler"
EXTRA_COLUMNS = ["truncated", "site_aspects"]


@dataclass
class SavedPage:
    product_id: str
    reviews: list[dict]
    cards: int                     # review cards in the file, including ones without text
    site_total: int | None = None  # Trendyol only: comment count the site reports
    page: int | None = None        # Hepsiburada only: "2 / 3" pagination
    total_pages: int | None = None


def _source_url(soup: BeautifulSoup, html: str, name: str) -> str:
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        return canonical["href"]
    saved = re.search(r"saved from url=\(\d+\)(\S+)", html[:1000])
    if saved:
        return saved.group(1)
    raise ValueError(f"{name}: sayfa adresi bulunamadı, sayfa tarayıcıdan mı kaydedildi?")


def _product_number(url: str, name: str) -> str:
    found = re.findall(r"-pm?-([A-Za-z0-9]+)", url)
    if not found:
        raise ValueError(f"{name}: adreste ürün numarası yok: {url}")
    return found[-1]


def _trendyol_rating(review: Tag, name: str) -> int:
    style = review.select_one(".review-stars .star-rating-full-star").get("style", "")
    padding = float(re.search(r"padding-inline-end:\s*([\d.]+)px", style).group(1))
    missing = padding / TRENDYOL_STAR_PX
    if abs(missing - round(missing)) > 0.05 or not 0 <= round(missing) <= 4:
        raise ValueError(f"{name}: yıldız genişliği beklenmedik: {style!r}")
    return 5 - round(missing)


def _trendyol_date(review: Tag) -> str | None:
    parts = [s.get_text(strip=True) for s in review.select(".detail-item.date span")]
    if len(parts) != 3 or parts[1] not in MONTHS:
        return None
    return f"{parts[2]}-{MONTHS[parts[1]]:02d}-{int(parts[0]):02d}"


def _parse_trendyol(soup: BeautifulSoup, html: str, url: str, name: str) -> SavedPage:
    cards = soup.select(".review")
    if not cards:
        raise ValueError(f"{name}: yorum bulunamadı. Sayfa yorumlar yüklendikten sonra mı kaydedildi?")
    reviews = []
    for card in cards:
        body = card.find(class_=re.compile(r"^comment-body\d+$"))
        text = card.select_one("span.review-comment > span")
        if body is None or text is None or not text.get_text(strip=True):
            continue
        comment_id = re.search(r"comment-body(\d+)", " ".join(body["class"])).group(1)
        more = card.select_one("button.read-more")
        reviews.append({
            "review_id": f"ty-{comment_id}",
            "rating": _trendyol_rating(card, name),
            "text": " ".join(text.get_text(" ").split()),
            "date": _trendyol_date(card),
            "truncated": bool(more and "Devamını" in more.get_text()),
            "site_aspects": None,
        })
    total = re.search(r'"commentCount":\s*(\d+)', html)
    return SavedPage(f"ty-{_product_number(url, name)}", reviews, len(cards),
                     site_total=int(total.group(1)) if total else None)


def _hepsiburada_rating(card: Tag, name: str) -> int:
    stars = [e for e in card.find_all("div", class_=["star", "outlinedStar"]) if e.get("style")]
    if len(stars) != 5:
        raise ValueError(f"{name}: yorum kartında 5 yıldız bekleniyordu, {len(stars)} bulundu")
    return sum("star" in e["class"] for e in stars)


def _hepsiburada_aspects(card: Tag) -> str | None:
    heading = card.find(string=re.compile(ASPECT_HEADING))
    box = heading.parent.find_next_sibling("div") if heading else None
    if box is None:
        return None
    values = [s.get_text(strip=True) for s in box.find_all("span")]
    pairs = {k: int(v) for k, v in zip(values[::2], values[1::2], strict=False) if v.isdigit()}
    return json.dumps(pairs, ensure_ascii=False) if pairs else None


def _parse_hepsiburada(soup: BeautifulSoup, url: str, name: str) -> SavedPage:
    holder = soup.select_one(".paginationContentHolder")
    cards = holder.find_all(recursive=False) if holder else []
    if not cards:
        raise ValueError(f"{name}: yorum bulunamadı. Sayfa yorumlar yüklendikten sonra mı kaydedildi?")
    product_id = f"hb-{_product_number(url, name)}"
    reviews = []
    for card in cards:
        spans = [s for s in card.find_all("span", class_=False) if s.get_text(strip=True)]
        if not spans:
            continue  # rating without a comment; counted in SavedPage.cards
        text = " ".join(spans[0].get_text(" ").split())
        date = card.find(attrs={"content": re.compile(r"^\d{4}-\d{2}-\d{2}$")})
        day = date["content"] if date else None
        key = f"{product_id}|{day}|{text}".encode()  # the page has no review id
        reviews.append({
            "review_id": f"hb-{hashlib.sha1(key).hexdigest()[:12]}",
            "rating": _hepsiburada_rating(card, name),
            "text": text,
            "date": day,
            "truncated": False,
            "site_aspects": _hepsiburada_aspects(card),
        })
    bar = soup.select_one(".paginationBarHolder")
    match = re.search(r"(\d+)\s*/\s*(\d+)", bar.get_text(" ")) if bar else None
    page, total = (int(match.group(1)), int(match.group(2))) if match else (1, 1)
    return SavedPage(product_id, reviews, len(cards), page=page, total_pages=total)


def parse_page(html: str, name: str) -> SavedPage:
    soup = BeautifulSoup(html, "html.parser")
    url = _source_url(soup, html, name)
    if "trendyol.com" in url:
        return _parse_trendyol(soup, html, url, name)
    if "hepsiburada.com" in url:
        return _parse_hepsiburada(soup, url, name)
    raise ValueError(f"{name}: desteklenmeyen site: {url}")


def _product_report(pages: list[SavedPage], reviews: list[dict]) -> dict:
    first = pages[0]
    report = {
        "reviews": len(reviews),
        "truncated": sum(r["truncated"] for r in reviews),
        "without_text": sum(p.cards for p in pages) - sum(len(p.reviews) for p in pages),
    }
    if first.site_total is not None:
        report["site_total"] = first.site_total
        report["missing"] = max(first.site_total - len(reviews), 0)
    if first.total_pages is not None:
        seen = {p.page for p in pages}
        report["missing_pages"] = sorted(set(range(1, first.total_pages + 1)) - seen)
    return report


def import_folder(folder: Path, known_products: set[str]) -> tuple[pd.DataFrame, dict]:
    """Reads every saved page in the folder. Returns the reviews table and a per-product report."""
    paths = sorted(folder.glob("*.htm*"))
    if not paths:
        raise ValueError(f"{folder}: html dosyası yok")
    pages: dict[str, list[SavedPage]] = {}
    for path in paths:
        page = parse_page(path.read_text(encoding="utf-8", errors="replace"), path.name)
        if page.product_id not in known_products:
            raise ValueError(f"{path.name}: {page.product_id} ürün listesinde yok")
        pages.setdefault(page.product_id, []).append(page)

    rows, report = [], {}
    for product_id, product_pages in pages.items():
        unique = {r["review_id"]: r for p in product_pages for r in p.reviews}
        rows += [{"product_id": product_id, **r} for r in unique.values()]
        report[product_id] = _product_report(product_pages, list(unique.values()))
    return conform(pd.DataFrame(rows), [*REVIEW_COLUMNS, *EXTRA_COLUMNS]), report
