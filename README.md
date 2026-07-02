# Image Studio

> Éditeur d'images desktop — Upscaling IA, filtres rétro et pixelisation, dans un seul outil.

---

## ✨ Fonctionnalités

### 🔍 Agrandir (Upscaling IA)
- Améliore la résolution d'une image basse qualité
- Facteurs disponibles : **×2** et **×4**
- Backend automatique :
  - **Real-ESRGAN** si `torch` + modèle `.pth` installés (qualité maximale)
  - **Pillow Lanczos + netteté** sinon (aucune dépendance GPU requise)
- Traitement en arrière-plan, l'interface ne se bloque jamais

### 🟦 Pixeliser
- Effet pixel art réglable via un slider (intensité 0 → 95)
- Rendu en direct à chaque mouvement

### 🎨 Style (filtres rétro)
| Filtre | Description |
|---|---|
| Game Boy | Palette 4 tons verts emblématiques |
| Game Boy Pocket | Niveaux de gris 4 tons |
| Game Boy Color | Palette 32 couleurs |
| NES | Palette 16 couleurs |
| SNES | Palette 64 couleurs |
| Mega Drive | 32 couleurs, boost rouge/bleu |
| CRT | Effet scanlines une ligne sur deux |

### 🛠️ Outils image
- **Rotation** 90° horaire / antihoraire
- **Retournement** horizontal / vertical
- **Redimensionnement** avec ratio automatique
- **Zoom** : 11 paliers de 25% à 400%, mode "ajusté à la fenêtre"
- **Plein écran** `F11`

### 📂 Gestion des fichiers
- Ouvrir / Enregistrer / Enregistrer sous / Exporter
- Historique **Annuler / Rétablir** (20 états)
- Fichiers récents (8 derniers)

---

## 📁 Structure du projet

```
ImageStudio/
├── main.py          # Point d'entrée (compatible dev + exe PyInstaller)
├── app.py           # Orchestrateur principal
├── menu.py          # Barre de menu native (Fichier / Édition / Image / Affichage / Aide)
├── sidebar.py       # Sidebar à 3 onglets (Agrandir / Pixeliser / Style)
├── filters.py       # Filtres rétro + pixelisation (vectorisé numpy)
├── upscaler.py      # Moteur upscale (Real-ESRGAN ou Pillow)
├── theme.py         # Thème visuel CustomTkinter
├── assets/
│   └── icon.ico     # Icône de l'application
├── models/          # → place ici les modèles .pth Real-ESRGAN
└── output/          # Images exportées
```

---

## 🚀 Installation

### Prérequis
- Python 3.10+
- Windows 10/11 (testé), Linux/macOS compatible

### Lancer en développement

```bash
git clone https://github.com/Xenebia/ImageStudio
cd ImageStudio
pip install -r requirements.txt
python main.py
```

---

## 🤖 Activer Real-ESRGAN (optionnel)

Par défaut l'upscaling utilise Pillow. Pour activer le moteur IA complet :

**1. Installer les dépendances**
```bash
pip install torch basicsr realesrgan
```

**2. Télécharger un modèle** sur [GitHub Real-ESRGAN Releases](https://github.com/xinntao/Real-ESRGAN/releases) :
- `RealESRGAN_x2plus.pth` → pour ×2
- `RealESRGAN_x4plus.pth` → pour ×4

**3. Placer le fichier `.pth`** dans le dossier `models/`

Le backend est détecté et affiché automatiquement au lancement.

---

## ⌨️ Raccourcis clavier

| Raccourci | Action |
|---|---|
| `Ctrl+O` | Ouvrir une image |
| `Ctrl+S` | Enregistrer |
| `Ctrl+Shift+S` | Enregistrer sous |
| `Ctrl+E` | Exporter |
| `Ctrl+Z` | Annuler |
| `Ctrl+Y` | Rétablir |
| `Ctrl+R` | Redimensionner |
| `Ctrl++` | Zoom + |
| `Ctrl+-` | Zoom - |
| `Ctrl+0` | Taille réelle |
| `F11` | Plein écran |

---

## 📦 Dépendances

```
customtkinter   # Interface graphique moderne
Pillow          # Traitement d'images
numpy           # Filtres vectorisés (performance)
```

Optionnel pour Real-ESRGAN :
```
torch
basicsr
realesrgan
```

---

## 📄 Licence

Projet personnel — tous droits réservés © 2026
