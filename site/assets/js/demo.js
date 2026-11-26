/* Démonstrations, version 2 du 26/11/2026 (page /demo/) : verre en relief, chiffres qui comptent, courbe nette, jeu du plus ou moins. */
(function () {
  var D = JSON.parse(document.getElementById('demo-data').textContent);
  var R = document.querySelector('link[href*="demo.css"]').getAttribute('href').split('?')[0].replace('assets/css/demo.css', '');
  var V = '?v=' + (window.ABV || '');
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function fr(x, d) { return x.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function vu(el, f, seuil) { new IntersectionObserver(function (es, o) { es.forEach(function (e) { if (e.isIntersecting) { f(); o.disconnect(); } }); }, { threshold: seuil || .4 }).observe(el); }
  function douce(p) { return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; }

  // 1. verre en relief. La tranche est faite de 24 couches empilées en profondeur, qui suivent l'inclinaison.
  // L'inclinaison est lissée image par image (pas de transition CSS relancée à chaque mouvement de souris, source des à-coups).
  var plaques = [];
  document.querySelectorAll('.v3d').forEach(function (t, k) {
    var corps = t.querySelector('.v-corps'), face = t.querySelector('.v-face');
    for (var i = 24; i >= 1; i--) {
      var c = document.createElement('div'); c.className = 'v-tranche' + (i === 24 ? ' der' : ''); c.style.setProperty('--z', i * 1.2); var f = 1 - i * .02; c.style.background = 'linear-gradient(180deg,rgb(' + [247 * f, 198 * f, 90 * f].map(Math.round) + '),rgb(' + [185 * f, 130 * f, 31 * f].map(Math.round) + '))';
      corps.insertBefore(c, face);
    }
    var p = { el: t, x: 0, y: 0, cx: 0, cy: 0, mx: 30, my: 20, cmx: 30, cmy: 20, dedans: false, phase: k * 1.7 };
    t.addEventListener('pointermove', function (e) {
      var b = t.getBoundingClientRect(), x = (e.clientX - b.left) / b.width - .5, y = (e.clientY - b.top) / b.height - .5;
      p.dedans = true; p.x = -4 + x * 30; p.y = 9 - y * 24; p.mx = 50 + x * 90; p.my = 50 + y * 90;
    });
    t.addEventListener('pointerleave', function () { p.dedans = false; });
    plaques.push(p);
  });
  if (plaques.length) {
    var visible = true;
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(document.querySelector('.demo-verres'));
    (function boucle(t) {
      if (visible) plaques.forEach(function (p) {
        if (!p.dedans) { var s = calme ? 0 : t / 1000 + p.phase; p.x = -13 + Math.sin(s * .9) * 5; p.y = 15 + Math.cos(s * .7) * 3; p.mx = 28 + Math.sin(s * .9) * 8; p.my = 18; }
        var k = p.dedans ? .14 : .05, e = innerWidth < 860 ? .6 : 1;
        p.cx += (p.x - p.cx) * k; p.cy += (p.y - p.cy) * k; p.cmx += (p.mx - p.cmx) * k; p.cmy += (p.my - p.cmy) * k;
        var s2 = p.el.style;
        s2.setProperty('--ry', (p.cx * e).toFixed(2) + 'deg'); s2.setProperty('--rx', (p.cy * e).toFixed(2) + 'deg');
        s2.setProperty('--mx', p.cmx.toFixed(1) + '%'); s2.setProperty('--my', p.cmy.toFixed(1) + '%');
        s2.setProperty('--ox', (-p.cx * 1.4).toFixed(1) + 'px'); s2.setProperty('--gx', (p.cx * 7).toFixed(1) + 'px');
      });
      requestAnimationFrame(boucle);
    })(0);
  }

  // chiffres qui comptent
  function compte(el, fin, dec, unite, ms) {
    if (calme) { el.textContent = fr(fin, dec) + unite; return; }
    var t0 = null;
    function pas(t) { t0 = t0 || t; var p = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - p, 4); el.textContent = fr(fin * e, dec) + unite; if (p < 1) requestAnimationFrame(pas); }
    requestAnimationFrame(pas);
  }
  document.querySelectorAll('.compte').forEach(function (el) { vu(el, function () { compte(el, +el.dataset.fin, +el.dataset.dec, el.dataset.unite, 1600); }); });

  // 3. courbe tracée à la taille réelle du cadre (pas d'étirement, donc nette), dessinée une fois à l'apparition.
  (function () {
    var box = document.querySelector('.demo-courbe'); if (!box || !D.sp.length) return;
    var svg = box.querySelector('.courbe-svg'), grille = svg.querySelector('.cb-grille'), rect = svg.querySelector('.cb-rect');
    var trait = svg.querySelector('.cb-trait'), halo = svg.querySelector('.cb-halo'), aire = svg.querySelector('.cb-aire'), point = svg.querySelector('.cb-point');
    var val = box.querySelector('.compte-courbe'), an = box.querySelector('.courbe-an');
    var pts = D.sp, vals = pts.map(function (p) { return p[1]; }), mn = Math.floor(Math.min.apply(0, vals) / 50) * 50, mx = Math.ceil(Math.max.apply(0, vals) * 1.04 / 50) * 50;
    var W = 0, H = 0, XY = [], fini = false, NS = 'http://www.w3.org/2000/svg';
    an.textContent = pts[0][0].slice(0, 4);
    function el(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }
    function trace() {
      var b = svg.getBoundingClientRect(); W = Math.round(b.width); H = Math.round(b.height); if (!W) return;
      var g = 36, bas = H - 26;
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      XY = pts.map(function (p, i) { return [g + i / (pts.length - 1) * (W - g - 14), bas - (p[1] - mn) / (mx - mn) * (bas - 10)]; });
      var d = XY.map(function (q, i) { return (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1); }).join('');
      trait.setAttribute('d', d); halo.setAttribute('d', d); aire.setAttribute('d', d + 'L' + XY[XY.length - 1][0].toFixed(1) + ' ' + bas + 'L' + g + ' ' + bas + 'Z');
      grille.textContent = '';
      for (var v = mn; v <= mx; v += 50) { var y = bas - (v - mn) / (mx - mn) * (bas - 10); grille.appendChild(el('line', { x1: g, x2: W, y1: y, y2: y })); var t = el('text', { x: 0, y: y + 4 }); t.textContent = v; grille.appendChild(t); }
      var vus = {};
      pts.forEach(function (p, i) { var a = p[0].slice(0, 4); if (!vus[a] && p[0].slice(5, 7) <= '01' && (W > 600 || +a % 2 === 0)) { vus[a] = 1; var t = el('text', { x: XY[i][0] - 14, y: H - 4 }); t.textContent = a; grille.appendChild(t); } });
      if (fini) pose(1);
    }
    function pose(p) {
      var f = p * (XY.length - 1), i = Math.min(XY.length - 2, Math.floor(f)), r = f - i;
      var x = XY[i][0] + (XY[i + 1][0] - XY[i][0]) * r, y = XY[i][1] + (XY[i + 1][1] - XY[i][1]) * r, v = vals[i] + (vals[i + 1] - vals[i]) * r;
      rect.setAttribute('width', x + 8); point.setAttribute('cx', x); point.setAttribute('cy', y); point.style.opacity = 1;
      val.textContent = fr(v, 0); an.textContent = pts[Math.round(f)][0].slice(0, 4);
    }
    function joue() {
      if (calme) { fini = true; pose(1); return; }
      var t0 = null; fini = false;
      (function pas(t) { t0 = t0 || t; var p = Math.min(1, (t - t0) / 2600); pose(douce(p)); if (p < 1) requestAnimationFrame(pas); else fini = true; })(performance.now());
    }
    new ResizeObserver(trace).observe(svg); trace();
    rect.setAttribute('width', 0);
    vu(box, joue, .5);
    box.querySelector('.cb-rejouer').addEventListener('click', joue);
  })();

  // 10. jeu du plus ou moins
  (function () {
    var box = document.querySelector('.demo-jeu'); if (!box) return;
    var P = D.perf, K = Object.keys(P), serie = 0, record = 0, bt = box.querySelectorAll('.duel'), coin = box.querySelector('.jeu-coin'), msg = box.querySelector('.jeu-msg'), duo, bloque = false;
    try { record = +localStorage.getItem('demo-record') || 0; } catch (e) {}
    function img(n) { coin.src = R + 'assets/img/expr/' + n + '.webp' + V; coin.style.scale = '1.12'; setTimeout(function () { coin.style.scale = '1'; }, 200); }
    function fmt(p) { return (p >= 0 ? '+' : '−') + Math.abs(p).toLocaleString('fr-FR') + ' %'; }
    function tour() {
      do { duo = [K[Math.floor(Math.random() * K.length)], K[Math.floor(Math.random() * K.length)]]; } while (duo[0] === duo[1] || P[duo[0]].p === P[duo[1]].p);
      bt.forEach(function (b, k) { var x = P[duo[k]]; b.className = 'duel'; b.innerHTML = '<b></b><small></small><span class="res"></span>'; b.querySelector('b').textContent = x.nom; b.querySelector('small').textContent = x.g; b.querySelector('.res').textContent = fmt(x.p); });
      bloque = false; msg.textContent = 'Laquelle ?'; img('reflechit');
      box.querySelector('#jeu-serie').textContent = 'Série : ' + serie; box.querySelector('#jeu-record').textContent = 'Record : ' + record;
    }
    bt.forEach(function (b, k) {
      b.addEventListener('click', function () {
        if (bloque) return; bloque = true;
        var bon = P[duo[k]].p > P[duo[1 - k]].p;
        bt.forEach(function (x, j) { x.classList.add('revele'); x.classList.add(P[duo[j]].p > P[duo[1 - j]].p ? 'bon' : 'faux'); });
        if (bon) { serie++; if (serie > record) { record = serie; try { localStorage.setItem('demo-record', record); } catch (e) {} } msg.textContent = serie >= 5 ? 'Série de ' + serie + ', quel flair !' : 'Bien vu !'; img(serie >= 5 ? 'site_trophee' : 'joie'); }
        else { msg.textContent = 'Raté ! Série remise à zéro.'; serie = 0; img('facepalm'); }
        setTimeout(tour, 1800);
      });
    });
    vu(box, tour, .2);
  })();
})();
