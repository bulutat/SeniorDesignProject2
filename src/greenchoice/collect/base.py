"""E-ticaret kaynakları için ortak arayüz.

Her kaynak (Trendyol, Hepsiburada ...) bu sınıftan türetilir ve çıktısını
contracts.PRODUCT_COLUMNS / REVIEW_COLUMNS sözleşmesine uygun sözlükler olarak verir.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from greenchoice.contracts import PRODUCT_COLUMNS, REVIEW_COLUMNS, conform


class ProductSource(ABC):
    source: str  # "trendyol", "hepsiburada" ...

    @abstractmethod
    def iter_product_urls(self, category: str, max_products: int) -> Iterator[str]:
        """Kategori listeleme sayfalarından ürün URL'lerini üretir."""

    @abstractmethod
    def fetch_product(self, url: str, category: str) -> dict:
        """Tek bir ürünün PRODUCT_COLUMNS alanlarını döner."""

    @abstractmethod
    def fetch_reviews(self, product: dict, max_reviews: int) -> list[dict]:
        """Ürünün yorumlarını REVIEW_COLUMNS alanlarıyla döner."""

    def collect(self, category: str, out_dir: Path, max_products: int = 100,
                max_reviews: int = 200) -> tuple[pd.DataFrame, pd.DataFrame]:
        products, reviews = [], []
        for url in self.iter_product_urls(category, max_products):
            product = self.fetch_product(url, category)
            products.append(product)
            reviews.extend(self.fetch_reviews(product, max_reviews))

        p = conform(pd.DataFrame(products), PRODUCT_COLUMNS)
        r = conform(pd.DataFrame(reviews), REVIEW_COLUMNS)
        out_dir.mkdir(parents=True, exist_ok=True)
        p.to_csv(out_dir / f"{self.source}_{category}_products.csv", index=False)
        r.to_csv(out_dir / f"{self.source}_{category}_reviews.csv", index=False)
        return p, r
