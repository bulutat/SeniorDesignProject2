"""Uçtan uca offline pipeline: CSV -> temizleme -> NLP -> özellikler -> skor -> SQLite.

Kullanım:
    greenchoice build                      # data/sample ile (sentetik örnek veri)
    greenchoice build --source interim     # data/interim/products.csv + reviews.csv
    greenchoice build --source <klasör> --eprel data/raw/eprel.csv --db <yol>
    greenchoice collect-labels             # etiketleme tabloları -> kappa + altın etiketler
    greenchoice eval-nlp                   # altın etiketlerin test bölümünde P/R/F1
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
from greenchoice.preprocess.energy_labels import apply_energy_sources, load_energy_labels
from greenchoice.preprocess.matching import merge_eprel
from greenchoice.preprocess.products import clean_products
from greenchoice.preprocess.reviews import clean_reviews
from greenchoice.preprocess.tco import add_tco
from greenchoice.scoring.criteria import compute_criteria
from greenchoice.scoring.service import score_products

SOURCES = {"sample": SAMPLE_DIR, "interim": INTERIM_DIR}


def build(source_dir: Path, out_db: Path, eprel_csv: Path | None = None,
          nlp: str = "rule", nlp_model: Path | None = None,
          energy_labels_csv: Path | None = None) -> dict:
    products = conform(pd.read_csv(source_dir / "products.csv", dtype={"product_id": str}),
                       PRODUCT_COLUMNS)
    reviews = conform(pd.read_csv(source_dir / "reviews.csv",
                                  dtype={"review_id": str, "product_id": str}), REVIEW_COLUMNS)

    products = clean_products(products)
    if eprel_csv:
        products = merge_eprel(products, load_manual_eprel(eprel_csv))
    labels = load_energy_labels(energy_labels_csv) if energy_labels_csv else None
    products = apply_energy_sources(products, labels)
    products = add_tco(products)
    reviews = clean_reviews(reviews)
    reviews = reviews[reviews["product_id"].isin(products["product_id"])]

    from greenchoice.nlp.training import load_extractor

    extractor = load_extractor(nlp, nlp_model)
    review_aspects = extractor.extract_df(reviews, column="text_product")
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
        "energy_source": products["energy_source"].fillna("none").value_counts().to_dict(),
        "reviews": len(reviews),
        "aspect_mentions": len(review_aspects),
        "nlp_method": extractor.method,
        "label_counts": scores["label"].value_counts().to_dict(),
    }


def eval_nlp(gold_csv: Path, reviews_csv: Path = INTERIM_DIR / "reviews.csv",
             split: str = "test") -> pd.DataFrame:
    """Rule-based extractor against the gold labels of one split (nlp/labels.py).

    The gold file holds ids and labels only; review text comes from reviews_csv and goes through
    the same cleaning as `build`. An older gold file with a "text" column is still accepted.
    """
    from greenchoice.nlp.evaluate import evaluate_aspects

    gold = pd.read_csv(gold_csv, dtype={"review_id": str})
    if "split" in gold.columns:
        gold = gold[gold["split"] == split]
    if gold.empty:
        raise ValueError(f"{gold_csv}: '{split}' bölümünde etiket yok")
    ids = gold["review_id"].drop_duplicates().tolist()
    if "text" in gold.columns:
        source = gold.drop_duplicates("review_id")[["review_id", "text"]].assign(
            product_id="", rating=None, date=None)
    else:
        source = pd.read_csv(reviews_csv, dtype={"review_id": str, "product_id": str})
    reviews = clean_reviews(conform(source[source["review_id"].isin(ids)], REVIEW_COLUMNS))
    lost = sorted(set(ids) - set(reviews["review_id"]))
    if lost:
        raise ValueError(f"{len(lost)} etiketli yorum metni bulunamadı veya temizlikte düştü: {lost[:5]}")
    pred = RuleBasedExtractor().extract_df(reviews, column="text_product")
    return evaluate_aspects(gold.dropna(subset=["aspect"]), pred, ids)


def collect_labels(sheets_dir: Path, out_dir: Path, seed: int = 491) -> dict:
    """Filled sheets -> raw labels, kappa table, disagreement file and gold file (nlp/labels.py)."""
    from greenchoice.nlp.labels import agreement, build_gold, read_sheet
    from greenchoice.nlp.pool import ANNOTATORS

    pool = pd.read_csv(sheets_dir / "pool.csv", dtype=str)
    parts, report, texts = [], {}, {}
    for name in ANNOTATORS:
        path = sheets_dir / f"etiketleme_{name}.csv"
        if not path.exists():
            continue
        sheet = pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False)
        mine = set(pool.loc[pool["annotators"].str.split(",").map(lambda a, n=name: n in a),
                            "review_id"])
        extra = sorted(set(sheet["review_id"]) - mine)
        if extra:
            raise ValueError(f"{path.name}: havuzda {name} için olmayan yorumlar var: {extra[:5]}")
        labels, counts = read_sheet(sheet, name, path.name)
        parts.append(labels)
        report[f"sheet_{name}"] = counts
        texts.update(zip(sheet["review_id"], sheet["text"], strict=True))
    if not parts:
        raise ValueError(f"{sheets_dir}: etiketleme_A.csv veya etiketleme_B.csv yok")
    raw = pd.concat(parts, ignore_index=True)

    both = raw.groupby("review_id")["annotator"].nunique()
    test = set(pool.loc[pool["split"] == "test", "review_id"])
    shared = sorted(r for r in both.index[both == 2] if r in test)
    kappa, disagreements = agreement(raw, shared)

    decisions_path = sheets_dir / "uzlasma.csv"
    previous = None
    if decisions_path.exists():
        previous = pd.read_csv(decisions_path, dtype=str, encoding="utf-8-sig",
                               keep_default_na=False)[["review_id", "aspect", "decision"]]
    merged = disagreements.merge(previous, on=["review_id", "aspect"], how="left")         if previous is not None else disagreements.assign(decision="")
    merged["decision"] = merged["decision"].fillna("")
    merged["text"] = merged["review_id"].map(texts)
    merged.to_csv(decisions_path, index=False, encoding="utf-8-sig")  # holds text: data/interim only

    gold, gold_report = build_gold(raw, pool, disagreements, merged, seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out_dir / "reviews_labels_raw.csv", index=False)
    gold.to_csv(out_dir / "reviews_gold.csv", index=False)
    kappa.to_csv(out_dir / "kappa.csv", index=False, float_format="%.3f")
    return {**report, "shared_reviews": len(shared), "disagreements": len(disagreements),
            "undecided": int((merged["decision"] == "").sum()), **gold_report,
            "kappa": kappa.round(3).to_dict(orient="records")}


def train_nlp(gold_csv: Path, reviews_csv: Path, out: Path, seed: int = 491) -> dict:
    """TF-IDF + LR on the train split, thresholds on val, P/R/F1 on test (nlp/training.py)."""
    from greenchoice.nlp.training import train_tfidf

    gold = pd.read_csv(gold_csv, dtype={"review_id": str})
    reviews = pd.read_csv(reviews_csv, dtype={"review_id": str, "product_id": str})
    return train_tfidf(gold, reviews, out, seed)


def export_nlp_data(gold_csv: Path, reviews_csv: Path, out_dir: Path) -> dict:
    """One CSV per split for the Colab notebook: review_id, text, one 0/1 column per label.

    The files hold review text, so they stay in data/interim and are shared privately.
    """
    from greenchoice.nlp.dataset import TEXT_COLUMN, label_names, split_data

    gold = pd.read_csv(gold_csv, dtype={"review_id": str})
    reviews = pd.read_csv(reviews_csv, dtype={"review_id": str, "product_id": str})
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for split in ("train", "val", "test"):
        if not (gold["split"] == split).any():
            continue
        part, y = split_data(gold, reviews, split)
        table = pd.DataFrame(y.astype(int), columns=label_names())
        table.insert(0, "text", part[TEXT_COLUMN].to_numpy())
        table.insert(0, "review_id", part["review_id"].to_numpy())
        table.to_csv(out_dir / f"{split}.csv", index=False, encoding="utf-8")
        counts[split] = len(table)
    return {**counts, "out_dir": str(out_dir)}


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


def annotation_pool(reviews: Path, products: Path, out_dir: Path, seed: int,
                    force: bool = False) -> dict:
    """Raw reviews -> annotation manifest and one sheet per annotator (nlp/pool.py)."""
    from greenchoice.nlp.pool import ANNOTATORS, PoolPlan, annotation_sheet, select_pool

    manifest = out_dir / "pool.csv"
    if manifest.exists() and not force:
        raise ValueError(f"{manifest} zaten var. Etiketleme başladıysa havuzu değiştirmeyin; "
                         "yine de yeniden seçmek için --force")
    cleaned = clean_reviews(pd.read_csv(reviews, dtype={"review_id": str, "product_id": str}))
    pool, report = select_pool(cleaned, pd.read_csv(products, dtype=str), PoolPlan(seed=seed))
    out_dir.mkdir(parents=True, exist_ok=True)
    pool.to_csv(manifest, index=False)
    for name in ANNOTATORS:
        sheet = annotation_sheet(pool, cleaned, name, seed)
        # utf-8-sig so that Excel shows Turkish letters correctly
        sheet.to_csv(out_dir / f"etiketleme_{name}.csv", index=False, encoding="utf-8-sig")
        report[f"sheet_{name}"] = len(sheet)
    return {**report, "out_dir": str(out_dir), "seed": seed}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="greenchoice")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Pipeline'ı çalıştırıp SQLite veritabanını üret")
    b.add_argument("--source", default="sample", help="sample | interim | klasör yolu")
    b.add_argument("--eprel", type=Path, default=None, help="EPREL CSV (isteğe bağlı)")
    b.add_argument("--db", type=Path, default=None, help="Çıktı veritabanı yolu")
    b.add_argument("--nlp", default="rule", help="rule | tfidf | berturk")
    b.add_argument("--nlp-model", type=Path, default=None,
                   help="tfidf: models/tfidf_lr_v0.joblib, berturk: model klasörü")

    tn = sub.add_parser("train-nlp", help="TF-IDF + LR aspect modelini altın etiketlerle eğit")
    tn.add_argument("--gold", type=Path, default=Path("data/annotations/reviews_gold.csv"))
    tn.add_argument("--reviews", type=Path, default=Path("data/interim/reviews.csv"))
    tn.add_argument("--out", type=Path, default=Path("models/tfidf_lr_v0.joblib"))

    ex = sub.add_parser("export-nlp-data", help="Colab BERTurk eğitimi için train/val/test CSV'leri")
    ex.add_argument("--gold", type=Path, default=Path("data/annotations/reviews_gold.csv"))
    ex.add_argument("--reviews", type=Path, default=Path("data/interim/reviews.csv"))
    ex.add_argument("--out-dir", type=Path, default=Path("data/interim/nlp_egitim"))
    b.add_argument("--energy-labels", type=Path, default=Path("data/manual/energy_labels.csv"),
                   help="üretici enerji etiketlerinden elle okunan değerler (dosya yoksa atlanır)")

    e = sub.add_parser("eval-nlp", help="NLP baseline'ını altın etiketlerle değerlendir")
    e.add_argument("--gold", type=Path, default=Path("data/annotations/reviews_gold.csv"))
    e.add_argument("--reviews", type=Path, default=Path("data/interim/reviews.csv"))
    e.add_argument("--split", default="test", help="test | val | train")

    cl = sub.add_parser("collect-labels", help="Doldurulan etiketleme tablolarından kappa ve altın etiket")
    cl.add_argument("--sheets-dir", type=Path, default=Path("data/interim/etiketleme"))
    cl.add_argument("--out-dir", type=Path, default=Path("data/annotations"))
    cl.add_argument("--seed", type=int, default=491)

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

    a = sub.add_parser("annotation-pool", help="Etiketlenecek yorumları seç, etiketçi tablolarını yaz")
    a.add_argument("--reviews", type=Path, default=Path("data/interim/reviews.csv"))
    a.add_argument("--products", type=Path, default=Path("data/interim/pilot_products.csv"))
    a.add_argument("--out-dir", type=Path, default=Path("data/interim/etiketleme"))
    a.add_argument("--seed", type=int, default=491)
    a.add_argument("--force", action="store_true", help="var olan havuzun üstüne yaz")

    args = parser.parse_args(argv)
    if args.cmd == "build":
        source = SOURCES.get(args.source, Path(args.source))
        labels = args.energy_labels if args.energy_labels.exists() else None
        try:
            summary = build(source, args.db or db_path(), args.eprel, args.nlp, args.nlp_model, labels)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.cmd in ("train-nlp", "export-nlp-data"):
        try:
            if args.cmd == "train-nlp":
                report = train_nlp(args.gold, args.reviews, args.out)
            else:
                report = export_nlp_data(args.gold, args.reviews, args.out_dir)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cmd == "eval-nlp":
        try:
            table = eval_nlp(args.gold, args.reviews, args.split)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(table.to_string(index=False, float_format="%.3f"))
    elif args.cmd == "collect-labels":
        try:
            report = collect_labels(args.sheets_dir, args.out_dir, args.seed)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))
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
    elif args.cmd == "annotation-pool":
        try:
            report = annotation_pool(args.reviews, args.products, args.out_dir, args.seed, args.force)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
