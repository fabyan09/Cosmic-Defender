"""
Module de chiffrement sécurisé pour le token GitHub
Utilise Fernet (cryptographie symétrique) pour protéger le token
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureToken:
    """Gestion sécurisée du token GitHub avec chiffrement Fernet"""

    def __init__(self):
        # Clé de chiffrement dérivée d'un mot de passe
        # Cette clé sera embarquée dans le code pour que le jeu fonctionne automatiquement
        self.encryption_key = None
        self.salt = b'cosmic_defender_salt_2025'  # Salt public (OK pour ce use case)

    def _derive_key(self, password: str) -> bytes:
        """Dérive une clé de chiffrement depuis un mot de passe"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_token(self, token: str, password: str) -> str:
        """Chiffre le token avec un mot de passe"""
        key = self._derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_token(self, encrypted_token: str, password: str) -> str:
        """Déchiffre le token avec le mot de passe"""
        try:
            key = self._derive_key(password)
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            print(f"Erreur de déchiffrement: {e}")
            return None

    def get_embedded_token(self) -> str:
        """
        Récupère le token déchiffré depuis le token embarqué dans le code
        Cette fonction sera appelée automatiquement par le jeu
        """
        # Token chiffré et mot de passe embarqués (à configurer via setup)
        ENCRYPTED_TOKEN = "Z0FBQUFBQm8zUllWazhtSVAxdkRNclZNWkFLM05rOENxQVU0c1diRngzRm9COEViV0pJNW5BTDJGQzBXZ0d6T3lIaFB1dlctdHZ3emU0QW41LUlnUTVXeWx2X1dXV19mNnBGSjRWTjVHSDFuMUpBUnowWWh3RzREMllFQnd3WVRHMU91RzJUTmRWbFA="
        PASSWORD = "ls72iw78&*F09"

        if ENCRYPTED_TOKEN == "__ENCRYPTED_TOKEN__":
            # Pas encore configuré
            return None

        return self.decrypt_token(ENCRYPTED_TOKEN, PASSWORD)


def setup_token():
    """
    Script interactif pour configurer le token
    À exécuter UNIQUEMENT par le propriétaire du repo
    """
    print("=" * 60)
    print("Configuration sécurisée du token GitHub")
    print("=" * 60)
    print()
    print("Ce script va chiffrer votre token GitHub pour l'embarquer")
    print("dans le code de façon sécurisée.")
    print()

    # Demander le token
    token = input("Entrez votre token GitHub: ").strip()
    if not token:
        print("Token vide, annulation.")
        return

    # Demander un mot de passe
    print()
    print("Choisissez un mot de passe pour chiffrer le token.")
    print("⚠️  Ce mot de passe sera embarqué dans le code.")
    print("⚠️  L'objectif est de protéger le token contre une lecture directe,")
    print("    pas de le rendre impossible à récupérer.")
    print()
    password = input("Mot de passe: ").strip()
    if not password:
        print("Mot de passe vide, annulation.")
        return

    # Chiffrer le token
    st = SecureToken()
    encrypted = st.encrypt_token(token, password)

    print()
    print("=" * 60)
    print("✅ Token chiffré avec succès!")
    print("=" * 60)
    print()
    print("Copiez les valeurs suivantes dans secure_token.py:")
    print()
    print(f'ENCRYPTED_TOKEN = "{encrypted}"')
    print(f'PASSWORD = "{password}"')
    print()
    print("Remplacez les valeurs __ENCRYPTED_TOKEN__ et __PASSWORD__")
    print("dans la fonction get_embedded_token()")
    print()

    # Test de déchiffrement
    decrypted = st.decrypt_token(encrypted, password)
    if decrypted == token:
        print("✅ Test de déchiffrement réussi!")
    else:
        print("❌ Erreur: le déchiffrement a échoué")


if __name__ == "__main__":
    # Test ou setup
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_token()
    else:
        print("Usage:")
        print("  python secure_token.py setup    - Configure le token chiffré")
        print()
        print("Pour tester le déchiffrement:")
        st = SecureToken()
        token = st.get_embedded_token()
        if token:
            print(f"✅ Token récupéré: {token[:10]}...")
        else:
            print("⚠️  Token non configuré. Exécutez: python secure_token.py setup")
