"""Uçtan uca offline pipeline: CSV -> temizleme -> NLP -> özellikler -> skor -> SQLite.

Kullanım:
    greenchoice build                      # data/sample ile (sentetik örnek veri)
    greenchoice build --source interim     # data/interim/products.csv + reviews.csv
    greenchoice build --source <klasör> --eprel data/raw/eprel.csv --db <yol>
    greenchoice eval-nlp --gold data/annotations/reviews_gold.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from greenchoice import db
from greenchoice.collect.eprel_manual import load_manual_eprel
from greenchoice.config import INTERIM_DIR, SAMPLE_DIR, db_path
from greenchoice.contracts import PRODUCT_COLUMNS, REVIEW_COLUMNS, conform
from greenchoice.nlp.aggregate import product_review_features
from greenchoice.nlp.rule_based import RuleBasedExtractor
from greenchoice.preprocess.matching import merge_eprel
from greenchoice.preprocess.products import clean_products
from greenchoice.preprocess.reviews import clean_reviews
from greenchoice.preprocess.tco import add_tco
from greenchoice.scoring.criteria import compute_criteria
from greenchoice.scoring.service import score_products

SOURCES = {"sample": SAMPLE_DIR, "interim": INTERIM_DIR}


def build(source_dir: Path, out_db: Path, eprel_csv: Path | None = None) -> dict:
    products = conform(pd.read_csv(source_dir / "products.csv", dtype={"product_id": str}),
                       PRODUCT_COLUMNS)
    reviews = conform(pd.read_csv(source_dir / "reviews.csv",
                                  dtype={"review_id": str, "product_id": str}), REVIEW_COLUMNS)

    products = clean_products(products)
    if eprel_csv:
        products = merge_eprel(products, load_manual_eprel(eprel_csv))
    products = add_tco(products)
    reviews = clean_reviews(reviews)
    reviews = reviews[reviews["product_id"].isin(products["product_id"])]

    extractor = RuleBasedExtractor()
    review_aspects = extractor.extract_df(reviews)
    review_feats = product_review_features(reviews, review_aspects)

    features = products.merge(review_feats, on="product_id", how="left")
    features["n_reviews"] = features["n_reviews"].fillna(0).astype(int)
    features = pd.concat([features, compute_criteria(features)], axis=1)

    scored = score_products(features)
    scores = pd.DataFrame({
        "product_id": scored["product_id"],
        "category": scored["category"],
        "method": scored["method"],
        "score": scored["score"],
        "label": scored["label"],
        "sub_scores_json": scored["sub_scores"].map(json.dumps),
        "explanations_json": scored["explanations"].map(
            lambda e: json.dumps(e, ensure_ascii=False)),
    })

    db.write_tables({
        "products": products,
        "reviews": reviews,
        "review_aspects": review_aspects,
        "product_features": features,
        "scores": scores,
    }, out_db)

    return {
        "db": str(out_db),
        "products": len(products),
        "eprel_matched": int(products["eprel_matched"].sum()) if "eprel_matched" in products else 0,
        "reviews": len(reviews),
        "aspect_mentions": len(review_aspects),
        "nlp_method": extractor.method,
        "label_counts": scores["label"].value_counts().to_dict(),
    }


def eval_nlp(gold_csv: Path) -> pd.DataFrame:
    """Kural tabanlı çıkarıcıyı altın etiketlere karşı değerlendirir.

    gold_csv: review_id, text, aspect, polarity. Aspect içermeyen yorumlar aspect boş bırakılarak
    bir satırla yer alır.
    """
    from greenchoice.nlp.evaluate import evaluate_aspects
    from greenchoice.preprocess.text import normalize_text

    gold = pd.read_csv(gold_csv, dtype={"review_id": str})
    texts = gold.drop_duplicates("review_id")[["review_id", "text"]].copy()
    texts["text_clean"] = texts["text"].astype(str).map(normalize_text)
    pred = RuleBasedExtractor().extract_df(texts)
    return evaluate_aspects(gold.dropna(subset=["aspect"]), pred, texts["review_id"].tolist())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="greenchoice")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Pipeline'ı çalıştırıp SQLite veritabanını üret")
    b.add_argument("--source", default="sample", help="sample | interim | klasör yolu")
    b.add_argument("--eprel", type=Path, default=None, help="EPREL CSV (isteğe bağlı)")
    b.add_argument("--db", type=Path, default=None, help="Çıktı veritabanı yolu")

    e = sub.add_parser("eval-nlp", help="NLP baseline'ını altın etiketlerle değerlendir")
    e.add_argument("--gold", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.cmd == "build":
        source = SOURCES.get(args.source, Path(args.source))
        summary = build(source, args.db or db_path(), args.eprel)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.cmd == "eval-nlp":
        print(eval_nlp(args.gold).to_string(index=False, float_format="%.3f"))


if __name__ == "__main__":
    main()
