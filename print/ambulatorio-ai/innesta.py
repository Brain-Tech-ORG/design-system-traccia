"""Sostituisce la prima pagina del PDF di base con la nuova copertina e mette
una foto sotto il contenuto dell'ultima.

    python3 -I innesta.py base.pdf copertina.pdf ultima.pdf finale.pdf

Le pagine 2-7 sono copiate cosi' come sono. Nell'ultima il contenuto non si
tocca: si tolgono solo i due riempimenti di sfondo a pagina intera (la carta e
il foglio bianco, che su carta bianca non si vedono) e si mette la foto al
loro posto, cosi' testo e filigrana restano sopra. Titolo, lingua e visualizzazione
del titolo restano quelli del PDF di base. La struttura di tag del PDF di base
non si porta dietro: i suoi riferimenti puntano al contenuto della vecchia
prima pagina, e un albero di tag a meta' e' peggio di nessun albero.
"""
import sys
from datetime import datetime, timezone
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DecodedStreamObject, DictionaryObject, NameObject, TextStringObject

base_path, cover_path, last_path, out_path = sys.argv[1:5]
base = PdfReader(base_path)
cover = PdfReader(cover_path)
last = PdfReader(last_path)
assert len(cover.pages) == 1, "la copertina deve essere una sola pagina"
assert len(last.pages) == 1, "il livello dell'ultima pagina deve essere una sola pagina"

box = base.pages[0].mediabox
for nome, pdf in (("copertina", cover), ("ultima", last)):
    mb = pdf.pages[0].mediabox
    if (round(float(mb.width), 2), round(float(mb.height), 2)) != (round(float(box.width), 2), round(float(box.height), 2)):
        raise SystemExit(f"formato diverso: {nome} {mb} / base {box}")

out = PdfWriter()
out.add_page(cover.pages[0])
for page in base.pages[1:]:
    out.add_page(page)

# --- Ultima pagina: la foto sotto il contenuto ---
# Il flusso della pagina comincia con due rettangoli a pagina intera riempiti
# (carta, foglio): il secondo sta in un marcatore, per questo i due attacchi
# sono diversi. Si cambia `f` in `n` (chiudi il tracciato senza riempirlo).
FONDI = (b"0 0 794 1123 re\nf\n", b"0 7861 794 1123 re\nf\n")
page = out.pages[-1]
stream = page.get_contents().get_data()
for fondo in FONDI:
    if stream.count(fondo) != 1:
        raise SystemExit("l'ultima pagina non ha la forma attesa: riempimento di sfondo non trovato")
    stream = stream.replace(fondo, fondo[:-2] + b"n\n")
nuovo = DecodedStreamObject()
nuovo.set_data(stream)
page[NameObject("/Contents")] = out._add_object(nuovo)
page.merge_page(last.pages[0], over=False)

meta = {k: v for k, v in (base.metadata or {}).items() if k in ("/Title", "/Creator", "/Producer", "/CreationDate")}
meta["/ModDate"] = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")
out.add_metadata(meta)

root = out._root_object
root[NameObject("/Lang")] = TextStringObject(base.trailer["/Root"].get("/Lang", "it"))
root[NameObject("/ViewerPreferences")] = DictionaryObject({NameObject("/DisplayDocTitle"): BooleanObject(True)})

with open(out_path, "wb") as f:
    out.write(f)
print(f"{out_path}: {len(out.pages)} pagine")
