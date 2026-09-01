// Carta intestata La Traccia — generatore del file Word.
//
// Il .docx e' la trasposizione in Word del documento formale del sistema
// (css/traccia-doc.css): stessa gabbia, stesso colophon, stessi filetti. Non
// si modifica a mano il .dotx: si modifica questo script e si rigenera con
// ./build.sh, cosi' il file Word non puo' allontanarsi dal sistema.
//
// Le misure sono in millimetri (il documento e' carta) e si convertono in DXA
// (1/20 di punto, l'unita' di Word: 1 mm = 56,69 DXA). Le taglie dei caratteri
// sono in mezzi punti, come vuole docx-js: 21 = 10,5 pt.

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, WidthType, BorderStyle, PageNumber, VerticalAlign,
  HeightRule, PageBreak, TabStopType, LineRuleType,
} = require("docx");

const ROOT = path.resolve(__dirname, "..", "..");
const asset = (p) => path.join(ROOT, "assets", p);
const here = (p) => path.join(__dirname, p);

// ---- token (tokens/tokens.css) ------------------------------------------
// Word non conosce le custom properties: i valori sono in esadecimale, come
// nella firma email. La sorgente resta tokens.css.
const T = {
  brand500: "4194D7",   // --tr-brand-500: solo elementi non testuali (punti)
  brand600: "2F7AB8",   // --tr-brand-600: testo piccolo in blu (4,57:1 su bianco)
  ink900: "1B1F2A",
  ink600: "3A4050",
  ink400: "565C6B",
  ruleprint: "C9CEDE",  // --tr-border-soft-2: in stampa i filetti salgono di tinta
};
const SANS = "Archivo", SANS_SEMI = "Archivo SemiBold", SANS_XB = "Archivo ExtraBold";
const MONO = "IBM Plex Mono", MONO_SEMI = "IBM Plex Mono SemiBold";

const mm = (v) => Math.round(v * 56.6929);   // mm -> DXA
const px = (v) => Math.round(v * 3.7795);    // mm -> px a 96dpi (misura immagini)
// tracking: docx vuole ventesimi di punto; em * corpo(pt) * 20
const track = (em, pt) => Math.round(em * pt * 20);

// ---- gabbia --------------------------------------------------------------
// --tr-doc-pad-x e' 64px, cioe' 17 mm: il testo non arriva mai al taglio.
// Testa e piede stanno a 10 mm dal bordo. I margini del corpo sono tarati
// sulla testata e sul piede COMPATTI (pagine interne): sulla prima pagina
// Word alza da solo il corpo per far posto al colophon, che e' piu' alto.
const PAGE = { w: 210, h: 297, side: 17, top: 30, bottom: 24, head: 10, foot: 10 };
const TEXT_W = PAGE.w - 2 * PAGE.side;          // 176 mm
const TEXT_W_DXA = mm(TEXT_W);
// La corsia del documento e' 330px su 666 di contenuto (README, "Una gabbia
// sola"): la stessa proporzione porta il filetto di testata a fermarsi sulla
// verticale del gutter, lasciando libero l'angolo del timbro.
const FIELD_W = Math.round(TEXT_W * 330 / 666);  // 87 mm
const STAMP_W = TEXT_W - FIELD_W;

const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const rule = { style: BorderStyle.SINGLE, size: 6, color: T.ruleprint, space: 1 }; // 6 = 0,75pt ~ 1px
const flush = { top: 0, bottom: 0, left: 0, right: 0 };

