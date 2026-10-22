"""ML modelleri ile karşılaştırma (Aşama 3, Kişi A).

Hedef (y): data/annotations/product_labels.csv'deki uzlaşılmış manuel etiketler
(recommended / neutral / not_recommended). Girdi (X): kriter alt skorları ve/veya
ham özellikler. Küçük veri setinde stratified k-fold cross-validation kullanılır.
"""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


def build_models(random_state: int = 42) -> dict:
    models = {
        "logreg": make_pipeline(StandardScaler(),
                                LogisticRegression(max_iter=1000, class_weight="balanced")),
        "random_forest": RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                random_state=random_state),
    }
    try:
        from xgboost import XGBClassifier  # ml extra'sı: pip install -e ".[ml]"
        models["xgboost"] = XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                                          random_state=random_state, eval_metric="mlogloss")
    except ImportError:
        pass
    return models


def compare_models(X: pd.DataFrame, y: pd.Series, folds: int = 5) -> pd.DataFrame:
    """Her model için cross-validation accuracy ve macro F1 (ortalama ± std)."""
    y_enc = LabelEncoder().fit_transform(y)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    rows = []
    for name, model in build_models().items():
        res = cross_validate(model, X, y_enc, cv=cv, scoring=["accuracy", "f1_macro"])
        rows.append({
            "model": name,
            "accuracy": res["test_accuracy"].mean(),
            "accuracy_std": res["test_accuracy"].std(),
            "f1_macro": res["test_f1_macro"].mean(),
            "f1_macro_std": res["test_f1_macro"].std(),
        })
    return pd.DataFrame(rows).sort_values("f1_macro", ascending=False)
