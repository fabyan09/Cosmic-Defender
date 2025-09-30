import subprocess
import sys
import os

def install_requirements():
    """Installe automatiquement les dépendances requises."""
    print("🚀 Cosmic Defender - Installation automatique des dépendances...")

    requirements = ["pygame==2.5.2", "numpy==1.24.3"]

    for package in requirements:
        print(f"Installation de {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            print(f"✓ {package} installé avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {package}: {e}")
            return False

    print("✅ Toutes les dépendances sont installées !")
    return True

def check_dependencies():
    """Vérifie si les dépendances sont installées."""
    try:
        import pygame
        import numpy
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("COSMIC DEFENDER")
    print("Defendez la Terre contre l'invasion spatiale !")
    print("=" * 50)
    print()

    # Vérifier et installer les dépendances si nécessaire
    if not check_dependencies():
        print("Installation des dependances requises...")
        if not install_requirements():
            print("ERREUR: Impossible d'installer les dependances. Verifiez votre connexion internet.")
            input("Appuyez sur Entree pour quitter...")
            sys.exit(1)
        print()

    print("Lancement du jeu...")
    print("Controles : WASD pour bouger, Espace pour tirer")
    print("Objectif : Survivez a 10 vagues d'ennemis !")
    print()

    # Importer et lancer le jeu
    try:
        # Code du jeu intégré
        exec(open('cosmic_defender.py').read())
    except FileNotFoundError:
        print("ERREUR: Fichier cosmic_defender.py introuvable !")
        input("Appuyez sur Entree pour quitter...")
    except Exception as e:
        print(f"ERREUR lors du lancement du jeu : {e}")
        input("Appuyez sur Entree pour quitter...")