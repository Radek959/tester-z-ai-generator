"""Scenariusze testowe: modyfikacje poprawnych rekordów `osoba`.

Każdy scenariusz to lista przypadków. Rekord nr i dostaje przypadek nr
(i mod liczba_przypadków), więc już kilka rekordów pokazuje różne przypadki.
Przypadek zmienia rekord i wpisuje swój opis do pola `przypadek`.
"""

import random
import string
from collections.abc import Callable
from datetime import date, timedelta

from testdata.generator import POLA_OSOBY, generuj_osobe, pesel

MAKS_DLUGOSC_IMIENIA = 50

# Przypadek: (rekord, rng, dzis) -> None, modyfikuje rekord w miejscu.
Przypadek = Callable[[dict, random.Random, date], None]


def _kobieta(rekord: dict) -> bool:
    """Płeć odczytana z PESEL (dziesiąta cyfra parzysta = kobieta)."""
    return int(rekord["pesel"][9]) % 2 == 0


def _ustaw_date(rekord: dict, data: date, rng: random.Random) -> None:
    """Zmienia datę urodzenia i dopasowuje do niej PESEL."""
    rekord["data_urodzenia"] = data.isoformat()
    rekord["pesel"] = pesel(data, _kobieta(rekord), rng)


def _przypadek(opis: str, zmiana: Przypadek) -> Przypadek:
    def zastosuj(rekord: dict, rng: random.Random, dzis: date) -> None:
        zmiana(rekord, rng, dzis)
        rekord["przypadek"] = opis

    return zastosuj


# --- graniczne: wartości na krawędzi, ale nadal poprawne ---


def _imie_jeden_znak(rekord, rng, dzis):
    rekord["imie"] = rekord["imie"][0]


def _imie_maks(rekord, rng, dzis):
    imie = rekord["imie"]
    rekord["imie"] = (imie + imie.lower() * MAKS_DLUGOSC_IMIENIA)[:MAKS_DLUGOSC_IMIENIA]


def _urodzony_dzis(rekord, rng, dzis):
    _ustaw_date(rekord, dzis, rng)


def _data_staly(data: date) -> Przypadek:
    def zmiana(rekord, rng, dzis):
        _ustaw_date(rekord, data, rng)

    return zmiana


def _29_lutego(rekord, rng, dzis):
    rok = rng.choice(range(1940, 2008, 4))
    _ustaw_date(rekord, date(rok, 2, 29), rng)


def _kod(kod: str, miasto: str | None = None) -> Przypadek:
    def zmiana(rekord, rng, dzis):
        rekord["kod_pocztowy"] = kod
        if miasto:
            rekord["miasto"] = miasto

    return zmiana


GRANICZNE: list[Przypadek] = [
    _przypadek("imię: 1 znak", _imie_jeden_znak),
    _przypadek(
        f"imię: maksymalna długość ({MAKS_DLUGOSC_IMIENIA} znaków)", _imie_maks
    ),
    _przypadek("data urodzenia: dziś", _urodzony_dzis),
    _przypadek("data urodzenia: 1900-01-01", _data_staly(date(1900, 1, 1))),
    _przypadek("data urodzenia: 1999-12-31", _data_staly(date(1999, 12, 31))),
    _przypadek(
        "data urodzenia: 2000-01-01 (PESEL: miesiąc +20)",
        _data_staly(date(2000, 1, 1)),
    ),
    _przypadek("data urodzenia: 29 lutego w roku przestępnym", _29_lutego),
    _przypadek("kod pocztowy: najmniejszy (00-001)", _kod("00-001", "Warszawa")),
    _przypadek("kod pocztowy: największy (99-999)", _kod("99-999")),
]


# --- bledne: jedno pole z błędną wartością ---


def _pesel_zla_suma(rekord, rng, dzis):
    p = rekord["pesel"]
    zla_cyfra = (int(p[10]) + rng.randint(1, 9)) % 10
    rekord["pesel"] = p[:10] + str(zla_cyfra)


