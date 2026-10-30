import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfWriter

def haupt_pdf_auswaehlen():
    pfad = filedialog.askopenfilename(
        title="Haupt-PDF auswählen",
        filetypes=[("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
    )
    if pfad:
        entry_haupt.delete(0, tk.END)
        entry_haupt.insert(0, pfad)

def insert_pdf_auswaehlen():
    pfad = filedialog.askopenfilename(
        title="Einzufügende PDF auswählen",
        filetypes=[("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
    )
    if pfad:
        entry_insert.delete(0, tk.END)
        entry_insert.insert(0, pfad)

def pdfs_zusammenfuegen():
    haupt_pfad = entry_haupt.get()
    insert_pfad = entry_insert.get()
    
    if not haupt_pfad or not insert_pfad:
        messagebox.showwarning("Achtung", "Bitte wähle sowohl die Haupt-PDF als auch die einzufügende PDF aus!")
        return

    try:
        # Speicherort für das Ergebnis festlegen
        output_pfad = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Datei", "*.pdf")],
            title="Kombinierte PDF speichern unter..."
        )
        
        if output_pfad:
            writer = PdfWriter()
            
            # Haupt-PDF hinzufügen
            writer.append(haupt_pfad)
            
            # Position bestimmen
            position_str = entry_position.get().strip()
            
            if position_str == "" or position_str.lower() == "ende":
                # Am Ende anfügen
                writer.append(insert_pfad)
            else:
                # Nach einer bestimmten Seite einfügen (0-indiziert oder 1-indiziert? Machen wir es intuitiv als Seitenzahl)
                try:
                    seite = int(position_str)
                    # Wenn der Benutzer z.B. nach Seite 2 einfügen möchte (Index 2 in pypdf)
                    writer.merge(seite, insert_pfad)
                except ValueError:
                    messagebox.showerror("Fehler", "Ungültige Positionsangabe! Bitte gib eine Zahl ein oder lass das Feld leer für das Ende.")
                    return
            
            # Neue Datei speichern
            with open(output_pfad, "wb") as output_file:
                writer.write(output_file)
            writer.close()
            
            messagebox.showinfo("Erfolg", f"Die PDF-Dateien wurden erfolgreich zusammengefügt:\n{output_pfad}")
            
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")

# Hauptfenster erstellen
fenster = tk.Tk()
fenster.title("PDF Inserter / Merger")
fenster.geometry("500x320")
fenster.resizable(False, False)

# UI-Elemente
label_titel = tk.Label(fenster, text="PDF-Dateien zusammenfügen", font=("Arial", 14, "bold"))
label_titel.pack(pady=10)

# 1. Haupt-PDF
frame_haupt = tk.Frame(fenster)
frame_haupt.pack(pady=5, padx=20, fill=tk.X)
tk.Label(frame_haupt, text="Haupt-PDF:", width=15, anchor="w", font=("Arial", 10)).pack(side=tk.LEFT)
entry_haupt = tk.Entry(frame_haupt, font=("Arial", 10))
entry_haupt.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
tk.Button(frame_haupt, text="Durchsuchen", command=haupt_pdf_auswaehlen, font=("Arial", 9)).pack(side=tk.RIGHT)

# 2. Einzufügende PDF
frame_insert = tk.Frame(fenster)
frame_insert.pack(pady=5, padx=20, fill=tk.X)
tk.Label(frame_insert, text="Einzufügende PDF:", width=15, anchor="w", font=("Arial", 10)).pack(side=tk.LEFT)
entry_insert = tk.Entry(frame_insert, font=("Arial", 10))
entry_insert.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
tk.Button(frame_insert, text="Durchsuchen", command=insert_pdf_auswaehlen, font=("Arial", 9)).pack(side=tk.RIGHT)

# 3. Position
frame_pos = tk.Frame(fenster)
frame_pos.pack(pady=5, padx=20, fill=tk.X)
tk.Label(frame_pos, text="Nach Seite (optional):", width=15, anchor="w", font=("Arial", 10)).pack(side=tk.LEFT)
entry_position = tk.Entry(frame_pos, font=("Arial", 10))
entry_position.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
entry_position.insert(0, "Ende")
tk.Label(frame_pos, text="(z.B. 1 für nach Seite 1)", fg="gray", font=("Arial", 8)).pack(side=tk.RIGHT)

# Ausführen-Button
btn_ausführen = tk.Button(fenster, text="PDFs zusammenfügen", command=pdfs_zusammenfuegen, bg="#2196F3", fg="white", font=("Arial", 11, "bold"), width=22, height=2)
btn_ausführen.pack(pady=15)

# Programm starten
fenster.mainloop()