#!/usr/bin/env python3
"""
Script pour déployer le leaderboard de Cosmic Defender sur GitHub Pages
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

def copy_web_files():
    """Copie les fichiers web vers le répertoire de déploiement"""
    web_dir = "web"
    deploy_dir = "leaderboard_deploy"

    # Créer le répertoire de déploiement
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)

    # Copier les fichiers web
    if os.path.exists(web_dir):
        for file in os.listdir(web_dir):
            if file.endswith(('.html', '.css', '.js')):
                shutil.copy2(os.path.join(web_dir, file), deploy_dir)
                print(f"[OK] Copie: {file}")

    # Copier le fichier de scores s'il existe
    if os.path.exists("cosmic_defender_leaderboard.json"):
        shutil.copy2("cosmic_defender_leaderboard.json", deploy_dir)
        print("[OK] Copie: cosmic_defender_leaderboard.json")
    else:
        # Créer un fichier de démonstration
        demo_data = {
            "last_updated": datetime.now().isoformat(),
            "total_scores": 0,
            "scores": []
        }
        with open(os.path.join(deploy_dir, "cosmic_defender_leaderboard.json"), 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2)
        print("[OK] Cree: fichier de demonstration cosmic_defender_leaderboard.json")

    return deploy_dir

def create_readme(deploy_dir):
    """Crée un README pour le leaderboard"""
    readme_content = """# 🚀 Cosmic Defender - Leaderboard

Leaderboard en temps réel pour le jeu Cosmic Defender.

## 🎮 À propos du jeu

Cosmic Defender est un jeu de tir spatial avec deux modes :
- **Mode Campagne** : Survivez à 10 vagues d'ennemis
- **Mode Infini** : Affrontez des vagues infinies avec des Giga Boss toutes les 10 vagues

## 📊 Leaderboard

Le leaderboard affiche :
- Les meilleurs scores de tous les joueurs
- Filtrage par mode de jeu (Campagne/Infini)
- Statistiques globales
- Historique des performances

## 🔄 Mise à jour automatique

Les scores sont automatiquement exportés depuis le jeu et peuvent être mis à jour sur cette page.

## 📥 Télécharger le jeu

[Télécharger Cosmic Defender](https://github.com/fabyan09/Cosmic-Defender)

---

*Dernière mise à jour : {}*
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open(os.path.join(deploy_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("[OK] Cree: README.md")

def create_github_workflow(deploy_dir):
    """Crée un workflow GitHub Actions pour le déploiement automatique"""
    workflow_dir = os.path.join(deploy_dir, ".github", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)

    workflow_content = """name: Deploy Cosmic Defender Leaderboard

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Pages
        uses: actions/configure-pages@v3

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: '.'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v1
"""

    with open(os.path.join(workflow_dir, "deploy.yml"), 'w') as f:
        f.write(workflow_content)
    print("[OK] Cree: workflow GitHub Actions")

def main():
    print("Deploiement du leaderboard Cosmic Defender")
    print("=" * 50)

    try:
        # Copier les fichiers
        deploy_dir = copy_web_files()

        # Créer les fichiers additionnels
        create_readme(deploy_dir)
        create_github_workflow(deploy_dir)

        print("\nDeploiement prepare avec succes!")
        print(f"Fichiers prets dans: {deploy_dir}/")
        print("\nProchaines etapes:")
        print("1. Creez un nouveau repository GitHub (ex: cosmic-defender-leaderboard)")
        print("2. Activez GitHub Pages dans les parametres du repository")
        print("3. Uploadez le contenu du dossier leaderboard_deploy/")
        print("4. Votre leaderboard sera accessible a l'adresse:")
        print("   https://fabyan09.github.io/cosmic-defender-leaderboard/")

        print("\nPour mettre a jour les scores:")
        print("- Jouez a Cosmic Defender et sauvegardez vos scores")
        print("- Le fichier cosmic_defender_leaderboard.json sera mis a jour")
        print("- Uploadez ce fichier sur votre repository GitHub")

    except Exception as e:
        print(f"Erreur lors du deploiement: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())