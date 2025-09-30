@echo off
chcp 65001 >nul

echo ============================================
echo    COSMIC DEFENDER - INSTALLATION COMPLÈTE
echo ============================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Téléchargez Python depuis https://python.org
    pause
    exit /b 1
)

echo ✅ Python détecté avec succès !
echo.

echo Installation des dépendances (y compris GitHub)...
pip install pygame==2.5.2 numpy==1.24.3 requests>=2.25.0

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo.
echo ✅ Installation terminée avec succès !
echo.
echo 🎮 Fonctionnalités installées :
echo   • Jeu Cosmic Defender complet
echo   • Mode Campagne et Infini
echo   • Leaderboard local et web
echo   • Upload automatique GitHub
echo.
echo ============================================
echo      LANCEMENT DE COSMIC DEFENDER
echo ============================================
echo.

echo Lancement du jeu...
python cosmic_defender.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Le jeu s'est fermé avec une erreur.
    echo.
) else (
    echo.
    echo ✅ Jeu terminé normalement.
    echo.
)

echo Merci d'avoir joué à Cosmic Defender !
echo.
echo 🌐 Pour configurer l'upload automatique :
echo   1. Lancez le jeu
echo   2. Cliquez sur "GITHUB SETUP"
echo   3. Suivez le guide GUIDE_AUTO_UPLOAD.md
echo.
pause