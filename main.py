"""
main.py
-------
Point d'entrée de l'application.
Gère aussi la résolution des chemins quand l'app tourne
depuis un exe PyInstaller (sys._MEIPASS).
"""

import sys
import os
from pathlib import Path


def get_base_dir() -> Path:
    """
    Retourne le dossier de base des ressources.
    - En développement : dossier du script
    - En exe PyInstaller : dossier temporaire _MEIPASS
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


# Rend le dossier de base accessible à tous les modules
BASE_DIR = get_base_dir()
os.environ["IMAGESTUDIO_BASE"] = str(BASE_DIR)

# Ajoute le dossier source au path pour les imports relatifs
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from theme import apply_theme
from app import App

apply_theme()
app = App()
app.mainloop()
