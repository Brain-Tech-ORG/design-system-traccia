// Tavola delle varianti dei totem, per la scelta interna: i totem sono due,
// le varianti tre. Non fa parte dell'esecutivo e non va all'allestitore.
//
//   node build.mjs totem && node varianti.mjs

import { mkdirSync } from 'node:fs';
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

const outDir = resolve(here, 'proposte');
mkdirSync(outDir, { recursive: true });
const out = resolve(outDir, 'SIN26_totem_tre-varianti.pdf');

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.goto(pathToFileURL(resolve(here, 'riepilogo', 'varianti-totem.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
} finally {
  await browser.close();
}

// Senza le date di Chromium: la stessa tavola da' lo stesso file.
execFileSync('python3', ['-I', '-c', `
import sys
from pypdf import PdfReader, PdfWriter
p = sys.argv[1]
r = PdfReader(p)
w = PdfWriter(clone_from=r)
info = {k: v for k, v in (r.metadata or {}).items() if k not in ('/CreationDate', '/ModDate')}
info.update({'/Title': 'La Traccia — SIN 2026 — Totem: tre varianti', '/Author': 'Cooperativa E.D.P. La Traccia'})
w.metadata = info
with open(p, 'wb') as f:
    w.write(f)
`, out]);
console.log('✓ proposte/SIN26_totem_tre-varianti.pdf');
