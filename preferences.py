"""
preferences.py
--------------

Fenêtre de préférences d'Image Studio (CTkToplevel).
Ouverte depuis Édition > Préférences.
"""

import customtkinter as ctk

from settings import DEFAULTS

APPEARANCE_LABELS = {"Sombre": "dark", "Clair": "light", "Système": "system"}
APPEARANCE_BY_VALUE = {v: k for k, v in APPEARANCE_LABELS.items()}
HISTORY_CHOICES = ["10", "20", "50"]


class PreferencesWindow(ctk.CTkToplevel):
    def __init__(self, master, settings, icon_path, on_apply):
        super().__init__(master)
        self.title("Préférences")
        self.geometry("420x470")
        self.resizable(False, False)
        self.transient(master)

        self._settings = settings
        self._on_apply = on_apply
        self._icon_path = icon_path

        self.grid_columnconfigure(0, weight=1)
        self._build()
        self._load_values(
            {key: settings.get(key) for key in DEFAULTS}
        )

        # CustomTkinter réécrit l'icône ~200 ms après l'ouverture :
        # on la remet juste après, sinon la fenêtre garde l'icône par défaut.
        self.after(250, self._apply_icon)
        self.after(150, self._safe_grab)

    # ──────────────────────────────────────────
    def _apply_icon(self):
        try:
            if self._icon_path and self._icon_path.exists():
                self.iconbitmap(str(self._icon_path))
        except Exception:
            pass

    def _safe_grab(self):
        try:
            self.grab_set()
            self.focus()
        except Exception:
            pass

    def _section(self, text, row):
        ctk.CTkLabel(
            self, text=text, font=("Arial", 13, "bold")
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(16, 4))

    def _build(self):
        # ── Apparence ──
        self._section("Apparence", 0)
        self.appearance_var = ctk.StringVar()
        ctk.CTkSegmentedButton(
            self,
            values=list(APPEARANCE_LABELS.keys()),
            variable=self.appearance_var,
        ).grid(row=1, column=0, sticky="ew", padx=20)

        # ── Pixelisation ──
        self._section("Pixelisation", 2)
        self.default_pixel_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.default_pixel_label.grid(row=3, column=0, sticky="w", padx=20)
        self.default_pixel_slider = ctk.CTkSlider(
            self, from_=0, to=95, number_of_steps=95,
            command=self._on_default_pixel,
        )
        self.default_pixel_slider.grid(row=4, column=0, sticky="ew", padx=20, pady=(4, 8))

        self.live_var = ctk.BooleanVar()
        ctk.CTkSwitch(
            self,
            text="Rendu en direct pendant le glissement du slider",
            variable=self.live_var,
        ).grid(row=5, column=0, sticky="w", padx=20)

        # ── Export ──
        self._section("Export JPEG", 6)
        self.jpeg_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.jpeg_label.grid(row=7, column=0, sticky="w", padx=20)
        self.jpeg_slider = ctk.CTkSlider(
            self, from_=60, to=100, number_of_steps=40,
            command=self._on_jpeg,
        )
        self.jpeg_slider.grid(row=8, column=0, sticky="ew", padx=20, pady=(4, 0))

        # ── Historique ──
        self._section("Historique Annuler / Rétablir", 9)
        self.history_var = ctk.StringVar()
        ctk.CTkSegmentedButton(
            self, values=HISTORY_CHOICES, variable=self.history_var,
        ).grid(row=10, column=0, sticky="ew", padx=20)

        # ── Boutons ──
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=11, column=0, sticky="ew", padx=20, pady=(24, 16))
        buttons.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            buttons, text="Valeurs par défaut", width=130,
            fg_color="transparent", border_width=1,
            text_color=("gray70", "gray70"),
            command=lambda: self._load_values(dict(DEFAULTS)),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            buttons, text="Annuler", width=90,
            fg_color="transparent", border_width=1,
            text_color=("gray70", "gray70"),
            command=self.destroy,
        ).grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(
            buttons, text="Enregistrer", width=110,
            command=self._save,
        ).grid(row=0, column=2)

    # ──────────────────────────────────────────
    def _on_default_pixel(self, value):
        self.default_pixel_label.configure(
            text=f"Intensité au chargement d'une image : {int(value)}"
        )

    def _on_jpeg(self, value):
        self.jpeg_label.configure(text=f"Qualité : {int(value)}")

    def _load_values(self, values):
        self.appearance_var.set(APPEARANCE_BY_VALUE.get(values["appearance"], "Sombre"))
        self.default_pixel_slider.set(values["default_pixel"])
        self._on_default_pixel(values["default_pixel"])
        self.live_var.set(bool(values["live_preview"]))
        self.jpeg_slider.set(values["jpeg_quality"])
        self._on_jpeg(values["jpeg_quality"])
        self.history_var.set(str(values["max_history"]))

    def _save(self):
        history = self.history_var.get()
        self._settings.update(
            appearance=APPEARANCE_LABELS.get(self.appearance_var.get(), "dark"),
            default_pixel=int(self.default_pixel_slider.get()),
            live_preview=bool(self.live_var.get()),
            jpeg_quality=int(self.jpeg_slider.get()),
            max_history=int(history) if history.isdigit() else DEFAULTS["max_history"],
        )
        self._settings.save()
        self._on_apply()
        self.destroy()