// ---- voci ---------------------------------------------------------------
const P = (children, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { before: o.before ?? 0, after: o.after ?? 0, line: o.line ?? 240, lineRule: LineRuleType.AUTO },
  tabStops: o.tabs,
  border: o.border,
  children,
});
const spacer = (twips) => new Paragraph({
  spacing: { before: 0, after: 0, line: twips, lineRule: LineRuleType.EXACT },
  children: [new TextRun({ text: "", size: 2 })],
});
// etichetta tecnica: mono, maiuscolo, tracking --tr-tracking-mono (0.08em)
const mono = (text, o = {}) => new TextRun({
  text, font: o.semi ? MONO_SEMI : MONO, size: o.size ?? 14, color: o.color ?? T.ink400,
  allCaps: o.caps ?? true, characterSpacing: track(o.em ?? 0.08, (o.size ?? 14) / 2),
});
const sans = (text, o = {}) => new TextRun({
  text, font: o.font ?? SANS, size: o.size ?? 21, color: o.color ?? T.ink600,
  allCaps: o.caps ?? false, characterSpacing: o.em ? track(o.em, (o.size ?? 21) / 2) : undefined,
});
// il punto separatore e' l'unico blu logo del foglio: non e' testo
const dot = () => new TextRun({ text: "· ", font: MONO, size: 14, color: T.brand500 });
const gap = () => new TextRun({ text: "   ", font: MONO, size: 14 });
const img = (file, wmm, hmm) => new ImageRun({
  type: "png", data: fs.readFileSync(file), transformation: { width: px(wmm), height: px(hmm) },
});
const cell = (children, w, o = {}) => new TableCell({
  width: { size: mm(w), type: WidthType.DXA }, margins: flush,
  borders: { ...noBorders, ...(o.borders || {}) },
  verticalAlign: o.valign ?? VerticalAlign.CENTER, children,
});
const table = (cols, rows) => new Table({
  width: { size: mm(cols.reduce((a, b) => a + b, 0)), type: WidthType.DXA },
  columnWidths: cols.map(mm), borders: noBorders, rows,
});
const pageOf = () => [
  mono("Pagina "),
  new TextRun({ children: [PageNumber.CURRENT], font: MONO_SEMI, size: 14, color: T.ink900, characterSpacing: track(0.08, 7) }),
  mono(" di "),
  new TextRun({ children: [PageNumber.TOTAL_PAGES], font: MONO_SEMI, size: 14, color: T.ink900, characterSpacing: track(0.08, 7) }),
];

// ---- dati d'impresa -------------------------------------------------------
// Sono dati, non stile: stessi valori della firma email e del colophon.
const CO = {
  name: "Cooperativa E.D.P. La Traccia",
  seat: "Recinto II Fiorentini, 10 — 75100 Matera (MT)",
  legal: "P.IVA 00317370773",
  mail: "info@latraccia.it",
  tel: "+39 0835 336836",
  certs: "ISO 9001:2015 · ISO 13485:2016 · ISO/IEC 27001:2022 · UNI PdR 125",
};

// ---- testata --------------------------------------------------------------
// Prima pagina: lockup a sinistra; a destra la zona del timbro, vuota per
// costruzione. Il filetto si ferma sul gutter: e' cio' che dice che l'angolo
// e' riservato e non dimenticato. Pagine interne: lockup ridotto e filetto
// pieno — il timbro si appone una volta sola.
const LOCKUP_H = 8.0;                             // 28px CSS -> ~7,4mm; arrotondato alla carta
const LOCKUP_W = LOCKUP_H * 1239 / 224;
const SMALL_H = 5.6;                              // 20px CSS
const SMALL_W = SMALL_H * 961 / 160;

const headerFirst = new Header({ children: [
  spacer(120),
  table([FIELD_W, STAMP_W], [
    new TableRow({ height: { value: mm(10), rule: HeightRule.ATLEAST }, children: [
      cell([P([img(here("brandmark-lockup.png"), LOCKUP_W, LOCKUP_H)]), spacer(140)], FIELD_W,
        { borders: { bottom: rule } }),
      cell([P([])], STAMP_W),
    ] }),
  ]),
]});

const headerNext = new Header({ children: [
  spacer(120),
  table([TEXT_W], [
    new TableRow({ height: { value: mm(7), rule: HeightRule.ATLEAST }, children: [
      cell([P([img(here("brandmark-lockup-small.png"), SMALL_W, SMALL_H)])], TEXT_W),
    ] }),
  ]),
  P([], { before: 80, border: { bottom: rule } }),
]});

