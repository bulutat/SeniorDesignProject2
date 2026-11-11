import pandas as pd
import pytest

from greenchoice.nlp.rule_based import RuleBasedExtractor
from greenchoice.preprocess.reviews import clean_reviews
from greenchoice.preprocess.scope import mentions_logistics, product_text
from greenchoice.preprocess.text import normalize_text


def scoped(raw: str) -> str:
    return product_text(normalize_text(raw))


@pytest.mark.parametrize("raw,expected", [
    ("Çoooook güzel", "çok güzel"),
    ("beğendimmmm!!", "beğendim"),
    ("saat tam geldi", "saat tam geldi"),   # çift harf korunur
    ("Süper 👍🏻 ürün 😊", "süper ürün"),
    ("2000 watt", "2000 watt"),             # rakamlar korunur
])
def test_normalize_handles_elongation_and_emoji(raw, expected):
    assert normalize_text(raw) == expected


@pytest.mark.parametrize("raw", [
    "Çok hızlı ve sorunsuz şekilde elime ulaştı, satıcıya teşekkürler",
    "Ürün sağlam geldi",
    "Sorunsuz bir alışverişti",
    "Kurulum sorunsuz yapıldı",
    "Cihaz sağlam kolilenmiş",
])
def test_delivery_context_removes_the_ambiguous_word(raw):
    remaining = scoped(raw)
    assert "sorunsuz" not in remaining and "sağlam" not in remaining


@pytest.mark.parametrize("raw", [
    "3 yıldır sorunsuz",
    "Kaliteli ve sağlam",
    "Kalite sağlamlık istiyorsan bunu al",
    "Kurulum yapıldı, sorunsuz çalışıyor",  # ürün kullanımı anlatılıyor
])
def test_durability_statements_are_kept(raw):
    assert scoped(raw) == normalize_text(raw)


def test_other_product_information_next_to_logistics_is_not_lost():
    text = "Ürün çok güzel ve sessiz sadece kargo geç geldi"
    assert scoped(text) == normalize_text(text)


def test_clean_reviews_keeps_raw_text_and_flags_logistics():
    df = pd.DataFrame({
        "review_id": ["1", "2"], "product_id": ["p", "p"], "rating": [1, 5],
        "text": ["Kargo çok geç geldi, satıcı ilgilenmedi", "Üç yıldır sorunsuz çalışıyor"],
        "date": [None, None],
    })
    out = clean_reviews(df).set_index("review_id")
    assert bool(out.loc["1", "mentions_logistics"]) is True
    assert bool(out.loc["2", "mentions_logistics"]) is False
    assert out.loc["1", "text"] == "Kargo çok geç geldi, satıcı ilgilenmedi"
    assert not mentions_logistics("kelime")  # kelime başından aranır, "elime" ile karışmaz


def test_delivery_praise_is_not_durability_for_the_extractor():
    reviews = pd.DataFrame({"review_id": ["1", "2"],
                            "text_product": [scoped("Sorunsuz ulaştı elime"),
                                             scoped("Yıllardır sorunsuz çalışıyor")]})
    found = RuleBasedExtractor().extract_df(reviews, column="text_product")
    assert found["review_id"].tolist() == ["2"]
