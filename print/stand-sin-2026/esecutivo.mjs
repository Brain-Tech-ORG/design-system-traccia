// Esecutivo di stampa: il pacchetto da consegnare all'allestitore.
//
// Prende i PDF gia' generati da build.mjs (out/) e li copia in esecutivo/
// con i nomi di produzione — numero, pezzo, misura, scala — uno per ogni
// pezzo stampato: il lato A dei totem compare due volte, perche' i totem
// sono due. Ci aggiunge la tavola di riepilogo (riepilogo/riepilogo.html ->
// 00_riepilogo-esecutivo.pdf) e chiude tutto in uno zip da allegare.
//
//   node build.mjs && node esecutivo.mjs

import { copyFileSync, mkdirSync, existsSync, rmSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = (() => {
  for (const spec of ['playwright', `${process.env.NODE_TOOLS || '/opt/node-tools'}/node_modules/playwright`]) {
    try { return require(spec); } catch { /* prossimo tentativo */ }
  }
  throw new Error('playwright non trovato: npm install playwright');
})();

// [numero, pezzo, sorgente in out/, misura in cm]
const PIECES = [
  ['01', 'parete-sinistra', 'parete-sinistra', '420x220'],
  ['02', 'parete-fondale-1', 'fondale-1', '270x220'],
  ['03', 'parete-fondale-2-quinta', 'fondale-2-quinta', '220x220'],
  ['04', 'parete-destra', 'parete-destra', '470x220'],
  ['05', 'totem-1-lato-A', 'totem-a-istituzionale', '100x200'],
  ['06', 'totem-1-lato-B', 'totem-b1-ambulatorio-ia', '100x200'],
  ['07', 'totem-2-lato-A', 'totem-a-istituzionale', '100x200'],
  ['08', 'totem-2-lato-B', 'totem-b2-dati-ia', '100x200'],
];
const PACKAGE = 'LaTraccia_SIN26_esecutivo-stampa';

const outDir = resolve(here, 'out');
const pkgDir = resolve(here, 'esecutivo');
if (existsSync(pkgDir)) rmSync(pkgDir, { recursive: true });
mkdirSync(pkgDir, { recursive: true });

for (const [n, piece, src, size] of PIECES) {
  const from = resolve(outDir, `${src}.pdf`);
  if (!existsSync(from)) throw new Error(`manca ${from}: prima node build.mjs`);
  copyFileSync(from, resolve(pkgDir, `${n}_${piece}_${size}cm_scala-1-10.pdf`));
}

// La tavola di riepilogo: un documento da leggere, non da stampare in
// grande, quindi resta in RGB e porta le miniature raster.
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.goto(pathToFileURL(resolve(here, 'riepilogo', 'riepilogo.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: resolve(pkgDir, '00_riepilogo-esecutivo.pdf'),
    preferCSSPageSize: true,
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
} finally {
  await browser.close();
}

// Come per le grafiche: senza le date di Chromium, lo stesso riepilogo da'
// lo stesso file.
execFileSync('python3', ['-I', '-c', `
import sys
from pypdf import PdfReader, PdfWriter
p = sys.argv[1]
r = PdfReader(p)
w = PdfWriter(clone_from=r)
info = {k: v for k, v in (r.metadata or {}).items() if k not in ('/CreationDate', '/ModDate')}
info.update({'/Title': 'La Traccia — SIN 2026 — Esecutivo di stampa: riepilogo', '/Author': 'Cooperativa E.D.P. La Traccia'})
w.metadata = info
with open(p, 'wb') as f:
    w.write(f)
`, resolve(pkgDir, '00_riepilogo-esecutivo.pdf')]);

// Lo zip: una cartella con lo stesso nome, cosi' chi lo apre ritrova i
// file in ordine. Resta fuori dal repository (.gitignore).
const zipPath = resolve(here, `${PACKAGE}.zip`);
if (existsSync(zipPath)) rmSync(zipPath);
const staging = resolve(here, '.zip-staging', PACKAGE);
rmSync(resolve(here, '.zip-staging'), { recursive: true, force: true });
mkdirSync(staging, { recursive: true });
const files = readdirSync(pkgDir).sort();
for (const f of files) copyFileSync(resolve(pkgDir, f), resolve(staging, f));
execFileSync('zip', ['-q', '-X', zipPath, ...files.map((f) => `${PACKAGE}/${f}`)], { cwd: resolve(here, '.zip-staging') });
rmSync(resolve(here, '.zip-staging'), { recursive: true, force: true });

for (const f of readdirSync(pkgDir).sort()) console.log(`  ${f}`);
console.log(`✓ ${PACKAGE}.zip`);
