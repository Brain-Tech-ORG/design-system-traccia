# MarkClip

## Scopo

`MarkClip` ritaglia una fotografia nelle due forme del marchio La Traccia e, quando richiesto,
allinea dietro alla foto la versione outline del medesimo marchio. È una primitiva per
**copertine e slide di apertura**, non un trattamento fotografico generico.

## Props

- `src` e `alt`: sorgente e testo alternativo della foto.
- `width` e `height`: dimensioni effettive del box in pixel CSS.
- `objectPosition`: inquadratura CSS; default `50% 50%`.
- `echo`: abilita la sagoma outline dietro al ritaglio.
- `echoSrc`: sorgente dell'outline; obbligatoria se `echo` è attivo.
- `bleed`: applica `.tr-mark-clip--bleed` per lo sbordo oltre il margine logico finale.
- `className`: gancio per il posizionamento nel layout ospite.

## Regole d'uso

1. Usare il componente solo su copertine, hero editoriali e slide di apertura.
2. Non usarlo per ritratti, primi piani o fotografie che contengono testo, insegne o dati da leggere.
3. Tenere il soggetto nella porzione più larga della sagoma, regolando `objectPosition` prima di
   cambiare scala o geometria della maschera.
4. Il marchio ritagliato e il logo pieno non convivono nella stessa area visuale. Il logo pieno può
   restare nel footer, se separato chiaramente dalla hero.
5. L'eco resta sempre a `var(--tr-watermark-opacity)`; non aumentare l'opacità per compensare una
   foto poco contrastata.
6. La foto sorgente deve avere risoluzione almeno pari a `width × height`; per stampa o retina usare
   preferibilmente il doppio.

## Contratto di implementazione

- Montare un `<clipPath>` con ID unico per ogni istanza (`useId`).
- Usare `clipPathUnits="userSpaceOnUse"` e le due path di `assets/logo-traccia.svg` senza
  semplificarle o ridisegnarle.
- La scala è `height / 746.67`; la centratura orizzontale è
  `(width - 592.5513333 × scala) / 2`.
- Non usare attributi `style` sugli elementi. Le misure dinamiche vanno su una classe di istanza
  che valorizza le variabili di `.tr-mark-clip`.
- L'immagine usa sempre `.tr-mark-clip__img`; l'outline usa `.tr-mark-clip__echo`; lo sbordo usa
  `.tr-mark-clip--bleed`.
- Non introdurre un secondo colore, una cornice, un'ombra o un gradiente.

## Esempio

```jsx
<MarkClip
  src="assets/sede.jpg"
  alt="Sede La Traccia"
  width={980}
  height={940}
  objectPosition="50% 50%"
  echo
  echoSrc="assets/logo-traccia-outline.svg"
  bleed
/>
```
