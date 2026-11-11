"""Annotation pool. Reviews are invented; the keyword phrases come from config/aspects.yaml."""

import pandas as pd
import pytest

from greenchoice.nlp.pool import PoolPlan, annotation_sheet, select_pool
from greenchoice.pipeline import annotation_pool
from greenchoice.preprocess.reviews import clean_reviews

PLAN = PoolPlan(test=20, train=60, per_aspect=5, low_rating=8, product_cap=15)


def make_reviews(per_product=40, products=("ty-1", "ty-2", "hb-1", "hb-2")):
    rows = []
    for p in products:
        for i in range(per_product):
            text, rating = f"ürün {p} hakkında yorum numarası {i} gayet güzel", 5
            if i == 0:
                text = "makine az yakıyor fatura düştü"  # energy keyword, 4 in total
            elif i % 10 == 1:
                text, rating = f"iki ayda arızalandı yorum {i}", 1
            elif i % 10 == 2:
                text = f"çok sessiz çalışıyor yorum {i}"
            rows.append({"review_id": f"{p}-{i}", "product_id": p, "rating": rating,
                         "text": text, "date": "2026-01-01"})
    return clean_reviews(pd.DataFrame(rows))


PRODUCTS = pd.DataFrame({"product_id": ["ty-1", "ty-2", "hb-1", "hb-2"],
                         "category": ["washing_machine", "washing_machine",
                                      "refrigerator", "refrigerator"]})


def test_test_and_train_are_disjoint_and_sized():
    pool, report = select_pool(make_reviews(), PRODUCTS, PLAN)
    test, train = pool[pool["split"] == "test"], pool[pool["split"] == "train"]
    assert len(test) == 20 and len(train) == 60 and pool["review_id"].is_unique
    assert set(test["reason"]) == {"random"} and report["train"] == 60


def test_same_seed_gives_the_same_pool_and_another_seed_does_not():
    reviews = make_reviews()
    first, _ = select_pool(reviews, PRODUCTS, PLAN)
    again, _ = select_pool(reviews, PRODUCTS, PLAN)
    other, _ = select_pool(reviews, PRODUCTS, PoolPlan(**{**PLAN.__dict__, "seed": 7}))
    assert first.equals(again)
    assert set(first["review_id"]) != set(other["review_id"])


def test_rare_keyword_candidates_outside_test_are_all_taken():
    pool, report = select_pool(make_reviews(), PRODUCTS, PLAN)
    energy = {f"{p}-0" for p in PRODUCTS["product_id"]}
    in_test = energy & set(pool.loc[pool["split"] == "test", "review_id"])
    in_train = set(pool.loc[pool["reason"] == "keyword:energy", "review_id"])
    assert in_train == energy - in_test
    assert report["candidates_available"]["energy"] == len(energy - in_test)


def test_product_cap_holds_in_train():
    pool, report = select_pool(make_reviews(), PRODUCTS, PLAN)
    train = pool[pool["split"] == "train"]
    assert train["product_id"].value_counts().max() <= PLAN.product_cap
    assert report["products_in_train"] == 4


def test_cap_that_cannot_fill_train_fails():
    with pytest.raises(ValueError, match="sınır"):
        select_pool(make_reviews(), PRODUCTS, PoolPlan(**{**PLAN.__dict__, "product_cap": 5}))


def test_too_few_reviews_and_unknown_products_fail():
    with pytest.raises(ValueError, match="gerekiyor"):
        select_pool(make_reviews(per_product=10), PRODUCTS, PLAN)
    with pytest.raises(ValueError, match="ürün listesinde"):
        select_pool(make_reviews(products=("ty-1", "ty-9")), PRODUCTS, PLAN)


def test_sheets_share_test_split_train_and_hide_the_reason():
    reviews = make_reviews()
    pool, _ = select_pool(reviews, PRODUCTS, PLAN)
    a, b = annotation_sheet(pool, reviews, "A"), annotation_sheet(pool, reviews, "B")
    test = set(pool.loc[pool["split"] == "test", "review_id"])
    assert len(a) == len(b) == 20 + 30
    assert set(a["review_id"]) & set(b["review_id"]) == test
    assert not {"split", "reason", "rating"} & set(a.columns)
    assert {"durability", "energy", "service", "failure", "noise", "checked", "note"} <= set(a.columns)
    assert a["text"].notna().all() and (a["noise"] == "").all()


def test_command_writes_files_and_refuses_to_overwrite(tmp_path):
    ids = [f"{site}-{n}" for site in ("ty", "hb") for n in range(1, 7)]  # cap 30 needs 10+
    raw = make_reviews(products=ids)[["review_id", "product_id", "rating", "text", "date"]]
    raw.to_csv(tmp_path / "reviews.csv", index=False)
    pd.DataFrame({"product_id": ids, "category": ["washing_machine"] * 6 + ["refrigerator"] * 6}
                 ).to_csv(tmp_path / "products.csv", index=False)
    out = tmp_path / "etiketleme"
    report = annotation_pool(tmp_path / "reviews.csv", tmp_path / "products.csv", out, seed=491)
    assert report["test"] == 100 and report["train"] == 300
    assert report["sheet_A"] == report["sheet_B"] == 250
    assert "text" not in pd.read_csv(out / "pool.csv").columns
    with pytest.raises(ValueError, match="--force"):
        annotation_pool(tmp_path / "reviews.csv", tmp_path / "products.csv", out, seed=491)
