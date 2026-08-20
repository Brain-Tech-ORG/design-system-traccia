/* ==========================================================================
   LA TRACCIA — Select
   Trasforma un <select> nativo nella listbox del design system.

   Il <select> resta nel DOM ed e' lui a tenere il valore: si aggiorna e
   riemette `input` e `change`, quindi form nativi, reactive forms di Angular,
   ngModel e qualunque codice in ascolto continuano a funzionare senza sapere
   nulla di questo file. Se lo script non viene caricato, o fallisce, resta in
   campo il select nativo: e' un miglioramento progressivo, non una
   sostituzione.

   In React NON va usato: la scrittura diretta su .value non attraversa il
   value tracker di React e il componente controllato non se ne accorge. La'
   si scrive un componente che rende le stesse classi e gli stessi attributi
   ARIA — il contratto e' il markup, non questo file.

   Uso:
     TrSelect.enhanceAll();                    // tutti i .tr-select del documento
     TrSelect.enhanceAll(unContenitore);       // solo dentro un sottoalbero
     var istanza = TrSelect.enhance(elemento); // uno solo
     istanza.sync();                           // dopo aver cambiato le <option>
     istanza.destroy();                        // smonta e riscopre il nativo

   Nessun listener globale permanente: quelli sul documento esistono solo
   mentre un pannello e' aperto, e vengono rimossi alla chiusura.
   ========================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.TrSelect = factory(); }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var CHEVRON =
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>';

  var uid = 0;

  function TrSelectInstance(field) {
    this.field = field;
    this.native = field.querySelector('.tr-select__native') || field.querySelector('select');
    if (!this.native) { throw new Error('tr-select: manca il <select> nativo'); }

    this.id = this.native.id || 'tr-select-' + ++uid;
    this.open = false;
    this.activeIndex = -1;
    this.typeahead = '';
    this.typeaheadTimer = null;
    this.optionEls = [];

    this.build();
    this.sync();
    this.bind();
    this.field.classList.add('tr-select--ready');
  }

  TrSelectInstance.prototype.build = function () {
    var f = this.field;
    this.native.classList.add('tr-select__native');
    this.native.setAttribute('tabindex', '-1');
    this.native.setAttribute('aria-hidden', 'true');

    this.trigger = document.createElement('button');
    this.trigger.type = 'button';
    this.trigger.className = 'tr-field__control tr-select__trigger';
    this.trigger.id = this.id + '-trigger';
    this.trigger.setAttribute('role', 'combobox');
    this.trigger.setAttribute('aria-haspopup', 'listbox');
    this.trigger.setAttribute('aria-expanded', 'false');
    this.trigger.setAttribute('aria-controls', this.id + '-listbox');
    if (this.native.disabled) { this.trigger.disabled = true; }

    this.valueEl = document.createElement('span');
    this.valueEl.className = 'tr-select__value';
    this.trigger.appendChild(this.valueEl);

    // L'etichetta del campo comanda il trigger, non piu' il select nascosto.
    var label = f.querySelector('.tr-field__label');
    if (label) {
      label.setAttribute('for', this.trigger.id);
      this.trigger.setAttribute('aria-labelledby', (label.id = label.id || this.id + '-label'));
    }

    var chevron = f.querySelector('.tr-field__suffix');
    if (!chevron) {
      chevron = document.createElement('span');
      chevron.className = 'tr-field__suffix';
      f.appendChild(chevron);
    }
    chevron.classList.add('tr-select__chevron');
    chevron.setAttribute('aria-hidden', 'true');
    if (!chevron.firstElementChild) { chevron.innerHTML = CHEVRON; }

    this.panel = document.createElement('ul');
    this.panel.className = 'tr-select__panel';
    this.panel.id = this.id + '-listbox';
    this.panel.setAttribute('role', 'listbox');
    if (label) { this.panel.setAttribute('aria-labelledby', label.id); }

    this.native.parentNode.insertBefore(this.trigger, this.native.nextSibling);
    f.appendChild(this.panel);
  };

  /** Ricostruisce le voci dalle <option> del select nativo. */
  TrSelectInstance.prototype.sync = function () {
    var self = this;
    this.panel.innerHTML = '';
    this.optionEls = [];

    Array.prototype.forEach.call(this.native.options, function (opt, i) {
      var li = document.createElement('li');
      li.className = 'tr-select__option';
      li.id = self.id + '-opt-' + i;
      li.setAttribute('role', 'option');
      li.setAttribute('data-value', opt.value);
      li.setAttribute('aria-selected', opt.selected ? 'true' : 'false');
      if (opt.disabled) { li.setAttribute('aria-disabled', 'true'); }

      var dot = document.createElement('span');
      dot.className = 'tr-select__dot';
      var text = document.createElement('span');
      text.className = 'tr-select__option-label';
      text.textContent = opt.textContent;

      li.appendChild(dot);
      li.appendChild(text);
      self.panel.appendChild(li);
      self.optionEls.push(li);
    });

    this.renderValue();
  };

  TrSelectInstance.prototype.renderValue = function () {
    var opt = this.native.options[this.native.selectedIndex];
    var placeholder = !opt || opt.disabled || opt.value === '';
    this.valueEl.textContent = opt ? opt.textContent : '';
    this.valueEl.classList.toggle('tr-select__value--placeholder', placeholder);
    var self = this;
    this.optionEls.forEach(function (li, i) {
      li.setAttribute('aria-selected', i === self.native.selectedIndex ? 'true' : 'false');
    });
  };

  TrSelectInstance.prototype.setOpen = function (next) {
    if (next === this.open || this.trigger.disabled) { return; }
    this.open = next;
    this.field.setAttribute('data-open', next ? 'true' : 'false');
    this.trigger.setAttribute('aria-expanded', next ? 'true' : 'false');

    if (next) {
      // Se sotto non c'e' spazio, il pannello si apre verso l'alto.
      var box = this.trigger.getBoundingClientRect();
      var below = window.innerHeight - box.bottom;
      this.field.setAttribute('data-drop', below < 280 && box.top > below ? 'up' : 'down');

      // Se la voce scelta e' un segnaposto disabilitato, si parte dalla prima
      // voce realmente selezionabile.
      var start = this.native.selectedIndex;
      if (start < 0 || (this.native.options[start] && this.native.options[start].disabled)) {
        start = this.firstEnabled();
      }
      this.setActive(start);
      // I listener sul documento vivono solo a pannello aperto.
      document.addEventListener('pointerdown', this.onDocPointer, true);
      window.addEventListener('resize', this.onDismiss, true);
      window.addEventListener('scroll', this.onDismiss, true);
    } else {
      this.setActive(-1);
      document.removeEventListener('pointerdown', this.onDocPointer, true);
      window.removeEventListener('resize', this.onDismiss, true);
      window.removeEventListener('scroll', this.onDismiss, true);
    }
  };

  TrSelectInstance.prototype.firstEnabled = function () {
    for (var i = 0; i < this.native.options.length; i++) {
      if (!this.native.options[i].disabled) { return i; }
    }
    return -1;
  };

  TrSelectInstance.prototype.setActive = function (index) {
    if (this.activeIndex >= 0 && this.optionEls[this.activeIndex]) {
      this.optionEls[this.activeIndex].classList.remove('tr-select__option--active');
    }
    this.activeIndex = index;
    if (index < 0 || !this.optionEls[index]) {
      this.trigger.removeAttribute('aria-activedescendant');
      return;
    }
    var li = this.optionEls[index];
    li.classList.add('tr-select__option--active');
    this.trigger.setAttribute('aria-activedescendant', li.id);
    if (li.scrollIntoView) { li.scrollIntoView({ block: 'nearest' }); }
  };

  TrSelectInstance.prototype.move = function (step) {
    var n = this.native.options.length;
    if (!n) { return; }
    var i = this.activeIndex;
    for (var k = 0; k < n; k++) {
      i = (i + step + n) % n;
      if (!this.native.options[i].disabled) { this.setActive(i); return; }
    }
  };

  TrSelectInstance.prototype.commit = function (index) {
    if (index < 0 || !this.native.options[index] || this.native.options[index].disabled) { return; }
    if (this.native.selectedIndex !== index) {
      this.native.selectedIndex = index;
      // Riemesso sul nativo: chi ascolta il select non deve cambiare nulla.
      this.native.dispatchEvent(new Event('input', { bubbles: true }));
      this.native.dispatchEvent(new Event('change', { bubbles: true }));
    }
    this.renderValue();
    this.setOpen(false);
    this.trigger.focus();
  };

  /** Digitando lettere si salta alla voce che inizia cosi', come nel nativo. */
  TrSelectInstance.prototype.search = function (char) {
    var self = this;
    clearTimeout(this.typeaheadTimer);
    this.typeahead += char.toLowerCase();
    this.typeaheadTimer = setTimeout(function () { self.typeahead = ''; }, 600);

    var n = this.native.options.length;
    var start = this.activeIndex < 0 ? 0 : this.activeIndex;
    for (var k = 1; k <= n; k++) {
      var i = (start + k) % n;
      var opt = this.native.options[i];
      if (opt.disabled) { continue; }
      if (opt.textContent.trim().toLowerCase().indexOf(this.typeahead) === 0) {
        this.setActive(i);
        if (!this.open) { this.commit(i); }
        return;
      }
    }
  };

  TrSelectInstance.prototype.bind = function () {
    var self = this;

    this.onDocPointer = function (e) {
      if (!self.field.contains(e.target)) { self.setOpen(false); }
    };
    this.onDismiss = function (e) {
      // Lo scroll dentro il pannello non lo chiude.
      if (e.type === 'scroll' && self.panel.contains(e.target)) { return; }
      self.setOpen(false);
    };

    this.onTriggerClick = function () { self.setOpen(!self.open); };
    this.trigger.addEventListener('click', this.onTriggerClick);

    this.onTriggerBlur = function (e) {
      if (!self.field.contains(e.relatedTarget)) { self.setOpen(false); }
    };
    this.trigger.addEventListener('blur', this.onTriggerBlur);

    this.onKeyDown = function (e) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (!self.open) { self.setOpen(true); } else { self.move(1); }
          break;
        case 'ArrowUp':
          e.preventDefault();
          if (!self.open) { self.setOpen(true); } else { self.move(-1); }
          break;
        case 'Home':
          if (self.open) { e.preventDefault(); self.setActive(self.firstEnabled()); }
          break;
        case 'End':
          if (self.open) {
            e.preventDefault();
            for (var i = self.native.options.length - 1; i >= 0; i--) {
              if (!self.native.options[i].disabled) { self.setActive(i); break; }
            }
          }
          break;
        case 'Enter':
        case ' ':
          e.preventDefault();
          if (self.open) { self.commit(self.activeIndex); } else { self.setOpen(true); }
          break;
        case 'Escape':
          if (self.open) { e.preventDefault(); self.setOpen(false); }
          break;
        case 'Tab':
          self.setOpen(false);
          break;
        default:
          if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) { self.search(e.key); }
      }
    };
    this.trigger.addEventListener('keydown', this.onKeyDown);

    // Un solo listener sul pannello invece di uno per voce.
    this.onPanelClick = function (e) {
      var li = e.target.closest ? e.target.closest('.tr-select__option') : null;
      if (!li || li.getAttribute('aria-disabled') === 'true') { return; }
      self.commit(self.optionEls.indexOf(li));
    };
    this.panel.addEventListener('click', this.onPanelClick);

    this.onPanelMove = function (e) {
      var li = e.target.closest ? e.target.closest('.tr-select__option') : null;
      if (li && li.getAttribute('aria-disabled') !== 'true') {
        self.setActive(self.optionEls.indexOf(li));
      }
    };
    this.panel.addEventListener('pointermove', this.onPanelMove);

    // Se il valore cambia da fuori (framework, reset del form), il trigger segue.
    this.onNativeChange = function () { self.renderValue(); };
    this.native.addEventListener('change', this.onNativeChange);
  };

  TrSelectInstance.prototype.destroy = function () {
    this.setOpen(false);
    this.trigger.removeEventListener('click', this.onTriggerClick);
    this.trigger.removeEventListener('blur', this.onTriggerBlur);
    this.trigger.removeEventListener('keydown', this.onKeyDown);
    this.panel.removeEventListener('click', this.onPanelClick);
    this.panel.removeEventListener('pointermove', this.onPanelMove);
    this.native.removeEventListener('change', this.onNativeChange);
    clearTimeout(this.typeaheadTimer);

    this.trigger.parentNode.removeChild(this.trigger);
    this.panel.parentNode.removeChild(this.panel);
    this.native.removeAttribute('tabindex');
    this.native.removeAttribute('aria-hidden');
    this.field.classList.remove('tr-select--ready');
    this.field.removeAttribute('data-open');
    this.field.removeAttribute('data-drop');
    delete this.field.trSelect;
  };

  return {
    enhance: function (field) {
      if (field.trSelect) { return field.trSelect; }
      field.trSelect = new TrSelectInstance(field);
      return field.trSelect;
    },
    enhanceAll: function (scope) {
      var root = scope || document;
      var out = [];
      Array.prototype.forEach.call(root.querySelectorAll('.tr-select'), function (f) {
        try { out.push(f.trSelect || (f.trSelect = new TrSelectInstance(f))); }
        catch (err) { /* il select nativo resta funzionante */ }
      });
      return out;
    },
  };
});
