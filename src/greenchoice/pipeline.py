"""Uçtan uca offline pipeline: CSV -> temizleme -> NLP -> özellikler -> skor -> SQLite.

Kullanım:
    greenchoice build                      # data/sample ile (sentetik örnek veri)
    greenchoice build --source interim     # data/interim/products.csv + reviews.csv
    greenchoice build --source <klasör> --eprel data/raw/eprel.csv --db <yol>
    greenchoice eval-nlp --gold data/annotations/reviews_gold.csv
    greenchoice check-pilot --products data/raw/pilot_products.csv --eprel data/raw/eprel_manual.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from greenchoice import db
from greenchoice.collect.eprel_manual import load_manual_eprel
from greenchoice.collect.http import PoliteClient
from greenchoice.collect.pilot import load_pilot_list, pilot_report
from greenchoice.collect.sheets import build_template, export_csvs
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


def check_pilot(products_csv: Path, eprel_csv: Path | None = None, out: Path | None = None) -> dict:
    products = load_pilot_list(products_csv)
    eprel = load_manual_eprel(eprel_csv) if eprel_csv else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        products[["product_id", "url", "category"]].to_csv(out, index=False)
    return pilot_report(products, eprel)


def import_sheets(xlsx: Path, out_dir: Path) -> dict[str, int]:
    """Excel -> CSV, then the same strict loaders the pipeline uses."""
    try:
        paths = export_csvs(xlsx, out_dir)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    try:
        pilot = load_pilot_list(paths["pilot"])
        eprel = load_manual_eprel(paths["eprel"])
    except ValueError as exc:
        raise SystemExit(f"{exc}\nExcel'deki satır = mesajdaki satır + 1 "
                         "(ortada boş satır varsa kayar). Düzeltip komutu tekrar çalıştır.") from exc
    return {paths["pilot"].name: len(pilot), paths["eprel"].name: len(eprel)}


def fetch_trendyol(urls: list[str], category: str, client=None) -> list[dict]:
    """Known Trendyol product pages -> product facts. Polite client; bs4 stays optional."""
    from greenchoice.collect.ecommerce import TrendyolSource

    source = TrendyolSource(client or PoliteClient())
    return [source.fetch_product(url, category) for url in urls]


def import_reviews(pages: Path, products: Path, out: Path) -> dict:
    """Saved review pages -> reviews CSV. Importing here keeps bs4 optional for other commands."""
    from greenchoice.collect.saved_pages import import_folder

    known = set(pd.read_csv(products, dtype=str)["product_id"])
    table, report = import_folder(pages, known)
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    return {"reviews": len(table), "out": str(out), "products": report}


def import_listings(pages: Path, out: Path) -> dict:
    """Saved Hepsiburada search pages -> candidate products CSV. bs4 stays optional."""
    from greenchoice.collect.listing_pages import import_listings as read_folder

    table, report = read_folder(pages)
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    return {**report, "out": str(out)}


def select_candidates(listings: Path | None, trendyol: Path | None, existing: Path, out: Path,
                      target: int, brand_cap: int, min_ratings: int) -> dict:
    """Candidate tables -> the products to add (decision 17c). Rules: collect/selection.py."""
    from greenchoice.collect.selection import pool_from_sources, select_products

    pool = pool_from_sources(pd.read_csv(listings) if listings else None,
                             json.loads(trendyol.read_text(encoding="utf-8")) if trendyol else None)
    chosen, report = select_products(pool, pd.read_csv(existing), target, min_ratings, brand_cap)
    out.parent.mkdir(parents=True, exist_ok=True)
    chosen.assign(model_codes=chosen["model_codes"].map(" | ".join)).to_csv(out, index=False)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="greenchoice")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Pipeline'ı çalıştırıp SQLite veritabanını üret")
    b.add_argument("--source", default="sample", help="sample | interim | klasör yolu")
    b.add_argument("--eprel", type=Path, default=None, help="EPREL CSV (isteğe bağlı)")
    b.add_argument("--db", type=Path, default=None, help="Çıktı veritabanı yolu")

    e = sub.add_parser("eval-nlp", help="NLP baseline'ını altın etiketlerle değerlendir")
    e.add_argument("--gold", type=Path, required=True)

    m = sub.add_parser("make-sheets", help="Boş veri toplama Excel dosyasını üret")
    m.add_argument("--out", type=Path, default=Path("data/raw/veri_toplama.xlsx"))

    i = sub.add_parser("import-sheets", help="Doldurulmuş Excel'i pilot ve EPREL CSV'lerine çevir")
    i.add_argument("--xlsx", type=Path, default=Path("data/raw/veri_toplama.xlsx"))
    i.add_argument("--out-dir", type=Path, default=Path("data/raw"))

    t = sub.add_parser("fetch-trendyol", help="Bilinen Trendyol ürün sayfalarını nazikçe oku (JSON)")
    t.add_argument("--url", nargs="+", required=True, help="Trendyol ürün sayfası adres(ler)i")
    t.add_argument("--category", required=True, help="refrigerator | washing_machine")

    li = sub.add_parser("import-listings", help="Kaydedilen Hepsiburada arama sayfalarından aday ürün listesi")
    li.add_argument("--pages", type=Path, default=Path("data/raw/listeleme_sayfalari"))
    li.add_argument("--out", type=Path, default=Path("data/interim/aday_urunler.csv"))

    s = sub.add_parser("select-candidates", help="Aday ürünlerden listeye eklenecekleri seç (karar 17c)")
    s.add_argument("--listings", type=Path, default=None, help="import-listings çıktısı (CSV)")
    s.add_argument("--trendyol", type=Path, default=None, help="fetch-trendyol çıktısı (JSON)")
    s.add_argument("--existing", type=Path, default=Path("data/raw/pilot_products.csv"))
    s.add_argument("--out", type=Path, default=Path("data/interim/secilen_urunler.csv"))
    s.add_argument("--target", type=int, default=40, help="kategori başına hedef ürün sayısı")
    s.add_argument("--brand-cap", type=int, default=12, help="kategori başına marka başına en fazla ürün")
    s.add_argument("--min-ratings", type=int, default=30)

    c = sub.add_parser("check-pilot", help="Pilot ürün listesini doğrula, EPREL kapsamını raporla")
    c.add_argument("--products", type=Path, required=True, help="Pilot ürün listesi CSV")
    c.add_argument("--eprel", type=Path, default=None, help="Elle toplanan EPREL CSV (isteğe bağlı)")
    c.add_argument("--out", type=Path, default=None,
                   help="Kişi A'ya verilecek product_id, url, category dosyası")

    r = sub.add_parser("import-reviews", help="Tarayıcıdan kaydedilen yorum sayfalarını CSV'ye çevir")
    r.add_argument("--pages", type=Path, default=Path("data/raw/yorum_sayfalari"))
    r.add_argument("--products", type=Path, default=Path("data/interim/pilot_products.csv"))
    r.add_argument("--out", type=Path, default=Path("data/interim/reviews.csv"))

    args = parser.parse_args(argv)
    if args.cmd == "build":
        source = SOURCES.get(args.source, Path(args.source))
        summary = build(source, args.db or db_path(), args.eprel)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.cmd == "eval-nlp":
        print(eval_nlp(args.gold).to_string(index=False, float_format="%.3f"))
    elif args.cmd == "make-sheets":
        build_template(args.out)
        print(f"Excel şablonu yazıldı: {args.out}")
    elif args.cmd == "import-sheets":
        for name, count in import_sheets(args.xlsx, args.out_dir).items():
            print(f"{name}: {count} satır")
    elif args.cmd == "select-candidates":
        try:
            report = select_candidates(args.listings, args.trendyol, args.existing, args.out,
                                       args.target, args.brand_cap, args.min_ratings)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cmd == "import-listings":
        try:
            report = import_listings(args.pages, args.out)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cmd == "fetch-trendyol":
        try:
            products = fetch_trendyol(args.url, args.category)
        except (ValueError, PermissionError) as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(products, ensure_ascii=False, indent=2))
    elif args.cmd == "check-pilot":
        try:
            report = check_pilot(args.products, args.eprel, args.out)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cmd == "import-reviews":
        try:
            report = import_reviews(args.pages, args.products, args.out)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
