#!/usr/bin/env python3
"""La conchiglia La Traccia, ridisegnata in modo regolare.

Genera assets/conchiglia.svg (tratto blu logo) e assets/conchiglia-mono.svg
(tratto currentColor, per l'SVG in linea che prende il colore dal contesto).

La conchiglia dell'immagine aziendale e' un ventaglio di petali attorno a un
perno, ognuno riempito di archi annidati. L'originale era disegnato a mano e
aveva qualche difetto: un petalino spurio fra il secondo e il terzo lobo,
archi a passo irregolare, tratti che si accavallano e un groviglio vicino al
perno. Qui la stessa figura e' costruita con una regola sola:

- i petali stanno fra raggi a passo quasi costante (82°, 96°, 110,5°, 125°,
  138°, 150,5°: gli angoli misurati sull'originale) e ognuno e' lungo 0,875
  del precedente;
- il contorno e' una catena di lobi: ogni lobo parte tangente al raggio di
  destra, gira sopra e scende tangente al raggio di sinistra, dove incontra il
  lobo successivo con una cuspide (la spina a lisca di pesce dell'originale);
- le righe interne sono copie del contorno scalate rispetto al perno a passo
  lineare (k/n): fra due archi c'e' la stessa distanza lungo ogni raggio, come
  nell'originale, e nessun arco tocca l'altro;
- le prime righe vicino al perno non si disegnano: e' li' che l'originale si
  impastava.

Il perno sta nell'angolo in basso a destra del viewBox: la conchiglia si
appoggia a un angolo della pagina e si apre verso l'alto a sinistra.

    python3 tools/conchiglia.py
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGES = (82, 96, 110.5, 125, 138, 150.5)  # raggi fra i petali, in gradi
L0 = 900          # lunghezza del primo petalo (unita' del viewBox)
RATIO = 0.875     # ogni petalo e' lungo cosi' rispetto al precedente
H1, H2 = 0.65, 1.08  # maniglie del lobo: uscita dal raggio destro, arrivo sul sinistro
N = 30            # righe dal perno al contorno, come nell'originale
K_MIN = 2         # la prima riga, minuscola, resta fuori
STROKE = 1.6       # tratto, in unita' del viewBox
BRAND = "#4194d7"


def u(a):
    a = math.radians(a)
    return math.cos(a), math.sin(a)


def rows():
    """Per ogni riga, la catena di lobi come curve di Bezier cubiche, in
    coordinate con il perno nell'origine e y verso l'alto."""
    out = []
    for k in range(K_MIN, N + 1):
        f = k / N
        segs = []
        for p in range(len(EDGES) - 1):
            ar, al = EDGES[p], EDGES[p + 1]
            lr, ll = f * L0 * RATIO ** p, f * L0 * RATIO ** (p + 1)
            s = (lr * u(ar)[0], lr * u(ar)[1])
            e = (ll * u(al)[0], ll * u(al)[1])
            ch = math.dist(s, e)
            c1 = (s[0] + H1 * ch * u(ar)[0], s[1] + H1 * ch * u(ar)[1])
            c2 = (e[0] + H2 * ch * u(al)[0], e[1] + H2 * ch * u(al)[1])
            segs.append((s, c1, c2, e))
        out.append(segs)
    return out


def bezier_points(seg, n=48):
    p0, p1, p2, p3 = seg
    for i in range(n + 1):
        t = i / n
        m = 1 - t
        yield tuple(m ** 3 * p0[j] + 3 * m * m * t * p1[j] + 3 * m * t * t * p2[j] + t ** 3 * p3[j] for j in range(2))


def svg(stroke):
    rs = rows()
    pts = [q for segs in rs for seg in segs for q in bezier_points(seg)]
    pad = STROKE
    minx = min(x for x, _ in pts) - pad
    maxy = max(y for _, y in pts) + pad
    # perno nell'angolo in basso a destra: il viewBox finisce a x = 0, y = 0
    w, h = -minx, maxy
    T = lambda q: f"{q[0] - minx:.1f} {maxy - q[1]:.1f}"
    paths = []
    for segs in rs:
        d = "M" + T(segs[0][0]) + "".join(f"C{T(c1)} {T(c2)} {T(e)}" for _, c1, c2, e in segs)
        paths.append(f'<path d="{d}"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Conchiglia La Traccia">\n'
        f'<g fill="none" stroke="{stroke}" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round">\n'
        + "\n".join(paths)
        + "\n</g>\n</svg>\n"
    )


if __name__ == "__main__":
    (ROOT / "assets/conchiglia.svg").write_text(svg(BRAND))
    (ROOT / "assets/conchiglia-mono.svg").write_text(svg("currentColor"))
    print("scritti assets/conchiglia.svg e assets/conchiglia-mono.svg")
