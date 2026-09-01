#!/usr/bin/env python3
"""Rasterizza il lockup (marchio + wordmark) e il solo marchio per Word.

Word non compone un lockup: non allinea un SVG a un testo con tracking, e
non regge un SVG in intestazione su tutte le versioni. Il lockup entra
quindi come PNG a 8x, composto qui con le stesse regole di `.tr-brandmark`:
marchio da `assets/logo-traccia-mark.svg` (tracciati letti dal file, non
ricopiati), gap `--tr-space-3` (12px), wordmark Archivo 800 con tracking
`--tr-tracking-wordmark` (0.08em) in `ink/900`.

Produce, accanto a questo script:
  brandmark-lockup.png        testata prima pagina   (28px marchio / 17px wordmark, come .tr-brandmark)
  brandmark-lockup-small.png  testata pagine interne (20px / 13px, come .tr-footer .tr-brandmark)
  mark.png                    solo marchio, per il colophon (come .tr-doc-footer__mark)
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = ROOT / "assets/fonts/ttf/Archivo-ExtraBold.ttf"
MARK = ROOT / "assets/logo-traccia-mark.svg"

S = 8                 # 1 px CSS = 8 px immagine
INK_900 = "#1b1f2a"
BRAND = "#4194d7"
GAP = 12              # --tr-space-3
TRACKING = 0.08       # --tr-tracking-wordmark
WORD = "LA TRACCIA"
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


def lockup(mark_px, word_px, out):
    font = ImageFont.truetype(str(FONT), word_px * S)
    ls = TRACKING * word_px * S
    mark_h = mark_px * S
    mark_w = mark_h * VB_W / VB_H
    text_w = sum(font.getlength(c) + ls for c in WORD) - ls
    W, H = int(mark_w + GAP * S + text_w) + 2, int(mark_h)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_mark(d, 0, mark_h)
    # il wordmark si centra sull'altezza delle maiuscole, non sul box del font
    bb = font.getbbox("L")
    y = (H - (bb[3] - bb[1])) / 2 - bb[1]
    x = mark_w + GAP * S
    for c in WORD:
        d.text((x, y), c, font=font, fill=INK_900)
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
    lockup(28, 17, HERE / "brandmark-lockup.png")
    lockup(20, 13, HERE / "brandmark-lockup-small.png")
    mark_only(20, HERE / "mark.png")
