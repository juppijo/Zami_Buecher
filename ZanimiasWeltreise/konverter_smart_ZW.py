import mammoth
import os
import re
from bs4 import BeautifulSoup

# Konfiguration
DOCX_FILE = "ZanimiasWeltreise.docx"
OUTPUT_DIR = "ZanimiasWeltreise_Smart"
IMG_DIR = os.path.join(OUTPUT_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def image_handler(image):
    image_count = len(os.listdir(IMG_DIR)) + 1
    image_filename = f"bild_{image_count}.jpg"
    with image.open() as image_source:
        with open(os.path.join(IMG_DIR, image_filename), "wb") as out:
            out.write(image_source.read())
    return {"src": f"images/{image_filename}", "class": "book-image"}

def create_mobile_book():
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
    limit = 800 # Kleineres Limit für Smartphone-Displays

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
    pages_divs = "".join([f'<div class="page"><div class="page-content">{p}</div></div>' for p in all_pages])

    # --- HTML ---
    index_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Die Kunst des einfühlsamen Zuhörens und Sprechens</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lora:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>
<body class="light-mode">
    <div class="stars"></div>

    <div class="controls-top">
        <button id="btn-toc">☰</button>
        <button id="btn-prev">⬅️</button>
        <span id="page-info">S. 1</span>
        <button id="btn-next">➡️</button>
        <button id="btn-dark-mode">🌓</button>
        <button id="btn-zen">🧘</button>
        <button id="btn-bookmark">🔖</button>
        <button id="btn-speak">▶</button>       
    </div>
    
    <div id="wrapper">
        <div id="book">{pages_divs}</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
    <script src="script.js"></script>
</body>
</html>"""

    # --- CSS (Mobile Optimiert) ---
    style_css = """
:root { --bg-color: #090a3f; --paper-color: #fdfaf3; --text-color: #2c3e50; --accent-color: #696a9f; }
body.dark-mode { --bg-color: #050515; --paper-color: #1a1a2a; --text-color: #e0e0e0; --accent-color: #393a6f; }
body.zen-mode { --bg-color: #000; }

body { 
    background: var(--bg-color); margin: 0; display: flex; flex-direction: column; 
    height: 100vh; font-family: 'Lora', serif; overflow: hidden; transition: 0.5s; 
}

#wrapper { 
    flex: 1; display: flex; align-items: center; justify-content: center; 
    width: 100vw; height: calc(100vh - 120px); 
}

.stars { position: fixed; top:0; left:0; width:100%; height:100%; background: url('https://www.transparenttextures.com/patterns/cream-paper.png'); opacity: 0.2; pointer-events: none; }

#book { box-shadow: 0 0 30px rgba(0,0,0,0.5); }

.page { background: var(--paper-color) !important; padding: 25px !important; box-sizing: border-box; }
.page-content { 
    height: 100%; width: 100%; overflow-y: auto; 
    font-size: 16px; line-height: 1.4; color: var(--text-color); 
    text-align: left; 
}

img { max-width: auto; height: 80vh; display: block; margin: 15px auto; border-radius: 5px; }

/* Steuerung oben und unten für Daumenbedienung */
.controls-top, .controls-bottom { 
    z-index: 100; display: flex; align-items: center; justify-content: space-around; 
    background: rgba(0,0,20,0.85); padding: 10px; backdrop-filter: blur(10px); 
}

.controls-top { border-bottom: 1px solid rgba(255,255,255,0.1); }
.controls-bottom { border-top: 1px solid rgba(255,255,255,0.1); }

body.zen-mode .controls-top, body.zen-mode .controls-bottom { display: none; }

#page-info { color: white; font-size: 0.8rem; }
button { 
    padding: 7px 10px; cursor: pointer; background: var(--accent-color); 
    color: #eeeeff; border: none; border-radius: 10px; font-weight: bold; 
}

#toc-inject a {
    font-weight: bold; text-decoration: none; color: inherit; 
    display: flex; justify-content: space-between; padding: 10px 0;
    border-bottom: 1px dotted #ccc; font-size: 14px;
}
.toc-item-h4 { padding-left: 15px; }
"""

    # --- JS (Single Page Mode) ---
    script_js = """
document.addEventListener('DOMContentLoaded', function() {
    const w = window.innerWidth * 0.99;
    const h = window.innerHeight * 0.99;

    const pageFlip = new St.PageFlip(document.getElementById('book'), {
        width: w, height: h,
        size: "fixed",
        //minWidth: 250, maxWidth: 600,
        //minHeight: 400, maxHeight: 1000,
        drawShadow: true, 
        showCover: false,
        usePortrait: true,      // ERZWINGT EINZELSEITE
        startPage: 0,
        mobileScrollSupport: true
    });
    pageFlip.loadFromHTML(document.querySelectorAll('.page'));

    const toc = document.getElementById('toc-inject');
    const contents = document.querySelectorAll('.page-content');
    let html = '<ul style="list-style:none; padding:0;">';
    contents.forEach((c, i) => {
        const h = c.querySelector('h1, h2, h3, h4');
        if(h && i > 0) {
            html += `<li class="toc-item-${h.tagName.toLowerCase()}"> 
                <a href="#" onclick="window.flipToPage(${i+1})">
                    <span>${h.innerText}</span> <span>S. ${i+1}</span>
                </a></li>`;
        }
    });
    if(toc) toc.innerHTML = html + '</ul>';

    // Audio & Controls (Analog zur Desktop Version)
    const synth = window.speechSynthesis;
    function stop() { synth.cancel(); document.getElementById('btn-speak').innerText = "▶"; }

    document.getElementById('btn-speak').addEventListener('click', () => {
        if(synth.speaking) stop();
        else {
            const idx = pageFlip.getCurrentPageIndex();
            const txt = document.querySelectorAll('.page-content')[idx].innerText;
            const u = new SpeechSynthesisUtterance(txt); u.lang = 'de-DE';
            u.onend = stop; synth.speak(u);
            document.getElementById('btn-speak').innerText = "■";
        }
    });

    document.getElementById('btn-dark-mode').addEventListener('click', () => document.body.classList.toggle('dark-mode'));
    document.getElementById('btn-zen').addEventListener('click', () => {
        document.body.classList.add('zen-mode');
        if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
    });

    document.addEventListener('keydown', e => { if(e.key === "Escape") { 
        document.body.classList.remove('zen-mode'); 
        if(document.exitFullscreen) document.exitFullscreen();
    }});

    document.getElementById('btn-bookmark').addEventListener('click', () => { 
        localStorage.setItem('m_book', pageFlip.getCurrentPageIndex()); 
        alert('Seite gemerkt!'); 
    });

    document.getElementById('btn-prev').addEventListener('click', () => { stop(); pageFlip.flipPrev(); });
    document.getElementById('btn-next').addEventListener('click', () => { stop(); pageFlip.flipNext(); });
    document.getElementById('btn-toc').addEventListener('click', () => { stop(); pageFlip.flip(1); });

    pageFlip.on('flip', e => { document.getElementById('page-info').innerText = "S. " + (e.data + 1); });
    window.flipToPage = n => { stop(); pageFlip.flip(n); };

    const saved = localStorage.getItem('m_book');
    if(saved) setTimeout(() => { if(confirm('Lesezeichen laden?')) pageFlip.turnToPage(parseInt(saved)); }, 1000);
});
"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(index_html)
    with open(os.path.join(OUTPUT_DIR, "style.css"), "w", encoding="utf-8") as f: f.write(style_css)
    with open(os.path.join(OUTPUT_DIR, "script.js"), "w", encoding="utf-8") as f: f.write(script_js)
    print(f"Smartphone-Version erstellt in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    create_mobile_book()
