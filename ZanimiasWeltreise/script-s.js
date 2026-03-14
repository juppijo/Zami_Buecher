
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
