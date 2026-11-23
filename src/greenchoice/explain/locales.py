"""Explanation sentences and number formats per language (tr / en / de).

Turkish is the original wording and must not change without reason: the pipeline stores it in
the database. Every language has the same keys and the same {placeholders}; a test checks this.
"""

from __future__ import annotations

TEMPLATES = {
    "tr": {
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
    },
    "en": {
        "energy_efficiency": {
            "positive": "Energy efficiency is better than similar products (energy class "
                        "{energy_class}, about {annual_kwh} kWh per year).",
            "negative": "Energy use is higher than similar products (energy class {energy_class}, "
                        "about {annual_kwh} kWh per year); the sustainability score is lower.",
        },
        "lifetime_cost": {
            "positive": "The {years}-year total cost of ownership (about {tco} TL) is lower than "
                        "similar products.",
            "negative": "The {years}-year total cost of ownership (about {tco} TL) is higher than "
                        "similar products.",
        },
        "durability": {
            "positive": "User reviews are positive about durability ({durability_pos} positive, "
                        "{durability_neg} negative reviews).",
            "negative": "Durability complaints stand out in the reviews ({durability_neg} negative, "
                        "{durability_pos} positive reviews).",
        },
        "service": {
            "positive": "The share of reviews with service or failure complaints is low ({issue_pct}%).",
            "negative": "The share of reviews with service or failure complaints is high ({issue_pct}%).",
        },
        "price_advantage": {
            "positive": "The price is favourable compared with similar products ({price} TL).",
            "negative": "The price is high compared with similar products ({price} TL).",
        },
        "satisfaction": {
            "positive": "User satisfaction is high (average {rating}/5, {rating_count} ratings).",
            "negative": "User satisfaction is low (average {rating}/5, {rating_count} ratings).",
        },
    },
    "de": {
        "energy_efficiency": {
            "positive": "Die Energieeffizienz ist besser als bei vergleichbaren Produkten "
                        "(Energieklasse {energy_class}, ca. {annual_kwh} kWh pro Jahr).",
            "negative": "Der Energieverbrauch ist höher als bei vergleichbaren Produkten "
                        "(Energieklasse {energy_class}, ca. {annual_kwh} kWh pro Jahr); die "
                        "Nachhaltigkeitsbewertung sinkt.",
        },
        "lifetime_cost": {
            "positive": "Die Gesamtkosten über {years} Jahre (ca. {tco} TL) sind niedriger als bei "
                        "vergleichbaren Produkten.",
            "negative": "Die Gesamtkosten über {years} Jahre (ca. {tco} TL) sind höher als bei "
                        "vergleichbaren Produkten.",
        },
        "durability": {
            "positive": "Die Nutzerbewertungen äußern sich positiv zur Haltbarkeit "
                        "({durability_pos} positive, {durability_neg} negative Bewertungen).",
            "negative": "In den Bewertungen fallen Beschwerden zur Haltbarkeit auf "
                        "({durability_neg} negative, {durability_pos} positive Bewertungen).",
        },
        "service": {
            "positive": "Der Anteil der Bewertungen mit Service- oder Defektbeschwerden ist niedrig "
                        "({issue_pct} %).",
            "negative": "Der Anteil der Bewertungen mit Service- oder Defektbeschwerden ist hoch "
                        "({issue_pct} %).",
        },
        "price_advantage": {
            "positive": "Der Preis ist im Vergleich zu ähnlichen Produkten günstig ({price} TL).",
            "negative": "Der Preis ist im Vergleich zu ähnlichen Produkten hoch ({price} TL).",
        },
        "satisfaction": {
            "positive": "Die Nutzerzufriedenheit ist hoch (durchschnittlich {rating}/5, "
                        "{rating_count} Bewertungen).",
            "negative": "Die Nutzerzufriedenheit ist niedrig (durchschnittlich {rating}/5, "
                        "{rating_count} Bewertungen).",
        },
    },
}

NO_SERVICE_ISSUES = {
    "tr": "Yorumlarda servis veya arıza şikâyetine rastlanmadı.",
    "en": "No service or failure complaints were found in the reviews.",
    "de": "In den Bewertungen wurden keine Service- oder Defektbeschwerden gefunden.",
}

GENERIC = {
    "tr": {"positive": "{criterion_name} benzer ürünlerin ortalamasından iyi.",
           "negative": "{criterion_name} benzer ürünlerin ortalamasından zayıf."},
    "en": {"positive": "{criterion_name} is better than the average of similar products.",
           "negative": "{criterion_name} is weaker than the average of similar products."},
    "de": {"positive": "{criterion_name}: besser als der Durchschnitt vergleichbarer Produkte.",
           "negative": "{criterion_name}: schwächer als der Durchschnitt vergleichbarer Produkte."},
}

# (thousands separator, decimal separator)
SEPARATORS = {"tr": (".", ","), "en": (",", "."), "de": (".", ",")}
