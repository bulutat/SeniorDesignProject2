"""Proje yolları ve YAML yapılandırmasının tek giriş noktası."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DIR = DATA_DIR / "sample"
ANNOTATIONS_DIR = DATA_DIR / "annotations"
MODELS_DIR = ROOT / "models"


def db_path() -> Path:
    """SQLite veritabanı yolu. GREENCHOICE_DB ortam değişkeniyle değiştirilebilir."""
    env = os.environ.get("GREENCHOICE_DB")
    return Path(env) if env else PROCESSED_DIR / "greenchoice.db"


@lru_cache
def _load_yaml(name: str) -> dict[str, Any]:
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def categories_config() -> dict[str, Any]:
    return _load_yaml("categories.yaml")


def aspects_config() -> dict[str, Any]:
    return _load_yaml("aspects.yaml")


def criteria_ids() -> list[str]:
    return list(categories_config()["criteria"].keys())


def category_config(category: str) -> dict[str, Any]:
    cats = categories_config()["categories"]
    if category not in cats:
        raise KeyError(f"Bilinmeyen kategori: {category!r}. Tanımlılar: {list(cats)}")
    return cats[category]
