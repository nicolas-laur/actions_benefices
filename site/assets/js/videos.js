/* Page Vidéos : clic sur une vignette (ou sur un bouton TikTok / Instagram) = lecteur en pop-up, avec un onglet par réseau.
   Le lecteur tiers ne se charge qu'à l'ouverture (aucun cookie avant). Filtres Tout / Vidéos / Carrousels. */
(function () {
  var d = document.querySelector('dialog.lecteur-pop'); if (!d) return;
  var ecran = d.querySelector('.lp-ecran'), ouvrir = d.querySelector('.lp-ouvrir'), carte = null;
  function url(pl, c, embed) {
    if (pl === 'tiktok') return embed ? 'https://www.tiktok.com/embed/v2/' + c.dataset.tiktok : 'https://www.tiktok.com/@actions_bnfices/video/' + c.dataset.tiktok;
    return 'https://www.instagram.com/' + c.dataset.insta + (embed ? '/embed/' : '/');
  }
  function montre(pl) {
    d.querySelectorAll('.lp-onglet').forEach(function (o) {
      var dispo = o.dataset.plateforme === 'tiktok' ? !!carte.dataset.tiktok : !!carte.dataset.insta;
      o.hidden = !dispo; o.classList.toggle('actif', o.dataset.plateforme === pl); o.setAttribute('aria-selected', o.dataset.plateforme === pl);
    });
    var f = document.createElement('iframe');
    f.src = url(pl, carte, true); f.title = 'Lecteur ' + (pl === 'tiktok' ? 'TikTok' : 'Instagram');
    f.setAttribute('allow', 'autoplay; encrypted-media; fullscreen; picture-in-picture'); f.setAttribute('allowfullscreen', '');
    f.className = pl; ecran.textContent = ''; ecran.appendChild(f); ouvrir.href = url(pl, carte, false);
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.video .ecran, .video .lecteur'); if (!b) return;
    carte = b.closest('.video');
    var pl = b.dataset.plateforme || (carte.dataset.tiktok ? 'tiktok' : 'insta');
    d.querySelector('.lp-titre').textContent = carte.dataset.titre; montre(pl); d.showModal();
  });
  d.querySelectorAll('.lp-onglet').forEach(function (o) { o.addEventListener('click', function () { montre(o.dataset.plateforme); }); });
  d.querySelector('.v-fermer').addEventListener('click', function () { d.close(); });
  d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
  d.addEventListener('close', function () { ecran.textContent = ''; });   // coupe le son en fermant
  var filtres = document.querySelectorAll('[data-filtre]');
  filtres.forEach(function (f) {
    f.addEventListener('click', function () {
      filtres.forEach(function (x) { x.classList.toggle('actif', x === f); });
      document.querySelectorAll('.video').forEach(function (v) { v.hidden = f.dataset.filtre !== 'tout' && v.dataset.type !== f.dataset.filtre; });
    });
  });
})();
