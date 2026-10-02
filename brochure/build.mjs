// Genera i PDF della brochure GeDon Banche — A.I.BA.T. 2026.
//
//   node brochure/build.mjs
//
// Esce in due versioni dallo stesso HTML:
//   - A4 al taglio (210x297mm): invio digitale, stampa da ufficio, controllo;
//   - A4 con 3mm di abbondanza per lato (216x303mm): il file per la tipografia.
//     La pagina cresce, il foglio resta al suo posto e solo la sagoma del
//     marchio, l'unico elemento al vivo, prosegue oltre il taglio.
//
// I font arrivano da assets/fonts tramite css/traccia-fonts.css: niente rete,
// e Chromium li incorpora nel PDF. Serve Playwright con Chromium; nel container
// cloud e' gia' installato (vedi PLAYWRIGHT_BROWSERS_PATH).

import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import path from "node:path";

// Il repository non ha un package.json: Playwright si prende da dove c'e',
// prima locale e poi installato globalmente (npm i -g playwright).
let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  const globalRoot = execSync("npm root -g").toString().trim();
  ({ chromium } = createRequire(path.join(globalRoot, "/"))("playwright"));
}

const here = path.dirname(fileURLToPath(import.meta.url));
const source = pathToFileURL(path.join(here, "gedon-banche-aibat-2026.html")).href;

// Il formato si dichiara con @page e preferCSSPageSize: Chromium quantizza la
// pagina a passi di 0,96pt, e per questa via lo scarto resta sotto 0,1mm
// (con width/height passati a page.pdf arriva a 0,24mm).
const outputs = [
  { file: "GeDon-Banche_AIBAT-2026_A4.pdf", bleed: false, size: "210mm 297mm" },
  { file: "GeDon-Banche_AIBAT-2026_A4_tipografia-abbondanza-3mm.pdf", bleed: true, size: "216mm 303mm" },
];

const browser = await chromium.launch();
try {
  for (const out of outputs) {
    const page = await browser.newPage();
    await page.goto(source, { waitUntil: "networkidle" });
    if (out.bleed) {
      await page.evaluate(() => document.documentElement.classList.add("gdt-bleed"));
    }
    await page.addStyleTag({ content: `@page { size: ${out.size}; margin: 0; }` });
    await page.evaluate(() => document.fonts.ready);
    await page.emulateMedia({ media: "print" });

    // Il foglio ha un'altezza fissa e overflow: clip, quindi un testo troppo
    // lungo non andrebbe a pagina due: sparirebbe sotto il taglio, in
    // silenzio. Meglio fermarsi: il piede deve chiudere dentro il margine.
    const overflow = await page.evaluate(() => {
      const sheet = document.querySelector(".gdt-sheet");
      const foot = document.querySelector(".gdt-foot");
      const padBottom = parseFloat(getComputedStyle(sheet).paddingBottom);
      const limit = sheet.getBoundingClientRect().bottom - padBottom;
      return Math.ceil(foot.getBoundingClientRect().bottom - limit);
    });
    if (overflow > 0) {
      throw new Error(`il contenuto sfora il foglio di ${overflow}px: accorciare i testi`);
    }

    await page.pdf({
      path: path.join(here, out.file),
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      preferCSSPageSize: true,
    });
    await page.close();
    console.log(`ok  ${out.file}`);
  }
} finally {
  await browser.close();
}
