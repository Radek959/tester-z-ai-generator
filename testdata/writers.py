"""Zapis rekordów do plików w różnych formatach.

Rejestr `WRITERS` mapuje nazwę formatu na funkcję zapisującą.
Każda funkcja ma sygnaturę `(rekordy, sciezka) -> None`.
"""

import json
from collections.abc import Callable
from pathlib import Path


def write_json(rekordy: list[dict], sciezka: Path) -> None:
    """Zapisuje rekordy jako JSON w UTF-8, z wcięciami i polskimi znakami."""
    tresc = json.dumps(rekordy, ensure_ascii=False, indent=2)
    sciezka.write_text(tresc + "\n", encoding="utf-8", newline="\n")


WRITERS: dict[str, Callable[[list[dict], Path], None]] = {
    "json": write_json,
}
