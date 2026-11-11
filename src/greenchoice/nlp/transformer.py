"""BERTurk aspect extractor (task A2.1): loads a model fine-tuned in Colab and predicts labels.

- Task: multi-label classification over "aspect:polarity" (nlp/dataset.py label_names), sigmoid
  outputs. Base model dbmdz/bert-base-turkish-cased.
- Training: notebooks/03_A_berturk_egitim.ipynb on the files `greenchoice export-nlp-data`
  writes. The notebook saves the model, the tokenizer and thresholds.json into one folder,
  which goes under models/ (not committed).
- Install: pip install -e ".[nlp]"
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from greenchoice.nlp.base import AspectExtractor, AspectMention
from greenchoice.nlp.dataset import TEXT_COLUMN, label_names, to_review_aspects

MODEL_NAME = "dbmdz/bert-base-turkish-cased"
MAX_LENGTH = 256


class TransformerExtractor(AspectExtractor):
    method = "berturk_v0"

    def __init__(self, model_dir: str, batch_size: int = 32, device: str | None = None):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device)
        self.model.eval()
        self.batch_size = batch_size
        labels = [self.model.config.id2label[i] for i in range(self.model.config.num_labels)]
        if labels != label_names():
            raise ValueError(f"{model_dir}: model etiketleri {labels}, beklenen {label_names()}")
        path = Path(model_dir) / "thresholds.json"
        self.thresholds = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        out = []
        with self._torch.no_grad():
            for start in range(0, len(texts), self.batch_size):
                batch = self.tokenizer(texts[start:start + self.batch_size], padding=True,
                                       truncation=True, max_length=MAX_LENGTH,
                                       return_tensors="pt").to(self.device)
                out.append(self._torch.sigmoid(self.model(**batch).logits).cpu().numpy())
        return np.vstack(out) if out else np.zeros((0, len(label_names())))

    def predict(self, texts: list[str]) -> np.ndarray:
        cut = np.array([self.thresholds.get(n, 0.5) for n in label_names()])
        return (self.predict_proba(texts) >= cut).astype(int)

    def extract(self, text_clean: str) -> list[AspectMention]:
        row = self.predict([text_clean])[0]
        return [AspectMention(*label_names()[j].split(":")) for j in np.flatnonzero(row)]

    def extract_df(self, reviews: pd.DataFrame, column: str = TEXT_COLUMN) -> pd.DataFrame:
        return to_review_aspects(reviews["review_id"].tolist(),
                                 self.predict(reviews[column].tolist()), self.method)
