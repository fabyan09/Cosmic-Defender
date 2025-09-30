# 🚀 Guide de déploiement du Leaderboard Cosmic Defender

Ce guide vous explique comment créer un site leaderboard pour votre jeu Cosmic Defender sur GitHub Pages.

## 🎯 Résultat final

Votre leaderboard sera accessible à l'adresse : `https://fabyan09.github.io/cosmic-defender-leaderboard/`

## 📋 Étapes de déploiement

### 1. Créer le repository GitHub

1. Allez sur [GitHub](https://github.com) et connectez-vous
2. Cliquez sur "New repository" (bouton vert)
3. Nommez votre repository : `cosmic-defender-leaderboard`
4. Cochez "Public" (obligatoire pour GitHub Pages gratuit)
5. Cochez "Add a README file"
6. Cliquez "Create repository"

### 2. Activer GitHub Pages

1. Dans votre nouveau repository, allez dans **Settings** (en haut)
2. Descendez jusqu'à la section **Pages** (dans le menu de gauche)
3. Sous "Source", sélectionnez **Deploy from a branch**
4. Sous "Branch", sélectionnez **main**
5. Laissez "/ (root)" sélectionné
6. Cliquez **Save**

### 3. Uploader les fichiers du leaderboard

1. Retournez à l'onglet **Code** de votre repository
2. Cliquez "uploading an existing file" ou glissez-déposez les fichiers
3. Uploadez TOUS les fichiers du dossier `leaderboard_deploy/` :
   - `index.html`
   - `styles.css`
   - `script.js`
   - `cosmic_defender_leaderboard.json`
   - `README.md`

4. Écrivez un message de commit : "Initial leaderboard setup"
5. Cliquez **Commit changes**

### 4. Vérifier le déploiement

1. Retournez dans **Settings > Pages**
2. Vous devriez voir un message vert : "Your site is published at..."
3. Cliquez sur le lien pour voir votre leaderboard !

## 🎮 Utilisation du système

### Fonctionnement automatique

Chaque fois que vous sauvegardez un score dans le jeu :
1. Le jeu met à jour `cosmic_defender_leaderboard.json`
2. Vous devez uploader ce fichier sur GitHub
3. Le site se met à jour automatiquement

### Mise à jour manuelle des scores

1. Jouez à Cosmic Defender et sauvegardez vos scores
2. Le fichier `cosmic_defender_leaderboard.json` est créé/mis à jour
3. Allez sur votre repository GitHub
4. Cliquez sur `cosmic_defender_leaderboard.json`
5. Cliquez sur l'icône crayon (Edit)
6. Supprimez tout le contenu
7. Copiez-collez le contenu du nouveau fichier
8. Cliquez "Commit changes"

## 🌟 Fonctionnalités du leaderboard

- **Affichage en temps réel** des meilleurs scores
- **Filtres par mode** : Campaign, Infinite, ou Tous
- **Statistiques globales** : nombre de joueurs, meilleur score, vague max
- **Design spatial** avec animations et effets visuels
- **Responsive** : fonctionne sur mobile et desktop
- **Médailles** pour le top 3 (🥇🥈🥉)

## 🔧 Personnalisation

### Changer l'apparence

Modifiez `styles.css` pour :
- Changer les couleurs
- Modifier les fonts
- Ajuster les animations

### Ajouter des fonctionnalités

Modifiez `script.js` pour :
- Ajouter de nouveaux filtres
- Modifier l'affichage des données
- Ajouter des statistiques

## 📊 Format des données

Le fichier `cosmic_defender_leaderboard.json` contient :

```json
{
  "last_updated": "2025-01-15T10:30:00",
  "total_scores": 50,
  "scores": [
    {
      "player_id": "unique-id",
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

## 🚨 Dépannage

### Le site ne s'affiche pas
- Vérifiez que GitHub Pages est activé
- Attendez quelques minutes (déploiement)
- Vérifiez que tous les fichiers sont présents

### Les scores ne s'affichent pas
- Vérifiez le format du fichier JSON
- Ouvrez la console du navigateur (F12) pour voir les erreurs
- Vérifiez que le fichier `cosmic_defender_leaderboard.json` est valide

### Erreur 404
- Vérifiez l'URL : doit être `https://VOTRE-USERNAME.github.io/cosmic-defender-leaderboard/`
- Vérifiez que le repository est public
- Vérifiez que GitHub Pages est activé sur la branche `main`

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez ce guide étape par étape
2. Consultez les logs GitHub Actions dans l'onglet "Actions"
3. Ouvrez une issue sur le repository du jeu

---

**Bon jeu et que le meilleur commandant galactique gagne ! 🛸**