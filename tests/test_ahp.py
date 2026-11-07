"""AHP weights. Judgements are invented."""

from itertools import combinations
from pathlib import Path

import numpy as np
import pytest
import yaml

from greenchoice.config import criteria_ids
from greenchoice.pipeline import ahp
from greenchoice.scoring.ahp import combine, pairwise_matrix, weights

CRITERIA = ["a", "b", "c"]


def test_consistent_judgements_recover_the_weights_with_zero_cr():
    true = np.array([0.6, 0.3, 0.1])
    judgements = {f"{x} vs {y}": true[i] / true[j]
                  for (i, x), (j, y) in combinations(enumerate(CRITERIA), 2)}
    w, cr = weights(pairwise_matrix(CRITERIA, judgements, "t"))
    assert np.allclose(w, true) and cr < 1e-9


def test_fractions_and_either_pair_order_are_read():
    m = pairwise_matrix(CRITERIA, {"a vs b": "3", "c vs a": "1/5", "b vs c": 1}, "t")
    assert m[0, 1] == 3 and np.isclose(m[1, 0], 1 / 3) and np.isclose(m[0, 2], 5)


def test_inconsistent_judgements_have_a_high_cr():
    # a > b, b > c, but c > a: circular
    _, cr = weights(pairwise_matrix(CRITERIA, {"a vs b": 5, "b vs c": 5, "a vs c": "1/5"}, "t"))
    assert cr > 0.1


@pytest.mark.parametrize("judgements, message", [
    ({"a vs b": 3, "a vs c": 3}, "eksik"),
    ({"a vs b": 3, "b vs a": 3, "a vs c": 1, "b vs c": 1}, "iki kez"),
    ({"a vs b": 12, "a vs c": 1, "b vs c": 1}, "1/9 ile 9"),
    ({"a vs b": "çok", "a vs c": 1, "b vs c": 1}, "sayı"),
    ({"a vs x": 3, "a vs c": 1, "b vs c": 1}, "anlaşılmadı"),
])
def test_bad_judgements_fail_with_a_clear_message(judgements, message):
    with pytest.raises(ValueError, match=message):
        pairwise_matrix(CRITERIA, judgements, "t")


def test_geometric_mean_keeps_the_matrix_reciprocal():
    m1 = pairwise_matrix(CRITERIA, {"a vs b": 3, "a vs c": 5, "b vs c": 2}, "t")
    m2 = pairwise_matrix(CRITERIA, {"a vs b": 1, "a vs c": 3, "b vs c": "1/2"}, "t")
    m = combine([m1, m2])
    assert np.allclose(m * m.T, 1)


def test_command_reads_a_folder_and_skips_empty_categories(tmp_path: Path):
    crits = criteria_ids()
    filled = {f"{a} vs {b}": 1 for a, b in combinations(crits, 2)}
    filled[f"{crits[0]} vs {crits[1]}"] = 3
    empty = {f"{a} vs {b}": None for a, b in combinations(crits, 2)}
    (tmp_path / "kisi1.yaml").write_text(yaml.safe_dump(
        {"categories": {"refrigerator": filled, "washing_machine": empty}}), encoding="utf-8")
    report = ahp(tmp_path)
    fridge = report["combined"]["refrigerator"]
    assert fridge["respondents"] == 1 and "washing_machine" not in report["combined"]
    assert fridge["weights"][crits[0]] > fridge["weights"][crits[1]]
    assert abs(sum(fridge["weights"].values()) - 1) < 0.01


def test_template_lists_every_pair_once():
    data = yaml.safe_load(Path("data/templates/ahp_karsilastirma.yaml").read_text(encoding="utf-8"))
    n = len(criteria_ids())
    assert all(len(pairs) == n * (n - 1) // 2 for pairs in data["categories"].values())
