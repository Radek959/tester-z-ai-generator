"""Skrypty wykonujemy przez cmd w izolowanych kopiach, bez sieci i przeglądarki."""

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import OutputTestCase

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(sys.platform == "win32", "Skrypty są przeznaczone dla Windows.")
class StartupScriptTests(OutputTestCase):
    def setUp(self):
        super().setUp()
        self.project = self.folder / "projekt ze spacjami"
        self.project.mkdir()
        for name in ("setup.bat", "start_web.bat", "requirements.txt", "requirements-dev.txt"):
            shutil.copyfile(ROOT / name, self.project / name)
        self.caller = self.folder / "katalog wywolujacy"
        self.caller.mkdir()

    def install_python(self):
        scripts = self.project / ".venv" / "Scripts"
        scripts.mkdir(parents=True)
        shutil.copyfile(sys.executable, scripts / "python.exe")
        shutil.copyfile(Path(sys.prefix) / "pyvenv.cfg", scripts.parent / "pyvenv.cfg")

    def fake_module(self, name, code):
        package = self.project / name
        package.mkdir()
        (package / "__init__.py").touch()
        (package / "__main__.py").write_text(code, encoding="utf-8")

    def fake_pip(self, result=0):
        self.fake_module("pip", (
            "import json, sys\nfrom pathlib import Path\n"
            "Path('pip_args.json').write_text(json.dumps(sys.argv[1:]))\n"
            f"raise SystemExit({result})\n"
        ))

    def run_script(self, name, *, bootstrap=True):
        wrapper = self.caller / "wywolaj.bat"
        wrapper.write_text(
            f'@echo off\r\ncall "{self.project / name}"\r\n'
            'set "SCRIPT_RESULT=%ERRORLEVEL%"\r\necho CALLER=%CD%\r\n'
            'exit /b %SCRIPT_RESULT%\r\n', encoding="utf-8",
        )
        # Wybieramy rzeczywisty Python, bez launchera py i aliasów WindowsApps.
        paths = [str(Path(os.environ["SystemRoot"]) / "System32")]
        if bootstrap:
            paths.insert(0, str(Path(sys._base_executable).parent))
        env = dict(
            os.environ, PATH=os.pathsep.join(paths), PYTHONIOENCODING="utf-8",
            PYTHONDONTWRITEBYTECODE="1",
        )
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", str(wrapper)], cwd=self.caller,
            stdin=subprocess.DEVNULL, capture_output=True, env=env, timeout=60,
        )
        self.output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        self.assertIn(f"CALLER={self.caller}\r\n", self.output)
        self.assertNotIn("Traceback", self.output)
        return result.returncode

    def test_setup_creates_venv_and_installs_both_requirement_files(self):
        self.fake_pip()
        self.assertEqual(self.run_script("setup.bat"), 0, self.output)
        self.assertTrue((self.project / ".venv" / "Scripts" / "python.exe").is_file())
        self.assertEqual(
            json.loads((self.project / "pip_args.json").read_text()),
            ["install", "-r", "requirements.txt", "-r", "requirements-dev.txt"],
        )
        self.assertIn("Gotowe", self.output)

    def test_setup_reuses_existing_venv_without_global_python(self):
        self.install_python()
        sentinel = self.project / ".venv" / "zachowaj.txt"
        sentinel.write_bytes(b"istniejace srodowisko")
        self.fake_pip()
        self.assertEqual(self.run_script("setup.bat", bootstrap=False), 0, self.output)
        self.assertEqual(sentinel.read_bytes(), b"istniejace srodowisko")
        self.assertNotIn("Tworzenie", self.output)

    def test_setup_missing_python(self):
        self.assertEqual(self.run_script("setup.bat", bootstrap=False), 1, self.output)
        self.assertIn("nie znaleziono Pythona 3", self.output)
        self.assertFalse((self.project / ".venv").exists())

    def test_setup_creation_failure_does_not_install_packages(self):
        (self.project / "venv.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
        self.fake_pip()
        self.assertEqual(self.run_script("setup.bat"), 1, self.output)
        self.assertIn("nie udalo sie utworzyc srodowiska", self.output)
        self.assertFalse((self.project / "pip_args.json").exists())

    def test_setup_incomplete_venv_is_not_overwritten(self):
        folder = self.project / ".venv"
        folder.mkdir()
        sentinel = folder / "zachowaj.txt"
        sentinel.write_bytes(b"zachowaj")
        self.assertEqual(self.run_script("setup.bat"), 1, self.output)
        self.assertIn("folder .venv jest niekompletny", self.output)
        self.assertEqual(sentinel.read_bytes(), b"zachowaj")

    def test_setup_pip_failure(self):
        self.install_python()
        self.fake_pip(result=1)
        self.assertEqual(self.run_script("setup.bat"), 1, self.output)
        self.assertIn("nie udalo sie zainstalowac zaleznosci", self.output)
        self.assertNotIn("Gotowe", self.output)

    def test_start_missing_venv(self):
        self.assertEqual(self.run_script("start_web.bat"), 1, self.output)
        self.assertIn("Uruchom najpierw setup.bat", self.output)

    def test_start_missing_flask(self):
        self.install_python()
        self.assertEqual(self.run_script("start_web.bat"), 1, self.output)
        self.assertIn("brak Flask", self.output)

    def test_start_runs_launcher_and_preserves_exit_code(self):
        self.install_python()
        (self.project / "flask.py").touch()
        package = self.project / "web"
        package.mkdir()
        (package / "__init__.py").touch()
        for code in (0, 1):
            with self.subTest(code=code):
                (package / "launcher.py").write_text(
                    f"print('LAUNCHER_EXECUTED')\nraise SystemExit({code})\n", encoding="utf-8",
                )
                self.assertEqual(self.run_script("start_web.bat"), code, self.output)
                self.assertIn("LAUNCHER_EXECUTED", self.output)
