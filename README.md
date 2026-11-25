# Generator danych testowych

Narzędzie dla testera, który nie programuje. Tworzy pliki z danymi testowymi
(polskie dane osobowe) w różnych scenariuszach: poprawne dane, wartości
graniczne, brakujące pola, błędne wartości.

> Status: **etap 6 – frontend Flask.** Dostępne są CLI i formularz w przeglądarce,
> JSON i CSV oraz scenariusze `poprawne`, `graniczne`, `brakujace_pole` i `bledne`.

## Wymagania

- Windows
- Python 3; środowisko projektu i reguły Ruff skonfigurowano dla Python 3.15
  (wersję sprawdzisz poleceniem `py -3 --version`)

## Pierwsze uruchomienie

1. Otwórz PowerShell w folderze projektu.
2. Jeśli folderu `.venv` nie ma, utwórz go:

   ```powershell
   py -3 -m venv .venv
   ```

3. Wygeneruj plik, używając interpretera z `.venv` (aktywacja nie jest potrzebna):

   ```powershell
   .\.venv\Scripts\python.exe -m testdata --format json --ilosc 10 --seed 42
   ```

   Inny przykład i pomoc:

   ```powershell
   .\.venv\Scripts\python.exe -m testdata --format csv --scenariusz bledne --ilosc 20 --seed 42
   .\.venv\Scripts\python.exe -m testdata --help
   ```

## Formularz w przeglądarce

1. Zainstaluj Flask (raz):

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Uruchom serwer:

   ```powershell
   .\.venv\Scripts\python.exe -m web.app
   ```

3. Otwórz w przeglądarce <http://127.0.0.1:5000>, wybierz format, scenariusz,
   ilość i (opcjonalnie) seed, kliknij **Generuj**, a potem **Pobierz plik**.
   Plik zapisuje się też w `output/`. Serwer zatrzymasz klawiszami `Ctrl+C`.

Formularz używa domyślnej daty odniesienia, więc ten sam seed i parametry dają
plik identyczny z wynikiem CLI.

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

Zainstaluj ustaloną wersję Ruff przez interpreter projektu:

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

## Gdzie trafiają pliki

Wszystkie wygenerowane pliki trafiają do folderu `output/`.
Ten folder nie jest zapisywany w repozytorium git.

## Planowane formaty

JSON, CSV, TXT, VCF, ICS.
