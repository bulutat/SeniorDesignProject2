"""Choosing which candidate products join the list (decision 17c).

Rule: rank by rating count, whatever the source and whether EPREL has the model (so the EPREL
match rate stays a finding, not something the selection engineered). Only products with enough
ratings are considered, one entry per model (the one with more ratings), no more than a cap per
brand, and models we already hold are skipped. Products without a model code stay in the pool.
"""

from __future__ import annotations

import re

import pandas as pd

from greenchoice.preprocess.text import tr_lower

POOL_COLUMNS = ["product_id", "source", "url", "category", "brand", "name", "price_tl",
                "rating_avg", "rating_count", "model_codes"]
KNOWN_BRANDS = ["Bosch", "Siemens", "Samsung", "LG", "Beko", "Arçelik", "Vestel", "Grundig", "Profilo",
                "Altus", "Regal", "Hoover", "Electrolux", "Candy", "Whirlpool", "Miele", "Haier",
                "Hisense", "Sharp", "Teka", "Kumtel", "Finlux", "Franke", "Fakir", "Daewoo", "Midea"]
_PREFIX_MIN = 8  # a held code this long also covers market-suffixed store codes (WW90CGC04DAE -> ...AH)


def _brand(guess: str, title: str) -> str:
    text = tr_lower(f"{guess} {title}")
    hits = [(m.start(), b) for b in KNOWN_BRANDS
            if (m := re.search(rf"(?<!\w){re.escape(tr_lower(b))}(?!\w)", text))]
    if hits:
        return min(hits)[1]
    return guess.title() if guess and not any(c.isdigit() for c in guess) else "Diğer"


def pool_from_sources(listings: pd.DataFrame | None, trendyol: list[dict] | None) -> pd.DataFrame:
    rows = []
    for r in (listings.to_dict("records") if listings is not None else []):
        codes = r["model_code_candidates"]
        rows.append({**{k: r[k] for k in ("product_id", "source", "url", "category", "name", "price_tl",
                                          "rating_avg", "rating_count")},
                     "brand": _brand(str(r["brand_guess"]), r["name"]),
                     "model_codes": [c.strip() for c in codes.split("|")] if isinstance(codes, str) else []})
    for r in trendyol or []:
        rows.append({**{k: r[k] for k in ("product_id", "source", "url", "category", "name", "price_tl",
                                          "rating_avg", "rating_count")},
                     "brand": _brand(str(r.get("brand") or ""), r["name"]),
                     "model_codes": list(r["model_code_candidates"])})
    return pd.DataFrame(rows, columns=POOL_COLUMNS)


COMPACT_FRIDGE = re.compile(r"\bmini\b|minibar|b[üu]ro|ofis|tezg[aâ]h|otel|şarap")  # not household fridges
_UNITS = {"kg", "lt", "l", "litre", "devir"}
_STOP = {"çamaşır", "buzdolabı", "no", "nofrost", "yıkama", "kapasiteli"}


def _title_key(name: str) -> str | None:
    """"Beko CMX 10120 10 Kg Çamaşır Makinesi" and "Beko CMX 10120 Çamaşır Makinesi" -> "beko cmx 10120".
    None when fewer than two words remain (brand only): such titles are not matched with each other."""
    tokens = tr_lower(name).replace(",", " ").split()
    words = []
    for i, token in enumerate(tokens):
        following = tokens[i + 1] if i + 1 < len(tokens) else ""
        if token in _STOP or (token.isdigit() and following in _UNITS) or token in _UNITS:
            break
        words.append(token)
    return " ".join(words) if len(words) >= 3 else None


def _key(model_codes: list[str], product_id: str, name: str) -> str:
    if model_codes:
        return model_codes[0].upper()
    title = _title_key(name)
    return f"t:{title}" if title else f"id:{product_id}"


def _same(a: str, b: str) -> bool:
    """Same model code, or one is the other plus a market suffix (RT47CG6636WW / ...WWTR)."""
    if a.startswith(("t:", "id:")) or b.startswith(("t:", "id:")):
        return a == b
    return a == b or (min(len(a), len(b)) >= _PREFIX_MIN and (a.startswith(b) or b.startswith(a)))


def _held(key: str, held: set[str]) -> bool:
    return any(_same(key, h) for h in held)


def select_products(pool: pd.DataFrame, existing: pd.DataFrame, target: int = 40, min_ratings: int = 30,
                    brand_cap: int = 12) -> tuple[pd.DataFrame, dict]:
    if target < 1 or brand_cap < 1:
        raise ValueError("target ve brand_cap en az 1 olmalı")
    existing = existing.reindex(columns=["product_id", "category", "brand", "model_code"])
    held_keys = {str(m).strip().upper() for m in existing["model_code"].dropna() if str(m).strip()}
    held_ids = set(existing["product_id"].dropna())
    keys = [_key(c, p, n) for c, p, n in zip(pool["model_codes"], pool["product_id"], pool["name"], strict=True)]
    pool = pool.assign(model_key=keys, has_model_code=pool["model_codes"].map(bool))
    chosen, report = [], {}
    for category in sorted(set(pool["category"]) | set(existing["category"].dropna())):
        have = existing[existing["category"] == category]
        need = max(target - len(have), 0)
        brands = have["brand"].map(lambda b: tr_lower(str(b))).value_counts().to_dict()
        cands = pool[(pool["category"] == category) & (pool["rating_count"].fillna(0) >= min_ratings)
                     & ~pool["product_id"].isin(held_ids)]
        cands = cands[~cands["model_key"].map(lambda k: _held(k, held_keys))]
        excluded = 0
        if category == "refrigerator":
            compact = cands["name"].map(lambda n: bool(COMPACT_FRIDGE.search(tr_lower(n))))
            excluded, cands = int(compact.sum()), cands[~compact]
        cands = cands.sort_values("rating_count", ascending=False, kind="stable")
        picked, seen = [], []
        for row in cands.itertuples():
            if len(picked) == need:
                break
            brand = tr_lower(row.brand)
            if _held(row.model_key, set(seen)) or brands.get(brand, 0) >= brand_cap:
                continue
            seen.append(row.model_key)
            brands[brand] = brands.get(brand, 0) + 1
            picked.append(row.Index)
        chosen.append(cands.loc[picked])
        report[category] = {"have": len(have), "need": need, "chosen": len(picked),
                            "shortfall": need - len(picked), **({"excluded_compact": excluded} if excluded else {})}
    table = pd.concat(chosen) if chosen else pool.iloc[0:0]
    return table.drop(columns=["model_key"]).reset_index(drop=True), report
