#!/usr/bin/env python3
"""Rasterizza il lockup (marchio + wordmark) e il solo marchio per Word.

Word non compone un lockup: non allinea un SVG a un testo con tracking, e
non regge un SVG in intestazione su tutte le versioni. Il lockup entra
quindi come PNG a 8x, composto qui con le stesse regole di `.tr-brandmark`:
marchio da `assets/logo-traccia-mark.svg` (tracciati letti dal file, non
ricopiati), wordmark «traccia» minuscolo in Space Grotesk 700 con tracking
`--tr-tracking-wordmark` (-0.02em) in `ink/900`. Come nel CSS, scritta e
distanza si contano sull'altezza del marchio: 0,8 e 0,34.

Produce, accanto a questo script:
  brandmark-lockup.png        testata prima pagina   (marchio 28px, come .tr-brandmark)
  brandmark-lockup-small.png  testata pagine interne (marchio 20px, come .tr-footer .tr-brandmark)
  mark.png                    solo marchio, per il colophon (come .tr-doc-footer__mark)
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = ROOT / "assets/fonts/ttf/SpaceGrotesk-Bold.ttf"
MARK = ROOT / "assets/logo-traccia-mark.svg"

S = 8                 # 1 px CSS = 8 px immagine
INK_900 = "#1b1f2a"
BRAND = "#4194d7"
WORD_RATIO = 0.8     # scritta / altezza del marchio
GAP_RATIO = 0.34      # distanza / altezza del marchio
TRACKING = -0.02      # --tr-tracking-wordmark
WORD = "traccia"
VB_W, VB_H = 594, 717 # viewBox di logo-traccia-mark.svg


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
    for c in WORD:
        d.text((x, base), c, font=font, fill=INK_900, anchor="ls")
        x += font.getlength(c) + ls
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
