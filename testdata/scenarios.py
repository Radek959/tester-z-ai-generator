"""Scenariusze testowe: modyfikacje poprawnych rekordów `osoba`.

Każdy scenariusz to lista przypadków. Rekord nr i dostaje przypadek nr
(i mod liczba_przypadków), więc już kilka rekordów pokazuje różne przypadki.
Przypadek zmienia rekord i wpisuje swój opis do pola `przypadek`.
"""

import random
import string
from collections.abc import Callable
from datetime import date, timedelta

from testdata.generator import (
    IMIONA_MESKIE,
    IMIONA_ZENSKIE,
    NAZWISKA,
    POLA_OSOBY,
    _email,
    _nazwisko_dla_plci,
    generuj_osobe,
    pesel,
)

MAKS_DLUGOSC_IMIENIA = 50
BARDZO_DLUGA_WARTOSC = 1000
DOMYSLNA_DATA_ODNIESIENIA = date(2026, 11, 25)

# Przypadek: (rekord, rng, dzis, poprzednie) -> None, modyfikuje rekord w miejscu.
# `poprzednie` to rekordy wygenerowane wcześniej w tym samym pliku.
Przypadek = Callable[[dict, random.Random, date, list[dict]], None]
# Zmiana: (rekord, rng, dzis) -> None, gdy przypadek nie zależy od innych rekordów.
Zmiana = Callable[[dict, random.Random, date], None]


def _kobieta(rekord: dict) -> bool:
    """Płeć odczytana z PESEL (dziesiąta cyfra parzysta = kobieta)."""
    return int(rekord["pesel"][9]) % 2 == 0


def _ustaw_date(rekord: dict, data: date, rng: random.Random) -> None:
    """Zmienia datę urodzenia i dopasowuje do niej PESEL."""
    rekord["data_urodzenia"] = data.isoformat()
    rekord["pesel"] = pesel(data, _kobieta(rekord), rng)


def _przypadek(opis: str, zmiana: Zmiana) -> Przypadek:
    def zastosuj(
        rekord: dict, rng: random.Random, dzis: date, poprzednie: list[dict]
    ) -> None:
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


def _data_staly(data: date) -> Zmiana:
    def zmiana(rekord, rng, dzis):
        _ustaw_date(rekord, data, rng)

    return zmiana


def _29_lutego(rekord, rng, dzis):
    rok = rng.choice(range(1940, 2008, 4))
    _ustaw_date(rekord, date(rok, 2, 29), rng)


def _kod(kod: str, miasto: str | None = None) -> Zmiana:
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
    przesuniecie = timedelta(days=rng.randint(1, 3650))
    try:
        data = dzis + przesuniecie
    except OverflowError:
        raise ValueError(
            f"Data odniesienia {dzis.isoformat()} jest poza zakresem: "
            "nie da się utworzyć daty urodzenia w przyszłości."
        ) from None
    _ustaw_date(rekord, data, rng)


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


# --- duplikaty: grupy po 5 rekordów, pierwszy jest wzorcem dla czterech kolejnych ---


def _wzorzec(poprzednie: list[dict], odstep: int) -> tuple[dict, int]:
    """Zwraca rekord wzorcowy sprzed `odstep` rekordów i jego numer w pliku (od 1)."""
    return poprzednie[-odstep], len(poprzednie) - odstep + 1


def _wzorcowy(rekord, rng, dzis, poprzednie):
    rekord["przypadek"] = f"duplikaty: rekord wzorcowy (nr {len(poprzednie) + 1})"


def _pelna_kopia(rekord, rng, dzis, poprzednie):
    wzor, numer = _wzorzec(poprzednie, 1)
    rekord.clear()
    rekord.update(wzor)
    rekord["przypadek"] = f"duplikat: pełna kopia danych rekordu nr {numer}"


def _ten_sam_pesel(rekord, rng, dzis, poprzednie):
    """Inna osoba tej samej płci, z tym samym PESEL i datą urodzenia co wzorzec."""
    wzor, numer = _wzorzec(poprzednie, 2)
    kobieta = _kobieta(wzor)
    imiona = IMIONA_ZENSKIE if kobieta else IMIONA_MESKIE
    inne_imiona = [imie for imie in imiona if imie != wzor["imie"]]
    rekord["imie"] = rng.choice(inne_imiona)
    rekord["nazwisko"] = _nazwisko_dla_plci(rng.choice(NAZWISKA), kobieta)
    rekord["email"] = _email(rekord["imie"], rekord["nazwisko"], rng)
    rekord["pesel"] = wzor["pesel"]
    rekord["data_urodzenia"] = wzor["data_urodzenia"]
    rekord["przypadek"] = f"duplikat PESEL: ten sam co w rekordzie nr {numer}"


