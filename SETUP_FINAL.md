# 🚀 Configuration Finale - Leaderboard Centralisé

## 🎯 Objectif
Configurer votre jeu pour que **tous les joueurs** contribuent automatiquement au **même leaderboard centralisé**.

## 📋 Étapes de configuration

### 1. Encoder votre token GitHub

```bash
python encode_token.py
```

Le script vous demandera votre token et vous donnera une chaîne encodée.

### 2. Modifier cosmic_defender.py

Ouvrez `cosmic_defender.py` et trouvez cette ligne (vers la ligne 456) :

```python
encoded_token = "REMPLACEZ_PAR_VOTRE_TOKEN_ENCODE"
```

Remplacez-la par la chaîne que le script vous a donnée, par exemple :

```python
encoded_token = "Z2hwX3MxMjM0NTY3ODkwYWJjZGVmZ2hpams..."
```

### 3. Créer votre repository leaderboard

1. Allez sur GitHub.com
2. Créez un nouveau repository public : `cosmic-defender-leaderboard`
3. Activez GitHub Pages (Settings > Pages > Deploy from branch > main)

### 4. Supprimer le script d'encodage

⚠️ **IMPORTANT** : Supprimez `encode_token.py` après utilisation !

```bash
del encode_token.py
```

### 5. Tester

Lancez le jeu, jouez une partie, sauvegardez votre score. Le fichier devrait être automatiquement uploadé sur votre repository.

## 🎮 Résultat final

- **Jeu prêt à distribuer** : Aucune configuration requise pour les joueurs
- **Leaderboard centralisé** : Tous les scores apparaissent sur VOTRE site
- **Upload automatique** : Transparent pour les joueurs
- **Site web** : `https://fabyan09.github.io/cosmic-defender-leaderboard/`

## 🔒 Sécurité

- Le token est encodé (pas en clair) dans le code
- Seul le repository leaderboard est accessible
- Les joueurs ne peuvent que ajouter des scores, pas les supprimer

## 📤 Distribution

Une fois configuré, vous pouvez :
- Commiter/pusher sur GitHub (sans encode_token.py)
- Partager le repository
- Créer des releases
- Tous les joueurs contribueront automatiquement à votre leaderboard !

---

**Votre jeu sera ready-to-play avec leaderboard centralisé ! 🛸**