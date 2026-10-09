# Allestimento stand — SIN 2026, Sorrento

Grafiche per lo stand La Traccia al Congresso Nazionale SIN 2026 (Hilton Sorrento
Palace, 10–13 novembre 2026, spazio n. 63), allestito da Alfonso Scuotto Group
S.r.l. su preventivo n. 229/26 del 1/10/2026. Lo stand e' chiuso su tre lati:
chi passa in corsia vede il fondale e i due totem esterni; chi entra legge le
pareti laterali.

Le misure sono quelle comunicate dall'allestitore (mail di Progettazione Scuotto
dell'8/10/2026): **file PDF alta qualita' o vettoriale, profilo CMYK, scala 1:1
o 1:10**.

## I file da consegnare — `out/`

Tutti in **scala 1:10**: 1 mm nel file = 1 cm in opera, quindi un PDF da
270×220 mm e' la parete da 270×220 cm. Sono vettoriali, con i font incorporati
(Archivo, IBM Plex Mono), colori dichiarati in **DeviceCMYK**, senza immagini
raster e senza trasparenze.

| File | Grafica | File (cm) | Area visibile (cm) | Contenuto |
|---|---|---|---|---|
| `fondale-1.pdf` | Parete fondale 1 | 270×220 | ~250×200 | Il marchio, in grande: lockup a 210 cm + sagoma outline a sbordo |
| `fondale-1--solo-logo.pdf` | Parete fondale 1 — variante | 270×220 | ~250×200 | Solo il lockup, senza sagoma |
| `fondale-2-quinta.pdf` | Parete fondale 2 (quinta) | 220×220 | ~200×200 | Lockup a 168 cm + sagoma outline dall'angolo opposto |
| `fondale-2-quinta--solo-logo.pdf` | Parete fondale 2 — variante | 220×220 | ~200×200 | Solo il lockup |
| `totem-a-istituzionale.pdf` | Totem esterni, lato A | 100×200 | — | Marchio, claim istituzionale, linee di prodotto, certificazioni, contatti |
| `totem-b1-ambulatorio-ia.pdf` | Totem 1, lato B | 100×200 | — | Ambulatorio con IA: il medico parla → il microfono Traccia decodifica → il referto si compila |
| `totem-b2-cartella-ia.pdf` | Totem 2, lato B | 100×200 | — | Cartella, IA e processo infermieristico: foto all'accesso vascolare → l'IA legge l'immagine → la cartella segnala e guida |
| `totem-b-concetti.pdf` | Totem, lato B — variante | 100×200 | — | I due concetti sullo stesso lato, per avere i due totem identici |
| `parete-sinistra.pdf` | Parete sinistra — **proposta** | 420×220 | ~370×200 | Il primo concetto per esteso, in quattro passi. Gli ultimi 30 cm a destra (giunzione) sono bianchi |
| `parete-destra.pdf` | Parete destra — **proposta** | 470×220 | ~450×200 | Il secondo concetto per esteso, in quattro passi, specchiato |

Le pagine misurano il nominale a meno di 0,1 mm (Chromium arrotonda i
millimetri a pixel interi): in opera e' un millimetro su una parete di quasi
tre metri, e la stampa scala comunque il file alla misura del pannello.

Le anteprime PNG in `out/anteprime/` sono rasterizzate **dal PDF finale**, cioe'
da cio' che va in stampa. In `out/verifica-ingombri/` le stesse grafiche con le
guide: area nascosta dal profilo dei pannelli (10 cm per lato) e striscia di
giunzione. Le guide non stanno nei PDF.

## Cosa c'e' sopra, e perche'

**Fondale e quinta: solo il marchio.** Il lockup e' quello di `.tr-brandmark`
— marchio e wordmark affiancati nelle proporzioni 28 : 17 : 12 — portato alla
larghezza massima che l'area visibile consente con un margine di 20 cm, poco
sopra il centro ottico. La sagoma outline a sbordo da un angolo e' il watermark
del sistema (`.tr-watermark`): sul fondale sborda in alto a destra, sulla quinta
in basso a sinistra, cosi' i due pannelli si rispondono. Per chi la trova di
troppo c'e' la variante `--solo-logo`.

**Totem, lato A: chi siamo.** Marchio in testa, eyebrow con la ragione sociale,
il claim istituzionale e il lead presi dalla vetrina del sistema (`index.html`,
blocco introduttivo), le tre linee di prodotto come `.tr-numbered-list`, e in
calce la riga certificazioni — che sta sulle superfici pubbliche, e un totem in
corsia lo e' — con sito e email.

