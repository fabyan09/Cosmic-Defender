# 🚀 Cosmic Defender

Un jeu de tir spatial épique développé en Python avec Pygame !

## 🎮 Comment jouer

### Objectif
Défendez la Terre contre les vagues d'envahisseurs cosmiques ! Survivez à 10 vagues pour remporter la victoire.

### Contrôles
- **Déplacement** : WASD ou flèches directionnelles
- **Tir** : Barre d'espace ou clic souris
- **Menu** : Appuyez sur SPACE pour commencer
- **Plein écran** : F11 (ESC pour sortir du plein écran)
- **Leaderboard** : L depuis le menu principal
- **Sauvegarder score** : S après game over/victoire
- **Redémarrer** : R après un game over
- **Retour au menu** : ESC après un game over

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
- **Sauvegarde automatique** : Les scores sont sauvés dans `scores.json`
- **Leaderboard** : Top 10 des meilleurs scores avec nom, score, vague et date
- **Classement** : Les scores sont triés par points obtenus
- **Navigation** : Accès facile depuis le menu principal avec la touche L

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
- **PyInstaller 6.1.0** - Compilation en exécutable

## 🎯 Caractéristiques du jeu

- **Physique fluide** : Mouvement à 60 FPS
- **Effets visuels** : Particules d'explosion et animations
- **Interface intuitive** : Barres de santé/bouclier, score en temps réel
- **Gameplay équilibré** : Difficulté progressive et power-ups stratégiques
- **Système de vagues** : 10 niveaux de difficulté croissante
- **Types d'ennemis variés** : 4 types avec comportements uniques
- **Mode plein écran** : Support F11 pour jeu immersif
- **Système de scores** : Sauvegarde et leaderboard des meilleurs scores
- **Interface de saisie** : Entrez votre nom pour sauvegarder vos exploits

## 🏆 Conseils de pro

1. **Collectez les boucliers** en priorité pour survivre plus longtemps
2. **Utilisez le multi-tir** pour éliminer plusieurs ennemis rapidement
3. **Restez mobile** - ne restez jamais immobile trop longtemps
4. **Anticipez les vagues de boss** à partir de la vague 5
5. **Gérez vos power-ups** - ne les gaspillez pas !

Bon voyage dans l'espace, Commandant ! 🌌