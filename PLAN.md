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
| 4 | Scenariusze testowe | [x] |
| 5 | Bramki jakości | [x] |
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
**Ukończono:** 2026-11-25, `15080e1`

---

## [x] Etap 4 – Scenariusze testowe

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
**Ukończono:** 2026-11-25, `a7ecbcb`

---

## [x] Etap 5 – Bramki jakości

**Zakres**
- Testy jednostkowe i integracyjne (`unittest`) w `tests/`, obejmujące zachowanie dostępne po etapach 0–4.
- Generator:
  - liczba rekordów, komplet wymaganych pól i `przypadek = poprawny`,
  - PESEL: 11 cyfr, suma kontrolna, zgodność z datą urodzenia i płcią; jawne przypadki dla obu płci, dat 1999-12-31 i 2000-01-01 oraz 29 lutego,
  - sprawdzanie PESEL niezależnie od produkcyjnej funkcji liczącej cyfrę kontrolną, z ustalonymi przykładami oczekiwanych wyników,
  - identyczne dane dla tego samego seeda, różne dla wybranych różnych seedów oraz brak wpływu na globalny stan `random`.
- Scenariusze:
  - każdy obecny przypadek graniczny i błędny sprawdzony pod kątem rzeczywistej wartości oraz zgodności opisu w `przypadek`,
  - `brakujace_pole`: brak dokładnie jednego pola danych, kolejne pola usuwane cyklicznie, `przypadek` pozostaje,
  - `poprawne` daje te same dane co generator dla tej samej liczby rekordów i seeda,
  - testy obejmują pełny cykl przypadków i początek kolejnego; daty odniesienia są ustalone, bez zależności od dnia uruchomienia.
- Writery:
  - ponowny odczyt przez `json` i `csv` oraz porównanie zapisanych danych, w tym polskich znaków i pola `przypadek`,
  - JSON: UTF-8, czytelne wcięcia, polskie znaki bez escape'owania, brak usuniętego klucza,
  - CSV: UTF-8, separator `,`, stała kolejność nagłówków, brakujące pole jako pusta komórka bez przesuwania pozostałych kolumn.
- `service.generate_file`:
  - wszystkie 4 scenariusze × 2 formaty: poprawna liczba rekordów, zwrócona ścieżka i zawartość pliku,
  - pliki wyłącznie w `output/`, poprawne rozszerzenie oraz brak nadpisania wcześniejszego pliku przy tym samym znaczniku czasu,
  - nieznany format i scenariusz, ilość 0, ujemna i ponad limit: polski komunikat błędu oraz brak utworzonego pliku,
  - powtarzalność treści pliku (porównanie bajtów, bez wymagania identycznych nazw plików).
- CLI: pomoc i poprawne wywołanie kończą się kodem 0; błędne argumenty oraz symulowany błąd zapisu dają niezerowy kod i polski komunikat bez tracebacku.
- Izolacja testów: małe zestawy danych, niezależność od kolejności wykonania, pliki w osobnych katalogach tymczasowych wewnątrz `output/`; sprzątanie także po porażce, bez usuwania istniejących plików użytkownika. Ścieżki przez `pathlib`, symulowanie błędów przez `unittest.mock`.
- Powtarzalność a bieżąca data — warunek do rozstrzygnięcia przed zamknięciem etapu:
  - obecne przypadki „dziś” i „w przyszłości” zależą od `date.today()`, a `AGENTS.md` i `service` deklarują identyczną treść dla tego samego seeda i parametrów,
  - ustalić i zapisać spójny kontrakt; ewentualne zawężenie wymagania z `AGENTS.md` wymaga uzgodnienia z użytkownikiem,
  - testy z ustaloną datą sprawdzają deterministyczność, ale nie mogą być uznane za rozwiązanie tej rozbieżności; dodać test zachowania dla dwóch różnych dat odniesienia zgodnie z przyjętym kontraktem.
