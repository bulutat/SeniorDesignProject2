"""Türk e-ticaret kaynakları.

Karar 17 (docs/decisions.md): Hepsiburada otomatik isteği engelliyor (CAPTCHA), onun için scraper
yok. Trendyol'da yalnızca bilinen ürün sayfaları okunur. Trendyol arama/listeleme ve yorum
API'si robots.txt'de yasak olduğu için kullanılmaz; yorumlar kaydedilen sayfalardan alınır.
"""

from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import urlparse

from greenchoice.collect.base import ProductSource
from greenchoice.collect.http import PoliteClient
from greenchoice.collect.trendyol_product import parse_product


class TrendyolSource(ProductSource):
    source = "trendyol"

    def __init__(self, client: PoliteClient | None = None):
        self.client = client or PoliteClient()

    def iter_product_urls(self, category: str, max_products: int) -> Iterator[str]:
        raise NotImplementedError("Trendyol arama ve listeleme sayfaları robots.txt'de yasak (karar 17)")

    def fetch_product(self, url: str, category: str) -> dict:
        host = urlparse(url).netloc
        if not (host == "trendyol.com" or host.endswith(".trendyol.com")):
            raise ValueError(f"trendyol adresi bekleniyordu: {url}")
        return parse_product(self.client.get_text(url), category)

    def fetch_reviews(self, product: dict, max_reviews: int) -> list[dict]:
        raise NotImplementedError("Trendyol yorum API'si robots.txt'de yasak; sayfaları kaydedin (karar 17)")
