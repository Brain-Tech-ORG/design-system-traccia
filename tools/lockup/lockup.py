#!/usr/bin/env python3
"""Il logo completo La Traccia: marchio e scritta TRACCIA in un solo SVG.

Scrive assets/logo-traccia-lockup.svg. E' il logo per i casi in cui viaggia
come file (la presentazione di un partner, un documento di terzi, una stampa)
e non come componente: nelle interfacce, nelle testate e nei piedi resta il
lockup compatto `.tr-brandmark`.

Il marchio e' quello di assets/logo-traccia-mark.svg, ricopiato com'e'. La
scritta e' TRACCIA in maiuscolo esteso, Archivo Expanded Black (OFL, il font
sta qui accanto con la sua licenza), obliquo e convertito in tracciati: il
file non dipende da nessun font. Le proporzioni stanno sul marchio, non sul
testo:

- l'altezza delle maiuscole e' meta' di quella del triangolo piccolo del
  marchio: dal suo bordo alto alla quota del suo vertice destro; la scritta
  poggia su quella quota;
- l'ultima lettera finisce a 0,45 volte l'altezza delle maiuscole dal lato
  sinistro del triangolo (il marchio sta a destra e la parola entra sotto lo
  sbalzo della barra);
- la scritta e' obliqua di 12 gradi, con 0,06 di tracking e il kerning del
  font (HarfBuzz);
- la linea di intermezzo e' un taglio orizzontale al 45% dell'altezza delle
  maiuscole, spesso il 5,5%, e attraversa solo alcune lettere: la T, le due
  C e l'ultima A. R, A e I restano intere;
- la scritta e' di un solo colore, ink/400 (--tr-ink-400): nessun blu dentro
  il testo. Sfondo trasparente: il logo e' per fondi chiari.

Il file non si edita a mano: si cambia questo generatore e lo si rilancia.

Dipendenze (provato con fonttools 4.68, uharfbuzz 0.57, shapely 2.2):

    pip install fonttools uharfbuzz shapely
    python3 tools/lockup/lockup.py
"""
import math
import re
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = HERE / "Archivo-ExpandedBlack.ttf"
MARK = ROOT / "assets/logo-traccia-mark.svg"
OUT = ROOT / "assets/logo-traccia-lockup.svg"

BRAND = "#4194d7"       # --tr-brand-500, il blu del marchio
TEXT = "#565c6b"        # --tr-ink-400, l'unico colore della scritta
WORD = "TRACCIA"
CAP = 1000.0            # unita' di disegno: altezza delle maiuscole
SLANT = 12              # inclinazione, gradi
TRACKING = 0.06         # fra le lettere, in altezze di maiuscola
CUT_LETTERS = (0, 3, 4, 6)   # T, C, C, A (l'ultima)
CUT_AT = 0.45           # quota del taglio, in altezze di maiuscola
CUT_W = 0.055           # spessore del taglio, in altezze di maiuscola
END_GAP = 0.45          # ultima lettera -> lato sinistro del triangolo, in altezze di maiuscola
SIMPLIFY = 0.3          # tolleranza di semplificazione dei tracciati, unita' di disegno

# Fascia delle maiuscole nel viewBox del marchio (594 x 717): dal bordo alto
# del triangolo alla quota del suo vertice destro. Il vertice sta a y = 538,4;
# la linea di base e' 538,44 per restare identica al file consegnato il
# 29/10/2026 (la differenza, 0,04 su 717, non si vede).
MARK_W, MARK_H = 594, 717
BAND_TOP, BAND_BOTTOM = 362.40, 538.44
TRI_LEFT = 183.1        # lato sinistro del triangolo, nel viewBox del marchio

DESC = "Logo La Traccia: marchio (chevron) e wordmark TRACCIA in tracciati. Fondo trasparente, per fondi chiari."


