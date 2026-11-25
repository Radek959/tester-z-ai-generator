# AGENTS.md

Instrukcje dla agentów AI pracujących w tym repozytorium.

## Cel projektu

Generator danych testowych dla testera, który nie programuje.
Dwa sposoby użycia: CLI w terminalu oraz prosty frontend we Flasku.
Oba korzystają z tej samej logiki.

## Zasady nadrzędne

- Python 3, uruchamiany z `.venv` w tym folderze (`.\.venv\Scripts\python.exe`).
- Tylko Windows. Ścieżki w kodzie zawsze przez `pathlib`.
- Maksymalnie biblioteka standardowa. Dozwolone zależności: Flask (frontend), Ruff (narzędzie deweloperskie).
  Nowej biblioteki nie dodawaj bez wyraźnej zgody użytkownika.
- Bez baz danych.
- Wygenerowane pliki trafiają wyłącznie do katalogu `output/`.
- Komunikaty dla użytkownika po polsku, zrozumiałe dla nieprogramisty, bez tracebacków.

## Rozwój

- Iteracyjnie, małymi etapami łatwymi do ręcznej weryfikacji.
- Plan etapów jest w `PLAN.md`. Rób tylko bieżący etap. Nie dodawaj funkcji z kolejnych etapów.
- Commit dopiero po potwierdzeniu etapu przez użytkownika.
- Po każdym wykonanym etapie oznacz go w `PLAN.md`: `[x]` przy nagłówku etapu
  i w tabeli „Postęp”, data i skrót commita w polu „Ukończono”.
  Zmiana `PLAN.md` wchodzi do commita danego etapu (lub, jeśli skrót commita
  nie jest jeszcze znany, do osobnego commita `docs: oznacz etap N w planie`).
- Wiadomości commitów: konwencja `typ: opis` (np. `feat: eksport CSV`).

## Architektura (docelowa)

- `testdata/service.py` – jedyny punkt wejścia do generowania: `generate_file(...)`.
  CLI (`testdata/__main__.py`) i Flask (`web/app.py`) tylko zbierają parametry i wołają service.
  Żadnej logiki generowania w warstwie CLI ani web.
- `testdata/generator.py` – poprawne rekordy.
- `testdata/scenarios.py` – modyfikacje rekordów według scenariusza.
- `testdata/writers.py` – zapis do formatów, rejestr `format -> funkcja`.
- `tests/` – testy jednostkowe (`unittest`).

## Model danych

Jedna stała encja `osoba` z polskimi danymi:
`imie`, `nazwisko`, `pesel`, `data_urodzenia`, `email`, `telefon`, `kod_pocztowy`, `miasto`.

- PESEL zgodny z datą urodzenia i płcią, z poprawną sumą kontrolną (w scenariuszu poprawnym).
- Każdy rekord ma pole `przypadek` z krótkim polskim opisem przypadku testowego
  (np. `poprawny`, `PESEL: błędna suma kontrolna`, `brak pola: email`).
  W VCF trafia do `NOTE`, w ICS do `DESCRIPTION`.
- W scenariuszu `brakujace_pole` pole `przypadek` zostaje, brakuje jednego pola danych.
- ICS: wydarzenie „Urodziny: <imię> <nazwisko>” w dniu `data_urodzenia`.

## Scenariusze

Jeden plik = jeden scenariusz.
MVP: `poprawne`, `graniczne`, `brakujace_pole`, `bledne`.
Później: duplikaty, nietypowe znaki.

## Formaty

MVP: JSON, CSV. Później: TXT, VCF, ICS.
CSV: UTF-8, separator `,` (nie dostosowujemy do polskiego Excela).

## Powtarzalność

Parametr `seed` – ten sam seed i parametry dają identyczną treść pliku.
Używaj instancji `random.Random(seed)`, nie globalnego `random`.

## Bramki jakości (od etapu 5)

Przed zgłoszeniem etapu jako gotowy:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m ruff check .
```

## Poza zakresem pierwszej wersji

Własne schematy, Faker, upload plików, historia generowań, konta, REST API,
Docker, CI, `.exe`, XML/XLSX/SQL, bardzo duże pliki, mieszanie scenariuszy w jednym pliku.
