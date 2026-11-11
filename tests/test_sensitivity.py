"""Sensitivity analysis on the synthetic sample data."""

import pandas as pd
import pytest

from greenchoice.config import SAMPLE_DIR, categories_config
from greenchoice.pipeline import build, sensitivity_report
from greenchoice.scoring.sensitivity import breakeven_prices, scenarios


@pytest.fixture(scope="module")
def sample_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "s.db"
    build(SAMPLE_DIR, path)
    return path


def test_report_covers_every_scenario_and_category(sample_db):
    report = sensitivity_report(sample_db)
    rankings = pd.DataFrame(report["rankings"])
    assert set(rankings["scenario"]) == set(scenarios(categories_config()))
    assert rankings["kendall_tau"].between(-1, 1).all()


def test_scenarios_do_not_change_the_base_config():
    cfg = categories_config()
    before = cfg["defaults"]["electricity_price_tl_per_kwh"]
    scenarios(cfg)
    assert cfg["defaults"]["electricity_price_tl_per_kwh"] == before
    for c in scenarios(cfg).values():
        for cat in c["categories"].values():
            assert abs(sum(cat["weights"].values()) - 1) < 1e-9


def test_breakeven_price_equalises_lifetime_cost():
    cfg = categories_config()
    years = cfg["categories"]["refrigerator"]["lifetime_years"]
    features = pd.DataFrame({
        "product_id": ["cheap", "efficient"], "category": "refrigerator",
        "price_tl": [30000, 36000], "energy_class": ["E", "C"],
        "energy_kwh_per_year": [300, 200], "energy_kwh_per_100_cycles": None,
        "water_l_per_cycle": None, "rating_avg": 4.5, "rating_count": 50, "n_reviews": 10,
        "review_rating_avg": 4.5, "durability_score": 0.0, "service_issue_rate": 0.0})
    pair = breakeven_prices(features, cfg).iloc[0]
    assert pair["cheap"] == "cheap" and pair["extra_kwh_per_year"] == 100
    assert pair["breakeven_tl_per_kwh"] == pytest.approx(6000 / (years * 100), abs=0.01)
