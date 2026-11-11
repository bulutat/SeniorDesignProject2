"""Annotation sheets -> kappa and gold labels. Reviews and labels are invented."""

import pandas as pd
import pytest

from greenchoice.nlp.labels import agreement, build_gold, read_sheet
from greenchoice.pipeline import collect_labels, eval_nlp

ASPECTS = ["durability", "energy", "service", "failure", "noise"]


def sheet(rows):
    """rows: (review_id, {aspect: value}, checked)"""
    out = []
    for rid, cells, checked in rows:
        out.append({"review_id": rid, "product_id": "ty-1", "text": f"metin {rid}",
                    **{a: cells.get(a, "") for a in ASPECTS},
                    "checked": "x" if checked else "", "note": ""})
    return pd.DataFrame(out)


def test_read_sheet_keeps_checked_rows_and_marks_empty_ones_as_no_aspect():
    labels, counts = read_sheet(sheet([
        ("r1", {"noise": "pos", "service": "pos, neg"}, True),
        ("r2", {}, True),
        ("r3", {"noise": "neg"}, False),  # not checked yet
    ]), "A", "a.csv")
    assert counts == {"rows": 3, "checked": 2}
    got = set(labels.fillna("").itertuples(index=False, name=None))
    assert got == {("r1", "A", "noise", "pos"), ("r1", "A", "service", "neg"),
                   ("r1", "A", "service", "pos"), ("r2", "A", "", "")}


@pytest.mark.parametrize("cells, message", [
    ({"noise": "iyi"}, "noise"),
    ({"failure": "pos"}, "yalnızca 'neg'"),
])
def test_read_sheet_rejects_bad_values_with_the_row(cells, message):
    with pytest.raises(ValueError, match=rf"a\.csv satır 2.*{message}|{message}.*"):
        read_sheet(sheet([("r1", cells, True)]), "A", "a.csv")


def raw_labels():
    a, _ = read_sheet(sheet([("t1", {"noise": "pos"}, True), ("t2", {"failure": "neg"}, True),
                             ("t3", {}, True), ("tr1", {"energy": "pos"}, True)]), "A", "a")
    b, _ = read_sheet(sheet([("t1", {"noise": "pos"}, True), ("t2", {}, True),
                             ("t3", {}, True), ("tr2", {}, True)]), "B", "b")
    return pd.concat([a, b], ignore_index=True)


POOL = pd.DataFrame({
    "review_id": ["t1", "t2", "t3", "tr1", "tr2"],
    "product_id": ["ty-1"] * 5,
    "split": ["test", "test", "test", "train", "train"],
    "annotators": ["A,B", "A,B", "A,B", "A", "B"],
})


def test_agreement_reports_kappa_and_the_disagreeing_cells():
    kappa, diff = agreement(raw_labels(), ["t1", "t2", "t3"])
    noise = kappa.set_index("aspect").loc["noise"]
    assert noise["agreement"] == 1 and noise["kappa"] == 1
    assert pd.isna(kappa.set_index("aspect").loc["energy", "kappa"])  # nobody used it
    assert diff.to_dict(orient="records") == [
        {"review_id": "t2", "aspect": "failure", "A": "neg", "B": ""}]


def test_gold_leaves_out_undecided_test_reviews_and_uses_decisions():
    raw = raw_labels()
    _, diff = agreement(raw, ["t1", "t2", "t3"])
    gold, report = build_gold(raw, POOL, diff, None, seed=491)
    assert "t2" not in set(gold["review_id"]) and report["test_unresolved"] == 1
    decided = diff.assign(decision="yok")
    gold, report = build_gold(raw, POOL, diff, decided, seed=491)
    t2 = gold[gold["review_id"] == "t2"]
    assert len(t2) == 1 and t2["aspect"].isna().all() and report["test_unresolved"] == 0
    assert set(gold.loc[gold["review_id"] == "tr1", "aspect"]) == {"energy"}
    assert set(gold["split"]) <= {"test", "train", "val"} and "text" not in gold.columns


def test_collect_labels_writes_files_without_text(tmp_path):
    sheets = tmp_path / "etiketleme"
    sheets.mkdir()
    POOL.assign(category="washing_machine", reason="random").to_csv(sheets / "pool.csv", index=False)
    sheet([("t1", {"noise": "pos"}, True), ("t2", {"failure": "neg"}, True),
           ("t3", {}, True), ("tr1", {"energy": "pos"}, True)]).to_csv(
        sheets / "etiketleme_A.csv", index=False, encoding="utf-8-sig")
    sheet([("t1", {"noise": "pos"}, True), ("t2", {}, True), ("t3", {}, True),
           ("tr2", {}, True)]).to_csv(sheets / "etiketleme_B.csv", index=False, encoding="utf-8-sig")
    out = tmp_path / "annotations"

    report = collect_labels(sheets, out)
    assert report["shared_reviews"] == 3 and report["undecided"] == 1
    for name in ["reviews_gold.csv", "reviews_labels_raw.csv", "kappa.csv"]:
        assert "text" not in pd.read_csv(out / name).columns
    decisions = pd.read_csv(sheets / "uzlasma.csv", encoding="utf-8-sig", keep_default_na=False)
    decisions.loc[0, "decision"] = "neg"
    decisions.to_csv(sheets / "uzlasma.csv", index=False, encoding="utf-8-sig")
    report = collect_labels(sheets, out)
    assert report["undecided"] == 0 and report["test_reviews"] == 3


def test_collect_labels_rejects_a_review_from_another_sheet(tmp_path):
    POOL.assign(category="x", reason="random").to_csv(tmp_path / "pool.csv", index=False)
    sheet([("tr2", {}, True)]).to_csv(tmp_path / "etiketleme_A.csv", index=False)
    with pytest.raises(ValueError, match="tr2"):
        collect_labels(tmp_path, tmp_path / "out")


def test_eval_nlp_joins_text_from_the_reviews_file(tmp_path):
    reviews = pd.DataFrame({"review_id": ["t1", "t2"], "product_id": ["ty-1", "ty-1"],
                            "rating": [5, 1], "date": None,
                            "text": ["Makine çok sessiz çalışıyor", "İki ayda arızalandı maalesef"]})
    reviews.to_csv(tmp_path / "reviews.csv", index=False)
    gold = pd.DataFrame({"review_id": ["t1", "t2"], "product_id": "ty-1", "split": "test",
                         "aspect": ["noise", "failure"], "polarity": ["pos", "neg"]})
    gold.to_csv(tmp_path / "gold.csv", index=False)
    table = eval_nlp(tmp_path / "gold.csv", tmp_path / "reviews.csv").set_index("label")
    assert table.loc["noise:pos", "f1"] == 1 and table.loc["failure:neg", "f1"] == 1
    with pytest.raises(ValueError, match="val"):
        eval_nlp(tmp_path / "gold.csv", tmp_path / "reviews.csv", split="val")
