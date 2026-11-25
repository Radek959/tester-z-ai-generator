"""Frontend Flask: `.\\.venv\\Scripts\\python.exe -m web.app`.

Tylko zbiera parametry z formularza i woła `service.generate_file`.
"""

from flask import Flask, abort, render_template, request, send_from_directory, url_for

from testdata import service
from testdata.scenarios import DOMYSLNA_DATA_ODNIESIENIA, SCENARIUSZE
from testdata.writers import WRITERS

DOMYSLNA_ILOSC = 10

OPISY_SCENARIUSZY = {
    "poprawne": "wszystkie dane poprawne",
    "graniczne": "poprawne wartości na granicach",
    "brakujace_pole": "w każdym rekordzie brakuje innego pola",
    "bledne": "w każdym rekordzie jedno pole ma błędną wartość",
    "duplikaty": "pełne kopie rekordów i powtórzone PESEL lub email",
    "nietypowe_znaki": "emoji, cudzysłowy, przecinki, nowe linie, długie wartości",
}

app = Flask(__name__)


def _na_liczbe(tekst: str, nazwa: str) -> int:
    try:
        return int(tekst.strip())
    except ValueError:
        raise ValueError(f"{nazwa} musi być liczbą całkowitą, a podano „{tekst}”.") from None


def _widok(formularz: dict, **kontekst):
    scenariusze = [(nazwa, OPISY_SCENARIUSZY.get(nazwa, "")) for nazwa in SCENARIUSZE]
    return render_template(
        "index.html", formaty=list(WRITERS), scenariusze=scenariusze,
        formularz=formularz, data_odniesienia=DOMYSLNA_DATA_ODNIESIENIA.isoformat(),
        **kontekst,
    )


@app.get("/")
def index():
    formularz = {"format": "json", "scenariusz": "poprawne",
                 "ilosc": str(DOMYSLNA_ILOSC), "seed": ""}
    return _widok(formularz)


@app.post("/")
def generuj():
    formularz = {
        "format": request.form.get("format", ""),
        "scenariusz": request.form.get("scenariusz", ""),
        "ilosc": request.form.get("ilosc", ""),
        "seed": request.form.get("seed", ""),
    }
    try:
        if not formularz["ilosc"].strip():
            raise ValueError("Podaj liczbę rekordów.")
        ilosc = _na_liczbe(formularz["ilosc"], "Ilość")
        seed = None
        if formularz["seed"].strip():
            seed = _na_liczbe(formularz["seed"], "Seed")
        sciezka = service.generate_file(
            formularz["format"], formularz["scenariusz"], ilosc, seed
        )
    except ValueError as e:
        return _widok(formularz, blad=str(e)), 400
    except OSError as e:
        return _widok(formularz, blad=f"Nie udało się zapisać pliku ({e.strerror or e})."), 500

    wynik = {
        "nazwa": sciezka.name,
        "ilosc": ilosc,
        "rozmiar": sciezka.stat().st_size,
        "link": url_for("pobierz", nazwa=sciezka.name),
    }
    return _widok(formularz, wynik=wynik)


@app.get("/pobierz/<nazwa>")
def pobierz(nazwa: str):
    # Ścieżka zawsze w `output/`; send_from_directory odrzuca wyjście poza katalog.
    katalog = service.KATALOG_WYJSCIOWY
    if not (katalog / nazwa).is_file():
        abort(404)
    return send_from_directory(katalog, nazwa, as_attachment=True)


@app.errorhandler(404)
def nie_znaleziono(_blad):
    return _widok({"format": "json", "scenariusz": "poprawne",
                   "ilosc": str(DOMYSLNA_ILOSC), "seed": ""},
                  blad="Nie znaleziono pliku. Wygeneruj go ponownie."), 404


if __name__ == "__main__":
    print("Generator danych testowych: http://127.0.0.1:5000  (Ctrl+C kończy)")
    app.run(host="127.0.0.1", port=5000)
