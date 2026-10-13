// Ambulatorio AI — copertina del PDF «GepaDial · La Traccia» (rev. 02).
//
// Il PDF di base (base/ambulatorio-ai-rev02-originale.pdf) arriva gia' composto:
// il sorgente delle sue pagine non e' nel repo. La copertina invece si rifa' qui,
// da copertina.html, e sostituisce la prima pagina. L'ultima pagina resta quella
// del PDF di base, con in piu' la foto di ultima.html messa sotto il contenuto.
// Le pagine 2-7 restano quelle del PDF di base, byte per byte.
//
//   node build.mjs
//
// Richiede Playwright (chromium) e python3 con pypdf; pdftoppm per l'anteprima.

import { mkdirSync, existsSync, rmSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
// Playwright puo' stare nel progetto, in NODE_PATH o nella cartella globale di npm.
const { chromium } = (() => {
  for (const spec of ['playwright', `${process.env.NODE_TOOLS || '/opt/node-tools'}/node_modules/playwright`]) {
    try { return require(spec); } catch { /* prossimo tentativo */ }
  }
  throw new Error('playwright non trovato: npm install playwright');
})();

const outDir = resolve(here, 'out');
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });
const coverPdf = resolve(outDir, '.copertina.pdf');
const lastPdf = resolve(outDir, '.ultima.pdf');
const finalPdf = resolve(outDir, 'ambulatorio-ai.pdf');

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.goto(pathToFileURL(resolve(here, 'copertina.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // @page { size: A4 } in copertina.html: stessa misura del PDF di base.
  await page.pdf({ path: coverPdf, preferCSSPageSize: true, printBackground: true });

  // La foto dell'ultima pagina e' un livello trasparente (omitBackground).
  await page.goto(pathToFileURL(resolve(here, 'ultima.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: lastPdf, preferCSSPageSize: true, printBackground: true, omitBackground: true });
} finally {
  await browser.close();
}

execFileSync('python3', ['-I', resolve(here, 'innesta.py'),
  resolve(here, 'base/ambulatorio-ai-rev02-originale.pdf'), coverPdf, lastPdf, finalPdf], { stdio: 'inherit' });
rmSync(coverPdf, { force: true });
rmSync(lastPdf, { force: true });

// Anteprime dal PDF finale, non dalle pagine HTML.
for (const [n, nome] of [[1, 'copertina'], [8, 'ultima']]) {
  execFileSync('pdftoppm', ['-r', '110', '-f', String(n), '-l', String(n), '-png', '-singlefile', finalPdf,
    resolve(outDir, `anteprima-${nome}`)]);
}
console.log('✓ out/ambulatorio-ai.pdf');
