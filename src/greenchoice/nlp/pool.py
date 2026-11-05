"""Choosing the reviews to annotate (docs/annotation-guideline.md, task O1.1).

- Test: drawn completely at random, so P/R/F1 reflect the real distribution. Both annotators
  label it; it is also the shared set for Cohen's kappa.
- Train: enriched, because random reviews rarely mention energy, failures, service or noise.
  Keyword candidates of those aspects and low-rated reviews come first, the rest is random and
  alternates between categories. A cap per product keeps a few popular products from dominating.

Each annotator gets one sheet: the shared test reviews and their own train reviews, shuffled
together, without the reason a review was chosen, so neither the split nor the keyword hit
steers the label. The manifest (pool.csv) holds ids only; the sheets hold review text and stay
in data/interim, which is not committed.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from greenchoice.config import aspects_config
from greenchoice.nlp.rule_based import RuleBasedExtractor

ENRICHED_ASPECTS = ("energy", "failure", "noise", "service")  # rarest first
ANNOTATORS = ("A", "B")


@dataclass(frozen=True)
class PoolPlan:
    test: int = 100
    train: int = 300
    per_aspect: int = 40   # keyword candidates taken per enriched aspect
    low_rating: int = 60   # reviews rated 3 or lower
    product_cap: int = 30  # train reviews per product at most
    seed: int = 491


def _with_category(reviews: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    category = products.drop_duplicates("product_id").set_index("product_id")["category"]
    unknown = sorted(set(reviews["product_id"]) - set(category.index))
    if unknown:
        raise ValueError(f"ürün listesinde olmayan ürünlerin yorumları var: {unknown[:5]}")
    return reviews.assign(category=reviews["product_id"].map(category))


def select_pool(reviews: pd.DataFrame, products: pd.DataFrame,
                plan: PoolPlan | None = None) -> tuple[pd.DataFrame, dict]:
    """Cleaned reviews -> manifest (review_id, product_id, category, split, reason, annotators)."""
    plan = plan or PoolPlan()
    reviews = _with_category(reviews, products)
    if len(reviews) < plan.test + plan.train:
        raise ValueError(f"{len(reviews)} yorum var, havuz için {plan.test + plan.train} gerekiyor")

    test = reviews.sample(n=plan.test, random_state=plan.seed)
    rest = reviews.drop(test.index).sample(frac=1, random_state=plan.seed + 1)
    found = RuleBasedExtractor().extract_df(rest, column="text_clean")

    chosen: dict[int, str] = {}  # index -> reason
    per_product: dict[str, int] = {}
    available: dict[str, int] = {}

    def take(candidates: pd.DataFrame, reason: str, limit: int) -> None:
        taken = 0
        for idx, product in zip(candidates.index, candidates["product_id"], strict=True):
            if taken == limit or len(chosen) == plan.train:
                return
            if idx in chosen or per_product.get(product, 0) >= plan.product_cap:
                continue
            chosen[idx] = reason
            per_product[product] = per_product.get(product, 0) + 1
            taken += 1

    for aspect in ENRICHED_ASPECTS:
        ids = set(found.loc[found["aspect"] == aspect, "review_id"])
        candidates = rest[rest["review_id"].isin(ids)]
        available[aspect] = len(candidates)
        take(candidates, f"keyword:{aspect}", plan.per_aspect)
    low = rest[pd.to_numeric(rest["rating"], errors="coerce") <= 3]
    available["low_rating"] = len(low)
    take(low, "low_rating", plan.low_rating)
    # Alternate categories: the k-th review of each category comes before the (k+1)-th of any
    order = rest.assign(_k=rest.groupby("category").cumcount()).sort_values("_k", kind="stable")
    take(order, "random", plan.train)
    if len(chosen) < plan.train:
        raise ValueError(f"ürün sınırı ({plan.product_cap}) ile yalnızca {len(chosen)} eğitim "
                         f"yorumu seçilebildi, {plan.train} gerekiyor; sınırı artırın")

    train = rest.loc[list(chosen)].assign(reason=list(chosen.values()))
    # Train halves go to A and B in turn, after a shuffle so reasons are spread evenly
    train = train.sample(frac=1, random_state=plan.seed + 2)
    train["annotators"] = [ANNOTATORS[i % 2] for i in range(len(train))]
    pool = pd.concat([test.assign(split="test", reason="random", annotators="A,B"),
                      train.assign(split="train")])
    pool = pool[["review_id", "product_id", "category", "split", "reason", "annotators"]]
    return pool.reset_index(drop=True), _report(pool, available)


def _report(pool: pd.DataFrame, available: dict[str, int]) -> dict:
    train = pool[pool["split"] == "train"]
    return {
        "test": int((pool["split"] == "test").sum()),
        "train": len(train),
        "train_reasons": train["reason"].value_counts().to_dict(),
        "candidates_available": available,
        "categories": pool.groupby("split")["category"].value_counts().unstack(fill_value=0)
                          .to_dict(orient="index"),
        "products_in_train": int(train["product_id"].nunique()),
        "largest_product_share_in_train": round(train["product_id"].value_counts().iloc[0]
                                                / len(train), 3),
    }


def annotation_sheet(pool: pd.DataFrame, reviews: pd.DataFrame, annotator: str,
                     seed: int = PoolPlan.seed) -> pd.DataFrame:
    """The reviews one annotator labels: text plus an empty column per aspect (pos / neg)."""
    mine = pool[pool["annotators"].str.split(",").map(lambda names: annotator in names)]
    text = reviews.drop_duplicates("review_id").set_index("review_id")["text"]
    sheet = mine[["review_id", "product_id"]].assign(text=mine["review_id"].map(text))
    sheet = sheet.sample(frac=1, random_state=seed + ord(annotator)).reset_index(drop=True)
    for aspect in aspects_config()["aspects"]:
        sheet[aspect] = ""
    sheet["note"] = ""
    return sheet
