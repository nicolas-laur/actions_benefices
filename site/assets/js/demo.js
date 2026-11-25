/* Démonstrations du 25/11/2026 (page /demo/) : verre épais, chiffres qui comptent, courbe au défilement, mot de la semaine,
   yeux qui suivent, pluie de pièces, tableau à palettes, fiche feuilletée, jeu du plus ou moins. */
(function () {
  var D = JSON.parse(document.getElementById('demo-data').textContent);
  var R = document.querySelector('link[href*="demo.css"]').getAttribute('href').split('?')[0].replace('assets/css/demo.css', '');
  var V = '?v=' + (window.ABV || '');
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function fr(x, d) { return x.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function vu(el, f, seuil) { new IntersectionObserver(function (es, o) { es.forEach(function (e) { if (e.isIntersecting) { f(); o.disconnect(); } }); }, { threshold: seuil || .4 }).observe(el); }

  // 1. verre épais : reflet et inclinaison qui suivent la souris
  document.querySelectorAll('.verre-epais').forEach(function (t) {
    t.addEventListener('pointermove', function (e) {
      var b = t.getBoundingClientRect(), x = (e.clientX - b.left) / b.width, y = (e.clientY - b.top) / b.height;
      t.style.setProperty('--mx', (x * 100) + '%'); t.style.setProperty('--my', (y * 100) + '%');
      t.style.setProperty('--ry', ((x - .5) * 14) + 'deg'); t.style.setProperty('--rx', ((.5 - y) * 12) + 'deg');
    });
    t.addEventListener('pointerleave', function () { t.style.setProperty('--rx', '0deg'); t.style.setProperty('--ry', '0deg'); });
  });

  // 3. chiffres qui comptent
  function compte(el, fin, dec, unite, ms) {
    if (calme) { el.textContent = fr(fin, dec) + unite; return; }
    var t0 = null;
    function pas(t) { t0 = t0 || t; var p = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - p, 4); el.textContent = fr(fin * e, dec) + unite; if (p < 1) requestAnimationFrame(pas); }
    requestAnimationFrame(pas);
  }
  document.querySelectorAll('.compte').forEach(function (el) { vu(el, function () { compte(el, +el.dataset.fin, +el.dataset.dec, el.dataset.unite, 1600); }); });

  // 3. courbe dessinée au défilement
  (function () {
    var box = document.querySelector('.demo-courbe'); if (!box || !D.sp.length) return;
    var pts = D.sp, vals = pts.map(function (p) { return p[1]; }), mn = Math.min.apply(0, vals) * .95, mx = Math.max.apply(0, vals) * 1.03;
    var X = function (i) { return i / (pts.length - 1) * 1000; }, Y = function (v) { return 350 - (v - mn) / (mx - mn) * 330; };
    var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join('');
    var tr = box.querySelector('.trace'), pt = box.querySelector('.point'), lab = box.querySelector('.compte-courbe');
    tr.setAttribute('d', d); var L = tr.getTotalLength();
    function maj() {
      var b = box.getBoundingClientRect(), av = Math.max(0, Math.min(1, (innerHeight * .9 - b.top) / (b.height + innerHeight * .4)));
      box.style.setProperty('--av', av);
      var q = tr.getPointAtLength(L * av); pt.setAttribute('cx', q.x); pt.setAttribute('cy', q.y);
      var i = Math.round(av * (pts.length - 1)); lab.textContent = fr(pts[i][1], 0) + ' €';
    }
    addEventListener('scroll', maj, { passive: true }); maj();
  })();

  // 4. mot de la semaine
  (function () {
    var c = document.querySelector('.mot-carte'); if (!c) return;
    c.querySelector('.mot-sigle').textContent = D.mot.sigle; c.querySelector('.mot-nom').textContent = D.mot.nom;
    var z = c.querySelector('.mot-q'), q = D.mot.q;
    if (!q) { var a = document.createElement('a'); a.className = 'bouton clair'; a.textContent = 'Voir la définition →'; a.href = R + 'lexique/'; z.appendChild(a); return; }
    var p = document.createElement('p'); p.textContent = q.q; z.appendChild(p);
    q.c.forEach(function (t, k) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'bouton clair'; b.textContent = t;
      b.addEventListener('click', function () {
        z.querySelectorAll('button').forEach(function (x, j) { x.disabled = true; if (j === q.b) x.style.boxShadow = 'inset 0 0 0 2px var(--vert-lum)'; });
        if (k !== q.b) b.style.boxShadow = 'inset 0 0 0 2px var(--rouge-lum)';
        var e = document.createElement('p'); e.className = 'petit'; e.textContent = (k === q.b ? 'Bravo ! ' : 'Raté ! ') + q.e; z.appendChild(e);
      });
      z.appendChild(b);
    });
  })();

  // 6. yeux qui suivent
  (function () {
    var sc = document.querySelector('.yeux-scene'); if (!sc) return;
    var Y = JSON.parse(sc.dataset.yeux), svg = sc.querySelector('.yeux-svg'), reac = sc.querySelector('.yeux-reaction');
    var pup = svg.querySelectorAll('.oeil'), ref = svg.querySelectorAll('.reflet');
    function regarde(cx, cy) {
      var b = svg.getBoundingClientRect(), k = Y.w / b.width;
      Y.yeux.forEach(function (e, i) {
        var dx = (cx - b.left) * k - e.cx, dy = (cy - b.top) * k - e.cy, n = Math.hypot(dx, dy) || 1, f = Math.min(1, n / 400);
        var mx = e.rx * .38 * f * dx / n, my = e.ry * .34 * f * dy / n;
        pup[i].setAttribute('cx', e.cx + mx); pup[i].setAttribute('cy', e.cy + my);
        ref[i].setAttribute('cx', e.cx + mx + e.rx * .14); ref[i].setAttribute('cy', e.cy + my - e.ry * .18);
      });
    }
    addEventListener('pointermove', function (e) { regarde(e.clientX, e.clientY); }, { passive: true });
    document.querySelectorAll('.yeux-chips .chip').forEach(function (c) {
      var src = R + 'assets/img/expr/' + c.dataset.expr + '.webp' + V; new Image().src = src;
      c.addEventListener('pointerenter', function () { reac.src = src; sc.classList.add('reagit'); });
      c.addEventListener('pointerleave', function () { sc.classList.remove('reagit'); });
    });
  })();

  // 7. pluie de pièces
  (function () {
    var cv = document.getElementById('pluie-cv'); if (!cv) return;
    var ctx = cv.getContext('2d'), piece = new Image(); piece.src = R + 'assets/deco/piece1.webp' + V;
    var anim = null;
    function lancer() {
      var m = +document.getElementById('pl-m').value || 100, t = (+document.getElementById('pl-t').value || 0) / 100, ans = +document.getElementById('pl-d').value || 30;
      var dpr = devicePixelRatio || 1, W = cv.clientWidth, H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var tranches = [], cap = 0, verse = 0, r = Math.pow(1 + t, 1 / 12) - 1;
      for (var a = 1; a <= ans; a++) { for (var k = 0; k < 12; k++) { cap = cap * (1 + r) + m; verse += m; } if (a % 5 === 0 || a === ans) tranches.push({ a: a, cap: cap, verse: verse }); }
      var n = tranches.length, larg = Math.min(110, (W - 60) / n), haut = H - 70, maxc = tranches[n - 1].cap, taille = Math.min(44, larg * .7), ep = taille * .32;
      var pieces = [];
      tranches.forEach(function (tr, i) {
        var nb = Math.max(1, Math.round(tr.cap / maxc * haut / ep)), nbv = Math.round(tr.verse / maxc * haut / ep), x = 40 + i * larg + larg / 2;
        for (var j = 0; j < nb; j++) pieces.push({ x: x, cible: H - 40 - j * ep, y: -40 - Math.random() * 300 - j * 14 - i * 60, v: 0, dore: j >= nbv, i: i });
      });
      cancelAnimationFrame(anim);
      function frame() {
        ctx.clearRect(0, 0, W, H); var fini = true;
        pieces.forEach(function (p) {
          if (p.y < p.cible) { p.v += .9; p.y = Math.min(p.cible, p.y + p.v); fini = false; }
          ctx.save(); ctx.globalAlpha = p.dore ? 1 : .55;
          ctx.drawImage(piece, p.x - taille / 2, p.y - ep, taille, ep * 1.4); ctx.restore();
        });
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--texte-clair'); ctx.font = '600 12px Inter, sans-serif'; ctx.textAlign = 'center';
        tranches.forEach(function (tr, i) {
          var x = 40 + i * larg + larg / 2; ctx.fillText(tr.a + ' ans', x, H - 14);
          if (fini) { ctx.font = '800 13px Inter, sans-serif'; ctx.fillText(Math.round(tr.cap).toLocaleString('fr-FR') + ' €', x, H - 50 - Math.round(tr.cap / maxc * haut)); ctx.font = '600 12px Inter, sans-serif'; }
        });
        if (!fini) anim = requestAnimationFrame(frame);
        else document.querySelector('.pluie-res').textContent = 'Au bout de ' + ans + ' ans : ' + Math.round(cap).toLocaleString('fr-FR') + ' €, dont ' + Math.round(verse).toLocaleString('fr-FR') + ' € versés (pièces pâles) et ' + Math.round(cap - verse).toLocaleString('fr-FR') + ' € d\'intérêts (pièces dorées). Calcul mensuel, rendement constant, avant impôts et frais.';
      }
      frame();
    }
    document.getElementById('pl-go').addEventListener('click', lancer);
    vu(cv, function () { (piece.complete ? lancer : function () { piece.onload = lancer; })(); });
  })();

  // 8. tableau à palettes
  (function () {
    var box = document.getElementById('pal-tab'); if (!box) return;
    var ALPH = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-,.%', son = false, ac = null;
    function clac() {
      if (!son) return; ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      var o = ac.createBufferSource(), b = ac.createBuffer(1, 600, ac.sampleRate), d = b.getChannelData(0);
      for (var i = 0; i < 600; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / 600, 6) * .25;
      o.buffer = b; o.connect(ac.destination); o.start();
    }
    var L = window.innerWidth < 860 ? 18 : 22;
    var lignes = D.bandeau.map(function (b) {
      var nom = b.nom.toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^A-Z0-9 &]/g, ' ').replace('&', ' ').slice(0, L - 8);
      var v = (b.var >= 0 ? '+' : '-') + Math.abs(b.var).toFixed(2).replace('.', ',') + '%';
      return { txt: (nom + ' '.repeat(L)).slice(0, L - v.length) + v, sens: b.var >= 0 ? 'hausse' : 'baisse', nv: v.length };
    });
    var cases = lignes.map(function (l) {
      var row = document.createElement('div'); row.className = 'ligne-pal'; box.appendChild(row);
      return l.txt.split('').map(function (ch, k) {
        var c = document.createElement('div'); c.className = 'case' + (k >= l.txt.length - l.nv ? ' ' + l.sens : '');
        c.innerHTML = '<div class="h"><span> </span></div><div class="b"><span> </span></div><div class="volet"><span> </span></div>'; row.appendChild(c); return c;
      });
    });
    function poser(c, ch) { c.querySelectorAll('span').forEach(function (s) { s.textContent = ch; }); }
    function jouer() {
      lignes.forEach(function (l, i) {
        l.txt.split('').forEach(function (cible, k) {
          var c = cases[i][k], pos = 0, fin = Math.max(0, ALPH.indexOf(cible)), tours = fin + (cible === ' ' ? 0 : 0);
          poser(c, ' ');
          if (calme) { poser(c, cible); return; }
          setTimeout(function pas() {
            if (pos >= tours) { poser(c, cible); return; }
            pos++; var ch = ALPH[pos % ALPH.length]; c.classList.remove('tourne'); void c.offsetWidth; c.classList.add('tourne');
            c.querySelector('.volet span').textContent = c.querySelector('.h span').textContent; c.querySelector('.h span').textContent = ch; c.querySelector('.b span').textContent = ch;
            if (k % 3 === 0) clac();
            setTimeout(pas, 45);
          }, i * 120 + k * 25);
        });
      });
    }
    document.getElementById('pal-go').addEventListener('click', jouer);
    document.getElementById('pal-son').addEventListener('click', function () { son = !son; this.textContent = (son ? '🔊' : '🔇') + ' Son'; });
    vu(box, jouer);
  })();

  // 9. fiche feuilletée
  (function () {
    var d = document.getElementById('dos-box'); if (!d) return;
    var f = [].slice.call(d.querySelectorAll('.feuille')), i = 0, num = document.getElementById('dos-num');
    f.forEach(function (x, k) { x.style.zIndex = f.length - k; });
    function maj() { f.forEach(function (x, k) { x.classList.toggle('tournee', k < i); x.style.zIndex = k < i ? k : f.length - k; }); num.textContent = (i + 1) + ' / ' + f.length; }
    function aller(n) { i = Math.max(0, Math.min(f.length - 1, n)); maj(); }
    d.addEventListener('click', function (e) { if (e.target.closest('a')) return; aller(i + 1 >= f.length ? 0 : i + 1); });
    d.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') aller(i + 1); if (e.key === 'ArrowLeft') aller(i - 1); });
    document.getElementById('dos-prec').addEventListener('click', function () { aller(i - 1); });
    document.getElementById('dos-suiv').addEventListener('click', function () { aller(i + 1); });
    maj();
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
