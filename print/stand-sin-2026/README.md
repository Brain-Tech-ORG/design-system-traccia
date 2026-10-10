# Allestimento stand — SIN 2026, Sorrento

Grafiche per lo stand La Traccia al Congresso Nazionale SIN 2026 (Hilton Sorrento
Palace, 10–13 novembre 2026, spazio n. 63), allestito da Alfonso Scuotto Group
S.r.l. su preventivo n. 229/26 del 1/10/2026. Lo stand e' chiuso su tre lati:
chi passa in corsia vede il fondale e i due totem esterni; chi entra legge le
pareti laterali.

Le misure sono quelle comunicate dall'allestitore (mail di Progettazione Scuotto
dell'8/10/2026): **file PDF alta qualita' o vettoriale, profilo CMYK, scala 1:1
o 1:10**.

## L'esecutivo di stampa — `esecutivo/`

E' il pacchetto da consegnare: **sei PDF, uno per ogni pezzo stampato** —
quattro pareti e due totem — con nomi di produzione che dicono numero, pezzo,
misura e scala (la scala nel nome evita che qualcuno stampi il file a un
decimo), piu' la tavola di riepilogo.

| N. | File | Pezzo |
|---|---|---|
| 00 | `00_riepilogo-esecutivo.pdf` | Tavola di riepilogo: miniature, file, specifiche, riferimenti (A4 orizzontale, 2 pagine, rev. 03) |
| 01 | `01_parete-sinistra_420x220cm_scala-1-10.pdf` | Parete sinistra |
| 02 | `02_parete-fondale-1_270x220cm_scala-1-10.pdf` | Parete fondale 1 |
| 03 | `03_parete-fondale-2-quinta_220x220cm_scala-1-10.pdf` | Parete fondale 2 (quinta) |
| 04 | `04_parete-destra_470x220cm_scala-1-10.pdf` | Parete destra |
| 05 | `05_totem-1_100x200cm_scala-1-10.pdf` | Totem 1 |
| 06 | `06_totem-2_100x200cm_scala-1-10.pdf` | Totem 2 |

Lo zip `LaTraccia_SIN26_esecutivo-stampa.zip` contiene la stessa cartella e si
rigenera con `node esecutivo.mjs`: non sta nel repository.

## Le grafiche — `out/`

Tutte in **scala 1:10**: 1 mm nel file = 1 cm in opera, quindi un PDF da
270×220 mm e' la parete da 270×220 cm. Sono vettoriali, con i font incorporati
(Archivo, IBM Plex Mono e, per il wordmark, Space Grotesk) dove c'e' testo, colori dichiarati in **DeviceCMYK**,
senza immagini raster e senza trasparenze.

| File | Pezzo | File (cm) | Area visibile (cm) | Contenuto |
|---|---|---|---|---|
| `fondale-1.pdf` | Parete fondale 1 | 270×220 | ~250×200 | Solo il marchio, pieno, alto 170 cm, al centro: niente testo |
| `fondale-2-quinta.pdf` | Parete fondale 2 (quinta) | 220×220 | ~200×200 | La sagoma outline del marchio, alla stessa misura e altezza: niente testo |
| `parete-sinistra.pdf` | Parete sinistra | 420×220 | ~370×200 | Solo grafica: la sagoma outline a sbordo dal bordo alto, verso l'ingresso. Gli ultimi 30 cm a destra (giunzione) sono bianchi |
| `parete-destra.pdf` | Parete destra | 470×220 | ~450×200 | Solo grafica: la stessa sagoma, a sbordo dal bordo alto verso l'ingresso |
| `totem-1-ambulatorio-ia.pdf` | Totem 1 | 100×200 | — | Eyebrow «Novita' · Hardware custom», titolo «Modelli IA per la nefrologia»; il microfono AI e accanto «Ambulatorio» e «Rilevazioni a bordo letto» |
| `totem-2-dati-ia.pdf` | Totem 2 | 100×200 | — | Eyebrow «Gen BI · Dati clinici e IA», titolo «I dati clinici prendono forma»; il marchio fatto di punti; certificazioni e contatti |
| `totem-3-percorso-infermieristico.pdf` | Totem 3 · **variante**, fuori dall'esecutivo | 100×200 | — | Eyebrow «Novita' · Gepadial», titolo «Nuovo percorso infermieristico personalizzabile»; il percorso standard accanto a quello costruito sull'azienda ospedaliera |

Le pagine misurano il nominale a meno di 0,1 mm (Chromium arrotonda i
millimetri a pixel interi): in opera e' un millimetro su una parete di quasi
tre metri, e la stampa scala comunque il file alla misura del pannello.

