"""Kriter katkılarını Türkçe açıklama cümlelerine çevirir.

Katkı (impact): kriterin, ürünün skorunu kategori ortalamasına göre kaç puan
yukarı/aşağı çektiği. Ağırlıklı baseline'da doğrudan hesaplanır; ML modellerinde
aynı yapı SHAP değerleriyle doldurulacak (Aşama 4, Kişi A).
"""

from __future__ import annotations

import math
from string import Formatter

import pandas as pd

TEMPLATES = {
    "energy_efficiency": {
        "positive": "Enerji verimliliği benzer ürünlerden iyi (enerji sınıfı {energy_class}, "
                    "yılda ~{annual_kwh} kWh).",
        "negative": "Enerji tüketimi benzer ürünlere göre yüksek (enerji sınıfı {energy_class}, "
                    "yılda ~{annual_kwh} kWh); sürdürülebilirlik puanı azaldı.",
    },
    "lifetime_cost": {
        "positive": "{years} yıllık toplam kullanım maliyeti (~{tco} TL) benzer ürünlerden düşük.",
        "negative": "{years} yıllık toplam kullanım maliyeti (~{tco} TL) benzer ürünlerden yüksek.",
    },
    "durability": {
        "positive": "Kullanıcı yorumlarında dayanıklılık olumlu ({durability_pos} olumlu, "
                    "{durability_neg} olumsuz yorum).",
        "negative": "Yorumlarda dayanıklılıkla ilgili şikâyetler öne çıkıyor ({durability_neg} "
                    "olumsuz, {durability_pos} olumlu yorum).",
    },
    "service": {
        "positive": "Servis veya arıza şikâyeti içeren yorum oranı düşük (%{issue_pct}).",
        "negative": "Servis veya arıza şikâyeti içeren yorum oranı yüksek (%{issue_pct}).",
    },
    "price_advantage": {
        "positive": "Benzer ürünlere göre fiyatı avantajlı ({price} TL).",
        "negative": "Benzer ürünlere göre fiyatı yüksek ({price} TL).",
    },
    "satisfaction": {
        "positive": "Kullanıcı memnuniyeti yüksek (ortalama {rating}/5, {rating_count} değerlendirme).",
        "negative": "Kullanıcı memnuniyeti düşük (ortalama {rating}/5, {rating_count} değerlendirme).",
    },
}
SERVICE_NO_ISSUES = "Yorumlarda servis veya arıza şikâyetine rastlanmadı."

# Yorum tabanlı açıklamalar yalnızca o yönde en az bir yorum varsa üretilir
EVIDENCE = {
    ("durability", "positive"): "durability_pos",
    ("durability", "negative"): "durability_neg",
}

GENERIC = {
    "positive": "{criterion_name} benzer ürünlerin ortalamasından iyi.",
    "negative": "{criterion_name} benzer ürünlerin ortalamasından zayıf.",
}


def _missing(v) -> bool:
    if v is None or v is pd.NA:
        return True
    return isinstance(v, float) and math.isnan(v)


def _tl(v) -> str:
    return f"{v:,.0f}".replace(",", ".")


def template_values(row: dict, lifetime_years: int) -> dict:
    def num(key):
        v = row.get(key)
        return None if _missing(v) else v

    rating = num("rating_avg") if num("rating_avg") is not None else num("review_rating_avg")
    rating_count = num("rating_count") if num("rating_count") is not None else num("n_reviews")
    issue = num("service_issue_rate")
    return {
        "energy_class": num("energy_class"),
        "annual_kwh": None if num("annual_kwh") is None else f"{num('annual_kwh'):.0f}",
        "tco": None if num("tco_tl") is None else _tl(num("tco_tl")),
        "years": lifetime_years,
        "durability_pos": int(num("durability_pos") or 0),
        "durability_neg": int(num("durability_neg") or 0),
        "issue_pct": None if issue is None else f"{100 * issue:.0f}",
        "price": None if num("price_tl") is None else _tl(num("price_tl")),
        "rating": None if rating is None else f"{rating:.1f}".replace(".", ","),
        "rating_count": None if rating_count is None else int(rating_count),
    }


def _render(template: str, values: dict) -> str | None:
    fields = [f for _, f, _, _ in Formatter().parse(template) if f]
    if any(values.get(f) is None for f in fields):
        return None
    return template.format(**values)


def build_explanations(row: dict, contributions: dict[str, float], imputed: list[str],
                       criteria_cfg: dict, lifetime_years: int,
                       top_k: int = 4, min_impact: float = 1.0) -> list[dict]:
    values = template_values(row, lifetime_years)
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
        name = criteria_cfg[criterion]["name"]
        template = TEMPLATES.get(criterion, {}).get(direction, "")
        if criterion == "service" and values["issue_pct"] == "0":
            template = SERVICE_NO_ISSUES
        text = (_render(template, values)
                or GENERIC[direction].format(criterion_name=name))
        out.append({"criterion": criterion, "criterion_name": name, "direction": direction,
                    "impact": round(impact, 1), "text": text})
        if len(out) == top_k:
            break
    return out
