# Plan implementacji

Generator danych testowych: CLI + frontend Flask, wspólna logika.
Jeden etap = jeden commit, po ręcznej weryfikacji i potwierdzeniu przez użytkownika.

**Jak oznaczać ukończenie:** zamień `[ ]` na `[x]` przy nagłówku etapu
i wpisz datę oraz skrót commita w polu „Ukończono”.

## Postęp

| Etap | Nazwa | Status |
|---|---|---|
| 0 | Szkielet projektu | [x] |
| 1 | Generator poprawnych rekordów | [x] |
| 2 | CLI i eksport JSON | [x] |
| 3 | Eksport CSV | [x] |
| 4 | Scenariusze testowe | [ ] |
| 5 | Bramki jakości | [ ] |
| 6 | Frontend Flask | [ ] |
| 7 | Skrypty uruchomieniowe | [ ] |
| 8 | Duplikaty i nietypowe znaki | [ ] |
| 9 | Eksport TXT | [ ] |
| 10 | Eksport VCF | [ ] |
| 11 | Eksport ICS | [ ] |

MVP = etapy 0–4.

---

## [x] Etap 0 – Szkielet projektu

**Zakres**
- Repozytorium git (gałąź `main`).
- `.venv` w folderze projektu.
- `.gitignore` (`.venv/`, `output/*` poza `.gitkeep`, cache).
- `output/.gitkeep`, `README.md`, `AGENTS.md`, `PLAN.md`.

**Weryfikacja ręczna**
- `git status` jest czysty po commicie.
- `.venv` jest ignorowany przez git.

**Commit:** `chore: szkielet projektu`
**Ukończono:** 2026-11-25, `beffb50`

---

## [x] Etap 1 – Generator poprawnych rekordów

**Zakres**
- `testdata/__init__.py`, `testdata/generator.py`.
- Funkcja zwracająca listę słowników `osoba` o zadanej liczbie, z parametrem `seed`.
- Pola: `imie`, `nazwisko`, `pesel`, `data_urodzenia`, `email`, `telefon`, `kod_pocztowy`, `miasto`, `przypadek` (= `poprawny`).
- PESEL zgodny z datą urodzenia i płcią, z poprawną sumą kontrolną.
- Polskie imiona, nazwiska (forma zgodna z płcią) i miasta z list wpisanych w kod.
- Losowość przez `random.Random(seed)`.

**Weryfikacja ręczna**
- Wywołanie funkcji w REPL zwraca sensowne rekordy z polskimi danymi.
- Dwa wywołania z tym samym seedem dają identyczny wynik, różne seedy – różny.
- PESEL z wyniku sprawdzony w dowolnym walidatorze online jest poprawny.

**Commit:** `feat: generator poprawnych rekordów`
**Ukończono:** 2026-11-25, `e9e0777`

---

## [x] Etap 2 – CLI i eksport JSON

**Zakres**
- `testdata/writers.py` z `write_json` i rejestrem `format -> funkcja`.
- `testdata/service.py` z `generate_file(format, scenario, count, seed)` zwracającą ścieżkę pliku.
- `testdata/__main__.py` (argparse): `--format`, `--ilosc`, `--seed`.
- Plik w `output/`, nazwa z formatem, scenariuszem i znacznikiem czasu.
- JSON w UTF-8, czytelne wcięcia, polskie znaki bez escape'owania.
- Zrozumiałe komunikaty błędów po polsku (np. ujemna ilość).

**Weryfikacja ręczna**
- `python -m testdata --help` pokazuje czytelną pomoc.
- `python -m testdata --format json --ilosc 10` tworzy plik z 10 rekordami w `output/`.
- Plik otwiera się w Notatniku z poprawnymi polskimi znakami.
- `--ilosc -5` daje komunikat po polsku zamiast tracebacku.

**Commit:** `feat: CLI i eksport JSON`
**Ukończono:** 2026-11-25, `bc55270`

---

## [x] Etap 3 – Eksport CSV

**Zakres**
- `write_csv` w `writers.py`, wpis w rejestrze.
- UTF-8, separator `,`, nagłówek z nazwami pól.

**Weryfikacja ręczna**
- `python -m testdata --format csv --ilosc 10` tworzy plik w `output/`.
- Plik w Notatniku: nagłówek + 10 wierszy, polskie znaki poprawne.
- Import w Excelu (Dane → Z tekstu/CSV, UTF-8) daje poprawne kolumny.

**Commit:** `feat: eksport CSV`
**Ukończono:** —

---

## [ ] Etap 4 – Scenariusze testowe

