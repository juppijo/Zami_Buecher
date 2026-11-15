#!/usr/bin/env python3
"""
Bettet ein Coverbild (z. B. cover.jpg) in eine EPUB-Datei ein.

Benutzung:
    python epub_add_cover.py buch.epub
    python epub_add_cover.py buch.epub mein_cover.jpg
    python epub_add_cover.py buch.epub cover.jpg -o buch_mit_cover.epub

Ohne -o wird "<name>_cover.epub" neben der Originaldatei erzeugt.
Keine externen Abhängigkeiten (nur Standardbibliothek).
Funktioniert mit EPUB 2 und EPUB 3.
"""

import argparse
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote

MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
}


def find_opf_path(zf: zipfile.ZipFile) -> str:
    container = zf.read("META-INF/container.xml").decode("utf-8")
    m = re.search(r'full-path\s*=\s*["\']([^"\']+)["\']', container)
    if not m:
        raise ValueError("OPF-Datei in container.xml nicht gefunden.")
    return unquote(m.group(1))


def get_attr(tag: str, name: str):
    m = re.search(rf'\b{name}\s*=\s*(["\'])(.*?)\1', tag, re.S)
    return m.group(2) if m else None


def find_existing_cover_item(opf: str):
    """Gibt das <item .../>-Tag des vorhandenen Covers zurück (oder None)."""
    items = re.findall(r"<(?:\w+:)?item\b[^>]*?>", opf, re.S)

    # EPUB 3: properties="cover-image"
    for it in items:
        props = get_attr(it, "properties") or ""
        if "cover-image" in props.split():
            return it

    # EPUB 2: <meta name="cover" content="ID"/>
    cover_id = None
    for meta in re.findall(r"<(?:\w+:)?meta\b[^>]*?>", opf, re.S):
        if get_attr(meta, "name") == "cover":
            cover_id = get_attr(meta, "content")
            break
    if cover_id:
        for it in items:
            if get_attr(it, "id") == cover_id:
                media = get_attr(it, "media-type") or ""
                if media.startswith("image/"):
                    return it
    return None


def add_cover(epub_in: Path, cover: Path, epub_out: Path) -> None:
    ext = cover.suffix.lower()
    if ext not in MEDIA_TYPES:
        raise ValueError(f"Nicht unterstütztes Bildformat: {ext}")
    media_type = MEDIA_TYPES[ext]
    cover_bytes = cover.read_bytes()

    with zipfile.ZipFile(epub_in) as zin:
        opf_path = find_opf_path(zin)
        opf_dir = posixpath.dirname(opf_path)
        opf = zin.read(opf_path).decode("utf-8")
        names = set(zin.namelist())

        existing = find_existing_cover_item(opf)

        if existing:
            # Vorhandenes Cover an gleicher Stelle ersetzen,
            # damit bestehende Verweise (z. B. cover.xhtml) intakt bleiben.
            href = unquote(get_attr(existing, "href"))
            zip_cover_path = posixpath.normpath(posixpath.join(opf_dir, href))
            new_tag = re.sub(
                r'(media-type\s*=\s*)(["\']).*?\2',
                rf'\1"{media_type}"',
                existing,
            )
            opf = opf.replace(existing, new_tag, 1)
            print(f"Vorhandenes Cover ersetzt: {zip_cover_path}")
        else:
            # Neues Cover hinzufügen
            href = f"images/cover{ext}"
            n = 1
            while posixpath.normpath(posixpath.join(opf_dir, href)) in names:
                n += 1
                href = f"images/cover{n}{ext}"
            zip_cover_path = posixpath.normpath(posixpath.join(opf_dir, href))

            item = (
                f'<item id="cover-image" href="{quote(href)}" '
                f'media-type="{media_type}" properties="cover-image"/>'
            )
            if not re.search(r"</(?:\w+:)?manifest>", opf):
                raise ValueError("<manifest> in der OPF-Datei nicht gefunden.")
            opf = re.sub(
                r"(</(?:\w+:)?manifest>)", item + r"\n\1", opf, count=1
            )

            # EPUB-2-Kompatibilität: <meta name="cover" .../>
            has_meta = any(
                get_attr(m, "name") == "cover"
                for m in re.findall(r"<(?:\w+:)?meta\b[^>]*?>", opf, re.S)
            )
            if not has_meta:
                meta = '<meta name="cover" content="cover-image"/>'
                opf = re.sub(
                    r"(</(?:\w+:)?metadata>)", meta + r"\n\1", opf, count=1
                )
            print(f"Neues Cover hinzugefügt: {zip_cover_path}")

        # Neue EPUB schreiben (mimetype zuerst und unkomprimiert)
        with zipfile.ZipFile(epub_out, "w") as zout:
            if "mimetype" in names:
                zout.writestr(
                    zipfile.ZipInfo("mimetype"),
                    zin.read("mimetype"),
                    compress_type=zipfile.ZIP_STORED,
                )
            for info in zin.infolist():
                if info.filename in ("mimetype", zip_cover_path):
                    continue
                if info.filename == opf_path:
                    zout.writestr(info.filename, opf.encode("utf-8"),
                                  compress_type=zipfile.ZIP_DEFLATED)
                else:
                    zout.writestr(info, zin.read(info.filename),
                                  compress_type=zipfile.ZIP_DEFLATED)
            zout.writestr(zip_cover_path, cover_bytes,
                          compress_type=zipfile.ZIP_DEFLATED)


def main():
    p = argparse.ArgumentParser(description="Cover in EPUB einbetten")
    p.add_argument("epub", type=Path, help="Eingabe-EPUB")
    p.add_argument("cover", type=Path, nargs="?", default=Path("cover.jpg"),
                   help="Coverbild (Standard: cover.jpg)")
    p.add_argument("-o", "--output", type=Path, help="Ausgabe-EPUB")
    args = p.parse_args()

    if not args.epub.is_file():
        sys.exit(f"EPUB nicht gefunden: {args.epub}")
    if not args.cover.is_file():
        sys.exit(f"Coverbild nicht gefunden: {args.cover}")

    out = args.output or args.epub.with_name(args.epub.stem + "_cover.epub")
    add_cover(args.epub, args.cover, out)
    print(f"Fertig: {out}")


if __name__ == "__main__":
    main()
