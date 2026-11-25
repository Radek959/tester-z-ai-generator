"""Próby check.bat na kopiach, bez zmieniania właściwej .venv i testów."""

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import OutputTestCase

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(sys.platform == "win32", "Skrypt jest przeznaczony dla Windows.")
class CheckScriptTests(OutputTestCase):
    def setUp(self):
        super().setUp()
        self.project = self.folder / "projekt ze spacjami"
        self.project.mkdir()
        shutil.copyfile(ROOT / "check.bat", self.project / "check.bat")
        self.tests = self.project / "tests"
        self.tests.mkdir()
        (self.tests / "__init__.py").touch()
        self.caller = self.folder / "katalog wywolujacy"
        self.caller.mkdir()

    def install_python(self):
        scripts = self.project / ".venv" / "Scripts"
        scripts.mkdir(parents=True)
        shutil.copyfile(sys.executable, scripts / "python.exe")
        shutil.copyfile(Path(sys.prefix) / "pyvenv.cfg", scripts.parent / "pyvenv.cfg")

    def install_test(self, failing=False):
        (self.tests / "test_probe.py").write_text(
            "import unittest\nclass Probe(unittest.TestCase):\n"
            "    def test_probe(self):\n"
            f"        self.assertTrue({not failing!r})\n", encoding="utf-8",
        )

    def install_fake_ruff(self, result=0):
        # Symulujemy jedynie wynik narzędzia; kolejność i kody obsługuje prawdziwy cmd.
        package = self.project / "ruff"
        package.mkdir()
        (package / "__init__.py").touch()
        (package / "__main__.py").write_text(
            f"print('RUFF_EXECUTED')\nraise SystemExit({result})\n", encoding="utf-8",
        )

    def run_check(self):
        original_cwd = Path.cwd()
        script = self.caller / "wywolaj.bat"
        script.write_text(
            f'@echo off\r\ncall "{self.project / "check.bat"}"\r\n'
            'set "CHECK_RESULT=%ERRORLEVEL%"\r\necho CALLER=%CD%\r\n'
            'exit /b %CHECK_RESULT%\r\n', encoding="utf-8",
        )
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", str(script)], cwd=self.caller,
            capture_output=True, env=env, timeout=30,
        )
        # cmd korzysta z kodowania konsoli; sprawdzane komunikaty skryptu są ASCII.
        self.stdout = result.stdout.decode("utf-8", errors="replace")
        self.stderr = result.stderr.decode("utf-8", errors="replace")
        self.assertIn(f"CALLER={self.caller}\r\n", self.stdout)
        self.assertEqual(Path.cwd(), original_cwd)
        return result.returncode

    def test_success_from_other_directory_and_spaces(self):
        self.install_python()
        self.install_test()
        self.install_fake_ruff()
        self.assertEqual(self.run_check(), 0, self.stdout + self.stderr)
        self.assertIn("Wykryte testy: 1", self.stdout)
        self.assertIn("Ran 1 test", self.stderr)
        self.assertIn("RUFF_EXECUTED", self.stdout)
        self.assertIn("Bramki jakosci: OK.", self.stdout)

    def test_failed_tests_still_run_ruff(self):
        self.install_python()
        self.install_test(failing=True)
        self.install_fake_ruff()
        self.assertEqual(self.run_check(), 1, self.stdout + self.stderr)
        self.assertIn("FAILED", self.stderr)
        self.assertIn("RUFF_EXECUTED", self.stdout)
        self.assertIn("Testy: blad.", self.stdout)
        self.assertIn("Ruff: OK.", self.stdout)

    def test_failed_ruff_preserves_test_success(self):
        self.install_python()
        self.install_test()
        self.install_fake_ruff(result=1)
        self.assertEqual(self.run_check(), 1, self.stdout + self.stderr)
        self.assertIn("Ran 1 test", self.stderr)
        self.assertIn("Testy: OK.", self.stdout)
        self.assertIn("Ruff: blad", self.stdout)

    def test_no_tests_is_failure(self):
        self.install_python()
        self.install_fake_ruff()
        self.assertEqual(self.run_check(), 1, self.stdout + self.stderr)
        self.assertIn("Wykryte testy: 0", self.stdout)
        self.assertIn("brak testow", self.stdout)
        self.assertIn("RUFF_EXECUTED", self.stdout)

    def test_missing_ruff_still_runs_tests(self):
        self.install_python()
        self.install_test()
        self.assertEqual(self.run_check(), 1, self.stdout + self.stderr)
        self.assertIn("Ran 1 test", self.stderr)
        self.assertIn("Testy: OK.", self.stdout)
        self.assertIn("Ruff: blad lub brak narzedzia", self.stdout)

    def test_missing_python(self):
        self.assertEqual(self.run_check(), 1, self.stdout + self.stderr)
        self.assertIn("brak interpretera", self.stdout)
