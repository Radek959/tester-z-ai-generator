@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 (
    echo Blad: nie mozna otworzyc folderu projektu.
    pause
    exit /b 1
)
set "TESTDATA_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%TESTDATA_PYTHON%" (
    echo Blad: brak srodowiska .venv. Uruchom najpierw setup.bat.
    goto blad
)
"%TESTDATA_PYTHON%" -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Blad: brak Flask lub Python w .venv nie dziala. Uruchom setup.bat.
    goto blad
)
"%TESTDATA_PYTHON%" -m web.launcher
if errorlevel 1 goto blad
popd
exit /b 0

:blad
popd
pause
exit /b 1
