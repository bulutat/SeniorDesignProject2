"""Filled annotation sheets -> raw labels, Cohen's kappa and the gold file (task O2.1).

A sheet (nlp/pool.py) has one column per aspect. A cell holds "pos", "neg", "pos,neg" or nothing
(no such aspect in the review); the "checked" column marks a row as labelled, so an empty row
means "no aspect" only once it is checked. Shared test reviews labelled differently by A and B
go to a disagreement file; once the two decide, the decision ("pos", "neg", "pos,neg" or "yok")
is written there and becomes the gold label.

Files in data/annotations hold ids and labels only, never review text.
"""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from greenchoice.config import aspects_config

NEG_ONLY = {"failure"}  # annotation guideline: a failure has no positive counterpart
NONE = "yok"            # decision meaning "this aspect is not in the review"
VAL_SHARE = 0.2         # share of train reviews held out for threshold tuning


def aspect_names() -> list[str]:
    return list(aspects_config()["aspects"])


def _parse_cell(value, aspect: str, where: str) -> tuple[str, ...]:
    if pd.isna(value) or not str(value).strip():
        return ()
    parts = sorted({p.strip().lower() for p in str(value).replace(";", ",").split(",") if p.strip()})
    if not parts or any(p not in ("pos", "neg") for p in parts):
        raise ValueError(f"{where}: '{aspect}' için 'pos', 'neg' veya 'pos,neg' bekleniyordu, "
                         f"{value!r} yazılmış")
    if aspect in NEG_ONLY and "pos" in parts:
        raise ValueError(f"{where}: '{aspect}' yalnızca 'neg' olabilir")
    return tuple(parts)


def read_sheet(sheet: pd.DataFrame, annotator: str, name: str) -> tuple[pd.DataFrame, dict]:
    """Checked rows -> long labels (review_id, annotator, aspect, polarity); aspect empty = none."""
    aspects = aspect_names()
    missing = [c for c in ["review_id", "checked", *aspects] if c not in sheet.columns]
    if missing:
        raise ValueError(f"{name}: eksik kolonlar {missing}")
    if sheet["review_id"].duplicated().any():
        raise ValueError(f"{name}: aynı review_id birden fazla satırda")
    checked = sheet["checked"].fillna("").astype(str).str.strip() != ""
    rows = []
    for row_no, record in zip(sheet.index[checked] + 2, sheet[checked].itertuples(), strict=True):
        found = False
        for aspect in aspects:
            for polarity in _parse_cell(getattr(record, aspect), aspect, f"{name} satır {row_no}"):
                rows.append((record.review_id, annotator, aspect, polarity))
                found = True
        if not found:
            rows.append((record.review_id, annotator, None, None))
    labels = pd.DataFrame(rows, columns=["review_id", "annotator", "aspect", "polarity"])
    return labels, {"rows": len(sheet), "checked": int(checked.sum())}


def _cells(labels: pd.DataFrame, review_ids: list[str]) -> pd.DataFrame:
    """Long labels -> one row per review, one "pos" / "neg" / "pos,neg" / "" cell per aspect."""
    out = pd.DataFrame("", index=pd.Index(review_ids, name="review_id"), columns=aspect_names())
    found = labels.dropna(subset=["aspect"])
    for (rid, aspect), group in found.groupby(["review_id", "aspect"]):
        if rid in out.index:
            out.loc[rid, aspect] = ",".join(sorted(group["polarity"]))
    return out


def agreement(raw: pd.DataFrame, shared: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Kappa per aspect on reviews both annotators checked, and the cells they disagree on."""
    a = _cells(raw[raw["annotator"] == "A"], shared)
    b = _cells(raw[raw["annotator"] == "B"], shared)
    rows = []
    for aspect in aspect_names():
        x, y = a[aspect], b[aspect]
        same = float((x == y).mean()) if len(x) else float("nan")
        # kappa is undefined when both annotators use a single value throughout
        kappa = (cohen_kappa_score(x, y) if len(set(x) | set(y)) > 1 else float("nan"))
        rows.append({"aspect": aspect, "reviews": len(x), "agreement": same, "kappa": kappa,
                     "labelled_A": int((x != "").sum()), "labelled_B": int((y != "").sum())})
    diff = [(rid, asp, a.loc[rid, asp], b.loc[rid, asp])
            for asp in aspect_names() for rid in shared if a.loc[rid, asp] != b.loc[rid, asp]]
    disagreements = pd.DataFrame(diff, columns=["review_id", "aspect", "A", "B"])
    return pd.DataFrame(rows), disagreements


def val_ids(train_ids: list[str], seed: int) -> set[str]:
    ids = pd.Series(sorted(train_ids))
    return set(ids.sample(frac=VAL_SHARE, random_state=seed)) if len(ids) else set()


def build_gold(raw: pd.DataFrame, pool: pd.DataFrame, disagreements: pd.DataFrame,
               decisions: pd.DataFrame | None, seed: int) -> tuple[pd.DataFrame, dict]:
    """Gold labels: train/val from their single annotator, test from agreement plus decisions.

    Test reviews with an undecided disagreement are left out, so the test set is never filled
    with one person's guess. Returns (review_id, product_id, split, aspect, polarity).
    """
    pool = pool.set_index("review_id")
    labelled = raw.groupby("review_id")["annotator"].apply(set)
    test_ids = [r for r in pool.index[pool["split"] == "test"]
                if labelled.get(r, set()) >= {"A", "B"}]
    train_ids = [r for r in pool.index[pool["split"] == "train"] if r in labelled.index]
    held_out = val_ids(list(pool.index[pool["split"] == "train"]), seed)

    decided = {}
    if decisions is not None and not decisions.empty:
        for record in decisions.itertuples():
            value = "" if pd.isna(record.decision) else str(record.decision).strip()
            if value:
                where = f"uzlaşma {record.review_id}/{record.aspect}"
                decided[(record.review_id, record.aspect)] = (
                    () if value.lower() == NONE else _parse_cell(value, record.aspect, where))

    agreed = _cells(raw[raw["annotator"] == "A"], test_ids)
    open_cells = set()
    for record in disagreements.itertuples():
        key = (record.review_id, record.aspect)
        if key in decided:
            agreed.loc[record.review_id, record.aspect] = ",".join(decided[key])
        else:
            open_cells.add(key)
    unresolved = {rid for rid, _ in open_cells}

    rows = []
    for rid in test_ids:
        if rid in unresolved:
            continue
        rows += _gold_rows(rid, "test", agreed.loc[rid])
    single = _cells(raw[raw["review_id"].isin(train_ids)], train_ids)
    for rid in train_ids:
        rows += _gold_rows(rid, "val" if rid in held_out else "train", single.loc[rid])
    gold = pd.DataFrame(rows, columns=["review_id", "split", "aspect", "polarity"])
    gold.insert(1, "product_id", gold["review_id"].map(pool["product_id"]))
    report = {
        "test_reviews": len(test_ids) - len(unresolved),
        "test_unresolved": len(unresolved),
        "train_reviews": sum(r not in held_out for r in train_ids),
        "val_reviews": sum(r in held_out for r in train_ids),
        "labels": gold.dropna(subset=["aspect"]).assign(
            label=lambda d: d["aspect"] + ":" + d["polarity"])["label"].value_counts().to_dict(),
    }
    return gold, report


def _gold_rows(review_id: str, split: str, cells: pd.Series) -> list[tuple]:
    rows = [(review_id, split, aspect, pol)
            for aspect, value in cells.items() if value for pol in value.split(",")]
    return rows or [(review_id, split, None, None)]
