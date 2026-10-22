"""Uzun vadeli toplam kullanım maliyeti (TCO).

TCO = fiyat + ömür (yıl) x (yıllık kWh x elektrik fiyatı + yıllık su m3 x su fiyatı)

Buzdolabında yıllık kWh doğrudan etikette yazar. Çamaşır makinesinde etiket 100 yıkama
başına kWh verir; yıllık değer kategori yapılandırmasındaki annual_cycles ile bulunur.
"""

from __future__ import annotations

import pandas as pd

from greenchoice.config import categories_config


def annual_kwh(row: pd.Series, cat_cfg: dict) -> float | None:
    if pd.notna(row.get("energy_kwh_per_year")):
        return float(row["energy_kwh_per_year"])
    cycles = cat_cfg.get("annual_cycles")
    if cycles and pd.notna(row.get("energy_kwh_per_100_cycles")):
        return float(row["energy_kwh_per_100_cycles"]) * cycles / 100
    return None


def annual_water_m3(row: pd.Series, cat_cfg: dict) -> float:
    cycles = cat_cfg.get("annual_cycles")
    if cycles and pd.notna(row.get("water_l_per_cycle")):
        return float(row["water_l_per_cycle"]) * cycles / 1000
    return 0.0


def add_tco(products: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or categories_config()
    defaults = cfg["defaults"]
    out = products.copy()
    kwh, tco = [], []
    for _, row in out.iterrows():
        cat_cfg = cfg["categories"].get(row["category"], {})
        k = annual_kwh(row, cat_cfg)
        kwh.append(k)
        if k is None or pd.isna(row.get("price_tl")):
            tco.append(None)
            continue
        yearly = (k * defaults["electricity_price_tl_per_kwh"]
                  + annual_water_m3(row, cat_cfg) * defaults["water_price_tl_per_m3"])
        tco.append(float(row["price_tl"]) + cat_cfg.get("lifetime_years", 10) * yearly)
    out["annual_kwh"] = pd.to_numeric(pd.Series(kwh, index=out.index), errors="coerce")
    out["tco_tl"] = pd.to_numeric(pd.Series(tco, index=out.index), errors="coerce")
    return out