**Zakres**
- `testdata/scenarios.py`, parametr `--scenariusz` w CLI.
- `poprawne` – jak w etapie 1.
- `graniczne` – np. imię 1 znak i maksymalnej długości, urodzony dziś, urodzony 1900-01-01, PESEL z 2000+ (miesiąc +20), 29 lutego w roku przestępnym, kody `00-001` i `99-999`.
- `brakujace_pole` – w każdym rekordzie brakuje innego pola (po kolei); `przypadek` zostaje. JSON: brak klucza, CSV: pusta komórka.
- `bledne` – np. PESEL ze złą sumą kontrolną, PESEL 10 znaków, email bez `@`, telefon z literami, kod `12345`, data `2023-02-30`, data urodzenia w przyszłości.
- Każdy rekord ma w `przypadek` opis przypadku po polsku.

**Weryfikacja ręczna**
- Dla każdego scenariusza i obu formatów powstaje plik.
- W pliku widać zamierzone anomalie, a `przypadek` je trafnie opisuje.
- Ten sam seed daje identyczny plik.

**Commit:** `feat: scenariusze testowe`
**Ukończono:** —

---

## [ ] Etap 5 – Bramki jakości

**Zakres**
- Testy jednostkowe (`unittest`) w `tests/`: generator (PESEL, seed), scenariusze, writery.
- `pyproject.toml` z konfiguracją Ruff, `requirements-dev.txt` (ruff).
- Jedno polecenie uruchamiające testy i Ruff (np. `check.bat`).

**Weryfikacja ręczna**
- `check.bat` kończy się na zielono.
- Celowo zepsuty kod (np. zła suma PESEL) daje czerwony wynik.

**Commit:** `test: testy jednostkowe i Ruff`
**Ukończono:** —

---

## [ ] Etap 6 – Frontend Flask

**Zakres**
- `web/app.py`, `web/templates/index.html`, `requirements.txt` (Flask).
- Formularz: format, scenariusz, ilość, seed; przycisk „Generuj”.
- Wywołanie `service.generate_file` (bez duplikacji logiki), plik w `output/`, link do pobrania.
- Błędy formularza po polsku.

**Weryfikacja ręczna**
- Formularz działa w przeglądarce, plik pojawia się w `output/` i da się go pobrać.
- Ten sam seed i parametry dają plik identyczny z wynikiem CLI.

**Commit:** `feat: frontend Flask`
**Ukończono:** —

---

## [ ] Etap 7 – Skrypty uruchomieniowe

**Zakres**
- `setup.bat` – tworzy `.venv` (jeśli brak) i instaluje zależności.
- `start_web.bat` – uruchamia Flaska i otwiera przeglądarkę.
- Aktualizacja README pod nieprogramistę.

**Weryfikacja ręczna**
- Świeży klon repo: dwuklik `setup.bat`, potem `start_web.bat` – formularz działa.

**Commit:** `chore: skrypty uruchomieniowe`
**Ukończono:** —

---

## [ ] Etap 8 – Duplikaty i nietypowe znaki

**Zakres**
- Scenariusz `duplikaty` – pełne duplikaty rekordów oraz duplikaty kluczowych pól (PESEL, email).
- Scenariusz `nietypowe_znaki` – emoji, cudzysłowy, przecinki i znaki nowej linii w polach, spacje na brzegach, bardzo długie wartości.
- Dostępne w CLI i we Flasku.

**Weryfikacja ręczna**
- W pliku widać duplikaty opisane w `przypadek`.
- CSV z nietypowymi znakami nadal parsuje się poprawnie (import w Excelu).

**Commit:** `feat: duplikaty i nietypowe znaki`
**Ukończono:** —

---

## [ ] Etap 9 – Eksport TXT

**Zakres**
- `write_txt` – jeden rekord w linii, kolumny z `przypadek`.

**Weryfikacja ręczna**
- Plik czytelny w Notatniku dla każdego scenariusza.

**Commit:** `feat: eksport TXT`
**Ukończono:** —

---

## [ ] Etap 10 – Eksport VCF

**Zakres**
- `write_vcf` – wizytówka na osobę, `przypadek` w `NOTE`.

**Weryfikacja ręczna**
- Plik ze scenariusza `poprawne` importuje się do Outlooka lub kontaktów Google.

**Commit:** `feat: eksport VCF`
**Ukończono:** —

---

## [ ] Etap 11 – Eksport ICS

**Zakres**
- `write_ics` – wydarzenie „Urodziny: <imię> <nazwisko>” w dniu `data_urodzenia`, `przypadek` w `DESCRIPTION`.

**Weryfikacja ręczna**
- Plik ze scenariusza `poprawne` importuje się do kalendarza (Outlook / Google).

**Commit:** `feat: eksport ICS`
**Ukończono:** —
