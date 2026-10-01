@echo off
chcp 65001 >nul
title Image Studio — Compilation EXE
cd /d "%~dp0"

echo.
echo ==============================================
echo   IMAGE STUDIO — Compilation EXE
echo ==============================================
echo.

:: Choix de Python : 3.14.7 de préférence (Tk stable), sinon celui par défaut
set "PYEXE=python"
py -3.14.7 --version >nul 2>&1 && set "PYEXE=py -3.14.7"
if "%PYEXE%"=="python" (
    py -3.14.7 --version >nul 2>&1 && set "PYEXE=py -3.14.7"
)
%PYEXE% --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python introuvable.
    echo Installe Python depuis https://python.org
    pause & exit /b 1
)
echo Python utilise : 
%PYEXE% --version

:: Vérifie les fichiers indispensables
for %%F in (main.py app.py sidebar.py menu.py filters.py upscaler.py theme.py settings.py preferences.py) do (
    if not exist "%%F" (
        echo [ERREUR] Fichier manquant : %%F
        pause & exit /b 1
    )
)
if not exist "assets\icon - visible.ico" (
    echo [ERREUR] assets\icon - visible.ico introuvable : le logo ne pourra pas etre integre.
    pause & exit /b 1
)

echo.
echo [1/4] Environnement virtuel de compilation...
if not exist ".venv_build\Scripts\python.exe" (
    ::%PYEXE% -m venv .venv_build
    if errorlevel 1 (
        echo [ERREUR] Creation de l'environnement virtuel impossible.
        pause & exit /b 1
    )
)
set "VPY=.venv_build\Scripts\python.exe"

echo [2/4] Installation des dependances (environnement propre)...
:: "%VPY%" -m pip install --upgrade pip --quiet
:: "%VPY%" -m pip install customtkinter Pillow numpy pyinstaller pyinstaller-hooks-contrib --quiet
if errorlevel 1 (
    echo [ERREUR] Installation échouée.
    pause & exit /b 1
)

echo [3/4] Compilation en cours...

:: Dossier models optionnel (Real-ESRGAN) : inclus seulement s'il existe
set "EXTRA="
if exist "models" set "EXTRA=--add-data models;models"

"%VPY%" -m PyInstaller main.py ^
    --name ImageStudio ^
    --noconfirm --clean ^
    --windowed ^
    --icon "assets\icon - visible.ico" ^
    --add-data "assets;assets" ^
    %EXTRA% ^
    --collect-all customtkinter

if errorlevel 1 (
    echo [ERREUR] La compilation a échoué.
    echo Lis les messages ci-dessus pour identifier le problème.
    pause & exit /b 1
)

echo.
echo [4/4] Terminé !
echo.
echo  Ton exe est ici :
echo  dist\ImageStudio\ImageStudio.exe
echo.
echo  (Les préférences sont enregistrées dans %%APPDATA%%\ImageStudio\settings.json)
echo.
explorer dist\ImageStudio
pause