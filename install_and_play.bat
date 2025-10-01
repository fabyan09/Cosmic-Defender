@echo off
title Cosmic Defender - Installation et Lancement
color 0A

echo.
echo ============================================
echo    COSMIC DEFENDER - INSTALLATION
echo ============================================
echo.

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python depuis https://python.org
    echo.
    pause
    exit /b 1
)

echo Python détecté avec succès !
REM Vérification de la version de Python
python --version >version.txt 2>&1
set /p PYVER=<version.txt
for /f "tokens=2 delims=. " %%i in ("%PYVER%") do set MAJOR=%%i
for /f "tokens=3 delims=. " %%i in ("%PYVER%") do set MINOR=%%i
if %MAJOR% LSS 3 (
    echo ERREUR: Version de Python trop ancienne. Utilisez Python 3.8 ou supérieur.
    echo Version détectée : %PYVER%
    echo Téléchargez Python ici : https://www.python.org/downloads/
    del version.txt
    pause
    exit /b 1
)
if %MAJOR%==3 if %MINOR% LSS 8 (
    echo ERREUR: Version de Python trop ancienne. Utilisez Python 3.8 ou supérieur.
    echo Version détectée : %PYVER%
    echo Téléchargez Python ici : https://www.python.org/downloads/
    del version.txt
    pause
    exit /b 1
)
del version.txt
echo Version Python : %PYVER%
echo.

REM Installation des dépendances
echo Installation des dépendances...
REM Mise à jour de pip et installation depuis requirements.txt
python -m pip install --upgrade pip
python -m pip install --user -r requirements.txt
if errorlevel 1 (
    echo ERREUR lors de l'installation des dépendances
    pause
    exit /b 1
)

echo.
echo Installation terminée avec succès !
echo.
echo ============================================
echo       LANCEMENT DE COSMIC DEFENDER
echo ============================================
echo.
echo Lancement du jeu...
python cosmic_defender.py

if errorlevel 1 (
    echo.
    echo Le jeu s'est fermé avec une erreur.
    echo.
)

echo.
echo Merci d'avoir joué à Cosmic Defender !
echo.
pause