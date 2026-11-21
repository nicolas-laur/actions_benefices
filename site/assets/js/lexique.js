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
  var Q = JSON.parse(src.textContent), r = q.dataset.r, i = 0, score = 0;
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function coin(pose) { var im = el('img', 'quiz-coin'); im.src = r + 'assets/img/' + pose + '.png'; im.alt = 'Mister Coin'; return im; }
  function question() {
    var x = Q[i]; q.textContent = '';
    var tete = el('div', 'quiz-tete');
    tete.appendChild(el('span', 'badge', 'Question ' + (i + 1) + ' / ' + Q.length));
    var barre = el('div', 'quiz-barre'), b = el('i'); b.style.width = (100 * i / Q.length) + '%'; barre.appendChild(b); tete.appendChild(barre);
    q.appendChild(tete);
    var zone = el('div', 'quiz-zone'); q.appendChild(zone);
    var g = el('div', 'pile'); g.style.gap = '14px'; zone.appendChild(g); var img = coin('question'); zone.appendChild(img);
    g.appendChild(el('h3', 'quiz-q', x.q));
    var choix = el('div', 'quiz-choix'); g.appendChild(choix);
    var fb = el('div', 'quiz-fb'); fb.setAttribute('aria-live', 'polite'); g.appendChild(fb);
    x.c.forEach(function (c, k) {
      var bt = el('button', 'quiz-rep', c); bt.type = 'button';
      bt.addEventListener('click', function () {
        var bon = k === x.b; if (bon) score++;
        Array.prototype.forEach.call(choix.children, function (o, j) { o.disabled = true; if (j === x.b) o.classList.add('bon'); else if (j === k) o.classList.add('faux'); });
        img.src = r + 'assets/img/' + (bon ? 'pouce' : 'facepalm') + '.png';
        fb.appendChild(el('strong', bon ? 'ok' : 'ko', bon ? 'Bonne réponse !' : 'Raté !'));
        fb.appendChild(el('p', null, x.e));
        var suite = el('button', 'bouton', i + 1 < Q.length ? 'Question suivante' : 'Voir mon score'); suite.type = 'button';
        suite.addEventListener('click', function () { i++; if (i < Q.length) question(); else fin(); });
        fb.appendChild(suite); suite.focus();
      });
      choix.appendChild(bt);
    });
  }
  function fin() {
    q.textContent = '';
    var zone = el('div', 'quiz-zone'), g = el('div', 'pile'); g.style.gap = '12px';
    var top = score >= Q.length * .8, moyen = score >= Q.length / 2;
    g.appendChild(el('span', 'badge or', 'Ton score'));
    g.appendChild(el('div', 'resultat', score + ' / ' + Q.length));
    g.appendChild(el('p', null, top ? 'Bravo, tu parles couramment la bourse !' : moyen ? 'Pas mal ! Relis les définitions et retente ta chance.' : 'Les définitions sont juste au-dessus : relis-les et retente.'));
    var re = el('button', 'bouton', 'Recommencer'); re.type = 'button';
    re.addEventListener('click', function () { i = 0; score = 0; question(); });
    g.appendChild(re); zone.appendChild(g); zone.appendChild(coin(top ? 'rire' : moyen ? 'pouce' : 'reflechit')); q.appendChild(zone);
  }
  question();
})();
