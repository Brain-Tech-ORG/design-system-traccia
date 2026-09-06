/* ==========================================================================
   LA TRACCIA — Parallasse dell'hero
   Muove l'immagine dell'hero piu' lenta della pagina, e fa scorrere e sfumare
   il testo che le sta sopra. E' l'unico movimento di pagina che il sistema
   ammette: un elemento solo, l'immagine, mai il testo corrente ne' le tabelle.

   Il markup e' dichiarativo:
     <section class="tr-hero" data-tr-parallax="hero">
       <div class="tr-hero__bg" data-tr-parallax="bg" style="background-image:url(...)"></div>
       <div class="tr-hero__overlay"></div>
       <div class="tr-hero__content" data-tr-parallax="content">…</div>
     </section>

   I fattori non stanno qui: li legge da CSS (--tr-parallax-bg e
   --tr-parallax-content in tokens.css) con getComputedStyle, cosi' si tarano
   nel posto in cui stanno le altre misure del sistema.

   Regole di condotta:
   - aggiorna in requestAnimationFrame, un frame per volta, con listener
     passivi: lo scorrimento non aspetta mai questo codice;
   - calcola solo finche' l'hero e' in vista — fuori dalla vista il listener
     non e' nemmeno registrato;
   - prefers-reduced-motion: reduce spegne tutto: il listener non si registra,
     e se la preferenza cambia a pagina aperta si rimuove e l'hero torna fermo.
     Il CSS fa la stessa promessa con transform: none !important.

   Uso:
     TrParallax.enhanceAll();                 // tutti gli hero del documento
     TrParallax.enhanceAll(unContenitore);    // solo dentro un sottoalbero
     var istanza = TrParallax.enhance(hero);  // uno solo
     istanza.destroy();                       // ferma e ripulisce gli stili
   ========================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.TrParallax = factory(); }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* Il testo sfuma un po' piu' in fretta di quanto scorra: a meta' corsa e'
     gia' quasi sparito, e non resta mai una riga mezza leggibile sopra il
     pannello che sale. */
  var FADE_RATE = 1.15;

  /* Fattori di riserva se il token manca o non e' un numero: gli stessi che
     stanno in tokens.css, qui solo come rete. */
  var DEFAULT_BG = 0.4;
  var DEFAULT_CONTENT = 0.25;

  function readFactor(el, name, fallback) {
    var v = parseFloat(getComputedStyle(el).getPropertyValue(name));
    return isNaN(v) ? fallback : v;
  }

  function TrParallaxInstance(hero) {
    this.hero = hero;
    this.bg = hero.querySelector('[data-tr-parallax="bg"]');
    this.content = hero.querySelector('[data-tr-parallax="content"]');
    if (!this.bg || !this.content) { throw new Error('tr-parallax: mancano bg o content'); }

    this.factorBg = readFactor(hero, '--tr-parallax-bg', DEFAULT_BG);
    this.factorContent = readFactor(hero, '--tr-parallax-content', DEFAULT_CONTENT);
    this.reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
    this.ticking = false;
    this.listening = false;
    this.inView = true;

    this.onScroll = this.onScroll.bind(this);
    this.onPreference = this.onPreference.bind(this);
    this.apply = this.apply.bind(this);

    this.observe();
    if (this.reduce.addEventListener) { this.reduce.addEventListener('change', this.onPreference); }
    else if (this.reduce.addListener) { this.reduce.addListener(this.onPreference); }
    this.start();
  }

  /* Il conto si fa solo mentre l'hero e' in vista. Senza IntersectionObserver
     resta il controllo dentro apply(), che costa comunque poco. */
  TrParallaxInstance.prototype.observe = function () {
    if (!('IntersectionObserver' in window)) { return; }
    var self = this;
    this.observer = new IntersectionObserver(function (entries) {
      self.inView = entries[0].isIntersecting;
      self.start();
    });
    this.observer.observe(this.hero);
  };

  TrParallaxInstance.prototype.start = function () {
    var wants = !this.reduce.matches && this.inView;
    if (wants && !this.listening) {
      window.addEventListener('scroll', this.onScroll, { passive: true });
      window.addEventListener('resize', this.onScroll, { passive: true });
      this.listening = true;
      this.apply();
    } else if (!wants && this.listening) {
      window.removeEventListener('scroll', this.onScroll);
      window.removeEventListener('resize', this.onScroll);
      this.listening = false;
      if (this.reduce.matches) { this.reset(); }
    }
  };

  TrParallaxInstance.prototype.onPreference = function () { this.start(); };

  TrParallaxInstance.prototype.onScroll = function () {
    if (this.ticking) { return; }
    this.ticking = true;
    window.requestAnimationFrame(this.apply);
  };

  /* La corsa parte quando il bordo superiore dell'hero passa il bordo
     superiore della finestra, e finisce quando l'hero e' uscito: prima di
     allora tutto e' fermo, che e' anche il caso dell'hero in testa alla pagina
     appena aperta. Lo sbordo dello sfondo (--tr-parallax-bleed) e' tarato su
     questa corsa: finche' l'hero e' in vista il bordo della foto non si scopre. */
  TrParallaxInstance.prototype.apply = function () {
    this.ticking = false;
    var rect = this.hero.getBoundingClientRect();
    var h = rect.height || 1;
    if (rect.bottom <= 0) { return; }
    var y = Math.max(0, -rect.top);
    var t = Math.min(1, y / h);
    var fade = 1 - t * FADE_RATE;
    this.bg.style.transform = 'translate3d(0,' + (y * this.factorBg).toFixed(1) + 'px,0)';
    this.content.style.transform = 'translate3d(0,' + (y * this.factorContent).toFixed(1) + 'px,0)';
    this.content.style.opacity = fade < 0 ? '0' : fade.toFixed(3);
  };

  TrParallaxInstance.prototype.reset = function () {
    this.bg.style.transform = '';
    this.content.style.transform = '';
    this.content.style.opacity = '';
  };

  TrParallaxInstance.prototype.destroy = function () {
    this.inView = false;
    this.start();
    this.reset();
    if (this.observer) { this.observer.disconnect(); }
    if (this.reduce.removeEventListener) { this.reduce.removeEventListener('change', this.onPreference); }
    else if (this.reduce.removeListener) { this.reduce.removeListener(this.onPreference); }
    delete this.hero.trParallax;
  };

  return {
    enhance: function (hero) {
      if (hero.trParallax) { return hero.trParallax; }
      hero.trParallax = new TrParallaxInstance(hero);
      return hero.trParallax;
    },
    enhanceAll: function (scope) {
      var root = scope || document;
      var out = [];
      Array.prototype.forEach.call(root.querySelectorAll('[data-tr-parallax="hero"]'), function (hero) {
        try { out.push(hero.trParallax || (hero.trParallax = new TrParallaxInstance(hero))); }
        catch (err) { /* l'hero resta fermo, che e' uno stato lecito */ }
      });
      return out;
    },
  };
});
