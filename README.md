# Generator danych testowych

Generator danych testowych to narzędzie zbudowane podczas warsztatu **Tester z AI. Zbuduj własne narzędzie QA**.
Tworzy pliki z syntetycznymi polskimi danymi osobowymi do testów: poprawne rekordy, wartości graniczne,
brakujące pola, błędne wartości, duplikaty i nietypowe znaki.

Narzędzie jest przeznaczone dla testera, który nie programuje. Można z niego korzystać na dwa sposoby:

* przez prosty formularz w przeglądarce (Flask),
* przez wiersz poleceń (CLI).

Oba sposoby korzystają z tej samej logiki, więc ten sam seed i te same parametry dają identyczny plik.

> [!WARNING]
> Generator tworzy wyłącznie dane syntetyczne. Numery PESEL, adresy e-mail i telefony są losowe i mogą
> przypadkowo pokrywać się z prawdziwymi. Używaj ich tylko w środowiskach testowych.

Autor projektu: **Radosław Wasik**.

🤖 **Szukasz gotowych promptów do pracy testera z AI?**
Zajrzyj do darmowego [Prompt Hub dla testerów i QA](https://prompty.rwasik.pl/) — bazy promptów do analizy
wymagań, projektowania testów, testów eksploracyjnych, Playwrighta, code review, DevTools i nie tylko.

---

## Funkcje

* 🇵🇱 **Polskie dane osobowe** — imię, nazwisko, PESEL, data urodzenia, e-mail, telefon, kod pocztowy, miasto
* ✅ **Poprawny PESEL** — zgodny z datą urodzenia i płcią, z poprawną sumą kontrolną
* 🧪 **Scenariusze testowe** — każdy plik zawiera jeden scenariusz, a każdy rekord ma pole `przypadek` z opisem
* 📄 **Formaty JSON i CSV** — UTF-8, polskie znaki bez escape'owania, CSV z separatorem `,`
* 🔁 **Powtarzalność** — ten sam `seed` i parametry dają identyczną treść pliku, także innego dnia
* 📅 **Stała data odniesienia** — "dziś" w scenariuszach to domyślnie `2026-11-25`, niezależnie od zegara komputera
* 🖱️ **Formularz w przeglądarce** — uruchamiany dwuklikiem, bez znajomości terminala
* 💻 **CLI** — do szybkiego generowania i skryptów
* 💬 **Komunikaty po polsku** — zrozumiałe błędy, bez tracebacków

### Scenariusze

| Scenariusz | Co zawiera |
|---|---|
| `poprawne` | wszystkie dane poprawne |
| `graniczne` | poprawne wartości na granicach (np. imię z 1 znaku, 29 lutego) |
| `brakujace_pole` | w każdym rekordzie brakuje innego pola |
| `bledne` | w każdym rekordzie jedno pole ma błędną wartość |
| `duplikaty` | pełne kopie rekordów i powtórzone PESEL lub e-mail |
| `nietypowe_znaki` | emoji, cudzysłowy, przecinki, nowe linie, długie wartości |

---

## Technologie

* Python 3 (biblioteka standardowa)
* Flask (formularz w przeglądarce)
* `unittest` (testy jednostkowe)
* Ruff (lint)
* Skrypty `.bat` dla Windows

---

## Wymagania

* Windows,
* Python 3 dodany do PATH lub dostępny przez launcher `py` (projekt sprawdzono na Pythonie 3.15),
* połączenie z internetem do pobrania zależności przy pierwszym uruchomieniu.

---

## Pierwsze uruchomienie

1. Pobierz projekt: na GitHubie kliknij **Code → Download ZIP** i rozpakuj archiwum
   albo sklonuj repozytorium:

   ```powershell
   git clone https://github.com/Radek959/tester-z-ai-generator.git
   ```

2. Kliknij dwukrotnie **`setup.bat`**. Poczekaj na komunikat "Gotowe", a potem naciśnij dowolny klawisz,
   aby zamknąć okno. Skrypt przygotuje środowisko `.venv` i zainstaluje zależności.
   Wykonaj ten krok także po pobraniu aktualizacji projektu.
3. Kliknij dwukrotnie **`start_web.bat`**. Przeglądarka otworzy formularz pod adresem
   [http://127.0.0.1:5000](http://127.0.0.1:5000).
4. Wybierz format, scenariusz i liczbę rekordów. Pole **seed** możesz zostawić puste
   lub wpisać liczbę, aby móc powtórzyć te same dane.
5. Kliknij **Generuj**, a następnie **Pobierz plik**. Plik znajdziesz również w folderze `output/`.

Podczas pracy pozostaw okno uruchomione przez `start_web.bat` otwarte. Aby zakończyć, przejdź do tego okna
i naciśnij **Ctrl+C**. Samo zamknięcie karty przeglądarki nie zatrzymuje generatora.

### Gdy nie udaje się uruchomić

* **Nie znaleziono Pythona:** zainstaluj Python 3 z opcją dodania go do PATH lub z launcherem `py`,
  a potem ponownie uruchom `setup.bat`.
* **Błąd instalacji zależności:** sprawdź połączenie z internetem i uruchom `setup.bat` ponownie.
* **Brak `.venv` lub Flask:** uruchom `setup.bat`, a po jego powodzeniu `start_web.bat`.
* **Port 5000 jest zajęty:** zatrzymaj poprzedni generator przez Ctrl+C. Jeśli portu używa inny program,
  zamknij go i ponownie uruchom `start_web.bat`.
* **Przeglądarka nie otworzyła się:** pozostaw okno generatora otwarte i wpisz w przeglądarce
  [http://127.0.0.1:5000](http://127.0.0.1:5000).

Przy błędzie okno skryptu pozostaje otwarte do naciśnięcia klawisza, aby można było przeczytać komunikat.

---

## Użycie w terminalu (opcjonalnie)

Po wykonaniu `setup.bat` otwórz PowerShell w folderze projektu. Nie trzeba aktywować `.venv`.

```powershell
.\.venv\Scripts\python.exe -m testdata --format json --ilosc 10 --seed 42
```

```powershell
.\.venv\Scripts\python.exe -m testdata --format csv --scenariusz bledne --ilosc 20 --seed 42
```

```powershell
.\.venv\Scripts\python.exe -m testdata --help
```

Parametry:

* `--format` — `json` lub `csv` (domyślnie `json`),
* `--scenariusz` — nazwa scenariusza z tabeli wyżej (domyślnie `poprawne`),
* `--ilosc` — liczba rekordów (domyślnie 10),
* `--seed` — liczba; ten sam seed daje ten sam plik (domyślnie dane losowe),
* `--data-odniesienia` — data `RRRR-MM-DD` oznaczająca "dziś" w scenariuszach (domyślnie `2026-11-25`).

### Powtarzalność i data odniesienia

Ten sam seed, format, scenariusz, liczba rekordów i data odniesienia dają identyczną treść pliku.
Nazwy plików mogą się różnić, bo zawierają znacznik czasu. Bez seeda dane są losowe.

Opisy "dziś" i "w przyszłości" w scenariuszach odnoszą się do daty odniesienia. Aby ją zmienić:

```powershell
.\.venv\Scripts\python.exe -m testdata --scenariusz graniczne --ilosc 11 --seed 42 --data-odniesienia 2024-02-29
```

W Pythonie `service.generate_file(..., reference_date=date(2024, 2, 29))` przyjmuje datę typu
`datetime.date`. Pominięcie parametru wybiera stałą domyślną.

### Gdzie trafiają pliki

Wszystkie wygenerowane pliki trafiają do folderu `output/`. Ten folder nie jest zapisywany w repozytorium git.

---

## Bramki jakości

Dla osób rozwijających projekt. Po każdej zmianie w kodzie uruchom w PowerShell:

```powershell
.\check.bat
```

Skrypt uruchamia testy `unittest` oraz Ruff. Kod wyjścia `0` oznacza, że oba kroki przeszły.
Ruff w ustalonej wersji instaluje `setup.bat` z pliku `requirements-dev.txt`.

Testy używają małych zestawów danych i własnych katalogów tymczasowych wewnątrz `output/`.
Sprzątają po sobie także po porażce. Testy `setup.bat` i `start_web.bat` działają na osobnych kopiach
projektu i symulują instalację pakietów oraz otwieranie przeglądarki, więc nie wymagają sieci.

---

## Struktura projektu

* `testdata/service.py` — jedyny punkt wejścia do generowania: `generate_file(...)`
* `testdata/generator.py` — poprawne rekordy
* `testdata/scenarios.py` — modyfikacje rekordów według scenariusza
* `testdata/writers.py` — zapis do formatów
* `testdata/__main__.py` — CLI
* `web/` — formularz Flask
* `tests/` — testy jednostkowe
* [`PLAN.md`](./PLAN.md) — plan rozwoju etapami i postęp
* [`AGENTS.md`](./AGENTS.md) — instrukcje dla agentów AI pracujących w repozytorium

### Planowane

Kolejne formaty: TXT, VCF (wizytówki) i ICS (urodziny jako wydarzenia w kalendarzu).
Szczegóły w [`PLAN.md`](./PLAN.md).

---

## Więcej materiałów

### 🤖 Prompt Hub dla testerów i QA

Darmowa baza praktycznych promptów AI dla testerów i inżynierów QA, m.in. do:

* generowania przypadków testowych,
* testów eksploracyjnych,
* analizy wymagań,
* zakresu regresji,
* testowania opartego na ryzyku,
* Playwrighta,
* code review,
* analizy w DevTools.

[Prompt Hub dla testerów i QA →](https://prompty.rwasik.pl/)

### 📘 Playwright Starter Kit

Darmowy PDF z praktycznymi materiałami o Playwrighcie: komendy, lokatory, asercje, przykłady konfiguracji
i checklisty.

[Playwright Starter Kit →](https://starter.rwasik.pl/)

---

## O autorze

Projekt tworzy i rozwija **Radosław Wasik** — QA Tech Lead, w IT od 2018 roku. Prowadzi transformację działu QA
w kierunku AI: szkoli zespoły, wdraża autorskie rozwiązania AI wspierające testowanie i zarządza zespołami QA.
Specjalizuje się w testach automatycznych (Playwright, TypeScript) i praktycznym wykorzystaniu AI w pracy testera.

* 🌐 [rwasik.pl](https://rwasik.pl/)
* 💼 [LinkedIn](https://www.linkedin.com/in/rwasik/)
* 📸 [Instagram](https://instagram.com/radwasik)
* ✉️ [Newsletter](https://newsletter.rwasik.pl/)

---

## Wykorzystanie

Generator danych testowych jest przeznaczony do celów edukacyjnych, warsztatowych i do pracy z danymi testowymi.
