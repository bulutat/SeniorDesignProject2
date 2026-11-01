"""Aspect çıkarıcılar için ortak arayüz.

Kural tabanlı, TF-IDF ve BERTurk yöntemlerinin hepsi bu arayüzü uygular; böylece
değerlendirme ve skorlama kodu hangi yöntemin kullanıldığından bağımsız kalır.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from greenchoice.contracts import REVIEW_ASPECT_COLUMNS


@dataclass(frozen=True)
class AspectMention:
    aspect: str
    polarity: str  # "pos" | "neg"
    evidence: str | None = None


class AspectExtractor(ABC):
    method: str

    @abstractmethod
    def extract(self, text_clean: str) -> list[AspectMention]:
        """Normalize edilmiş tek bir yorumdan aspect/duygu çiftlerini çıkarır."""

    def extract_df(self, reviews: pd.DataFrame, column: str = "text_clean") -> pd.DataFrame:
        """reviews (review_id, column) -> review_aspects tablosu."""
        rows = []
        for review_id, text in zip(reviews["review_id"], reviews[column], strict=True):
            seen = set()
            for m in self.extract(text):
                if (m.aspect, m.polarity) in seen:
                    continue
                seen.add((m.aspect, m.polarity))
                rows.append({"review_id": review_id, "aspect": m.aspect,
                             "polarity": m.polarity, "method": self.method,
                             "evidence": m.evidence})
        return pd.DataFrame(rows, columns=REVIEW_ASPECT_COLUMNS)
