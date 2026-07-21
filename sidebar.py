"""
sidebar.py
----------
Barre latérale à onglets : Agrandir / Pixeliser / Style.
Chaque onglet expose ses propres contrôles ; les callbacks remontent
vers l'app principale via les fonctions passées au constructeur.
"""

import customtkinter as ctk
from filters import FILTER_NAMES


class Sidebar(ctk.CTkFrame):

    TABS = ["Agrandir", "Pixeliser", "Style"]

    def __init__(
        self,
        master,
        on_upscale,
        on_pixelate_change,
        on_filter_change,
        on_reset,
        **kwargs
    ):
        super().__init__(master, width=300, **kwargs)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._on_upscale = on_upscale
        self._on_pixelate_change = on_pixelate_change
        self._on_filter_change = on_filter_change
        self._on_reset = on_reset

        self._active_tab = self.TABS[0]

        self._build_header()
        self._build_tab_buttons()
        self._build_panels()
        self._show_tab(self.TABS[0])

    # ──────────────────────────────────────────
    def _build_header(self):
        ctk.CTkLabel(
            self, text="OUTILS", font=("Arial", 16, "bold")
        ).grid(row=0, column=0, pady=(16, 8), padx=16, sticky="w")

    def _build_tab_buttons(self):
        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        tab_frame.grid_columnconfigure(tuple(range(len(self.TABS))), weight=1)

        self._tab_buttons = {}
        for i, tab in enumerate(self.TABS):
            btn = ctk.CTkButton(
                tab_frame,
                text=tab,
                command=lambda t=tab: self._show_tab(t),
                fg_color="transparent",
                border_width=1,
                corner_radius=6,
                width=0,
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
            self._tab_buttons[tab] = btn

    def _build_panels(self):
        self._panel_container = ctk.CTkFrame(self, fg_color="transparent")
        self._panel_container.grid(row=2, column=0, sticky="nsew", padx=16, pady=4)
        self._panel_container.grid_columnconfigure(0, weight=1)

        self._panels = {
            "Agrandir": self._build_upscale_panel(self._panel_container),
            "Pixeliser": self._build_pixelate_panel(self._panel_container),
            "Style": self._build_style_panel(self._panel_container),
        }
        for panel in self._panels.values():
            panel.grid(row=0, column=0, sticky="nsew")

        # ── Bouton reset, toujours visible en bas ──
        ctk.CTkButton(
            self,
            text="↺  Réinitialiser",
            command=self._on_reset,
            fg_color="transparent",
            border_width=1,
            text_color=("gray70", "gray70")
        ).grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 16))

    def _show_tab(self, tab: str):
        self._active_tab = tab
        for name, btn in self._tab_buttons.items():
            if name == tab:
                btn.configure(fg_color="#1f6aa5", border_width=0)
            else:
                btn.configure(fg_color="transparent", border_width=1)
        self._panels[tab].tkraise()

    # ──────────────────────────────────────────
    # Onglet : Agrandir (upscale)
    # ──────────────────────────────────────────
    def _build_upscale_panel(self, master):
        panel = ctk.CTkFrame(master, fg_color="transparent")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Améliore la résolution de l'image avec l'IA ou un\nré-échantillonnage haute qualité.",
            font=("Arial", 11),
            text_color="gray",
            justify="left"
        ).grid(row=0, column=0, sticky="w", pady=(8, 16))

        ctk.CTkLabel(panel, text="Facteur d'agrandissement", font=("Arial", 12)).grid(
            row=1, column=0, sticky="w"
        )

        self.scale_var = ctk.StringVar(value="2")
        scale_frame = ctk.CTkFrame(panel, fg_color="transparent")
        scale_frame.grid(row=2, column=0, sticky="ew", pady=(6, 16))
        for i, val in enumerate(["2", "4"]):
            ctk.CTkRadioButton(
                scale_frame, text=f"×{val}", variable=self.scale_var, value=val
            ).grid(row=0, column=i, padx=(0, 20))

        self.upscale_btn = ctk.CTkButton(
            panel,
            text="✨  Lancer l'amélioration",
            command=lambda: self._on_upscale(int(self.scale_var.get())),
            fg_color="#1f6aa5",
            hover_color="#144f7a"
        )
        self.upscale_btn.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        self.backend_label = ctk.CTkLabel(
            panel, text="", font=("Arial", 10), text_color="gray"
        )
        self.backend_label.grid(row=4, column=0, sticky="w")

        return panel

    # ──────────────────────────────────────────
    # Onglet : Pixeliser
    # ──────────────────────────────────────────
    def _build_pixelate_panel(self, master):
        panel = ctk.CTkFrame(master, fg_color="transparent")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Réduit l'image en blocs pour un effet pixel art.",
            font=("Arial", 11),
            text_color="gray",
            justify="left"
        ).grid(row=0, column=0, sticky="w", pady=(8, 16))

        self._pixel_value_label = ctk.CTkLabel(panel, text="Intensité : 0", font=("Arial", 12))
        self._pixel_value_label.grid(row=1, column=0, sticky="w")

        self.pixel_slider = ctk.CTkSlider(
            panel,
            from_=0,
            to=95,
            number_of_steps=95,
            command=self._on_pixel_slider
        )
        self.pixel_slider.set(0)
        self.pixel_slider.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        return panel

    def _on_pixel_slider(self, value):
        value = int(value)
        self._pixel_value_label.configure(text=f"Intensité : {value}")
        self._on_pixelate_change(value)

    # ──────────────────────────────────────────
    # Onglet : Style (filtres rétro)
    # ──────────────────────────────────────────
    def _build_style_panel(self, master):
        panel = ctk.CTkFrame(master, fg_color="transparent")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Applique une palette de couleurs rétro façon\nconsole vintage.",
            font=("Arial", 11),
            text_color="gray",
            justify="left"
        ).grid(row=0, column=0, sticky="w", pady=(8, 16))

        ctk.CTkLabel(panel, text="Filtre", font=("Arial", 12)).grid(row=1, column=0, sticky="w")

        self.filter_var = ctk.StringVar(value=FILTER_NAMES[0])
        self.filter_menu = ctk.CTkOptionMenu(
            panel,
            values=FILTER_NAMES,
            variable=self.filter_var,
            command=self._on_filter_change
        )
        self.filter_menu.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        return panel

    # ──────────────────────────────────────────
    def set_backend_label(self, text: str):
        self.backend_label.configure(text=f"Backend : {text}")

    def set_upscale_enabled(self, enabled: bool):
        self.upscale_btn.configure(state="normal" if enabled else "disabled")

    def reset_controls(self):
        self.pixel_slider.set(0)
        self._pixel_value_label.configure(text="Intensité : 0")
        self.filter_var.set(FILTER_NAMES[0])
