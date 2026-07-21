"""
filters.py
----------
Filtres rétro (Game Boy, NES, SNES, etc.) et pixelisation.
Implémentés avec numpy pour rester rapides même sur de grandes images.
"""

import numpy as np
from PIL import Image

FILTER_NAMES = [
    "Aucun",
    "Game Boy",
    "Game Boy Pocket",
    "Game Boy Color",
    "NES",
    "SNES",
    "Mega Drive",
    "CRT",
]


def pixelate(image: Image.Image, amount: int) -> Image.Image:
    """amount: 0-95, 0 = pas de pixelisation."""
    if amount <= 0:
        return image

    width, height = image.size
    factor = max(1, int((100 - amount) / 100 * width))
    factor_h = max(1, int((100 - amount) / 100 * height))

    small = image.resize((factor, factor_h), Image.Resampling.NEAREST)
    return small.resize((width, height), Image.Resampling.NEAREST)


def _map_palette_by_luminance(gray_arr: np.ndarray, palette: list[tuple[int, int, int]]) -> np.ndarray:
    """Mappe une image en niveaux de gris vers une palette à 4 teintes par seuils de luminance."""
    h, w = gray_arr.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)

    thresholds = [64, 128, 192]
    masks = [
        gray_arr < thresholds[0],
        (gray_arr >= thresholds[0]) & (gray_arr < thresholds[1]),
        (gray_arr >= thresholds[1]) & (gray_arr < thresholds[2]),
        gray_arr >= thresholds[2],
    ]
    for mask, color in zip(masks, palette):
        out[mask] = color

    return out


def _game_boy(image: Image.Image) -> Image.Image:
    gray = np.array(image.convert("L"))
    palette = [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)]
    return Image.fromarray(_map_palette_by_luminance(gray, palette))


def _game_boy_pocket(image: Image.Image) -> Image.Image:
    gray = np.array(image.convert("L"))
    palette = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
    return Image.fromarray(_map_palette_by_luminance(gray, palette))


def _game_boy_color(image: Image.Image) -> Image.Image:
    return image.quantize(colors=32).convert("RGB")


def _nes(image: Image.Image) -> Image.Image:
    return image.quantize(colors=16).convert("RGB")


def _snes(image: Image.Image) -> Image.Image:
    return image.quantize(colors=64).convert("RGB")


def _mega_drive(image: Image.Image) -> Image.Image:
    img = image.quantize(colors=32).convert("RGB")
    arr = np.array(img).astype(np.float32)
    arr[..., 0] = np.clip(arr[..., 0] * 1.15, 0, 255)  # Rouge
    arr[..., 2] = np.clip(arr[..., 2] * 1.15, 0, 255)  # Bleu
    return Image.fromarray(arr.astype(np.uint8))


def _crt(image: Image.Image) -> Image.Image:
    arr = np.array(image).astype(np.float32)
    arr[0::2, :, :] *= 0.65  # assombrit une ligne sur deux
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


_FILTER_FUNCS = {
    "Game Boy": _game_boy,
    "Game Boy Pocket": _game_boy_pocket,
    "Game Boy Color": _game_boy_color,
    "NES": _nes,
    "SNES": _snes,
    "Mega Drive": _mega_drive,
    "CRT": _crt,
}


def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
    func = _FILTER_FUNCS.get(filter_name)
    if func is None:
        return image
    return func(image)
