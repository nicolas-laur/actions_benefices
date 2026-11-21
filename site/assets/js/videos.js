/* Page Vidéos : le lecteur TikTok ou Instagram ne se charge qu'au clic (aucun service tiers avant le choix du visiteur),
   et filtres Tout / Vidéos / Carrousels. Aucune dépendance. */
(function () {
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.lecteur'); if (!b) return;
    var carte = b.closest('.video'), ecran = carte.querySelector('.ecran');
    var f = document.createElement('iframe');
    f.src = b.dataset.src; f.title = 'Lecteur ' + b.textContent.trim();
    f.setAttribute('allow', 'encrypted-media; fullscreen; picture-in-picture'); f.setAttribute('allowfullscreen', '');
    f.loading = 'lazy'; f.className = b.classList.contains('insta') ? 'insta' : 'tiktok';
    ecran.textContent = ''; ecran.classList.add('joue'); ecran.appendChild(f);
    carte.querySelectorAll('.lecteur').forEach(function (x) { x.classList.toggle('actif', x === b); });
    var o = carte.querySelector('.ouvrir'); o.href = b.dataset.lien; o.hidden = false;
  });
  var filtres = document.querySelectorAll('[data-filtre]');
  filtres.forEach(function (f) {
    f.addEventListener('click', function () {
      filtres.forEach(function (x) { x.classList.toggle('actif', x === f); });
      document.querySelectorAll('.video').forEach(function (v) { v.hidden = f.dataset.filtre !== 'tout' && v.dataset.type !== f.dataset.filtre; });
    });
  });
})();
