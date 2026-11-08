#!/usr/bin/env python3
"""Il taglio del wordmark «traccia»: le lettere tagliate come il marchio.

La scritta accanto al marchio e' testo vivo (Space Grotesk 700, minuscolo,
tracking -0.02em): resta selezionabile, leggibile dagli screen reader, e il
colore lo decide il CSS (antracite sui fondi chiari, bianco sul blu). Il
taglio non cambia niente di questo: e' una maschera sopra il testo.

Il marchio e' una freccia tagliata: un taglio bianco, in diagonale, la divide
in due pezzi. La scritta porta lo stesso taglio, e tutto si legge sul marchio:

- il taglio e' diagonale, inclinato come il taglio del marchio (circa 41
  gradi, scende verso destra);
- e' spesso quanto il taglio del marchio, nelle proporzioni del lockup
  (.tr-brandmark: scritta alta 0,8 del marchio);
- e' uno per lettera, e passa per il centro della lettera: a meta' della
  x-height, al centro del suo ingombro;
- taglia solo la t e le due c. R, a e i restano intere: la a e' stata
  provata e scartata;
- resta nella propria lettera: non arriva alle lettere vicine;
- dove lascerebbe una scheggia (un pezzo di lettera sotto l'1% della
  lettera), la scheggia si toglie.

Angolo e spessore si leggono da assets/logo-traccia-mark.svg: se cambia il
marchio, si rilancia lo script e il taglio lo segue.

Lo script compone la parola come il browser (HarfBuzz, kerning attivo,
legature spente come fa il browser con il letter-spacing, tracking dopo ogni
lettera) e scrive la maschera, come SVG in data URI, in css/traccia.css fra i
commenti `intagli:inizio` e `intagli:fine`. La maschera si estende in
larghezza sulla scritta (100%) ed e' alta 1em centrata in verticale: vale per
qualsiasi interlinea, perche' il browser centra il testo nella riga allo
stesso modo.

office/carta-intestata/render-lockup.py usa le stesse funzioni per il PNG del
lockup in Word.

La maschera non si edita a mano: si cambia questo script e lo si rilancia.

Dipendenze (provato con fonttools 4.60, uharfbuzz 0.53, shapely 2.1):

    pip install fonttools uharfbuzz shapely
    python3 tools/wordmark/intagli.py
"""
import math
import re
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FONT = ROOT / "assets/fonts/ttf/SpaceGrotesk-Bold.ttf"
MARK = ROOT / "assets/logo-traccia-mark.svg"
CSS = ROOT / "css/traccia.css"

WORD = "traccia"
TRACKING = -0.02         # --tr-tracking-wordmark, in em
WORD_RATIO = 0.8         # altezza della scritta (1em) / altezza del marchio, come .tr-brandmark
CUT_LETTERS = (0, 3, 4)  # t, c, c
CUT_AT = 0.5             # centro del taglio, in x-height sopra la linea di base
SLIVER = 0.01            # un pezzo di lettera sotto l'1% della lettera e' una scheggia
SLIVER_PAD = 4           # margine attorno alla scheggia tolta, unita' del font
STEPS = 24               # segmenti per curva, per riconoscere le schegge


def mark_geometry():
    """Dal marchio: altezza, spessore e inclinazione del taglio interno."""
    svg = MARK.read_text()
    h = float(re.search(r'viewBox="([^"]+)"', svg).group(1).split()[3])
    paths = re.findall(r' d="([^"]+)"', svg)
    assert len(paths) == 2, "assets/logo-traccia-mark.svg: attesi due tracciati (barra e triangolo)"
    bar, tri = ([(n[i], n[i + 1]) for i in range(0, len(n), 2)]
                for n in ([float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)] for d in paths))
    # il taglio interno sta fra il lato basso della barra (dal vertice a
    # sinistra a quello piu' in basso) e il lato alto del triangolo (dal
    # vertice in alto a quello a destra). I due lati non sono del tutto
    # paralleli: spessore e inclinazione sono la media.
    a, b = min(bar, key=lambda p: p[0]), max(bar, key=lambda p: p[1])
    top, right = min(tri, key=lambda p: p[1]), max(tri, key=lambda p: p[0])
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    nx, ny = -(b[1] - a[1]) / length, (b[0] - a[0]) / length
    gap = sum((q[0] - a[0]) * nx + (q[1] - a[1]) * ny for q in (top, right)) / 2
    angle = (math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
             + math.degrees(math.atan2(right[1] - top[1], right[0] - top[0]))) / 2
    return {"h": h, "gap": gap, "angle": angle}


