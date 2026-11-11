"""Energy data from labels and titles. Products are invented."""

import pandas as pd
import pytest

from greenchoice.preprocess.energy_labels import (
    apply_energy_sources,
    class_from_title,
    load_energy_labels,
)


@pytest.mark.parametrize("name, expected", [
    ("Buzdolabı 506 lt E Enerji Sınıfı Geniş İç Hacim", "E"),
    ("No-Frost Buzdolabı 468 lt Enerji Sınıfı F Gümüş", "F"),
    ("9 kg Çamaşır Makinesi Enerji Sınıfı: A 1000 Devir", "A"),
    ("Çamaşır Makinesi A+++ Enerji Sınıfı", None),      # old scale, not convertible
    ("Çamaşır Makinesi Enerji Sınıfı A++", None),
    ("Gwm 101414 A 10 kg 1400 Devir", None),             # "A" is part of the model code
    (None, None),
])
def test_class_from_title(name, expected):
    assert class_from_title(name) == expected


def products():
    return pd.DataFrame({
        "product_id": ["eprel-1", "label-1", "shop-1", "title-1", "none-1"],
        "name": ["X E Enerji Sınıfı", "Y", "Z", "W F Enerji Sınıfı", "V"],
        "energy_class": ["B", None, "C", None, None],
        "energy_kwh_per_year": [200.0, None, None, None, None],
        "energy_kwh_per_100_cycles": [None] * 5,
        "water_l_per_cycle": [None] * 5,
        "capacity": [None] * 5,
        "eprel_matched": [True, False, False, False, False],
    })


LABELS = pd.DataFrame({
    "product_id": ["label-1", "eprel-1", "shop-1"],
    "energy_class": ["E", "G", "D"],
    "energy_kwh_per_year": [268.0, 999.0, 300.0],
    "source_url": ["https://x"] * 3, "checked_on": ["2026-11-10"] * 3,
})


def test_sources_are_applied_in_order_of_trust():
    out = apply_energy_sources(products(), LABELS).set_index("product_id")
    assert out.loc["eprel-1", ["energy_class", "energy_kwh_per_year"]].tolist() == ["B", 200.0]
    assert out.loc["label-1", ["energy_class", "energy_kwh_per_year"]].tolist() == ["E", 268.0]
    assert out.loc["shop-1", "energy_class"] == "D"          # official label outranks the shop
    assert out.loc["title-1", "energy_class"] == "F"
    assert pd.isna(out.loc["none-1", "energy_class"])
    assert out["energy_source"].fillna("none").to_dict() == {
        "eprel-1": "eprel", "label-1": "label", "shop-1": "label", "title-1": "title",
        "none-1": "none"}


def test_without_label_file_shop_and_title_still_count():
    out = apply_energy_sources(products()).set_index("product_id")
    assert out.loc["shop-1", "energy_source"] == "shop"
    assert out.loc["title-1", "energy_source"] == "title"


def test_label_file_is_validated(tmp_path):
    good = LABELS.drop(columns=[])
    good.to_csv(tmp_path / "ok.csv", index=False)
    assert len(load_energy_labels(tmp_path / "ok.csv")) == 3
    LABELS.assign(energy_class=["A+", "E", "E"]).to_csv(tmp_path / "old.csv", index=False)
    with pytest.raises(ValueError, match="satır 2"):
        load_energy_labels(tmp_path / "old.csv")
    LABELS.assign(source_url="www.x").to_csv(tmp_path / "url.csv", index=False)
    with pytest.raises(ValueError, match="https"):
        load_energy_labels(tmp_path / "url.csv")


def test_repository_label_file_is_valid():
    table = load_energy_labels(__import__("pathlib").Path("data/manual/energy_labels.csv"))
    assert table["product_id"].is_unique and len(table) >= 20
