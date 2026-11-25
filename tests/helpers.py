"""Niezależne sprawdzanie PESEL i izolacja plików testowych."""

import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "output"
FIELDS = (
    "imie", "nazwisko", "pesel", "data_urodzenia", "email", "telefon",
    "kod_pocztowy", "miasto", "przypadek",
)
REFERENCE = date(2026, 11, 25)


def valid_checksum(value):
    # Równoważne wagi dopełniające: suma wraz z cyfrą kontrolną ma resztę 0.
    return (
        len(value) == 11 and value.isascii() and value.isdigit()
        and sum(int(c) * w for c, w in zip(value, (9, 7, 3, 1, 9, 7, 3, 1, 9, 7, 9)))
        % 10 == 0
    )


def birth_from_pesel(value):
    month = int(value[2:4])
    century = {0: 1900, 1: 2000, 2: 2100, 3: 2200, 4: 1800}[month // 20]
    return date(century + int(value[:2]), month % 20, int(value[4:6]))


def read_records(path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def csv_records(records):
    return [{field: row.get(field, "") for field in FIELDS} for row in records]


class OutputTestCase(unittest.TestCase):
    def setUp(self):
        OUTPUT.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="test_", dir=OUTPUT)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
