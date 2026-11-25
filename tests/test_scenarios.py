import random
import re
import unittest
from datetime import date
from unittest.mock import patch

from testdata import generator, scenarios
from tests.helpers import FIELDS, REFERENCE, birth_from_pesel, valid_checksum


def invalid_fields(row):
    """Zwraca nazwy pól, które łamią reguły poprawnego rekordu."""
    invalid = set()
    try:
        birthday = date.fromisoformat(row["data_urodzenia"])
    except ValueError:
        birthday = None
    if birthday is None or birthday > REFERENCE:
        invalid.add("data_urodzenia")
    pesel = row["pesel"]
    if not valid_checksum(pesel) or (birthday and birth_from_pesel(pesel) != birthday):
        invalid.add("pesel")
    if row["imie"] not in generator.IMIONA_MESKIE + generator.IMIONA_ZENSKIE:
        invalid.add("imie")
    if not re.fullmatch(r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+", row["nazwisko"]):
        invalid.add("nazwisko")
    if not re.fullmatch(r"[a-z.]+\d+@example\.(com|org|net)", row["email"]):
        invalid.add("email")
    if not re.fullmatch(r"\+48 \d{3} \d{3} \d{3}", row["telefon"]):
        invalid.add("telefon")
    if row["miasto"] not in generator.MIASTA:
        invalid.add("miasto")
    elif not re.fullmatch(r"\d{2}-\d{3}", row["kod_pocztowy"]) or (
        row["kod_pocztowy"][:2] not in generator.MIASTA[row["miasto"]]
    ):
        invalid.add("kod_pocztowy")
    return invalid


class ScenarioTests(unittest.TestCase):
    def test_correct_matches_generator(self):
        self.assertEqual(
            scenarios.generuj_rekordy("poprawne", 20, 42, REFERENCE),
            generator.generuj_osoby(20, 42),
        )

    def test_every_boundary_case_and_cycle(self):
        descriptions = (
            "imię: 1 znak", "imię: maksymalna długość (50 znaków)",
            "data urodzenia: dziś", "data urodzenia: 1900-01-01",
            "data urodzenia: 1999-12-31",
            "data urodzenia: 2000-01-01 (PESEL: miesiąc +20)",
            "data urodzenia: 29 lutego w roku przestępnym",
            "kod pocztowy: najmniejszy (00-001)",
            "kod pocztowy: największy (99-999)",
        )
        rows = scenarios.generuj_rekordy("graniczne", 20, 42, REFERENCE)
        self.assertEqual(len(rows), 20)
        for index, row in enumerate(rows):
            case = index % 9
            with self.subTest(index=index, case=case):
                self.assertEqual(row["przypadek"], descriptions[case])
                self.assertEqual(set(row), set(FIELDS))
                birthday = date.fromisoformat(row["data_urodzenia"])
                self.assertTrue(valid_checksum(row["pesel"]))
                self.assertEqual(birth_from_pesel(row["pesel"]), birthday)
                # Imię może być zmienione, email zachowuje imię sprzed modyfikacji.
                original_name = row["email"].split(".")[0]
                female = original_name in {
                    "agnieszka", "aleksandra", "anna", "barbara", "beata", "dorota",
                    "ewa", "grazyna", "joanna", "julia", "katarzyna", "magdalena",
                    "malgorzata", "maria", "marta", "monika", "natalia", "paulina",
                    "zofia", "zaneta",
                }
                self.assertEqual(int(row["pesel"][9]) % 2, 0 if female else 1)
                if case == 0:
                    self.assertEqual(len(row["imie"]), 1)
                elif case == 1:
                    self.assertEqual(len(row["imie"]), 50)
                elif case in (2, 3, 4, 5):
                    expected = {2: REFERENCE, 3: date(1900, 1, 1),
                                4: date(1999, 12, 31), 5: date(2000, 1, 1)}[case]
                    self.assertEqual(birthday, expected)
                    self.assertEqual(row["pesel"][2:4], "21" if case == 5 else f"{expected.month + (20 if expected.year >= 2000 else 0):02d}")
                elif case == 6:
                    self.assertEqual((birthday.month, birthday.day), (2, 29))
                    self.assertIn(birthday.year, range(1940, 2008, 4))
                elif case == 7:
                    self.assertEqual(row["kod_pocztowy"], "00-001")
                    self.assertEqual(row["miasto"], "Warszawa")
                elif case == 8:
                    self.assertEqual(row["kod_pocztowy"], "99-999")

    def test_every_invalid_case_and_cycle(self):
        descriptions = (
            "PESEL: błędna suma kontrolna", "PESEL: 10 cyfr zamiast 11",
            "PESEL: niezgodny z datą urodzenia", "email: brak znaku @",
            "telefon: litery zamiast cyfr", "kod pocztowy: bez myślnika (5 cyfr)",
            "data urodzenia: nieistniejąca (30 lutego)", "data urodzenia: w przyszłości",
        )
        rows = scenarios.generuj_rekordy("bledne", 18, 42, REFERENCE)
        self.assertEqual(len(rows), 18)
        for index, row in enumerate(rows):
            case = index % 8
            with self.subTest(index=index, case=case):
                self.assertEqual(row["przypadek"], descriptions[case])
                self.assertEqual(set(row), set(FIELDS))
                if case == 0:
                    self.assertRegex(row["pesel"], r"^[0-9]{11}$")
                    self.assertFalse(valid_checksum(row["pesel"]))
                    self.assertEqual(birth_from_pesel(row["pesel"]).isoformat(), row["data_urodzenia"])
                elif case == 1:
                    self.assertRegex(row["pesel"], r"^[0-9]{10}$")
                elif case == 2:
                    self.assertTrue(valid_checksum(row["pesel"]))
                    difference = birth_from_pesel(row["pesel"]) - date.fromisoformat(row["data_urodzenia"])
                    self.assertIn(difference.days, range(1, 3651))
                elif case == 3:
                    self.assertNotIn("@", row["email"])
                elif case == 4:
                    self.assertRegex(row["telefon"], r"^\+48 \d{3} [a-z]{3} \d{3}$")
                elif case == 5:
                    self.assertRegex(row["kod_pocztowy"], r"^[0-9]{5}$")
                elif case == 6:
                    self.assertTrue(row["data_urodzenia"].endswith("-02-30"))
                    with self.assertRaises(ValueError):
                        date.fromisoformat(row["data_urodzenia"])
                elif case == 7:
                    birthday = date.fromisoformat(row["data_urodzenia"])
                    self.assertIn((birthday - REFERENCE).days, range(1, 3651))
                    self.assertTrue(valid_checksum(row["pesel"]))
                    self.assertEqual(birth_from_pesel(row["pesel"]), birthday)

    def test_invalid_case_breaks_exactly_one_field(self):
        # Opis przypadku -> jedyne pole, które ma być błędne; reszta rekordu poprawna.
        expected = {
            "PESEL: błędna suma kontrolna": {"pesel"},
            "PESEL: 10 cyfr zamiast 11": {"pesel"},
            "PESEL: niezgodny z datą urodzenia": {"pesel"},
            "email: brak znaku @": {"email"},
            "telefon: litery zamiast cyfr": {"telefon"},
            "kod pocztowy: bez myślnika (5 cyfr)": {"kod_pocztowy"},
            "data urodzenia: nieistniejąca (30 lutego)": {"data_urodzenia"},
            "data urodzenia: w przyszłości": {"data_urodzenia"},
        }
        for seed in range(5):
            for index, row in enumerate(scenarios.generuj_rekordy("bledne", 16, seed, REFERENCE)):
                with self.subTest(seed=seed, index=index, case=row["przypadek"]):
                    self.assertIn(row["przypadek"], expected)
                    self.assertEqual(invalid_fields(row), expected[row["przypadek"]])

    def test_missing_fields_cycle_and_preserve_description(self):
        rows = scenarios.generuj_rekordy("brakujace_pole", 18, 42, REFERENCE)
        for index, row in enumerate(rows):
            missing = FIELDS[index % 8]
            self.assertEqual(set(FIELDS) - set(row), {missing})
            self.assertEqual(set(row) - set(FIELDS), set())
            self.assertEqual(row["przypadek"], f"brak pola: {missing}")

    def test_repeatability_and_global_random(self):
        for scenario in ("poprawne", "graniczne", "bledne", "brakujace_pole"):
            with self.subTest(scenario=scenario):
                before = random.getstate()
                rows = scenarios.generuj_rekordy(scenario, 20, 42, REFERENCE)
                self.assertEqual(rows, scenarios.generuj_rekordy(scenario, 20, 42, REFERENCE))
                self.assertNotEqual(rows, scenarios.generuj_rekordy(scenario, 20, 43, REFERENCE))
                self.assertEqual(random.getstate(), before)

    def test_explicit_reference_dates(self):
        for scenario, index in (("graniczne", 2), ("bledne", 7)):
            first = scenarios.generuj_rekordy(scenario, 20, 42, date(2024, 2, 29))
            second = scenarios.generuj_rekordy(scenario, 20, 42, date(2030, 1, 1))
            self.assertNotEqual(first, second)
            difference = date.fromisoformat(second[index]["data_urodzenia"]) - date.fromisoformat(first[index]["data_urodzenia"])
            self.assertEqual(difference, date(2030, 1, 1) - date(2024, 2, 29))
        self.assertEqual(first, scenarios.generuj_rekordy("bledne", 20, 42, date(2024, 2, 29)))

    def test_default_reference_ignores_wall_clock(self):
        for scenario in ("poprawne", "graniczne", "bledne", "brakujace_pole"):
            results = []
            for today in (date(2024, 2, 29), date(2030, 1, 1)):
                with patch("testdata.scenarios.date", wraps=date) as clock:
                    clock.today.return_value = today
                    results.append(scenarios.generuj_rekordy(scenario, 20, 42))
                    clock.today.assert_not_called()
            self.assertEqual(results[0], results[1])
            self.assertEqual(results[0], scenarios.generuj_rekordy(scenario, 20, 42, REFERENCE))

    def test_correct_records_have_no_invalid_fields(self):
        # Kontrola samego walidatora: poprawne rekordy nie mogą być przez niego odrzucane.
        for row in scenarios.generuj_rekordy("poprawne", 40, 42, REFERENCE):
            self.assertEqual(invalid_fields(row), set())

    def test_reference_date_out_of_range_is_polish_value_error(self):
        with self.assertRaisesRegex(ValueError, "Data odniesienia 9999-12-31 jest poza zakresem"):
            scenarios.generuj_rekordy("bledne", 8, 42, date(9999, 12, 31))

    def test_invalid_parameters_and_empty_result(self):
        with self.assertRaisesRegex(ValueError, "Nieznany scenariusz"):
            scenarios.generuj_rekordy("nieznany", 1)
        with self.assertRaisesRegex(ValueError, "nie może być ujemna"):
            scenarios.generuj_rekordy("poprawne", -1)
        self.assertEqual(scenarios.generuj_rekordy("poprawne", 0, 42), [])
