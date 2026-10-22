"""Aspect çıkarımı için Precision / Recall / F1 (Aşama 2).

gold ve pred aynı biçimdedir: review_id, aspect, polarity (yorum başına 0..n satır).
review_ids, etiketlenmiş tüm yorumların listesidir; hiç aspect içermeyen yorumlar
da bu sayede değerlendirmeye girer.
"""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer


def _label_sets(df: pd.DataFrame, review_ids: list) -> list[set[str]]:
    labels = (df.assign(label=df["aspect"] + ":" + df["polarity"])
                .groupby("review_id")["label"].apply(set))
    return [labels.get(rid, set()) for rid in review_ids]


def evaluate_aspects(gold: pd.DataFrame, pred: pd.DataFrame, review_ids: list) -> pd.DataFrame:
    y_true = _label_sets(gold, review_ids)
    y_pred = _label_sets(pred[pred["review_id"].isin(review_ids)], review_ids)

    mlb = MultiLabelBinarizer()
    mlb.fit(y_true + y_pred)
    t, p = mlb.transform(y_true), mlb.transform(y_pred)

    prec, rec, f1, support = precision_recall_fscore_support(t, p, zero_division=0)
    rows = [{"label": lbl, "precision": pr, "recall": rc, "f1": f, "support": int(s)}
            for lbl, pr, rc, f, s in zip(mlb.classes_, prec, rec, f1, support, strict=True)]
    for avg in ("micro", "macro"):
        pr, rc, f, _ = precision_recall_fscore_support(t, p, average=avg, zero_division=0)
        rows.append({"label": f"[{avg}]", "precision": pr, "recall": rc, "f1": f,
                     "support": int(t.sum())})
    return pd.DataFrame(rows)
