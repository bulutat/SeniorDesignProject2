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

Choose the reviews to annotate and write one sheet per annotator (`nlp/pool.py`). Sheets contain
review text and stay in `data/interim/etiketleme/`, which is not committed:
`greenchoice annotation-pool`

The `--eprel` file is the hand-collected EPREL CSV (the EPREL public API needs a key that
requires a sealed declaration). Template: `data/templates/eprel_manual.csv`; collection
guide: `docs/eprel-manual-toplama.md` (Turkish). The file is validated row by row: energy
class must be A-G, the source URL must be an EPREL page, numbers must parse, and duplicate
model codes must agree. The build summary reports `eprel_matched`.

## Tests

```bash
pytest                    # 164 tests
ruff check src tests      # lint
cd frontend && npm run build
```

Last verified: 2026-11-05, Python 3.12.10 - 191 passed, ruff clean. The
frontend build was last run on 2026-10-29; nothing since then touches `frontend/`.

## Team workflow

Roles and schedule: [docs/gorev-dagilimi.md](docs/gorev-dagilimi.md) (in Turkish).
Current status and the next tasks for Person A: [docs/devir-kisi-a.md](docs/devir-kisi-a.md).
Rules for AI assistants working on this repository: [AGENTS.md](AGENTS.md) (`CLAUDE.md` imports it).
Rules: [CONTRIBUTING.md](CONTRIBUTING.md). One branch per task, pull request, review by the
other person, then merge to `main`.

## Progress and changelog

### 2026-11-10 - Importance choices instead of weight sliders (Person A for Person B)

- The weight panel now asks, for each criterion, "Önemli değil / Önemli / Çok önemli" (relative
  weights 0 / 1 / 2; the API scales them to sum to 1). Starting choices follow the category's
  default weights (0.20 and above is "very important"). With every criterion set to "not
  important" the re-rank button is disabled. Frontend only; the API is unchanged.

### 2026-11-10 - Energy data for products outside EPREL (Person A)

- 32 of 80 products had no energy class. The official EU energy labels of 23 of them were read
  by hand from the manufacturers' Turkish sites and stored with their URLs in
  `data/manual/energy_labels.csv`; 7 more get the class from the store title ("E Enerji Sınıfı").
  Pre-2021 classes (A+++ ...) are never used. 2 products remain unknown.
- New `preprocess/energy_labels.py`; `build` fills only empty fields in the order EPREL, label,
  shop data, title, and writes the source to `energy_source`. Method and doubts:
  `docs/enerji-etiketleri.md`. Energy class known for 78 products (was 48), annual kWh for 71
  (was 48). 161 tests.

### 2026-11-07 - Sensitivity analysis (Person A for Person B, task B3.3)

- `scoring/sensitivity.py` and `greenchoice sensitivity`: electricity price (-50%, +50%, upper
  tier), lifetime (8, 15 years) and each criterion weight (+/-50%, equal weights) are changed one
  at a time; the ranking inside each category is compared with Kendall tau, top-10 overlap and
  label changes. Results and limits: `docs/duyarlilik-analizi.md`.
- On the real data the ranking hardly moves with electricity price or lifetime (tau >= 0.98) but
  does move with weights; labels are fragile near the 70 threshold. For the cheap-but-inefficient
  question, the median break-even electricity price is 49 TL/kWh (refrigerators) and 104 TL/kWh
  (washing machines), against 2.919 today: the efficient model rarely pays back its higher price.
  164 tests.

### 2026-11-07 - AHP criterion weights (Person A for Person B, task B3.1)

- `scoring/ahp.py` and `greenchoice ahp`: each person fills a copy of
  `data/templates/ahp_karsilastirma.yaml` (Saaty 1-9 scale, fractions for the reverse direction)
  in `data/annotations/ahp/`. The command gives weights (principal eigenvector) and the
  consistency ratio per category, per person and combined (element-wise geometric mean).
  Missing, repeated or out-of-range judgements fail with the file and pair named.
- The weights are a suggestion; `config/categories.yaml` is not changed. 161 tests.

### 2026-11-07 - Learned aspect extractors ready for labels (Person A; B2.1 for Person B, A2.1)

- `nlp/tfidf.py`: TF-IDF (character n-grams within words) + one balanced Logistic Regression per
  `aspect:polarity` label. `greenchoice train-nlp` trains on `train`, tunes a threshold per label
  on `val` and reports P/R/F1 on `test` only (`models/tfidf_lr_v0.json`). Labels without a
  training example are listed, not guessed.
- `nlp/transformer.py`: `TransformerExtractor` loads a BERTurk model fine-tuned in Colab
  (`notebooks/03_A_berturk_egitim.ipynb`, class-weighted loss, epoch and thresholds chosen on
  `val`). `greenchoice export-nlp-data` writes the split files the notebook needs; they hold
  review text and stay in `data/interim`. The notebook has not been run yet (no labels).
- `greenchoice build --nlp rule|tfidf|berturk --nlp-model <path>` picks the extractor. 191 tests;
  the BERTurk class is not covered by tests because torch is not installed locally.

