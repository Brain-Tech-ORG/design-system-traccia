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
| `totem-a-istituzionale.pdf` | Totem 1 e 2, lato A | 100×200 | — | Marchio, «Dal 1980 · Matera», la cifra «oltre 400 installazioni», le tre linee (Gepadial in testa), certificazioni, contatti |
| `totem-b1-ambulatorio-ia.pdf` | Totem 1, lato B | 100×200 | — | Eyebrow «Novita' · Hardware custom», titolo «Modelli IA per la nefrologia»; il wireframe del microfono AI (sigla AI sulla capsula) e accanto «Ambulatorio» e «Rilevazioni a bordo letto» |
| `totem-b2-dati-ia.pdf` | Totem 2, lato B | 100×200 | — | Solo istituzionale: eyebrow «Gen BI · Dati clinici e IA», titolo «I dati clinici prendono forma», il marchio fatto di punti — una mappa di dati, con tre anelli per i dati che l'IA segnala — certificazioni, contatti |
| `parete-sinistra.pdf` | Parete sinistra | 420×220 | ~370×200 | Solo grafica: la sagoma outline del marchio a sbordo dal bordo alto, verso l'ingresso. Gli ultimi 30 cm a destra (giunzione) sono bianchi |
| `parete-destra.pdf` | Parete destra | 470×220 | ~450×200 | Solo grafica: la stessa sagoma, a sbordo dal bordo alto verso l'ingresso |

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

**Totem, lato A: chi siamo.** Marchio in testa, eyebrow «Dal 1980 · Matera»,
poi la cifra in evidenza di `.tr-figure` — «oltre», **400**, «installazioni»
— che dice chi siamo senza claim, un lead di una frase, tre linee di
nefrologia e dialisi come `.tr-numbered-list` (la cartella clinica si chiama
Gepadial, e basta il nome), e in calce la riga certificazioni, che sta sulle
superfici pubbliche, e un totem in corsia lo e', con sito e email.

**Totem, lato B: le novita', in modo grafico e vago.** Nessuna schermata,
nessuna spiegazione. La testata e' quella del lato A — marchio alla stessa
misura, eyebrow, titolo display — e la sagoma outline sborda in basso,
perche' anche da questo lato si capisca subito di chi e' il totem. Sul primo
il titolo e' «Modelli IA per la nefrologia» (non «intelligenza
artificiale»), con la nota dell'eyebrow che dice «Hardware custom»: e' li'
che si scrive che cos'e', non in una didascalia sotto il disegno. Sotto, il
**wireframe del microfono AI**, disegnato con le convenzioni del disegno
tecnico del sistema (`.tr-drawing`: silhouette con tratto `ink/900` e
riempimento `surface/tint`, dettagli in blu: l'anello LED, l'anello della
base, le onde senza fili) con la sola sigla **AI** in display sulla capsula,
e accanto le due parole con il tratto d'accento: «Ambulatorio», «Rilevazioni
a bordo letto».

**Totem 2, lato B: solo istituzionale.** Nessuna novita' di prodotto: un
gioco con il marchio e il tema della gestione dei dati clinici con l'IA (gen
BI). Testata come sul lato A — marchio, eyebrow «Gen BI · Dati clinici e
IA», titolo «I dati clinici prendono forma» — e in calce certificazioni e
contatti. Sotto il titolo il **marchio fatto di punti**: le due figure del
logo campionate su un reticolo parallelo ai loro lati, cosi' i bordi restano
dritti e la fessura fra le due figure resta aperta. Da lontano e' il logo, da
vicino una mappa di dati: la tinta di ogni punto (`brand/300` → `brand/600`)
e' il suo valore, piu' scura verso la punta; tre anelli sono i dati che l'IA
segnala. Il reticolo lo genera `src/dot-mark.js`, deterministico: stesso
seme, stesso disegno, stesso PDF. In entrambi i lati B il disegno sta a
meta' tra il titolo e il piede.

**Pareti laterali: solo grafica, e poca.** Niente testo: su ciascuna parete
la sola sagoma outline del marchio, a sbordo dal bordo alto verso l'ingresso
dello stand — a sinistra sulla parete sinistra, a destra su quella destra. La
posizione e' specchiata, il disegno no: il marchio non si ribalta. E' il
watermark del sistema alla scala della parete; tutto il resto e' bianco.

### Scala tipografica

Due formati, due scale (`src/stand.css`). I valori sono centimetri in opera.
Le pareti oggi non portano testo: la scala resta definita per quando dovesse
servire.

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

1. **La cifra del totem A** — oltre 400 installazioni — e' quella indicata
   nel brief. Le tre linee (cartella clinica Gepadial; sedute di dialisi e
   trattamenti domiciliari; ambulatori e telemedicina) sono una scelta per il
   pubblico della SIN.
2. **Il microfono** e' un wireframe generico — capsula, stelo, base con
   anello luminoso, onde senza fili — non il disegno del dispositivo reale.
   Se il prodotto ha una forma riconoscibile, il disegno va rifatto su quella.
3. **La riga certificazioni** e' solo testo: i badge IMQ / SI Cert sono un PNG
   che ingrandito dieci volte non regge. Se servono, vanno chiesti in vettoriale
   agli enti.
4. **I totem** non hanno un'area nascosta dichiarata: il contenuto tiene 8 cm
   dal bordo. Se il profilo copre di piu', va detto.
5. **Il microfono AI e la gen BI** sono raccontati come concetti, senza
   schermate: e' coerente con la scelta, verbalizzata nella call del 25/9, di
   non esporre il prototipo a tutti.
6. **Il fondale e la quinta** esistono in due versioni: con la sagoma outline
   a sbordo (`fondale-1.pdf`, `fondale-2-quinta.pdf`) e con il solo lockup
   (`--solo-logo`). Va mandata a Scuotto una delle due coppie.

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