def _glyph_geometry(glyph_set, name):
    """Il glifo come geometria piana (shapely), unita' del font, y in su."""
    from fontTools.pens.basePen import BasePen
    from shapely.geometry import Polygon

    class Flatten(BasePen):
        def __init__(self, gs):
            super().__init__(gs)
            self.contours, self.cur = [], None

        def _moveTo(self, p):
            self.cur = [p]

        def _lineTo(self, p):
            self.cur.append(p)

        def _curveToOne(self, p1, p2, p3):
            p0 = self.cur[-1]
            for i in range(1, STEPS + 1):
                t = i / STEPS
                m = 1 - t
                self.cur.append((m**3 * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t**3 * p3[0],
                                 m**3 * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t**3 * p3[1]))

        def _qCurveToOne(self, p1, p2):
            p0 = self.cur[-1]
            for i in range(1, STEPS + 1):
                t = i / STEPS
                m = 1 - t
                self.cur.append((m * m * p0[0] + 2 * m * t * p1[0] + t * t * p2[0],
                                 m * m * p0[1] + 2 * m * t * p1[1] + t * t * p2[1]))

        def _closePath(self):
            if self.cur and len(self.cur) >= 3:
                self.contours.append(self.cur)
            self.cur = None

        _endPath = _closePath

    pen = Flatten(glyph_set)
    glyph_set[name].draw(pen)
    geom = None
    for poly in sorted((Polygon(c).buffer(0) for c in pen.contours), key=lambda p: -p.area):
        if geom is None:
            geom = poly
        elif poly.within(geom):
            geom = geom.difference(poly)        # contorno interno: un buco
        else:
            geom = geom.union(poly)
    return geom


def font_data():
    """La parola composta come nel browser, in unita' del font."""
    import uharfbuzz as hb
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
        geom = _glyph_geometry(gs, order[info.codepoint])
        x0, _, x1, _ = geom.bounds
        letters.append({"x": x, "geom": geom, "ink": (x + x0, x + x1)})
        x += pos.x_advance + TRACKING * upm
    baseline = (upm - asc - desc) / 2 + asc          # dall'alto della riga alta 1em, come il browser
    return {"upm": upm, "xh": os2.sxHeight, "baseline": baseline, "width": x, "letters": letters}


