import json

import pytest

from greenchoice import db
from greenchoice.scoring.weighted import WeightedScorer


def test_pipeline_summary(sample_db):
    _, summary = sample_db
    assert summary["products"] == 12
    assert summary["reviews"] == 43  # 47 - spam - kopya - 2 kısa yorum
    assert summary["aspect_mentions"] > 0


def test_pipeline_runs_before_any_review_is_collected(tmp_path):
    """Products and EPREL data exist before the review scraper has delivered anything."""
    import shutil

    from greenchoice.config import SAMPLE_DIR
    from greenchoice.pipeline import build

    shutil.copy(SAMPLE_DIR / "products.csv", tmp_path / "products.csv")
    (tmp_path / "reviews.csv").write_text("review_id,product_id,rating,text,date\n", encoding="utf-8")
    summary = build(tmp_path, tmp_path / "no_reviews.db")
    assert summary["products"] == 12 and summary["reviews"] == 0
    scores = db.read_table("scores", tmp_path / "no_reviews.db")
    assert len(scores) == 12 and scores["score"].between(0, 100).all()


def test_scores_are_in_range_and_explained(sample_db):
    path, _ = sample_db
    scores = db.read_table("scores", path)
    assert scores["score"].between(0, 100).all()
    assert set(scores["label"]) <= {"recommended", "neutral", "not_recommended"}
    for raw in scores["explanations_json"]:
        for e in json.loads(raw):
            assert e["text"] and e["direction"] in ("positive", "negative")


def test_efficient_fridge_beats_inefficient_one(sample_db):
    path, _ = sample_db
    f = db.read_table("product_features", path).set_index("product_id")
    s = db.read_table("scores", path).set_index("product_id")
    # s-rf-01 (C, 182 kWh, olumlu yorumlar) vs s-rf-04 (F, 352 kWh, arıza şikâyetleri)
    assert f.loc["s-rf-01", "c_energy_efficiency"] > f.loc["s-rf-04", "c_energy_efficiency"]
    assert s.loc["s-rf-01", "score"] > s.loc["s-rf-04", "score"]


def test_missing_data_is_imputed_not_explained(sample_db):
    path, _ = sample_db
    f = db.read_table("product_features", path).set_index("product_id")
    assert "satisfaction" in f.loc["s-wm-06", "imputed"]
    expl = json.loads(db.read_table("scores", path).set_index("product_id")
                      .loc["s-wm-06", "explanations_json"])
    assert all(e["criterion"] != "satisfaction" for e in expl)


def test_review_explanations_need_evidence(sample_db):
    path, _ = sample_db
    expl = json.loads(db.read_table("scores", path).set_index("product_id")
                      .loc["s-rf-04", "explanations_json"])
    # s-rf-04'te dayanıklılıktan bahseden yorum yok; skor ortalamanın altında olsa da açıklanmaz
    assert all(e["criterion"] != "durability" for e in expl)


def test_energy_criterion_ignores_reviews(sample_db):
    """Decision 16: energy comes from the energy class and kWh, never from review text."""
    from greenchoice.scoring.criteria import compute_criteria

    path, _ = sample_db
    features = db.read_table("product_features", path)
    changed = features.assign(energy_score=-1.0, energy_pos=0, energy_neg=99)
    before = compute_criteria(features)["c_energy_efficiency"]
    after = compute_criteria(changed)["c_energy_efficiency"]
    assert before.tolist() == after.tolist()


def test_weights_are_normalized_and_overridable():
    scorer = WeightedScorer()
    w = scorer.weights_for("refrigerator", {"energy_efficiency": 5})
    assert sum(w.values()) == pytest.approx(1.0)
    assert max(w, key=w.get) == "energy_efficiency"
    with pytest.raises(ValueError):
        scorer.weights_for("refrigerator", {k: 0 for k in w})
