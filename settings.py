"""
settings.py
-----------

Préférences utilisateur persistantes (fichier JSON).
Windows : %APPDATA%\\ImageStudio\\settings.json
Autres  : ~/.config/ImageStudio/settings.json
"""

import json
import os
from pathlib import Path

DEFAULTS = {
    "appearance": "dark",     # dark | light | system
    "default_pixel": 0,       # intensité de pixelisation au chargement (0-95)
    "live_preview": True,     # pixelisation en direct pendant le glissement du slider
    "jpeg_quality": 95,       # qualité de l'export JPEG (60-100)
    "max_history": 20,        # nombre d'états Annuler / Rétablir
}


def _config_path() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    folder = Path(base) / "ImageStudio"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"


class Settings:
    def __init__(self):
        self._path = _config_path()
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            for key in DEFAULTS:
                if key in stored:
                    self._data[key] = stored[key]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass  # premier lancement ou fichier corrompu : valeurs par défaut

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key):
        return self._data.get(key, DEFAULTS[key])

    def update(self, **values):
        for key, value in values.items():
            if key in DEFAULTS:
                self._data[key] = value
