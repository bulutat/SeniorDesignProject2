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
  raw/ interim/ processed/   collected and generated data (not committed)
docs/            architecture, data and API contracts, decisions, source review, schedule
frontend/        React + Vite UI
notebooks/       exploration notebooks
src/greenchoice/
  collect/       data collection (e-commerce - not implemented yet; EPREL hand-collected
                 CSV loader with strict validation in eprel_manual.py)
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

The `--eprel` file is the hand-collected EPREL CSV (the EPREL public API needs a key that
requires a sealed declaration). Template: `data/templates/eprel_manual.csv`; collection
guide: `docs/eprel-manual-toplama.md` (Turkish). The file is validated row by row: energy
class must be A-G, the source URL must be an EPREL page, numbers must parse, and duplicate
model codes must agree. The build summary reports `eprel_matched`.

## Tests

```bash
pytest                    # 72 tests
ruff check src tests      # lint
cd frontend && npm run build
```

Last verified: 2026-10-30, Python 3.12.10, Node 26.13.0 - 72 passed, ruff clean. The
frontend build was last run before the EPREL changes, which do not touch `frontend/`.

## Team workflow

Roles and schedule: [docs/gorev-dagilimi.md](docs/gorev-dagilimi.md) (in Turkish).
Current status and the next tasks for Person A: [docs/devir-kisi-a.md](docs/devir-kisi-a.md).
Rules for AI assistants working on this repository: [AGENTS.md](AGENTS.md) (`CLAUDE.md` imports it).
Rules: [CONTRIBUTING.md](CONTRIBUTING.md). One branch per task, pull request, review by the
other person, then merge to `main`.

## Progress and changelog

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
