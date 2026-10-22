import pandas as pd
import pytest

from greenchoice.nlp.aggregate import product_review_features
from greenchoice.nlp.evaluate import evaluate_aspects
from greenchoice.nlp.rule_based import RuleBasedExtractor
from greenchoice.preprocess.text import normalize_text


@pytest.fixture(scope="module")
def extractor():
    return RuleBasedExtractor()


def labels(extractor, text):
    return {(m.aspect, m.polarity) for m in extractor.extract(normalize_text(text))}


def test_positive_phrases_are_not_counted_as_failures(extractor):
    got = labels(extractor, "Üç yıldır hiç bozulmadı, arızasız ve çok sessiz çalışıyor.")
    assert ("durability", "pos") in got
    assert ("noise", "pos") in got
    assert ("failure", "neg") not in got
    assert ("noise", "neg") not in got


def test_negative_service_and_failure(extractor):
    got = labels(extractor, "Altı ayda arızalandı, servis gelmedi.")
    assert got == {("failure", "neg"), ("service", "neg")}


def test_suffixes_match(extractor):
    assert ("durability", "pos") in labels(extractor, "Dayanıklılığı çok iyi")


def test_aggregate_counts_and_issue_rate():
    reviews = pd.DataFrame({"review_id": ["1", "2", "3", "4"], "product_id": ["p"] * 4,
                            "rating": [5, 4, 2, 3]})
    ra = pd.DataFrame({
        "review_id": ["1", "2", "3", "3"],
        "aspect": ["durability", "durability", "failure", "service"],
        "polarity": ["pos", "pos", "neg", "neg"],
        "method": "x", "evidence": None,
    })
    f = product_review_features(reviews, ra).iloc[0]
    assert f["n_reviews"] == 4
    assert f["durability_pos"] == 2 and f["durability_neg"] == 0
    assert f["durability_score"] == pytest.approx(2 / 4)
    assert f["service_issue_rate"] == pytest.approx(1 / 4)  # aynı yorum bir kez sayılır


def test_evaluate_aspects_perfect_and_partial():
    gold = pd.DataFrame({"review_id": ["1", "2"], "aspect": ["noise", "energy"],
                         "polarity": ["pos", "neg"]})
    pred = pd.DataFrame({"review_id": ["1", "3"], "aspect": ["noise", "energy"],
                         "polarity": ["pos", "neg"]})
    res = evaluate_aspects(gold, pred, ["1", "2", "3"]).set_index("label")
    assert res.loc["noise:pos", "f1"] == pytest.approx(1.0)
    assert res.loc["energy:neg", "precision"] == pytest.approx(0.0)
    assert res.loc["[micro]", "precision"] == pytest.approx(0.5)
    assert res.loc["[micro]", "recall"] == pytest.approx(0.5)
