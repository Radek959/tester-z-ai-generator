# Generator danych testowych

Narzędzie dla testera, który nie programuje. Tworzy pliki z danymi testowymi
(polskie dane osobowe) w różnych scenariuszach: poprawne dane, wartości
graniczne, brakujące pola, błędne wartości.

> Status: **etap 7 – skrypty uruchomieniowe.** Dostępne są CLI i formularz w przeglądarce,
> JSON i CSV oraz scenariusze `poprawne`, `graniczne`, `brakujace_pole` i `bledne`.

## Wymagania

- Windows
- Zainstalowany Python 3; projekt sprawdzono na Pythonie 3.15.
- Połączenie z internetem do pobrania zależności podczas przygotowania.

## Pierwsze uruchomienie

1. Otwórz folder projektu w Eksploratorze plików. Jeśli pobrałeś archiwum ZIP,
   najpierw je rozpakuj.
2. Kliknij dwukrotnie **`setup.bat`**. Poczekaj na komunikat „Gotowe”, a potem
   naciśnij dowolny klawisz, aby zamknąć okno. Skrypt przygotuje środowisko
   `.venv` i zainstaluje potrzebne zależności. Wykonaj ten krok także po
   pobraniu aktualizacji projektu.
3. Kliknij dwukrotnie **`start_web.bat`**. Przeglądarka otworzy formularz pod
   adresem [http://127.0.0.1:5000](http://127.0.0.1:5000).
4. Wybierz format, scenariusz i liczbę rekordów. Pole **seed** możesz zostawić
   puste lub wpisać liczbę, aby móc powtórzyć te same dane.
5. Kliknij **Generuj**, a następnie **Pobierz plik**. Plik znajdziesz również
   w folderze `output/` wewnątrz projektu.

Podczas pracy pozostaw okno uruchomione przez `start_web.bat` otwarte.
Aby zakończyć, przejdź do tego okna i naciśnij **Ctrl+C**. Samo zamknięcie
karty przeglądarki nie zatrzymuje generatora. Przy kolejnym użyciu wystarczy
dwuklik `start_web.bat`.

Formularz używa domyślnej daty odniesienia, więc ten sam seed i parametry dają
plik identyczny z wynikiem CLI.

## Gdy nie udaje się uruchomić

- **Nie znaleziono Pythona:** zainstaluj Python 3 z opcją dodania go do PATH
  lub z launcherem `py`, a potem ponownie uruchom `setup.bat`.
- **Błąd instalacji zależności:** sprawdź połączenie z internetem i uruchom
  `setup.bat` ponownie. Skrypt korzysta z istniejącego `.venv`.
- **Brak `.venv` lub Flask:** uruchom `setup.bat`, a po jego powodzeniu
  `start_web.bat`.
- **Port 5000 jest zajęty:** zatrzymaj poprzedni generator przez Ctrl+C.
  Jeśli portu używa inny program, zamknij go i ponownie uruchom `start_web.bat`.
- **Przeglądarka nie otworzyła się:** pozostaw okno generatora otwarte i wpisz
  w przeglądarce [http://127.0.0.1:5000](http://127.0.0.1:5000).

Przy błędzie okno skryptu pozostaje otwarte do naciśnięcia klawisza,
aby można było przeczytać komunikat.

## Użycie w terminalu (opcjonalnie)

Po wykonaniu `setup.bat` otwórz PowerShell w folderze projektu.
Wygeneruj plik poleceniem:

```powershell
.\.venv\Scripts\python.exe -m testdata --format json --ilosc 10 --seed 42
```

Inny przykład i pomoc:

```powershell
.\.venv\Scripts\python.exe -m testdata --format csv --scenariusz bledne --ilosc 20 --seed 42
.\.venv\Scripts\python.exe -m testdata --help
```

Nie trzeba aktywować `.venv`. Formularz można też uruchomić z terminala:

```powershell
.\start_web.bat
```

## Powtarzalność i data odniesienia

Podanie tego samego seeda, formatu, scenariusza, liczby rekordów i daty
odniesienia daje identyczną treść pliku, także innego dnia. Nazwy plików mogą
się różnić. Bez seeda dane są losowe.

Domyślna data odniesienia jest stała: **2026-11-25**. Opisy „dziś” i „w przyszłości”
w scenariuszach odnoszą się do niej, a nie do zegara komputera. Aby zmienić tę datę:

```powershell
.\.venv\Scripts\python.exe -m testdata --scenariusz graniczne --ilosc 11 --seed 42 --data-odniesienia 2024-02-29
```

W Pythonie `service.generate_file(..., reference_date=date(2024, 2, 29))`
przyjmuje datę typu `datetime.date`; pominięcie parametru wybiera stałą domyślną.

## Bramki jakości (dla rozwijających projekt)

`setup.bat` instaluje też ustaloną wersję Ruff z `requirements-dev.txt`.
W razie potrzeby możesz zainstalować ją osobno przez interpreter projektu:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Po każdej zmianie w kodzie uruchom w PowerShell:

```powershell
.\check.bat
$LASTEXITCODE
```

Skrypt uruchamia testy `unittest` oraz Ruff, również gdy testy zawiodą.
Kod `0` oznacza, że oba kroki przeszły; `1` oznacza błąd, brak testów,
interpretera lub Ruff. Przy braku Ruff testy nadal się wykonują.
Skrypt działa też po wywołaniu pełną ścieżką z innego katalogu (ścieżkę ze
spacjami ujmij w cudzysłowy i poprzedź `&` w PowerShell).

Testy używają małych zestawów danych i własnych katalogów tymczasowych
wewnątrz `output/`. Sprzątają po sobie również po porażce; istniejące pliki
użytkownika pozostają na miejscu. Próby awarii `check.bat` używają kopii
skryptu i izolowanego środowiska, bez usuwania właściwej `.venv` lub testów.
Testy `setup.bat` i `start_web.bat` działają na osobnych kopiach projektu ze
spacjami w ścieżkach. Instalację pakietów i otwieranie przeglądarki symulują,
więc nie wymagają sieci ani nie otwierają okien.

## Gdzie trafiają pliki

Wszystkie wygenerowane pliki trafiają do folderu `output/`.
Ten folder nie jest zapisywany w repozytorium git.

## Planowane formaty

JSON, CSV, TXT, VCF, ICS.
