from datetime import date, datetime
from unittest.mock import patch

from testdata import service
from testdata.scenarios import generuj_rekordy
from tests.helpers import REFERENCE, OutputTestCase, csv_records, read_records


class ServiceTests(OutputTestCase):
    def setUp(self):
        super().setUp()
        patcher = patch.object(service, "KATALOG_WYJSCIOWY", self.folder)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_all_scenarios_and_formats(self):
        for scenario in ("poprawne", "graniczne", "brakujace_pole", "bledne"):
            expected = generuj_rekordy(scenario, 20, 42, REFERENCE)
            for format in ("json", "csv"):
                with self.subTest(scenario=scenario, format=format):
                    path = service.generate_file(format, scenario, 20, 42)
                    self.assertEqual(path.parent, self.folder)
                    self.assertTrue(path.is_relative_to(service.KATALOG_WYJSCIOWY))
                    self.assertEqual(path.suffix, f".{format}")
                    self.assertTrue(path.name.startswith(f"{scenario}_{format}_"))
                    rows = read_records(path)
                    self.assertEqual(len(rows), 20)
                    self.assertEqual(rows, expected if format == "json" else csv_records(expected))

    def test_collision_never_overwrites_existing_file(self):
        with patch.object(service, "datetime") as clock:
            clock.now.return_value = datetime(2026, 11, 25, 12, 0, 0)
            first = service.generate_file("json", "poprawne", 2, 42)
            original = first.read_bytes()
            second = service.generate_file("json", "poprawne", 3, 43)
            third = service.generate_file("json", "poprawne", 4, 44)
        self.assertEqual(first.name, "poprawne_json_20261125_120000.json")
        self.assertEqual(second.name, "poprawne_json_20261125_120000_2.json")
        self.assertEqual(third.name, "poprawne_json_20261125_120000_3.json")
        self.assertEqual(first.read_bytes(), original)
        self.assertEqual(len(read_records(second)), 3)
        self.assertEqual(len(read_records(third)), 4)

    def test_invalid_parameters_create_no_files(self):
        cases = (
            ("xml", "poprawne", 1, "Nieznany format"),
            ("json", "../bledne", 1, "Nieznany scenariusz"),
            ("../json", "poprawne", 1, "Nieznany format"),
            ("json", "poprawne", 0, "większa od zera"),
            ("csv", "poprawne", -5, "większa od zera"),
            ("json", "poprawne", 100_001, "nie może być większa niż 100000"),
        )
        sentinel = self.folder / "istniejacy.txt"
        sentinel.write_text("Plik użytkownika", encoding="utf-8")
        for format, scenario, count, message in cases:
            with self.subTest(format=format, scenario=scenario, count=count):
                with self.assertRaisesRegex(ValueError, message):
                    service.generate_file(format, scenario, count, 42)
                self.assertEqual(list(self.folder.iterdir()), [sentinel])
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "Plik użytkownika")

    def test_repeatability_in_bytes_on_different_days(self):
        for scenario in ("poprawne", "graniczne", "brakujace_pole", "bledne"):
            for format in ("json", "csv"):
                results = []
                for today in (date(2024, 2, 29), date(2030, 1, 1)):
                    with patch("testdata.scenarios.date", wraps=date) as clock:
                        clock.today.return_value = today
                        results.append(service.generate_file(format, scenario, 20, 42).read_bytes())
                self.assertEqual(results[0], results[1])

    def test_reference_date_is_forwarded_and_changes_content(self):
        for scenario in ("graniczne", "bledne"):
            for format in ("json", "csv"):
                paths = [
                    service.generate_file(format, scenario, 20, 42, reference_date=value)
                    for value in (date(2024, 2, 29), date(2030, 1, 1), date(2024, 2, 29))
                ]
                self.assertNotEqual(paths[0].read_bytes(), paths[1].read_bytes())
                self.assertEqual(paths[0].read_bytes(), paths[2].read_bytes())
                expected = generuj_rekordy(scenario, 20, 42, date(2024, 2, 29))
                self.assertEqual(read_records(paths[0]), expected if format == "json" else csv_records(expected))

    def test_missing_output_directory_is_created(self):
        destination = self.folder / "nowy"
        with patch.object(service, "KATALOG_WYJSCIOWY", destination):
            path = service.generate_file("json", "poprawne", 1, 42)
        self.assertEqual(path.parent, destination)
        self.assertEqual(len(read_records(path)), 1)
