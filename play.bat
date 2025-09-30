@echo off
title Cosmic Defender
color 0A

echo.
echo ============================================
echo         COSMIC DEFENDER
echo    Défendez la Terre contre l'invasion !
echo ============================================
echo.

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé
    echo Utilisez "install_and_play.bat" pour installer
    echo.
    pause
    exit /b 1
)

REM Lancement du jeu
python cosmic_defender.py

echo.
echo Merci d'avoir joué !
pause