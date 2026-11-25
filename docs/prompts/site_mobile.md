Chantier : rendre le site actionsbenefices.com vraiment adapté au téléphone (responsive). Une session dédiée.

PREMIÈRE RÉPONSE, avant tout le reste :
1. Clone le dépôt nicolas-laur/actions_benefices.
2. Lis CLAUDE.md, docs/retours.md (section « Site actionsbenefices.com »), site/A_FAIRE.md (section « Affichage mobile ») et parcours la structure de site/ (templates, assets/css/theme.css, assets/js/theme.js, outils de génération).
3. Génère le site en local et fais l'état des lieux page par page en 390 px de large (iPhone) et 360 px (Android), avec des captures : accueil, fiches entreprises (Nvidia, Alphabet), News, vidéos, lexique et quiz, comparateur PEA/CTO, calculateurs, lettre du dimanche, pied de page. Pour chaque page, note ce qui casse : sections pas centrées, débordements horizontaux, textes trop petits ou trop grands, tuiles et tableaux trop larges, graphiques illisibles (défilement horizontal, étiquettes qui se chevauchent), infobulles inutilisables au toucher, menu qui s'empile.
4. Envoie-moi une planche de captures avant/après prévue et un plan par ordre de priorité, puis pose tes questions à la fin.

Ce que j'attends :
- En-tête compact avec menu repliable (☰) ; le bouton « La lettre du dimanche » reste accessible.
- Toutes les sections centrées, marges régulières, aucune barre de défilement horizontale sur la page.
- Graphiques lisibles sans défilement horizontal : versions verticales ou simplifiées sur mobile (barres horizontales, moins d'étiquettes, légende sous le graphique), valeurs au toucher, et aucun chiffre caché par un tracé.
- Tuiles et tableaux (rivaux, comparateur) empilés ou en cartes sur mobile.
- Images nettes (2× la taille d'affichage), rien de pixelisé.
- La direction artistique validée le 22/11 ne change pas (sombre et or, mode clair crème et or, Mister Coin, entrées à ressort) ; référence UX : more-nutrition.webflow.io.

Méthode :
- Maquettes (captures mobiles) à valider avant de tout reprendre, puis une page à la fois, en commençant par celles qui comptent le plus pour les visiteurs venus de TikTok et Instagram (accueil, fiches, News).
- Vérifier chaque page modifiée en 390 px et 360 px, en mode sombre et en mode clair, et sur ordinateur pour ne rien casser.
- Commits par page, poussés avec la boucle de 5 essais ; mettre à jour site/A_FAIRE.md et docs/retours.md à la fin.
