#!/usr/bin/env python3
"""Gli intagli del wordmark «traccia»: la linea di intermezzo nelle lettere.

La scritta accanto al marchio e' testo vivo (Space Grotesk 700, minuscolo,
tracking -0.02em): resta selezionabile, leggibile dagli screen reader, e il
colore lo decide il CSS (antracite sui fondi chiari, bianco sul blu). Gli
intagli non cambiano niente di questo: sono una maschera sopra il testo, che
lascia trasparente una fascia orizzontale in alcune lettere.

Le regole sono quelle della linea di intermezzo del logo esteso TRACCIA,
riportate sulle minuscole:

- il taglio e' orizzontale, al 45% dell'altezza delle lettere dalla linea di
  base, spesso il 5,5% di quell'altezza. In minuscolo l'altezza delle lettere
  e' la x-height del font (486 unita' su 1000), non quella delle maiuscole;
- attraversa solo la t, le due c e l'ultima a. R, prima a e i restano intere;
- non tocca le lettere vicine: ogni taglio copre l'ingombro della propria
  lettera piu' un margine, e lo script verifica che non arrivi alle altre.

Lo script compone la parola come il browser (HarfBuzz, kerning attivo,
legature spente come fa il browser con il letter-spacing, tracking dopo ogni
lettera) e scrive la maschera, come SVG in data URI, in css/traccia.css fra i
commenti `intagli:inizio` e `intagli:fine`. La maschera si estende in
larghezza sulla scritta (100%) ed e' alta 1em centrata in verticale: vale per
qualsiasi interlinea, perche' il browser centra il testo nella riga allo
stesso modo.

Le costanti qui sotto le legge anche office/carta-intestata/render-lockup.py,
che rasterizza il lockup per Word con gli stessi tagli.

La maschera non si edita a mano: si cambia questo script e lo si rilancia.

Dipendenze (provato con fonttools 4.60, uharfbuzz 0.53):

    pip install fonttools uharfbuzz
    python3 tools/wordmark/intagli.py
"""
import re
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = ROOT / "assets/fonts/ttf/SpaceGrotesk-Bold.ttf"
CSS = ROOT / "css/traccia.css"

WORD = "traccia"
TRACKING = -0.02            # --tr-tracking-wordmark, in em
CUT_LETTERS = (0, 3, 4, 6)  # t, c, c, a (l'ultima)
CUT_AT = 0.45               # quota del taglio, in altezze di lettera (x-height) dalla linea di base
CUT_W = 0.055               # spessore del taglio, in altezze di lettera
PAD = 8                     # margine del taglio oltre l'ingombro della lettera, unita' del font


def font_data():
    """Metriche e glifi della parola, in unita' del font."""
    import uharfbuzz as hb
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.ttLib import TTFont

    tt = TTFont(FONT)
    upm = tt["head"].unitsPerEm
    os2, hhea = tt["OS/2"], tt["hhea"]
    use_typo = bool(os2.fsSelection & (1 << 7))
    asc, desc = (os2.sTypoAscender, -os2.sTypoDescender) if use_typo else (hhea.ascent, -hhea.descent)

    buf = hb.Buffer()
    buf.add_str(WORD)
    buf.guess_segment_properties()
    hb.shape(hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT)))), buf, {"kern": True, "liga": False})

    order, gs = tt.getGlyphOrder(), tt.getGlyphSet()
    letters, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = BoundsPen(gs)
        gs[order[info.codepoint]].draw(pen)
        xmin, _, xmax, _ = pen.bounds
        letters.append({"x": x, "ink": (x + xmin, x + xmax), "rel": (xmin, xmax)})
        x += pos.x_advance + TRACKING * upm
    return {"upm": upm, "asc": asc, "desc": desc, "xh": os2.sxHeight, "width": x, "letters": letters}


def band(xh):
    """La fascia del taglio, sopra la linea di base: (da, a), unita' del font."""
    mid, half = CUT_AT * xh, CUT_W * xh / 2
    return mid - half, mid + half


def cuts(fd):
    """I rettangoli dei tagli nella riga alta 1em (line-height 1): x0, y0, x1, y1."""
    upm, letters = fd["upm"], fd["letters"]
    baseline = (upm - fd["asc"] - fd["desc"]) / 2 + fd["asc"]   # dall'alto, come il browser
    lo, hi = band(fd["xh"])
    out = []
    for i in CUT_LETTERS:
        x0, x1 = letters[i]["ink"][0] - PAD, letters[i]["ink"][1] + PAD
        for j in (i - 1, i + 1):
            if 0 <= j < len(letters) and j not in CUT_LETTERS:
                nx0, nx1 = letters[j]["ink"]
                assert x1 < nx0 or x0 > nx1, f"il taglio della lettera {i} arriva alla lettera {j}"
        out.append((x0, baseline - hi, x1, baseline - lo))
    return out


def num(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def mask_svg(fd):
    """Maschera alfa: tutto opaco, i tagli trasparenti (buchi evenodd)."""
    w, h = fd["width"], fd["upm"]
    d = f"M0 0H{num(w)}V{num(h)}H0Z"
    for x0, y0, x1, y1 in cuts(fd):
        d += f"M{num(x0)} {num(y0)}H{num(x1)}V{num(y1)}H{num(x0)}Z"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {num(w)} {num(h)}' "
            f"preserveAspectRatio='none'><path fill-rule='evenodd' d='{d}'/></svg>")


def css_block(fd):
    uri = "data:image/svg+xml," + quote(mask_svg(fd), safe=" =:/'.,-")
    return (
        "/* intagli:inizio — scritto da tools/wordmark/intagli.py, non editare a mano */\n"
        ".tr-brandmark__wordmark,\n"
        ".tr-spinner__wordmark {\n"
        f'  --tr-wordmark-cuts: url("{uri}");\n'
        "  -webkit-mask: var(--tr-wordmark-cuts) left center / 100% 1em no-repeat;\n"
        "          mask: var(--tr-wordmark-cuts) left center / 100% 1em no-repeat;\n"
        "}\n"
        "/* intagli:fine */"
    )


if __name__ == "__main__":
    fd = font_data()
    css = CSS.read_text()
    new, n = re.subn(r"/\* intagli:inizio.*?/\* intagli:fine \*/", lambda _: css_block(fd), css, flags=re.S)
    assert n == 1, "css/traccia.css: attesi i commenti intagli:inizio / intagli:fine una volta"
    CSS.write_text(new)
    print(f"scritti {len(CUT_LETTERS)} tagli in {CSS.relative_to(ROOT)}")
