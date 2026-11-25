# Generator danych testowych

Narzędzie dla testera, który nie programuje. Tworzy pliki z danymi testowymi
(polskie dane osobowe) w różnych scenariuszach: poprawne dane, wartości
graniczne, brakujące pola, błędne wartości.

> Status: **etap 0 – szkielet projektu.** Generator jeszcze nie działa.

## Wymagania

- Windows
- Python 3 (sprawdzisz poleceniem `py -3 --version`)

## Pierwsze uruchomienie

1. Otwórz PowerShell w folderze projektu.
2. Jeśli folderu `.venv` nie ma, utwórz go:

   ```powershell
   py -3 -m venv .venv
   ```

3. Aktywuj środowisko:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Po aktywacji na początku linii zobaczysz `(.venv)`.

## Gdzie trafiają pliki

Wszystkie wygenerowane pliki trafiają do folderu `output/`.
Ten folder nie jest zapisywany w repozytorium git.

## Planowane formaty

JSON, CSV, TXT, VCF, ICS.
