// Calculateurs d'actions-benefices.com : tout est calculé dans le navigateur, rien n'est envoyé.
(function () {
  // Barème 2026 : prélèvements sociaux 18,6 % ; PFU 31,4 % (12,8 % d'impôt + 18,6 %)
  var PS = 0.186, PFU = 0.314;
  function val(id) { var v = parseFloat(String(document.getElementById(id).value).replace(',', '.')); return isNaN(v) || v < 0 ? 0 : v; }
  function eur(x) { return Math.round(x).toLocaleString('fr-FR') + ' €'; }
  function ecrire(id, t) { document.getElementById(id).textContent = t; }

  // 1. Intérêts composés, capitalisation mensuelle
  function composes() {
    var c = val('c-init'), m = val('c-mois'), t = val('c-taux') / 100, n = Math.round(val('c-ans') * 12);
    var rm = Math.pow(1 + t, 1 / 12) - 1;
    for (var i = 0; i < n; i++) c = c * (1 + rm) + m;
    var verse = val('c-init') + m * n;
    ecrire('c-res', eur(c));
    ecrire('c-det', 'Dont ' + eur(verse) + ' versés et ' + eur(c - verse) + ' d’intérêts.');
  }
  // 2. Vivre de ses dividendes : capital = revenu annuel net / (rendement × (1 − impôt))
  function dividendes() {
    var rev = val('d-rev') * 12, r = val('d-rdt') / 100, imp = document.getElementById('d-env').value === 'pea' ? PS : PFU;
    if (r === 0) { ecrire('d-res', '–'); ecrire('d-det', 'Indique un rendement supérieur à 0.'); return; }
    var cap = rev / (r * (1 - imp));
    ecrire('d-res', eur(cap));
    ecrire('d-det', 'Pour ' + eur(rev / (1 - imp)) + ' de dividendes bruts par an, dont ' + eur(rev / (1 - imp) - rev) + ' d’impôts.'
      + (imp === PS && cap > 150000 ? ' Attention : au-delà de 150 000 € de versements, il faut un autre compte que le PEA (ou des gains déjà faits dedans).' : ''));
  }
  // 3. PEA ou CTO sur une plus-value
  function peacto() {
    var g = val('p-gain');
    ecrire('p-pea', eur(g * PS)); ecrire('p-cto', eur(g * PFU));
    ecrire('p-det', 'Écart : ' + eur(g * (PFU - PS)) + ' de plus pour l’État sur un compte-titres.');
  }
  var calc = { c: composes, d: dividendes, p: peacto };
  document.querySelectorAll('input, select').forEach(function (el) {
    var f = calc[el.id.charAt(0)];
    if (f && el.id.charAt(1) === '-') { el.addEventListener('input', f); el.addEventListener('change', f); }
  });
  composes(); dividendes(); peacto();
})();
