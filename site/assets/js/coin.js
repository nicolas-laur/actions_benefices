/* Mister Coin vivant sur l'accueil : il arrive en sautant, salue en se balançant, réagit quand on clique sur lui
   (animation tirée des clips Veo, son coupé par défaut), et au 5e clic lance une pluie de pièces à attraper. */
(function () {
  var sc = document.querySelector('.coin-scene'); if (!sc) return;
  var r = sc.dataset.r, img = sc.querySelector('.coin-anim'), bulle = sc.querySelector('.coin-bulle'), btSon = sc.querySelector('.coin-son');
  var REPOS = r + 'assets/img/salut.webp';
  // durée de chaque clip (images / 15 i/s) et son associé
  var CLIPS = { saut: [4000, 'saut'], joie: [4000, 'joie'], rire: [4000, 'rire'], danse: [4000, 'danse'], pouce: [3530, 's_bon'], choc: [3070, 's_rate'] };
  var REACTIONS = ['joie', 'rire', 'danse', 'pouce', 'saut'];
  var son = false, occupe = false, minuteur = null, clics = 0, jeu = false, derniere = '';
  try { son = localStorage.getItem('coin-son') === '1'; } catch (e) {}
  function majSon() { btSon.textContent = son ? '🔊' : '🔇'; btSon.setAttribute('aria-label', son ? 'Couper le son' : 'Activer le son'); btSon.setAttribute('aria-pressed', son); }
  majSon();
  btSon.addEventListener('click', function (e) { e.stopPropagation(); son = !son; majSon(); try { localStorage.setItem('coin-son', son ? '1' : '0'); } catch (er) {} });
  var audios = {};
  function joue(nom) {
    if (!son || !nom) return;
    var a = audios[nom] || (audios[nom] = new Audio(r + 'assets/anim/' + nom + '.mp3?v=' + (window.ABV || '')));
    try { a.currentTime = 0; var p = a.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {}
  }
  function dit(t, ms) { bulle.textContent = t; bulle.classList.add('visible'); clearTimeout(dit.t); dit.t = setTimeout(function () { bulle.classList.remove('visible'); }, ms || 2200); }
  // Animations : vidéo WebM transparente (nette et légère) là où elle est gérée, WebP animé ailleurs (Safari, iPhone).
  // Chargées à l'avance et gardées en mémoire : chaque lecture repart du début sans retélécharger.
  var V = '?v=' + (window.ABV || '');
  var WEBM = !!document.createElement('video').canPlayType('video/webm; codecs="vp9"') && !/^((?!chrome|android|crios|fxios).)*safari/i.test(navigator.userAgent);
  var EXT = WEBM ? '.webm' : '.webp', vid = null;
  if (WEBM) {
    vid = document.createElement('video'); vid.className = 'coin-anim coin-video'; vid.muted = true; vid.playsInline = true; vid.setAttribute('playsinline', '');
    vid.setAttribute('aria-hidden', 'true'); vid.hidden = true; img.parentNode.insertBefore(vid, img.nextSibling);
  }
  var cache = {}, urlActive = null;
  function precharge(n) {
    if (cache[n]) return cache[n];
    return cache[n] = fetch(r + 'assets/anim/' + n + EXT + V).then(function (x) { return x.blob(); }).catch(function () { return null; });
  }
  function repos() { img.src = REPOS; img.hidden = false; if (vid) { vid.pause(); vid.hidden = true; } sc.classList.remove('anime'); }
  function anime(n, fin) {
    var c = CLIPS[n]; occupe = true; clearTimeout(minuteur);
    precharge(n).then(function (b) {
      if (urlActive) URL.revokeObjectURL(urlActive);
      urlActive = b ? URL.createObjectURL(b) : null;
      var src = urlActive || r + 'assets/anim/' + n + EXT + V;
      sc.classList.add('anime'); joue(c[1]);
      if (WEBM) { vid.src = src; vid.currentTime = 0; vid.hidden = false; img.hidden = true; var p = vid.play(); if (p && p.catch) p.catch(function () {}); }
      else img.src = src;
      minuteur = setTimeout(function () { repos(); occupe = false; if (fin) fin(); }, c[0]);
    });
  }
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // pas de bulle quand une annotation « Clique-moi ! » est déjà dessinée à côté de lui
  var accueil = document.querySelector('.mq-note.n1') ? function () {} : function () { dit('Salut ! Clique sur moi 👋', 3500); };
  if (!calme) { precharge('saut'); setTimeout(function () { anime('saut', accueil); }, 400); }
  else accueil();
  setTimeout(function () { REACTIONS.forEach(precharge); }, 2500);

  img.addEventListener('click', clic); if (vid) vid.addEventListener('click', clic);
  img.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); clic(); } });
  function clic() {
    if (jeu || occupe) return;
    clics++;
    if (clics === 5) { lancerJeu(); return; }
    var choix = REACTIONS.filter(function (x) { return x !== derniere; }); derniere = choix[Math.floor(Math.random() * choix.length)];
    anime(derniere);
  }

  // ---------- mini-jeu : la pluie de pièces ----------
  var zone = document.querySelector('.hero'), score = 0;
  function lancerJeu() {
    jeu = true; score = 0; clics = 0;
    joue('s_pieces');
    var tableau = document.createElement('div'); tableau.className = 'jeu-score'; tableau.innerHTML = 'Attrape les pièces ! 🪙 <b>0</b> · <span>15</span> s';
    zone.appendChild(tableau); zone.classList.add('en-jeu');
    var t0 = Date.now(), DUREE = 15000;
    var pluie = setInterval(function () {
      var p = document.createElement('button'); p.type = 'button'; p.className = 'piece'; p.setAttribute('aria-label', 'Attraper la pièce');
      var taille = 38 + Math.random() * 26; p.style.width = p.style.height = taille + 'px';
      p.style.left = (4 + Math.random() * 88) + '%'; p.style.animationDuration = (2.2 + Math.random() * 1.6) + 's';
      p.addEventListener('pointerdown', function (e) {
        e.preventDefault(); if (p.classList.contains('prise')) return;
        p.classList.add('prise'); score++; tableau.querySelector('b').textContent = score; joue('s_piece');
        setTimeout(function () { p.remove(); }, 300);
      });
      p.addEventListener('animationend', function () { p.remove(); });
      zone.appendChild(p);
    }, 380);
    var horloge = setInterval(function () {
      var reste = Math.max(0, Math.ceil((DUREE - (Date.now() - t0)) / 1000)); tableau.querySelector('span').textContent = reste;
      if (reste <= 0) finJeu();
    }, 250);
    function finJeu() {
      clearInterval(pluie); clearInterval(horloge);
      setTimeout(function () { zone.querySelectorAll('.piece').forEach(function (p) { p.remove(); }); }, 1500);
      var record = 0; try { record = +localStorage.getItem('coin-record') || 0; if (score > record) localStorage.setItem('coin-record', score); } catch (e) {}
      var msg = score > record && record ? 'Nouveau record 🏆' : score >= 20 ? 'Quel talent !' : score >= 10 ? 'Bien joué !' : 'Retente ta chance !';
      tableau.innerHTML = msg + ' 🪙 <b>' + score + '</b>' + (record ? ' · record ' + Math.max(score, record) : '');
      anime(score >= 10 ? 'joie' : 'rire', function () { jeu = false; setTimeout(function () { tableau.remove(); zone.classList.remove('en-jeu'); }, 2500); });
      if (score >= 10) joue('s_fanfare');
    }
  }
})();