Le anteprime PNG in `out/anteprime/` sono rasterizzate **dal PDF finale**, cioe'
da cio' che va in stampa. In `out/verifica-ingombri/` le stesse grafiche con le
guide: area nascosta dal profilo dei pannelli (10 cm per lato) e striscia di
giunzione. Le guide non stanno nei PDF.

## Cosa c'e' sopra, e perche'

**Fondale: il marchio, e basta.** Niente testo, nemmeno il wordmark: il
marchio pieno, blu di marca, alto 170 cm, al centro dell'area visibile, con
15 cm d'aria sopra e sotto. E' l'unica cosa che chi passa in corsia deve
riconoscere, e da lontano un segno solo si riconosce prima di un segno con una
parola accanto.

**Quinta: l'eco del marchio.** Anche qui niente testo. La sagoma outline del
marchio — il watermark del sistema, `brand/500` a 0,16 sul bianco — alla
stessa misura e alla stessa altezza del marchio del fondale: sul fondo dello
stand il segno pieno resta uno solo, e la quinta gli risponde invece di
ripeterlo.

**Il wordmark e' «traccia»**: tutto minuscolo, senza «la», in Space Grotesk
700 e in antracite, come nel design system (`.tr-brandmark`): scritta 0,8 e
distanza 0,34 dell'altezza del marchio. Sui totem il lockup e' largo 54 cm.

**Totem 1: modelli IA per la nefrologia.** In testa il lockup, eyebrow
«Novita' · Hardware custom» e titolo display «Modelli IA per la nefrologia»
(non «intelligenza artificiale»): che sia hardware custom lo dice la nota
dell'eyebrow, non una didascalia sotto il disegno. Sotto, il **wireframe del
microfono AI**, disegnato con le convenzioni del disegno tecnico del sistema
(`.tr-drawing`: silhouette con tratto `ink/900` e riempimento `surface/tint`,
dettagli in blu: l'anello LED, l'anello della base, le onde senza fili) con la
sola sigla **AI** in display sulla capsula, e accanto le due parole con il
tratto d'accento: «Ambulatorio», «Rilevazioni a bordo letto». La sagoma
outline sborda in basso.

**Totem 2: istituzionale.** Un gioco con il marchio e il tema della gestione
dei dati clinici con l'IA (gen BI). In testa il lockup, eyebrow «Gen BI · Dati
clinici e IA» e titolo «I dati clinici prendono forma»; in calce
certificazioni e contatti. In mezzo il **marchio fatto di punti**: le due
figure del logo campionate su un reticolo parallelo ai loro lati, cosi' i bordi
restano dritti e la fessura fra le due figure resta aperta. Da lontano e' il
logo, da vicino una mappa di dati: la tinta di ogni punto (`brand/300` →
`brand/600`) e' il suo valore, piu' scura verso la punta; tre anelli sono i
dati che l'IA segnala. Il reticolo lo genera `src/dot-mark.js`,
deterministico: stesso seme, stesso disegno, stesso PDF.

**Totem 3, variante: il percorso infermieristico personalizzabile.** Stessa
testata, eyebrow «Novita' · Gepadial» e titolo «Nuovo percorso
infermieristico personalizzabile». Il concetto e' che il percorso si
costruisce sull'azienda ospedaliera invece di essere quello standard, e il
disegno mette i due a confronto: a sinistra il percorso **standard**, una
linea dritta di tappe uguali, in grigio; a destra quello di **la tua azienda
ospedaliera**, in blu, con le stesse partenza e arrivo ma una deviazione,
tappe proprie e una tappa che si aggiunge (il «+» tratteggiato).

**I totem sono due, le varianti tre.** La scelta e' interna: la tavola
`proposte/SIN26_totem_tre-varianti.pdf` (A4, una pagina, `node varianti.mjs`)
le mette affiancate. Finche' non si sceglie, l'esecutivo porta i totem 1 e 2.

**Pareti laterali: quattro varianti con piu' colore.** L'ufficio commerciale
ha chiesto piu' azzurro aziendale sulle pareti laterali. La tavola interna
`proposte/SIN26_pareti-laterali_quattro-varianti.pdf` (A4, due pagine) mostra
le pareti aperte attorno al fondale in quattro varianti: 1 blocco (banda
verticale piena a tutta altezza verso l'ingresso, attraversata dalla sagoma
del marchio), 2 parete piena nel blu del logo, 3 conchiglia in linee blu,
speculare sulle due pareti, 4 conchiglia con i petali nelle tinte del blu solo
sulla parete sinistra, destra bianca. La conchiglia e' l'asset di sfondo del
design system (`assets/conchiglia.svg`). Finche' non si sceglie, l'esecutivo
porta le pareti con la sola sagoma.

