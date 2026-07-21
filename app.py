"""
app.py
------
Application principale : upscaler IA + éditeur de filtres rétro
avec menu complet, sidebar à onglets, historique Annuler/Rétablir,
transformations image, zoom et gestion des fichiers récents.
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path
from collections import deque

import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image

from menu import build_menu
from sidebar import Sidebar
from filters import pixelate, apply_filter
from upscaler import upscale_image_obj, get_backend_name

MAX_HISTORY = 20
MAX_RECENT  = 8
ZOOM_STEPS  = [0.25, 0.33, 0.5, 0.67, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0]


def _base_dir() -> Path:
    """Chemin de base des ressources (fonctionne en dev ET en exe)."""
    env = os.environ.get("IMAGESTUDIO_BASE")
    if env:
        return Path(env)
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Image Studio — Upscale & Style")
        self.geometry("1300x800")
        self.minsize(1050, 650)

        # ── État image ──────────────────────────────────────────
        self.original_image: Image.Image | None = None
        self.working_image:  Image.Image | None = None
        self.modified_image: Image.Image | None = None
        self.current_path:   str | None = None

        self.pixel_amount   = 0
        self.current_filter = "Aucun"

        # ── Zoom ────────────────────────────────────────────────
        self._zoom_level = 1.0   # 1.0 = ajusté à la fenêtre

        # ── Historique Annuler / Rétablir ───────────────────────
        self._undo_stack: deque[Image.Image] = deque(maxlen=MAX_HISTORY)
        self._redo_stack: deque[Image.Image] = deque(maxlen=MAX_HISTORY)

        # ── Fichiers récents ────────────────────────────────────
        self._recent_files: list[str] = []

        # ── Divers ──────────────────────────────────────────────
        self._ctk_preview = None
        self._fullscreen  = False

        self._build_layout()
        self._build_menu()
        self.sidebar.set_backend_label(get_backend_name())

        # ── Icône de la fenêtre ─────────────────────────────────
        # Fonctionne en développement ET dans l'exe PyInstaller.
        # Pour changer l'icône : remplace assets/icon.ico
        icon_path = _base_dir() / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass   # Certaines versions Linux ne supportent pas .ico

    # ═══════════════════════════════════════════════════════════
    # Layout
    # ═══════════════════════════════════════════════════════════
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(
            self,
            on_upscale=self.start_upscale,
            on_pixelate_change=self.on_pixelate_change,
            on_filter_change=self.on_filter_change,
            on_reset=self.reset_image,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # ── Toolbar ─────────────────────────────────────────────
        toolbar = ctk.CTkFrame(main, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        ctk.CTkButton(
            toolbar, text="📂  Ouvrir", command=self.open_image, width=130
        ).grid(row=0, column=0, padx=(0, 6))

        self.save_btn = ctk.CTkButton(
            toolbar, text="💾  Enregistrer", command=self.save_image,
            state="disabled", width=140,
            fg_color="#2a7a2a", hover_color="#1d561d"
        )
        self.save_btn.grid(row=0, column=1, padx=(0, 16))

        ctk.CTkButton(toolbar, text="↩", command=self.undo, width=36).grid(row=0, column=2, padx=2)
        ctk.CTkButton(toolbar, text="↪", command=self.redo, width=36).grid(row=0, column=3, padx=2)

        ctk.CTkButton(toolbar, text="−", command=self.zoom_out, width=36).grid(row=0, column=4, padx=(16, 2))
        self._zoom_label = ctk.CTkLabel(toolbar, text="Ajusté", width=52, font=("Arial", 11))
        self._zoom_label.grid(row=0, column=5)
        ctk.CTkButton(toolbar, text="+", command=self.zoom_in, width=36).grid(row=0, column=6, padx=2)

        # ── Zone d'aperçu ────────────────────────────────────────
        self.preview_frame = ctk.CTkFrame(main)
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Aucune image chargée")
        self.preview_label.grid(row=0, column=0, sticky="nsew")

        # ── Barre de statut ──────────────────────────────────────
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        bottom.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(bottom)
        self.progress.grid(row=0, column=0, sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            bottom, text="Prêt.", font=("Arial", 11), text_color="gray"
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.bind("<Configure>", self._on_resize)

    def _build_menu(self):
        build_menu(
            self,
            on_open=self.open_image,
            on_open_recent=self.open_recent,
            on_save=self.save_image,
            on_save_as=self.save_image_as,
            on_export=self.export_image,
            on_quit=self.quit,
            on_undo=self.undo,
            on_redo=self.redo,
            on_reset=self.reset_image,
            on_preferences=self._show_preferences,
            on_rotate_cw=lambda: self.rotate(90),
            on_rotate_ccw=lambda: self.rotate(-90),
            on_flip_h=lambda: self.flip("horizontal"),
            on_flip_v=lambda: self.flip("vertical"),
            on_resize=self.resize_dialog,
            on_crop=lambda: self._set_status("Recadrage : à venir."),
            on_zoom_in=self.zoom_in,
            on_zoom_out=self.zoom_out,
            on_zoom_reset=self.zoom_reset,
            on_fullscreen=self.toggle_fullscreen,
            on_about=self._show_about,
            on_doc=lambda: webbrowser.open("https://github.com/xinntao/Real-ESRGAN"),
            on_update=lambda: self._set_status("Vérification des mises à jour… (non implémenté)"),
        )

    # ═══════════════════════════════════════════════════════════
    # Fichiers
    # ═══════════════════════════════════════════════════════════
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if path:
            self._load_image(path)

    def open_recent(self, path: str):
        self._load_image(path)

    def _load_image(self, path: str):
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            return

        self.current_path   = path
        self.original_image = img
        self.working_image  = img.copy()
        self.pixel_amount   = 0
        self.current_filter = "Aucun"

        self._undo_stack.clear()
        self._redo_stack.clear()
        self.sidebar.reset_controls()
        self._add_recent(path)
        self._render()
        self.save_btn.configure(state="normal")
        self._set_status(f"Chargé : {Path(path).name}  ({img.width}×{img.height})")

    def _add_recent(self, path: str):
        if path in self._recent_files:
            self._recent_files.remove(path)
        self._recent_files.insert(0, path)
        self._recent_files = self._recent_files[:MAX_RECENT]

    def save_image(self):
        if self.current_path:
            try:
                self.modified_image.save(self.current_path)
                self._set_status(f"✅ Enregistré : {Path(self.current_path).name}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        else:
            self.save_image_as()

    def save_image_as(self):
        if self.modified_image is None:
            return
        default = (Path(self.current_path).stem + "_edited.png") if self.current_path else "image.png"
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("WEBP", "*.webp")],
            initialfile=default
        )
        if not path:
            return
        try:
            self.modified_image.save(path)
            self.current_path = path
            self._set_status(f"✅ Enregistré sous : {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def export_image(self):
        if self.modified_image is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG haute qualité", "*.jpg"), ("PNG sans perte", "*.png"), ("WEBP", "*.webp")],
            initialfile="export.jpg"
        )
        if not path:
            return
        try:
            ext = Path(path).suffix.lower()
            if ext in (".jpg", ".jpeg"):
                self.modified_image.save(path, "JPEG", quality=95, subsampling=0)
            else:
                self.modified_image.save(path)
            self._set_status(f"✅ Exporté : {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ═══════════════════════════════════════════════════════════
    # Historique Annuler / Rétablir
    # ═══════════════════════════════════════════════════════════
    def _push_history(self):
        if self.working_image is not None:
            self._undo_stack.append(self.working_image.copy())
            self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            self._set_status("Rien à annuler.")
            return
        self._redo_stack.append(self.working_image.copy())
        self.working_image = self._undo_stack.pop()
        self._render()
        self._set_status(f"Annulé. ({len(self._undo_stack)} restant(s))")

    def redo(self):
        if not self._redo_stack:
            self._set_status("Rien à rétablir.")
            return
        self._undo_stack.append(self.working_image.copy())
        self.working_image = self._redo_stack.pop()
        self._render()
        self._set_status("Rétabli.")

    # ═══════════════════════════════════════════════════════════
    # Transformations image
    # ═══════════════════════════════════════════════════════════
    def rotate(self, degrees: int):
        if self.working_image is None:
            return
        self._push_history()
        self.working_image = self.working_image.rotate(-degrees, expand=True)
        self._render()
        self._set_status(f"Rotation {'horaire' if degrees > 0 else 'antihoraire'} 90°")

    def flip(self, direction: str):
        if self.working_image is None:
            return
        self._push_history()
        if direction == "horizontal":
            self.working_image = self.working_image.transpose(Image.FLIP_LEFT_RIGHT)
            self._set_status("Retourné horizontalement.")
        else:
            self.working_image = self.working_image.transpose(Image.FLIP_TOP_BOTTOM)
            self._set_status("Retourné verticalement.")
        self._render()

    def resize_dialog(self):
        if self.working_image is None:
            return
        w, h = self.working_image.size
        new_w = simpledialog.askinteger(
            "Redimensionner",
            f"Largeur actuelle : {w} px\nNouvelle largeur (px) :",
            minvalue=1, maxvalue=16000, initialvalue=w
        )
        if new_w is None:
            return
        new_h = int(h * (new_w / w))
        self._push_history()
        self.working_image = self.working_image.resize((new_w, new_h), Image.LANCZOS)
        self._render()
        self._set_status(f"Redimensionné : {new_w}×{new_h} px")

    def reset_image(self):
        if self.original_image is None:
            return
        self._push_history()
        self.working_image  = self.original_image.copy()
        self.pixel_amount   = 0
        self.current_filter = "Aucun"
        self.sidebar.reset_controls()
        self._render()
        self._set_status("Image réinitialisée.")

    # ═══════════════════════════════════════════════════════════
    # Effets
    # ═══════════════════════════════════════════════════════════
    def on_pixelate_change(self, amount: int):
        self.pixel_amount = amount
        self._render()

    def on_filter_change(self, filter_name: str):
        self.current_filter = filter_name
        self._render()

    def _render(self):
        if self.working_image is None:
            return
        img = self.working_image.copy()
        img = pixelate(img, self.pixel_amount)
        img = apply_filter(img, self.current_filter)
        self.modified_image = img
        self._update_preview(img)

    # ═══════════════════════════════════════════════════════════
    # Upscale IA
    # ═══════════════════════════════════════════════════════════
    def start_upscale(self, scale: int):
        if self.working_image is None:
            messagebox.showwarning("Aucune image", "Ouvre d'abord une image.")
            return
        self._push_history()
        self.sidebar.set_upscale_enabled(False)
        self.progress.set(0)
        self._set_status(f"Amélioration ×{scale} en cours…")
        source = self.working_image.copy()

        def run():
            try:
                result = upscale_image_obj(source, scale=scale, callback=self._on_progress)
                self.after(0, self._on_upscale_done, result)
            except Exception as e:
                self.after(0, self._on_upscale_error, str(e))

        threading.Thread(target=run, daemon=True).start()

    def _on_progress(self, value: float):
        self.after(0, self.progress.set, value)
        self.after(0, self._set_status, f"Amélioration… {int(value * 100)}%")

    def _on_upscale_done(self, result: Image.Image):
        self.working_image = result
        self.progress.set(1.0)
        self.sidebar.set_upscale_enabled(True)
        self._render()
        self._set_status(f"✅ Amélioration terminée — {result.width}×{result.height}")

    def _on_upscale_error(self, msg: str):
        self.progress.set(0)
        self.sidebar.set_upscale_enabled(True)
        self._set_status("❌ Erreur lors de l'amélioration")
        messagebox.showerror("Erreur", msg)

    # ═══════════════════════════════════════════════════════════
    # Zoom
    # ═══════════════════════════════════════════════════════════
    def zoom_in(self):
        idx = self._nearest_zoom_idx()
        if idx < len(ZOOM_STEPS) - 1:
            self._zoom_level = ZOOM_STEPS[idx + 1]
            self._refresh_zoom()

    def zoom_out(self):
        idx = self._nearest_zoom_idx()
        if idx > 0:
            self._zoom_level = ZOOM_STEPS[idx - 1]
            self._refresh_zoom()

    def zoom_reset(self):
        self._zoom_level = 1.0
        self._zoom_label.configure(text="Ajusté")
        if self.modified_image:
            self._update_preview(self.modified_image)

    def _nearest_zoom_idx(self) -> int:
        return min(range(len(ZOOM_STEPS)), key=lambda i: abs(ZOOM_STEPS[i] - self._zoom_level))

    def _refresh_zoom(self):
        self._zoom_label.configure(text=f"{int(self._zoom_level * 100)}%")
        if self.modified_image:
            self._update_preview(self.modified_image)

    # ═══════════════════════════════════════════════════════════
    # Plein écran
    # ═══════════════════════════════════════════════════════════
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    # ═══════════════════════════════════════════════════════════
    # Aperçu
    # ═══════════════════════════════════════════════════════════
    def _update_preview(self, img: Image.Image):
        frame_w = max(self.preview_frame.winfo_width(),  400)
        frame_h = max(self.preview_frame.winfo_height(), 300)

        if self._zoom_level == 1.0:
            preview = img.copy()
            preview.thumbnail((frame_w - 20, frame_h - 20))
        else:
            w = int(img.width  * self._zoom_level)
            h = int(img.height * self._zoom_level)
            preview = img.resize((max(1, w), max(1, h)), Image.LANCZOS)

        self._ctk_preview = ctk.CTkImage(
            light_image=preview, dark_image=preview, size=preview.size
        )
        self.preview_label.configure(image=self._ctk_preview, text="")

    def _on_resize(self, event):
        if event.widget is self and self.modified_image is not None:
            self._update_preview(self.modified_image)

    # ═══════════════════════════════════════════════════════════
    # Divers
    # ═══════════════════════════════════════════════════════════
    def _set_status(self, text: str):
        self.status_label.configure(text=text)

    def _show_preferences(self):
        messagebox.showinfo("Préférences", "Panneau de préférences — à implémenter.")

    def _show_about(self):
        messagebox.showinfo(
            "À propos",
            "Image Studio\n\n"
            "Upscaling IA + filtres rétro + pixelisation,\n"
            "dans un seul outil.\n\n"
            f"Backend upscale : {get_backend_name()}\n\n"
            "© 2026 — Développé par Xenebia (tous les scripts) & Ewan (filtres, pixelation)"
        )
