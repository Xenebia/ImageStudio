"""
upscaler.py
-----------
Moteur d'upscaling avec deux backends :
  1. Real-ESRGAN  (si torch + basicsr + realesrgan sont installés)
  2. Pillow Lanczos + filtre de netteté  (fallback toujours dispo)

Usage :
    from upscaler import upscale_image
    output_path = upscale_image("input.png", scale=4, callback=lambda p: print(p))
"""

import os
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance


# ──────────────────────────────────────────────────────────────
# Détection Real-ESRGAN
# ──────────────────────────────────────────────────────────────
def _realesrgan_available():
    try:
        import torch  # noqa: F401
        from basicsr.archs.rrdbnet_arch import RRDBNet  # noqa: F401
        from realesrgan import RealESRGANer  # noqa: F401
        return True
    except ImportError:
        return False


# ──────────────────────────────────────────────────────────────
# Backend Real-ESRGAN
# ──────────────────────────────────────────────────────────────
def _upscale_realesrgan(img_path: str, scale: int, callback) -> Image.Image:
    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    models_dir = Path(__file__).parent / "models"
    model_name = f"RealESRGAN_x{scale}plus.pth"
    model_path = models_dir / model_name

    if not model_path.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {model_path}\n"
            f"Télécharge-le sur https://github.com/xinntao/Real-ESRGAN/releases "
            f"et place-le dans le dossier models/"
        )

    model = RRDBNet(
        num_in_ch=3, num_out_ch=3,
        num_feat=64, num_block=23, num_grow_ch=32,
        scale=scale
    )
    upsampler = RealESRGANer(
        scale=scale,
        model_path=str(model_path),
        model=model,
        tile=400,
        tile_pad=10,
        pre_pad=0,
        half=torch.cuda.is_available(),
    )

    if callback:
        callback(0.3)

    import cv2, numpy as np
    img_cv = cv2.imread(img_path, cv2.IMREAD_COLOR)
    output, _ = upsampler.enhance(img_cv, outscale=scale)

    if callback:
        callback(0.9)

    return Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))


# ──────────────────────────────────────────────────────────────
# Backend Pillow (fallback)
# ──────────────────────────────────────────────────────────────
def _upscale_pillow(img: Image.Image, scale: int, callback) -> Image.Image:
    """
    Upscaling Pillow en plusieurs passes pour meilleure qualité :
      - Redimensionnement Lanczos
      - Filtre de netteté adaptatif
      - Légère amélioration du contraste
    """
    w, h = img.size
    steps = 4

    if callback:
        callback(0.1)

    # Conversion en RGB si nécessaire (ex. PNG avec transparence)
    if img.mode != "RGB":
        img = img.convert("RGB")

    if callback:
        callback(0.2)

    # Upscale en une passe Lanczos
    new_w, new_h = w * scale, h * scale
    upscaled = img.resize((new_w, new_h), Image.LANCZOS)

    if callback:
        callback(0.5)

    # Filtre de netteté (UnsharpMask simule ce que fait Real-ESRGAN côté détails)
    upscaled = upscaled.filter(
        ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3)
    )

    if callback:
        callback(0.7)

    # Légère amélioration du contraste
    upscaled = ImageEnhance.Contrast(upscaled).enhance(1.05)
    upscaled = ImageEnhance.Sharpness(upscaled).enhance(1.1)

    if callback:
        callback(0.9)

    return upscaled


# ──────────────────────────────────────────────────────────────
# Fonction publique
# ──────────────────────────────────────────────────────────────
def upscale_image(
    input_path: str,
    scale: int = 4,
    output_dir: str | None = None,
    callback=None,
) -> str:
    """
    Upscale une image et retourne le chemin du fichier de sortie.

    Args:
        input_path  : chemin vers l'image source
        scale       : facteur d'agrandissement (2 ou 4)
        output_dir  : dossier de sortie (défaut : ./output/)
        callback    : fonction(progress: float) appelée pendant le traitement

    Returns:
        Chemin absolu de l'image améliorée
    """
    input_path = Path(input_path)
    if output_dir is None:
        output_dir = Path(__file__).parent / "output"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    suffix = input_path.suffix.lower() or ".png"
    output_path = output_dir / f"{stem}_x{scale}{suffix}"

    use_realesrgan = _realesrgan_available()

    if use_realesrgan:
        result = _upscale_realesrgan(str(input_path), scale, callback)
    else:
        img = Image.open(input_path)
        result = _upscale_pillow(img, scale, callback)

    # Sauvegarde
    if suffix in (".jpg", ".jpeg"):
        result.save(str(output_path), "JPEG", quality=95, subsampling=0)
    else:
        result.save(str(output_path), "PNG")

    if callback:
        callback(1.0)

    return str(output_path)


def get_backend_name() -> str:
    return "Real-ESRGAN (GPU/CPU)" if _realesrgan_available() else "Pillow Lanczos + Netteté"
