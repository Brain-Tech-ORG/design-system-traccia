# Ritaglio fotografico nella sagoma del marchio

## Ambito

La maschera del marchio è una firma editoriale: si usa nelle **copertine**, nelle hero e nelle
**slide di apertura**. Non sostituisce `.tr-photo-frame` nelle pagine interne e non è un effetto da
ripetere su più immagini nella stessa pagina.

### Usare quando

- una fotografia ambientata introduce un prodotto, un servizio o una sezione;
- la composizione ha abbastanza spazio negativo per far respirare la sagoma;
- il soggetto può essere collocato nella porzione più larga del marchio.

### Non usare quando

- la foto è un ritratto o un primo piano: il taglio separerebbe volto e corpo;
- la foto contiene testo, insegne, schermate, numeri o altri elementi che devono restare leggibili;
- nella stessa area è già presente il logo pieno La Traccia;
- la sorgente è più piccola del box di ritaglio.

## Regole invarianti

1. Il soggetto principale resta centrato nella porzione più larga della sagoma. Correggere prima
   `object-position`; non deformare il marchio.
2. Il marchio ritagliato non convive con il logo pieno nella stessa area. Un logo nel footer è
   ammesso solo quando il footer è una fascia chiaramente separata dalla hero.
3. L'eco outline usa sempre `--tr-watermark-opacity`, resta dietro alla foto e non intercetta il
   puntatore.
4. La risoluzione della foto è almeno pari a larghezza e altezza del box. Per retina/stampa è
   raccomandata una sorgente 2×.
5. Non aggiungere bordi, fondi colorati, ombre o gradienti intorno alla sagoma.

## Geometria della maschera

Le due path arrivano senza modifiche da `assets/logo-traccia.svg`. La sorgente ha viewBox
`1280 × 746.67`; il marchio normalizzato occupa `592.5513333` unità in larghezza e parte da
`x = 317.4745067`, `y = 12.91`.

Per un box `W × H`:

```text
scala  = H / 746.67
offsetX = (W - 592.5513333 × scala) / 2
offsetY = 0
```

Il transform esterno è quindi:

```text
translate(offsetX offsetY)
scale(scala)
translate(-317.4745067 -12.91)
```

Per la copertina `980 × 940`:

```text
scala   = 1.258922951
offsetX = 117.0117634
offsetY = 0
```

## Snippet statico: una volta per pagina

Sostituire `{{offsetX}}`, `{{offsetY}}` e `{{scale}}` con i valori calcolati. Il componente React
esegue il calcolo e genera un ID unico automaticamente; lo snippet è per HTML statico.

```html
<svg class="tr-mark-clip__defs" width="0" height="0" aria-hidden="true" focusable="false">
  <defs>
    <clipPath id="tracciaMarkClip" clipPathUnits="userSpaceOnUse">
      <g transform="translate({{offsetX}} {{offsetY}}) scale({{scale}}) translate(-317.4745067 -12.91)">
        <g transform="matrix(1.3333333,0,0,-1.3333333,0,746.66667)">
          <g transform="translate(564.7686,408.0532)">
            <path d="M -178.98068,140.25259 117.75078,-123.05869 -29.934521,-253.9852 -326.66272,9.3260847 Z"></path>
          </g>
          <g transform="translate(70.5,0)">
            <g transform="translate(490.998,243.2061)">
              <path d="m -186.33241,-230.2956 c 0.37348,48.93181 0.42546,137.18833 -0.12993,264.019319 L -34.288526,-98.229099 c 0,0 -150.504424,-133.424071 -152.043884,-132.066501 Z"></path>
            </g>
          </g>
        </g>
      </g>
    </clipPath>
  </defs>
</svg>
```

### Snippet già calcolato per 980 × 940

```html
<g transform="translate(117.0117634 0) scale(1.258922951) translate(-317.4745067 -12.91)">
  <!-- matrix e due path come sopra -->
</g>
```

## CSS del layout ospite

Il componente non decide la posizione nella copertina. Il template usa `className` e una regola
locale; le dimensioni e la maschera restano responsabilità di `MarkClip`.

```css
.presenze-cover__mark {
  position: absolute;
  inset: -20px 0 auto auto;
  --tr-mark-clip-bleed-inline: 96px;
  --tr-mark-clip-echo-offset-x: 24px;
  --tr-mark-clip-echo-offset-y: 18px;
}
```
