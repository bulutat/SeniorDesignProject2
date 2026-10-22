"""Türk e-ticaret kaynakları. Aşama 0-1'de site yapısı incelendikten sonra doldurulacak.

Notlar:
- Önce robots.txt ve kullanım koşulları okunmalı. PoliteClient robots.txt'ye uyar.
- Yorumlar çoğu sitede sayfa HTML'i yerine ayrı bir JSON isteğiyle yükleniyor;
  tarayıcının Network sekmesinden bu istek bulunabilir.
- Toplanan ham HTML/JSON data/raw/ altında önbelleğe alınır, repoya girmez.
"""

from __future__ import annotations

from collections.abc import Iterator

from greenchoice.collect.base import ProductSource
from greenchoice.collect.http import PoliteClient


class TrendyolSource(ProductSource):
    source = "trendyol"

    def __init__(self, client: PoliteClient | None = None):
        self.client = client or PoliteClient()

    def iter_product_urls(self, category: str, max_products: int) -> Iterator[str]:
        raise NotImplementedError("Aşama 1: kategori listeleme sayfası ayrıştırılacak")

    def fetch_product(self, url: str, category: str) -> dict:
        raise NotImplementedError("Aşama 1 (Kişi B): ürün sayfası ayrıştırılacak")

    def fetch_reviews(self, product: dict, max_reviews: int) -> list[dict]:
        raise NotImplementedError("Aşama 1 (Kişi A): yorum uç noktası ayrıştırılacak")
