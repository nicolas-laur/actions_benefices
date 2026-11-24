/* Thème du site : entrées à ressort à l'apparition (une fois), parallaxe, récit épinglé et tracé doré de l'accueil.
   Sans dépendance ; sans JavaScript, tout reste visible. */
(function () {
  document.documentElement.classList.add('js');
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // pages intérieures : les blocs encore sous l'écran au chargement entreront au défilement (ceux déjà visibles ne bougent pas : pas de clignotement)
  document.querySelectorAll('main .section > *, main .grille > *, main .lecture, main .tuiles > *').forEach(function (el) {
    if (el.closest('.mq-couverture, .mq-recit, .hero') || el.classList.contains('mq-anim') || el.closest('.mq-anim')) return;
    if (el.getBoundingClientRect().top < innerHeight * .92) return;
    var i = [].indexOf.call(el.parentNode.children, el); el.classList.add('mq-anim'); el.style.setProperty('--i', i % 6);
  });
  // 1. entrées : chaque élément s'anime une seule fois quand il arrive à l'écran
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vu'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -12% 0px' });
  document.querySelectorAll('.mq-anim, .mq-mot, .mq-pastille, .mq-note, .mq-trait').forEach(function (el) {
    if (!el.closest('.mq-cote')) io.observe(el);
  });
  // 2. récit épinglé : l'étape active suit le repère qui passe au milieu de l'écran
  var recit = document.querySelector('.mq-recit');
  if (recit) {
    var reperes = recit.querySelectorAll('.mq-repere');
    function etape(k) {
      recit.dataset.k = k;
      recit.querySelectorAll('[data-k]').forEach(function (el) { if (el !== recit && !el.classList.contains('mq-repere')) el.classList.toggle('actif', el.dataset.k === String(k)); });
    }
    var io2 = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) etape(e.target.dataset.k); });
    }, { rootMargin: '-50% 0px -50% 0px' });
    reperes.forEach(function (r) { io2.observe(r); });
  }
  // parallaxe : décalage proportionnel à la distance entre l'élément et le milieu de l'écran (moitié moins fort sur téléphone)
  var plans = [].slice.call(document.querySelectorAll('[data-vitesse]')), recitEl = document.querySelector('.mq-recit');
  if (!calme && (plans.length || recitEl)) {
    var attente = false;
    function parallaxe() {
      attente = false;
      var h = innerHeight, f = innerWidth < 860 ? .5 : 1;
      plans.forEach(function (el) {
        var r = el.getBoundingClientRect(), py = parseFloat(el.style.getPropertyValue('--py')) || 0;
        var centre = r.top - py + r.height / 2;            // position sans le décalage déjà appliqué
        if (centre < -h || centre > 2 * h) return;
        el.style.setProperty('--py', ((centre - h / 2) * -el.dataset.vitesse * f).toFixed(1) + 'px');
      });
      if (recitEl) {                                       // avancement du récit épinglé, de 0 à 1
        var rr = recitEl.getBoundingClientRect(), course = rr.height - h;
        recitEl.style.setProperty('--p', Math.min(1, Math.max(0, -rr.top / (course || 1))).toFixed(3));
      }
    }
    addEventListener('scroll', function () { if (!attente) { attente = true; requestAnimationFrame(parallaxe); } }, { passive: true });
    addEventListener('resize', parallaxe); parallaxe();
  }
  // 3. tracé doré : sa longueur dessinée suit la position de la zone dans l'écran
  var zone = document.querySelector('.mq-trace-zone'), trace = zone && zone.querySelector('.mq-trace');
  if (trace && !calme) {
    var demande = false;
    function maj() {
      demande = false;
      var r = zone.getBoundingClientRect(), h = innerHeight;
      var p = Math.min(1, Math.max(0, (h - r.top) / (h * .8 + r.height)));
      trace.style.setProperty('--avance', (1 - p).toFixed(3));
    }
    addEventListener('scroll', function () { if (!demande) { demande = true; requestAnimationFrame(maj); } }, { passive: true });
    maj();
  }
})();

// mode clair / sombre : réglage de l'appareil par défaut ; le bouton fixe un choix gardé dans le navigateur
(function () {
  var d = document.documentElement, b = document.querySelector('.bascule-theme');
  function choisi() { try { return localStorage.getItem('theme'); } catch (e) { return null; } }
  function etiquette() { if (b) b.setAttribute('aria-label', d.dataset.theme === 'clair' ? 'Passer en mode sombre' : 'Passer en mode clair'); }
  etiquette();
  if (b) b.addEventListener('click', function () {
    d.dataset.theme = d.dataset.theme === 'clair' ? 'sombre' : 'clair';
    try { localStorage.setItem('theme', d.dataset.theme); } catch (e) {}
    etiquette(); document.dispatchEvent(new Event('theme'));
  });
  var m = matchMedia('(prefers-color-scheme: light)');
  (m.addEventListener ? m.addEventListener.bind(m, 'change') : m.addListener.bind(m))(function (e) {
    if (choisi()) return;                       // le visiteur a choisi : on ne suit plus l'appareil
    d.dataset.theme = e.matches ? 'clair' : 'sombre'; etiquette(); document.dispatchEvent(new Event('theme'));
  });
})();

