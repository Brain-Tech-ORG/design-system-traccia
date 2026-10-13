"""Sostituisce la prima pagina del PDF di base con la nuova copertina.

    python3 -I innesta.py base.pdf copertina.pdf finale.pdf

Le pagine 2-8 sono copiate cosi' come sono. Titolo, lingua e visualizzazione
del titolo restano quelli del PDF di base. La struttura di tag del PDF di base
non si porta dietro: i suoi riferimenti puntano al contenuto della vecchia
prima pagina, e un albero di tag a meta' e' peggio di nessun albero.
"""
import sys
from datetime import datetime, timezone
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DictionaryObject, NameObject, TextStringObject

base_path, cover_path, out_path = sys.argv[1:4]
base = PdfReader(base_path)
cover = PdfReader(cover_path)
assert len(cover.pages) == 1, "la copertina deve essere una sola pagina"

box = base.pages[0].mediabox
cover_page = cover.pages[0]
if (round(float(cover_page.mediabox.width), 2), round(float(cover_page.mediabox.height), 2)) != (
        round(float(box.width), 2), round(float(box.height), 2)):
    raise SystemExit(f"formato diverso: copertina {cover_page.mediabox} / base {box}")

out = PdfWriter()
out.add_page(cover_page)
for page in base.pages[1:]:
    out.add_page(page)

meta = {k: v for k, v in (base.metadata or {}).items() if k in ("/Title", "/Creator", "/Producer", "/CreationDate")}
meta["/ModDate"] = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")
out.add_metadata(meta)

root = out._root_object
root[NameObject("/Lang")] = TextStringObject(base.trailer["/Root"].get("/Lang", "it"))
root[NameObject("/ViewerPreferences")] = DictionaryObject({NameObject("/DisplayDocTitle"): BooleanObject(True)})

with open(out_path, "wb") as f:
    out.write(f)
print(f"{out_path}: {len(out.pages)} pagine")
