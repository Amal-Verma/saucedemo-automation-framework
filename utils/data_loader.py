"""Loads data-driven test inputs from testdata/ (JSON or CSV)."""
import csv
import json

from config.config import TESTDATA_DIR


def load_json(name: str) -> list[dict]:
    with open(TESTDATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def load_csv(name: str) -> list[dict]:
    with open(TESTDATA_DIR / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
