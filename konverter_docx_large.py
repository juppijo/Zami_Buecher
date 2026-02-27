import mammoth
import os
import re
from bs4 import BeautifulSoup

# Konfiguration
DOCX_FILE = "Die Kunst des einfühlsamen Zuhörens und Sprechens.docx"
OUTPUT_DIR = "Die Kunst des einfühlsamen Zuhörens und Sprechens"
IMG_DIR = os.path.join(OUTPUT_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text or "section"

def image_handler(image):
    image_count = len(os.listdir(IMG_DIR)) + 1
    image_filename = f"bild_{image_count}.jpg"
    with image.open() as image_source:
        with open(os.path.join(IMG_DIR, image_filename), "wb") as out:
            out.write(image_source.read())
    return {"src": f"images/{image_filename}", "class": "book-image"}

def create_large_book():
    if not os.path.exists(DOCX_FILE):
        print(f"Fehler: {DOCX_FILE} nicht gefunden!")
        return

    with open(DOCX_FILE, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(image_handler))
        raw_html = result.value

    soup = BeautifulSoup(raw_html, 'html.parser')

    # ... (vorheriger Code bleibt gleich)

    pages = []
    current_content = ""
    limit = 1200 

    for el in soup.contents:
        el_str = str(el)
        
        # 1. Bedingung: Manuelles Symbol ### gefunden
        manual_break = "###" in el_str
        
        # 2. Bedingung: Das Element ist ein Bild (img-Tag)
        # BeautifulSoup hilft uns hier zu prüfen, ob ein Bild im aktuellen Element steckt
        contains_image = False
        if el.name: # Nur echte HTML-Tags prüfen, keine reinen Textknoten
            if el.name == 'img' or el.find('img'):
                contains_image = True

        # Wenn eines von beiden zutrifft:
        if manual_break or contains_image:
            # Falls ### vorhanden, Text säubern
            if manual_break:
                el_str = el_str.replace("###", "")
            
            # Das aktuelle Element (Bild oder Text vor dem ###) noch zur Seite hinzufügen
            current_content += el_str
            
            # Seite sofort abschließen und neue beginnen
            if current_content:
                pages.append(current_content)
                current_content = ""
            continue 

        # Normaler Umbruch bei Kapiteln oder Zeichenlimit
        if el.name in ['h1', 'h2'] or len(current_content) + len(el_str) > limit:
            if current_content:
                pages.append(current_content)
                current_content = ""
        
        current_content += el_str

    if current_content:
        pages.append(current_content)

    # ... (Rest des Skripts bleibt gleich)

    all_pages = [pages[0], "<h1>Inhaltsverzeichnis</h1><div id='toc-inject'></div>"] + pages[1:]
    if len(all_pages) % 2 != 0: all_pages.append("<p style='text-align:center; margin-top:50%;'>- Finis -</p>")

    pages_divs = "".join([f'<div class="page"><div class="page-content">{p}</div></div>' for p in all_pages])

    # --- HTML ---
    index_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Die Kunst des einfühlsamen Zuhörens und Sprechens</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lora:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body class="light-mode">
    <div class="stars"></div>

    <div class="controls">
        <button id="btn-toc">Inhalt</button>
        <button id="btn-prev">Zurück</button>
        <span id="page-info">Seite 1</span>
        <button id="btn-next">Vorwärts</button>
        <button id="btn-bookmark">🔖 Lesezeichen</button>
        <button id="btn-speak">▶ Vorlesen</button>
        <button id="btn-dark-mode">🌓 Dark</button>
        <button id="btn-zen">🧘 Zen</button>
    </div>
    
    <div id="wrapper">
        <div id="book">{pages_divs}</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
    <script src="script.js"></script>
</body>
</html>"""

    # --- CSS (Verbesserte Größen) ---
    style_css = """
:root { --bg-color: #090a3f; --paper-color: #fdfaf3; --text-color: #2c3e50; --accent-color: #696a9f; }
body.dark-mode { --bg-color: #050515; --paper-color: #1a1a2a; --text-color: #e0e0e0; --accent-color: #393a6f; }

body.zen-mode {--bg-color: #051515; --paper-color: #1a2a2a; --text-color: #e0f0e0; }

body { background: var(--bg-color); margin: 0; display: flex; flex-direction: column; height: 100vh; font-family: 'Lora', serif; overflow: hidden; transition: 0.5s; align-items: center; }

#wrapper { flex: 1; display: flex; align-items: center; justify-content: center; width: 100%; padding: 10px; box-sizing: border-box; }

.stars { position: fixed; top:0; left:0; width:100%; height:100%; background: url('https://www.transparenttextures.com/patterns/cream-paper.png'); opacity: 0.3; pointer-events: none; }
/* background-color: #12004d;
   background-image: url("https://www.transparenttextures.com/patterns/cream-paper.png");  stardust
/* This is mostly intended for prototyping; please download the pattern and re-host for production environments. Thank you! */

#book { box-shadow: 0 0 100px rgba(0,0,0,0.8); }

.page { background: var(--paper-color) !important; padding: 60px !important; box-sizing: border-box; border: 1px solid rgba(0,0,0,0.1); }
.page-content { 
    height: 100%; width: 100%; overflow-y: auto; 
    font-size: 14px; line-height: 1.2; color: var(--text-color); 
    text-align: justify; hyphens: auto;
}
img { max-width: auto; max-height: 60vh; display: block; margin: 30px auto; border-radius: 5px; border: 5px solid #fff; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }

.controls { margin-top: 1px; margin-bottom: 1px; z-index: 100; display: flex; align-items: center; background: rgba(0,0,20,0.7); padding: 12px 25px; border-radius: 50px; backdrop-filter: blur(10px); }

body.zen-mode .controls { opacity: 0; transform: translateY(50px); pointer-events: none; }
#page-info { color: white; margin: 0 15px; font-size: 0.9rem; min-width: 80px; text-align: center; }
button { padding: 10px 18px; cursor: pointer; background: var(--accent-color); color: #eeeeff; border: none; border-radius: 20px; font-weight: bold; margin: 0 5px; transition: 0.3s; }

/* Macht nur die Einträge im Inhaltsverzeichnis fett */
/* 1. Haupt-Einträge im Verzeichnis (h1 und h2) fett machen */
#toc-inject a {
    font-weight: bold;      /* Macht den Text fett */
    text-decoration: none;  /* Entfernt den Unterstrich */
    color: inherit;         /* Nutzt die Textfarbe des Buches */
    display: flex;          /* Ermöglicht die Seitenzahlen rechts */
    justify-content: space-between;
    padding: 4px 0;         /* Mehr Platz zwischen den Zeilen */
    border-bottom: 1px dotted #ccc; /* Eine feine Linie dazwischen */
}

/* Optional: Nur H1 und H2 im Verzeichnis fett, H4 normal */
#toc-inject li:has(h1), #toc-inject li:has(h2) {
    font-weight: 800;
}

/* 2. Falls h4 vorhanden ist: Diese im Verzeichnis NICHT fett machen */
#toc-inject li:has(h4) a {
    font-weight: normal;    /* h4 Einträge sind wieder dünn */
    font-size: 0.9em;       /* Etwas kleiner */
    padding-left: 20px;     /* Einrücken nach rechts */
}

/* 3. Effekt beim Drüberfahren (Hover) */
#toc-inject a:hover {
    color: #b8860b;         /* Goldene Farbe beim Berühren */
}
"""

    # --- JS (Stabile Größensteuerung) ---
    script_js = """
document.addEventListener('DOMContentLoaded', function() {

    // Dynamische Berechnung der Buchgröße basierend auf Fensterhöhe
    const h = window.innerHeight * 0.80; 
    //const w = h * 0.75; // Goldenes Schnittverhältnis
    const w = window.innerWidth * 0.40;
    const pageFlip = new St.PageFlip(document.getElementById('book'), {
        width: w, height: h,
        size: "fixed",
        minWidth: 400, maxWidth: 1200,
        minHeight: 600, maxHeight: 1600,
        drawShadow: true, showCover: true,
        usePortrait: false, // Erzwingt Doppelseite wenn Platz da ist
        mobileScrollSupport: false
    });
    pageFlip.loadFromHTML(document.querySelectorAll('.page'));

    // TOC Generator & Funktionen
    const toc = document.getElementById('toc-inject');
    const contents = document.querySelectorAll('.page-content');
    let html = '<ul style="list-style:none; padding:0;">';

    contents.forEach((c, i) => {
        const h = c.querySelector('h1, h2, h3, h4, h5, h6');
        if(h && i > 0) {
            // Hier ist der Trick: Wir merken uns, welcher Tag es war (h1, h2, etc.)
            const tagName = h.tagName.toLowerCase(); 
            //    style="margin:10px 0; border-bottom:1px dotted #ccc;"
            html += `
                <li class="toc-item-${tagName}"> 
                    <a href="#" onclick="window.flipToPage(${i+2})" style="text-decoration:none; color:inherit; display:flex; justify-content:space-between;">
                        <${tagName} style="margin:0; font-size:inherit; font-family:inherit; font-weight:inherit;">
                            ${h.innerText}
                        </${tagName}>
                        <span>S. ${i+2}</span>
                    </a>
                </li>`;
        }
    });
    if(toc) toc.innerHTML = html + '</ul>';

    const synth = window.speechSynthesis;
    let isReading = false;
    function stop() { synth.cancel(); isReading = false; document.getElementById('btn-speak').innerText = "▶ Vorlesen"; }

    document.getElementById('btn-speak').addEventListener('click', () => {
        if(synth.speaking) stop();
        else {
            isReading = true;
            const idx = pageFlip.getCurrentPageIndex();
            const pages = document.querySelectorAll('.page-content');
            let txt = pages[idx].innerText;
            if(idx > 0 && idx + 1 < pages.length) txt += " " + pages[idx+1].innerText;
            const u = new SpeechSynthesisUtterance(txt);
            u.lang = 'de-DE';
            u.onend = () => { if(isReading && idx+2 < pages.length) { pageFlip.flipNext(); setTimeout(() => document.getElementById('btn-speak').click(), 1200); } else stop(); };
            synth.speak(u);
            document.getElementById('btn-speak').innerText = "■ Stop";
        }
    });

    document.getElementById('btn-dark-mode').addEventListener('click', () => document.body.classList.toggle('dark-mode'));

    document.getElementById('btn-zen').addEventListener('click', () => {
        // 1. Zen-Klasse für CSS hinzufügen
        document.body.classList.add('zen-mode');
        
        // 2. Browser in den echten Vollbildmodus versetzen
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        } else if (document.documentElement.mozRequestFullScreen) { // Firefox
            document.documentElement.mozRequestFullScreen();
        } else if (document.documentElement.webkitRequestFullscreen) { // Chrome, Safari
            document.documentElement.webkitRequestFullscreen();
        } else if (document.documentElement.msRequestFullscreen) { // IE/Edge
            document.documentElement.msRequestFullscreen();
        }
    });


    // ESC-Taste: Beendet den Zen-Modus und den Vollbildmodus
    document.addEventListener('keydown', e => {
        if (e.key === "Escape") {
            document.body.classList.remove('zen-mode');
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    });

    document.addEventListener('keydown', e => { if(e.key === "Escape") document.body.classList.remove('zen-mode'); });
    document.getElementById('btn-bookmark').addEventListener('click', () => { localStorage.setItem('u_book', pageFlip.getCurrentPageIndex()); alert('Lesezeichen gesetzt!'); });
    document.getElementById('btn-prev').addEventListener('click', () => { stop(); pageFlip.flipPrev(); });
    document.getElementById('btn-next').addEventListener('click', () => { stop(); pageFlip.flipNext(); });
    document.getElementById('btn-toc').addEventListener('click', () => { stop(); pageFlip.flip(1); });

    pageFlip.on('flip', e => { document.getElementById('page-info').innerText = "Seite " + (e.data + 1); });
    window.flipToPage = n => { stop(); pageFlip.flip(n); };

    const saved = localStorage.getItem('u_book');
    if(saved) setTimeout(() => { if(confirm('Lesezeichen laden?')) pageFlip.turnToPage(parseInt(saved)); }, 1000);
});
"""

    # Schreiben
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(index_html)
    with open(os.path.join(OUTPUT_DIR, "style.css"), "w", encoding="utf-8") as f: f.write(style_css)
    with open(os.path.join(OUTPUT_DIR, "script.js"), "w", encoding="utf-8") as f: f.write(script_js)
    print(f"Großformat-Edition fertig in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    create_large_book()