- `pyproject.toml` z jawnym zestawem reguł Ruff: `E4`, `E7`, `E9`, `F`, `I`; wersja docelowa Pythona zgodna z używaną w projekcie. `requirements-dev.txt` z ustaloną dokładną wersją Ruff.
- Krótka instrukcja w README: instalacja zależności deweloperskich przez interpreter z `.venv`, uruchomienie bramek i znaczenie kodów wyjścia.
- `check.bat` w katalogu głównym – jedno polecenie uruchamiające testy i Ruff:
  - woła `.\.venv\Scripts\python.exe` wprost (bez aktywacji `.venv`), ustawia katalog roboczy względem pliku (`%~dp0`), ujmuje ścieżki w cudzysłowy i przywraca katalog wywołującego,
  - uruchamia `-m unittest discover -s tests` i `-m ruff check .`, także gdy testy zawiodą; zapamiętuje wynik każdego kroku i na końcu podaje polskie podsumowanie,
  - brak wykrytych testów oznacza porażkę, nawet jeśli samo `unittest` zgłosi sukces,
  - brak interpretera lub Ruff daje czytelny komunikat i kod 1; przy braku Ruff testy nadal się wykonują,
  - kończy się `exit /b 0`, gdy wszystko przeszło, i `exit /b 1` w przeciwnym razie,
  - nie ma `pause` ani innych pytań (agent uruchamia go nieinteraktywnie).

**Weryfikacja ręczna**
- Po instalacji zależności `.\check.bat; $LASTEXITCODE` uruchamia niezerową liczbę testów, oba kroki przechodzą i końcowy kod wynosi `0`.
- Wywołanie skryptu z innego katalogu działa również przy ścieżce projektu ze spacjami; po zakończeniu katalog wywołującego pozostaje bez zmian.
- Celowo zepsuta suma PESEL powoduje porażkę odpowiedniego testu i końcowy kod `1`; Ruff nadal się wykonuje, a jego sukces nie nadpisuje błędu testów.
- Celowy błąd Ruff (np. nieużywany import) daje końcowy kod `1`, przy wykonanych testach.
- Brak wykrytych testów, brak Ruff i brak interpretera sprawdzone osobno, w izolacji lub przez symulację, bez usuwania właściwej `.venv` ani testów: każdy przypadek daje kod `1` i zrozumiałe podsumowanie.
- Testy nie pozostawiają plików ani nie zmieniają istniejącej zawartości `output/`, również po celowej porażce testu zapisującego plik.
- Kontrakt powtarzalności jest rozstrzygnięty i udokumentowany, a test dla dwóch dat odniesienia potwierdza przyjęte zachowanie.
- Po cofnięciu wszystkich celowych usterek ponowne `.\check.bat` kończy się kodem `0`; dopiero wtedy etap jest gotowy do ręcznego odbioru.

**Commit:** `test: testy jednostkowe i Ruff`
**Ukończono:** 2026-11-25, skrót commita do uzupełnienia po potwierdzeniu etapu przez użytkownika.

**Przyjęty kontrakt powtarzalności:** uzgodniona z użytkownikiem stała domyślna
data odniesienia `2026-11-25`; opcjonalnie `--data-odniesienia RRRR-MM-DD` w CLI,
`reference_date` w service i `dzis` w scenariuszach. Ten sam podany seed
i parametry dają identyczną treść niezależnie od zegara. Kontrakt opisano
w `AGENTS.md` i README oraz sprawdzono dla dwóch dat odniesienia i dwóch
symulowanych dni uruchomienia.

**Wynik weryfikacji:** 37 testów `unittest` i Ruff 0.17.6 przechodzą;
`check.bat` kończy się kodem `0`. W izolowanych kopiach sprawdzono kod `1`
dla zepsutej sumy PESEL, nieużywanego importu, braku testów, Ruff i interpretera.
Ruff wykonuje się także po porażce testów. Potwierdzono wywołanie z innego
katalogu przy ścieżkach ze spacjami i przywrócenie katalogu wywołującego,
sprzątanie po celowej porażce testu zapisującego plik oraz zachowanie
istniejącej zawartości `output/`. Po usunięciu celowych usterek kopia ponownie
przeszła bramki. Commit czeka na odbiór użytkownika.

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
