import pytest
from fastapi.testclient import TestClient

from greenchoice.api.main import create_app


@pytest.fixture(scope="module")
def client(sample_db):
    path, _ = sample_db
    return TestClient(create_app(path))


def test_categories(client):
    cats = {c["id"]: c for c in client.get("/api/categories").json()}
    assert cats["refrigerator"]["product_count"] == 6
    assert len(cats["washing_machine"]["criteria"]) == 6


def test_products_sorted_by_score(client):
    items = client.get("/api/products", params={"category": "refrigerator"}).json()
    scores = [p["score"] for p in items]
    assert scores == sorted(scores, reverse=True)
    assert all(p["category"] == "refrigerator" for p in items)


def test_product_detail(client):
    d = client.get("/api/products/s-rf-01").json()
    assert d["energy_class"] == "C"
    assert d["tco_tl"] > d["price_tl"]
    assert set(d["sub_scores"]) == {"energy_efficiency", "lifetime_cost", "durability",
                                    "service", "price_advantage", "satisfaction"}
    assert d["explanations"]
    assert d["review_stats"]["n_reviews"] == 4


def test_unknown_product_is_404(client):
    assert client.get("/api/products/yok").status_code == 404


def test_compare_requires_two_to_four(client):
    assert client.get("/api/compare", params={"ids": "s-rf-01"}).status_code == 422
    res = client.get("/api/compare", params={"ids": "s-rf-01,s-rf-04"})
    assert [p["id"] for p in res.json()] == ["s-rf-01", "s-rf-04"]


def test_custom_weights_change_ranking(client):
    price_only = {k: 0 for k in ("energy_efficiency", "lifetime_cost", "durability",
                                 "service", "satisfaction")} | {"price_advantage": 1}
    res = client.post("/api/score", json={"category": "refrigerator", "weights": price_only})
    assert res.status_code == 200
    assert res.json()[0]["id"] == "s-rf-06"  # en ucuz buzdolabı


def test_language_defaults_to_the_original_turkish_response(client):
    assert client.get("/api/products/s-rf-01").json() == \
        client.get("/api/products/s-rf-01", params={"lang": "tr"}).json()


def test_english_names_labels_and_explanations(client):
    cats = {c["id"]: c for c in client.get("/api/categories", params={"lang": "en"}).json()}
    assert cats["refrigerator"]["name"] == "Refrigerator"
    assert {c["name"] for c in cats["refrigerator"]["criteria"]} >= {"Energy efficiency"}

    tr = client.get("/api/products/s-rf-01").json()
    en = client.get("/api/products/s-rf-01", params={"lang": "en"}).json()
    assert en["label_text"] in {"Recommended", "Neutral", "Not recommended"}
    assert en["name"] == tr["name"] and en["price_tl"] == tr["price_tl"]  # data is not translated
    assert [(e["criterion"], e["impact"]) for e in en["explanations"]] == \
        [(e["criterion"], e["impact"]) for e in tr["explanations"]]
    assert en["explanations"][0]["text"] != tr["explanations"][0]["text"]


def test_language_on_list_compare_and_custom_score(client):
    items = client.get("/api/products", params={"category": "refrigerator", "lang": "de"}).json()
    assert {p["label_text"] for p in items} <= {"Empfohlen", "Neutral", "Nicht empfohlen"}
    res = client.get("/api/compare", params={"ids": "s-rf-01,s-rf-04", "lang": "de"}).json()
    assert all(e["text"] for p in res for e in p["explanations"])
    scored = client.post("/api/score", params={"lang": "en"},
                         json={"category": "refrigerator", "weights": {}}).json()
    assert {p["label_text"] for p in scored} <= {"Recommended", "Neutral", "Not recommended"}


def test_unsupported_language_is_422(client):
    assert client.get("/api/categories", params={"lang": "fr"}).status_code == 422
