"""Learned extractors. Reviews and labels are invented; no model is downloaded."""

import numpy as np
import pandas as pd
import pytest

from greenchoice.config import SAMPLE_DIR
from greenchoice.nlp.dataset import label_names, split_data
from greenchoice.nlp.tfidf import TfidfExtractor
from greenchoice.nlp.training import load_extractor, tune_thresholds
from greenchoice.pipeline import build, export_nlp_data, train_nlp

TEMPLATES = [
    ("makine çok sessiz çalışıyor {i}", [("noise", "pos")]),
    ("sıkmada çok gürültülü ve titreşim var {i}", [("noise", "neg")]),
    ("iki ayda arızalandı hata kodu veriyor {i}", [("failure", "neg")]),
    ("servis hemen geldi çok ilgiliydi {i}", [("service", "pos")]),
    ("güzel ürün tavsiye ederim teşekkürler {i}", []),
]


def make_data(n_per=12):
    reviews, gold = [], []
    for k, (text, labels) in enumerate(TEMPLATES):
        for i in range(n_per):
            rid = f"r{k}-{i}"
            split = "test" if i < 2 else "val" if i < 4 else "train"
            reviews.append({"review_id": rid, "product_id": "ty-1", "rating": 5,
                            "text": text.format(i=f"numara {i}"), "date": None})
            rows = labels or [(None, None)]
            gold += [{"review_id": rid, "product_id": "ty-1", "split": split,
                      "aspect": a, "polarity": p} for a, p in rows]
    return pd.DataFrame(gold), pd.DataFrame(reviews)


def test_label_names_follow_the_guideline():
    names = label_names()
    assert "failure:pos" not in names and "failure:neg" in names and len(names) == 9


def test_split_data_builds_a_label_matrix_in_review_order():
    gold, reviews = make_data()
    part, y = split_data(gold, reviews, "test")
    assert len(part) == 10 and y.shape == (10, 9)
    noise_pos = label_names().index("noise:pos")
    assert y[part["review_id"] == "r0-0", noise_pos].item() == 1
    assert y[part["review_id"].str.startswith("r4"), :].sum() == 0


def test_tfidf_learns_the_invented_patterns_and_reloads(tmp_path):
    gold, reviews = make_data()
    report = train_nlp_from_frames(gold, reviews, tmp_path / "m.joblib")
    assert "energy:pos" in report["labels_skipped"]  # no example, cannot be learned
    f1 = {r["label"]: r["f1"] for r in report["test"]}
    assert f1["noise:pos"] == 1 and f1["failure:neg"] == 1
    model = TfidfExtractor.load(tmp_path / "m.joblib")
    labels = {(m.aspect, m.polarity) for m in model.extract("makine çok sessiz çalışıyor")}
    assert labels == {("noise", "pos")}
    assert (tmp_path / "m.json").exists()


def train_nlp_from_frames(gold, reviews, out):
    gold.to_csv(out.parent / "gold.csv", index=False)
    reviews.to_csv(out.parent / "reviews.csv", index=False)
    return train_nlp(out.parent / "gold.csv", out.parent / "reviews.csv", out)


def test_thresholds_are_tuned_only_for_labels_seen_in_val():
    y = np.zeros((4, 9))
    y[:2, 0] = 1
    proba = np.zeros((4, 9))
    proba[:2, 0] = 0.3
    out = tune_thresholds(proba, y)
    assert list(out) == [label_names()[0]] and out[label_names()[0]] <= 0.3


def test_build_can_use_the_tfidf_model(tmp_path):
    gold, reviews = make_data()
    train_nlp_from_frames(gold, reviews, tmp_path / "m.joblib")
    summary = build(SAMPLE_DIR, tmp_path / "x.db", nlp="tfidf", nlp_model=tmp_path / "m.joblib")
    assert summary["nlp_method"] == "tfidf_lr_v0" and summary["products"] > 0


def test_unknown_method_and_missing_model_fail():
    with pytest.raises(ValueError, match="bilinmeyen"):
        load_extractor("svm", None)
    with pytest.raises(ValueError, match="--nlp-model"):
        load_extractor("tfidf", None)


def test_export_writes_one_file_per_split(tmp_path):
    gold, reviews = make_data()
    gold.to_csv(tmp_path / "gold.csv", index=False)
    reviews.to_csv(tmp_path / "reviews.csv", index=False)
    report = export_nlp_data(tmp_path / "gold.csv", tmp_path / "reviews.csv", tmp_path / "out")
    assert report["train"] == 40 and report["val"] == 10 and report["test"] == 10
    train = pd.read_csv(tmp_path / "out" / "train.csv")
    assert list(train.columns) == ["review_id", "text", *label_names()]
    assert train["noise:pos"].sum() == 8
