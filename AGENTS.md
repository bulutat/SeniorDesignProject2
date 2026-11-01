# AGENTS.md — rules for AI assistants working on GreenChoice

Read this file first, then `docs/devir-kisi-a.md` (current status and the next tasks for
Person A), then `docs/decisions.md`. These rules apply to every AI assistant (Claude Code,
Copilot, ChatGPT, Gemini, ...). The human owner of a task is responsible for the result.

## Project in one paragraph

GreenChoice is a senior design project (COMP 491, 2026–2027 Fall): an AI-based decision
support prototype that scores household appliances (refrigerators and washing machines) by
energy use, long-term cost, durability and user experience, and explains the score.
Architecture: an offline pipeline (`greenchoice build`) writes one SQLite file, a FastAPI service
reads it, a React UI shows it. Details: `README.md`, `docs/architecture.md`.

Team: Person A (NLP and explainability: review collection, BERTurk, SHAP, user study) and
Person B (data, scoring, web: product and EPREL data, scoring, API, UI). Roles and dates:
`docs/gorev-dagilimi.md`.

## Operating rules (strict)

1. **Zero hallucination.**
   - Never invent APIs, endpoints, HTML selectors, JSON field names, library methods,
     package names, tariffs, product data or numbers.
   - Verify a library function signature before using it (read the installed package or run a
     minimal sanity script). Verify web facts on the real page and record the source.
   - If you cannot verify something, say so and leave it as an explicit open question
     (`docs/decisions.md`). A marked placeholder is better than a plausible guess.
   - Example learned here: the EPREL JSON field names are still unverified because the
     public API needs a key, so nothing relies on them.
2. **Clean architecture, no spaghetti.** Separation of concerns and single responsibility.
   Keep modules small (about 200 lines or less). Core logic lives in `src/greenchoice/`,
   tests in `tests/`, configuration in `config/`. Do not put logic in notebooks.
3. **Test-driven development with a self-healing loop.**
   a. Write the tests for the feature first (pytest).
   b. Write the minimal implementation.
   c. Run the tests and `ruff check src tests`.
   d. If tests fail: revert or fix the broken code, find the root cause, re-run. Never build a
      new feature on a failing codebase.
   e. Continue only when everything is green.
   Tests must not need the network. Use small saved fixtures or synthetic data and say so.
4. **Keep the English `README.md` current.** At every milestone, before finishing: update the
   overview and architecture, folder structure, setup and run instructions, test
   instructions, and the progress/changelog section.
5. **Atomic milestones.** One milestone = one feature + its tests + verification + README
   update, in one small commit. No giant multi-file dumps.

## Project rules

- **Git workflow** (`CONTRIBUTING.md`): never commit to `main`. One branch per task
  (`<person>/<topic>`), a Pull Request, review by the other person, then merge. Do not
  force-push shared branches.
- **Data is not committed.** `data/raw/`, `data/interim/`, `data/processed/`, `models/`,
  `*.db` and `.env` stay out of Git. Committed data: `data/sample/` (synthetic, must never
  appear in results), `data/annotations/` (manual labels), `data/templates/`, and one
  exception, `data/interim/pilot_products.csv` (product ids, public shop URLs and categories
  only; it is the hand-off list for the review scraper).
- **Contracts.** Table columns (`src/greenchoice/contracts.py`, `docs/data-contracts.md`),
  the API (`schemas.py`, `frontend/src/types.ts`, `docs/api.md`) are shared. Adding a column is
  fine; removing or renaming one needs both people's approval and a doc update.
- **Ownership.** The owner of a module is responsible for it and approves PRs touching it
  (table in `docs/gorev-dagilimi.md`).
- **Collecting data.** Check `robots.txt` and the terms of the site first. Use
  `collect/http.py::PoliteClient` (wildcard-aware `collect/robots.py`, honest User-Agent, at
  least 2 s between requests, disk cache; an unreadable robots.txt closes the site).
  Do not bypass blocks, logins or bot detection. Decision 17 lists what is allowed per site. Inspect the real response before writing a
  parser, and save a small fixture for the tests.
- **Silent data loss is a bug.** Do not turn invalid input into empty values. Validate, fail
  with a row number, and test it (see `collect/pilot.py`, `collect/eprel_manual.py`).
- **Decisions and sources.** Every assumption that affects results goes into
  `docs/decisions.md` with its source, date and status. Unverified values are marked.
- **Language.** Code, comments, commit messages and `README.md` in English. Team documents
  under `docs/` are in Turkish.
- **Secrets and privacy.** Never commit keys, tokens, personal data or private messages.
  Anything pushed to the public repository is public.

## Working here

```bash
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -e ".[dev,ml,scrape]"                  # add ,nlp for BERTurk
pytest && ruff check src tests                     # must stay green
greenchoice build                                  # sample data -> data/processed/greenchoice.db
```

Useful commands: `greenchoice check-pilot`, `greenchoice make-sheets`,
`greenchoice import-sheets`, `greenchoice eval-nlp`. On Windows PowerShell, chain commands with
`;`, not `&&`.

## Where things are

| Need | Look at |
|---|---|
| Status and next tasks for Person A | `docs/devir-kisi-a.md` |
| Tasks, owners, deadlines | `docs/gorev-dagilimi.md`, `docs/takvim.html` |
| Decisions, assumptions, open questions | `docs/decisions.md` |
| Source research (EPREL, shops) | `docs/kaynak-inceleme.md` |
| Table and API contracts | `docs/data-contracts.md`, `docs/api.md` |
| Labelling rules | `docs/annotation-guideline.md` |
