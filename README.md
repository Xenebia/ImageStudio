# AI Image Upscaler

Améliore la qualité d'une image basse résolution via upscaling IA.

## Lancer

```bash
pip install -r requirements.txt
python main.py
```

## Backends disponibles

| Backend | Qualité | Prérequis |
|---|---|---|
| **Pillow Lanczos + Netteté** | Bonne | Aucun (auto) |
| **Real-ESRGAN** | Excellente | `torch`, `basicsr`, `realesrgan` + modèle `.pth` |

## Activer Real-ESRGAN (optionnel)

1. Installer les dépendances :
   ```bash
   pip install torch basicsr realesrgan
   ```

2. Télécharger un modèle sur [GitHub Real-ESRGAN Releases](https://github.com/xinntao/Real-ESRGAN/releases) :
   - `RealESRGAN_x2plus.pth` pour ×2
   - `RealESRGAN_x4plus.pth` pour ×4

3. Placer le fichier `.pth` dans le dossier `models/`

Le backend est détecté automatiquement au lancement.

## Structure

```
IA Image/
├── main.py          # Point d'entrée
├── gui.py           # Interface graphique
├── upscaler.py      # Moteur d'upscaling (Pillow ou Real-ESRGAN)
├── theme.py         # Thème visuel
├── requirements.txt
├── models/          # → place ici les .pth Real-ESRGAN
├── input/           # (optionnel)
└── output/          # Images améliorées (générées automatiquement)
```
