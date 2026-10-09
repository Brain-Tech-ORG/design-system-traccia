#!/usr/bin/env python3
"""Converte in CMYK i PDF vettoriali prodotti da Chromium.

Chromium scrive i colori come DeviceRGB (operatori `rg` / `RG`). Qui si
riscrivono i flussi di contenuto — pagine e Form XObject — sostituendo ogni
colore con la ricetta CMYK corrispondente (`k` / `K`):

- i colori del sistema hanno una ricetta fissa, decisa a mano, perche' la
  conversione automatica di un blu saturo aggiunge nero e lo spegne;
- qualunque altro colore passa per la formula standard (nero = 1 - max).

Nessuna immagine raster e nessuna trasparenza: le grafiche sono solo tracciati
e testo, quindi la riscrittura copre tutto il contenuto. Il profilo di uscita
(FOGRA39, SWOP, ...) lo applica la stampa: il file dichiara DeviceCMYK.

Uso: python3 -I cmyk.py in.pdf out.pdf "Titolo del documento"
"""
import re
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

# sRGB (hex) -> CMYK 0..1. Stessi valori di tokens/tokens.css.
TABLE = {
    "#4194d7": (0.70, 0.32, 0.00, 0.00),  # brand/500 — blu logo
    "#2f7ab8": (0.80, 0.45, 0.00, 0.10),  # brand/600
    "#266296": (0.85, 0.55, 0.05, 0.25),  # brand/700
    "#69aadf": (0.55, 0.22, 0.00, 0.00),  # brand/400
    "#8fc0e7": (0.42, 0.12, 0.00, 0.00),  # brand/300 — linee secondarie
    "#b0d2ee": (0.28, 0.08, 0.00, 0.00),  # brand/200
    "#d0e4f5": (0.18, 0.05, 0.00, 0.00),  # brand/100 — tinta pallida
    "#edf6fd": (0.07, 0.02, 0.00, 0.00),  # brand/50
    "#e1eef9": (0.11, 0.05, 0.00, 0.00),  # watermark: brand/500 a 0,16 sul bianco
    "#1b1f2a": (0.60, 0.50, 0.40, 1.00),  # ink/900 — nero freddo, pieno
    "#3a4050": (0.70, 0.60, 0.45, 0.60),  # ink/600
    "#565c6b": (0.65, 0.55, 0.40, 0.40),  # ink/400
    "#dde2ee": (0.12, 0.08, 0.02, 0.00),  # border/soft
    "#c9cede": (0.20, 0.14, 0.04, 0.02),  # border/soft-2
    "#eff2f9": (0.05, 0.03, 0.00, 0.00),  # surface/tint
    "#fbfbfd": (0.00, 0.00, 0.00, 0.00),  # paper: in stampa e' il supporto
    "#ffffff": (0.00, 0.00, 0.00, 0.00),
    "#000000": (0.00, 0.00, 0.00, 1.00),
}

NUM = r"(-?(?:\d+\.?\d*|\.\d+))"
RGB_RE = re.compile(rf"{NUM}\s+{NUM}\s+{NUM}\s+(rg|RG)(?![A-Za-z])")
LEFTOVER_RE = re.compile(r"(?<![A-Za-z/])(rg|RG|sc|scn|SC|SCN)(?![A-Za-z])")

unmapped = {}


def to_hex(r, g, b):
    return "#%02x%02x%02x" % tuple(min(255, max(0, round(v * 255))) for v in (r, g, b))


def cmyk_of(r, g, b):
    key = to_hex(r, g, b)
    if key in TABLE:
        return TABLE[key]
    k = 1 - max(r, g, b)
    if k >= 0.999:
        rec = (0.0, 0.0, 0.0, 1.0)
    else:
        rec = ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k)
    unmapped[key] = rec
    return rec


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def rewrite(data: bytes) -> bytes:
    text = data.decode("latin-1")

    def sub(m):
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        c, mm, y, k = cmyk_of(r, g, b)
        op = "k" if m.group(4) == "rg" else "K"
        return f"{fmt(c)} {fmt(mm)} {fmt(y)} {fmt(k)} {op}"

    out = RGB_RE.sub(sub, text)
    left = LEFTOVER_RE.findall(out)
    if left:
        raise SystemExit(f"operatori colore non convertiti: {sorted(set(left))}")
    return out.encode("latin-1")


def process_xobjects(resources, seen):
    if resources is None:
        return
    xobjs = resources.get("/XObject")
    if not xobjs:
        return
    for name, ref in list(xobjs.items()):
        obj = ref.get_object()
        key = id(obj)
        if key in seen:
            continue
        seen.add(key)
        subtype = obj.get("/Subtype")
        if subtype == "/Image":
            raise SystemExit(f"immagine raster trovata ({name}): la grafica deve restare vettoriale")
        if subtype == "/Form":
            obj.set_data(rewrite(obj.get_data()))
            process_xobjects(obj.get("/Resources"), seen)


def check_extgstate(resources):
    if resources is None:
        return
    for name, ref in (resources.get("/ExtGState") or {}).items():
        gs = ref.get_object()
        for k in ("/CA", "/ca"):
            if k in gs and float(gs[k]) < 1:
                raise SystemExit(f"trasparenza in {name} ({k}={gs[k]}): va appiattita nel CSS")


def main(src, dst, title):
    reader = PdfReader(src)
    writer = PdfWriter(clone_from=reader)
    seen = set()
    for page in writer.pages:
        contents = page.get_contents()
        if contents is None:
            continue
        new = DecodedStreamObject()
        new.set_data(rewrite(contents.get_data()))
        page.replace_contents(new)
        process_xobjects(page.get("/Resources"), seen)
        check_extgstate(page.get("/Resources"))
    writer.add_metadata({
        "/Title": title,
        "/Author": "Cooperativa E.D.P. La Traccia",
        "/Subject": "Allestimento stand SIN 2026 Sorrento — scala 1:10, DeviceCMYK",
        "/Creator": "design-system-traccia / print/stand-sin-2026",
    })
    with open(dst, "wb") as f:
        writer.write(f)
    if unmapped:
        for k, v in unmapped.items():
            print(f"  colore fuori tabella {k} -> C{v[0]:.2f} M{v[1]:.2f} Y{v[2]:.2f} K{v[3]:.2f}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
