"""Anahtar ifade tabanlı baseline çıkarıcı (config/aspects.yaml)."""

from __future__ import annotations

import re

from greenchoice.config import aspects_config
from greenchoice.nlp.base import AspectExtractor, AspectMention
from greenchoice.preprocess.text import normalize_text


class RuleBasedExtractor(AspectExtractor):
    method = "rule_based_v0"

    def __init__(self, aspects: dict | None = None):
        aspects = aspects or aspects_config()["aspects"]
        patterns = []
        for aspect, spec in aspects.items():
            for polarity in ("pos", "neg"):
                for phrase in spec.get(polarity) or []:
                    norm = normalize_text(phrase)
                    # Kelime başından eşleş, eklere izin ver: "dayanıklı" -> "dayanıklılığı"
                    patterns.append((len(norm), aspect, polarity,
                                     re.compile(r"(?<!\w)" + re.escape(norm))))
        # Uzun ifadeler önce: "arızasız" "arıza"dan, "çok sessiz" "çok ses"ten önce eşleşir
        patterns.sort(key=lambda p: p[0], reverse=True)
        self._patterns = [(a, pol, rx) for _, a, pol, rx in patterns]

    def extract(self, text_clean: str) -> list[AspectMention]:
        taken: list[tuple[int, int]] = []
        mentions = []
        for aspect, polarity, rx in self._patterns:
            for m in rx.finditer(text_clean):
                s, e = m.span()
                if any(s < te and ts < e for ts, te in taken):
                    continue
                taken.append((s, e))
                mentions.append(AspectMention(aspect, polarity, m.group(0)))
        return mentions
