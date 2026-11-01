import json
from pathlib import Path

import pytest

from greenchoice.collect.ecommerce import TrendyolSource
from greenchoice.collect.trendyol_product import parse_product
from greenchoice.pipeline import fetch_trendyol, main

FIXTURE = Path(__file__).parent / "fixtures" / "trendyol_product.html"  # real page, product facts only
URL = ("https://www.trendyol.com/bosch/wga25203tr-serie-4-camasir-makinesi-10-kg-1200-devir-"
       "p-1136461902")


@pytest.fixture(scope="module")
def html():
    return FIXTURE.read_text(encoding="utf-8")


class FakeClient:
    def __init__(self, html):
        self.html, self.requested = html, []

    def get_text(self, url):
        self.requested.append(url)
        return self.html


def with_property(html, name, value):
    """Fixture copy where one technical property has a different value."""
    data = json.loads(html.split('application/ld+json">')[1].split("</script>")[0])
    for prop in data["additionalProperty"]:
        if prop["name"] == name:
            prop["unitText"] = value
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def test_parses_the_product_facts(html):
    p = parse_product(html, "washing_machine")
    assert p["product_id"] == "ty-1136461902" and p["source"] == "trendyol"
    assert p["url"] == URL and p["category"] == "washing_machine"
    assert p["brand"] == "Bosch" and "WGA25203TR" in p["name"]
    assert p["price_tl"] == pytest.approx(30000.0)
    assert (p["rating_avg"], p["rating_count"], p["review_count"]) == (4.6, 108, 64)
    assert p["capacity"] == pytest.approx(10.0) and p["warranty_years"] == pytest.approx(3.0)
    assert p["warnings"] == []


def test_model_code_is_only_suggested_never_filled_in(html):
    p = parse_product(html, "washing_machine")
    assert p["model_code"] is None
    assert "WGA25203TR" in p["model_code_candidates"]


def test_no_review_text_or_author_is_returned(html):
    assert not {"review", "reviews", "author"} & set(parse_product(html, "washing_machine"))


def test_unreadable_values_become_warnings_not_guesses(html):
    p = parse_product(with_property(html, "Kapasite", "çok büyük"), "washing_machine")
    assert p["capacity"] is None
    assert any("Kapasite" in w for w in p["warnings"])


def test_warranty_in_months_is_converted_to_years(html):
    p = parse_product(with_property(html, "Garanti Süresi", "24 Ay"), "washing_machine")
    assert p["warranty_years"] == pytest.approx(2.0)


def test_page_without_product_data_fails_loudly():
    with pytest.raises(ValueError, match="Product"):
        parse_product("<html><body>captcha</body></html>", "washing_machine")


def test_source_reads_only_trendyol_product_pages_through_the_client(html):
    client = FakeClient(html)
    p = TrendyolSource(client).fetch_product(URL, "washing_machine")
    assert p["product_id"] == "ty-1136461902" and client.requested == [URL]
    with pytest.raises(ValueError, match="trendyol"):
        TrendyolSource(client).fetch_product("https://www.example.com/x-p-1", "washing_machine")
    assert client.requested == [URL]  # the foreign address was never requested


def test_search_and_review_discovery_stay_unavailable():
    source = TrendyolSource(FakeClient(""))
    with pytest.raises(NotImplementedError, match="robots"):
        list(source.iter_product_urls("washing_machine", 10))
    with pytest.raises(NotImplementedError, match="robots"):
        source.fetch_reviews({}, 10)


def test_cli_prints_the_product_json(html, monkeypatch, capsys):
    monkeypatch.setattr("greenchoice.pipeline.PoliteClient", lambda: FakeClient(html))
    main(["fetch-trendyol", "--url", URL, "--category", "washing_machine"])
    printed = json.loads(capsys.readouterr().out)
    assert printed[0]["product_id"] == "ty-1136461902"
    assert fetch_trendyol([URL], "washing_machine", FakeClient(html))[0]["price_tl"] == 30000.0
