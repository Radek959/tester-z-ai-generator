import contextlib
import io
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

from testdata import __main__ as cli
from testdata import service
from testdata.scenarios import SCENARIUSZE, generuj_rekordy
from tests.helpers import REFERENCE, OutputTestCase, csv_records, read_records

ROOT = Path(__file__).resolve().parent.parent


class CliTests(OutputTestCase):
    def invoke(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                cli.main(args)
            except SystemExit as error:
                code = error.code
        return code, stdout.getvalue(), stderr.getvalue()

    def test_real_module_help(self):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "testdata", "--help"], cwd=ROOT,
            capture_output=True, encoding="utf-8", env=env, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("Użycie:", "Parametry", "--scenariusz", "--data-odniesienia", "2026-11-25",
                     "duplikaty", "nietypowe_znaki"):
            self.assertIn(text, result.stdout)
        self.assertEqual(result.stderr, "")

    def test_real_module_success(self):
        # Osobny proces, prawdziwy CLI i service; zmieniamy tylko folder wyjściowy.
        bootstrap = (
            "import runpy, sys; from pathlib import Path; from testdata import service; "
            "service.KATALOG_WYJSCIOWY = Path(sys.argv.pop(1)); "
            "runpy.run_module('testdata', run_name='__main__')"
        )
        result = subprocess.run(
            [sys.executable, "-c", bootstrap, str(self.folder), "--format", "json",
             "--scenariusz", "graniczne", "--ilosc", "11", "--seed", "42",
             "--data-odniesienia", "2024-02-29"],
            cwd=ROOT, capture_output=True, encoding="utf-8",
            env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Gotowe. Zapisano 11 rekordów", result.stdout)
        self.assertEqual(result.stderr, "")
        paths = list(self.folder.iterdir())
        self.assertEqual(len(paths), 1)
        self.assertEqual(read_records(paths[0]), generuj_rekordy("graniczne", 11, 42, date(2024, 2, 29)))

    def test_every_scenario_generates_file_and_is_described_in_help(self):
        code, help_text, _ = self.invoke(["--help"])
        self.assertEqual(code, 0)
        with patch.object(service, "KATALOG_WYJSCIOWY", self.folder):
            for scenario in SCENARIUSZE:
                with self.subTest(scenario=scenario):
                    self.assertRegex(help_text, rf"\n  {scenario} +– \S")
                    code, stdout, stderr = self.invoke(
                        ["--scenariusz", scenario, "--format", "csv", "--ilosc", "6", "--seed", "3"]
                    )
                    self.assertEqual(code, 0, stderr)
                    path = next(p for p in self.folder.iterdir() if p.name.startswith(f"{scenario}_csv_"))
                    self.assertEqual(
                        read_records(path), csv_records(generuj_rekordy(scenario, 6, 3, REFERENCE))
                    )

    def test_default_and_explicit_parameters_forwarded_to_service(self):
        cases = (
            ([], ("json", "poprawne", 10, None), None),
            (["--format", "CSV", "--scenariusz", "BLEDNE", "--ilosc", "3", "--seed", "7",
              "--data-odniesienia", "2030-01-01"], ("csv", "bledne", 3, 7), date(2030, 1, 1)),
        )
        for args, expected, reference in cases:
            with patch.object(cli.service, "generate_file", return_value=self.folder / "test.json") as generate:
                code, stdout, stderr = self.invoke(args)
            self.assertEqual(code, 0)
            self.assertIn("Gotowe.", stdout)
            self.assertEqual(stderr, "")
            generate.assert_called_once_with(*expected, reference_date=reference)

    def test_invalid_arguments_are_polish_without_tracebacks_or_files(self):
        cases = (
            (["--nieznany"], "Nieznane parametry"),
            (["--ilosc"], "trzeba podać wartość"),
            (["--ilosc", "abc"], "Ilość musi być liczbą całkowitą"),
            (["--seed", "abc"], "Seed musi być liczbą całkowitą"),
            (["--ilosc", "0"], "większa od zera"),
            (["--ilosc", "-5"], "większa od zera"),
            (["--ilosc", "100001"], "nie może być większa"),
            (["--format", "xml"], "Nieznany format"),
            (["--scenariusz", "zly"], "Nieznany scenariusz"),
            (["--data-odniesienia", "2023-02-30"], "Data odniesienia musi być poprawną datą"),
            (["--data-odniesienia", "20261125"], "w formacie RRRR-MM-DD"),
            (["--scenariusz", "bledne", "--ilosc", "8", "--data-odniesienia", "9999-12-31"],
             "jest poza zakresem"),
            (["--scenariusz", "graniczne", "--ilosc", "3", "--data-odniesienia", "1799-01-01"],
             "poza zakresem obsługiwanym przez PESEL"),
        )
        with patch.object(service, "KATALOG_WYJSCIOWY", self.folder):
            for args, message in cases:
                with self.subTest(args=args):
                    code, stdout, stderr = self.invoke(args)
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn("Błąd:", stderr)
                    self.assertIn(message, stderr)
                    self.assertNotIn("Traceback", stderr)
                    self.assertEqual(list(self.folder.iterdir()), [])

    def test_write_error_is_polish_without_traceback(self):
        with patch.object(service, "KATALOG_WYJSCIOWY", self.folder):
            with patch.dict(service.WRITERS, {"json": patch_writer}):
                code, stdout, stderr = self.invoke(["--ilosc", "1"])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("Błąd: Nie udało się zapisać pliku", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(list(self.folder.iterdir()), [])


def patch_writer(records, path):
    raise PermissionError("Brak dostępu")
