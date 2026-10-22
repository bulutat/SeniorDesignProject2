"""API sözleşmesi (Pydantic modelleri).

frontend/src/types.ts bu modellerin TypeScript karşılığıdır; biri değişirse diğeri de güncellenir.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Label = Literal["recommended", "neutral", "not_recommended"]


class Criterion(BaseModel):
    id: str
    name: str
    weight: float


class Category(BaseModel):
    id: str
    name: str
    product_count: int
    criteria: list[Criterion]


class Explanation(BaseModel):
    criterion: str
    criterion_name: str
    direction: Literal["positive", "negative"]
    impact: float = Field(description="Kategori ortalamasına göre skora etkisi (puan)")
    text: str


class ProductSummary(BaseModel):
    id: str
    name: str
    brand: str | None
    category: str
    price_tl: float | None
    energy_class: str | None
    score: float
    label: Label
    label_text: str


class AspectCount(BaseModel):
    pos: int
    neg: int


class ReviewStats(BaseModel):
    n_reviews: int
    rating_avg: float | None
    rating_count: int | None
    aspects: dict[str, AspectCount]


class ProductDetail(ProductSummary):
    model_code: str | None
    url: str | None
    specs: dict[str, float | str | None]
    annual_kwh: float | None
    tco_tl: float | None
    lifetime_years: int
    sub_scores: dict[str, float]
    imputed: list[str] = Field(description="Verisi eksik olup kategori medyanıyla doldurulan kriterler")
    explanations: list[Explanation]
    review_stats: ReviewStats
    method: str


class CustomScoreRequest(BaseModel):
    category: str
    weights: dict[str, float]
