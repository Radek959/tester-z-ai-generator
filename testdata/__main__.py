"""Wiersz poleceń: `python -m testdata --format json --ilosc 10`.

Tylko zbiera parametry i woła `service.generate_file`.
"""

import argparse
import sys

from testdata import service
from testdata.scenarios import SCENARIUSZE
from testdata.writers import WRITERS

DOMYSLNA_ILOSC = 10


class _PolskiFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, prefix="Użycie: ")


class _PolskiParser(argparse.ArgumentParser):
    """Parser z komunikatami błędów po polsku, bez angielskich wstawek."""

    def error(self, message: str) -> None:
        if message.startswith("unrecognized arguments:"):
            nieznane = message.split(":", 1)[1].strip()
            opis = f"Nieznane parametry: {nieznane}"
        elif "expected one argument" in message:
            opcja = message.split(":", 1)[0].replace("argument", "").strip()
            opis = f"Po parametrze {opcja} trzeba podać wartość."
        else:
            opis = "Nieprawidłowe parametry polecenia."
        _blad(f"{opis}\nPomoc: python -m testdata --help", kod=2)


def _blad(komunikat: str, kod: int = 1) -> None:
    print(f"Błąd: {komunikat}", file=sys.stderr)
    sys.exit(kod)


def _zbuduj_parser() -> argparse.ArgumentParser:
    formaty = ", ".join(WRITERS)
    scenariusze = ", ".join(SCENARIUSZE)
    parser = _PolskiParser(
        prog="python -m testdata",
        description="Generator danych testowych – tworzy plik z polskimi danymi osobowymi.",
        epilog=(
            "Przykłady:\n"
            "  python -m testdata --format json --ilosc 10\n"
            "  python -m testdata --format csv --ilosc 50 --seed 123\n"
            "  python -m testdata --scenariusz bledne --format csv --ilosc 20\n"
            "\n"
            "Scenariusze:\n"
            "  poprawne        – wszystkie dane poprawne\n"
            "  graniczne       – poprawne wartości na granicach (np. imię 1 znak, 29 lutego)\n"
            "  brakujace_pole  – w każdym rekordzie brakuje innego pola\n"
            "  bledne          – w każdym rekordzie jedno pole ma błędną wartość\n"
            "Opis przypadku jest w polu „przypadek” każdego rekordu.\n"
            "\n"
            "Plik trafia do folderu output/."
        ),
        formatter_class=_PolskiFormatter,
        add_help=False,
    )
    opcje = parser.add_argument_group("Parametry")
    opcje.add_argument(
        "--format",
        default="json",
        metavar="FORMAT",
        help=f"format pliku: {formaty} (domyślnie: json)",
    )
    opcje.add_argument(
        "--scenariusz",
        default="poprawne",
        metavar="NAZWA",
        help=f"scenariusz testowy: {scenariusze} (domyślnie: poprawne)",
    )
    opcje.add_argument(
        "--ilosc",
        default=str(DOMYSLNA_ILOSC),
        metavar="LICZBA",
        help=f"ile rekordów wygenerować (domyślnie: {DOMYSLNA_ILOSC})",
    )
    opcje.add_argument(
        "--seed",
        default=None,
        metavar="LICZBA",
        help="ziarno losowania – ten sam seed daje ten sam plik (domyślnie: losowe)",
    )
    opcje.add_argument("-h", "--help", action="help", help="pokaż tę pomoc i zakończ")
    return parser


def _na_liczbe(tekst: str, nazwa: str) -> int:
    try:
        return int(tekst)
    except ValueError:
        _blad(f"{nazwa} musi być liczbą całkowitą, a podano „{tekst}”.", kod=2)


def main(argv: list[str] | None = None) -> None:
    args = _zbuduj_parser().parse_args(argv)
    ilosc = _na_liczbe(args.ilosc, "Ilość")
    seed = None if args.seed is None else _na_liczbe(args.seed, "Seed")

    try:
        sciezka = service.generate_file(
            args.format.lower(), args.scenariusz.lower(), ilosc, seed
        )
    except ValueError as e:
        _blad(str(e), kod=2)
    except OSError as e:
        _blad(f"Nie udało się zapisać pliku ({e.strerror or e}).")

    print(f"Gotowe. Zapisano {ilosc} {_odmiana_rekord(ilosc)} do pliku:\n{sciezka}")


def _odmiana_rekord(n: int) -> str:
    if n == 1:
        return "rekord"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "rekordy"
    return "rekordów"


if __name__ == "__main__":
    main()