def _ten_sam_email(rekord, rng, dzis, poprzednie):
    wzor, numer = _wzorzec(poprzednie, 3)
    rekord["email"] = wzor["email"]
    rekord["przypadek"] = f"duplikat email: ten sam co w rekordzie nr {numer}"


def _email_inna_wielkosc_liter(rekord, rng, dzis, poprzednie):
    wzor, numer = _wzorzec(poprzednie, 4)
    rekord["email"] = wzor["email"].upper()
    rekord["przypadek"] = (
        f"duplikat email: jak w rekordzie nr {numer}, inna wielkość liter"
    )


DUPLIKATY: list[Przypadek] = [
    _wzorcowy,
    _pelna_kopia,
    _ten_sam_pesel,
    _ten_sam_email,
    _email_inna_wielkosc_liter,
]


# --- nietypowe_znaki: znaki, które często psują import, parsowanie lub widok ---


def _imie_emoji(rekord, rng, dzis):
    rekord["imie"] = f"{rekord['imie']} 😀"


def _imie_cudzyslow(rekord, rng, dzis):
    imie = rekord["imie"]
    rekord["imie"] = f'{imie} "{imie[:3]}"'


def _nazwisko_apostrof(rekord, rng, dzis):
    rekord["nazwisko"] = f"{rekord['nazwisko']}-O'Brien"


def _miasto_przecinek(rekord, rng, dzis):
    rekord["miasto"] = f"{rekord['miasto']}, Śródmieście"


def _nazwisko_nowa_linia(rekord, rng, dzis):
    rekord["nazwisko"] = f"{rekord['nazwisko']}\nNowak"


def _imie_spacje(rekord, rng, dzis):
    rekord["imie"] = f"  {rekord['imie']}  "


def _nazwisko_bardzo_dlugie(rekord, rng, dzis):
    nazwisko = rekord["nazwisko"]
    powtorzone = "-".join([nazwisko] * BARDZO_DLUGA_WARTOSC)
    rekord["nazwisko"] = powtorzone[:BARDZO_DLUGA_WARTOSC]


NIETYPOWE_ZNAKI: list[Przypadek] = [
    _przypadek("imię: emoji", _imie_emoji),
    _przypadek("imię: cudzysłowy", _imie_cudzyslow),
    _przypadek("nazwisko: apostrof", _nazwisko_apostrof),
    _przypadek("miasto: przecinek w wartości", _miasto_przecinek),
    _przypadek("nazwisko: znak nowej linii", _nazwisko_nowa_linia),
    _przypadek("imię: spacje na początku i końcu", _imie_spacje),
    _przypadek(
        f"nazwisko: bardzo długa wartość ({BARDZO_DLUGA_WARTOSC} znaków)",
        _nazwisko_bardzo_dlugie,
    ),
]


SCENARIUSZE: dict[str, list[Przypadek]] = {
    "poprawne": [],
    "graniczne": GRANICZNE,
    "brakujace_pole": BRAKUJACE_POLE,
    "bledne": BLEDNE,
    "duplikaty": DUPLIKATY,
    "nietypowe_znaki": NIETYPOWE_ZNAKI,
}


def generuj_rekordy(
    scenariusz: str, ilosc: int, seed: int | None = None, dzis: date | None = None
) -> list[dict]:
    """Zwraca `ilosc` rekordów dla podanego scenariusza.

    Ten sam `seed` i parametry dają identyczną listę niezależnie od zegara.
    `dzis` to jawna data odniesienia; domyślnie 2026-11-25.
    Scenariusz `poprawne` daje to samo co `generator.generuj_osoby`.
    """
    if scenariusz not in SCENARIUSZE:
        dostepne = ", ".join(SCENARIUSZE)
        raise ValueError(
            f"Nieznany scenariusz „{scenariusz}”. Dostępne scenariusze: {dostepne}."
        )
    if ilosc < 0:
        raise ValueError("Liczba rekordów nie może być ujemna.")
    dzis = dzis if dzis is not None else DOMYSLNA_DATA_ODNIESIENIA
    rng = random.Random(seed)
    przypadki = SCENARIUSZE[scenariusz]
    rekordy = []
    for i in range(ilosc):
        rekord = generuj_osobe(rng)
        if przypadki:
            przypadki[i % len(przypadki)](rekord, rng, dzis, rekordy)
        rekordy.append(rekord)
    return rekordy
