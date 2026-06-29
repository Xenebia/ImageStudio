import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image

from upscaler import upscale_image, get_backend_name


class ImagePanel(ctk.CTkFrame):
    """Panneau affichant une image avec son label et ses dimensions."""

    MAX_W = 500
    MAX_H = 480

    def __init__(self, master, label_text: str, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._label_text = label_text
        self._label = ctk.CTkLabel(self, text=label_text, font=("Arial", 14, "bold"))
        self._label.grid(row=0, column=0, pady=(10, 4))

        self._image_label = ctk.CTkLabel(self, text="")
        self._image_label.grid(row=1, column=0, padx=10, pady=4, sticky="nsew")

        self._info = ctk.CTkLabel(self, text="—", font=("Arial", 11), text_color="gray")
        self._info.grid(row=2, column=0, pady=(4, 10))

        self._ctk_image = None  # keep reference

    def show(self, img: Image.Image):
        w, h = img.size
        ratio = min(self.MAX_W / w, self.MAX_H / h, 1.0)
        disp_w, disp_h = int(w * ratio), int(h * ratio)

        self._ctk_image = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(disp_w, disp_h)
        )
        self._image_label.configure(image=self._ctk_image, text="")
        self._info.configure(text=f"{w} × {h} px")

    def clear(self):
        self._image_label.configure(image=None, text="")
        self._info.configure(text="—")
        self._ctk_image = None


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AI Image Upscaler")
        self.geometry("1200x750")
        self.minsize(1000, 620)

        self._input_path: str | None = None
        self._output_path: str | None = None
        self._result_image: Image.Image | None = None

        self._build_ui()

    # ──────────────────────────────────────────
    # Construction de l'interface
    # ──────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Titre ──
        ctk.CTkLabel(
            self,
            text="AI IMAGE UPSCALER",
            font=("Arial", 28, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(20, 4))

        # Backend info
        self._backend_label = ctk.CTkLabel(
            self,
            text=f"Backend : {get_backend_name()}",
            font=("Arial", 11),
            text_color="gray"
        )
        self._backend_label.grid(row=1, column=0, columnspan=2, pady=(0, 6))

        # ── Barre d'outils ──
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=2, column=0, columnspan=2, pady=6)

        self._open_btn = ctk.CTkButton(
            toolbar,
            text="📂  Choisir une image",
            command=self._open_image,
            width=180
        )
        self._open_btn.grid(row=0, column=0, padx=10)

        ctk.CTkLabel(toolbar, text="Facteur ×", font=("Arial", 12)).grid(row=0, column=1, padx=(10, 2))
        self._scale_var = ctk.StringVar(value="4")
        self._scale_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["2", "4"],
            variable=self._scale_var,
            width=70
        )
        self._scale_menu.grid(row=0, column=2, padx=(2, 10))

        self._start_btn = ctk.CTkButton(
            toolbar,
            text="✨  Lancer l'amélioration",
            command=self._start_upscale,
            state="disabled",
            width=200,
            fg_color="#1f6aa5",
            hover_color="#144f7a"
        )
        self._start_btn.grid(row=0, column=3, padx=10)

        self._save_btn = ctk.CTkButton(
            toolbar,
            text="💾  Sauvegarder",
            command=self._save_output,
            state="disabled",
            width=150,
            fg_color="#2a7a2a",
            hover_color="#1d561d"
        )
        self._save_btn.grid(row=0, column=4, padx=10)

        # ── Panneaux images ──
        panels = ctk.CTkFrame(self, fg_color="transparent")
        panels.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        panels.grid_columnconfigure((0, 1), weight=1)
        panels.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._before_panel = ImagePanel(panels, "Avant")
        self._before_panel.grid(row=0, column=0, padx=10, sticky="nsew")

        self._after_panel = ImagePanel(panels, "Après")
        self._after_panel.grid(row=0, column=1, padx=10, sticky="nsew")

        # ── Barre de progression ──
        self._progress = ctk.CTkProgressBar(self)
        self._progress.grid(row=4, column=0, columnspan=2, sticky="ew", padx=30, pady=4)
        self._progress.set(0)

        self._status_label = ctk.CTkLabel(
            self,
            text="Prêt — choisissez une image pour commencer.",
            font=("Arial", 12),
            text_color="gray"
        )
        self._status_label.grid(row=5, column=0, columnspan=2, pady=(0, 16))

    # ──────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────
    def _open_image(self):
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff")]
        )
        if not file:
            return

        self._input_path = file
        self._output_path = None
        self._result_image = None

        img = Image.open(file)
        self._before_panel.show(img)
        self._after_panel.clear()

        self._start_btn.configure(state="normal")
        self._save_btn.configure(state="disabled")
        self._progress.set(0)
        self._set_status(f"Image chargée : {Path(file).name}")

    def _start_upscale(self):
        if not self._input_path:
            return

        self._start_btn.configure(state="disabled")
        self._open_btn.configure(state="disabled")
        self._save_btn.configure(state="disabled")
        self._progress.set(0)
        self._set_status("Traitement en cours…")

        scale = int(self._scale_var.get())
        output_dir = str(Path(self._input_path).parent / "output")

        def run():
            try:
                out = upscale_image(
                    self._input_path,
                    scale=scale,
                    output_dir=output_dir,
                    callback=self._on_progress
                )
                self.after(0, self._on_done, out)
            except Exception as e:
                self.after(0, self._on_error, str(e))

        threading.Thread(target=run, daemon=True).start()

    def _save_output(self):
        if not self._result_image:
            return

        dest = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("Tous", "*.*")
            ],
            initialfile=Path(self._output_path).name if self._output_path else "upscaled.png"
        )
        if not dest:
            return

        ext = Path(dest).suffix.lower()
        if ext in (".jpg", ".jpeg"):
            self._result_image.save(dest, "JPEG", quality=95, subsampling=0)
        else:
            self._result_image.save(dest, "PNG")

        self._set_status(f"✅ Sauvegardé : {Path(dest).name}")

    # ──────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────
    def _on_progress(self, value: float):
        self.after(0, self._progress.set, value)
        percent = int(value * 100)
        self.after(0, self._set_status, f"Traitement… {percent}%")

    def _on_done(self, output_path: str):
        self._output_path = output_path
        self._result_image = Image.open(output_path)
        self._after_panel.show(self._result_image)

        self._progress.set(1.0)
        self._set_status(f"✅ Terminé ! → {Path(output_path).name}")
        self._start_btn.configure(state="normal")
        self._open_btn.configure(state="normal")
        self._save_btn.configure(state="normal")

    def _on_error(self, msg: str):
        self._progress.set(0)
        self._set_status("❌ Erreur")
        self._start_btn.configure(state="normal")
        self._open_btn.configure(state="normal")
        messagebox.showerror("Erreur lors de l'upscaling", msg)

    def _set_status(self, text: str):
        self._status_label.configure(text=text)

    # ──────────────────────────────────────────
    # Redimensionnement réactif des panneaux
    # ──────────────────────────────────────────
    def mainloop(self, n=0):
        self.bind("<Configure>", self._on_resize)
        super().mainloop(n)

    def _on_resize(self, event):
        # Re-affiche les images si la fenêtre change de taille
        if event.widget is not self:
            return
        # (optionnel : re-render les CTkImage — skippé pour garder simple)
