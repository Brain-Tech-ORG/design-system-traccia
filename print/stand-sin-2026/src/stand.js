// Porta ogni lockup con data-fit-w="<mm>" esattamente a quella larghezza,
// scalando --mark-h in proporzione. Va chiamato a font caricati: lo fa
// build.mjs dopo document.fonts.ready.
window.trFit = function trFit() {
  const PX_PER_MM = 96 / 25.4;
  document.querySelectorAll('[data-fit-w]').forEach((el) => {
    const target = parseFloat(el.dataset.fitW) * PX_PER_MM;
    const current = parseFloat(getComputedStyle(el).getPropertyValue('--mark-h')) || 20;
    el.style.setProperty('--mark-h', `${current}mm`);
    const width = el.getBoundingClientRect().width;
    if (width > 0) el.style.setProperty('--mark-h', `${(current * target / width).toFixed(3)}mm`);
  });
};
