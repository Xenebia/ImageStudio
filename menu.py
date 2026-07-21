"""
menu.py
-------
Barre de menu complète (Fichier / Édition / Image / Affichage / Aide).
"""

import tkinter as tk


def build_menu(
    root,
    on_open,
    on_open_recent,
    on_save,
    on_save_as,
    on_export,
    on_quit,
    on_undo,
    on_redo,
    on_reset,
    on_preferences,
    on_rotate_cw,
    on_rotate_ccw,
    on_flip_h,
    on_flip_v,
    on_resize,
    on_crop,
    on_zoom_in,
    on_zoom_out,
    on_zoom_reset,
    on_fullscreen,
    on_about,
    on_doc,
    on_update,
):
    menubar = tk.Menu(root)

    # ── Fichier ──────────────────────────────
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Ouvrir...", command=on_open, accelerator="Ctrl+O")
    file_menu.add_cascade(label="Ouvrir récent", menu=_build_recent_menu(file_menu, on_open_recent))
    file_menu.add_separator()
    file_menu.add_command(label="Enregistrer", command=on_save, accelerator="Ctrl+S")
    file_menu.add_command(label="Enregistrer sous...", command=on_save_as, accelerator="Ctrl+Shift+S")
    file_menu.add_command(label="Exporter...", command=on_export, accelerator="Ctrl+E")
    file_menu.add_separator()
    file_menu.add_command(label="Quitter", command=on_quit, accelerator="Alt+F4")
    menubar.add_cascade(label="Fichier", menu=file_menu)

    # ── Édition ──────────────────────────────
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label="Annuler", command=on_undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Rétablir", command=on_redo, accelerator="Ctrl+Y")
    edit_menu.add_separator()
    edit_menu.add_command(label="Réinitialiser", command=on_reset)
    edit_menu.add_command(label="Préférences", command=on_preferences)
    menubar.add_cascade(label="Édition", menu=edit_menu)

    # ── Image ────────────────────────────────
    image_menu = tk.Menu(menubar, tearoff=0)

    rotation_menu = tk.Menu(image_menu, tearoff=0)
    rotation_menu.add_command(label="90° dans le sens horaire",  command=on_rotate_cw)
    rotation_menu.add_command(label="90° dans le sens antihoraire", command=on_rotate_ccw)
    image_menu.add_cascade(label="Rotation", menu=rotation_menu)

    flip_menu = tk.Menu(image_menu, tearoff=0)
    flip_menu.add_command(label="Horizontal", command=on_flip_h)
    flip_menu.add_command(label="Vertical",   command=on_flip_v)
    image_menu.add_cascade(label="Retourner", menu=flip_menu)

    image_menu.add_command(label="Redimensionner...", command=on_resize, accelerator="Ctrl+R")
    image_menu.add_command(label="Recadrer...",       command=on_crop,   accelerator="Ctrl+Shift+C")
    menubar.add_cascade(label="Image", menu=image_menu)

    # ── Affichage ────────────────────────────
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(label="Zoom +",       command=on_zoom_in,    accelerator="Ctrl++")
    view_menu.add_command(label="Zoom -",       command=on_zoom_out,   accelerator="Ctrl+-")
    view_menu.add_command(label="Taille réelle",command=on_zoom_reset, accelerator="Ctrl+0")
    view_menu.add_separator()
    view_menu.add_command(label="Plein écran",  command=on_fullscreen, accelerator="F11")
    menubar.add_cascade(label="Affichage", menu=view_menu)

    # ── Aide ─────────────────────────────────
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Documentation",          command=on_doc)
    help_menu.add_command(label="Vérifier les mises à jour", command=on_update)
    help_menu.add_separator()
    help_menu.add_command(label="À propos",               command=on_about)
    menubar.add_cascade(label="Aide", menu=help_menu)

    root.config(menu=menubar)

    # ── Raccourcis clavier ───────────────────
    root.bind("<Control-o>",       lambda e: on_open())
    root.bind("<Control-s>",       lambda e: on_save())
    root.bind("<Control-S>",       lambda e: on_save_as())
    root.bind("<Control-e>",       lambda e: on_export())
    root.bind("<Control-z>",       lambda e: on_undo())
    root.bind("<Control-y>",       lambda e: on_redo())
    root.bind("<Control-r>",       lambda e: on_resize())
    root.bind("<Control-C>",       lambda e: on_crop())
    root.bind("<Control-plus>",    lambda e: on_zoom_in())
    root.bind("<Control-minus>",   lambda e: on_zoom_out())
    root.bind("<Control-0>",       lambda e: on_zoom_reset())
    root.bind("<F11>",             lambda e: on_fullscreen())

    return menubar


def _build_recent_menu(parent, on_open_recent):
    """Sous-menu 'Ouvrir récent' — peuplé dynamiquement par App."""
    recent_menu = tk.Menu(parent, tearoff=0)
    recent_menu.add_command(label="(aucun fichier récent)", state="disabled")
    return recent_menu
