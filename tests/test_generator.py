import random
import unittest
from datetime import date
from unittest.mock import Mock

from testdata import generator
from tests.helpers import FIELDS, birth_from_pesel, valid_checksum


class GeneratorTests(unittest.TestCase):
    def test_count_fields_and_valid_values(self):
        for count in (0, 1, 40):
            rows = generator.generuj_osoby(count, seed=42)
            self.assertEqual(len(rows), count)
            for row in rows:
                self.assertEqual(tuple(row), FIELDS)
                self.assertEqual(row["przypadek"], "poprawny")
                self.assertTrue(all(isinstance(value, str) and value for value in row.values()))
                self.assertTrue(valid_checksum(row["pesel"]))
                self.assertEqual(birth_from_pesel(row["pesel"]).isoformat(), row["data_urodzenia"])
                female = row["imie"] in generator.IMIONA_ZENSKIE
                self.assertEqual(int(row["pesel"][9]) % 2, 0 if female else 1)
                if row["nazwisko"].endswith(("ki", "ka")):
                    self.assertTrue(row["nazwisko"].endswith("ka" if female else "ki"))
                self.assertRegex(row["email"], r"^[a-z.]+\d+@example\.(com|org|net)$")
                self.assertRegex(row["telefon"], r"^\+48 [5678]\d{2} \d{3} \d{3}$")
                self.assertRegex(row["kod_pocztowy"], r"^\d{2}-\d{3}$")
                self.assertIn(row["miasto"], generator.MIASTA)

    def test_explicit_pesel_examples_for_dates_and_both_sexes(self):
        # Ustalone serie 123 i cyfry płci 4/5, oczekiwane wyniki wpisane niezależnie.
        cases = (
            (date(1999, 12, 31), True, "99123112343"),
            (date(1999, 12, 31), False, "99123112350"),
            (date(2000, 1, 1), True, "00210112344"),
            (date(2000, 1, 1), False, "00210112351"),
            (date(2000, 2, 29), True, "00222912349"),
            (date(2000, 2, 29), False, "00222912356"),
        )
        for birthday, female, expected in cases:
            with self.subTest(birthday=birthday, female=female):
                rng = Mock()
                rng.randint.return_value = 123
                rng.choice.return_value = "4" if female else "5"
                value = generator.pesel(birthday, female, rng)
                self.assertEqual(value, expected)
                self.assertTrue(valid_checksum(value))
                self.assertEqual(birth_from_pesel(value), birthday)
                rng.choice.assert_called_once_with("02468" if female else "13579")

    def test_repeatability_and_different_seeds(self):
        self.assertEqual(generator.generuj_osoby(10, 42), generator.generuj_osoby(10, 42))
        self.assertNotEqual(generator.generuj_osoby(10, 42), generator.generuj_osoby(10, 43))

    def test_global_random_is_unchanged(self):
        before = random.getstate()
        generator.generuj_osoby(10, 42)
        self.assertEqual(random.getstate(), before)

    def test_negative_count(self):
        with self.assertRaisesRegex(ValueError, "nie może być ujemna"):
            generator.generuj_osoby(-1, 42)
