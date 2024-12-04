@echo off
echo Installation de Bot Manager Pro...

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe. Veuillez installer Python 3.8 ou superieur.
    pause
    exit /b 1
)

REM Mettre a jour pip
python -m pip install --upgrade pip

REM Installer les dependances avec pip
python -m pip install --user -r requirements.txt

REM Installer Playwright et ses navigateurs
python -m playwright install chromium

echo Installation terminee !
pause