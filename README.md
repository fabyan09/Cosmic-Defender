# 🚀 Cosmic Defender

Un jeu de tir spatial épique développé en Python avec Pygame !

## 🎮 Comment jouer

### Modes de jeu
- **🎯 Mode Campagne** : Survivez à 10 vagues pour remporter la victoire
- **♾️ Mode Infini** : Affrontez des vagues infinies avec des Giga Boss toutes les 10 vagues !

### Contrôles
- **Déplacement** : WASD ou flèches directionnelles
- **Tir** : Barre d'espace ou clic souris
- **Menu interactif** : Cliquez sur les boutons ou utilisez les raccourcis
- **Plein écran** : F11 (ESC pour sortir du plein écran)
- **Configuration GitHub** : Bouton "GITHUB SETUP" dans le menu
- **Sauvegarder score** : S après game over/victoire
- **Redémarrer** : R après un game over
- **Retour au menu** : ESC dans tous les écrans

### Éléments de jeu

#### 🛸 Votre Vaisseau
- **Santé** : 100 points de vie
- **Bouclier** : Protection supplémentaire (bleu)
- **Vitesse** : Déplacement rapide dans toutes les directions

#### 👾 Ennemis
- **Basiques** (Rouge) : Ennemis standard - 10 points
- **Rapides** (Rouge clair) : Plus rapides mais fragiles - 15 points
- **Blindés** (Rouge foncé) : Plus résistants et lents - 25 points
- **Boss** (Violet) : Très résistants avec patterns d'attaque - 100 points
- **🏰 Giga Boss** (Mode Infini) : Boss géants avec 4 patterns d'attaque et barre de vie - 500+ points

#### ⚡ Power-ups
- **🔶 Tir Rapide (Orange)** : Cadence de tir accélérée
- **🔵 Bouclier (Cyan)** : +25 points de bouclier
- **🟢 Multi-Tir (Vert)** : Tir en éventail (3 projectiles)
- **🟣 Laser (Violet)** : Tir puissant perforant

### Système de progression
- **Vagues** : Chaque vague augmente en difficulté
- **Score** : Accumulez des points en détruisant les ennemis
- **Power-ups** : 30% de chance d'apparition à la destruction d'un ennemi
- **Durée des power-ups** : 5 secondes d'effet

### 🏆 Système de scores
- **Sauvegarde locale** : Les scores sont sauvés dans `scores.json`
- **Leaderboard unifié** : Affiche les scores des modes Campagne et Infini
- **🌐 Leaderboard web** : Site web avec vos scores en temps réel
- **📤 Upload automatique** : Synchronisation automatique vers GitHub Pages
- **Filtrage par mode** : Visualisez séparément les scores par mode de jeu

## 🚀 Lancement du jeu

### Option 1 : Exécutable (.exe)
Double-cliquez sur `Cosmic_Defender.exe` dans le dossier `dist/`

### Option 2 : Code source Python
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le jeu (recommandé)
python launch.py

# Ou directement
python cosmic_defender.py
```

## 📁 Structure du projet

```
Jeu random/
├── cosmic_defender.py      # Code source principal
├── requirements.txt        # Dépendances Python
├── Cosmic_Defender.spec   # Configuration PyInstaller
├── dist/                  # Dossier contenant l'exécutable
│   └── Cosmic_Defender.exe
├── build/                 # Fichiers temporaires de compilation
└── README.md             # Ce fichier
```

## 🛠️ Technologies utilisées

- **Python 3.11**
- **Pygame 2.5.2** - Moteur de jeu 2D
- **NumPy 1.24.3** - Calculs mathématiques
- **Requests 2.32+** - API GitHub pour upload automatique
- **PyInstaller 6.1.0** - Compilation en exécutable

## 🎯 Caractéristiques du jeu

- **🎮 Deux modes de jeu** : Campagne (10 vagues) et Infini (sans fin)
- **🤖 Menu interactif** : Boutons cliquables responsive à toutes résolutions
- **🏰 Giga Boss** : Boss épiques avec patterns d'attaque complexes (mode infini)
- **🌐 Leaderboard web** : Site web automatiquement mis à jour
- **📤 Upload automatique** : Synchronisation GitHub en temps réel
- **🖥️ Responsive design** : Compatible fullscreen et toutes résolutions
- **🎨 Effets visuels** : Particules d'explosion et animations
- **⚖️ Gameplay équilibré** : Difficulté progressive et power-ups stratégiques
- **👾 Ennemis variés** : 5 types avec comportements uniques + Giga Boss
- **🎯 Interface intuitive** : Barres de santé/bouclier, score en temps réel

## 🏆 Conseils de pro

1. **Collectez les boucliers** en priorité pour survivre plus longtemps
2. **Utilisez le multi-tir** pour éliminer plusieurs ennemis rapidement
3. **Restez mobile** - ne restez jamais immobile trop longtemps
4. **Anticipez les vagues de boss** à partir de la vague 5
5. **Gérez vos power-ups** - ne les gaspillez pas !

Bon voyage dans l'espace, Commandant ! 🌌

## 🆕 Nouvelles fonctionnalités (v2.0)

### 🌐 Leaderboard Web
- **Site automatique** : Votre leaderboard en ligne sur GitHub Pages
- **Design spatial** : Interface immersive avec animations d'étoiles
- **Filtres intelligents** : Affichage par mode de jeu (Campagne/Infini/Tous)
- **Statistiques** : Nombre de joueurs, meilleur score, vague maximum
- **Responsive** : Fonctionne parfaitement sur mobile et desktop

### 📤 Upload Automatique GitHub
- **Configuration simple** : Interface intégrée dans le jeu
- **Synchronisation instantanée** : Scores uploadés automatiquement
- **Sécurisé** : Token GitHub avec permissions limitées
- **Mode offline** : Fonctionne même sans internet (sync plus tard)

### 🎮 Mode Infini
- **Vagues sans fin** : Défi ultime pour les meilleurs pilotes
- **Giga Boss toutes les 10 vagues** : Combats épiques avec patterns complexes
- **Difficulté progressive** : Plus d'ennemis et spawn plus rapide
- **Scores séparés** : Leaderboard dédié au mode infini

### 🤖 Interface Moderne
- **Menu interactif** : Boutons cliquables responsive
- **Configuration GitHub** : Interface complète dans le jeu
- **Fullscreen amélioré** : Adaptation parfaite à toutes les résolutions
- **Feedback visuel** : Effets hover et animations

**🚀 Explorez l'univers infini de Cosmic Defender !**
