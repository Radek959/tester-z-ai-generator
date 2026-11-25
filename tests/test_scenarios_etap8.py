"""Scenariusze `duplikaty` i `nietypowe_znaki` (etap 8)."""

import unittest
from datetime import date

from testdata import generator, scenarios
from testdata.writers import write_csv, write_json
from tests.helpers import (
    FIELDS,
    REFERENCE,
    OutputTestCase,
    birth_from_pesel,
    csv_records,
    read_records,
    valid_checksum,
)

DATA_FIELDS = tuple(field for field in FIELDS if field != "przypadek")


class DuplicatesTests(unittest.TestCase):
    def setUp(self):
        self.rows = scenarios.generuj_rekordy("duplikaty", 12, 42, REFERENCE)

    def test_cycle_of_descriptions(self):
        expected = [
            "duplikaty: rekord wzorcowy (nr 1)",
            "duplikat: pełna kopia danych rekordu nr 1",
            "duplikat PESEL: ten sam co w rekordzie nr 1",
            "duplikat email: ten sam co w rekordzie nr 1",
            "duplikat email: jak w rekordzie nr 1, inna wielkość liter",
            "duplikaty: rekord wzorcowy (nr 6)",
            "duplikat: pełna kopia danych rekordu nr 6",
            "duplikat PESEL: ten sam co w rekordzie nr 6",
            "duplikat email: ten sam co w rekordzie nr 6",
            "duplikat email: jak w rekordzie nr 6, inna wielkość liter",
            "duplikaty: rekord wzorcowy (nr 11)",
            "duplikat: pełna kopia danych rekordu nr 11",
        ]
        self.assertEqual([row["przypadek"] for row in self.rows], expected)
        for row in self.rows:
            self.assertEqual(tuple(row), FIELDS)

    def test_duplicates_match_their_template(self):
        for start in (0, 5):
            with self.subTest(start=start):
                template = self.rows[start]
                full, same_pesel, same_email, upper_email = self.rows[start + 1:start + 5]
                self.assertEqual(
                    {f: full[f] for f in DATA_FIELDS},
                    {f: template[f] for f in DATA_FIELDS},
                )
                self.assertEqual(same_pesel["pesel"], template["pesel"])
                self.assertEqual(same_pesel["data_urodzenia"], template["data_urodzenia"])
                self.assertNotEqual(same_pesel["imie"], template["imie"])
                self.assertNotEqual(same_pesel["email"], template["email"])
                self.assertEqual(same_email["email"], template["email"])
                self.assertNotEqual(same_email["pesel"], template["pesel"])
                self.assertEqual(upper_email["email"], template["email"].upper())
                self.assertNotEqual(upper_email["email"], template["email"])
                self.assertEqual(upper_email["email"].lower(), template["email"])

    def test_same_pesel_person_is_consistent(self):
        # Inna osoba z tym samym PESEL: poprawna suma, data i płeć zgodne z PESEL.
        for index in (2, 7):
            row = self.rows[index]
            with self.subTest(index=index):
                self.assertTrue(valid_checksum(row["pesel"]))
                self.assertEqual(
                    birth_from_pesel(row["pesel"]), date.fromisoformat(row["data_urodzenia"])
                )
                female = int(row["pesel"][9]) % 2 == 0
                names = generator.IMIONA_ZENSKIE if female else generator.IMIONA_MESKIE
                self.assertIn(row["imie"], names)

    def test_small_counts(self):
        self.assertEqual(
            [r["przypadek"] for r in scenarios.generuj_rekordy("duplikaty", 1, 1)],
            ["duplikaty: rekord wzorcowy (nr 1)"],
        )
        self.assertEqual(scenarios.generuj_rekordy("duplikaty", 0, 1), [])

    def test_repeatable(self):
        self.assertEqual(scenarios.generuj_rekordy("duplikaty", 12, 42, REFERENCE), self.rows)


class UnusualCharactersTests(unittest.TestCase):
    def setUp(self):
        self.rows = scenarios.generuj_rekordy("nietypowe_znaki", 9, 42, REFERENCE)
        self.base = generator.generuj_osoby(9, 42)

    def test_every_case_and_cycle(self):
        descriptions = (
            "imię: emoji", "imię: cudzysłowy", "nazwisko: apostrof",
            "miasto: przecinek w wartości", "nazwisko: znak nowej linii",
            "imię: spacje na początku i końcu",
            "nazwisko: bardzo długa wartość (1000 znaków)",
        )
        for index, row in enumerate(self.rows):
            case = index % 7
            with self.subTest(index=index, case=case):
                self.assertEqual(row["przypadek"], descriptions[case])
                self.assertEqual(tuple(row), FIELDS)
                if case == 0:
                    self.assertTrue(row["imie"].endswith(" 😀"))
                elif case == 1:
                    self.assertEqual(row["imie"].count('"'), 2)
                elif case == 2:
                    self.assertIn("'", row["nazwisko"])
                elif case == 3:
                    self.assertIn(",", row["miasto"])
                elif case == 4:
                    self.assertIn("\n", row["nazwisko"])
                elif case == 5:
                    self.assertNotEqual(row["imie"], row["imie"].strip())
                    self.assertTrue(row["imie"].startswith(" "))
                    self.assertTrue(row["imie"].endswith(" "))
                elif case == 6:
                    self.assertEqual(len(row["nazwisko"]), 1000)

    def test_only_described_field_changes(self):
        changed = {0: "imie", 1: "imie", 2: "nazwisko", 3: "miasto",
                   4: "nazwisko", 5: "imie", 6: "nazwisko"}
        for index, (row, base) in enumerate(zip(self.rows, self.base)):
            with self.subTest(index=index):
                field = changed[index % 7]
                self.assertNotEqual(row[field], base[field])
                for other in DATA_FIELDS:
                    if other != field:
                        self.assertEqual(row[other], base[other])


class UnusualCharactersFilesTests(OutputTestCase):
    def test_csv_and_json_roundtrip(self):
        rows = scenarios.generuj_rekordy("nietypowe_znaki", 14, 3, REFERENCE)
        for format, writer in (("json", write_json), ("csv", write_csv)):
            with self.subTest(format=format):
                path = self.folder / f"nietypowe.{format}"
                writer(rows, path)
                expected = rows if format == "json" else csv_records(rows)
                self.assertEqual(read_records(path), expected)

    def test_duplicates_csv_roundtrip(self):
        rows = scenarios.generuj_rekordy("duplikaty", 10, 3, REFERENCE)
        path = self.folder / "duplikaty.csv"
        write_csv(rows, path)
        self.assertEqual(read_records(path), csv_records(rows))
