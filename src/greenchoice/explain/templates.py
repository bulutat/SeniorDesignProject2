"""Kriter katkılarını Türkçe açıklama cümlelerine çevirir.

Katkı (impact): kriterin, ürünün skorunu kategori ortalamasına göre kaç puan
yukarı/aşağı çektiği. Ağırlıklı baseline'da doğrudan hesaplanır; ML modellerinde
aynı yapı SHAP değerleriyle doldurulacak (Aşama 4, Kişi A).
"""

from __future__ import annotations

import math
from string import Formatter

import pandas as pd

from greenchoice.explain.locales import GENERIC, NO_SERVICE_ISSUES, SEPARATORS
from greenchoice.explain.locales import TEMPLATES as LOCALE_TEMPLATES
from greenchoice.i18n import DEFAULT_LANGUAGE, check_language, display_name

# Sentences per language live in locales.py; these names keep the Turkish set importable.
TEMPLATES = LOCALE_TEMPLATES[DEFAULT_LANGUAGE]
SERVICE_NO_ISSUES = NO_SERVICE_ISSUES[DEFAULT_LANGUAGE]

# Yorum tabanlı açıklamalar yalnızca o yönde en az bir yorum varsa üretilir
EVIDENCE = {
    ("durability", "positive"): "durability_pos",
    ("durability", "negative"): "durability_neg",
}


def _missing(v) -> bool:
    if v is None or v is pd.NA:
        return True
    return isinstance(v, float) and math.isnan(v)


def _tl(v, lang: str = DEFAULT_LANGUAGE) -> str:
    return f"{v:,.0f}".replace(",", SEPARATORS[lang][0])


def template_values(row: dict, lifetime_years: int, lang: str = DEFAULT_LANGUAGE) -> dict:
    def num(key):
        v = row.get(key)
        return None if _missing(v) else v

    rating = num("rating_avg") if num("rating_avg") is not None else num("review_rating_avg")
    rating_count = num("rating_count") if num("rating_count") is not None else num("n_reviews")
    issue = num("service_issue_rate")
    return {
        "energy_class": num("energy_class"),
        "annual_kwh": None if num("annual_kwh") is None else f"{num('annual_kwh'):.0f}",
        "tco": None if num("tco_tl") is None else _tl(num("tco_tl"), lang),
        "years": lifetime_years,
        "durability_pos": int(num("durability_pos") or 0),
        "durability_neg": int(num("durability_neg") or 0),
        "issue_pct": None if issue is None else f"{100 * issue:.0f}",
        "price": None if num("price_tl") is None else _tl(num("price_tl"), lang),
        "rating": None if rating is None else f"{rating:.1f}".replace(".", SEPARATORS[lang][1]),
        "rating_count": None if rating_count is None else int(rating_count),
    }


def _render(template: str, values: dict) -> str | None:
    fields = [f for _, f, _, _ in Formatter().parse(template) if f]
    if any(values.get(f) is None for f in fields):
        return None
    return template.format(**values)


def _sentence(criterion: str, direction: str, name: str, values: dict, lang: str) -> str:
    template = LOCALE_TEMPLATES[lang].get(criterion, {}).get(direction, "")
    if criterion == "service" and values["issue_pct"] == "0":
        template = NO_SERVICE_ISSUES[lang]
    return _render(template, values) or GENERIC[lang][direction].format(criterion_name=name)


def build_explanations(row: dict, contributions: dict[str, float], imputed: list[str],
                       criteria_cfg: dict, lifetime_years: int,
                       top_k: int = 4, min_impact: float = 1.0,
                       lang: str = DEFAULT_LANGUAGE) -> list[dict]:
    check_language(lang)
    values = template_values(row, lifetime_years, lang)
    ranked = sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)
    out = []
    for criterion, impact in ranked:
        if criterion in imputed or abs(impact) < min_impact:
            continue
        direction = "positive" if impact > 0 else "negative"
        evidence = EVIDENCE.get((criterion, direction))
        if evidence and not values[evidence]:
            # Yorumlarda bu yönde hiç kanıt yoksa açıklama üretme (ör. "0 olumsuz yorum")
            continue
        name = display_name(criteria_cfg[criterion], lang)
        out.append({"criterion": criterion, "criterion_name": name, "direction": direction,
                    "impact": round(impact, 1),
                    "text": _sentence(criterion, direction, name, values, lang)})
        if len(out) == top_k:
            break
    return out


def localize_explanations(stored: list[dict], row: dict, criteria_cfg: dict,
                          lifetime_years: int, lang: str) -> list[dict]:
    """Re-render stored (Turkish) explanations in another language from the same product row.

    Which criteria are explained, their direction and impact are kept as stored; only
    criterion_name and text change. Turkish returns the stored list unchanged.
    """
    if check_language(lang) == DEFAULT_LANGUAGE:
        return stored
    values = template_values(row, lifetime_years, lang)
    out = []
    for e in stored:
        name = display_name(criteria_cfg[e["criterion"]], lang)
        out.append(e | {"criterion_name": name,
                        "text": _sentence(e["criterion"], e["direction"], name, values, lang)})
    return out
