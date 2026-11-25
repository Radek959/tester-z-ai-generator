"""Generowanie poprawnych rekordów encji `osoba` z polskimi danymi."""

import random
from datetime import date, timedelta

IMIONA_MESKIE = [
    "Adam", "Andrzej", "Bartosz", "Damian", "Dawid", "Grzegorz", "Jakub",
    "Jan", "Kamil", "Krzysztof", "Łukasz", "Maciej", "Marcin", "Mateusz",
    "Michał", "Paweł", "Piotr", "Rafał", "Szymon", "Tomasz", "Wojciech",
    "Zbigniew",
]

IMIONA_ZENSKIE = [
    "Agnieszka", "Aleksandra", "Anna", "Barbara", "Beata", "Dorota", "Ewa",
    "Grażyna", "Joanna", "Julia", "Katarzyna", "Magdalena", "Małgorzata",
    "Maria", "Marta", "Monika", "Natalia", "Paulina", "Zofia", "Żaneta",
]

# Nazwiska w formie męskiej; forma żeńska tworzona w `_nazwisko_dla_plci`.
NAZWISKA = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński",
    "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Dąbrowski",
    "Kozłowski", "Jankowski", "Mazur", "Kwiatkowski", "Krawczyk", "Piotrowski",
    "Grabowski", "Zając", "Pawłowski", "Michalski", "Król", "Wieczorek",
    "Jabłoński", "Wróbel", "Nowicki", "Majewski", "Olszewski", "Stępień",
    "Jaworski", "Malinowski", "Górecki", "Sadowski", "Zawadzki",
]

# Miasto -> możliwe dwucyfrowe początki kodu pocztowego.
MIASTA = {
    "Warszawa": ["00", "01", "02", "03", "04"],
    "Kraków": ["30", "31"],
    "Łódź": ["90", "91", "92", "93", "94"],
    "Wrocław": ["50", "51", "52", "53", "54"],
    "Poznań": ["60", "61"],
    "Gdańsk": ["80"],
    "Szczecin": ["70", "71"],
    "Bydgoszcz": ["85"],
    "Lublin": ["20"],
    "Białystok": ["15"],
    "Katowice": ["40"],
    "Gdynia": ["81"],
    "Częstochowa": ["42"],
    "Radom": ["26"],
    "Rzeszów": ["35"],
    "Toruń": ["87"],
    "Kielce": ["25"],
    "Olsztyn": ["10"],
    "Opole": ["45"],
    "Zielona Góra": ["65"],
}

DOMENY_EMAIL = ["example.com", "example.org", "example.net"]

# Stały zakres dat urodzenia, żeby wynik nie zależał od dnia uruchomienia.
DATA_URODZENIA_OD = date(1940, 1, 1)
DATA_URODZENIA_DO = date(2007, 12, 31)

WAGI_PESEL = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)

_ZAMIANA_POLSKICH_ZNAKOW = str.maketrans(
    "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ"
)


def cyfra_kontrolna_pesel(pierwsze_10_cyfr: str) -> int:
    """Zwraca cyfrę kontrolną PESEL dla pierwszych 10 cyfr."""
    suma = sum(int(c) * w for c, w in zip(pierwsze_10_cyfr, WAGI_PESEL))
    return (10 - suma % 10) % 10


def _przesuniecie_miesiaca(rok: int) -> int:
    if 1800 <= rok <= 1899:
        return 80
    if 1900 <= rok <= 1999:
        return 0
    if 2000 <= rok <= 2099:
        return 20
    if 2100 <= rok <= 2199:
        return 40
    if 2200 <= rok <= 2299:
        return 60
    raise ValueError(f"Rok {rok} jest poza zakresem obsługiwanym przez PESEL.")


def pesel(data_urodzenia: date, kobieta: bool, rng: random.Random) -> str:
    """Tworzy PESEL zgodny z datą urodzenia i płcią, z poprawną sumą kontrolną."""
    miesiac = data_urodzenia.month + _przesuniecie_miesiaca(data_urodzenia.year)
    data_czesc = f"{data_urodzenia.year % 100:02d}{miesiac:02d}{data_urodzenia.day:02d}"
    numer_serii = f"{rng.randint(0, 999):03d}"
    # Dziesiąta cyfra: parzysta dla kobiet, nieparzysta dla mężczyzn.
    cyfra_plci = rng.choice("02468" if kobieta else "13579")
    pierwsze_10 = data_czesc + numer_serii + cyfra_plci
    return pierwsze_10 + str(cyfra_kontrolna_pesel(pierwsze_10))


def _nazwisko_dla_plci(nazwisko: str, kobieta: bool) -> str:
    if kobieta and nazwisko.endswith("ki"):
        return nazwisko[:-1] + "a"
    return nazwisko


def _bez_polskich_znakow(tekst: str) -> str:
    return tekst.translate(_ZAMIANA_POLSKICH_ZNAKOW)


def _losowa_data(rng: random.Random) -> date:
    dni = (DATA_URODZENIA_DO - DATA_URODZENIA_OD).days
    return DATA_URODZENIA_OD + timedelta(days=rng.randint(0, dni))


def _email(imie: str, nazwisko: str, rng: random.Random) -> str:
    lokalna = _bez_polskich_znakow(f"{imie}.{nazwisko}").lower()
    return f"{lokalna}{rng.randint(1, 99)}@{rng.choice(DOMENY_EMAIL)}"


def _telefon(rng: random.Random) -> str:
    cyfry = str(rng.choice("5678")) + "".join(str(rng.randint(0, 9)) for _ in range(8))
    return f"+48 {cyfry[0:3]} {cyfry[3:6]} {cyfry[6:9]}"


def _kod_pocztowy(miasto: str, rng: random.Random) -> str:
    return f"{rng.choice(MIASTA[miasto])}-{rng.randint(1, 999):03d}"


def generuj_osobe(rng: random.Random) -> dict:
    """Zwraca jeden poprawny rekord `osoba`."""
    kobieta = rng.random() < 0.5
    imie = rng.choice(IMIONA_ZENSKIE if kobieta else IMIONA_MESKIE)
    nazwisko = _nazwisko_dla_plci(rng.choice(NAZWISKA), kobieta)
    data_urodzenia = _losowa_data(rng)
    miasto = rng.choice(list(MIASTA))
    return {
        "imie": imie,
        "nazwisko": nazwisko,
        "pesel": pesel(data_urodzenia, kobieta, rng),
        "data_urodzenia": data_urodzenia.isoformat(),
        "email": _email(imie, nazwisko, rng),
        "telefon": _telefon(rng),
        "kod_pocztowy": _kod_pocztowy(miasto, rng),
        "miasto": miasto,
        "przypadek": "poprawny",
    }


def generuj_osoby(ilosc: int, seed: int | None = None) -> list[dict]:
    """Zwraca listę `ilosc` poprawnych rekordów `osoba`.

    Ten sam `seed` daje zawsze identyczną listę.
    """
    if ilosc < 0:
        raise ValueError("Liczba rekordów nie może być ujemna.")
    rng = random.Random(seed)
    return [generuj_osobe(rng) for _ in range(ilosc)]
