from unittest.mock import patch

from testdata import service
from testdata.scenarios import SCENARIUSZE
from tests.helpers import OutputTestCase, read_records
from web.app import OPISY_SCENARIUSZY, app


class WebTests(OutputTestCase):
    def setUp(self):
        super().setUp()
        patcher = patch.object(service, "KATALOG_WYJSCIOWY", self.folder)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = app.test_client()

    def post(self, **pola):
        dane = {"format": "json", "scenariusz": "poprawne", "ilosc": "5", "seed": "42"}
        dane.update(pola)
        return self.client.post("/", data=dane)

    def files(self):
        return sorted(self.folder.iterdir())

    def test_form_lists_formats_and_scenarios(self):
        odpowiedz = self.client.get("/")
        self.assertEqual(odpowiedz.status_code, 200)
        html = odpowiedz.get_data(as_text=True)
        for nazwa in ("json", "csv", "poprawne", "graniczne", "brakujace_pole", "bledne",
                      "duplikaty", "nietypowe_znaki"):
            self.assertIn(f'value="{nazwa}"', html)
        self.assertIn("Generuj", html)

    def test_every_scenario_on_form_with_description(self):
        # Każdy scenariusz z logiki musi być do wyboru na froncie i mieć opis.
        html = self.client.get("/").get_data(as_text=True)
        for nazwa in SCENARIUSZE:
            with self.subTest(scenariusz=nazwa):
                self.assertTrue(OPISY_SCENARIUSZY.get(nazwa, "").strip())
                self.assertIn(f'value="{nazwa}"', html)
                self.assertIn(
                    f"<code>{nazwa}</code><small>{OPISY_SCENARIUSZY[nazwa]}</small>", html
                )
        self.assertEqual(set(OPISY_SCENARIUSZY), set(SCENARIUSZE))

    def test_generates_file_and_download_link(self):
        for format in ("json", "csv"):
            with self.subTest(format=format):
                odpowiedz = self.post(format=format, scenariusz="bledne")
                self.assertEqual(odpowiedz.status_code, 200)
                sciezka = self.files()[-1] if format == "json" else next(
                    p for p in self.files() if p.suffix == ".csv")
                self.assertEqual(len(read_records(sciezka)), 5)
                html = odpowiedz.get_data(as_text=True)
                link = f"/pobierz/{sciezka.name}"
                self.assertIn(link, html)
                pobrany = self.client.get(link)
                self.assertEqual(pobrany.status_code, 200)
                self.assertIn("attachment", pobrany.headers["Content-Disposition"])
                self.assertEqual(pobrany.data, sciezka.read_bytes())
                pobrany.close()

    def test_same_content_as_service(self):
        self.post(format="csv", scenariusz="graniczne", ilosc="12", seed="7")
        (z_formularza,) = self.files()
        z_service = service.generate_file("csv", "graniczne", 12, 7)
        self.assertEqual(z_formularza.read_bytes(), z_service.read_bytes())

    def test_new_scenarios_from_form(self):
        for scenariusz in ("duplikaty", "nietypowe_znaki"):
            with self.subTest(scenariusz=scenariusz):
                odpowiedz = self.post(format="csv", scenariusz=scenariusz, ilosc="10", seed="5")
                self.assertEqual(odpowiedz.status_code, 200)
                sciezka = next(p for p in self.files() if p.name.startswith(scenariusz))
                z_service = service.generate_file("csv", scenariusz, 10, 5)
                self.assertEqual(sciezka.read_bytes(), z_service.read_bytes())

    def test_empty_seed_means_random(self):
        odpowiedz = self.post(seed="  ")
        self.assertEqual(odpowiedz.status_code, 200)
        self.assertEqual(len(self.files()), 1)

    def test_form_errors_in_polish_without_file(self):
        przypadki = {
            "ilosc": ("abc", "Ilość musi być liczbą całkowitą"),
            "seed": ("x1", "Seed musi być liczbą całkowitą"),
        }
        for pole, (wartosc, komunikat) in przypadki.items():
            with self.subTest(pole=pole):
                odpowiedz = self.post(**{pole: wartosc})
                self.assertEqual(odpowiedz.status_code, 400)
                self.assertIn(komunikat, odpowiedz.get_data(as_text=True))
        for pola, komunikat in (
            ({"ilosc": ""}, "Podaj liczbę rekordów."),
            ({"ilosc": "0"}, "większa od zera"),
            ({"ilosc": "-5"}, "większa od zera"),
            ({"ilosc": "100001"}, "nie może być większa"),
            ({"format": "xml"}, "Nieznany format"),
            ({"scenariusz": "inne"}, "Nieznany scenariusz"),
        ):
            with self.subTest(pola=pola):
                odpowiedz = self.post(**pola)
                self.assertEqual(odpowiedz.status_code, 400)
                self.assertIn(komunikat, odpowiedz.get_data(as_text=True))
        self.assertEqual(self.files(), [])

    def test_write_error_shows_polish_message(self):
        with patch.object(service, "WRITERS", {"json": self._fail}):
            odpowiedz = self.post()
        self.assertEqual(odpowiedz.status_code, 500)
        html = odpowiedz.get_data(as_text=True)
        self.assertIn("Nie udało się zapisać pliku", html)
        self.assertNotIn("Traceback", html)

    @staticmethod
    def _fail(rekordy, sciezka):
        raise PermissionError(13, "Brak dostępu")

    def test_download_missing_or_outside_output(self):
        for adres in ("/pobierz/brak.json", "/pobierz/..%2Fpyproject.toml"):
            with self.subTest(adres=adres):
                odpowiedz = self.client.get(adres)
                self.assertEqual(odpowiedz.status_code, 404)
                self.assertIn("Nie znaleziono pliku", odpowiedz.get_data(as_text=True))
