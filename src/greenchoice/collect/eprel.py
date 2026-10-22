"""AB EPREL (European Product Registry for Energy Labelling) istemcisi.

TODO (Aşama 0, Kişi B): Erişim yöntemini doğrula. Seçenekler:
  1. Public API: ürün grubu + kayıt numarası ile sorgu; bazı uç noktalar API anahtarı ister
     (anahtar .env içindeki EPREL_API_KEY).
  2. Toplu dışa aktarım: ürün grubunun tamamı indirilip data/raw/eprel_<grup>.csv olarak saklanır.
Eşleştirme her iki durumda da model koduyla yapılır (preprocess.matching).

Aşağıdaki URL ve alan adları doğrulanmamış tahminlerdir; ilk denemede kontrol edilmeli.
"""

from __future__ import annotations

import os

EPREL_BASE = "https://eprel.ec.europa.eu/api"  # TODO: doğrula

# EPREL alanı -> PRODUCT_COLUMNS alanı. TODO: gerçek alan adlarıyla güncelle.
FIELD_MAP = {
    "refrigeratingappliances2019": {
        "energyClass": "energy_class",
        "energyConsAnnual": "energy_kwh_per_year",
        "noise": "noise_db",
    },
    "washingmachines2019": {
        "energyClass": "energy_class",
        "energyConsPer100Cycle": "energy_kwh_per_100_cycles",
        "waterCons": "water_l_per_cycle",
        "noise": "noise_db",
    },
}


class EprelClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("EPREL_API_KEY")

    def search_model(self, product_group: str, model_code: str) -> dict | None:
        raise NotImplementedError("Aşama 0-1: EPREL erişimi doğrulandıktan sonra yazılacak")


def to_product_fields(product_group: str, record: dict) -> dict:
    """EPREL kaydını PRODUCT_COLUMNS alanlarına çevirir."""
    mapping = FIELD_MAP.get(product_group, {})
    return {ours: record.get(theirs) for theirs, ours in mapping.items()}