Su tutti i totem il disegno sta a meta' tra il titolo e il piede.

**Pareti laterali: solo grafica, e poca.** Niente testo: su ciascuna parete
la sola sagoma outline del marchio, a sbordo dal bordo alto verso l'ingresso
dello stand — a sinistra sulla parete sinistra, a destra su quella destra. La
posizione e' specchiata, il disegno no: il marchio non si ribalta.

### Scala tipografica

Le pareti non portano testo. Sui totem, letti da fermi a 1,5–4 m: titolo
display 8 cm, le due parole accanto al microfono 4,8 cm, voce mono 2,3–3 cm
(eyebrow, piede, certificazioni). La scala completa — anche quella delle
pareti, per quando dovesse servire — sta in `src/stand.css`.

### Colore

In stampa il `paper` e' il supporto: il fondo e' bianco puro (0/0/0/0), non la
tinta `#fbfbfd` dello schermo, che in macchina diventerebbe una velatura. I
colori del sistema hanno una ricetta CMYK fissa (`cmyk.py`), decisa a mano
perche' la conversione automatica di un blu saturo aggiunge nero e lo spegne:

| Token | sRGB | CMYK |
|---|---|---|
| `brand/600` | `#2f7ab8` | 80 · 45 · 0 · 10 |
| `brand/500` blu logo | `#4194d7` | 70 · 32 · 0 · 0 |
| `brand/400` | `#69aadf` | 55 · 22 · 0 · 0 |
| `brand/300` linee secondarie | `#8fc0e7` | 42 · 12 · 0 · 0 |
| watermark (brand/500 a 0,16 sul bianco) | `#e1eef9` | 11 · 5 · 0 · 0 |
| `ink/900` testo primario | `#1b1f2a` | 60 · 50 · 40 · 100 |
| `ink/600` corpo | `#3a4050` | 70 · 60 · 45 · 60 |
| `ink/400` didascalie | `#565c6b` | 65 · 55 · 40 · 40 |
| `anthracite` wordmark «traccia» | `#383e42` | 65 · 55 · 50 · 60 |
| `border/soft` filetti | `#dde2ee` | 12 · 8 · 2 · 0 |

Il watermark e' un colore pieno, non un'opacita': il PDF resta senza
trasparenze. Il file dichiara DeviceCMYK senza output intent: il profilo
(FOGRA39, SWOP…) lo applica la stampa.

## Da confermare prima di mandare in stampa

1. **Il microfono** e' un wireframe generico — capsula, stelo, base con
   anello luminoso, onde senza fili — non il disegno del dispositivo reale.
   Se il prodotto ha una forma riconoscibile, il disegno va rifatto su quella.
2. **La riga certificazioni** del totem 2 e' solo testo: i badge IMQ / SI
   Cert sono un PNG che ingrandito dieci volte non regge. Se servono, vanno
   chiesti in vettoriale agli enti.
3. **I totem** non hanno un'area nascosta dichiarata: il contenuto tiene 8 cm
   dal bordo. Se il profilo copre di piu', va detto.
4. **Il microfono AI e la gen BI** sono raccontati come concetti, senza
   schermate: e' coerente con la scelta, verbalizzata nella call del 25/9, di
   non esporre il prototipo a tutti.
5. **La quinta** porta l'eco chiara del marchio. Se la si vuole con il
   marchio pieno come il fondale, e' la stessa pagina con il riempimento al
   posto del tratto.

## Come si rigenera

```sh
cd print/stand-sin-2026
node build.mjs            # tutte le grafiche
node build.mjs totem      # solo quelle il cui nome contiene "totem"
node esecutivo.mjs        # il pacchetto di consegna: esecutivo/ e lo zip
node varianti.mjs         # la tavola interna delle tre varianti dei totem
```

Due generazioni consecutive danno file identici, byte per byte: le date di
Chromium vengono tolte, e nel repository cambia solo cio' che e' cambiato.

Serve Playwright con Chromium (`npm install playwright && npx playwright
install chromium`) e `python3` con `pypdf`; `pdftoppm` (poppler) per le
anteprime. Ogni pagina in `src/` dichiara la propria misura in `data-w` /
`data-h` (mm) e in `@page`; `stand.js` porta i lockup con `data-fit-w` alla
larghezza esatta a font caricati. Chromium stampa il PDF vettoriale, `cmyk.py`
riscrive i flussi di contenuto da RGB a CMYK, li ricomprime e si rifiuta di
continuare se trova un'immagine raster, una trasparenza o un operatore colore
che non sa convertire.
