import os
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urlparse
from PIL import Image

def html_zu_markdown_erweitert(html_pfad, md_pfad, bilder_speichern=True, ziel_format="png", css_bereinigen=True):
    # Basisverzeichnis ermitteln
    output_dir = os.path.dirname(os.path.abspath(md_pfad))
    images_dir = os.path.join(output_dir, "images")
    
    if bilder_speichern and not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    with open(html_pfad, "r", encoding="utf-8") as f:
        html_inhalt = f.read()
        
    soup = BeautifulSoup(html_inhalt, "html.parser")
    
    # 1. CSS-Stile und Rauschen bereinigen
    if css_bereinigen:
        # Entferne style-Attribute, class-Attribute und id-Attribute von allen Tags
        for tag in soup.find_all(True):
            for attr in ["style", "class", "id"]:
                if tag.has_attr(attr):
                    del tag[attr]
                    
    # 2. Bilder verarbeiten und konvertieren
    img_zaehler = 1
    if bilder_speichern:
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
                
            try:
                bild_daten = None
                if src.startswith("http://") or src.startswith("https://"):
                    antwort = requests.get(src, timeout=10)
                    if antwort.status_code == 200:
                        bild_daten = BytesIO(antwort.content)
                elif os.path.exists(src):
                    with open(src, "rb") as quelle:
                        bild_daten = BytesIO(quelle.read())
                        
                if bild_daten:
                    # Mit Pillow öffnen und ins Zielformat konvertieren
                    with Image.open(bild_daten) as pil_img:
                        # Falls das Bild Transparenz hat (RGBA), aber als JPEG gespeichert werden soll, konvertieren
                        if ziel_format.lower() == "jpg" or ziel_format.lower() == "jpeg":
                            if pil_img.mode in ("RGBA", "P"):
                                pil_img = pil_img.convert("RGB")
                            save_ext = ".jpg"
                        else:
                            save_ext = f".{ziel_format.lower()}"
                            
                        neuer_name = f"bild_{img_zaehler}{save_ext}"
                        neuer_pfad = os.path.join(images_dir, neuer_name)
                        relativer_link = f"images/{neuer_name}"
                        
                        pil_img.save(neuer_pfad)
                        img["src"] = relativer_link
            except Exception as e:
                print(f"Konnte Bild {src} nicht verarbeiten: {e}")
                
            img_zaehler += 1
            
    # HTML in Markdown umwandeln
    markdown_inhalt = md(str(soup), heading_style="ATX")
    
    with open(md_pfad, "w", encoding="utf-8") as f:
        f.write(markdown_inhalt)
        
    print(f"✨ Perfekt! Markdown gespeichert unter: {md_pfad}")
    if bilder_speichern:
        print(f"📁 Bilder konvertiert und im Ordner abgelegt: {images_dir}")

if __name__ == "__main__":
    # Passe hier deine Einstellungen an:
    html_eingabe = "Mirjam_ha-Magdalit.html"
    md_ausgabe = "Mirjam_ha-Magdalit.md"
    
    # Du kannst hier das Format ("png", "jpg", etc.) und die Bereinigung steuern
    html_zu_markdown_erweitert(
        html_pfad=html_eingabe, 
        md_pfad=md_ausgabe, 
        bilder_speichern=False, 
        ziel_format="jpg",       # Konvertiert alle Bilder automatisch einheitlich zu jpg
        css_bereinigen=True      # Befreit das HTML von lästigem CSS und Klassen
    )
