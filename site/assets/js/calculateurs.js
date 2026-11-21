// Calculateurs d'actionsbenefices.com : tout est calculé dans le navigateur, rien n'est envoyé.
(function () {
  // Fiscalité 2026 : prélèvements sociaux 18,6 % ; PFU 31,4 % (12,8 % d'impôt + 18,6 %)
  var PS = 0.186, IR_PFU = 0.128, PFU = IR_PFU + PS, RETENUE_US = 0.15;
  function $(id) { return document.getElementById(id); }
  function val(id) { var v = parseFloat(String($(id).value).replace(',', '.')); return isNaN(v) || v < 0 ? 0 : v; }
  function eur(x) { return Math.round(x).toLocaleString('fr-FR') + ' €'; }
  function court(x) { return x >= 1e6 ? (x / 1e6).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' M€' : x >= 1e3 ? Math.round(x / 1e3).toLocaleString('fr-FR') + ' k€' : Math.round(x) + ' €'; }
  function ecrire(id, t) { var e = $(id); if (e) e.textContent = t; }
  var NS = 'http://www.w3.org/2000/svg';
  function svgEl(tag, attrs, txt) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (txt != null) e.textContent = txt; return e; }

  // 1. Intérêts composés, capitalisation mensuelle, avec courbe année par année
  function composes() {
    var c0 = val('c-init'), m = val('c-mois'), t = val('c-taux') / 100, ans = Math.min(60, Math.round(val('c-ans')));
    var rm = Math.pow(1 + t, 1 / 12) - 1, c = c0, pts = [{ a: 0, cap: c0, verse: c0 }], bascule = null;
    for (var a = 1; a <= ans; a++) {
      for (var i = 0; i < 12; i++) c = c * (1 + rm) + m;
      var v = c0 + m * 12 * a; pts.push({ a: a, cap: c, verse: v });
      if (bascule === null && c - v > v) bascule = a;
    }
    var fin = pts[pts.length - 1];
    ecrire('c-res', eur(fin.cap));
    ecrire('c-det', 'Dont ' + eur(fin.verse) + ' versés et ' + eur(fin.cap - fin.verse) + ' d’intérêts'
      + (fin.cap > 0 ? ' (' + Math.round(100 * (fin.cap - fin.verse) / fin.cap) + ' % du capital).' : '.')
      + (bascule ? ' À partir de l’année ' + bascule + ', les intérêts accumulés dépassent tout ce que tu as versé : c’est la force des intérêts composés.' : ''));
    courbe(pts);
  }
  function courbe(pts) {
    var box = $('c-graph'); if (!box) return;
    var W = 1000, H = 380, x0 = 70, x1 = W - 20, y0 = H - 40, y1 = 20, n = pts.length - 1 || 1;
    var max = Math.max.apply(null, pts.map(function (p) { return p.cap; })) || 1;
    // graduation « ronde »
    var pas = Math.pow(10, Math.floor(Math.log10(max / 4))), k = [1, 2, 2.5, 5, 10].find(function (f) { return max / (pas * f) <= 5; }) || 10; pas *= k;
    var top = Math.ceil(max / pas) * pas;
    function X(a) { return x0 + (x1 - x0) * a / n; } function Y(v) { return y0 - (y0 - y1) * v / top; }
    var s = svgEl('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img', 'aria-label': 'Évolution du capital et des versements cumulés, année par année' });
    for (var g = 0; g <= top + 1; g += pas) {
      s.appendChild(svgEl('line', { x1: x0, x2: x1, y1: Y(g), y2: Y(g), stroke: '#E2DFD8' }));
      s.appendChild(svgEl('text', { x: x0 - 8, y: Y(g) + 4, 'text-anchor': 'end', 'font-size': 12, fill: '#5F5F66' }, court(g)));
    }
    var pasA = n <= 12 ? 1 : n <= 30 ? 5 : 10;
    for (var a = 0; a <= n; a += pasA) s.appendChild(svgEl('text', { x: X(a), y: y0 + 22, 'text-anchor': 'middle', 'font-size': 12, fill: '#5F5F66' }, a === 0 ? 'départ' : a + ' an' + (a > 1 ? 's' : '')));
    function chemin(cle) { return pts.map(function (p, i) { return (i ? 'L' : 'M') + X(p.a).toFixed(1) + ',' + Y(p[cle]).toFixed(1); }).join(' '); }
    s.appendChild(svgEl('path', { d: chemin('cap') + ' L' + X(n) + ',' + y0 + ' L' + x0 + ',' + y0 + ' Z', fill: '#2E8C38', opacity: .16 }));
    s.appendChild(svgEl('path', { d: chemin('verse') + ' L' + X(n) + ',' + y0 + ' L' + x0 + ',' + y0 + ' Z', fill: '#17375E', opacity: .12 }));
    s.appendChild(svgEl('path', { d: chemin('verse'), fill: 'none', stroke: '#17375E', 'stroke-width': 3, 'stroke-dasharray': '7 6' }));
    s.appendChild(svgEl('path', { d: chemin('cap'), fill: 'none', stroke: '#2E8C38', 'stroke-width': 4, 'stroke-linejoin': 'round' }));
    // zones de survol, une par année
    pts.forEach(function (p) {
      var g = svgEl('g', { class: 'c-an', tabindex: 0, 'data-tip': (p.a === 0 ? 'Au départ' : 'Après ' + p.a + ' an' + (p.a > 1 ? 's' : '')) + '\n' + eur(p.cap) + '\nVersé : ' + eur(p.verse) + '\nIntérêts : ' + eur(p.cap - p.verse) });
      var w = (x1 - x0) / n;
      g.appendChild(svgEl('rect', { class: 'zone', x: X(p.a) - w / 2, y: y1, width: w, height: y0 - y1 }));
      g.appendChild(svgEl('line', { class: 'guide', x1: X(p.a), x2: X(p.a), y1: y1, y2: y0, stroke: '#B8860B', 'stroke-width': 1.5 }));
      g.appendChild(svgEl('circle', { class: 'guide', cx: X(p.a), cy: Y(p.cap), r: 6, fill: '#fff', stroke: '#2E8C38', 'stroke-width': 3 }));
      s.appendChild(g);
    });
    box.textContent = ''; box.appendChild(s);
  }

  // 2. Vivre de ses dividendes : capital = revenu annuel net / (rendement × (1 − impôt))
  function dividendes() {
    var rev = val('d-rev') * 12, r = val('d-rdt') / 100, imp = $('d-env').value === 'pea' ? PS : PFU;
    if (r === 0) { ecrire('d-res', '–'); ecrire('d-det', 'Indique un rendement supérieur à 0.'); return; }
    var cap = rev / (r * (1 - imp));
    ecrire('d-res', eur(cap));
    ecrire('d-det', 'Pour ' + eur(rev / (1 - imp)) + ' de dividendes bruts par an, dont ' + eur(rev / (1 - imp) - rev) + ' d’impôts.'
      + (imp === PS && cap > 150000 ? ' Attention : au-delà de 150 000 € de versements, il faut un autre compte que le PEA (ou des gains déjà faits dedans).' : ''));
  }

  // 3. PEA ou CTO : plus-value ou dividende, actions européennes ou américaines, durée de détention, flat tax ou barème
  function peacto() {
    var g = val('p-gain'), nature = $('p-nature').value, us = $('p-origine').value === 'us', duree = $('p-duree').value,
        avant2018 = $('p-2018').checked, tmi = +$('p-tmi').value / 100, div = nature === 'div';
    $('p-ligne-2018').hidden = div;
    var lignes = [];
    // --- PEA ---
    var pea, peaTxt;
    if (us) { pea = null; peaTxt = 'Les actions américaines ne sont pas éligibles au PEA.'; }
    else if (duree === 'm2' || duree === '2-5') { pea = g * PFU; peaTxt = 'Plan de moins de 5 ans : le gain retiré est taxé à la flat tax de 31,4 %, et le retrait clôture en principe le plan.'; }
    else { pea = g * PS; peaTxt = 'Plan de plus de 5 ans : pas d’impôt sur le revenu, seulement 18,6 % de prélèvements sociaux, au moment du retrait.'; }
    if (div && !us) peaTxt += ' Les dividendes restent dans le plan sans impôt tant que tu ne retires rien.';
    // --- CTO : flat tax ---
    var ctoPfu, ctoBar, abat = 0, retenue = us && div ? g * RETENUE_US : 0;
    if (div) {
      // dividende : impôt français moins le crédit d'impôt égal à la retenue américaine (simplifié : il efface au plus l'impôt français)
      ctoPfu = retenue + Math.max(0, g * IR_PFU - retenue) + g * PS;
      ctoBar = retenue + Math.max(0, g * 0.6 * tmi - retenue) + g * PS;     // barème : abattement de 40 % sur les dividendes
    } else {
      ctoPfu = g * PFU;
      if (avant2018) abat = duree === '8p' ? 0.65 : duree === 'm2' ? 0 : 0.5;
      ctoBar = g * (1 - abat) * tmi + g * PS;
    }
    var mieux = ctoBar < ctoPfu - 0.5 ? 'bar' : 'pfu', cto = Math.min(ctoPfu, ctoBar);
    ecrire('p-pea', pea === null ? 'Non éligible' : eur(pea)); ecrire('p-pea-net', pea === null ? '' : 'Il te reste ' + eur(g - pea));
    ecrire('p-cto', eur(cto)); ecrire('p-cto-net', 'Il te reste ' + eur(g - cto));
    ecrire('p-pea-txt', peaTxt);
    ecrire('p-cto-pfu', eur(ctoPfu)); ecrire('p-cto-bar', eur(ctoBar));
    $('p-ch-pfu').classList.toggle('meilleur', mieux === 'pfu'); $('p-ch-bar').classList.toggle('meilleur', mieux === 'bar');
    var d = [];
    if (us && div) d.push('Dividende américain : ' + eur(retenue) + ' retenus aux États-Unis (15 %, formulaire W-8BEN), compensés en France par un crédit d’impôt.');
    if (div) d.push('Au barème, le dividende n’est imposé que sur 60 % de son montant (abattement de 40 %).');
    else if (avant2018 && abat) d.push('Titres achetés avant 2018 et détenus ' + (abat === 0.65 ? 'plus de 8 ans' : 'de 2 à 8 ans') + ' : au barème, abattement de ' + Math.round(abat * 100) + ' % sur la plus-value pour l’impôt sur le revenu (pas sur les prélèvements sociaux).');
    else if (!div && !avant2018) d.push('Titres achetés depuis 2018 : pas d’abattement pour durée de détention, même au barème.');
    d.push(mieux === 'bar' ? 'Avec ta tranche à ' + Math.round(tmi * 100) + ' %, le barème est plus avantageux que la flat tax.' : 'Avec ta tranche à ' + Math.round(tmi * 100) + ' %, la flat tax reste la meilleure option.');
    if (pea !== null) d.push('Écart PEA / compte-titres : ' + eur(Math.abs(cto - pea)) + (cto > pea ? ' de plus pour l’État sur le compte-titres.' : ' de plus pour l’État sur le PEA.'));
    ecrire('p-det', d.join(' '));
  }

  var calc = { c: composes, d: dividendes, p: peacto };
  document.querySelectorAll('input, select').forEach(function (el) {
    var f = calc[el.id.charAt(0)];
    if (f && el.id.charAt(1) === '-') { el.addEventListener('input', f); el.addEventListener('change', f); }
  });
  composes(); dividendes(); peacto();
})();
