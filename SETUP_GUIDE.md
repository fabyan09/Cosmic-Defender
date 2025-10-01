# 🎮 Guide de Configuration - Cosmic Defender Leaderboard

## 📋 Vue d'ensemble

Cosmic Defender utilise maintenant un système **d'upload automatique** vers GitHub.
Les joueurs n'ont **rien à configurer** - ils jouent, et leurs scores sont automatiquement uploadés!

## 🔐 Pour le Propriétaire (Configuration une seule fois)

### Étape 1: Installer les dépendances

```bash
pip install cryptography requests
```

### Étape 2: Créer un token GitHub

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur **"Generate new token"** → **"Generate new token (classic)"**
3. Nom: `Cosmic Defender Leaderboard`
4. Permissions: Cochez **`repo`** (Full control of private repositories)
5. Cliquez sur **"Generate token"**
6. **Copiez le token** (commence par `ghp_...`)

### Étape 3: Configurer le token dans le jeu

```bash
python setup_github_token.py
```

Le script va:
1. Vous demander votre token GitHub
2. Vous demander un mot de passe pour le chiffrer
3. Modifier automatiquement `secure_token.py`
4. Tester que tout fonctionne

### Étape 4: Committer les changements

```bash
git add secure_token.py setup_github_token.py
git commit -m "Configure encrypted GitHub token for auto-upload"
git push
```

✅ **C'est tout!** Le token est maintenant chiffré et embarqué dans le jeu.

## 🎮 Pour les Joueurs (Aucune configuration!)

### Installation

```bash
# Cloner le repo
git clone https://github.com/fabyan09/Cosmic-Defender.git
cd Cosmic-Defender

# Installer les dépendances
pip install pygame requests cryptography

# Lancer le jeu
python cosmic_defender.py
```

### Jouer et sauvegarder

1. **Jouez** au jeu
2. Faites un bon score!
3. Appuyez sur **S** pour sauvegarder
4. Entrez votre nom
5. **C'est tout!**

Le score est **automatiquement uploadé** vers le leaderboard GitHub en arrière-plan. 🎉

### Voir le leaderboard

Visitez: https://fabyan09.github.io/cosmic-defender-leaderboard/

## 🔒 Sécurité

### Pourquoi c'est sécuritaire?

1. **Token chiffré** : Utilise Fernet (cryptographie symétrique AES)
2. **Pas en clair** : Contrairement à base64, c'est du vrai chiffrement
3. **Protection raisonnable** : Protège contre la lecture directe du token

### Qu'est-ce qui EST committé sur GitHub?

✅ **OUI - Safe à committer:**
- `secure_token.py` (contient le token **chiffré**)
- `setup_github_token.py` (script de configuration)
- Tous les fichiers du jeu

❌ **NON - Ne JAMAIS committer:**
- `config_token.py` (ancien système, token en base64)
- Votre token GitHub en clair
- Vos credentials personnels

## 🔧 Architecture Technique

### Comment ça marche?

```
1. Joueur sauvegarde un score
   ↓
2. Le jeu crée un objet score JSON
   ↓
3. Le jeu déchiffre le token embarqué
   ↓
4. Upload via GitHub API (en arrière-plan)
   ↓
5. Le score apparaît sur le leaderboard GitHub
```

### Fichiers importants

```
Cosmic Defender/
├── secure_token.py          # Module de chiffrement + token chiffré
├── setup_github_token.py    # Script de configuration (propriétaire)
├── cosmic_defender.py       # Jeu principal
├── .gitignore              # Protège config_token.py
└── SETUP_GUIDE.md          # Ce fichier
```

### Flux de données

```python
# Dans secure_token.py (après configuration)
ENCRYPTED_TOKEN = "gAAAAABl..." # Token chiffré
PASSWORD = "votre_password"      # Mot de passe (embarqué)

# Au runtime
SecureToken().get_embedded_token()
→ Déchiffre le token
→ Retourne le token en clair (en mémoire uniquement)
→ GitHubUploader l'utilise pour l'API
```

## 🧪 Tests

### Tester la configuration

```bash
python secure_token.py
```

Devrait afficher:
```
✅ Token récupéré: ghp_5NRm1...
```

### Tester l'upload

1. Lancez le jeu: `python cosmic_defender.py`
2. Jouez et sauvegardez un score
3. Regardez la console:

```
============================================================
📤 Upload automatique du score vers GitHub...
✓ Leaderboard uploaded to GitHub successfully!
============================================================
```

## ❓ FAQ

### Un joueur peut-il récupérer mon token?

**Techniquement oui**, mais c'est beaucoup plus difficile qu'avec base64:
- Il faudrait décompiler le code Python
- Extraire le token chiffré ET le mot de passe
- Les utiliser pour déchiffrer

**Comparaison:**
- Base64: `1 ligne de Python` pour décoder
- Fernet: `Décompiler + reverse engineering + utiliser cryptography`

### C'est vraiment sûr?

Pour un **jeu open-source**, c'est un **bon compromis**:
- ✅ Empêche la lecture directe du token
- ✅ Les joueurs peuvent télécharger et jouer facilement
- ✅ Upload automatique sans configuration
- ⚠️ Un hacker déterminé peut toujours extraire le token

**Solution alternative pour sécurité maximale:**
- Héberger un backend serveur
- Mais c'est beaucoup plus complexe pour un jeu indie

### Pourquoi ne pas utiliser GitHub Secrets + Actions?

GitHub Actions nécessite que les joueurs **push leurs scores**, ce qui n'est pas automatique.
L'upload direct via l'API GitHub est **instantané** et **transparent**.

### Que se passe-t-il si GitHub rate limit?

GitHub API limite:
- **5000 requests/heure** pour les utilisateurs authentifiés
- Pour un jeu, c'est largement suffisant
- Si dépassé: le score est sauvegardé localement uniquement

## 🚀 Migration depuis l'ancien système

Si vous utilisiez `config_token.py`:

1. Exécutez `python setup_github_token.py`
2. Supprimez `config_token.py` (ne plus nécessaire)
3. Le jeu utilisera automatiquement le nouveau système

## 📞 Support

En cas de problème:
1. Vérifiez que `cryptography` est installé
2. Testez avec `python secure_token.py`
3. Relancez `python setup_github_token.py` si nécessaire

---

**Profitez du jeu et que le meilleur gagne! 🚀**
