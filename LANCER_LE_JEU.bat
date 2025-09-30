@echo off
title 🚀 COSMIC DEFENDER 🚀
color 0A
mode con: cols=80 lines=25

echo.
echo ████████████████████████████████████████████████████████████████████████████
echo ██                                                                        ██
echo ██  🚀 🛸 🌌    C O S M I C   D E F E N D E R    🌌 🛸 🚀              ██
echo ██                                                                        ██
echo ██           Défendez la Terre contre l'invasion spatiale !               ██
echo ██                                                                        ██
echo ████████████████████████████████████████████████████████████████████████████
echo.
echo 🎮 CONTROLES:
echo    WASD ou Flèches : Déplacer le vaisseau
echo    Espace ou Clic  : Tirer
echo    ESC             : Retour au menu
echo.
echo 🎯 OBJECTIF:
echo    Survivez à 10 vagues d'ennemis cosmiques pour sauver la Terre !
echo.
echo 💫 POWER-UPS:
echo    🔶 Orange : Tir rapide    🔵 Cyan : Bouclier
echo    🟢 Vert   : Multi-tir     🟣 Violet : Laser
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python n'est pas installé sur ce système.
    echo.
    echo 💡 SOLUTION: Installez Python depuis https://python.org
    echo    ⚠️  N'oubliez pas de cocher "Add Python to PATH" !
    echo.
    pause
    exit /b 1
)

echo ✅ Python détecté !
echo 🚀 Lancement de Cosmic Defender...
echo.

python cosmic_defender_standalone.py

if errorlevel 1 (
    echo.
    echo ❌ Le jeu s'est fermé de manière inattendue.
    echo 💡 Vérifiez que tous les fichiers sont présents.
)

echo.
echo 🌟 Merci d'avoir joué à Cosmic Defender !
echo 👋 À bientôt, Commandant !
echo.
timeout /t 3 >nul