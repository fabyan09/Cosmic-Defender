#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuration du token GitHub pour Cosmic Defender
A executer UNIQUEMENT par le proprietaire du repository
"""

import sys
import os
import re


def main():
    print()
    print("=" * 70)
    print(" Configuration du token GitHub - Cosmic Defender")
    print("=" * 70)
    print()
    print("ATTENTION: Ce script est pour le proprietaire du repo uniquement!")
    print()
    print("Le token sera chiffre et embarque dans le code pour permettre")
    print("l'upload automatique des scores.")
    print()

    # Verifier que cryptography est installe
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("ERREUR: Le module 'cryptography' n'est pas installe.")
        print()
        print("Installation requise:")
        print("  pip install cryptography")
        print()
        return 1

    # Importer le module secure_token
    try:
        from secure_token import SecureToken
    except ImportError:
        print("ERREUR: Impossible d'importer secure_token.py")
        print("   Verifiez que le fichier existe dans le meme dossier.")
        return 1

    print("Etape 1/3 - Token GitHub")
    print("-" * 70)
    print("Creez un token sur: https://github.com/settings/tokens")
    print("Permissions requises: 'repo' (Full control)")
    print()
    token = input("Entrez votre token GitHub (ghp_...): ").strip()

    if not token:
        print("ERREUR: Token vide, annulation.")
        return 1

    if not token.startswith("ghp_") and not token.startswith("github_pat_"):
        print("ATTENTION: le token ne commence pas par 'ghp_' ou 'github_pat_'")
        confirm = input("Continuer quand meme? (o/N): ").lower()
        if confirm != 'o':
            print("Annule.")
            return 1

    print()
    print("Etape 2/3 - Mot de passe de chiffrement")
    print("-" * 70)
    print("Choisissez un mot de passe pour chiffrer le token.")
    print()
    print("IMPORTANT:")
    print("  - Ce mot de passe sera embarque dans le code")
    print("  - Il protege contre une lecture directe du token")
    print("  - Beaucoup plus sur que du base64!")
    print()
    password = input("Mot de passe (min 8 caracteres): ").strip()

    if not password or len(password) < 8:
        print("ERREUR: Mot de passe trop court (minimum 8 caracteres).")
        return 1

    print()
    print("Etape 3/3 - Chiffrement et integration")
    print("-" * 70)

    # Chiffrer le token
    st = SecureToken()
    try:
        encrypted = st.encrypt_token(token, password)
    except Exception as e:
        print(f"ERREUR lors du chiffrement: {e}")
        return 1

    # Verifier que le dechiffrement fonctionne
    decrypted = st.decrypt_token(encrypted, password)
    if decrypted != token:
        print("ERREUR: echec de la verification du chiffrement")
        return 1

    print("OK: Token chiffre avec succes!")
    print()

    # Modifier secure_token.py
    secure_token_file = "secure_token.py"
    if not os.path.exists(secure_token_file):
        print(f"ERREUR: {secure_token_file} introuvable")
        return 1

    try:
        with open(secure_token_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remplacer les placeholders
        content = re.sub(
            r'ENCRYPTED_TOKEN = "__ENCRYPTED_TOKEN__"',
            f'ENCRYPTED_TOKEN = "{encrypted}"',
            content
        )
        content = re.sub(
            r'PASSWORD = "__PASSWORD__"',
            f'PASSWORD = "{password}"',
            content
        )

        # Ecrire le fichier modifie
        with open(secure_token_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"OK: Fichier {secure_token_file} mis a jour!")
        print()

    except Exception as e:
        print(f"ERREUR lors de la modification du fichier: {e}")
        return 1

    # Test final
    print("Test de configuration...")
    st_test = SecureToken()
    test_token = st_test.get_embedded_token()

    if test_token == token:
        print("OK: Test reussi! Le token est correctement configure.")
        print()
        print("=" * 70)
        print(" Configuration terminee avec succes!")
        print("=" * 70)
        print()
        print("Prochaines etapes:")
        print()
        print("1. Testez le jeu:")
        print("   python cosmic_defender.py")
        print()
        print("2. Jouez et sauvegardez un score")
        print("   -> Il sera automatiquement uploade sur GitHub!")
        print()
        print("3. Committez les changements:")
        print("   git add secure_token.py")
        print("   git commit -m 'Configure GitHub token'")
        print("   git push")
        print()
        print("IMPORTANT:")
        print("   - secure_token.py contient le token chiffre")
        print("   - C'est securise de le committer sur GitHub")
        print("   - NE COMMITTEZ PAS config_token.py")
        print()
        print("Les joueurs n'auront rien a configurer!")
        print()
        return 0
    else:
        print("ERREUR: le test de recuperation du token a echoue")
        print("   Verifiez la configuration manuellement.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAnnule par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERREUR inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
