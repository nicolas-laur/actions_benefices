/* Lexique : définition en pop-up au clic sur un sigle (le lien mène à la page du terme si JavaScript est coupé),
   et quiz à choix multiples avec correction et score. Aucune dépendance. */
(function () {
  // ---------- pop-up ----------
  var d = document.querySelector('dialog.fiche-terme');
  if (d) {
    var corps = d.querySelector('.fiche-corps');
    function ouvrir(slug) {
      var t = document.getElementById('t-' + slug); if (!t) return false;
      corps.textContent = ''; corps.appendChild(t.content.cloneNode(true));
      if (!d.open) d.showModal(); corps.scrollTop = 0; return true;
    }
    document.addEventListener('click', function (e) {
      var a = e.target.closest('[data-terme]');
      if (a && ouvrir(a.dataset.terme)) { e.preventDefault(); history.replaceState(null, '', '#' + a.dataset.terme); }
    });
    d.querySelector('.v-fermer').addEventListener('click', function () { d.close(); });
    d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
    d.addEventListener('close', function () { history.replaceState(null, '', location.pathname); });
    if (location.hash.length > 1) ouvrir(location.hash.slice(1));
  }

  // ---------- quiz ----------
  var q = document.querySelector('[data-quiz]'), src = document.getElementById('quiz-donnees');
  if (!q || !src) return;
  // banque de questions en trois niveaux ; chaque partie tire 10 questions du niveau choisi, d'abord parmi celles pas encore vues
  var BANQUE = JSON.parse(src.textContent), r = q.dataset.r, i = 0, score = 0, son = true, Q = [], niveau = null, PAR_PARTIE = 10;
  function melange(t) { t = t.slice(); for (var k = t.length - 1; k > 0; k--) { var j = Math.floor(Math.random() * (k + 1)), x = t[k]; t[k] = t[j]; t[j] = x; } return t; }
  function vus(n, ajout) {
    var cle = 'quiz-vus-' + n, l = [];
    try { l = JSON.parse(localStorage.getItem(cle) || '[]'); } catch (e) {}
    if (ajout) { l = l.concat(ajout); try { localStorage.setItem(cle, JSON.stringify(l)); } catch (e) {} }
    return l;
  }
  function tirage(n) {
    var pool = BANQUE.q.filter(function (x) { return x.n === n; }), deja = vus(n);
    var neuves = melange(pool.filter(function (x) { return deja.indexOf(x.id) < 0; }));
    if (neuves.length < PAR_PARTIE) {   // tout a été vu : on repart de zéro, en gardant les questions neuves en tête
      try { localStorage.removeItem('quiz-vus-' + n); } catch (e) {}
      neuves = neuves.concat(melange(pool.filter(function (x) { return neuves.indexOf(x) < 0; })));
    }
    return neuves.slice(0, PAR_PARTIE).map(function (x) {   // réponses mélangées à chaque partie
      var ordre = melange(x.c.map(function (_, k) { return k; }));
      return { id: x.id, q: x.q, e: x.e, p: x.p, c: ordre.map(function (k) { return x.c[k]; }), b: ordre.indexOf(x.b) };
    });
  }
  function lancer(n) { niveau = n; Q = tirage(n); vus(n, Q.map(function (x) { return x.id; })); i = 0; score = 0; question(); }
  function accueil() {
    q.textContent = '';
    var zone = el('div', 'quiz-zone'), g = el('div', 'pile'); g.style.gap = '14px'; zone.appendChild(g);
    g.appendChild(el('h3', 'quiz-q', 'Choisis ton niveau'));
    var l = el('div', 'quiz-niveaux');
    BANQUE.niveaux.forEach(function (nv, k) {
      var b = el('button', 'quiz-niveau'); b.type = 'button';
      b.appendChild(el('span', 'surtitre', 'Niveau ' + (k + 1))); b.appendChild(el('b', null, nv.nom)); b.appendChild(el('span', 'gris petit', nv.txt));
      b.appendChild(el('span', 'date', PAR_PARTIE + ' questions tirées parmi ' + nv.n));
      b.addEventListener('click', function () { lancer(nv.k); });
      l.appendChild(b);
    });
    g.appendChild(l); zone.appendChild(coin('question')); q.appendChild(zone);
  }
  try { son = localStorage.getItem('quiz-son') !== '0'; } catch (e) {}
  var BRAVO = ['pouce', 'rire', 'joie', 'etoiles'], RATE = ['facepalm', 'choc', 'triste', 'haussement'];
  var MOTS_OK = ['Bonne réponse !', 'Exact !', 'Bien vu !', 'Parfait !'], MOTS_KO = ['Raté !', 'Pas tout à fait…', 'Oups !', 'Presque !'];
  var audios = {};
  function joue(n) {
    if (!son) return;
    var a = audios[n] || (audios[n] = new Audio(r + 'assets/anim/' + n + '.mp3?v=' + (window.ABV || '')));
    try { a.currentTime = 0; var p = a.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {}
  }
  function hasard(t) { return t[Math.floor(Math.random() * t.length)]; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function coin(pose) { var im = el('img', 'quiz-coin'); im.src = r + 'assets/img/' + pose + '.webp?v=' + (window.ABV || ''); im.alt = 'Mister Coin'; return im; }
  function boutonSon() {
    var b = el('button', 'quiz-son', son ? '🔊' : '🔇'); b.type = 'button'; b.setAttribute('aria-label', son ? 'Couper le son' : 'Activer le son');
    b.addEventListener('click', function () { son = !son; b.textContent = son ? '🔊' : '🔇'; b.setAttribute('aria-label', son ? 'Couper le son' : 'Activer le son'); try { localStorage.setItem('quiz-son', son ? '1' : '0'); } catch (e) {} });
    return b;
  }
  // l'animation de fin est chargée pendant le quiz, pour démarrer sans attente
  var anim = null, WEBM = !!document.createElement('video').canPlayType('video/webm; codecs="vp9"') && !/^((?!chrome|android|crios|fxios).)*safari/i.test(navigator.userAgent);
  var FIN = r + 'assets/anim/joie' + (WEBM ? '.webm' : '.webp') + '?v=' + (window.ABV || '');
  function prechargeFin() { if (!anim) anim = fetch(FIN).then(function (x) { return x.blob(); }).catch(function () { return null; }); return anim; }
  function question() {
    var x = Q[i]; q.textContent = '';
    if (i === Q.length - 3) prechargeFin();
    var tete = el('div', 'quiz-tete');
    tete.appendChild(el('span', 'badge', BANQUE.niveaux.filter(function (nv) { return nv.k === niveau; })[0].nom + ' · question ' + (i + 1) + ' / ' + Q.length));
    var barre = el('div', 'quiz-barre'), b = el('i'); b.style.width = (100 * i / Q.length) + '%'; barre.appendChild(b); tete.appendChild(barre);
    tete.appendChild(el('span', 'quiz-pts', score + ' pt' + (score > 1 ? 's' : ''))); tete.appendChild(boutonSon());
    q.appendChild(tete);
    var zone = el('div', 'quiz-zone'); q.appendChild(zone);
    var g = el('div', 'pile'); g.style.gap = '14px'; zone.appendChild(g); var img = coin(x.p || ['question', 'reflechit', 'loupe', 'sceptique'][i % 4]); zone.appendChild(img);
    g.appendChild(el('h3', 'quiz-q', x.q));
    var choix = el('div', 'quiz-choix'); g.appendChild(choix);
    var fb = el('div', 'quiz-fb'); fb.setAttribute('aria-live', 'polite'); g.appendChild(fb);
    x.c.forEach(function (c, k) {
      var bt = el('button', 'quiz-rep', c); bt.type = 'button';
      bt.addEventListener('click', function () {
        var bon = k === x.b; if (bon) score++;
        Array.prototype.forEach.call(choix.children, function (o, j) { o.disabled = true; if (j === x.b) o.classList.add('bon'); else if (j === k) o.classList.add('faux'); });
        img.src = r + 'assets/img/' + hasard(bon ? BRAVO : RATE) + '.webp?v=' + (window.ABV || ''); img.classList.remove('saute'); void img.offsetWidth; img.classList.add('saute');
        joue(bon ? 's_bon' : 's_rate');
        tete.querySelector('.quiz-pts').textContent = score + ' pt' + (score > 1 ? 's' : '');
        fb.appendChild(el('strong', bon ? 'ok' : 'ko', hasard(bon ? MOTS_OK : MOTS_KO)));
        fb.appendChild(el('p', null, x.e));
        var suite = el('button', 'bouton', i + 1 < Q.length ? 'Question suivante' : 'Voir mon score'); suite.type = 'button';
        suite.addEventListener('click', function () { i++; if (i < Q.length) question(); else fin(); });
        fb.appendChild(suite); suite.focus({ preventScroll: true });
      });
      choix.appendChild(bt);
    });
  }
  function fin() {
    q.textContent = '';
    var zone = el('div', 'quiz-zone fin'), g = el('div', 'pile'); g.style.gap = '12px';
    var top = score >= Q.length * .8, moyen = score >= Q.length / 2;
    var tete = el('div', 'quiz-tete'); tete.appendChild(el('span', 'badge or', 'Ton score')); tete.appendChild(el('span', 'quiz-pts', '')); tete.appendChild(boutonSon()); q.appendChild(tete);
    g.appendChild(el('div', 'resultat', score + ' / ' + Q.length));
    g.appendChild(el('p', null, top ? 'Bravo, tu parles couramment la bourse ! Mister Coin danse de joie.' : moyen ? 'Pas mal ! Relis les définitions et retente ta chance.' : 'Les définitions sont juste au-dessus : relis-les et retente.'));
    var re = el('button', 'bouton or', 'Nouvelle partie'); re.type = 'button';
    re.addEventListener('click', function () { lancer(niveau); q.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    var ch = el('button', 'bouton', 'Changer de niveau'); ch.type = 'button';
    ch.addEventListener('click', function () { accueil(); q.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    var bs = el('div', 'pastilles'); bs.appendChild(re); bs.appendChild(ch); g.appendChild(bs); zone.appendChild(g);
    var parfait = score === Q.length;
    var img = coin(parfait ? 'site_trophee' : top || moyen ? 'joie' : 'site_ardoise'); zone.appendChild(img); q.appendChild(zone);
    if ((top || moyen) && !parfait) {
      // Mister Coin heureux et animé (clip « joie »), avec son cri de joie et une pluie de pièces
      prechargeFin().then(function (b) {
        var src = b ? URL.createObjectURL(b) : FIN;
        if (WEBM) { var v = el('video', 'quiz-coin'); v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.src = src; v.setAttribute('aria-label', 'Mister Coin danse de joie'); img.replaceWith(v); var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else { img.classList.add('anime'); img.src = src; }
      });
    }
    if (top || moyen) {
      // fanfare et pluie de pièces ; sans faute, Mister Coin brandit son trophée (image fixe) au lieu du clip « joie »
      joue('joie'); setTimeout(function () { joue('s_fanfare'); }, 350);
      for (var k = 0; k < 18; k++) {
        var p = el('span', 'confetti-piece'); p.style.left = Math.random() * 100 + '%'; p.style.animationDelay = (Math.random() * 1.2) + 's';
        p.style.animationDuration = (1.8 + Math.random() * 1.4) + 's'; zone.appendChild(p);
      }
    } else joue('s_rate');
  }
  accueil();
})();
