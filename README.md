# GreenChoice

AI-based decision support for sustainable and informed product choice.
COMP 491 senior design project, 2026–2027 Fall. Authors: Atahan Bulut, Ali Rubar Kal.
Advisor: Tuna Çakar.

GreenChoice scores products by more than price: energy consumption, long-term cost of
ownership, durability and user experience from reviews. It also explains why a product
received its score. The current scope is two categories (refrigerators and washing
machines) and a prototype, not a real-time marketplace system.

> **Status: skeleton.** The pipeline, API and UI run end to end on the **synthetic** data in
> `data/sample/`. Real data collection, BERTurk, ML models and SHAP are placeholders.
> Details: [Progress](#progress-and-changelog).

## Architecture

Two parts:

1. **Offline pipeline** (`greenchoice build`): collects and cleans data, analyses reviews,
   computes scores and explanations, and writes everything to one SQLite file.
2. **Service** (FastAPI + React): only reads that database. The one computation it does is
   re-scoring with user-chosen weights (a cheap weighted sum).

```
sources (e-commerce, EPREL)
   -> collect -> preprocess (clean, EPREL match, TCO)
   -> nlp (aspect extraction) -> nlp.aggregate (per-product review features)
   -> scoring.criteria (0-1 sub-scores) -> scoring (weighted / ML) -> explain
   -> SQLite (products, reviews, review_aspects, product_features, scores)
   -> FastAPI -> React UI
```

Scoring (`weighted_v0`): six criteria (energy efficiency, lifetime cost, durability,
service and failures, price advantage, satisfaction), each scaled to 0-1, combined with
per-category weights from `config/categories.yaml`. Score >= 70 is *recommended*, >= 45
*neutral*, below that *not recommended*. Missing criteria are filled with the category
median and are never used in explanations.

More: [docs/architecture.md](docs/architecture.md) (in Turkish).

## Folder structure

```
config/          categories, criteria weights, aspect key phrases (YAML)
data/
  sample/        synthetic example data (committed)
  annotations/   manual labels (committed)
  templates/     empty CSV templates for hand-collected data (committed)
  raw/ interim/ processed/   collected and generated data (not committed, except the
                             hand-off list data/interim/pilot_products.csv)
docs/            architecture, data and API contracts, decisions, source review, schedule
frontend/        React + Vite UI
notebooks/       exploration notebooks
src/greenchoice/
  collect/       data collection: reviews from browser-saved pages (saved_pages.py), EPREL
                 hand-collected CSV loader with strict validation (eprel_manual.py)
  preprocess/    cleaning, EPREL matching, TCO
  nlp/           aspect extraction, aggregation, P/R/F1 evaluation
  scoring/       criteria sub-scores, weighted baseline, ML comparison
  explain/       explanation sentences
  api/           FastAPI app
  pipeline.py    command line entry point (`greenchoice`)
tests/           pytest
```

## Setup

Requires Python 3.11+, Node.js 20+ and Git.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows; on macOS/Linux: source .venv/bin/activate
pip install -e ".[dev,ml,scrape]"

cd frontend
npm install
```

Optional, large download for BERTurk (stage 2): `pip install -e ".[nlp]"`

## Run

```bash
greenchoice build                                  # build the database from data/sample
uvicorn greenchoice.api.main:app --reload          # API at http://localhost:8000/docs
cd frontend && npm run dev                         # UI at http://localhost:5173
```

With real data: `greenchoice build --source interim --eprel data/raw/eprel_manual.csv`

Hand-collected data is entered in `data/raw/veri_toplama.xlsx` (template:
`data/templates/veri_toplama.xlsx`, guide: `docs/veri-toplama-excel.md`), then converted:
`greenchoice import-sheets --xlsx data/raw/veri_toplama.xlsx --out-dir data/raw`

Check the pilot product list (and its EPREL coverage) before handing it over:
`greenchoice check-pilot --products data/raw/pilot_products.csv --eprel data/raw/eprel_manual.csv --out data/interim/pilot_products.csv`

Reviews come from pages saved by hand in a normal browser, because the sites do not allow
automated collection (`docs/kaynak-inceleme.md`). This command only reads local files and never
extracts usernames; guide: `docs/yorum-toplama.md`:
`greenchoice import-reviews --pages data/raw/yorum_sayfalari --out data/interim/reviews.csv`

The `--eprel` file is the hand-collected EPREL CSV (the EPREL public API needs a key that
requires a sealed declaration). Template: `data/templates/eprel_manual.csv`; collection
guide: `docs/eprel-manual-toplama.md` (Turkish). The file is validated row by row: energy
class must be A-G, the source URL must be an EPREL page, numbers must parse, and duplicate
model codes must agree. The build summary reports `eprel_matched`.

## Tests

```bash
pytest                    # 149 tests
ruff check src tests      # lint
cd frontend && npm run build
```

Last verified: 2026-11-02, Python 3.12.10, Node 26.13.0 - 149 passed, ruff clean. The
frontend build was last run on 2026-10-29; nothing since then touches `frontend/`.

## Team workflow

Roles and schedule: [docs/gorev-dagilimi.md](docs/gorev-dagilimi.md) (in Turkish).
Current status and the next tasks for Person A: [docs/devir-kisi-a.md](docs/devir-kisi-a.md).
Rules for AI assistants working on this repository: [AGENTS.md](AGENTS.md) (`CLAUDE.md` imports it).
Rules: [CONTRIBUTING.md](CONTRIBUTING.md). One branch per task, pull request, review by the
other person, then merge to `main`.

## Progress and changelog

### 2026-11-02 - Product selection rule (Person B, decision 18)

- `collect/selection.py` and `greenchoice select-candidates`: pick the products that bring each
  category to 40 from the saved-page candidates and the Trendyol pages. Rank by rating count
  (at least 30), one entry per model (market-suffix variants and codeless titles with the same
  words count as one model), at most 12 per brand, models already held skipped, compact
  fridges (mini, office, under-counter, hotel) excluded. EPREL availability plays no part.
- Real data again found problems that are now tests: "İkili Soğutma", "20+ Program" and "A+++"
  were read as bundle marks and dropped real appliances; a merchant-style product number
  (`pm-mtsam...`) was rejected. 149 tests.

### 2026-11-02 - Candidate products from saved Hepsiburada search pages (Person B)

- `collect/listing_pages.py` and `greenchoice import-listings`: read search pages saved in a
  browser (no network) and write `data/interim/aday_urunler.csv` with title, URL, price, rating,
  rating count and suggested model codes. Advertisement cards, bundles, accessories and other
  appliances are skipped and counted; a page that parses to nothing fails with its file name.
- Checked on 9 real saved pages. Real data exposed three bugs, now covered by tests: prices
  without decimals (`47.930`) were read as 47.93 TL, a "3-piece appliance package" counted as a
  washing machine, and a 1.6k TL accessory counted as an appliance.
- Shared helper `collect/model_codes.py` (also used by the Trendyol reader). 127 tests.

### 2026-11-02 - Polite data collection (Person B, decision 17)

- Tried one honest-User-Agent request per shop: Hepsiburada answers 403 with a CAPTCHA page
  (no scraper, nothing is circumvented), Trendyol serves product pages. Decision 17 records
  the collection method: saved pages for Hepsiburada, a polite reader for known Trendyol
  product pages, product selection by review count rather than by EPREL availability.
- `collect/robots.py`: robots.txt parser with `*` and `$` support (`urllib.robotparser` ignores
  them, so Trendyol's `Disallow: /*?q=` would have been missed). An unreadable robots.txt (403,
  429, 5xx, network error) closes the site. `PoliteClient` now uses it and accepts an injected
  session, so it is tested without network (`tests/test_robots.py`, `tests/test_http.py`).
- `collect/trendyol_product.py` + `TrendyolSource.fetch_product` + `greenchoice fetch-trendyol`:
  reads price, rating and counts, capacity and warranty from the page's schema.org product
  data. Reviews and authors are never returned; the model code is only suggested. Checked on
  the five known Trendyol products. Search, listing and reviews stay unavailable (robots.txt).
- `requests` and `beautifulsoup4` added to the `dev` extra. 29 new tests.
- Fixed `docs/decisions.md`, where a previous edit had removed the "Açık sorular" heading.

### 2026-11-01 - Review source check and saved-page import (Person A, tasks A0.1, A1.1)

- Source check: Trendyol reviews load from `apigw.trendyol.com`, whose robots.txt disallows
  everything; Hepsiburada answers automated requests with 403. No scraper was written.
- New `greenchoice import-reviews` parses pages saved by hand in a browser (`collect/saved_pages.py`).
  No network access, no usernames. Unreadable pages fail with the file name; the report lists
  missing reviews or pages, and truncated text.
- Checked on real pages: 87 reviews from 2 products. All 9 Hepsiburada reviews with text in the
  page's JSON-LD match on text, rating and date. Trendyol has no such check: ratings come from
  the star bar width.
- 8 new tests with synthetic HTML (no user content in the repository); 86 in total.

### 2026-11-01 - Electricity price from the official EPDK table (Person B, task B0.3)

- `electricity_price_tl_per_kwh` is now 2.919 TL/kWh (placeholder was 3.0): EPDK decision 14461,
  table valid from 2026-04-04, residential low-voltage single-time, up to 8 kWh/day, excluding
  taxes (energy 49.4065 + distribution 242.49 kr/kWh). The high tier (above 8 kWh/day) is
  4.321 TL/kWh. Sources and the open questions (is there a newer quarterly decision, which
  tier a typical household is in) are in `docs/decisions.md` 15 and `docs/kaynak-inceleme.md`.
- Config change only; 78 tests still pass.

### 2026-10-30 - Pilot product list in the repository (Person B)

- `data/interim/pilot_products.csv` (26 products: id, public shop URL, category) is now
  committed through a `.gitignore` exception so Person A gets it with the branch. Everything
  else under `data/interim/` stays untracked.

### 2026-10-30 - Review of the filled workbook (Person B)

- Checked all 12 refrigerator rows against their Hepsiburada pages (price, rating, review
  count) and the washing machines already checked before. Most values matched exactly.
- Found input errors the loader did not catch and fixed the loader: a price typed as `42.218`
  (thousands separator read as a decimal, i.e. 42 TL) is now rejected (price must be at least
  1000 TL), a rating of 0 for "no reviews yet" is rejected (ratings are 1-5, leave empty), and
  `check-pilot` prints the row error instead of a traceback.
- 78 tests (up from 74).

### 2026-10-30 - Excel shows #### (Person B)

- Cause: dates written by the merge script carried a time part (`yyyy-mm-dd h:mm:ss`, 19
  characters) in a 12-character column, and the price column was narrow.
- The template now pre-formats all data rows (dates `yyyy-mm-dd`, prices `#,##0.00`) and uses
  wider date, price, rating and count columns. `collect.sheets.format_sheet` applies the
  same widths and formats to an existing, filled workbook and strips time parts from dates.
- 2 new tests; 74 in total.

### 2026-10-30 - Hand-over report and AI rules (Person B)

- Added `AGENTS.md` (operating rules and project rules for AI assistants; `CLAUDE.md` imports
  it) and `docs/devir-kisi-a.md` (what is done, the input data, ordered tasks and deadlines
  for Person A, and a prompt pattern). Documentation only; no code changed.

### 2026-10-30 - Cost assumptions with sources (Person B, task B0.3)

- Water price set to the official Istanbul (ISKI) 2026 residential tariff, 65.52 TL/m3
  (water + wastewater, excl. VAT), replacing the placeholder 40.
- Washing machine lifetime 10 -> 12 years (sourced); refrigerator lifetime stays 12 years and
  is documented as unsourced. The 220 washes per year assumption was verified in Regulation
  (EU) 2019/2023 Annex V.
- The electricity price could not be verified from an official EPDK table (secondary sources
  disagree), so the 3.0 TL/kWh placeholder stays and is marked as an open question.
- Added `tests/test_config.py` (weights sum to 1, positive assumptions, ordered thresholds).
- `docs/kaynak-inceleme.md` now records the verified EPREL search behaviour, field labels and the
  per-brand match results; `docs/meetings/2026-10-31.md` holds the advisor meeting agenda.
- 72 tests (up from 67).

### 2026-10-30 - First real data review and hardening (Person B)

- Reviewed the first 5 hand-collected washing machines against their EPREL pages: all
  EPREL values (kWh per 100 cycles, water, noise, energy class A) matched. One site value
  (capacity) was wrong and several cells held text instead of numbers.
- Found and fixed silent data loss: `import-sheets` skipped a product typed into the hint
  row (now an error), and the pilot loader turned text such as "4 nokta 6" or "10 kg" into an
  empty value (now rejected with the row number; decimal commas are accepted; ranges checked).
- Fixed `clean_reviews` crashing on an empty review table, so the pipeline runs before any
  review has been collected. Smoke test on 5 real products: 5/5 EPREL matches, scores built.
- 67 tests (up from 55).

### 2026-10-30 - Excel workbook for hand-collected data (Person B)

- Hand-filling the two CSV files was hard to read (and Turkish-locale Excel opens
  comma-separated CSV as a single column), so data entry now happens in one workbook.
- `collect/sheets.py` and `collect/sheets_layout.py`: generate `veri_toplama.xlsx` (Turkish
  headers, hints, dropdowns, frozen header rows) and export its two sheets to the CSVs the
  existing loaders expect. The loaders are unchanged and still validate everything.
- New commands: `greenchoice make-sheets` and `greenchoice import-sheets` (the latter also
  runs the loaders and points to the Excel row of any error). 6 new tests, 55 in total.
- `openpyxl` added to the `dev` and new `sheets` extras. Guide: `docs/veri-toplama-excel.md`.

### 2026-10-29 - Pilot product list (Person B, task B0.2)

- Added `collect/pilot.py`: loader and validator for the hand-built pilot product list
  (required fields, `ty-123456` style ids, known categories, https URLs, unique ids and
  URLs) plus a report with products per category and EPREL coverage.
- New command `greenchoice check-pilot` prints the report and, with `--out`, writes the
  `product_id, url, category` hand-off file for Person A (10 new tests).
- Added the CSV template and `docs/pilot-urun-listesi.md` (Turkish guide).

### 2026-10-29 - Hand-collected EPREL data (Person B)

- Decision: collect EPREL values by hand from public product pages instead of waiting for an
  API key. The terms document has not been read by the team yet; see the guide.
- Added `collect/eprel_manual.py`: strict loader for the hand-collected CSV (13 new tests).
- `greenchoice build --eprel` now uses the loader and reports `eprel_matched`.
- Fixed `merge_eprel` raising `KeyError` when the product table lacks an EPREL column.
- Added the CSV template and the collection guide.

### 2026-10-29 - Environment and EPREL access review (Person B)

- Installed Python 3.12, Node.js LTS and Git; created `.venv`; baseline verified (see Tests).
- Initialised the Git repository with the imported skeleton as the first commit.
- Reviewed how to access EPREL (task B0.1). Result in `docs/kaynak-inceleme.md`:
  - The EPREL public API **requires an API key**.
  - The key requires a declaration sealed with an electronic seal or digital signature.
  - The official API documentation and JSON field names could not be obtained, so
    `FIELD_MAP` in `collect/eprel.py` is still unverified and unchanged.
- Rewrote this README in English.

### 2026-10-22 - Skeleton (imported)

- Repository layout, CI, TCO, SQLite schema, data contracts.
- Review cleaning, rule-based aspect extraction, per-product aggregation, P/R/F1 script.
- Weighted baseline scoring and explanation templates.
- FastAPI with 7 endpoints and a React UI (list, detail, compare, weight sliders).

### Next

- Read the EPREL terms document, then collect 5 refrigerator and 5 washing machine models
  by hand and confirm the washing machine field labels (task B0.1).
- Product listing: pilot list of 10 products per category due 2026-10-31 (task B0.2).
