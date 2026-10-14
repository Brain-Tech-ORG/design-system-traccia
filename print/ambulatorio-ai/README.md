# Ambulatorio AI · GepaDial — brochure A4, rev. 02

Brochure di otto pagine su Ambulatorio AI, il modulo di GepaDial che ascolta la
visita nefrologica e prepara il referto. Questa cartella rifa la **copertina**,
che ora porta anche la foto del Traccia Mic, e aggiunge la stessa foto, in
primo piano, nello spazio vuoto in cima all'**ultima pagina**.

| | |
|---|---|
| `out/ambulatorio-ai.pdf` | Il PDF finale, otto pagine A4 (594,96 × 841,92 pt) |
| `out/anteprima-copertina.png`, `out/anteprima-ultima.png` | Anteprime della prima e dell'ultima pagina, prese dal PDF finale |
| `copertina.html` | Sorgente della copertina: foglio A4 a 96 dpi, font, token e componenti del design system |
| `ultima.html` | Livello trasparente con la sola foto dell'ultima pagina |
| `foto/traccia-mic.jpg` | La foto del dispositivo, intera (1448 × 1086): il ritaglio lo fa la copertina |
| `base/ambulatorio-ai-rev02-originale.pdf` | Il PDF com'era, con la vecchia copertina |
| `build.mjs`, `innesta.py` | Il generatore |

## Come si rifà

```
node build.mjs
```

Chromium stampa `copertina.html` e `ultima.html`; `innesta.py` mette la copertina
al posto della prima pagina del PDF di base e la foto sotto il contenuto
dell'ultima. Richiede Playwright (chromium), python3 con pypdf e
`pdftoppm` per l'anteprima.

## Cosa è cambiato rispetto alla copertina precedente

La copertina è stata ricostruita da zero: il sorgente delle pagine del PDF non
è nel repo, quindi la vecchia prima pagina è stata misurata (posizioni del
testo entro mezzo pixel, geometria del diagramma letta dal vettoriale) e rifatta
con gli stessi componenti. Il confronto col PDF originale, prima di aggiungere
la foto, dava uno scarto medio sotto 1/255 su 255.

- **La foto** sta in cornice arrotondata (`.tr-photo-frame`, bordo 1px
  `border/soft`), a destra del paragrafo introduttivo. Le chip dei temi sono
  passate sotto il paragrafo, in colonna con lui, così testo e foto hanno la
  stessa altezza.
- **Il ritmo verticale** è stato stretto di circa 30 px fra le fasce, per
  fare posto alla foto senza avvicinare i dati in fondo al piede.
- **Tutto il resto** — titolo, diagramma, i quattro passi, la riga dei dati —
  è quello di prima.

**Ultima pagina.** La fascia in cima era vuota fino al marchio (y = 465 px, a
parte la filigrana). La foto la riempie entro i margini del documento, nella
stessa cornice della copertina, con un primo piano sullo schermo del Traccia
Mic. Testo e filigrana restano sopra la foto e non sono stati toccati: dal
flusso di contenuto della pagina si tolgono solo i due riempimenti di sfondo a
pagina intera (carta e foglio bianco), che su carta bianca non si vedono.

Le pagine 2–7 sono quelle del PDF di base, copiate senza modifiche.

## Da sapere

- Il PDF finale **non è più «tagged»**: l'albero di tag del PDF di base
  puntava al contenuto della vecchia copertina e non si può portare dietro a
  metà. Titolo, lingua (`it`) e visualizzazione del titolo restano quelli
  originali. Per riavere un PDF accessibile serve il sorgente delle pagine 2–8.
- Il ritaglio della foto sta in `object-view-box`, dentro `copertina.html` e
  `ultima.html`: per cambiarlo si modifica lì, il file in `foto/` resta intero.
  Entrambi i ritagli partono dopo il cavo (x ≈ 390 su 1448): sul connettore
  c'è il marchio di un terzo, e così non compare.
- L'ultima pagina, senza il riempimento di sfondo, ha il fondo trasparente: i
  lettori PDF la mostrano bianca e su carta bianca non cambia nulla.
