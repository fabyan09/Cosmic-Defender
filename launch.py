#!/usr/bin/env python3
"""
Cosmic Defender - Launcher Script
Script de lancement sécurisé pour Cosmic Defender
"""

import sys
import os

def main():
    try:
        # Ajouter le répertoire du jeu au path
        game_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, game_dir)

        # Changer vers le répertoire du jeu
        os.chdir(game_dir)

        # Importer et lancer le jeu
        from cosmic_defender import CosmicDefender

        print("=" * 44)
        print("   LANCEMENT DE COSMIC DEFENDER")
        print("=" * 44)
        print()
        print("Initialisation...")

        game = CosmicDefender()

        print("Jeu prêt ! Utilisez F11 pour le plein écran.")
        print("Amusez-vous bien ! 🚀")
        print()

        game.run()

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous que pygame est installé: pip install pygame")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        print("\nMerci d'avoir joué à Cosmic Defender ! 🌌")

if __name__ == "__main__":
    main()