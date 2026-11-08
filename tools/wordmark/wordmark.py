#!/usr/bin/env python3
"""Il wordmark TRACCIA: disegnato, non composto.

La scritta accanto al marchio e' TRACCIA, maiuscolo, in Servetica Medium
(Zenze Media, 2011, disegno di Brandon Landaal; Servetica e' un marchio di
Cleanvertising.com). Servetica e' uno stencil e i tagli sono quelli del
font: in TRACCIA la barra della T e' staccata dall'asta, la pancia della R e
il triangolo delle A sono aperti. Nessun taglio aggiunto da noi.

La scritta non e' testo composto nel browser: e' disegnata. Lo script
converte le sette lettere in tracciati e scrive:

- assets/logo-traccia-completo.svg: il logo completo, marchio e scritta, per
  fondi chiari. E' il file che viaggia (presentazioni, documenti di terzi,
  stampa) e la sorgente del PNG della carta intestata;
- in css/traccia.css, fra i commenti `wordmark:inizio` e `wordmark:fine`, la
  scritta come maschera (SVG in data URI) e la sua larghezza in em. Il
  componente la colora con il colore del testo (antracite sui fondi chiari,
  bianco sul blu); il testo «traccia» del markup resta per gli screen reader.

Proporzioni, quelle della prova scelta l'8/11/2026:

- corpo della scritta 0,5 dell'altezza del marchio: le maiuscole sono alte
  0,357 del marchio (714 unita' su 1000);
- nessun tracking; la crenatura e' quella del font (HarfBuzz, come il
  browser: in TRACCIA non ci sono coppie crenate);
- distanza dal marchio 0,34 della sua altezza;
- la riga della scritta (alta 1em, linea di base a 714/1000 dall'alto, come
  nel browser con line-height 1) e' centrata sul marchio.

IL FONT NON STA NEL REPOSITORY. Il file non porta una licenza (nel campo:
«From www.cleanvertising.com»), i suoi permessi di incorporamento sono solo
anteprima e stampa (fsType 4) e il produttore dichiarato e' Linotype
(achVendID LINO). Nel sistema entrano i tracciati delle sette lettere, non il
font. Per rigenerare, mettere il file in tools/wordmark/Servetica-Medium.ttf
(ignorato da git) e lanciare:

    pip install fonttools uharfbuzz
    python3 tools/wordmark/wordmark.py

I file scritti non si editano a mano: si cambia questo script e lo si rilancia.
"""
import re
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = HERE / "Servetica-Medium.ttf"
MARK = ROOT / "assets/logo-traccia-mark.svg"
CSS = ROOT / "css/traccia.css"
LOCKUP = ROOT / "assets/logo-traccia-completo.svg"

WORD = "TRACCIA"
SIZE = 0.5               # corpo della scritta / altezza del marchio
GAP = 0.34               # distanza dal marchio / altezza del marchio
BRAND = "#4194d7"        # --tr-brand-500, il blu del marchio
TEXT = "#383e42"         # --tr-color-wordmark, antracite (RAL 7016)


def num(n, digits=2):
    s = f"{n:.{digits}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def word(transform=(1, 0, 0, 1, 0, 0)):
    """TRACCIA in tracciati. Coordinate della riga alta 1em (unita' del font,
    y verso il basso, linea di base come nel browser), poi `transform`."""
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    assert FONT.exists(), f"manca {FONT.relative_to(ROOT)}: il font non sta nel repository (vedi in cima)"
    tt = TTFont(FONT)
    upm = tt["head"].unitsPerEm
    os2, hhea = tt["OS/2"], tt["hhea"]
    use_typo = bool(os2.fsSelection & (1 << 7))
    asc, desc = (os2.sTypoAscender, -os2.sTypoDescender) if use_typo else (hhea.ascent, -hhea.descent)
    baseline = (upm - asc - desc) / 2 + asc

    buf = hb.Buffer()
    buf.add_str(WORD)
    buf.guess_segment_properties()
    hb.shape(hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT)))), buf)

    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    a, b, c, d, e, f = transform
    pen = SVGPathPen(gs, ntos=num)
    x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gx, gy = x + pos.x_offset, baseline - pos.y_offset
        # glifo (y in su) -> riga (y in giu') -> transform
        tf = (a, b, -c, -d, a * gx + c * gy + e, b * gx + d * gy + f)
        gs[order[info.codepoint]].draw(TransformPen(pen, tf))
        x += pos.x_advance
    return {"d": pen.getCommands(), "width": x, "upm": upm}


def mark():
    svg = MARK.read_text()
    w, h = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()[2:])
    paths = re.findall(r' d="([^"]+)"', svg)
    assert len(paths) == 2, "assets/logo-traccia-mark.svg: attesi due tracciati (barra e triangolo)"
    return w, h, paths


def lockup_svg():
    mw, mh, paths = mark()
    k = SIZE * mh / 1000                      # unita' del font -> unita' del marchio (upm 1000)
    x0, y0 = mw + GAP * mh, (mh - SIZE * mh) / 2
    w = word((k, 0, 0, k, x0, y0))
    assert w["upm"] == 1000
    width = x0 + w["width"] * k
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(width)} {num(mh)}" '
        f'width="{num(width)}" height="{num(mh)}" role="img" aria-label="La Traccia">\n'
        "  <title>La Traccia</title>\n"
        "  <desc>Logo completo La Traccia: marchio e scritta TRACCIA (Servetica Medium) in tracciati. "
        "Per fondi chiari. Scritto da tools/wordmark/wordmark.py.</desc>\n"
        f'  <path fill="{BRAND}" d="{paths[0]}"/>\n'
        f'  <path fill="{BRAND}" d="{paths[1]}"/>\n'
        f'  <path fill="{TEXT}" fill-rule="evenodd" d="{w["d"]}"/>\n'
        "</svg>\n"
    )


def css_block():
    w = word()
    mask = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {num(w['width'])} {num(w['upm'])}'>"
            f"<path fill-rule='evenodd' d='{w['d']}'/></svg>")
    uri = "data:image/svg+xml," + quote(mask, safe=" =:/'.,-")
    return (
        "/* wordmark:inizio — scritto da tools/wordmark/wordmark.py, non editare a mano */\n"
        ".tr-brandmark__wordmark,\n"
        ".tr-spinner__wordmark {\n"
        f'  --tr-wordmark: url("{uri}");\n'
        f"  width: {num(w['width'] / w['upm'], 4)}em;\n"
        "}\n"
        "/* wordmark:fine */"
    )


if __name__ == "__main__":
    LOCKUP.write_text(lockup_svg())
    css = CSS.read_text()
    new, n = re.subn(r"/\* wordmark:inizio.*?/\* wordmark:fine \*/", lambda _: css_block(), css, flags=re.S)
    assert n == 1, "css/traccia.css: attesi i commenti wordmark:inizio / wordmark:fine una volta"
    CSS.write_text(new)
    print(f"scritti {LOCKUP.relative_to(ROOT)} e il wordmark in {CSS.relative_to(ROOT)}")
