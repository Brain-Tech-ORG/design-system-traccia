#!/usr/bin/env python3
"""Il taglio del wordmark «traccia»: la parola tagliata dalla freccia.

La scritta accanto al marchio e' testo vivo (Space Grotesk 700, minuscolo,
tracking -0.02em): resta selezionabile, leggibile dagli screen reader, e il
colore lo decide il CSS (antracite sui fondi chiari, bianco sul blu). Il
taglio non cambia niente di questo: e' una maschera sopra il testo.

Il taglio racconta una cosa sola: la freccia e' passata attraverso la
parola. Per questo non e' un segno a se': sta tutto sul marchio.

- E' orizzontale, nella direzione in cui punta la freccia.
- E' all'altezza della punta del marchio. Nel lockup (.tr-brandmark:
  scritta alta 0,8 del marchio, centrata) la linea della punta prosegue
  nella parola: il taglio parte da li'.
- E' spesso quanto il taglio bianco che divide il marchio in due pezzi:
  e' lo stesso taglio.
- Attraversa tutta la parola, ogni lettera che incontra: una freccia non
  salta le lettere.
- Dove lascerebbe una scheggia (un pezzo di lettera sotto l'1% della
  lettera: succede all'estremita' dell'arco delle «a»), la scheggia si
  toglie.

Punta e spessore si leggono da assets/logo-traccia-mark.svg: se cambia il
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
TRACKING = -0.02     # --tr-tracking-wordmark, in em
WORD_RATIO = 0.8     # altezza della scritta (1em) / altezza del marchio, come .tr-brandmark
SLIVER = 0.01        # un pezzo di lettera sotto l'1% della lettera e' una scheggia
SLIVER_PAD = 4       # margine attorno alla scheggia tolta, unita' del font
STEPS = 24           # segmenti per curva, per riconoscere le schegge


def mark_geometry():
    """Dal marchio: altezza, quota della punta e spessore del taglio interno."""
    svg = MARK.read_text()
    h = float(re.search(r'viewBox="([^"]+)"', svg).group(1).split()[3])
    paths = re.findall(r' d="([^"]+)"', svg)
    assert len(paths) == 2, "assets/logo-traccia-mark.svg: attesi due tracciati (barra e triangolo)"
    bar, tri = ([(n[i], n[i + 1]) for i in range(0, len(n), 2)]
                for n in ([float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)] for d in paths))
    tip = max(bar, key=lambda p: p[0])
    # il taglio interno: fra il lato basso della barra (dal vertice a sinistra
    # a quello piu' in basso) e il lato alto del triangolo (dal vertice in alto
    # a quello a destra). Non sono del tutto paralleli: si prende la media.
    a, b = min(bar, key=lambda p: p[0]), max(bar, key=lambda p: p[1])
    top, right = min(tri, key=lambda p: p[1]), max(tri, key=lambda p: p[0])
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    nx, ny = -(b[1] - a[1]) / length, (b[0] - a[0]) / length
    gap = sum((q[0] - a[0]) * nx + (q[1] - a[1]) * ny for q in (top, right)) / 2
    return {"h": h, "tip_y": tip[1], "gap": gap}


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
        letters.append({"x": x, "geom": _glyph_geometry(gs, order[info.codepoint])})
        x += pos.x_advance + TRACKING * upm
    baseline = (upm - asc - desc) / 2 + asc          # dall'alto della riga alta 1em, come il browser
    return {"upm": upm, "baseline": baseline, "width": x, "letters": letters}


def cut(fd=None, mk=None):
    """Il taglio, in unita' del font.

    Restituisce la fascia sopra la linea di base (da, a) e le schegge da
    togliere: (indice della lettera, (x0, y0, x1, y1) rispetto all'origine
    della lettera, y in su).
    """
    from shapely.affinity import translate
    from shapely.geometry import box

    fd = fd or font_data()
    mk = mk or mark_geometry()
    em = WORD_RATIO * mk["h"]                 # la riga della scritta, in unita' del marchio
    k = fd["upm"] / em                        # unita' del marchio -> unita' del font
    centre = fd["baseline"] - (mk["tip_y"] - (mk["h"] - em) / 2) * k   # sopra la linea di base
    half = mk["gap"] * k / 2
    band = (centre - half, centre + half)

    slivers = []
    blade = box(-1e5, band[0], 1e5, band[1])
    for i, letter in enumerate(fd["letters"]):
        g = letter["geom"]
        rest = g.difference(blade)
        pieces = list(rest.geoms) if rest.geom_type == "MultiPolygon" else [rest]
        keep = [p for p in pieces if p.area >= SLIVER * g.area]
        for p in pieces:
            if p.area >= SLIVER * g.area:
                continue
            x0, y0, x1, y1 = p.bounds
            patch = box(x0 - SLIVER_PAD, y0 - SLIVER_PAD, x1 + SLIVER_PAD, y1 + SLIVER_PAD)
            assert not any(patch.intersects(q) for q in keep), f"la scheggia della lettera {i} tocca la lettera"
            for j in (i - 1, i + 1):
                if 0 <= j < len(fd["letters"]):
                    other = translate(fd["letters"][j]["geom"], fd["letters"][j]["x"] - letter["x"])
                    assert not patch.intersects(other), f"la scheggia della lettera {i} tocca la lettera {j}"
            slivers.append((i, patch.bounds))
    return {"band": band, "slivers": slivers}


def num(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def mask_svg(fd, ct):
    """Maschera alfa della riga (larga quanto la scritta, alta 1em): opaco
    dove il testo resta, trasparente nel taglio e nelle schegge."""
    from shapely.geometry import box
    from shapely.ops import unary_union

    w, h, base = fd["width"], fd["upm"], fd["baseline"]
    lo, hi = ct["band"]
    holes = [box(-10, base - hi, w + 10, base - lo)]
    for i, (x0, y0, x1, y1) in ct["slivers"]:
        x = fd["letters"][i]["x"]
        holes.append(box(x + x0, base - y1, x + x1, base - y0))
    opaque = box(0, 0, w, h).difference(unary_union(holes))
    d = ""
    for poly in (opaque.geoms if opaque.geom_type == "MultiPolygon" else [opaque]):
        for ring in (poly.exterior, *poly.interiors):
            pts = list(ring.coords)[:-1]
            d += "M" + " ".join(f"{num(px)} {num(py)}" for px, py in pts) + "Z"
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
    lo, hi = ct["band"]
    print(f"taglio a {num((lo + hi) / 2)} unita' sopra la linea di base, spesso {num(hi - lo)}; "
          f"{len(ct['slivers'])} schegge tolte; scritto {CSS.relative_to(ROOT)}")
