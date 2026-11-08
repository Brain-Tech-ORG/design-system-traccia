#!/usr/bin/env python3
"""Rasterizza il lockup (marchio + wordmark) e il solo marchio per Word.

Word non compone un lockup: non allinea un SVG a un testo, e non regge un
SVG in intestazione su tutte le versioni. Il lockup entra quindi come PNG a
8x, ricavato da `assets/logo-traccia-completo.svg`: il logo completo, marchio
e scritta TRACCIA gia' in tracciati, con le proporzioni di `.tr-brandmark`
(scritta di corpo 0,5 e distanza 0,34 dell'altezza del marchio). Lo scrive
tools/wordmark/wordmark.py; qui lo si legge e basta, quindi serve solo Pillow.

Produce, accanto a questo script:
  brandmark-lockup.png        testata prima pagina   (marchio 28px, come .tr-brandmark)
  brandmark-lockup-small.png  testata pagine interne (marchio 20px, come .tr-footer .tr-brandmark)
  mark.png                    solo marchio, per il colophon (come .tr-doc-footer__mark)
"""
import re
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MARK = ROOT / "assets/logo-traccia-mark.svg"
LOCKUP = ROOT / "assets/logo-traccia-completo.svg"

S = 8                 # 1 px CSS = 8 px immagine
BRAND = "#4194d7"
VB_W, VB_H = 594, 717 # viewBox di logo-traccia-mark.svg
STEPS = 16            # segmenti per curva


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


def rings(d):
    """Un tracciato SVG (comandi assoluti M L H V Q C Z, come li scrive
    wordmark.py) in anelli di punti, con le curve appiattite."""
    toks = re.findall(r"[MLHVQCZ]|-?\d*\.?\d+", d)
    out, cur, cmd, i = [], [], None, 0
    x = y = 0.0

    def take(n):
        nonlocal i
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        return vals

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                if cur:
                    out.append(cur)
                cur = []
                continue
        if cmd == "M":
            if cur:
                out.append(cur)
            x, y = take(2)
            cur = [(x, y)]
            cmd = "L"                       # le coppie dopo M sono linee
        elif cmd == "L":
            x, y = take(2)
            cur.append((x, y))
        elif cmd == "H":
            (x,) = take(1)
            cur.append((x, y))
        elif cmd == "V":
            (y,) = take(1)
            cur.append((x, y))
        elif cmd == "Q":
            x1, y1, x2, y2 = take(4)
            for k in range(1, STEPS + 1):
                t = k / STEPS
                m = 1 - t
                cur.append((m * m * x + 2 * m * t * x1 + t * t * x2, m * m * y + 2 * m * t * y1 + t * t * y2))
            x, y = x2, y2
        elif cmd == "C":
            x1, y1, x2, y2, x3, y3 = take(6)
            for k in range(1, STEPS + 1):
                t = k / STEPS
                m = 1 - t
                cur.append((m**3 * x + 3 * m * m * t * x1 + 3 * m * t * t * x2 + t**3 * x3,
                            m**3 * y + 3 * m * m * t * y1 + 3 * m * t * t * y2 + t**3 * y3))
            x, y = x3, y3
        else:
            raise ValueError(f"comando SVG non previsto: {cmd}")
    if cur:
        out.append(cur)
    return out


def lockup(mark_px, out):
    svg = LOCKUP.read_text()
    vb_w, vb_h = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()[2:])
    k = mark_px * S / vb_h
    W, H = int(vb_w * k) + 2, int(mark_px * S)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paths = re.findall(r'<path fill="([^"]+)"(?: fill-rule="evenodd")? d="([^"]+)"', svg)
    assert len(paths) == 3, "logo-traccia-completo.svg: attesi tre tracciati (barra, triangolo, scritta)"
    for fill, d in paths:
        # riempimento pari-dispari, come nel file: un anello dentro un altro e' un buco
        mask = Image.new("1", (W, H), 0)
        for ring in rings(d):
            m = Image.new("1", (W, H), 0)
            ImageDraw.Draw(m).polygon([(px * k, py * k) for px, py in ring], fill=1)
            mask = ImageChops.logical_xor(mask, m)
        im.paste(fill, mask=mask)
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
