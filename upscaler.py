"""
upscaler.py
-----------
Moteur d'upscaling avec deux backends :
  1. Real-ESRGAN  (si torch + basicsr + realesrgan sont installés)
  2. Pillow Lanczos + filtre de netteté  (fallback toujours dispo)
"""

from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance


def _realesrgan_available():
    try:
        import torch  # noqa: F401
        from basicsr.archs.rrdbnet_arch import RRDBNet  # noqa: F401
        from realesrgan import RealESRGANer  # noqa: F401
        return True
    except ImportError:
        return False


def _upscale_realesrgan(img_path: str, scale: int, callback) -> Image.Image:
    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    models_dir = Path(__file__).parent / "models"
    model_path = models_dir / f"RealESRGAN_x{scale}plus.pth"

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

    import cv2
    img_cv = cv2.imread(img_path, cv2.IMREAD_COLOR)
    output, _ = upsampler.enhance(img_cv, outscale=scale)

    if callback:
        callback(0.9)

    return Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))


def _upscale_pillow(img: Image.Image, scale: int, callback) -> Image.Image:
    if callback:
        callback(0.1)

    if img.mode != "RGB":
        img = img.convert("RGB")

    if callback:
        callback(0.2)

    w, h = img.size
    upscaled = img.resize((w * scale, h * scale), Image.LANCZOS)

    if callback:
        callback(0.5)

    upscaled = upscaled.filter(
        ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3)
    )

    if callback:
        callback(0.7)

    upscaled = ImageEnhance.Contrast(upscaled).enhance(1.05)
    upscaled = ImageEnhance.Sharpness(upscaled).enhance(1.1)

    if callback:
        callback(0.9)

    return upscaled


def upscale_image_obj(img: Image.Image, scale: int = 4, callback=None) -> Image.Image:
    """Upscale a PIL Image object directly and return the result (in-memory)."""
    if _realesrgan_available():
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        try:
            result = _upscale_realesrgan(tmp_path, scale, callback)
        finally:
            os.unlink(tmp_path)
        return result
    else:
        return _upscale_pillow(img, scale, callback)


def get_backend_name() -> str:
    return "Real-ESRGAN (GPU/CPU)" if _realesrgan_available() else "Pillow Lanczos + Netteté"
