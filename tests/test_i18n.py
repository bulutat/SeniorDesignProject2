"""Language support: display names, labels and explanation sentences in tr / en / de."""

from string import Formatter
from typing import get_args

import pytest

from greenchoice.config import categories_config
from greenchoice.contracts import LABELS
from greenchoice.explain.locales import GENERIC, NO_SERVICE_ISSUES, TEMPLATES
from greenchoice.explain.templates import build_explanations, localize_explanations
from greenchoice.i18n import DEFAULT_LANGUAGE, LANGUAGES, display_name, label_text
from greenchoice.schemas import Language


def fields(template: str) -> set[str]:
    return {f for _, f, _, _ in Formatter().parse(template) if f}


def test_api_language_type_matches_supported_languages():
    assert set(get_args(Language)) == set(LANGUAGES)
    assert DEFAULT_LANGUAGE == "tr"


def test_labels_in_every_language_and_turkish_unchanged():
    assert {lang: label_text("recommended", lang) for lang in LANGUAGES} == {
        "tr": "Önerilir", "en": "Recommended", "de": "Empfohlen"}
    for label, text in LABELS.items():
        assert label_text(label, "tr") == text


def test_every_criterion_and_category_has_a_name_in_every_language():
    cfg = categories_config()
    for entry in [*cfg["criteria"].values(), *cfg["categories"].values()]:
        for lang in LANGUAGES:
            assert display_name(entry, lang).strip(), (entry["name"], lang)
    assert display_name(cfg["categories"]["refrigerator"], "tr") == "Buzdolabı"
    assert display_name(cfg["categories"]["refrigerator"], "en") == "Refrigerator"
    assert display_name(cfg["criteria"]["durability"], "de") == "Haltbarkeit"


def test_unknown_language_is_rejected():
    with pytest.raises(ValueError):
        label_text("neutral", "fr")
    with pytest.raises(ValueError):
        display_name({"name": "X"}, "fr")


def test_templates_have_the_same_keys_and_placeholders_in_every_language():
    base = TEMPLATES["tr"]
    for lang in LANGUAGES:
        assert set(TEMPLATES[lang]) == set(base), lang
        for criterion, by_dir in base.items():
            for direction, text in by_dir.items():
                assert fields(TEMPLATES[lang][criterion][direction]) == fields(text), (lang, criterion)
        assert fields(GENERIC[lang]["positive"]) == {"criterion_name"}
        assert NO_SERVICE_ISSUES[lang]


ROW = {"energy_class": "C", "annual_kwh": 182.0, "tco_tl": 45551.4, "price_tl": 38999.0,
       "durability_pos": 4, "durability_neg": 1, "service_issue_rate": 0.25,
       "rating_avg": 4.6, "rating_count": 1812, "n_reviews": 5}
CRITERIA = categories_config()["criteria"]
CONTRIB = {"energy_efficiency": 8.3, "lifetime_cost": -5.0, "durability": 3.9,
           "service": -2.0, "price_advantage": -1.5, "satisfaction": 2.2}


def test_turkish_build_is_the_default():
    assert build_explanations(ROW, CONTRIB, [], CRITERIA, 12) == \
        build_explanations(ROW, CONTRIB, [], CRITERIA, 12, lang="tr")


def test_languages_keep_criteria_order_impacts_and_numbers():
    tr = build_explanations(ROW, CONTRIB, [], CRITERIA, 12)
    en = build_explanations(ROW, CONTRIB, [], CRITERIA, 12, lang="en")
    de = build_explanations(ROW, CONTRIB, [], CRITERIA, 12, lang="de")
    key = [(e["criterion"], e["direction"], e["impact"]) for e in tr]
    assert key == [(e["criterion"], e["direction"], e["impact"]) for e in en]
    assert key == [(e["criterion"], e["direction"], e["impact"]) for e in de]
    assert en[0]["text"] == ("Energy efficiency is better than similar products "
                             "(energy class C, about 182 kWh per year).")
    assert en[0]["criterion_name"] == "Energy efficiency"
    assert "45,551 TL" in en[1]["text"] and "45.551 TL" in de[1]["text"]
    assert "45.551 TL" in tr[1]["text"]


def test_rating_decimal_separator_follows_the_language():
    only_sat = {"satisfaction": 5.0}
    assert "4.6/5" in build_explanations(ROW, only_sat, [], CRITERIA, 12, lang="en")[0]["text"]
    assert "4,6/5" in build_explanations(ROW, only_sat, [], CRITERIA, 12, lang="de")[0]["text"]


def test_service_without_complaints_uses_the_special_sentence():
    row = ROW | {"service_issue_rate": 0.0}
    out = build_explanations(row, {"service": 3.0}, [], CRITERIA, 12, lang="en")
    assert out[0]["text"] == NO_SERVICE_ISSUES["en"]


def test_missing_values_fall_back_to_the_generic_sentence():
    row = ROW | {"price_tl": None}
    out = build_explanations(row, {"price_advantage": 4.0}, [], CRITERIA, 12, lang="de")
    assert out[0]["text"] == "Preisvorteil: besser als der Durchschnitt vergleichbarer Produkte."


def test_localize_stored_explanations():
    stored = build_explanations(ROW, CONTRIB, [], CRITERIA, 12)
    assert localize_explanations(stored, ROW, CRITERIA, 12, "tr") == stored
    assert localize_explanations(stored, ROW, CRITERIA, 12, "en") == \
        build_explanations(ROW, CONTRIB, [], CRITERIA, 12, lang="en")
    assert stored[0]["text"].startswith("Enerji verimliliği")  # input is not modified
