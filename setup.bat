@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 (
    echo Blad: nie mozna otworzyc folderu projektu.
    pause
    exit /b 1
)
set "TESTDATA_PYTHON=%~dp0.venv\Scripts\python.exe"
if exist ".venv" goto sprawdz_srodowisko

echo Tworzenie srodowiska .venv...
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 goto utworz_przez_py
python -c "import sys" >nul 2>&1
if not errorlevel 1 goto utworz_przez_python
echo Blad: nie znaleziono Pythona 3. Zainstaluj Python 3 i uruchom setup.bat ponownie.
goto blad

:utworz_przez_py
py -3 -m venv .venv
if errorlevel 1 goto blad_tworzenia
goto sprawdz_srodowisko

:utworz_przez_python
python -m venv .venv
if errorlevel 1 goto blad_tworzenia

:sprawdz_srodowisko
if not exist "%TESTDATA_PYTHON%" (
    echo Blad: folder .venv jest niekompletny. Nie udalo sie znalezc interpretera.
    goto blad
)
"%TESTDATA_PYTHON%" -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo Blad: Python w .venv nie dziala. Sprawdz instalacje Pythona.
    goto blad
)
echo Instalowanie zaleznosci aplikacji i narzedzi do sprawdzania projektu...
"%TESTDATA_PYTHON%" -m pip install -r requirements.txt -r requirements-dev.txt
if errorlevel 1 (
    echo Blad: nie udalo sie zainstalowac zaleznosci. Sprawdz polaczenie z internetem i uruchom setup.bat ponownie.
    goto blad
)
echo Gotowe. Uruchom start_web.bat, aby otworzyc formularz.
popd
pause
exit /b 0

:blad_tworzenia
echo Blad: nie udalo sie utworzyc srodowiska .venv. Sprawdz instalacje Pythona i dostep do folderu projektu.
:blad
popd
pause
exit /b 1
