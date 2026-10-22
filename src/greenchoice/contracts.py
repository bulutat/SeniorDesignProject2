"""Modüller arası veri sözleşmeleri (tablo kolonları).

Bir modül bir tabloyu üretirken veya okurken bu listeleri kullanır. Kolon eklemek
serbesttir; buradaki kolonları kaldırmak veya yeniden adlandırmak diğer kişiyi
etkileyeceği için iki kişinin onayıyla yapılır. Ayrıntılar: docs/data-contracts.md
"""

from __future__ import annotations

import pandas as pd

# Aşama 1 çıktısı: data/interim/products.csv ve SQLite "products" tablosu
PRODUCT_COLUMNS = [
    "product_id",                 # kaynak önekli benzersiz id, ör. "ty-123456"
    "source",                     # trendyol | hepsiburada | sample ...
    "url",
    "category",                   # config/categories.yaml anahtarı
    "brand",
    "model_code",                 # EPREL eşleştirmesi için
    "name",
    "price_tl",
    "energy_class",               # A-G (2021 sonrası ölçek), bilinmiyorsa boş
    "energy_kwh_per_year",        # buzdolabı
    "energy_kwh_per_100_cycles",  # çamaşır makinesi
    "water_l_per_cycle",
    "capacity",                   # litre (buzdolabı) / kg (çamaşır makinesi)
    "noise_db",
    "warranty_years",
    "rating_avg",                 # sitedeki ortalama puan (1-5)
    "rating_count",
]

# Aşama 1 çıktısı: data/interim/reviews.csv ve "reviews" tablosu
REVIEW_COLUMNS = ["review_id", "product_id", "rating", "text", "date"]

# Aşama 2 çıktısı: "review_aspects" tablosu (yorum başına 0..n satır)
REVIEW_ASPECT_COLUMNS = ["review_id", "aspect", "polarity", "method", "evidence"]
POLARITIES = ("pos", "neg")

# Skorlama çıktısı: "scores" tablosu
SCORE_COLUMNS = ["product_id", "category", "method", "score", "label",
                 "sub_scores_json", "explanations_json"]

LABELS = {
    "recommended": "Önerilir",
    "neutral": "Nötr",
    "not_recommended": "Önerilmez",
}


def require_columns(df: pd.DataFrame, columns: list[str], table: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"'{table}' tablosunda eksik kolonlar: {missing}")


def conform(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Eksik sözleşme kolonlarını boş olarak ekler, sözleşme kolonlarını başa alır."""
    out = df.copy()
    for c in columns:
        if c not in out.columns:
            out[c] = pd.NA
    extra = [c for c in out.columns if c not in columns]
    return out[columns + extra]
