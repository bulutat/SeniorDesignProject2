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

Check the pilot product list (and its EPREL coverage) before handing it over:
`greenchoice check-pilot --products data/raw/pilot_products.csv --eprel data/raw/eprel_manual.csv --out data/interim/pilot_products.csv`

The `--eprel` file is the hand-collected EPREL CSV (the EPREL public API needs a key that
requires a sealed declaration). Template: `data/templates/eprel_manual.csv`; collection
guide: `docs/eprel-manual-toplama.md` (Turkish). The file is validated row by row: energy
class must be A-G, the source URL must be an EPREL page, numbers must parse, and duplicate
model codes must agree. The build summary reports `eprel_matched`.

## Tests

```bash
pytest                    # 49 tests
ruff check src tests      # lint
cd frontend && npm run build
```

Last verified: 2026-10-29, Python 3.12.10, Node 26.13.0 - 49 passed, ruff clean. The
frontend build was last run before the EPREL changes, which do not touch `frontend/`.

## Team workflow

Roles and schedule: [docs/gorev-dagilimi.md](docs/gorev-dagilimi.md) (in Turkish).
Rules: [CONTRIBUTING.md](CONTRIBUTING.md). One branch per task, pull request, review by the
other person, then merge to `main`.

## Progress and changelog

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
