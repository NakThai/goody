@echo off
echo Demarrage de Bot Manager Pro...

REM Verifier si les dependances sont installees
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances manquantes...
    call install.bat
)

REM Ajouter le repertoire src au PYTHONPATH et le repertoire courant
set PYTHONPATH=%~dp0src;%~dp0
cd %~dp0src

REM Lancer l'application
python main.py
pause