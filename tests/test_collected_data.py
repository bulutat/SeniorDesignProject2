"""Guards the one place where collected data may be committed (decision 19)."""

import re
from pathlib import Path

import pytest

FOLDER = Path(__file__).resolve().parents[1] / "data" / "toplanan"
FORBIDDEN = re.compile(r"author|reviewBody|review_text|password|token|api[_-]?key|boutiqueId|merchantId",
                       re.IGNORECASE)
ALLOWED = {".csv", ".json", ".xlsx", ".md"}
MAX_BYTES = 1_000_000  # product facts only; page copies and caches are megabytes


def files():
    return sorted(p for p in FOLDER.rglob("*") if p.is_file())


def test_the_folder_exists_and_is_documented():
    assert FOLDER.is_dir() and (FOLDER / "README.md").exists()


def test_only_small_product_fact_files_are_committed():
    assert files()
    for path in files():
        assert path.suffix in ALLOWED, f"{path.name}: only {sorted(ALLOWED)} may be committed here"
        assert path.stat().st_size <= MAX_BYTES, f"{path.name} is larger than {MAX_BYTES} bytes"


@pytest.mark.parametrize("suffix", [".csv", ".json", ".md"])
def test_no_reviews_authors_or_secrets_in_text_files(suffix):
    for path in (p for p in files() if p.suffix == suffix):
        match = FORBIDDEN.search(path.read_text(encoding="utf-8"))
        assert match is None, f"{path.name}: found {match.group(0)!r}"
