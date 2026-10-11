// Allestimento SIN 2026 — generatore delle grafiche di stand.
//
// Ogni pagina in src/ e' una grafica in scala 1:10 (1 mm nel file = 1 cm in
// opera). Chromium la stampa in PDF vettoriale, cmyk.py riscrive i colori in
// CMYK, pdftoppm produce l'anteprima PNG dal PDF finale — cioe' da cio' che va
// in stampa, non dalla pagina HTML.
//
//   node build.mjs            tutte le grafiche
//   node build.mjs totem-a    solo quelle il cui nome contiene "totem-a"
//
// Richiede Playwright (chromium) e python3 con pypdf.

import { readdirSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
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
const srcDir = resolve(here, 'src');
const outDir = resolve(here, 'out');
const previewDir = resolve(outDir, 'anteprime');
const checkDir = resolve(outDir, 'verifica-ingombri');
for (const d of [outDir, previewDir, checkDir]) if (!existsSync(d)) mkdirSync(d, { recursive: true });

const filter = process.argv[2] || '';
const pages = readdirSync(srcDir)
  .filter((f) => f.endsWith('.html') && f.includes(filter))
  .sort();

const browser = await chromium.launch();
try {
  for (const file of pages) {
    const name = basename(file, '.html');
    const url = pathToFileURL(resolve(srcDir, file)).href;
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const size = await page.evaluate(() => {
      if (window.trFit) window.trFit();
      const root = document.documentElement;
      return { w: root.dataset.w, h: root.dataset.h, title: document.title };
    });
    if (!size.w || !size.h) throw new Error(`${file}: manca data-w / data-h su <html>`);

    const rgbPdf = resolve(outDir, `.${name}.rgb.pdf`);
    const pdf = resolve(outDir, `${name}.pdf`);
    await page.pdf({
      path: rgbPdf,
      width: `${size.w}mm`,
      height: `${size.h}mm`,
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
    });
    execFileSync('python3', ['-I', resolve(here, 'cmyk.py'), rgbPdf, pdf, size.title], { stdio: 'inherit' });
    execFileSync('rm', ['-f', rgbPdf]);

    // Anteprima dal PDF finale: 1:10 a 96 dpi = circa 3,8 px per cm in opera.
    execFileSync('pdftoppm', ['-r', '96', '-png', '-singlefile', pdf, resolve(previewDir, name)]);

    // Verifica ingombri: la stessa pagina con le guide (area nascosta, giunzione).
    await page.evaluate(() => document.documentElement.classList.add('guide'));
    await page.screenshot({ path: resolve(checkDir, `${name}.png`), fullPage: true, scale: 'css' });
    await page.close();
    console.log(`✓ ${name}  ${size.w}×${size.h} mm (1:10)`);
  }
} finally {
  await browser.close();
}