def cut(fd=None, mk=None):
    """I tagli, in unita' del font, rispetto all'origine di ogni lettera (y in su).

    Restituisce le lame, (indice della lettera, vertici del poligono), e le
    schegge da togliere, (indice della lettera, (x0, y0, x1, y1)).
    """
    from shapely.affinity import translate
    from shapely.geometry import Polygon, box

    fd = fd or font_data()
    mk = mk or mark_geometry()
    letters = fd["letters"]
    half = mk["gap"] * fd["upm"] / (WORD_RATIO * mk["h"]) / 2   # unita' del marchio -> del font
    a = math.radians(mk["angle"])
    ux, uy = math.cos(a), -math.sin(a)      # lungo il taglio: scende verso destra (qui y va in su)
    nx, ny = -uy, ux                        # di traverso
    far = 2 * fd["upm"]

    blades, slivers = [], []
    for i in CUT_LETTERS:
        g, gx = letters[i]["geom"], letters[i]["x"]
        x0, _, x1, _ = g.bounds
        cx, cy = (x0 + x1) / 2, CUT_AT * fd["xh"]
        blade = Polygon([(cx + sx * ux * far + sn * nx * half, cy + sx * uy * far + sn * ny * half)
                         for sx, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
        # la lama resta nella cella della lettera: si ferma a meta' strada
        # dalle lettere vicine
        lo = (letters[i - 1]["ink"][1] + letters[i]["ink"][0]) / 2 - gx if i > 0 else -far
        hi = (letters[i]["ink"][1] + letters[i + 1]["ink"][0]) / 2 - gx if i + 1 < len(letters) else far
        blade = blade.intersection(box(lo, -far, hi, far))
        neighbours = [translate(letters[j]["geom"], letters[j]["x"] - gx)
                      for j in (i - 1, i + 1) if 0 <= j < len(letters)]
        assert not any(blade.intersects(n) for n in neighbours), f"il taglio della lettera {i} tocca una vicina"
        blades.append((i, list(blade.exterior.coords)[:-1]))

        rest = g.difference(blade)
        pieces = list(rest.geoms) if rest.geom_type == "MultiPolygon" else [rest]
        keep = [p for p in pieces if p.area >= SLIVER * g.area]
        for p in pieces:
            if p.area >= SLIVER * g.area:
                continue
            px0, py0, px1, py1 = p.bounds
            patch = box(px0 - SLIVER_PAD, py0 - SLIVER_PAD, px1 + SLIVER_PAD, py1 + SLIVER_PAD)
            assert not any(patch.intersects(q) for q in keep + neighbours), f"la scheggia della lettera {i} tocca altro"
            slivers.append((i, patch.bounds))
    return {"blades": blades, "slivers": slivers}


def num(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def mask_svg(fd, ct):
    """Maschera alfa della riga (larga quanto la scritta, alta 1em): opaco
    dove il testo resta, trasparente nei tagli e nelle schegge."""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union

    w, h, base = fd["width"], fd["upm"], fd["baseline"]
    holes = []
    for i, pts in ct["blades"]:
        x = fd["letters"][i]["x"]
        holes.append(Polygon([(x + px, base - py) for px, py in pts]))
    for i, (x0, y0, x1, y1) in ct["slivers"]:
        x = fd["letters"][i]["x"]
        holes.append(box(x + x0, base - y1, x + x1, base - y0))
    opaque = box(0, 0, w, h).difference(unary_union(holes))
    d = ""
    for poly in (opaque.geoms if opaque.geom_type == "MultiPolygon" else [opaque]):
        for ring in (poly.exterior, *poly.interiors):
            d += "M" + " ".join(f"{num(px)} {num(py)}" for px, py in list(ring.coords)[:-1]) + "Z"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {num(w)} {num(h)}' "
            f"preserveAspectRatio='none'><path fill-rule='evenodd' d='{d}'/></svg>")


def css_block(fd, ct):
    uri = "data:image/svg+xml," + quote(mask_svg(fd, ct), safe=" =:/'.,-")
    return (
        "/* intagli:inizio — scritto da tools/wordmark/intagli.py, non editare a mano */\n"
        ".tr-brandmark__wordmark,\n"
        ".tr-spinner__wordmark {\n"
        f'  --tr-wordmark-cut: url("{uri}");\n'
        "  -webkit-mask: var(--tr-wordmark-cut) left center / 100% 1em no-repeat;\n"
        "          mask: var(--tr-wordmark-cut) left center / 100% 1em no-repeat;\n"
        "}\n"
        "/* intagli:fine */"
    )


if __name__ == "__main__":
    fd, mk = font_data(), mark_geometry()
    ct = cut(fd, mk)
    css = CSS.read_text()
    new, n = re.subn(r"/\* intagli:inizio.*?/\* intagli:fine \*/", lambda _: css_block(fd, ct), css, flags=re.S)
    assert n == 1, "css/traccia.css: attesi i commenti intagli:inizio / intagli:fine una volta"
    CSS.write_text(new)
    print(f"tagli diagonali a {num(mk['angle'])} gradi, spessi {num(mk['gap'] * fd['upm'] / (WORD_RATIO * mk['h']))} "
          f"unita', su {len(ct['blades'])} lettere; {len(ct['slivers'])} schegge tolte; scritto {CSS.relative_to(ROOT)}")
