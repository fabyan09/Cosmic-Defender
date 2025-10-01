# 🚀 Configuration du Leaderboard GitHub Actions

Ce guide explique comment configurer le système automatique de leaderboard pour Cosmic Defender.

## 📋 Aperçu

Le nouveau système utilise **GitHub Actions** pour gérer automatiquement le leaderboard :
- ✅ **Sécuritaire** : Votre token GitHub reste privé dans les Secrets
- ✅ **Automatique** : Les scores sont uploadés quand vous pushez sur GitHub
- ✅ **Simple** : Les joueurs n'ont qu'à jouer et push leurs scores

## 🔧 Configuration (Propriétaire du repo uniquement)

### Étape 1 : Créer un token GitHub

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur **"Generate new token"** → **"Generate new token (classic)"**
3. Donnez un nom : `Cosmic Defender Leaderboard`
4. Sélectionnez les permissions :
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (si demandé)
5. Générez et **copiez le token** (vous ne pourrez plus le voir après !)

### Étape 2 : Ajouter le token aux GitHub Secrets

1. Allez sur votre repository GitHub
2. Cliquez sur **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **"New repository secret"**
4. Nom : `LEADERBOARD_TOKEN`
5. Valeur : Collez votre token GitHub
6. Cliquez sur **"Add secret"**

### Étape 3 : Vérifier le workflow

Le fichier `.github/workflows/update-leaderboard.yml` est déjà configuré.
Il se déclenche automatiquement quand des scores sont poussés dans `scores/`.

## 🎮 Utilisation (Pour tous les joueurs)

### Jouer et sauvegarder un score

1. Lancez le jeu : `python cosmic_defender.py`
2. Jouez et faites un bon score !
3. Appuyez sur **S** pour sauvegarder votre score
4. Entrez votre nom

Le score est sauvegardé localement dans le dossier `scores/`.

### Uploader votre score sur le leaderboard

```bash
# 1. Ajoutez vos scores
git add scores/

# 2. Créez un commit
git commit -m "Add my new score"

# 3. Pushez sur GitHub
git push
```

**C'est tout !** GitHub Actions va automatiquement :
- Collecter tous les nouveaux scores dans `scores/`
- Les fusionner avec le leaderboard existant
- Uploader le tout sur `cosmic-defender-leaderboard`

## 📊 Voir le leaderboard

Le leaderboard est accessible sur :
https://fabyan09.github.io/cosmic-defender-leaderboard/

## 🔍 Vérifier que ça fonctionne

1. Allez sur votre repo GitHub
2. Cliquez sur l'onglet **"Actions"**
3. Vous verrez le workflow **"Update Leaderboard"** s'exécuter
4. Si tout est vert ✅, votre score est uploadé !

## ⚠️ Important

### Sécurité

- ❌ **NE JAMAIS** commiter `config_token.py`
- ❌ **NE JAMAIS** commiter votre token GitHub en clair
- ✅ Le token doit UNIQUEMENT être dans GitHub Secrets

### Structure des fichiers

```
Cosmic Defender/
├── .github/
│   └── workflows/
│       └── update-leaderboard.yml    # GitHub Actions workflow
├── scores/                            # ✅ INCLUS dans Git
│   ├── score_uuid1_20250101_120000.json
│   ├── score_uuid2_20250101_120100.json
│   └── ...
├── config_token.py                    # ❌ IGNORÉ par Git (.gitignore)
├── scores.json                        # ❌ IGNORÉ (leaderboard local)
└── web_scores.json                    # ❌ IGNORÉ (backup local)
```

## 🛠️ Dépannage

### Le workflow ne se déclenche pas

- Vérifiez que vous avez bien poussé des fichiers dans `scores/`
- Vérifiez que vous êtes sur la branche `master`

### Erreur "Invalid token"

- Vérifiez que le secret `LEADERBOARD_TOKEN` est bien configuré
- Vérifiez que le token a les bonnes permissions (`repo`)
- Générez un nouveau token si nécessaire

### Le leaderboard n'est pas mis à jour

1. Allez dans l'onglet **Actions** sur GitHub
2. Cliquez sur le workflow qui a échoué
3. Lisez les logs pour voir l'erreur

## 🎯 Avantages de cette approche

| Avant (upload direct) | Maintenant (GitHub Actions) |
|----------------------|----------------------------|
| Token en base64 dans le code | Token sécurisé dans Secrets |
| Chaque joueur doit configurer | Configuration centralisée |
| Upload immédiat (peut échouer) | Upload fiable via GitHub |
| Dépend du module `requests` | Fonctionne toujours |

## 📝 Notes

- Le leaderboard garde les **250 meilleurs scores**
- Les scores sont dédupliqués automatiquement
- Vous pouvez push plusieurs scores en même temps
- Le workflow fusionne intelligemment les scores
