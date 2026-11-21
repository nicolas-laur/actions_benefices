/* Galerie des diapos des News : flèches pour faire défiler la piste, et visionneuse plein écran au clic
   (flèches, clavier ← → Échap, glissé du doigt). Aucune dépendance. */
(function () {
  var g = document.querySelector('[data-galerie]'); if (!g) return;
  var piste = g.querySelector('.gal-piste');
  var imgs = Array.prototype.map.call(g.querySelectorAll('.gal-diapo img'), function (im) { return im.src; });
  g.querySelector('.prec').addEventListener('click', function () { piste.scrollBy({ left: -piste.clientWidth * .8, behavior: 'smooth' }); });
  g.querySelector('.suiv').addEventListener('click', function () { piste.scrollBy({ left: piste.clientWidth * .8, behavior: 'smooth' }); });

  // visionneuse
  var v = document.createElement('dialog'); v.className = 'visionneuse'; v.setAttribute('aria-label', 'Diapos du carrousel');
  v.innerHTML = '<button class="v-fermer" type="button" aria-label="Fermer">×</button>'
    + '<button class="v-fleche prec" type="button" aria-label="Diapo précédente">‹</button>'
    + '<figure><img alt=""><figcaption></figcaption></figure>'
    + '<button class="v-fleche suiv" type="button" aria-label="Diapo suivante">›</button>';
  document.body.appendChild(v);
  var im = v.querySelector('img'), cap = v.querySelector('figcaption'), i = 0;
  function voir(k) { i = (k + imgs.length) % imgs.length; im.src = imgs[i]; im.alt = 'Diapo ' + (i + 1); cap.textContent = (i + 1) + ' / ' + imgs.length; }
  function ouvrir(k) { voir(k); if (!v.open) v.showModal(); }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.gal-diapo, .gal-ouvre'); if (b) ouvrir(+b.dataset.i || 0);
  });
  v.querySelector('.v-fermer').addEventListener('click', function () { v.close(); });
  v.querySelector('.v-fleche.prec').addEventListener('click', function () { voir(i - 1); });
  v.querySelector('.v-fleche.suiv').addEventListener('click', function () { voir(i + 1); });
  v.addEventListener('click', function (e) { if (e.target === v) v.close(); });   // clic sur le fond
  v.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') voir(i - 1); if (e.key === 'ArrowRight') voir(i + 1); });
  var x0 = null;
  v.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  v.addEventListener('touchend', function (e) {
    if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) voir(dx < 0 ? i + 1 : i - 1);
  });
})();