class Flatten(BasePen):
    """Appiattisce i contorni di un glifo in poligoni (20 segmenti per curva)."""

    def __init__(self, glyph_set, steps=20):
        super().__init__(glyph_set)
        self.contours, self.cur, self.steps = [], None, steps

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            m = 1 - t
            self.cur.append((m**3 * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t**3 * p3[0],
                             m**3 * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t**3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            m = 1 - t
            self.cur.append((m * m * p0[0] + 2 * m * t * p1[0] + t * t * p2[0],
                             m * m * p0[1] + 2 * m * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if self.cur and len(self.cur) >= 3:
            self.contours.append(self.cur)
        self.cur = None

    def _endPath(self):
        self._closePath()


def glyph(glyph_set, name):
    """Il glifo come geometria piana: i contorni interni sono buchi."""
    pen = Flatten(glyph_set)
    glyph_set[name].draw(pen)
    polys = sorted((Polygon(c).buffer(0) for c in pen.contours), key=lambda p: -p.area)
    shells = []
    for p in polys:
        if p.is_empty:
            continue
        for s in shells:
            if p.within(s[0]):
                s[1].append(p)
                break
        else:
            shells.append([p, []])
    out = []
    for shell, holes in shells:
        g = shell
        for h in holes:
            g = g.difference(h)
        out.append(g)
    return unary_union(out) if out else Polygon()


def word():
    """TRACCIA composta, con le linee di intermezzo e l'inclinazione."""
    tt = TTFont(FONT)
    glyph_set, order = tt.getGlyphSet(), tt.getGlyphOrder()
    t_pen = Flatten(glyph_set)
    glyph_set[tt.getBestCmap()[ord("T")]].draw(t_pen)
    s = CAP / max(y for c in t_pen.contours for _, y in c)   # unita' del font -> unita' di disegno

    buf = hb.Buffer()
    buf.add_str(WORD)
    buf.guess_segment_properties()
    hb.shape(hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT)))), buf, {"kern": True, "liga": False})

    parts, x = [], 0.0
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        g = affinity.scale(glyph(glyph_set, order[info.codepoint]), s, s, origin=(0, 0))
        g = affinity.translate(g, x + pos.x_offset * s, pos.y_offset * s)
        if i in CUT_LETTERS:
            y, h = CUT_AT * CAP, CUT_W * CAP / 2
            g = g.difference(box(-1e5, y - h, 1e5, y + h))
        parts.append(g)
        x += pos.x_advance * s + TRACKING * CAP
    shear = math.tan(math.radians(SLANT))
    return unary_union([affinity.affine_transform(g, [1, shear, 0, 1, 0, 0]) for g in parts])


def num(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def path_d(geom, tf):
    polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            d.append("M" + " ".join(f"{num(x)} {num(y)}" for x, y in (tf(x, y) for x, y in ring.coords[:-1])) + "Z")
    return "".join(d)


def svg():
    w = word()
    minx, _, maxx, _ = w.bounds
    s = (BAND_BOTTOM - BAND_TOP) / CAP                  # unita' di disegno -> unita' del marchio
    word_w = (maxx - minx) * s
    mark_dx = word_w + END_GAP * CAP * s - TRI_LEFT     # dove sta il marchio, a destra della scritta
    width = mark_dx + MARK_W
    mark = re.findall(r' d="([^"]+)"', MARK.read_text())
    assert len(mark) == 2, "assets/logo-traccia-mark.svg: attesi due tracciati"
    d = path_d(w.simplify(SIMPLIFY, preserve_topology=True), lambda x, y: ((x - minx) * s, BAND_BOTTOM - y * s))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(width)} {MARK_H}" '
        f'width="{num(width)}" height="{MARK_H}" role="img" aria-label="La Traccia">\n'
        f'  <title>La Traccia</title>\n'
        f'  <desc>{DESC}</desc>\n'
        f'  <g fill="{BRAND}" transform="translate({num(mark_dx)} 0)">\n'
        f'    <path d="{mark[0]}"/>\n    <path d="{mark[1]}"/>\n  </g>\n'
        f'  <path fill="{TEXT}" fill-rule="evenodd" d="{d}"/>\n</svg>\n'
    )


if __name__ == "__main__":
    OUT.write_text(svg())
    print(f"scritto {OUT.relative_to(ROOT)}")
