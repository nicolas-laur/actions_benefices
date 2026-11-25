/* Infobulles des graphiques : tout élément portant data-tip affiche son détail au survol (souris), au focus (clavier) ou au toucher (mobile).
   data-tip : lignes séparées par « \n » ; la première ligne sert de titre. Aucune dépendance. */
(function () {
  var bulle = document.createElement('div');
  bulle.className = 'infobulle'; bulle.setAttribute('role', 'tooltip'); bulle.hidden = true;
  document.body.appendChild(bulle);
  var actif = null;

  function remplir(el) {
    bulle.textContent = '';
    el.getAttribute('data-tip').split('\n').forEach(function (ligne, i) {
      var d = document.createElement(i === 0 ? 'strong' : 'span');
      d.textContent = ligne; bulle.appendChild(d);
    });
  }
  // place la bulle près du point (x, y) sans sortir de l'écran
  function placer(x, y) {
    var m = 12, w = bulle.offsetWidth, h = bulle.offsetHeight, vw = window.innerWidth, vh = window.innerHeight;
    var gx = x + m + w > vw - 8 ? x - m - w : x + m;
    var gy = y - h - m < 8 ? y + m : y - h - m;
    bulle.style.left = Math.max(8, gx) + 'px'; bulle.style.top = Math.max(8, Math.min(gy, vh - h - 8)) + 'px';
  }
  function montrer(el, x, y) {
    if (actif !== el) { if (actif) actif.classList.remove('survol'); actif = el; el.classList.add('survol'); remplir(el); }
    bulle.hidden = false; placer(x, y);
  }
  function cacher() { if (actif) actif.classList.remove('survol'); actif = null; bulle.hidden = true; }
  function cible(e) { return e.target.closest && e.target.closest('[data-tip]'); }

  document.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;
    var el = cible(e); if (el) montrer(el, e.clientX, e.clientY); else if (actif) cacher();
  });
  // au toucher : un appui ouvre la bulle, un appui ailleurs la ferme
  document.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'touch') return;
    var el = cible(e); if (el) montrer(el, e.clientX, e.clientY); else cacher();
  });
  document.addEventListener('focusin', function (e) {
    var el = cible(e); if (!el) return;
    var r = el.getBoundingClientRect(); montrer(el, r.left + r.width / 2, r.top);
  });
  document.addEventListener('focusout', cacher);
  window.addEventListener('scroll', cacher, { passive: true });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cacher(); });
})();

// graphiques version téléphone : bouton « Voir les N trimestres », et vue en grand du flux au toucher de l'aperçu
(function () {
  document.querySelectorAll('.hb-plus').forEach(function (b) {
    b.addEventListener('click', function () {
      var o = b.getAttribute('aria-expanded') !== 'true'; b.setAttribute('aria-expanded', o);
      var hb = b.closest('.hb'), lignes = hb.querySelectorAll('.hb-l, .hb-an');
      if (!hb.dataset.vis) hb.dataset.vis = [].map.call(lignes, function (l) { return l.hidden ? 0 : 1; }).join('');
      lignes.forEach(function (l, i) { l.hidden = !o && hb.dataset.vis[i] === '0'; });
      if (!o) hb.scrollIntoView({ block: 'nearest' });
    });
  });
  var vue = null;
  document.querySelectorAll('.flux-apercu').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!vue) {
        vue = document.createElement('div'); vue.className = 'flux-grand'; vue.setAttribute('role', 'dialog'); vue.setAttribute('aria-modal', 'true');
        vue.innerHTML = '<div class="flux-grand-tete"><span>Touche un bloc pour son détail. Tourne ton téléphone pour l\'agrandir.</span><button type="button" aria-label="Fermer">✕</button></div><div class="flux-grand-corps"></div>';
        document.body.appendChild(vue);
        vue.querySelector('button').addEventListener('click', fermer);
        addEventListener('keydown', function (e) { if (e.key === 'Escape' && !vue.hidden) fermer(); });
      }
      // le graphique complet, avec ses infobulles, est celui de la version ordinateur de la même figure
      var svg = b.closest('figure, .carte').querySelector('.g-bureau svg');
      var corps = vue.querySelector('.flux-grand-corps'); corps.innerHTML = ''; corps.appendChild(svg.cloneNode(true));
      vue.setAttribute('aria-label', svg.getAttribute('aria-label') || 'Graphique');
      vue.hidden = false; document.documentElement.classList.add('flux-ouvert'); vue.querySelector('button').focus(); vue._de = b;
    });
  });
  function fermer() { vue.hidden = true; document.documentElement.classList.remove('flux-ouvert'); if (vue._de) vue._de.focus(); }
})();
