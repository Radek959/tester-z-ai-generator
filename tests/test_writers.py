import csv
import json

from testdata.writers import write_csv, write_json
from tests.helpers import FIELDS, OutputTestCase, csv_records, read_records


class WriterTests(OutputTestCase):
    def setUp(self):
        super().setUp()
        self.rows = [{
            "imie": "Łukasz", "nazwisko": "Żółć", "pesel": "00210112351",
            "data_urodzenia": "2000-01-01", "email": "lukasz@example.org",
            "telefon": "+48 600 123 456", "kod_pocztowy": "00-001",
            "miasto": "Łódź", "przypadek": "poprawny",
        }]
        missing = dict(self.rows[0])
        del missing["email"]
        missing["przypadek"] = "brak pola: email"
        self.rows.append(missing)

    def test_json_roundtrip_encoding_layout_and_missing_key(self):
        path = self.folder / "osoby.json"
        write_json(self.rows, path)
        self.assertEqual(read_records(path), self.rows)
        text = path.read_bytes().decode("utf-8")
        self.assertIn("Łukasz", text)
        self.assertIn("Żółć", text)
        self.assertNotIn(r"\u", text)
        self.assertIn('\n  {\n    "imie":', text)
        self.assertTrue(text.endswith("\n"))
        self.assertNotIn("email", json.loads(text)[1])

    def test_csv_roundtrip_encoding_header_and_empty_cell(self):
        path = self.folder / "osoby.csv"
        write_csv(self.rows, path)
        self.assertEqual(read_records(path), csv_records(self.rows))
        text = path.read_bytes().decode("utf-8")
        self.assertIn("Łukasz", text)
        self.assertIn("Żółć", text)
        self.assertEqual(text.splitlines()[0], ",".join(FIELDS))
        with path.open(encoding="utf-8", newline="") as stream:
            lines = list(csv.reader(stream, delimiter=","))
        self.assertEqual([len(row) for row in lines], [9, 9, 9])
        self.assertEqual(lines[2][4], "")
        self.assertEqual(lines[2][5], self.rows[1]["telefon"])
        self.assertEqual(lines[2][8], "brak pola: email")

    def test_empty_exports(self):
        for format, writer in (("json", write_json), ("csv", write_csv)):
            path = self.folder / f"puste.{format}"
            writer([], path)
            self.assertEqual(read_records(path), [])
        self.assertEqual((self.folder / "puste.csv").read_text(encoding="utf-8").strip(), ",".join(FIELDS))
