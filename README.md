# La Traccia — Design System

Design system aziendale de **La Traccia** (software house — prodotti per PA, sanità e imprese).
Coerente con la brochure **Tmas A100** e il deck istituzionale: grafica minimale basata su linee
sottili e colore, geometrie morbide e smussate, layout aperti senza box. Niente ombre pesanti,
niente gradienti, niente emoji, molto bianco.

## Struttura del repository

```
├── assets/
│   ├── logo-traccia.svg          Logo (chevron blu, pieno)
│   ├── logo-traccia-outline.svg  Sagoma outline per watermark negli sfondi
│   └── certificazioni.png        Badge certificazioni (IMQ / SI Cert)
├── tokens/
│   ├── tokens.css                Design token come CSS custom properties
│   └── tokens.json               Design token in formato W3C draft
├── css/traccia.css               Libreria componenti (prefisso .tr-)
└── index.html                    Documentazione visiva / showcase
```

## Uso rapido

```html
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="tokens/tokens.css">
<link rel="stylesheet" href="css/traccia.css">

<body class="tr-page">
  <h1 class="tr-h1">Titolo con parola <em>chiave</em></h1>
</body>
```

## Brand

- **Logo**: chevron/freccia blu (`assets/logo-traccia.svg`). Compare sempre affiancato al wordmark
  **LA TRACCIA** in maiuscolo con letter-spacing 0.08em (componente `.tr-brandmark`).
- **Logo nello sfondo (watermark)**: la sagoma outline del logo
  (`assets/logo-traccia-outline.svg` — stessi tracciati, senza riempimento, tratto blu logo)
  può essere usata negli sfondi delle brochure e delle pagine delle presentazioni:
  opacità 0.16 sul paper, dietro ai contenuti, tipicamente a sbordo da un angolo pagina,
  `pointer-events: none`. Componente `.tr-watermark` dentro un `.tr-watermark-host`
  (position relative + overflow hidden), con varianti di posizione `--top-right` e `--bottom-left`.
- **Tono**: tecnico, sobrio, istituzionale ma moderno.

## Palette

| Token | Hex | Uso |
|---|---|---|
| `brand/500` | `#4194d7` | Blu logo. **Unico accento**: evidenze, numeri, quote, dot, icone |
| `brand/300` | `#8fc0e7` | Linee secondarie |
| `brand/100` | `#d0e4f5` | Tinta pallida decorativa |
| `brand/600` | `#2f7ab8` | Tinta scura, stesso hue: testo piccolo e fondi pieni con testo bianco (4,6:1) |
| `brand/700` | `#266296` | Tinta scura, stesso hue: hover delle superfici piene |
| `surface/tint` | `#eff2f9` | Solo riempimenti piccoli (cerchietti, silhouette). **Mai** sfondi di card/pannelli |
| `border/soft` | `#dde2ee` / `#c9cede` | Filetti e bordi leggeri |
| `ink/900` | `#1b1f2a` | Testo primario, tratti dei disegni tecnici |
| `ink/600` | `#3a4050` | Testo secondario / body |
| `ink/400` | `#565c6b` | Didascalie e metadati |
| `paper` | `#fbfbfd` | Sfondo pagina |
| `state/danger` | `#a53a3a` | **Solo UI software**: errore, campo non valido |
| `state/warning` | `#99631d` | **Solo UI software**: avviso, azione da confermare |
| `state/success` | `#2f6b45` | **Solo UI software**: esito positivo |

