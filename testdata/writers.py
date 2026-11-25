"""Zapis rekordów do plików w różnych formatach.

Rejestr `WRITERS` mapuje nazwę formatu na funkcję zapisującą.
Każda funkcja ma sygnaturę `(rekordy, sciezka) -> None`.
"""

import csv
import json
from collections.abc import Callable
from pathlib import Path


def write_json(rekordy: list[dict], sciezka: Path) -> None:
    """Zapisuje rekordy jako JSON w UTF-8, z wcięciami i polskimi znakami."""
    tresc = json.dumps(rekordy, ensure_ascii=False, indent=2)
    sciezka.write_text(tresc + "\n", encoding="utf-8", newline="\n")


def _kolumny(rekordy: list[dict]) -> list[str]:
    """Zwraca nazwy pól w kolejności pierwszego wystąpienia we wszystkich rekordach."""
    kolumny: dict[str, None] = {}
    for rekord in rekordy:
        kolumny.update(dict.fromkeys(rekord))
    return list(kolumny)


def write_csv(rekordy: list[dict], sciezka: Path) -> None:
    """Zapisuje rekordy jako CSV w UTF-8, separator `,`, z nagłówkiem.

    Brakujące pole w rekordzie daje pustą komórkę.
    """
    with sciezka.open("w", encoding="utf-8", newline="") as plik:
        writer = csv.DictWriter(plik, fieldnames=_kolumny(rekordy), restval="")
        writer.writeheader()
        writer.writerows(rekordy)


WRITERS: dict[str, Callable[[list[dict], Path], None]] = {
    "json": write_json,
    "csv": write_csv,
}
