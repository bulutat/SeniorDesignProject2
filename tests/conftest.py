import pytest

from greenchoice.config import SAMPLE_DIR
from greenchoice.pipeline import build


@pytest.fixture(scope="session")
def sample_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "test.db"
    summary = build(SAMPLE_DIR, path)
    return path, summary
