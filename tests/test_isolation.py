import unittest
from unittest.mock import patch

from testdata import service
from tests.helpers import OutputTestCase


class IsolationTests(OutputTestCase):
    def test_failed_file_test_cleans_only_its_own_directory(self):
        sentinel = self.folder / "plik_uzytkownika.txt"
        sentinel.write_bytes(b"Nie zmieniaj tego pliku.")
        created = []

        class DeliberatelyFailingTest(OutputTestCase):
            def runTest(inner):
                created.append(inner.folder)
                with patch.object(service, "KATALOG_WYJSCIOWY", inner.folder):
                    path = service.generate_file("json", "poprawne", 2, 42)
                inner.assertTrue(path.exists())
                inner.fail("Celowa porażka po zapisaniu pliku.")

        before = set(self.folder.parent.iterdir())
        result = unittest.TestResult()
        DeliberatelyFailingTest().run(result)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(len(created), 1)
        self.assertFalse(created[0].exists())
        self.assertEqual(set(self.folder.parent.iterdir()), before)
        self.assertEqual(sentinel.read_bytes(), b"Nie zmieniaj tego pliku.")