// ---- piede ---------------------------------------------------------------
// Prima pagina: il colophon di .tr-doc-footer — chi emette (nome a contrasto
// pieno, sede in frase, identificativi in mono), recapiti a destra, riga
// certificazioni con badge. Il wordmark non compare: lo sostituisce la
// ragione sociale, resta il solo marchio.
const MARK_H = 5.0, MARK_W = MARK_H * 594 / 717;
const CERTS_H = 7.5, CERTS_W = CERTS_H * 452 / 118;
const ruleTop = () => P([], { after: 100, border: { top: rule } });

const footerFirst = new Footer({ children: [
  ruleTop(),
  table([9, 118, 49], [
    new TableRow({ children: [
      cell([P([img(here("mark.png"), MARK_W, MARK_H)])], 9, { valign: VerticalAlign.TOP }),
      cell([
        P([sans(CO.name, { font: SANS_XB, size: 16, color: T.ink900, caps: true, em: 0.08 })], { after: 30 }),
        P([sans(CO.seat, { size: 16 })], { after: 30 }),
        P([mono(CO.legal, { size: 14, color: T.ink600, em: 0.03, caps: false })]),
      ], 118, { valign: VerticalAlign.TOP }),
      cell([
        P([mono(CO.mail, { caps: false, em: 0.06 })], { align: AlignmentType.RIGHT, after: 30 }),
        P([mono(CO.tel, { em: 0.06 })], { align: AlignmentType.RIGHT, after: 30 }),
        P(pageOf(), { align: AlignmentType.RIGHT }),
      ], 49, { valign: VerticalAlign.TOP }),
    ] }),
  ]),
  P([], { before: 120, border: { bottom: rule } }),
  table([136, 40], [
    new TableRow({ height: { value: mm(10), rule: HeightRule.ATLEAST }, children: [
      cell([P([
        mono("Certificazioni", { semi: true, color: T.brand600, em: 0.14 }), gap(),
        mono(CO.certs, { caps: false, em: 0.03 }),
      ])], 136),
      cell([P([img(asset("certificazioni.png"), CERTS_W, CERTS_H)], { align: AlignmentType.RIGHT })], 40),
    ] }),
  ]),
]});

// Pagine interne: una riga sola. Il piede deve ancora dire chi ha emesso il
// foglio — una pagina staccata dal fascicolo si ritrova mesi dopo — ma senza
// l'apparato: nome, sede, P.IVA e numero di pagina.
const footerNext = new Footer({ children: [
  ruleTop(),
  P([
    sans(CO.name, { font: SANS_XB, size: 14, color: T.ink900, caps: true, em: 0.08 }), gap(),
    dot(), sans(CO.seat, { size: 15 }), gap(),
    dot(), mono(CO.legal, { color: T.ink600, em: 0.03, caps: false }),
    new TextRun({ text: "\t", size: 14 }),
    ...pageOf(),
  ], { tabs: [{ type: TabStopType.RIGHT, position: TEXT_W_DXA }] }),
]});

// ---- corpo: lettera d'esempio, da sostituire ------------------------------
const body = (text, o = {}) => P([sans(text)], { after: o.after ?? 160, line: 300 });
const eyebrow = (label) => P(
  [mono(label, { semi: true, size: 15, color: T.brand600, em: 0.22 })],
  { before: 360, after: 120, border: { bottom: { ...rule, space: 4 } } },
);

