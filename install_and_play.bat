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
if %MAJOR% GTR 3 (
    echo ERREUR: Version de Python non supportée. Utilisez Python 3.11 ou inférieur.
    echo Version détectée : %PYVER%
    echo Téléchargez Python 3.11 ici : https://www.python.org/downloads/release/python-3110/
    del version.txt
    pause
    exit /b 1
)
if %MAJOR%==3 if %MINOR% GTR 11 (
    echo ERREUR: Version de Python non supportée. Utilisez Python 3.11 ou inférieur.
    echo Version détectée : %PYVER%
    echo Téléchargez Python 3.11 ici : https://www.python.org/downloads/release/python-3110/
    del version.txt
    pause
    exit /b 1
)
del version.txt
echo.

REM Installation des dépendances
echo Installation des dépendances...
REM Mise à jour de pip et installation de setuptools/distutils
python -m pip install --upgrade pip
python -m pip install --user setuptools
python -m pip install --user distutils
python -m pip install --user pygame==2.5.2 numpy==1.24.3
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