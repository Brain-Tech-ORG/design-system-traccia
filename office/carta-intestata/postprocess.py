#!/usr/bin/env python3
"""Ritocchi al .docx generato da docx-js, e copia .dotx.

Due cose che docx-js non fa e che Word e LibreOffice pretendono:

1. I campi PAGE / NUMPAGES escono senza risultato: fra `separate` ed `end`
   non c'e' testo. Word li ricalcola all'apertura, LibreOffice e le anteprime
   no, e il numero di pagina sparisce. Qui si inserisce un risultato
   provvisorio ("1") con la stessa formattazione del campo.
2. La chiave dei font incorporati (`w:fontKey`) esce in minuscolo; lo schema
   la vuole in maiuscolo. L'offuscamento del file .odttf non cambia — la
   chiave e' la stessa, cambia solo come e' scritta.

Uso: postprocess.py in.docx out.docx [out.dotx]
"""
import re
import sys
import zipfile

RPR = r'(<w:rPr>(?:(?!</w:rPr>).)*</w:rPr>)'
FIELD = re.compile(
    r'<w:r>' + RPR +
    r'<w:fldChar w:fldCharType="begin"/><w:instrText xml:space="preserve">(PAGE|NUMPAGES)</w:instrText>'
    r'<w:fldChar w:fldCharType="separate"/><w:fldChar w:fldCharType="end"/></w:r>'
)


def field_with_result(m):
    rpr, instr = m.group(1), m.group(2)
    return (
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r>{rpr}<w:t>1</w:t></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
    )


def rewrite(src, dst, template=False):
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith("word/footer") or item.filename.startswith("word/header"):
            data = FIELD.sub(field_with_result, data.decode("utf8")).encode("utf8")
        elif item.filename == "word/fontTable.xml":
            x = data.decode("utf8")
            x = re.sub(r'w:fontKey="\{([0-9a-fA-F-]+)\}"', lambda m: 'w:fontKey="{%s}"' % m.group(1).upper(), x)
            data = x.encode("utf8")
        elif template and item.filename == "[Content_Types].xml":
            # un .dotx e' un .docx con un content type diverso: Word lo apre
            # come modello e crea un documento nuovo invece di sovrascriverlo
            data = data.replace(b"wordprocessingml.document.main+xml", b"wordprocessingml.template.main+xml")
        zout.writestr(item, data)
    zout.close()


if __name__ == "__main__":
    src, docx = sys.argv[1], sys.argv[2]
    rewrite(src, docx)
    if len(sys.argv) > 3:
        rewrite(src, sys.argv[3], template=True)
