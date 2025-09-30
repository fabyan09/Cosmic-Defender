# 🚀 COSMIC DEFENDER - Guide d'Installation

## ✅ Solution Recommandée : Script de Lancement (.bat)

### Option 1 : Lancement Direct
Double-cliquez sur **`START_GAME.bat`** pour lancer le jeu immédiatement !

### Option 2 : Installation Automatique
Double-cliquez sur **`install_and_play.bat`** pour installer automatiquement les dépendances puis lancer le jeu.

## 📋 Prérequis

### Python
- **Version requise** : Python 3.7 ou supérieur
- **Téléchargement** : https://python.org
- ⚠️ **IMPORTANT** : Cochez "Add Python to PATH" lors de l'installation !

### Vérification de Python
Ouvrez une invite de commande et tapez :
```bash
python --version
```
Si vous voyez un numéro de version, Python est installé correctement.

## 🎮 Fichiers de Lancement

### 1. `START_GAME.bat` ⭐ (Recommandé)
- **Usage** : Double-cliquez pour jouer
- **Avantages** : Simple, rapide, fiable
- **Prérequis** : Python + dépendances déjà installées

### 2. `install_and_play.bat`
- **Usage** : Installation complète automatique
- **Avantages** : Installe tout automatiquement
- **Prérequis** : Python seulement

### 3. `LANCER_LE_JEU.bat`
- **Usage** : Version avec interface graphique améliorée
- **Avantages** : Joli affichage, instructions détaillées
- **Note** : Peut avoir des problèmes d'encodage sur certains systèmes

## 🔧 Installation Manuelle

Si les scripts automatiques ne fonctionnent pas :

### 1. Installer les dépendances
```bash
pip install pygame==2.5.2 numpy==1.24.3
```

### 2. Lancer le jeu
```bash
python cosmic_defender.py
```

## ❌ Résolution des Problèmes

### Erreur "Python n'est pas reconnu"
- **Solution** : Réinstallez Python en cochant "Add Python to PATH"
- **Alternative** : Ajoutez manuellement Python au PATH système

### Erreur "ordinal 380 introuvable"
- **Cause** : Problème avec l'exécutable PyInstaller
- **Solution** : Utilisez les scripts .bat à la place

### Erreur de dépendances
- **Solution** : Exécutez `install_and_play.bat`
- **Manuel** : `pip install --user pygame numpy`

### Problème d'encodage (emojis)
- **Solution** : Utilisez `START_GAME.bat` (version simple)
- **Cause** : Certains terminaux Windows ne supportent pas l'UTF-8

## 📁 Structure des Fichiers

```
Jeu random/
├── cosmic_defender.py           # Code source principal ⭐
├── START_GAME.bat              # Lanceur simple ⭐
├── install_and_play.bat        # Installeur automatique
├── LANCER_LE_JEU.bat          # Lanceur avec interface
├── cosmic_defender_standalone.py # Version avec auto-install
├── requirements.txt            # Liste des dépendances
├── README.md                   # Guide du jeu
├── INSTALLATION.md            # Ce fichier
└── build/                     # Fichiers de compilation
    └── Cosmic_Defender/
        └── Cosmic_Defender.exe # Exécutable (peut ne pas fonctionner)
```

## 🎯 Contrôles du Jeu

- **Déplacement** : WASD ou flèches directionnelles
- **Tir** : Barre d'espace ou clic souris
- **Menu** : SPACE pour commencer
- **Redémarrer** : R après game over
- **Retour menu** : ESC après game over

## 🌟 Conseils de Performance

1. **Fermez** les autres applications pour de meilleures performances
2. **Résolution** : Le jeu fonctionne en 1000x700 pixels
3. **FPS** : Optimisé pour 60 FPS

---

**Bon voyage dans l'espace, Commandant ! 🚀**

*Si vous rencontrez des problèmes, essayez d'abord `START_GAME.bat` - c'est la solution la plus fiable !*