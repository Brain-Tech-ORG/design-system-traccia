#!/usr/bin/env bash
# Rigenera la carta intestata: office/carta-intestata.docx e .dotx.
#
# Richiede: node con il pacchetto `docx` (npm i -g docx), python3 con Pillow.
# Con LibreOffice installato produce anche un PDF di controllo in build/.
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p build
python3 render-lockup.py
node build.js build/carta-intestata.raw.docx
python3 postprocess.py build/carta-intestata.raw.docx ../carta-intestata.docx ../carta-intestata.dotx
echo "scritti office/carta-intestata.docx e office/carta-intestata.dotx"

if command -v soffice >/dev/null 2>&1; then
  soffice --headless --convert-to pdf --outdir build ../carta-intestata.docx >/dev/null 2>&1 && echo "anteprima: build/carta-intestata.pdf"
fi
