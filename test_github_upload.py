#!/usr/bin/env python3
"""
Script de test pour l'upload automatique GitHub
"""

import json
from datetime import datetime
from cosmic_defender import GitHubUploader

def test_github_integration():
    """Test de l'intégration GitHub"""
    print("Test de l'upload automatique GitHub")
    print("=" * 50)

    # Créer un uploader
    uploader = GitHubUploader()

    # Afficher la configuration actuelle
    print("Configuration actuelle:")
    config = uploader.config
    print(f"  Username: {config.get('username', 'Non configuré')}")
    print(f"  Repository: {config.get('repository', 'Non configuré')}")
    print(f"  Token: {'*' * 20 if config.get('token') else 'Non configuré'}")
    print(f"  Auto-upload: {config.get('auto_upload', False)}")
    print(f"  Configuré: {config.get('configured', False)}")

    # Test de connexion
    print("\nTest de connexion...")
    if uploader.is_configured():
        success, message = uploader.test_connection()
        if success:
            print(f"[OK] {message}")
        else:
            print(f"[ERROR] {message}")
            return False
    else:
        print("[ERROR] Configuration incomplete")
        return False

    # Test d'upload avec des données fictives
    print("\nTest d'upload avec donnees fictives...")
    test_data = {
        "last_updated": datetime.now().isoformat(),
        "total_scores": 5,
        "scores": [
            {
                "player_id": "test-player-123",
                "name": "TEST_PLAYER",
                "score": 9999,
                "wave": 15,
                "mode": "infinite",
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        ]
    }

    success, message = uploader.upload_leaderboard(test_data)
    if success:
        print(f"[OK] {message}")
        print("Verifiez votre site web pour voir les donnees de test!")
    else:
        print(f"[ERROR] {message}")

    return success

if __name__ == "__main__":
    test_github_integration()