// Il marchio a punti.
//
// Le due figure del logo — il parallelogramma e il triangolo di
// assets/logo-traccia-mark.svg (viewBox 594 x 717) — campionate su un
// reticolo parallelo ai loro lati: i bordi restano dritti, la fessura fra le
// due figure resta aperta, e il segno si riconosce da lontano. Da vicino ogni
// punto e' un dato. Tutto e' deterministico: stesso seme, stesso disegno, e
// il PDF non cambia da una generazione all'altra.
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  // Vertici del parallelogramma (A in alto, B la punta, D a sinistra) e del
  // triangolo (T1 in alto, T2 la punta, T3 in basso).
  const A = [197.4, 0.6], B = [593, 351.7], D = [0.5, 175.2];
  const T1 = [183.1, 362.4], T2 = [386, 538.4], T3 = [183.2, 714.5];

  const step = (p, q, n) => [(q[0] - p[0]) / n, (q[1] - p[1]) / n];
  const at = (o, a, ka, b, kb) => [o[0] + a[0] * ka + b[0] * kb, o[1] + a[1] * ka + b[1] * kb];

  // mulberry32: un generatore piccolo e ripetibile.
  function rng(seed) {
    let s = seed >>> 0;
    return function () {
      s = (s + 0x6d2b79f5) | 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // n x m punti nel parallelogramma, una scala di t passi nel triangolo.
  function markDots(n, m, t) {
    const pts = [];
    const u = step(A, B, n), v = step(A, D, m);
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < m; j++) {
        const [x, y] = at(A, u, i + 0.5, v, j + 0.5);
        pts.push({ x, y, key: `p${i}-${j}` });
      }
    }
    const e1 = step(T2, T1, t), e2 = step(T2, T3, t);
    for (let a = 0; a < t; a++) {
      for (let b = 0; a + b <= t - 2; b++) {
        const [x, y] = at(T2, e1, a + 0.5, e2, b + 0.5);
        pts.push({ x, y, key: `t${a}-${b}` });
      }
    }
    return pts;
  }

  function dot(g, x, y, r, cls) {
    const c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', x.toFixed(2));
    c.setAttribute('cy', y.toFixed(2));
    c.setAttribute('r', String(r));
    c.setAttribute('class', cls);
    g.appendChild(c);
  }

  // Il marchio a punti. Con `levels` ogni punto prende la tinta del suo
  // valore — piu' scuro verso la punta, con il rumore di un dato vero; senza,
  // e' tutto blu di marca. `rings` sono i punti che l'IA segnala.
  window.trDotMark = function (g, o) {
    const { n = 20, m = 10, t = 10, r = 9.5, seed = 7, levels = null, rings = [] } = o || {};
    const rand = rng(seed);
    markDots(n, m, t).forEach((p) => {
      let cls = 'l500';
      if (levels) {
        const val = 0.08 + 0.8 * (p.x / B[0]) + (rand() - 0.5) * 0.5;
        const k = Math.max(0, Math.min(levels.length - 1, Math.floor(val * levels.length)));
        cls = levels[k];
      }
      if (rings.includes(p.key)) cls = 'ring';
      dot(g, p.x, p.y, r, cls);
    });
  };
})();
