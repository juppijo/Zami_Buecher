
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
