"""TF-IDF + Logistic Regression aspect extractor (task B2.1).

Character n-grams inside word boundaries cope with Turkish suffixes ("bozuldu", "bozulmadı")
without a stemmer. One binary classifier per label with balanced class weights, because most
labels are rare. A label with no positive training example cannot be learned; it is never
predicted and the training report lists it.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from greenchoice.nlp.base import AspectExtractor, AspectMention
from greenchoice.nlp.dataset import TEXT_COLUMN, label_names


class TfidfExtractor(AspectExtractor):
    method = "tfidf_lr_v0"

    def __init__(self, vectorizer: TfidfVectorizer, models: dict[str, LogisticRegression],
                 thresholds: dict[str, float] | None = None):
        self.vectorizer = vectorizer
        self.models = models
        self.thresholds = thresholds or {}

    @classmethod
    def train(cls, texts: list[str], y: np.ndarray, seed: int = 491) -> tuple[TfidfExtractor, dict]:
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2,
                                     sublinear_tf=True)
        x = vectorizer.fit_transform(texts)
        models, skipped = {}, []
        for j, name in enumerate(label_names()):
            if y[:, j].sum() == 0 or y[:, j].sum() == len(y):
                skipped.append(name)
                continue
            model = LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed)
            models[name] = model.fit(x, y[:, j])
        return cls(vectorizer, models), {"labels_trained": len(models), "labels_skipped": skipped,
                                         "vocabulary": len(vectorizer.vocabulary_)}

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        x = self.vectorizer.transform(texts)
        out = np.zeros((len(texts), len(label_names())))
        for j, name in enumerate(label_names()):
            if name in self.models:
                out[:, j] = self.models[name].predict_proba(x)[:, 1]
        return out

    def predict(self, texts: list[str]) -> np.ndarray:
        cut = np.array([self.thresholds.get(n, 0.5) for n in label_names()])
        return (self.predict_proba(texts) >= cut).astype(int)

    def extract(self, text_clean: str) -> list[AspectMention]:
        row = self.predict([text_clean])[0]
        return [AspectMention(*label_names()[j].split(":")) for j in np.flatnonzero(row)]

    def extract_df(self, reviews: pd.DataFrame, column: str = TEXT_COLUMN) -> pd.DataFrame:
        from greenchoice.nlp.dataset import to_review_aspects

        return to_review_aspects(reviews["review_id"].tolist(),
                                 self.predict(reviews[column].tolist()), self.method)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "models": self.models,
                     "thresholds": self.thresholds, "labels": label_names()}, path)

    @classmethod
    def load(cls, path: Path) -> TfidfExtractor:
        saved = joblib.load(path)  # only load files this project wrote (joblib runs pickle)
        if saved["labels"] != label_names():
            raise ValueError(f"{path}: model farklı bir etiket listesiyle eğitilmiş, yeniden eğitin")
        return cls(saved["vectorizer"], saved["models"], saved["thresholds"])
