"""BERTurk tabanlı çıkarıcı (Aşama 2, Kişi A).

Plan:
- Görev: yorum (veya cümle) başına çok etiketli sınıflandırma; etiketler "aspect:polarity"
  (ör. "durability:neg"). Etiket listesi config/aspects.yaml'dan gelir.
- Model: dbmdz/bert-base-turkish-cased, sigmoid çıkışlı sınıflandırma başı.
- Eğitim verisi: data/annotations/reviews_gold.csv (docs/annotation-guideline.md).
- Kurulum: pip install -e ".[nlp]"
- Eğitilen model models/ altına kaydedilir (repoya girmez).
"""

from __future__ import annotations

from greenchoice.nlp.base import AspectExtractor, AspectMention

MODEL_NAME = "dbmdz/bert-base-turkish-cased"


class TransformerExtractor(AspectExtractor):
    method = "berturk_v0"

    def __init__(self, model_dir: str, threshold: float = 0.5):
        self.model_dir = model_dir
        self.threshold = threshold
        raise NotImplementedError("Aşama 2: fine-tune sonrası yükleme kodu yazılacak")

    def extract(self, text_clean: str) -> list[AspectMention]:
        raise NotImplementedError
