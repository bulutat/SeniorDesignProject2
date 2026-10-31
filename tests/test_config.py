import pytest

from greenchoice.config import aspects_config, categories_config, criteria_ids


@pytest.fixture(scope="module")
def cfg():
    return categories_config()


def test_category_weights_cover_all_criteria_and_sum_to_one(cfg):
    for name, cat in cfg["categories"].items():
        assert set(cat["weights"]) == set(criteria_ids()), name
        assert sum(cat["weights"].values()) == pytest.approx(1.0), name


def test_running_cost_assumptions_are_positive(cfg):
    defaults = cfg["defaults"]
    assert defaults["electricity_price_tl_per_kwh"] > 0
    assert defaults["water_price_tl_per_m3"] > 0
    for name, cat in cfg["categories"].items():
        assert isinstance(cat["lifetime_years"], int) and cat["lifetime_years"] > 0, name


def test_washing_machine_has_cycles_and_every_category_names_its_eprel_group(cfg):
    assert cfg["categories"]["washing_machine"]["annual_cycles"] > 0
    for name, cat in cfg["categories"].items():
        assert cat["eprel_group"].endswith("2019"), name  # EPREL group URL segment, e.g. washingmachines2019


def test_label_thresholds_are_ordered(cfg):
    t = cfg["defaults"]["label_thresholds"]
    assert 0 < t["neutral"] < t["recommended"] <= 100


def test_aspect_phrases_are_lists():
    for name, spec in aspects_config()["aspects"].items():
        assert isinstance(spec["pos"], list) and isinstance(spec["neg"], list), name