**Totem, lato B: le novita', in modo grafico.** Nessuna schermata di prodotto:
ogni concetto e' un titolo display con la parola chiave in blu e tre passi con
icone sulla griglia del sistema (viewBox 24, tratto 2, estremita' tonde),
collegati dalla linea `brand/300` di `.tr-steps`. Le icone nuove — persona che
parla, microfono, fotocamera, inquadratura, cartella — seguono la stessa
griglia delle ventidue del registro. Un concetto per totem (B1 e B2) si legge
meglio da lontano; la variante `totem-b-concetti` li mette insieme.

**Pareti laterali: proposta.** Il brief non le descrive; l'allestitore le
chiede. Portano i due concetti per esteso — titolo, lead, quattro passi in
colonna, firma — nella stessa lingua dei totem, cosi' lo stand racconta una
cosa sola: fuori il marchio e il perche' entrare, dentro il come.

### Scala tipografica

Due formati, due scale (`src/stand.css`). I valori sono centimetri in opera.

| | Pareti (lette in cammino, 3–6 m) | Totem (letti da fermi, 1,5–4 m) |
|---|---|---|
| Display | 15–22 | 6,8–8 |
| Lead | 6–6,5 | 4–4,6 |
| Corpo | 4,2–5 | 3,3–3,9 |
| Mono | 3,2–3,8 | 2,3–3 |

### Colore

In stampa il `paper` e' il supporto: il fondo e' bianco puro (0/0/0/0), non la
tinta `#fbfbfd` dello schermo, che in macchina diventerebbe una velatura. I
colori del sistema hanno una ricetta CMYK fissa (`cmyk.py`), decisa a mano
perche' la conversione automatica di un blu saturo aggiunge nero e lo spegne:

| Token | sRGB | CMYK |
|---|---|---|
| `brand/500` blu logo | `#4194d7` | 70 · 32 · 0 · 0 |
| `brand/300` linee secondarie | `#8fc0e7` | 42 · 12 · 0 · 0 |
| watermark (brand/500 a 0,16 sul bianco) | `#e1eef9` | 11 · 5 · 0 · 0 |
| `ink/900` testo primario | `#1b1f2a` | 60 · 50 · 40 · 100 |
| `ink/600` corpo | `#3a4050` | 70 · 60 · 45 · 60 |
| `ink/400` didascalie | `#565c6b` | 65 · 55 · 40 · 40 |
| `border/soft` filetti | `#dde2ee` | 12 · 8 · 2 · 0 |

Il watermark e' un colore pieno, non un'opacita': il PDF resta senza
trasparenze. Il file dichiara DeviceCMYK senza output intent: il profilo
(FOGRA39, SWOP…) lo applica la stampa.

## Da confermare prima di mandare in stampa

1. **Le due facce dei totem.** Qui lato A = istituzionale, lato B = un
   concetto per totem (B1 sul primo, B2 sul secondo). Se i due totem devono
   essere identici, il lato B e' `totem-b-concetti.pdf`.
2. **Le pareti laterali** sono una proposta: il brief non le descriveva.
3. **I dati istituzionali** sul totem A — «Leader in Italia nel software per
   sanita' e pubblica amministrazione», «dal 1985», le tre linee di prodotto —
   vengono dalla vetrina del design system, non da un testo approvato per la
   fiera.
4. **La riga certificazioni** e' solo testo: i badge IMQ / SI Cert sono un PNG
   che ingrandito dieci volte non regge. Se servono, vanno chiesti in vettoriale
   agli enti.
5. **I totem** non hanno un'area nascosta dichiarata: il contenuto tiene 8 cm
   dal bordo. Se il profilo copre di piu', va detto.
6. **Il microfono Traccia e l'assistente della cartella** sono raccontati come
   concetti, senza schermate: e' coerente con la scelta, verbalizzata nella call
   del 25/9, di non esporre il prototipo a tutti.

## Come si rigenera

```sh
cd print/stand-sin-2026
node build.mjs            # tutte le grafiche
node build.mjs totem-b    # solo quelle il cui nome contiene "totem-b"
```

Serve Playwright con Chromium (`npm install playwright && npx playwright
install chromium`) e `python3` con `pypdf`; `pdftoppm` (poppler) per le
anteprime. Ogni pagina in `src/` dichiara la propria misura in `data-w` /
`data-h` (mm) e in `@page`; `stand.js` porta i lockup con `data-fit-w` alla
larghezza esatta a font caricati. Chromium stampa il PDF vettoriale, `cmyk.py`
riscrive i flussi di contenuto da RGB a CMYK e si rifiuta di continuare se
trova un'immagine raster, una trasparenza o un operatore colore che non sa
convertire.