def _pesel_10_cyfr(rekord, rng, dzis):
    rekord["pesel"] = rekord["pesel"][:10]


def _pesel_inna_data(rekord, rng, dzis):
    data = date.fromisoformat(rekord["data_urodzenia"])
    inna = data + timedelta(days=rng.randint(1, 3650))
    rekord["pesel"] = pesel(inna, _kobieta(rekord), rng)


def _email_bez_malpy(rekord, rng, dzis):
    rekord["email"] = rekord["email"].replace("@", "")


def _telefon_z_literami(rekord, rng, dzis):
    litery = "".join(rng.choice(string.ascii_lowercase) for _ in range(3))
    czesci = rekord["telefon"].split(" ")
    czesci[2] = litery
    rekord["telefon"] = " ".join(czesci)


def _kod_bez_myslnika(rekord, rng, dzis):
    rekord["kod_pocztowy"] = rekord["kod_pocztowy"].replace("-", "")


def _data_30_lutego(rekord, rng, dzis):
    rok = rekord["data_urodzenia"][:4]
    rekord["data_urodzenia"] = f"{rok}-02-30"


def _data_w_przyszlosci(rekord, rng, dzis):
    _ustaw_date(rekord, dzis + timedelta(days=rng.randint(1, 3650)), rng)


BLEDNE: list[Przypadek] = [
    _przypadek("PESEL: błędna suma kontrolna", _pesel_zla_suma),
    _przypadek("PESEL: 10 cyfr zamiast 11", _pesel_10_cyfr),
    _przypadek("PESEL: niezgodny z datą urodzenia", _pesel_inna_data),
    _przypadek("email: brak znaku @", _email_bez_malpy),
    _przypadek("telefon: litery zamiast cyfr", _telefon_z_literami),
    _przypadek("kod pocztowy: bez myślnika (5 cyfr)", _kod_bez_myslnika),
    _przypadek("data urodzenia: nieistniejąca (30 lutego)", _data_30_lutego),
    _przypadek("data urodzenia: w przyszłości", _data_w_przyszlosci),
]


# --- brakujace_pole: w każdym rekordzie brakuje innego pola, po kolei ---


def _brak_pola(pole: str) -> Przypadek:
    def zmiana(rekord, rng, dzis):
        del rekord[pole]

    return _przypadek(f"brak pola: {pole}", zmiana)


BRAKUJACE_POLE: list[Przypadek] = [
    _brak_pola(pole) for pole in POLA_OSOBY if pole != "przypadek"
]


SCENARIUSZE: dict[str, list[Przypadek]] = {
    "poprawne": [],
    "graniczne": GRANICZNE,
    "brakujace_pole": BRAKUJACE_POLE,
    "bledne": BLEDNE,
}


def generuj_rekordy(
    scenariusz: str, ilosc: int, seed: int | None = None, dzis: date | None = None
) -> list[dict]:
    """Zwraca `ilosc` rekordów dla podanego scenariusza.

    Ten sam `seed` (i ten sam dzień) daje identyczną listę.
    Scenariusz `poprawne` daje to samo co `generator.generuj_osoby`.
    """
    if scenariusz not in SCENARIUSZE:
        dostepne = ", ".join(SCENARIUSZE)
        raise ValueError(
            f"Nieznany scenariusz „{scenariusz}”. Dostępne scenariusze: {dostepne}."
        )
    if ilosc < 0:
        raise ValueError("Liczba rekordów nie może być ujemna.")
    dzis = dzis or date.today()
    rng = random.Random(seed)
    przypadki = SCENARIUSZE[scenariusz]
    rekordy = []
    for i in range(ilosc):
        rekord = generuj_osobe(rng)
        if przypadki:
            przypadki[i % len(przypadki)](rekord, rng, dzis)
        rekordy.append(rekord)
    return rekordy
