/* Mister Coin sur l'accueil (25/11/2026) : à chaque clic, il change d'expression en puisant dans la banque de poses
   (assets/img/expr/, 1080 px de haut). Toutes les expressions passent avant qu'une revienne, dans un ordre mélangé.
   Le disque de la pièce reste toujours au même endroit (centre de l'arc) et à la même taille : chaque image porte
   ses mesures (--h, --fx, --fy en rayons de disque, site/outils/expressions.py) et le CSS en déduit taille et position. */
(function () {
  var sc = document.querySelector('.coin-scene'); if (!sc) return;
  var r = sc.dataset.r, img = sc.querySelector('.coin-expr'), btSon = sc.querySelector('.coin-son');
  if (!img) return;
  var EXPR = JSON.parse(img.dataset.expr), V = '?v=' + (window.ABV || '');
  var NOMS = Object.keys(EXPR).filter(function (n) { return n !== 'salut'; }), file = [], actuel = 'salut', occupe = false;
  var son = false;
  try { son = localStorage.getItem('coin-son') === '1'; } catch (e) {}
  function majSon() { btSon.textContent = son ? '🔊' : '🔇'; btSon.setAttribute('aria-label', son ? 'Couper le son' : 'Activer le son'); btSon.setAttribute('aria-pressed', son); }
  if (btSon) { majSon(); btSon.addEventListener('click', function (e) { e.stopPropagation(); son = !son; majSon(); try { localStorage.setItem('coin-son', son ? '1' : '0'); } catch (er) {} }); }
  // un bruitage par famille d'expressions (site/outils/sons_coin.py), avec une légère variation de hauteur à chaque clic
  var SONS = { salut: 'pop', pouce: 'pop', question: 'pop', joie: 'monte', site_saut_joie: 'monte', etoiles: 'monte', rire: 'monte',
    triste: 'descend', inquiet: 'descend', sueur: 'descend', choc: 'choc', facepalm: 'choc', reflechit: 'ding', loupe: 'ding',
    site_trophee: 'caisse', site_tirelire: 'caisse', sceptique: 'hmm', haussement: 'hmm', site_dort: 'ronfle',
    site_megaphone: 'annonce', court: 'pas', site_parapluie: 'pas' };
  var lecteurs = {};
  function joue(n) {
    if (!son) return;
    try {
      var s = SONS[n] || 'piece', a = lecteurs[s] = lecteurs[s] || new Audio(r + 'assets/anim/s_' + s + '.mp3' + V);
      a.preservesPitch = a.mozPreservesPitch = a.webkitPreservesPitch = false;
      a.playbackRate = .92 + Math.random() * .16; a.volume = .8; a.currentTime = 0;
      var p = a.play(); if (p && p.catch) p.catch(function () {});
    } catch (e) {}
  }
  function url(n) { return r + 'assets/img/expr/' + n + '.webp' + V; }
  var cache = {};
  function precharge(n) {
    if (cache[n]) return cache[n];
    return cache[n] = new Promise(function (ok) { var i = new Image(); i.decoding = 'async'; i.onload = i.onerror = function () { (i.decode ? i.decode() : Promise.resolve()).catch(function () {}).then(ok); }; i.src = url(n); });
  }
  function suivant() {
    if (!file.length) {   // nouveau tour : ordre mélangé, sans répéter l'expression affichée
      file = NOMS.slice(); for (var k = file.length - 1; k > 0; k--) { var j = Math.floor(Math.random() * (k + 1)), t = file[k]; file[k] = file[j]; file[j] = t; }
      if (file[0] === actuel) file.push(file.shift());
    }
    return file.shift();
  }
  function pose(n) {
    var m = EXPR[n];
    img.style.setProperty('--h', m[0]); img.style.setProperty('--fx', m[1]); img.style.setProperty('--fy', m[2]);
    img.src = url(n); actuel = n;
  }
  function clic() {
    if (occupe) return; occupe = true;
    var n = suivant();
    precharge(n).then(function () {
      sc.classList.remove('pop'); void img.offsetWidth;   // relance l'animation d'apparition
      pose(n); sc.classList.add('pop'); joue(n);
      if (file[0]) precharge(file[0]); if (file[1]) precharge(file[1]);
      setTimeout(function () { occupe = false; }, 260);
    });
  }
  img.addEventListener('click', clic);
  img.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); clic(); } });
  // les premières expressions sont chargées dès que la page est au repos, les suivantes au fil des clics
  setTimeout(function () { var n = suivant(); file.unshift(n); precharge(n); if (file[1]) precharge(file[1]); }, 1500);
})();
