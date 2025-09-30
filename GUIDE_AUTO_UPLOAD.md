# 🚀 Guide Upload Automatique GitHub

Ce guide vous explique comment configurer l'upload automatique des scores vers votre leaderboard GitHub.

## 🎯 Avantages de l'upload automatique

- ✅ **Mise à jour instantanée** : Les scores apparaissent sur le site web dès la fin de partie
- ✅ **Aucune intervention manuelle** : Plus besoin d'uploader le fichier JSON manuellement
- ✅ **Synchronisation en temps réel** : Votre leaderboard est toujours à jour
- ✅ **Fonctionne en arrière-plan** : Pas d'interruption du jeu

## 📋 Prérequis

1. **Module requests** installé :
   ```bash
   pip install requests
   ```

2. **Repository GitHub** configuré avec GitHub Pages

3. **Token d'accès GitHub** avec les bonnes permissions

## 🔧 Configuration étape par étape

### 1. Créer un token GitHub

1. Allez sur [GitHub.com](https://github.com) > **Settings** (profil)
2. Dans le menu de gauche : **Developer settings**
3. Cliquez sur **Personal access tokens** > **Tokens (classic)**
4. Cliquez **Generate new token** > **Generate new token (classic)**
5. Nommez votre token : `Cosmic Defender Leaderboard`
6. Sélectionnez la durée (recommandé : No expiration)
7. **Permissions requises** :
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
8. Cliquez **Generate token**
9. **⚠️ IMPORTANT** : Copiez le token immédiatement (il ne sera plus affiché)

### 2. Configurer dans le jeu

1. Lancez Cosmic Defender
2. Dans le menu principal, cliquez **GITHUB SETUP**
3. Remplissez les champs :
   - **Username GitHub** : Votre nom d'utilisateur GitHub
   - **Nom du repository** : Le nom de votre repository (ex: `cosmic-defender-leaderboard`)
   - **Token d'accès** : Le token créé à l'étape 1

### 3. Tester la configuration

1. Appuyez sur **T** pour tester la connexion
2. Si tout est OK, vous verrez : "Connection successful"
3. Appuyez sur **S** pour sauvegarder
4. Cochez l'option **Upload automatique** avec **A**

## 🎮 Utilisation

Une fois configuré, l'upload automatique fonctionne ainsi :

1. **Jouez normalement** à Cosmic Defender
2. **Sauvegardez votre score** avec S à la fin de partie
3. **Le jeu upload automatiquement** vers GitHub
4. **Votre site web** se met à jour avec le nouveau score

### Notifications

Le jeu affiche des messages dans la console :
- ✅ `Leaderboard uploaded to GitHub successfully!` : Upload réussi
- ❌ `GitHub upload failed: [raison]` : Échec de l'upload

## 🛠️ Dépannage

### ❌ "Module 'requests' requis"
```bash
pip install requests
```

### ❌ "Invalid token"
- Vérifiez que le token est correct
- Assurez-vous qu'il n'a pas expiré
- Recréez un nouveau token si nécessaire

### ❌ "Repository not found"
- Vérifiez l'orthographe du nom du repository
- Assurez-vous que le repository est public ou que le token a accès aux repos privés

### ❌ "No internet connection"
- L'upload automatique nécessite une connexion internet
- Les scores sont sauvegardés localement et peuvent être uploadés manuellement plus tard

### ❌ "Upload timeout"
- Problème de connexion temporaire
- Le jeu réessaiera automatiquement au prochain score

## 🔒 Sécurité

- **Token stocké localement** : Le token est sauvé dans `github_config.json`
- **Chiffrement recommandé** : Considérez chiffrer votre disque dur
- **Accès limité** : Le token n'a accès qu'aux repositories, pas aux autres données GitHub

## 📊 Format des données uploadées

Le fichier uploadé (`cosmic_defender_leaderboard.json`) contient :

```json
{
  "last_updated": "2025-01-15T10:30:00",
  "total_scores": 25,
  "scores": [
    {
      "player_id": "unique-player-id",
      "name": "COSMIC_ACE",
      "score": 15420,
      "wave": 25,
      "mode": "infinite",
      "timestamp": "2025-01-15T10:30:00",
      "date": "2025-01-15 10:30"
    }
  ]
}
```

## 🔄 Mode offline/online

Le système gère automatiquement les cas où :
- **Pas d'internet** : Les scores sont sauvés localement
- **Serveur GitHub indisponible** : Réessai automatique plus tard
- **Token expiré** : Message d'erreur explicite

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifiez la console** du jeu pour les messages d'erreur
2. **Testez la connexion** avec le bouton TESTER
3. **Recréez le token** GitHub si nécessaire
4. **Vérifiez les permissions** du repository

---

**Profitez de votre leaderboard automatisé ! 🛸**