#!/usr/bin/env python3
"""
JPG → PDF Konverter
Voraussetzung:  pip install pillow
Start:          python jpg_zu_pdf.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps

# --- Farben (dunkel / gold) ---
BG = "#14110d"
PANEL = "#1e1a14"
GOLD = "#d4af37"
TEXT = "#eadfc4"

# A4 bei 150 dpi
A4_PX = (1240, 1754)


def bild_laden(pfad):
    """Öffnet ein Bild, korrigiert EXIF-Drehung und wandelt in RGB."""
    img = Image.open(pfad)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def auf_a4_setzen(img, rand=60):
    """Skaliert das Bild proportional auf eine weiße A4-Seite."""
    seite = Image.new("RGB", A4_PX, "white")
    # Querformat-Bilder auf Querformat-Seite
    if img.width > img.height:
        seite = Image.new("RGB", (A4_PX[1], A4_PX[0]), "white")
    max_w = seite.width - 2 * rand
    max_h = seite.height - 2 * rand
    img = img.copy()
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    x = (seite.width - img.width) // 2
    y = (seite.height - img.height) // 2
    seite.paste(img, (x, y))
    return seite


def pdf_erstellen(pfade, ziel, a4=False, qualitaet=90):
    seiten = []
    for p in pfade:
        img = bild_laden(p)
        seiten.append(auf_a4_setzen(img) if a4 else img)
    erste, rest = seiten[0], seiten[1:]
    erste.save(
        ziel,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=rest,
        quality=qualitaet,
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JPG → PDF")
        self.geometry("620x520")
        self.configure(bg=BG)
        self.minsize(520, 420)

        self.dateien = []
        self.a4 = tk.BooleanVar(value=False)
        self.qualitaet = tk.IntVar(value=90)

        self._stil()
        self._aufbau()

    def _stil(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=TEXT)
        s.configure("TCheckbutton", background=BG, foreground=TEXT)
        s.map("TCheckbutton", background=[("active", BG)])
        s.configure("TButton", background=PANEL, foreground=GOLD,
                    bordercolor=GOLD, padding=6)
        s.map("TButton", background=[("active", "#2a241a")])
        s.configure("Gold.TButton", background=GOLD, foreground="#14110d",
                    font=("Segoe UI", 10, "bold"), padding=8)
        s.map("Gold.TButton", background=[("active", "#e6c455")])
        s.configure("Horizontal.TScale", background=BG)

    def _aufbau(self):
        kopf = ttk.Label(self, text="JPG → PDF", foreground=GOLD,
                         font=("Segoe UI", 18, "bold"))
        kopf.pack(pady=(14, 4))
        ttk.Label(self, text="Bilder hinzufügen, Reihenfolge anpassen, PDF erstellen."
                  ).pack(pady=(0, 10))

        mitte = ttk.Frame(self)
        mitte.pack(fill="both", expand=True, padx=14)

        self.liste = tk.Listbox(
            mitte, bg=PANEL, fg=TEXT, selectbackground=GOLD,
            selectforeground="#14110d", highlightthickness=1,
            highlightbackground=GOLD, relief="flat", selectmode="extended",
            font=("Segoe UI", 10),
        )
        self.liste.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mitte, command=self.liste.yview)
        sb.pack(side="left", fill="y")
        self.liste.config(yscrollcommand=sb.set)

        knoepfe = ttk.Frame(mitte)
        knoepfe.pack(side="left", padx=(10, 0), fill="y")
        for text, cmd in [
            ("Hinzufügen …", self.hinzufuegen),
            ("Entfernen", self.entfernen),
            ("▲ Nach oben", lambda: self.verschieben(-1)),
            ("▼ Nach unten", lambda: self.verschieben(1)),
            ("Leeren", self.leeren),
        ]:
            ttk.Button(knoepfe, text=text, command=cmd).pack(fill="x", pady=3)

        opt = ttk.Frame(self)
        opt.pack(fill="x", padx=14, pady=10)
        ttk.Checkbutton(opt, text="Auf A4-Seite einpassen",
                        variable=self.a4).pack(anchor="w")
        zeile = ttk.Frame(opt)
        zeile.pack(fill="x", pady=(6, 0))
        ttk.Label(zeile, text="JPEG-Qualität:").pack(side="left")
        ttk.Scale(zeile, from_=40, to=100, variable=self.qualitaet,
                  command=lambda v: self.q_label.config(
                      text=str(int(float(v))))
                  ).pack(side="left", fill="x", expand=True, padx=8)
        self.q_label = ttk.Label(zeile, text="90", width=4)
        self.q_label.pack(side="left")

        ttk.Button(self, text="PDF erstellen", style="Gold.TButton",
                   command=self.erstellen).pack(pady=(0, 6))
        self.status = ttk.Label(self, text="Keine Bilder ausgewählt.")
        self.status.pack(pady=(0, 10))

    # --- Aktionen ---
    def _aktualisieren(self):
        self.liste.delete(0, "end")
        for p in self.dateien:
            self.liste.insert("end", os.path.basename(p))
        self.status.config(text=f"{len(self.dateien)} Bild(er) ausgewählt.")

    def hinzufuegen(self):
        pfade = filedialog.askopenfilenames(
            title="Bilder auswählen",
            filetypes=[("Bilder", "*.jpg *.jpeg *.JPG *.JPEG *.png"),
                       ("Alle Dateien", "*.*")],
        )
        self.dateien.extend(pfade)
        self._aktualisieren()

    def entfernen(self):
        for i in reversed(self.liste.curselection()):
            del self.dateien[i]
        self._aktualisieren()

    def leeren(self):
        self.dateien.clear()
        self._aktualisieren()

    def verschieben(self, richtung):
        sel = list(self.liste.curselection())
        if not sel:
            return
        if richtung < 0 and sel[0] == 0:
            return
        if richtung > 0 and sel[-1] == len(self.dateien) - 1:
            return
        for i in (sel if richtung < 0 else reversed(sel)):
            j = i + richtung
            self.dateien[i], self.dateien[j] = self.dateien[j], self.dateien[i]
        self._aktualisieren()
        for i in sel:
            self.liste.selection_set(i + richtung)

    def erstellen(self):
        if not self.dateien:
            messagebox.showwarning("Hinweis", "Bitte zuerst Bilder hinzufügen.")
            return
        ziel = filedialog.asksaveasfilename(
            title="PDF speichern unter", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")], initialfile="ausgabe.pdf",
        )
        if not ziel:
            return
        try:
            self.status.config(text="Erstelle PDF …")
            self.update_idletasks()
            pdf_erstellen(self.dateien, ziel, self.a4.get(),
                          int(self.qualitaet.get()))
            self.status.config(text=f"Fertig: {os.path.basename(ziel)}")
            messagebox.showinfo("Fertig", f"PDF gespeichert:\n{ziel}")
        except Exception as e:
            self.status.config(text="Fehler.")
            messagebox.showerror("Fehler", str(e))


if __name__ == "__main__":
    App().mainloop()
