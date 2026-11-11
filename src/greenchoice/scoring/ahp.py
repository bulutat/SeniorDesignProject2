"""AHP criterion weights (task B3.1).

Each respondent fills one YAML file (template: data/templates/ahp_karsilastirma.yaml) with a
Saaty-scale judgement for every pair of criteria in a category: "a vs b: 3" means a is
moderately more important than b, "a vs b: 1/3" the opposite, 1 equal. Weights are the
normalised principal eigenvector of the pairwise matrix; the consistency ratio (CR) compares the
matrix with random ones and should stay below 0.1. Several respondents are combined by the
element-wise geometric mean of their matrices, which keeps the result reciprocal.

The output is a suggestion: updating config/categories.yaml stays a decision of the team.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np
import yaml

# Saaty's random consistency index by matrix size
RANDOM_INDEX = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41,
                9: 1.45, 10: 1.49}
CR_LIMIT = 0.1


def _value(raw, where: str) -> float:
    try:
        value = float(Fraction(str(raw).strip()))
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"{where}: sayı veya kesir bekleniyordu (ör. 3, 1/5), {raw!r} yazılmış") from None
    if not 1 / 9 - 1e-9 <= value <= 9 + 1e-9:
        raise ValueError(f"{where}: değer 1/9 ile 9 arasında olmalı, {raw!r} yazılmış")
    return value


def pairwise_matrix(criteria: list[str], judgements: dict[str, object], where: str) -> np.ndarray:
    """{"a vs b": value} for every pair, each pair once in either order -> reciprocal matrix."""
    index = {c: i for i, c in enumerate(criteria)}
    m = np.ones((len(criteria), len(criteria)))
    seen = set()
    for key, raw in judgements.items():
        parts = [p.strip() for p in str(key).split(" vs ")]
        if len(parts) != 2 or any(p not in index for p in parts) or parts[0] == parts[1]:
            raise ValueError(f"{where}: '{key}' anlaşılmadı; 'kriter_a vs kriter_b' bekleniyordu")
        a, b = parts
        pair = frozenset(parts)
        if pair in seen:
            raise ValueError(f"{where}: {a} ile {b} iki kez karşılaştırılmış")
        seen.add(pair)
        if raw is None or str(raw).strip() == "":
            raise ValueError(f"{where}: '{key}' boş")
        value = _value(raw, f"{where} '{key}'")
        m[index[a], index[b]] = value
        m[index[b], index[a]] = 1 / value
    missing = [f"{a} vs {b}" for a, b in combinations(criteria, 2) if frozenset((a, b)) not in seen]
    if missing:
        raise ValueError(f"{where}: eksik karşılaştırmalar: {missing}")
    return m


def weights(m: np.ndarray) -> tuple[np.ndarray, float]:
    """Principal eigenvector weights (sum 1) and the consistency ratio."""
    values, vectors = np.linalg.eig(m)
    k = int(np.argmax(values.real))
    w = np.abs(vectors[:, k].real)
    w = w / w.sum()
    n = len(m)
    ci = (values[k].real - n) / (n - 1) if n > 2 else 0.0
    cr = ci / RANDOM_INDEX[n] if RANDOM_INDEX.get(n) else 0.0
    return w, max(float(cr), 0.0)


def combine(matrices: list[np.ndarray]) -> np.ndarray:
    return np.exp(np.mean([np.log(m) for m in matrices], axis=0))


def load_respondent(path: Path, criteria: list[str], categories: list[str]) -> dict[str, np.ndarray]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = {}
    for category in categories:
        judgements = (data.get("categories") or {}).get(category) or {}
        if any(v is not None and str(v).strip() for v in judgements.values()):  # skip empty ones
            out[category] = pairwise_matrix(criteria, judgements, f"{path.name} / {category}")
    if not out:
        raise ValueError(f"{path.name}: hiçbir kategori doldurulmamış")
    return out


def ahp_report(paths: list[Path], criteria: list[str], categories: list[str]) -> dict:
    """Per respondent and combined: weights per category and CR."""
    per_person = {p.stem: load_respondent(p, criteria, categories) for p in paths}
    report: dict = {"criteria": criteria, "respondents": {}, "combined": {}}
    for name, matrices in per_person.items():
        report["respondents"][name] = {}
        for category, m in matrices.items():
            w, cr = weights(m)
            report["respondents"][name][category] = {
                "weights": dict(zip(criteria, np.round(w, 3).tolist(), strict=True)),
                "cr": round(cr, 3), "consistent": cr < CR_LIMIT}
    for category in categories:
        ms = [m[category] for m in per_person.values() if category in m]
        if not ms:
            continue
        w, cr = weights(combine(ms))
        report["combined"][category] = {
            "respondents": len(ms),
            "weights": dict(zip(criteria, np.round(w, 3).tolist(), strict=True)),
            "cr": round(cr, 3), "consistent": cr < CR_LIMIT}
    return report
