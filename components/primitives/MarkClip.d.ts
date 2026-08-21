import type { ReactElement } from "react";

export interface MarkClipProps {
  /** URL della foto da ritagliare. */
  src: string;
  /** Testo alternativo della foto; usare stringa vuota solo per immagini decorative. */
  alt: string;
  /** Larghezza del box di ritaglio, in pixel CSS. */
  width: number;
  /** Altezza del box di ritaglio, in pixel CSS. */
  height: number;
  /** Posizione CSS del soggetto nella foto, per esempio "50% 50%" o "center 35%". */
  objectPosition?: string;
  /** Mostra la sagoma outline sfalsata dietro al ritaglio. */
  echo?: boolean;
  /** URL di assets/logo-traccia-outline.svg; obbligatorio quando echo è true. */
  echoSrc?: string;
  /** Applica il modificatore di sbordo sul margine logico finale. */
  bleed?: boolean;
  /** Classi aggiuntive per il posizionamento nel layout ospite. */
  className?: string;
}

declare function MarkClip(props: MarkClipProps): ReactElement;
export default MarkClip;
