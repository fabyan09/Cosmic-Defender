@echo off
chcp 65001 >nul
title COSMIC DEFENDER

echo ========================================
echo     COSMIC DEFENDER
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python non installe
    echo.
    pause
    exit /b 1
)

echo Lancement du jeu...
python cosmic_defender.py

echo.
echo Merci d'avoir joue !
pause