### 2026-11-07 - Label collection, kappa and gold file (Person A, task O2.1 tools)

- New `greenchoice collect-labels` (`nlp/labels.py`): reads the filled sheets, checks every value
  (row number in the error), computes Cohen's kappa per aspect on the shared test reviews, writes
  the disagreements to `data/interim/etiketleme/uzlasma.csv` for a decision and builds the gold
  file. 20% of train becomes `val` for threshold tuning. Undecided test reviews stay out.
- **Contract change, needs Person B's approval:** `data/annotations/reviews_gold.csv` no longer has
  a `text` column (review text is never committed); it now has `split`. `eval-nlp` joins the text
  from `data/interim/reviews.csv`, cleans it like `build` and scores the `test` split by default.
- Sheets have a `checked` column, so an empty row can mean "no aspect". Sheets were regenerated;
  the 400 chosen reviews did not change. 184 tests.
- Guideline: counts and proposals for the two open questions (durability at least 6 months; add a
  `performance` label that does not enter the score yet).

### 2026-11-06 - 80-product list handed to review collection (Person A)

- `data/interim/pilot_products.csv` now holds the 80 products of Person B's
  `veri_toplama_v4.xlsx` (40 washing machines, 40 refrigerators), produced with
  `import-sheets` and `check-pilot --out`. The workbook was only read, not changed.
- All 26 earlier products are kept; 54 are new (47 Hepsiburada, 7 Trendyol). Reviews for
  the new products still have to be saved by hand (`docs/yorum-toplama.md`).
- Hepsiburada shows the reviews of a seller listing (`-p-` address) under the product's main
  `-pm-` number. Optional column `review_page_id` in `pilot_products.csv` maps that number to the
  listed product, so ids stay the same as in the workbook and EPREL data. 151 tests.

### 2026-11-05 - Annotation pool (Person A, task O1.1)

- New `greenchoice annotation-pool` (`nlp/pool.py`): 100 random test reviews that both people
  label, and 300 train reviews enriched with keyword candidates (energy, failure, noise,
  service), reviews rated 3 or lower, then random reviews alternating between categories. At
  most 30 train reviews per product. Fixed seed; it refuses to overwrite an existing pool.
- Each annotator gets one sheet of 250 reviews (shared 100 + own 150) in random order, without
  the split, the reason or the rating.
- Dry run on the 1,460 pilot reviews: the rule extractor finds few candidates (energy 1,
  service 6, failure 14), so 180 of the 300 train reviews are random. To be run again on the
  80-product reviews before labelling starts. 176 tests.

### 2026-11-05 - Clear error for a broken Trendyol review card (Person A)

- `import-reviews` crashed with `AttributeError` when a saved Trendyol review card had no star bar
  or no width in it (reported by Person B). It now stops with a `ValueError` that names the file
  and the review id, like the other parse errors.
- 2 new tests; 152 in total. The 1,492 pilot reviews still import unchanged.


### 2026-11-02 - 80-product list assembled (Person B)

- Applied the selection rule to 15 saved Hepsiburada pages and 17 Trendyol product pages,
  looked the chosen models up in EPREL and added 54 products and 18 EPREL records to
  `data/raw/veri_toplama_v4.xlsx`: 40 washing machines and 40 refrigerators.
- EPREL match rate: **48 of 80 (60%)**, below the 70% target of task B1.2. 17 products carry no
  model code in their title (mostly Arcelik, Beko, Grundig, Altus, Vestel) and 15 have a code
  EPREL does not know (mostly Samsung refrigerators, Profilo, LG). Washing machines match much
  better than refrigerators. This is reported as a finding, not tuned away (decision 18).
- `model_code` is now optional in the pilot list (empty means "not in the title"); the report
  counts `no_model_code` separately from codes missing in EPREL. Workbooks made from an older
  template (previous hint text) are still accepted. 150 tests.

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

### 2026-11-01 - Annotation guideline and energy decision (Person A, task A1.3)

- `docs/annotation-guideline.md` tried on 32 real reviews chosen to be difficult: aspect scopes,
  a table of confusing cases (examples are invented) and a pool plan with a random test set.
- Decision 16: the energy criterion is not fed from reviews. Scoring already used only the energy
  class and kWh, so no scoring code changed; a new test guards it. 104 tests.

### 2026-11-01 - Review cleaning (Person A, task A1.2)

- `normalize_text` shortens elongated letters and removes emoji. No language filter: non-Turkish
  reviews did not appear in the pilot data (samples were Turkish typed without diacritics).
- New `preprocess/scope.py`: "sorunsuz" and "sağlam" next to delivery or installation words no
  longer count as durability. New columns `text_product` and `mentions_logistics`; the raw text
  is unchanged and the extractor reads `text_product`.
- On 1,460 pilot reviews `durability:pos` fell from 218 to 41, other aspects unchanged. Removing
  whole clauses was tried first and dropped: it lost real product mentions.
- 17 new tests; 103 in total. Accuracy is not measured yet, labelled data comes next.

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
