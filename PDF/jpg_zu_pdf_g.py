import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def bild_auswaehlen():
    # Dateiauswahl-Dialog für JPG-Bilder
    dateipfad = filedialog.askopenfilename(
        title="Wähle ein JPG-Bild aus",
        filetypes=[("JPG-Dateien", "*.jpg *.jpeg"), ("Alle Dateien", "*.*")]
    )
    if dateipfad:
        entry_pfad.delete(0, tk.END)
        entry_pfad.insert(0, dateipfad)

def in_pdf_umwandeln():
    bild_pfad = entry_pfad.get()
    if not bild_pfad:
        messagebox.showwarning("Achtung", "Bitte wähle zuerst ein Bild aus!")
        return

    try:
        # Speicherort für die PDF festlegen
        pdf_pfad = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Datei", "*.pdf")],
            title="PDF speichern unter..."
        )
        
        if pdf_pfad:
            # Bild öffnen und in RGB konvertieren (notwendig für JPEG zu PDF)
            bild = Image.open(bild_pfad)
            if bild.mode != "RGB":
                bild = bild.convert("RGB")
            
            # Als PDF speichern
            bild.save(pdf_pfad, "PDF", resolution=100.0)
            messagebox.success("Erfolg", f"Das Bild wurde erfolgreich als PDF gespeichert:\n{pdf_pfad}")
            
    except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")

# Hauptfenster erstellen
fenster = tk.Tk()
fenster.title("JPG zu PDF Umwandler")
fenster.geometry("450x200")
fenster.resizable(False, False)

# UI-Elemente
label_titel = tk.Label(fenster, text="JPG in PDF umwandeln", font=("Arial", 14, "bold"))
label_titel.pack(pady=10)

frame_pfad = tk.Frame(fenster)
frame_pfad.pack(pady=10, padx=20, fill=tk.X)

entry_pfad = tk.Entry(frame_pfad, width=35, font=("Arial", 10))
entry_pfad.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)

btn_durchsuchen = tk.Button(frame_pfad, text="Durchsuchen", command=bild_auswaehlen, font=("Arial", 10))
btn_durchsuchen.pack(side=tk.RIGHT)

btn_umwandeln = tk.Button(fenster, text="In PDF umwandeln", command=in_pdf_umwandeln, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=20, height=2)
btn_umwandeln.pack(pady=10)

# Programm starten
fenster.mainloop()