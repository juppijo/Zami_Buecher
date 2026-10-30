#!/usr/bin/env python3
"""
PDF in PDF einfügen
Voraussetzung:  pip install pypdf
Start:          python pdf_einfuegen.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader, PdfWriter

# --- Farben (dunkel / gold) ---
BG = "#14110d"
PANEL = "#1e1a14"
GOLD = "#d4af37"
TEXT = "#eadfc4"


def seiten_parsen(text, anzahl):
    """'1-3,5' -> [0,1,2,4]. Leer = alle Seiten."""
    text = text.strip()
    if not text:
        return list(range(anzahl))
    ergebnis = []
    for teil in text.split(","):
        teil = teil.strip()
        if not teil:
            continue
        if "-" in teil:
            a, b = teil.split("-", 1)
            a, b = int(a), int(b)
            if a > b:
                a, b = b, a
        else:
            a = b = int(teil)
        if a < 1 or b > anzahl:
            raise ValueError(f"Seitenbereich '{teil}' liegt außerhalb von 1–{anzahl}.")
        ergebnis.extend(range(a - 1, b))
    if not ergebnis:
        raise ValueError("Keine gültigen Seiten angegeben.")
    return ergebnis


def pdf_einfuegen(basis, einfuegen, ziel, nach_seite, seiten_text):
    r_basis = PdfReader(basis)
    r_ein = PdfReader(einfuegen)
    for r in (r_basis, r_ein):
        if r.is_encrypted:
            raise ValueError("Verschlüsselte PDFs werden nicht unterstützt.")

    n_basis = len(r_basis.pages)
    n_ein = len(r_ein.pages)
    if not 0 <= nach_seite <= n_basis:
        raise ValueError(f"Position muss zwischen 0 und {n_basis} liegen.")
    auswahl = seiten_parsen(seiten_text, n_ein)

    w = PdfWriter()
    for i in range(nach_seite):
        w.add_page(r_basis.pages[i])
    for i in auswahl:
        w.add_page(r_ein.pages[i])
    for i in range(nach_seite, n_basis):
        w.add_page(r_basis.pages[i])

    with open(ziel, "wb") as f:
        w.write(f)
    return n_basis + len(auswahl)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF in PDF einfügen")
        self.geometry("620x470")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.basis = tk.StringVar()
        self.ein = tk.StringVar()
        self.pos = tk.IntVar(value=0)
        self.seiten = tk.StringVar()
        self.n_basis = 0
        self.n_ein = 0

        self._stil()
        self._aufbau()

    def _stil(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=TEXT)
        s.configure("Info.TLabel", background=BG, foreground=GOLD)
        s.configure("TButton", background=PANEL, foreground=GOLD,
                    bordercolor=GOLD, padding=6)
        s.map("TButton", background=[("active", "#2a241a")])
        s.configure("Gold.TButton", background=GOLD, foreground="#14110d",
                    font=("Segoe UI", 10, "bold"), padding=8)
        s.map("Gold.TButton", background=[("active", "#e6c455")])
        s.configure("TEntry", fieldbackground=PANEL, foreground=TEXT,
                    insertcolor=GOLD)
        s.configure("TSpinbox", fieldbackground=PANEL, foreground=TEXT,
                    arrowcolor=GOLD)

    def _datei_zeile(self, parent, titel, var, cmd):
        ttk.Label(parent, text=titel, foreground=GOLD,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 2))
        z = ttk.Frame(parent)
        z.pack(fill="x")
        ttk.Entry(z, textvariable=var, state="readonly").pack(
            side="left", fill="x", expand=True)
        ttk.Button(z, text="Wählen …", command=cmd).pack(side="left", padx=(8, 0))

    def _aufbau(self):
        ttk.Label(self, text="PDF in PDF einfügen", foreground=GOLD,
                  font=("Segoe UI", 18, "bold")).pack(pady=(14, 0))

        rahmen = ttk.Frame(self)
        rahmen.pack(fill="x", padx=18)

        self._datei_zeile(rahmen, "1. Haupt-PDF (hier wird eingefügt)",
                          self.basis, self.basis_waehlen)
        self.basis_info = ttk.Label(rahmen, text="", style="Info.TLabel")
        self.basis_info.pack(anchor="w")

        self._datei_zeile(rahmen, "2. PDF, die eingefügt werden soll",
                          self.ein, self.ein_waehlen)
        self.ein_info = ttk.Label(rahmen, text="", style="Info.TLabel")
        self.ein_info.pack(anchor="w")

        ttk.Label(rahmen, text="3. Optionen", foreground=GOLD,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(14, 4))

        z1 = ttk.Frame(rahmen)
        z1.pack(fill="x", pady=2)
        ttk.Label(z1, text="Einfügen nach Seite (0 = am Anfang):").pack(side="left")
        self.spin = ttk.Spinbox(z1, from_=0, to=0, width=6, textvariable=self.pos)
        self.spin.pack(side="left", padx=8)

        z2 = ttk.Frame(rahmen)
        z2.pack(fill="x", pady=2)
        ttk.Label(z2, text="Nur diese Seiten einfügen (z. B. 1-3,5; leer = alle):"
                  ).pack(side="left")
        ttk.Entry(z2, textvariable=self.seiten, width=14).pack(side="left", padx=8)

        ttk.Button(self, text="PDF zusammenfügen", style="Gold.TButton",
                   command=self.erstellen).pack(pady=(18, 6))
        self.status = ttk.Label(self, text="Bitte beide PDFs auswählen.")
        self.status.pack()

    # --- Aktionen ---
    def _pdf_waehlen(self, titel):
        return filedialog.askopenfilename(
            title=titel, filetypes=[("PDF", "*.pdf"), ("Alle Dateien", "*.*")])

    def basis_waehlen(self):
        p = self._pdf_waehlen("Haupt-PDF auswählen")
        if not p:
            return
        try:
            self.n_basis = len(PdfReader(p).pages)
        except Exception as e:
            messagebox.showerror("Fehler", f"PDF konnte nicht gelesen werden:\n{e}")
            return
        self.basis.set(p)
        self.basis_info.config(text=f"{self.n_basis} Seite(n)")
        self.spin.config(to=self.n_basis)
        self.pos.set(self.n_basis)  # Standard: am Ende

    def ein_waehlen(self):
        p = self._pdf_waehlen("Einzufügende PDF auswählen")
        if not p:
            return
        try:
            self.n_ein = len(PdfReader(p).pages)
        except Exception as e:
            messagebox.showerror("Fehler", f"PDF konnte nicht gelesen werden:\n{e}")
            return
        self.ein.set(p)
        self.ein_info.config(text=f"{self.n_ein} Seite(n)")

    def erstellen(self):
        if not self.basis.get() or not self.ein.get():
            messagebox.showwarning("Hinweis", "Bitte beide PDFs auswählen.")
            return
        try:
            nach = int(self.pos.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("Hinweis", "Ungültige Position.")
            return
        ziel = filedialog.asksaveasfilename(
            title="Ergebnis speichern unter", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")], initialfile="zusammengefuegt.pdf")
        if not ziel:
            return
        if os.path.abspath(ziel) in (os.path.abspath(self.basis.get()),
                                     os.path.abspath(self.ein.get())):
            messagebox.showwarning(
                "Hinweis", "Bitte einen anderen Dateinamen wählen, "
                           "um die Originale nicht zu überschreiben.")
            return
        try:
            gesamt = pdf_einfuegen(self.basis.get(), self.ein.get(), ziel,
                                   nach, self.seiten.get())
            self.status.config(text=f"Fertig: {gesamt} Seiten in {os.path.basename(ziel)}")
            messagebox.showinfo("Fertig", f"PDF gespeichert ({gesamt} Seiten):\n{ziel}")
        except Exception as e:
            self.status.config(text="Fehler.")
            messagebox.showerror("Fehler", str(e))


if __name__ == "__main__":
    App().mainloop()