const children = [
  P([mono("Matera, 31 agosto 2026", { size: 15, caps: false })], { align: AlignmentType.RIGHT, after: 480 }),
  // Spett.le e c.a. non sono etichette di sistema: sono la lingua della lettera, in frase
  P([sans("Spett.le", { size: 21 })], { after: 60 }),
  P([sans("Nome del destinatario", { font: SANS_SEMI, size: 24, color: T.ink900 })], { after: 20 }),
  P([sans("Indirizzo — CAP Città (PR)")], { after: 20 }),
  P([sans("c.a. Ufficio / Referente", { size: 20, color: T.ink400 })]),

  eyebrow("Oggetto"),
  P([sans("Oggetto della comunicazione", { font: SANS_XB, size: 30, color: T.ink900 })], { after: 400, line: 276 }),

  body("Gentile Destinatario,"),
  body("questo documento è la carta intestata di La Traccia. L’intestazione e il piè di pagina si ripetono da soli: la prima pagina porta il colophon completo, dalla seconda in poi restano il marchio ridotto e una riga di identificazione con il numero di pagina. Sostituisca questo testo con il contenuto della lettera."),
  body("Il corpo usa Archivo 10,5 pt con interlinea 1,25 e 8 pt fra i paragrafi; i titoli Archivo ExtraBold; le etichette IBM Plex Mono. L’unico accento è il blu del marchio, e sul testo piccolo prende la tinta scura brand/600."),
  body("Restiamo a disposizione per ogni chiarimento e porgiamo cordiali saluti.", { after: 600 }),

  P([mono(CO.name)], { after: 60 }),
  P([sans("Nome Cognome", { font: SANS_SEMI, size: 22, color: T.ink900 })], { after: 20 }),
  P([sans("Ruolo", { size: 20, color: T.ink400 })]),

  // seconda pagina d'esempio: mostra testata e piede compatti. Si elimina.
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ style: "Heading1", children: [new TextRun("Pagine successive")] }),
  body("Dalla seconda pagina in poi testata e piede passano alla versione compatta: marchio ridotto e filetto in alto, ragione sociale, sede, P.IVA e numero di pagina in basso. Il corpo guadagna circa due centimetri e mezzo per pagina."),
  body("Questa pagina serve solo a mostrarla: si elimina insieme al testo d’esempio della prima."),
];

const ttf = (f) => fs.readFileSync(asset(path.join("fonts", "ttf", f)));

const doc = new Document({
  creator: "La Traccia",
  title: "Carta intestata La Traccia",
  // I font viaggiano dentro il file: e' la versione Word di css/traccia-fonts.css.
  // Word incorpora un file per nome, quindi i pesi sono famiglie distinte.
  fonts: [
    { name: SANS, data: ttf("Archivo-Regular.ttf") },
    { name: SANS_SEMI, data: ttf("Archivo-SemiBold.ttf") },
    { name: SANS_XB, data: ttf("Archivo-ExtraBold.ttf") },
    { name: MONO, data: ttf("IBMPlexMono-Regular.ttf") },
    { name: MONO_SEMI, data: ttf("IBMPlexMono-SemiBold.ttf") },
  ],
  styles: {
    default: {
      document: {
        run: { font: SANS, size: 21, color: T.ink600 },
        paragraph: { spacing: { after: 160, line: 300, lineRule: LineRuleType.AUTO } },
      },
    },
    paragraphStyles: [
      { id: "Heading1", name: "heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SANS_XB, size: 32, color: T.ink900 }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SANS_SEMI, size: 24, color: T.ink900 }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Etichetta", name: "Etichetta", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: MONO_SEMI, size: 15, color: T.brand600, allCaps: true, characterSpacing: track(0.22, 7.5) },
        paragraph: { spacing: { before: 240, after: 80 } } },
      { id: "Dato", name: "Dato tecnico", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: MONO, size: 17, color: T.ink900, characterSpacing: track(0.03, 8.5) }, paragraph: { spacing: { after: 60 } } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: mm(PAGE.w), height: mm(PAGE.h) },
        margin: { top: mm(PAGE.top), bottom: mm(PAGE.bottom), left: mm(PAGE.side), right: mm(PAGE.side), header: mm(PAGE.head), footer: mm(PAGE.foot) },
      },
      titlePage: true,
    },
    headers: { first: headerFirst, default: headerNext },
    footers: { first: footerFirst, default: footerNext },
    children,
  }],
});

const out = process.argv[2] || here("carta-intestata.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("scritto", path.relative(process.cwd(), out), buf.length, "byte");
});
