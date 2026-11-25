@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 (
    echo Blad: nie mozna otworzyc folderu projektu.
    exit /b 1
)
set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo Blad: brak interpretera .venv\Scripts\python.exe. Utworz srodowisko .venv.
    popd
    exit /b 1
)

echo Sprawdzanie liczby testow...
"%PYTHON%" -c "import sys, unittest; n = unittest.defaultTestLoader.discover('tests').countTestCases(); print('Wykryte testy:', n); sys.exit(0 if n else 1)"
set "DISCOVERY_RESULT=%ERRORLEVEL%"
echo Uruchamianie testow...
"%PYTHON%" -m unittest discover -s tests
set "TEST_RESULT=%ERRORLEVEL%"

echo Uruchamianie Ruff...
"%PYTHON%" -m ruff check .
set "RUFF_RESULT=%ERRORLEVEL%"

set "RESULT=0"
if not "%DISCOVERY_RESULT%"=="0" (
    echo Testy: blad wykrywania lub brak testow.
    set "RESULT=1"
)
if not "%TEST_RESULT%"=="0" (
    echo Testy: blad.
    set "RESULT=1"
)
if "%DISCOVERY_RESULT%"=="0" if "%TEST_RESULT%"=="0" echo Testy: OK.
if not "%RUFF_RESULT%"=="0" (
    echo Ruff: blad lub brak narzedzia. Instalacja: .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    set "RESULT=1"
)
if "%RUFF_RESULT%"=="0" echo Ruff: OK.
if "%RESULT%"=="0" echo Bramki jakosci: OK.
if not "%RESULT%"=="0" echo Bramki jakosci: niepowodzenie.
popd
exit /b %RESULT%
