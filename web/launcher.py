"""Uruchomienie lokalnego formularza z automatycznym otwarciem przeglądarki."""

import webbrowser
from contextlib import redirect_stderr
from io import StringIO
from threading import Thread

from werkzeug.serving import make_server

from web.app import app

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


def _otworz_przegladarke() -> None:
    try:
        if webbrowser.open(URL):
            return
    except (OSError, webbrowser.Error):
        pass
    print(f"Nie udało się otworzyć przeglądarki. Otwórz samodzielnie: {URL}")


def main() -> int:
    try:
        # Werkzeug sam kończy proces przy błędzie wiązania portu. Zastępujemy
        # jego komunikat czytelną instrukcją po polsku.
        with redirect_stderr(StringIO()):
            serwer = make_server(HOST, PORT, app, threaded=True)
    except (OSError, SystemExit):
        print(
            f"Nie udało się uruchomić formularza pod adresem {URL}. "
            f"Port {PORT} może być zajęty. Zamknij poprzednie okno generatora "
            "lub inny program korzystający z tego portu i spróbuj ponownie."
        )
        return 1

    try:
        print(f"Generator danych testowych: {URL}")
        print("Pozostaw to okno otwarte. Aby zakończyć, naciśnij Ctrl+C.")
        # Port jest już zajęty przez nasz serwer; przeglądarka może się połączyć.
        Thread(target=_otworz_przegladarke, daemon=True).start()
        serwer.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError:
        print("Wystąpił błąd serwera. Uruchom start_web.bat ponownie.")
        return 1
    finally:
        serwer.server_close()
    print("Generator został zatrzymany.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
