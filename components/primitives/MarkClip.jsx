import React, { useId, useMemo } from "react";

const SOURCE_WIDTH = 1280;
const SOURCE_HEIGHT = 746.67;
const NORMALIZED_X = 317.4745067;
const NORMALIZED_Y = 12.91;
const MARK_WIDTH = 592.5513333;

const PRIMARY_PATH =
  "M -178.98068,140.25259 117.75078,-123.05869 -29.934521,-253.9852 -326.66272,9.3260847 Z";
const SECONDARY_PATH =
  "m -186.33241,-230.2956 c 0.37348,48.93181 0.42546,137.18833 -0.12993,264.019319 L -34.288526,-98.229099 c 0,0 -150.504424,-133.424071 -152.043884,-132.066501 Z";

const POSITION_TOKEN =
  /^(?:left|center|right|top|bottom|-?\d+(?:\.\d+)?(?:%|px|rem|em|vw|vh))$/i;

function finiteDimension(value, name) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric <= 0) {
    throw new TypeError(`${name} deve essere un numero positivo.`);
  }
  return numeric;
}

function safeObjectPosition(value) {
  const position = String(value ?? "50% 50%").trim();
  const tokens = position.split(/\s+/);
  if (tokens.length < 1 || tokens.length > 2 || tokens.some((token) => !POSITION_TOKEN.test(token))) {
    throw new TypeError(
      'objectPosition accetta uno o due token CSS semplici, per esempio "50% 50%" o "center 35%".',
    );
  }
  return position;
}

function safeScope(value) {
  const token = String(value).replace(/[^a-zA-Z0-9_-]/g, "");
  return token || "mark-clip";
}

function cssNumber(value) {
  return Number(value.toFixed(6));
}

/**
 * Ritaglia una foto nelle due forme del marchio La Traccia.
 * Le dimensioni dinamiche sono espresse come variabili su una classe di istanza:
 * nessun elemento riceve un attributo style.
 */
export default function MarkClip({
  src,
  alt,
  width,
  height,
  objectPosition = "50% 50%",
  echo = false,
  echoSrc,
  bleed = false,
  className = "",
}) {
  const reactId = useId();
  const instanceClass = useMemo(() => `tr-mark-clip-scope-${safeScope(reactId)}`, [reactId]);
  const clipId = `${instanceClass}-path`;

  const boxWidth = finiteDimension(width, "width");
  const boxHeight = finiteDimension(height, "height");
  const position = safeObjectPosition(objectPosition);
  const scale = boxHeight / SOURCE_HEIGHT;
  const maskOffsetX = (boxWidth - MARK_WIDTH * scale) / 2;
  const maskOffsetY = 0;
  const canvasLeft = maskOffsetX - NORMALIZED_X * scale;
  const canvasTop = maskOffsetY - NORMALIZED_Y * scale;
  const canvasWidth = SOURCE_WIDTH * scale;
  const canvasHeight = SOURCE_HEIGHT * scale;

  if (echo && !echoSrc) {
    throw new TypeError("echoSrc è obbligatorio quando echo è true.");
  }

  const classes = [
    "tr-mark-clip",
    instanceClass,
    bleed ? "tr-mark-clip--bleed" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const instanceCss = `
.${instanceClass} {
  --tr-mark-clip-width: ${cssNumber(boxWidth)}px;
  --tr-mark-clip-height: ${cssNumber(boxHeight)}px;
  --tr-mark-clip-scale: ${cssNumber(scale)};
  --tr-mark-clip-mask-offset-x: ${cssNumber(maskOffsetX)}px;
  --tr-mark-clip-mask-offset-y: ${cssNumber(maskOffsetY)}px;
  --tr-mark-clip-object-position: ${position};
  --tr-mark-clip-path: url(#${clipId});
  --tr-mark-clip-canvas-left: ${cssNumber(canvasLeft)}px;
  --tr-mark-clip-canvas-top: ${cssNumber(canvasTop)}px;
  --tr-mark-clip-canvas-width: ${cssNumber(canvasWidth)}px;
  --tr-mark-clip-canvas-height: ${cssNumber(canvasHeight)}px;
}`;

  const maskTransform = [
    `translate(${cssNumber(maskOffsetX)} ${cssNumber(maskOffsetY)})`,
    `scale(${cssNumber(scale)})`,
    `translate(${-NORMALIZED_X} ${-NORMALIZED_Y})`,
  ].join(" ");

  return (
    <figure className={classes} data-tr-mark-clip="">
      <style>{instanceCss}</style>

      <svg
        className="tr-mark-clip__defs"
        width="0"
        height="0"
        aria-hidden="true"
        focusable="false"
      >
        <defs>
          <clipPath id={clipId} clipPathUnits="userSpaceOnUse">
            <g transform={maskTransform}>
              <g transform="matrix(1.3333333,0,0,-1.3333333,0,746.66667)">
                <g transform="translate(564.7686,408.0532)">
                  <path d={PRIMARY_PATH} />
                </g>
                <g transform="translate(70.5,0)">
                  <g transform="translate(490.998,243.2061)">
                    <path d={SECONDARY_PATH} />
                  </g>
                </g>
              </g>
            </g>
          </clipPath>
        </defs>
      </svg>

      {echo ? (
        <img
          className="tr-mark-clip__echo"
          src={echoSrc}
          alt=""
          aria-hidden="true"
          draggable="false"
          decoding="async"
        />
      ) : null}

      <img
        className="tr-mark-clip__img"
        src={src}
        alt={alt}
        draggable="false"
        decoding="async"
      />
    </figure>
  );
}
