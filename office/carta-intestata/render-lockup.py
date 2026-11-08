#!/usr/bin/env python3
"""Rasterizza il lockup (marchio + wordmark) e il solo marchio per Word.

Word non compone un lockup: non allinea un SVG a un testo con tracking, e
non regge un SVG in intestazione su tutte le versioni. Il lockup entra
quindi come PNG a 8x, composto qui con le stesse regole di `.tr-brandmark`:
marchio da `assets/logo-traccia-mark.svg` (tracciati letti dal file, non
ricopiati), wordmark «traccia» minuscolo in Space Grotesk 700 con tracking
`--tr-tracking-wordmark` (-0.02em) in antracite (`--tr-color-wordmark`). Come nel CSS, scritta e
distanza si contano sull'altezza del marchio: 0,8 e 0,34. I tagli diagonali
su t, c e c vengono da tools/wordmark/intagli.py, con le stesse regole della
maschera CSS.

Produce, accanto a questo script:
  brandmark-lockup.png        testata prima pagina   (marchio 28px, come .tr-brandmark)
  brandmark-lockup-small.png  testata pagine interne (marchio 20px, come .tr-footer .tr-brandmark)
  mark.png                    solo marchio, per il colophon (come .tr-doc-footer__mark)
"""
import re
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = ROOT / "assets/fonts/ttf/SpaceGrotesk-Bold.ttf"
MARK = ROOT / "assets/logo-traccia-mark.svg"

S = 8                 # 1 px CSS = 8 px immagine
ANTHRACITE = "#383e42"  # --tr-color-wordmark
BRAND = "#4194d7"
WORD_RATIO = 0.8     # scritta / altezza del marchio
GAP_RATIO = 0.34      # distanza / altezza del marchio
TRACKING = -0.02      # --tr-tracking-wordmark
WORD = "traccia"
VB_W, VB_H = 594, 717 # viewBox di logo-traccia-mark.svg

sys.path.insert(0, str(ROOT / "tools/wordmark"))
import intagli  # noqa: E402  (richiede fonttools, uharfbuzz e shapely)


def mark_polygons():
    """Legge i due tracciati del marchio. Il secondo ha una curva C con punti
    di controllo quasi collineari: a queste dimensioni e' un poligono."""
    svg = MARK.read_text()
    polys = []
    for d in re.findall(r' d="([^"]+)"', svg):
        nums = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', d)]
        polys.append(list(zip(nums[0::2], nums[1::2])))
    return polys


def draw_mark(draw, x0, height):
    w = height * VB_W / VB_H
    sx, sy = w / VB_W, height / VB_H
    for poly in mark_polygons():
        draw.polygon([(x0 + x * sx, y * sy) for x, y in poly], fill=BRAND)
    return w


def lockup(mark_px, out):
    word = mark_px * WORD_RATIO * S
    font = ImageFont.truetype(str(FONT), round(word))
    ls = TRACKING * word
    mark_h = mark_px * S
    mark_w = mark_h * VB_W / VB_H
    gap = mark_h * GAP_RATIO
    text_w = sum(font.getlength(c) + ls for c in WORD) - ls
    W, H = int(mark_w + gap + text_w) + 2, int(mark_h)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_mark(d, 0, mark_h)
    # come il CSS (line-height 1, align-items center): si centra la riga, e
    # la linea di base cade a meta' interlinea piu' l'ascendente
    asc, desc = font.getmetrics()
    base = (H - word) / 2 + (word - asc - desc) / 2 + asc
    x = mark_w + gap
    xs = []
    for c in WORD:
        xs.append(x)
        d.text((x, base), c, font=font, fill=ANTHRACITE, anchor="ls")
        x += font.getlength(c) + ls
    # i tagli: uno per lettera su t, c e c, inclinati e spessi come il taglio
    # del marchio; poi le schegge
    fd = intagli.font_data()
    ct = intagli.cut(fd)
    k = word / fd["upm"]
    for i, pts in ct["blades"]:
        d.polygon([(xs[i] + px * k, base - py * k) for px, py in pts], fill=(0, 0, 0, 0))
    for i, (x0, y0, x1, y1) in ct["slivers"]:
        d.rectangle((xs[i] + x0 * k, base - y1 * k, xs[i] + x1 * k, base - y0 * k), fill=(0, 0, 0, 0))
    im.save(out)
    print(out.name, im.size)


def mark_only(mark_px, out):
    h = mark_px * S
    w = int(h * VB_W / VB_H) + 1
    im = Image.new("RGBA", (w, int(h)), (0, 0, 0, 0))
    draw_mark(ImageDraw.Draw(im), 0, h)
    im.save(out)
    print(out.name, im.size)


if __name__ == "__main__":
    lockup(28, HERE / "brandmark-lockup.png")
    lockup(20, HERE / "brandmark-lockup-small.png")
    mark_only(20, HERE / "mark.png")
