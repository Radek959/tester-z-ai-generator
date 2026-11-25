"""Jedyny punkt wejścia do generowania plików z danymi testowymi.

CLI i frontend tylko zbierają parametry i wołają `generate_file`.
"""

from datetime import datetime
from pathlib import Path

from testdata.generator import generuj_osoby
from testdata.writers import WRITERS

KATALOG_WYJSCIOWY = Path(__file__).resolve().parent.parent / "output"

SCENARIUSZE = ("poprawne",)

MAKS_ILOSC = 100_000


def _sprawdz_parametry(format: str, scenario: str, count: int) -> None:
    if format not in WRITERS:
        dostepne = ", ".join(WRITERS)
        raise ValueError(f"Nieznany format „{format}”. Dostępne formaty: {dostepne}.")
    if scenario not in SCENARIUSZE:
        dostepne = ", ".join(SCENARIUSZE)
        raise ValueError(f"Nieznany scenariusz „{scenario}”. Dostępne scenariusze: {dostepne}.")
    if count < 1:
        raise ValueError("Liczba rekordów musi być większa od zera.")
    if count > MAKS_ILOSC:
        raise ValueError(f"Liczba rekordów nie może być większa niż {MAKS_ILOSC}.")


def _nowa_sciezka(format: str, scenario: str) -> Path:
    """Zwraca nieistniejącą ścieżkę w `output/` z nazwą scenariusza i czasem."""
    znacznik = datetime.now().strftime("%Y%m%d_%H%M%S")
    baza = f"{scenario}_{format}_{znacznik}"
    sciezka = KATALOG_WYJSCIOWY / f"{baza}.{format}"
    numer = 2
    while sciezka.exists():
        sciezka = KATALOG_WYJSCIOWY / f"{baza}_{numer}.{format}"
        numer += 1
    return sciezka


def generate_file(format: str, scenario: str, count: int, seed: int | None = None) -> Path:
    """Generuje plik z danymi testowymi i zwraca ścieżkę do niego.

    Ten sam `seed` i parametry dają identyczną treść pliku.
    Błędne parametry zgłaszane są jako `ValueError` z opisem po polsku.
    """
    _sprawdz_parametry(format, scenario, count)
    rekordy = generuj_osoby(count, seed)
    KATALOG_WYJSCIOWY.mkdir(exist_ok=True)
    sciezka = _nowa_sciezka(format, scenario)
    WRITERS[format](rekordy, sciezka)
    return sciezka
