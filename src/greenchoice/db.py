"""SQLite okuma/yazma yardımcıları.

Pipeline tabloları her çalıştırmada baştan yazar (offline batch); API yalnızca okur.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from greenchoice.config import db_path

TABLES = ("products", "reviews", "review_aspects", "product_features", "scores")


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = Path(path or db_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def write_tables(tables: dict[str, pd.DataFrame], path: Path | None = None) -> None:
    with connect(path) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)


def read_table(name: str, path: Path | None = None) -> pd.DataFrame:
    if name not in TABLES:
        raise ValueError(f"Bilinmeyen tablo: {name!r}")
    with connect(path) as conn:
        return pd.read_sql_query(f"SELECT * FROM {name}", conn)
