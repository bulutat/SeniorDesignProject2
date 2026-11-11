"""Train a learned extractor on the train split, tune thresholds on val, score on test.

The test split is used once, for the reported P/R/F1; nothing is tuned on it. Thresholds are
chosen per label on val to maximise F1; a label without a positive val example keeps 0.5.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from greenchoice.nlp.dataset import TEXT_COLUMN, label_names, split_data, to_review_aspects
from greenchoice.nlp.evaluate import evaluate_aspects

GRID = np.round(np.arange(0.1, 0.91, 0.05), 2)


def tune_thresholds(proba: np.ndarray, y: np.ndarray) -> dict[str, float]:
    out = {}
    for j, name in enumerate(label_names()):
        if y[:, j].sum() == 0:
            continue
        scores = [f1_score(y[:, j], proba[:, j] >= t, zero_division=0) for t in GRID]
        out[name] = float(GRID[int(np.argmax(scores))])
    return out


def load_extractor(method: str, model_path: Path | None):
    """'rule' needs no model; 'tfidf' and 'berturk' load what train-nlp wrote."""
    if method not in ("rule", "tfidf", "berturk"):
        raise ValueError(f"bilinmeyen NLP yöntemi: {method} (rule | tfidf | berturk)")
    if method == "rule":
        from greenchoice.nlp.rule_based import RuleBasedExtractor
        return RuleBasedExtractor()
    if model_path is None:
        raise ValueError(f"'{method}' için --nlp-model gerekli")
    if method == "tfidf":
        from greenchoice.nlp.tfidf import TfidfExtractor
        return TfidfExtractor.load(model_path)
    from greenchoice.nlp.transformer import TransformerExtractor  # method == "berturk"
    return TransformerExtractor(str(model_path))


def train_tfidf(gold: pd.DataFrame, reviews: pd.DataFrame, out: Path, seed: int = 491) -> dict:
    from greenchoice.nlp.tfidf import TfidfExtractor

    train, y_train = split_data(gold, reviews, "train")
    model, report = TfidfExtractor.train(train[TEXT_COLUMN].tolist(), y_train, seed)
    if (gold["split"] == "val").any():
        val, y_val = split_data(gold, reviews, "val")
        model.thresholds = tune_thresholds(model.predict_proba(val[TEXT_COLUMN].tolist()), y_val)
    model.save(out)
    report = {**report, "train_reviews": len(train), "thresholds": model.thresholds,
              "model": str(out)}
    if (gold["split"] == "test").any():
        test, _ = split_data(gold, reviews, "test")
        pred = model.extract_df(test)
        table = evaluate_aspects(gold[gold["split"] == "test"].dropna(subset=["aspect"]), pred,
                                 test["review_id"].tolist())
        report["test"] = table.round(3).to_dict(orient="records")
    out.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    return report


__all__ = ["load_extractor", "to_review_aspects", "train_tfidf", "tune_thresholds"]
