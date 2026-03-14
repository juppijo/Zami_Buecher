document.addEventListener('DOMContentLoaded', function() {

    const bookEl  = document.getElementById('book');
    const wrapper = document.getElementById('wrapper');

    // Feste Buchgröße – wird NIE geändert
    const BASE_W = 800;
    const BASE_H = 1100;

    // PageFlip einmal erstellen
    const pageFlip = new St.PageFlip(bookEl, {
        width: BASE_W, height: BASE_H,
        size: "fixed",
        drawShadow: true, showCover: true,
        usePortrait: false, mobileScrollSupport: false
    });
    pageFlip.loadFromHTML(document.querySelectorAll('.page'));

    // ─── Skalierung per CSS transform ─────────────────────────────────────────
    // Das Buch bleibt immer BASE_W x BASE_H groß,
    // wird aber via scale() ins Fenster eingepasst – zuverlässig, kein Neuaufbau.
    function scaleBook() {
        const controlsH = 70; // Platz für Controls-Leiste
        const availW = document.documentElement.clientWidth  * 0.98;
        const availH = document.documentElement.clientHeight - controlsH;
        const scale  = Math.min(availW / (BASE_W * 2), availH / BASE_H);
        bookEl.style.transform       = `scale(${scale})`;
        bookEl.style.transformOrigin = 'center center';
        // Wrapper braucht explizite Größe damit das skalierte Buch zentriert bleibt
        wrapper.style.width  = (BASE_W * 2 * scale) + 'px';
        wrapper.style.height = (BASE_H  * scale) + 'px';
    }

    scaleBook();
    window.addEventListener('resize', scaleBook);
    document.addEventListener('fullscreenchange', () => setTimeout(scaleBook, 50));

    // ─── Inhaltsverzeichnis ────────────────────────────────────────────────────
    const toc = document.getElementById('toc-inject');
    const contents = document.querySelectorAll('.page-content');
    let tocHtml = '<ul style="list-style:none;padding:0;">';
    contents.forEach((c, i) => {
        const hd = c.querySelector('h1,h2,h3,h4,h5,h6');
        if (hd && i > 0) {
            const tag = hd.tagName.toLowerCase();
            tocHtml += `<li class="toc-item-${tag}">
                <a href="#" onclick="window.flipToPage(${i+2})" style="text-decoration:none;color:inherit;display:flex;justify-content:space-between;">
                    <${tag} style="margin:0;font-size:inherit;font-family:inherit;font-weight:inherit;">${hd.innerText}</${tag}>
                    <span>S. ${i+2}</span>
                </a></li>`;
        }
    });
    if (toc) toc.innerHTML = tocHtml + '</ul>';

    // ─── Vorlesen ──────────────────────────────────────────────────────────────
    const synth = window.speechSynthesis;
    let isReading = false;
    function stop() {
        synth.cancel(); isReading = false;
        document.getElementById('btn-speak').innerText = "▶ Vorlesen";
    }
    document.getElementById('btn-speak').addEventListener('click', () => {
        if (synth.speaking) { stop(); return; }
        isReading = true;
        const idx   = pageFlip.getCurrentPageIndex();
        const pages = document.querySelectorAll('.page-content');
        let txt = pages[idx].innerText;
        if (idx > 0 && idx + 1 < pages.length) txt += " " + pages[idx+1].innerText;
        const u = new SpeechSynthesisUtterance(txt);
        u.lang = 'de-DE';
        u.onend = () => {
            if (isReading && idx + 2 < pages.length) {
                pageFlip.flipNext();
                setTimeout(() => document.getElementById('btn-speak').click(), 1200);
            } else stop();
        };
        synth.speak(u);
        document.getElementById('btn-speak').innerText = "■ Stop";
    });

    // ─── Dark / Zen ────────────────────────────────────────────────────────────
    document.getElementById('btn-dark-mode').addEventListener('click', () => document.body.classList.toggle('dark-mode'));
    document.getElementById('btn-zen').addEventListener('click',       () => document.body.classList.toggle('zen-mode'));
    document.addEventListener('keydown', e => { if (e.key === "Escape") document.body.classList.remove('zen-mode'); });

    // ─── Vollbild-Button ───────────────────────────────────────────────────────
    const btnFS = document.getElementById('btn-fullscreen');
    btnFS.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            btnFS.innerText = '✕ Vollbild';
        } else {
            document.exitFullscreen();
            btnFS.innerText = '⛶ Vollbild';
        }
    });
    document.addEventListener('fullscreenchange', () => {
        if (!document.fullscreenElement) btnFS.innerText = '⛶ Vollbild';
    });

    // ─── Lesezeichen ───────────────────────────────────────────────────────────
    document.getElementById('btn-bookmark').addEventListener('click', () => {
        localStorage.setItem('u_book', pageFlip.getCurrentPageIndex());
        alert('Lesezeichen gesetzt!');
    });

    // ─── Navigation ────────────────────────────────────────────────────────────
    document.getElementById('btn-prev').addEventListener('click', () => { stop(); pageFlip.flipPrev(); });
    document.getElementById('btn-next').addEventListener('click', () => { stop(); pageFlip.flipNext(); });
    document.getElementById('btn-toc' ).addEventListener('click', () => { stop(); pageFlip.flip(1);   });
    window.flipToPage = n => { stop(); pageFlip.flip(n); };

    pageFlip.on('flip', e => {
        document.getElementById('page-info').innerText = "Seite " + (e.data + 1);
    });

    // ─── Schrift- und Bildgröße ────────────────────────────────────────────────
    const sizes = [
        { label: "🔤 A",  font: "16px", img: "50vh", bookImg: "40vh" },
        { label: "🔤 A+", font: "21px", img: "70vh", bookImg: "55vh" },
        { label: "🔤 A++",font: "26px", img: "85vh", bookImg: "70vh" }
    ];
    let sizeIdx = 1; // Standard: mittlere Größe

    function applySize(idx) {
        const s = sizes[idx];
        document.documentElement.style.setProperty("--font-size",   s.font);
        document.documentElement.style.setProperty("--img-height",  s.img);
        document.documentElement.style.setProperty("--bimg-height", s.bookImg);
        document.getElementById("btn-fontsize").innerText = s.label;
        localStorage.setItem("u_fontsize", idx);
    }

    document.getElementById("btn-fontsize").addEventListener("click", () => {
        sizeIdx = (sizeIdx + 1) % sizes.length;
        applySize(sizeIdx);
    });

    const savedSize = localStorage.getItem("u_fontsize");
    if (savedSize !== null) sizeIdx = parseInt(savedSize);
    applySize(sizeIdx);

    const saved = localStorage.getItem("u_book");
    if (saved) setTimeout(() => { if (confirm('Lesezeichen laden?')) pageFlip.turnToPage(parseInt(saved)); }, 1000);
});
