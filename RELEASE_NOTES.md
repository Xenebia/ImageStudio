## Image Studio v1.1.0

Cette version ajoute le logo dans la fenêtre, un vrai contrôle de la pixellisation et un panneau de préférences.

### ✨ Nouveautés

**Pixellisation plus précise**
- Champ de saisie pour taper la valeur exacte (0 – 95), avec validation à la touche Entrée ou à la perte du focus
- Boutons **−** / **+** pour ajuster de 1 en 1
- 4 préréglages en un clic : **Léger** (10), **Moyen** (30), **Fort** (60), **Max** (95)
- Le slider, le champ et les boutons restent synchronisés

**Panneau de préférences** (menu *Édition → Préférences*)
- Apparence : sombre, clair ou système
- Intensité de pixellisation appliquée au chargement d'une image
- Rendu en direct : activé, la pixellisation suit le slider en temps réel ; désactivé, elle s'applique au relâchement
- Qualité de l'export JPEG (60 – 100)
- Taille de l'historique Annuler / Rétablir (10, 20 ou 50)
- Bouton *Valeurs par défaut*
- Les réglages sont enregistrés dans `%APPDATA%\ImageStudio\settings.json` et conservés entre les sessions

### 🐛 Corrections

- **Logo de l'application** : l'icône s'affiche maintenant dans la barre de titre. CustomTkinter remplaçait l'icône par défaut environ 200 ms après l'ouverture de la fenêtre ; elle est désormais réappliquée juste après. L'icône est aussi utilisée dans la barre des tâches et dans la fenêtre de préférences.

### 🔧 Compilation

- Nouveau script `build_exe_v2.bat` : compile dans un environnement virtuel propre (`.venv_build`), avec l'icône (`--icon`), le dossier `assets` et les données de CustomTkinter intégrés
- Corrige l'erreur `RecursionError` de PyInstaller causée par les paquets parasites d'un Python global
- Python 3.12 ou 3.13 recommandé pour la compilation

### 📁 Fichiers ajoutés ou modifiés

| Fichier | Changement |
|---|---|
| `settings.py` | **Nouveau**, sauvegarde et chargement des préférences |
| `preferences.py` | **Nouveau**, fenêtre de préférences |
| `sidebar.py` | Onglet Pixeliser : champ, boutons −/+, préréglages, rendu en direct |
| `app.py` | Icône réappliquée, préférences branchées, qualité JPEG et historique configurables |
| `build_exe_v2.bat` | **Nouveau**, compilation en environnement propre |

### 📦 Installation

Télécharge `ImageStudio.zip` ci-dessous, décompresse-le et lance `ImageStudio.exe`. Aucune installation de Python n'est nécessaire.