**Regola**: mai introdurre altri hue. Per varianti usare oklch mantenendo lo stesso hue del blu logo.
Unica eccezione, e solo nell'interfaccia software: le tre tinte `state/*` per la validazione
dei form e gli esiti di sistema — vedi [Pagine di login](#pagine-di-login-prodotti-software).

## Tipografia

- **Display/UI — Archivo (400–800)**: titoli in maiuscolo, weight 800, tracking −0.015em,
  line-height 1.04–1.15; la parola chiave finale in blu logo (markup: `<em>` dentro `.tr-h1/.tr-h2`).
- **Tecnico/etichette — IBM Plex Mono (400–600)**: sempre maiuscolo, tracking 0.06–0.3em, per
  eyebrow/kicker, numerazioni, quote, specifiche, contatti, metadati.
- **Body — Archivo 400**: 12–14px stampa / 14–16px UI / 24–30px slide, line-height 1.5–1.65, ink/600.
- **Slide 16:9 (1920×1080)**: mai testo sotto 17px; titoli 60–92px.

## Linguaggio geometrico

- **Layout aperti**: niente box, niente sfondi colorati dietro i contenuti, niente bordi-contenitore.
  La struttura la danno filetti sottili, spaziatura e allineamenti a griglia.
- **Linee stondate** (radius 99px): filetti orizzontali 1–2px `border/soft` (`.tr-rule`);
  segmenti verticali 2px in brand — pieni sopra il contenuto, tinta chiara sotto (`.tr-vseg`).
- **Tratti d'accento** ~64×3px stondati sopra i titoli di sezione (`.tr-accent-dash`),
  al posto di bordi a larghezza piena.
- **Pillole** (radius 999px) e angoli smussati 16–26px solo dove serve un contenitore vero.
- **Cerchietti numerati** 24–52px (`.tr-circle`): tinta + cifra mono blu, solo bordo blu
  (`--outline`) o pieno blu (`--solid`).
- **Dot bullet**: pallino pieno blu 6–13px + voce mono (`.tr-dot`, `.tr-dotlist`).
- **Triangoli/chevron** solo come richiamo del logo, con parsimonia.
- **Foto**: render/scontornati PNG fluttuano sul fondo pagina (`.tr-photo-float`,
  object-fit contain); le foto ambientate stanno in cornice arrotondata 22–36px con bordo
  1px `border/soft` e padding 7–14px (`.tr-photo-frame`).

## Componenti

| # | Componente | Classe |
|---|---|---|
| 1 | Header di pagina | `.tr-header` + `.tr-brandmark` |
| 2 | Eyebrow / kicker (con variante nota a destra) | `.tr-eyebrow` |
| 3 | Chip / pill | `.tr-chip` |
| 4 | Voce elenco numerata | `.tr-numbered` |
| 5 | Step di processo (riga da 4, linea `brand/300`) | `.tr-steps.tr-steps--linked` > `.tr-step` |
| 6 | Riga specifiche / elenco tecnico | `.tr-specs`, `.tr-dotlist` |
| 7 | Tabella dati (nota unità in basso a destra) | `.tr-datatable` |
| 8 | Disegno tecnico quotato (convenzioni SVG) | `.tr-drawing` (`.silhouette`, `.quota`, `.quota-label`) |
| 9 | Footer (con riga certificazioni sempre presente) | `.tr-footer` + `.tr-footer__certs` |
| 10 | Pagina di login (co-branding con il cliente) | `.tr-login` + `.tr-clientmark` |
| 11 | H1/H2 con parola chiave blu | `.tr-h1`, `.tr-h2` + `<em>` |

Tutti i componenti sono mostrati e documentati in [`index.html`](index.html).

### Footer e certificazioni

Il footer include **sempre** la riga certificazioni (`.tr-footer__certs`): etichetta
`CERTIFICAZIONI` in mono blu (tracking 0.14em), elenco in mono grigio
`ISO 9001:2015 · ISO 13485:2016 · ISO/IEC 27001:2022 · UNI PdR 125`, filetto stondato
`border/soft` che riempie la riga e badge `assets/certificazioni.png`
(IMQ Certified + SI Cert, altezza ~30px).

### Convenzioni disegno tecnico

Silhouette con tratto `ink/900` 2–2.5px e riempimento `surface/tint`, angoli reali del prodotto.
Linee di quota blu 1.5–3px con tacche alle estremità; valore in mono blu con **virgola decimale
italiana** (es. `1.580,0`).

## Pagine di login (prodotti software)

Le pagine di accesso ai prodotti sono l'unico punto in cui il sistema incontra
il marchio di un **cliente**. Valgono le regole generali — layout aperto, niente
card, niente ombre, niente gradienti — piu' le seguenti.

### Co-branding: un solo marchio per lockup

| Posizione | Marchio | Note |
|---|---|---|
| Testata | **Cliente** (`.tr-clientmark`) | La pagina e' il suo prodotto: il suo marchio sta in alto a sinistra, affiancato dal nome del prodotto in mono. |
| Sfondo | La Traccia, sagoma outline (`.tr-watermark`) | Opzionale, opacita' 0,16, a sbordo da un angolo. E' la presenza di marchio "ambientale". |
| Footer | La Traccia (`.tr-footer` + `.tr-brandmark`) | Firma del fornitore, sempre con la riga certificazioni. |

**Mai i due marchi affiancati nello stesso lockup**: un logo cliente accanto al
chevron La Traccia produce un blocco confuso e sposta l'identita' della pagina.
La gerarchia e' sempre cliente in testa, La Traccia in calce.

Il logo del cliente **non si ricolora, non si ridisegna e non si mette dentro un
riquadro**: si appoggia sul paper alla sua altezza nominale
(`--tr-client-logo-h`, 40px; 32px sotto i 720px). Se il file del cliente ha un
margine trasparente proprio, va ritagliato prima di essere usato, non compensato
con il padding.

### Struttura

```html
<body class="tr-login tr-watermark-host">
  <img class="tr-watermark tr-watermark--top-right" src="assets/logo-traccia-outline.svg" alt="" aria-hidden="true">

  <header class="tr-login__header">
    <div class="tr-header">
      <a class="tr-clientmark" href="/">
        <img class="tr-clientmark__logo" src="logo-cliente.svg" alt="Nome cliente">
        <span class="tr-clientmark__sep"></span>
        <span class="tr-clientmark__product">Nome prodotto</span>
      </a>
      <span class="tr-eyebrow__label">Accesso riservato</span>
    </div>
  </header>

  <main class="tr-login__main">
    <div class="tr-login__panel">
      <div class="tr-eyebrow"><span class="tr-eyebrow__label">Accesso</span><span class="tr-eyebrow__line"></span></div>
      <h1 class="tr-h2">Accedi al <em>registro</em></h1>
      <!-- .tr-field / .tr-btn -->
    </div>
  </main>

  <div class="tr-login__footer"><footer class="tr-footer">...</footer></div>
</body>
```

Ogni passo del flusso — credenziali, secondo fattore, configurazione 2FA,
cambio password obbligatorio, recupero credenziali — usa la **stessa
intestazione**: eyebrow mono con filetto, titolo `.tr-h2` con la parola chiave
in blu, testo di servizio in body. Cambia il contenuto, non la struttura.

### Controlli

La pagina di login introduce i tre controlli di interfaccia del sistema, riusabili
ovunque nella UI software:

| Componente | Classe | Nota |
|---|---|---|
| Campo | `.tr-field` + `__label` / `__control` / `__hint` / `__error` | Fondo trasparente e filetto 1px che vira al blu sul focus. Nessuna ombra, nessun ring. Varianti `--error` e `--code` (cifre OTP mono distanziate). |
| Azione | `.tr-btn` + `--primary` / `--secondary` / `--quiet` / `--block` | Pillola 999px con etichetta mono maiuscola, come la chip. |
| Avviso in linea | `.tr-notice` + `--danger` / `--warning` / `--success` | Filetto verticale colorato: il sistema non ammette pannelli con sfondo colorato dietro ai contenuti. |

### Stati di validazione

`--tr-state-danger` / `--tr-state-warning` / `--tr-state-success` sono l'**unica
eccezione ammessa alla regola del singolo hue**, e valgono solo per
l'interfaccia software: validazione dei form ed esiti di sistema. Sono tinte
desaturate, scelte per convivere con il blu logo senza competere con esso. Su
brochure, slide e materiale stampato non si usano.

### Contrasto

Il blu logo `#4194d7` non regge il testo bianco (2,9:1). Per le superfici piene
con testo bianco e per il testo piccolo in blu si usano le tinte scure dello
stesso hue: `--tr-brand-600` (`#2f7ab8`, 4,6:1 su bianco) e `--tr-brand-700`
per l'hover. `#4194d7` resta per elementi non testuali — dot, filetti, icone —
e per il testo grande in grassetto.

## Vincoli

- **Minimalismo**: whitespace generoso; max un colore d'accento per composizione.
- **Multi-formato**: lo stesso sistema serve brochure A4 stampata, schermo e slide 16:9.
- **Accessibilità**: contrasto testo ≥ 4.5:1. Il blu `#4194d7` su bianco si usa solo a taglie
  ≥ 12px bold o per elementi non testuali; il testo body è sempre in ink. Per testo piccolo in
  blu e per i fondi pieni con testo bianco si usa `brand/600` (`#2f7ab8`).
- Niente icone illustrative complesse; solo forme base (cerchi, linee, triangoli).
