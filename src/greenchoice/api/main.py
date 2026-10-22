"""GreenChoice API.

Çalıştırma:  uvicorn greenchoice.api.main:app --reload
Dokümantasyon: http://localhost:8000/docs
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from greenchoice import db
from greenchoice.config import aspects_config, categories_config, db_path
from greenchoice.contracts import LABELS
from greenchoice.schemas import (
    AspectCount,
    Category,
    Criterion,
    CustomScoreRequest,
    Explanation,
    ProductDetail,
    ProductSummary,
    ReviewStats,
)
from greenchoice.scoring.service import score_products

SPEC_FIELDS = ["capacity", "noise_db", "warranty_years", "energy_kwh_per_year",
               "energy_kwh_per_100_cycles", "water_l_per_cycle", "energy_class_raw"]


def _clean(v):
    """NaN / pd.NA / numpy türlerini JSON'a uygun Python değerlerine çevirir."""
    if v is None or v is pd.NA:
        return None
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


class Store:
    """Veritabanı tablolarını ilk istekte belleğe alır (prototip ölçeği için yeterli)."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.features: pd.DataFrame | None = None
        self.scores: pd.DataFrame | None = None

    def ensure_loaded(self) -> None:
        if self.features is not None:
            return
        if not self.path.exists():
            raise HTTPException(503, f"Veritabanı bulunamadı ({self.path}). "
                                     "Önce `greenchoice build` çalıştırın.")
        self.features = db.read_table("product_features", self.path)
        self.scores = db.read_table("scores", self.path).set_index("product_id")

    def row(self, product_id: str) -> dict:
        self.ensure_loaded()
        match = self.features[self.features["product_id"] == product_id]
        if match.empty:
            raise HTTPException(404, f"Ürün bulunamadı: {product_id}")
        return {k: _clean(v) for k, v in match.iloc[0].to_dict().items()}


def _summary(row: dict, score: float, label: str) -> ProductSummary:
    return ProductSummary(
        id=row["product_id"], name=row["name"], brand=row.get("brand"),
        category=row["category"], price_tl=row.get("price_tl"),
        energy_class=row.get("energy_class"), score=score, label=label,
        label_text=LABELS[label],
    )


def create_app(path: Path | None = None) -> FastAPI:
    store = Store(path or db_path())
    cfg = categories_config()
    aspect_ids = list(aspects_config()["aspects"].keys())

    app = FastAPI(title="GreenChoice API", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                       allow_methods=["*"], allow_headers=["*"])

    def detail(product_id: str) -> ProductDetail:
        row = store.row(product_id)
        s = store.scores.loc[product_id]
        cat_cfg = cfg["categories"][row["category"]]
        return ProductDetail(
            **_summary(row, float(s["score"]), s["label"]).model_dump(),
            model_code=row.get("model_code"), url=row.get("url"),
            specs={k: row.get(k) for k in SPEC_FIELDS if row.get(k) is not None},
            annual_kwh=row.get("annual_kwh"), tco_tl=row.get("tco_tl"),
            lifetime_years=cat_cfg["lifetime_years"],
            sub_scores=json.loads(s["sub_scores_json"]),
            imputed=[c for c in (row.get("imputed") or "").split(",") if c],
            explanations=[Explanation(**e) for e in json.loads(s["explanations_json"])],
            review_stats=ReviewStats(
                n_reviews=int(row.get("n_reviews") or 0),
                rating_avg=row.get("rating_avg") or row.get("review_rating_avg"),
                rating_count=row.get("rating_count"),
                aspects={a: AspectCount(pos=int(row.get(f"{a}_pos") or 0),
                                        neg=int(row.get(f"{a}_neg") or 0)) for a in aspect_ids},
            ),
            method=s["method"],
        )

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "db_exists": store.path.exists()}

    @app.get("/api/categories", response_model=list[Category])
    def categories():
        store.ensure_loaded()
        counts = store.features["category"].value_counts()
        return [
            Category(id=cid, name=c["name"], product_count=int(counts.get(cid, 0)),
                     criteria=[Criterion(id=k, name=cfg["criteria"][k]["name"], weight=w)
                               for k, w in c["weights"].items()])
            for cid, c in cfg["categories"].items()
        ]

    @app.get("/api/products", response_model=list[ProductSummary])
    def products(category: str | None = None, q: str | None = None,
                 label: str | None = None,
                 sort: str = Query("score", pattern="^(score|price|tco)$"),
                 limit: int = Query(100, ge=1, le=500)):
        store.ensure_loaded()
        df = store.features.join(store.scores[["score", "label"]], on="product_id")
        if category:
            df = df[df["category"] == category]
        if label:
            df = df[df["label"] == label]
        if q:
            text = (df["name"].fillna("") + " " + df["brand"].fillna("")).str.lower()
            df = df[text.str.contains(q.lower(), regex=False)]
        key, asc = {"score": ("score", False), "price": ("price_tl", True),
                    "tco": ("tco_tl", True)}[sort]
        df = df.sort_values(key, ascending=asc, na_position="last").head(limit)
        return [_summary({k: _clean(v) for k, v in r.items()}, float(r["score"]), r["label"])
                for r in df.to_dict("records")]

    @app.get("/api/products/{product_id}", response_model=ProductDetail)
    def product(product_id: str):
        return detail(product_id)

    @app.get("/api/products/{product_id}/explain", response_model=list[Explanation])
    def explain(product_id: str):
        return detail(product_id).explanations

    @app.get("/api/compare", response_model=list[ProductDetail])
    def compare(ids: str = Query(..., description="Virgülle ayrılmış 2-4 ürün id'si")):
        id_list = [i.strip() for i in ids.split(",") if i.strip()]
        if not 2 <= len(id_list) <= 4:
            raise HTTPException(422, "Karşılaştırma için 2-4 ürün seçin")
        return [detail(i) for i in id_list]

    @app.post("/api/score", response_model=list[ProductSummary])
    def custom_score(req: CustomScoreRequest):
        """Kullanıcının kriter ağırlıklarıyla bir kategoriyi yeniden skorlar (ağırlık slider'ı)."""
        store.ensure_loaded()
        if req.category not in cfg["categories"]:
            raise HTTPException(404, f"Bilinmeyen kategori: {req.category}")
        feats = store.features[store.features["category"] == req.category]
        try:
            scored = score_products(feats, req.weights, cfg)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        by_id = feats.set_index("product_id")
        scored = scored.sort_values("score", ascending=False)
        return [_summary({"product_id": r["product_id"],
                          **{k: _clean(v) for k, v in by_id.loc[r["product_id"]].items()}},
                         float(r["score"]), r["label"])
                for _, r in scored.iterrows()]

    return app


app = create_app()
