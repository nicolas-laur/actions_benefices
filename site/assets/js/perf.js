/* Performances historiques comparées (base 100), données assets/data/marches.json (Yahoo Finance, relevé chaque nuit).
   Choix des séries (5 au plus), de la période, infobulle qui suit la souris ou le doigt. Aucune dépendance. */
(function () {
  var box = document.getElementById('perf'); if (!box) return;
  var NS = 'http://www.w3.org/2000/svg', COUL = ['#FFC24A', '#35D6FF', '#3FE08A', '#FF4D5E', '#C08BFF'];
  var D, choix = ['sp500', 'aapl'], periode = '10';
  function el(t, a, x) { var e = document.createElementNS(NS, t); for (var k in a) e.setAttribute(k, a[k]); if (x != null) e.textContent = x; return e; }
  function pct(x, d) { return (x >= 0 ? '+' : '−') + Math.abs(x).toLocaleString('fr-FR', { maximumFractionDigits: d == null ? 1 : d }) + ' %'; }
  function date(s) { var p = s.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function an(s) { return s.slice(0, 4); }

  fetch(box.dataset.src).then(function (r) { return r.json(); }).then(function (d) { D = d; menu(); trace(); })
    .catch(function () { box.querySelector('.perf-graph').textContent = 'Données momentanément indisponibles.'; });

  function menu() {
    // familles (Indices, Actions américaines…) puis secteurs : groupe « Famille|Secteur » dans marches.json
    var m = box.querySelector('.perf-choix'), familles = {}, ordre = [];
    Object.keys(D.series).forEach(function (k) {
      var s = D.series[k]; if (k === 'eurusd') return;
      var p = s.groupe.split('|'), f = p[0], sec = p[1] || '';
      if (!familles[f]) { familles[f] = {}; ordre.push(f); }
      (familles[f][sec] = familles[f][sec] || []).push(k);
    });
    function puce(k) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'bouton clair puce'; b.dataset.k = k; b.textContent = D.series[k].nom;
      b.addEventListener('click', function () {
        var i = choix.indexOf(k);
        if (i >= 0) { if (choix.length > 1) choix.splice(i, 1); }
        else { if (choix.length >= 5) choix.shift(); choix.push(k); }
        trace();
      });
      return b;
    }
    ordre.forEach(function (f) {
      var secs = familles[f], n = 0; Object.keys(secs).forEach(function (x) { n += secs[x].length; });
      var bloc = document.createElement('details'); bloc.className = 'perf-groupe';
      if (f === 'Indices' || Object.keys(secs).some(function (x) { return secs[x].some(function (k) { return choix.indexOf(k) >= 0; }); })) bloc.open = true;
      var t = document.createElement('summary'); t.innerHTML = '<span class="surtitre"></span><span class="gris petit"></span>';
      t.firstChild.textContent = f; t.lastChild.textContent = n + ' au choix'; bloc.appendChild(t);
      Object.keys(secs).forEach(function (x) {
        var ligne = document.createElement('div'); ligne.className = 'perf-secteur';
        if (x) { var lab = document.createElement('span'); lab.className = 'perf-sec-nom'; lab.textContent = x; ligne.appendChild(lab); }
        var l = document.createElement('div'); l.className = 'pastilles'; secs[x].forEach(function (k) { l.appendChild(puce(k)); });
        ligne.appendChild(l); bloc.appendChild(ligne);
      });
      m.appendChild(bloc);
    });
    box.querySelectorAll('[data-periode]').forEach(function (b) {
      b.addEventListener('click', function () { periode = b.dataset.periode; trace(); });
    });
  }

  function trace() {
    box.querySelectorAll('.puce').forEach(function (b) {
      var i = choix.indexOf(b.dataset.k); b.classList.toggle('actif', i >= 0); b.style.setProperty('--c', i >= 0 ? COUL[i] : '');
    });
    box.querySelectorAll('[data-periode]').forEach(function (b) { b.classList.toggle('actif', b.dataset.periode === periode); });
    var dates = D.dates, n = dates.length, fin = n - 1;
    // début : période demandée, mais pas avant la première cotation commune aux séries choisies
    var debutCommun = 0;
    choix.forEach(function (k) { var v = D.series[k].v, i = 0; while (i < n && v[i] == null) i++; debutCommun = Math.max(debutCommun, i); });
    var i0 = debutCommun;
    if (periode !== 'max') {
      var cible = new Date(dates[fin]); cible.setFullYear(cible.getFullYear() - (+periode)); var c = cible.toISOString().slice(0, 10);
      var j = 0; while (j < n && dates[j] < c) j++; i0 = Math.max(i0, j);
    }
    var tronque = periode !== 'max' && i0 === debutCommun && debutCommun > 0;
    var S = choix.map(function (k, ci) {
      var v = D.series[k].v, base = v[i0], pts = [];
      for (var i = i0; i <= fin; i++) pts.push(v[i] == null ? null : 100 * v[i] / base);
      return { k: k, nom: D.series[k].nom, dev: D.series[k].devise, c: COUL[ci], p: pts };
    });
    var lo = Infinity, hi = -Infinity;
    S.forEach(function (s) { s.p.forEach(function (x) { if (x != null) { lo = Math.min(lo, x); hi = Math.max(hi, x); } }); });
    var log = hi / lo > 12;                                   // échelle logarithmique quand les écarts deviennent énormes
    var W = 1000, H = 420, x0 = 64, x1 = W - 16, y0 = H - 36, y1 = 16, m = S[0].p.length - 1 || 1;
    function f(x) { return log ? Math.log(x) : x; }
    var a = f(lo * (log ? .9 : 1) - (log ? 0 : (hi - lo) * .05)), b = f(hi * (log ? 1.1 : 1) + (log ? 0 : (hi - lo) * .05));
    function X(i) { return x0 + (x1 - x0) * i / m; } function Y(x) { return y0 - (y0 - y1) * (f(x) - a) / (b - a); }
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img', 'aria-label': 'Performances comparées, base 100 au ' + date(dates[i0]) });
    // graduations
    var ticks = [];
    if (log) { [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000].forEach(function (t) { if (t >= lo * .9 && t <= hi * 1.1) ticks.push(t); }); }
    else { var pas = Math.pow(10, Math.floor(Math.log10((hi - lo) / 4))); var k2 = [1, 2, 2.5, 5, 10].find(function (q) { return (hi - lo) / (pas * q) <= 5; }) || 10; pas *= k2;
      for (var t = Math.ceil(lo / pas) * pas; t <= hi; t += pas) ticks.push(t); }
    ticks.forEach(function (t) {
      svg.appendChild(el('line', { x1: x0, x2: x1, y1: Y(t), y2: Y(t), stroke: t === 100 ? 'rgba(255,255,255,.35)' : 'rgba(255,255,255,.1)', 'stroke-dasharray': t === 100 ? '4 4' : '' }));
      svg.appendChild(el('text', { x: x0 - 8, y: Y(t) + 4, 'text-anchor': 'end', 'font-size': 12, fill: '#9AA6B8' }, Math.round(t).toLocaleString('fr-FR')));
    });
    var nbA = 6; for (var q = 0; q <= nbA; q++) { var ii = Math.round(m * q / nbA); svg.appendChild(el('text', { x: X(ii), y: y0 + 22, 'text-anchor': q === 0 ? 'start' : q === nbA ? 'end' : 'middle', 'font-size': 12, fill: '#9AA6B8' }, an(dates[i0 + ii]))); }
    S.forEach(function (s) {
      var d = '', debut = true;
      s.p.forEach(function (x, i) { if (x == null) { debut = true; return; } d += (debut ? 'M' : 'L') + X(i).toFixed(1) + ',' + Y(x).toFixed(1); debut = false; });
      svg.appendChild(el('path', { d: d, fill: 'none', stroke: s.c, 'stroke-width': 2.6, 'stroke-linejoin': 'round' }));
    });
    var guide = el('line', { y1: y1, y2: y0, stroke: '#FFC24A', 'stroke-width': 1.5, opacity: 0 }); svg.appendChild(guide);
    var pts = S.map(function (s) { var c = el('circle', { r: 5, fill: '#0E131D', stroke: s.c, 'stroke-width': 3, opacity: 0 }); svg.appendChild(c); return c; });
    var zone = el('rect', { x: x0, y: y1, width: x1 - x0, height: y0 - y1, fill: 'transparent', tabindex: 0 }); svg.appendChild(zone);
    var g = box.querySelector('.perf-graph'); g.textContent = ''; g.appendChild(svg);
    var bulle = box.querySelector('.perf-bulle');
    function montre(i, cx, cy) {
      i = Math.max(0, Math.min(m, i)); guide.setAttribute('x1', X(i)); guide.setAttribute('x2', X(i)); guide.setAttribute('opacity', 1);
      var lignes = ['<strong>' + date(dates[i0 + i]) + '</strong>'];
      S.forEach(function (s, k) {
        var x = s.p[i]; pts[k].setAttribute('opacity', x == null ? 0 : 1);
        if (x != null) { pts[k].setAttribute('cx', X(i)); pts[k].setAttribute('cy', Y(x)); }
        lignes.push('<span><i style="background:' + s.c + '"></i>' + s.nom + ' : <b>' + (x == null ? '–' : pct(x - 100)) + '</b></span>');
      });
      bulle.innerHTML = lignes.join(''); bulle.hidden = false;
      var r = g.getBoundingClientRect(), px = r.left + r.width * X(i) / W;
      bulle.style.left = Math.min(Math.max(px - r.left + 14, 0), r.width - bulle.offsetWidth) + 'px';
      if (px - r.left + 14 + bulle.offsetWidth > r.width) bulle.style.left = Math.max(0, px - r.left - 14 - bulle.offsetWidth) + 'px';
    }
    function pos(e) { var r = svg.getBoundingClientRect(); return Math.round(((e.clientX - r.left) * W / r.width - x0) / (x1 - x0) * m); }
    zone.addEventListener('pointermove', function (e) { montre(pos(e)); });
    zone.addEventListener('pointerdown', function (e) { montre(pos(e)); });
    zone.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'touch') { bulle.hidden = true; guide.setAttribute('opacity', 0); pts.forEach(function (p) { p.setAttribute('opacity', 0); }); } });
    var ik = m; zone.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') ik = Math.max(0, ik - 4); else if (e.key === 'ArrowRight') ik = Math.min(m, ik + 4); else return; e.preventDefault(); montre(ik); });
    // résultats : performance totale et par an
    var ans = (new Date(dates[fin]) - new Date(dates[i0])) / 3.15576e10;
    box.querySelector('.perf-res').innerHTML = S.map(function (s) {
      var x = null; for (var i = s.p.length - 1; i >= 0; i--) if (s.p[i] != null) { x = s.p[i]; break; }
      var par = ans >= 1 ? Math.pow(x / 100, 1 / ans) * 100 - 100 : null;
      return '<div class="perf-carte" style="--c:' + s.c + '"><span>' + s.nom + '</span><b>' + pct(x - 100, 0) + '</b>'
        + '<small>' + (par == null ? '' : pct(par) + ' par an · ') + '1 000 ' + (s.dev === 'USD' ? '$' : s.dev === 'EUR' ? '€' : s.dev) + ' → ' + Math.round(10 * x).toLocaleString('fr-FR') + '</small></div>';
    }).join('');
    box.querySelector('.perf-note').textContent = 'Du ' + date(dates[i0]) + ' au ' + date(dates[fin]) + (tronque ? ' (période raccourcie : une des valeurs choisies n’était pas encore cotée)' : '')
      + (log ? '. Échelle logarithmique : une même hauteur correspond à une même multiplication.' : '.');
  }
})();
