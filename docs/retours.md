# Retours de Nicolas et leçons apprises (à relire en début de session)

Ce fichier garde l'essentiel de ce que Nicolas a validé, refusé ou corrigé, pour qu'une session neuve ne refasse pas les mêmes erreurs. Une ligne par leçon, la plus récente en haut de chaque section. Ajouter une ligne à chaque retour important.

## Ce qu'il attend de Claude
- Vérifier soi-même chaque version (image et son) avant de l'envoyer, et le dire franchement quand une partie n'est pas au niveau.
- Proposer des alternatives quand une idée ne le convainc pas (ex. sujets du 14/11, polices GTA), puis appliquer ce qu'il choisit sans revenir dessus.
- Tenir les promesses de délai (« je te l'envoie demain matin ») ; ne jamais annoncer un livrable non produit (excuse du 15/11 pour le script loto).
- Ne jamais lancer un rendu complet avant validation des maquettes (écart du 15/11 sur le loto, signalé).
- Économie de tokens (16/11) : une session par épisode ; valider script, DA et maquettes avant tout rendu ; grouper les retours en une passe ; vérifier sur planches en basse définition et zoomer seulement sur les zones à risque ; s'appuyer sur les gabarits de `lib/` plutôt que recopier de gros scripts.

## Lisibilité (retour le plus fréquent)
- Polices condensées type Big Shoulders illisibles en vidéo : les garder pour la couverture. Notre police habituelle est Inter Display (lib/mty.py, carrousels), pas Alfa Slab One ni Archivo Black (17/11).
- Jamais de texte sur du texte : c'est le premier motif de refus (loto, 15-16/11 : TOI contre « 1 chance sur… », note 7 % sur les sous-titres, sous-titre de l'accroche doublé pendant le fondu). Contrôler chaque transition de scène, pas seulement une image par scène.
- Petits textes posés sur une plaque ; rangées de jours et étiquettes au-dessus des sous-titres, jamais dessous.
- Panneaux et compteurs : apparition et disparition en fondu, jamais d'un coup.

## Mise en scène et motion design
- Photo d'une personne réelle : fournie par Nicolas, posée dans un cadre Polaroïd avec une courte fiche (Ellison, 20/11).
- Le verre 3D translucide (`lib/verre_epais.py`) est notre signature pour afficher les informations, y compris dans une DA dédiée comme GTA (17/11).
- Il pousse vers le spectaculaire quand une scène est plate : le zoom « 1 chance sur 19 068 840 » a été refait cinq fois (grille plate → perspective, personnages → foule de Mister Coin, cible joyeuse et rieuse au milieu de pièces inquiètes, halo rond et non carré, éclairages de projecteurs). Viser d'emblée ce niveau.
- Travelling : Mister Coin marche de face en parlant (clips `danse_parle_*`, marche sur place), jamais de dos (23/11, Black Friday). Ces clips se jouent toujours vers l'avant (`VeoCoin(..., boucle=(...))`) : en aller-retour il marche à reculons et la scène paraît « glitchée » (24/11).
- Texte posé sur un objet mobile du décor (étiquette) : trajectoire suivie sur toutes les images du décor 60 i/s puis lissée, taille liée au seul travelling ; jamais une détection par image arrondie (le texte tremble, 24/11).
- Clips assis (`parle_compte_doigts`, `loupe_parle`) : posé au bord d'un objet, jambes pendantes ; décalage pièce-pieds mesuré par clip et bord suivi image par image pendant le travelling, sinon il flotte (23/11).
- Mister Coin posé sur les objets du décor (debout sur le comptoir) plutôt que flottant devant.
- Objets du réel conformes à la réalité : une seule boule rouge (numéro chance) au Loto, cinq blanches.
- Sons satisfaisants à garder quand ils existent (pièces qui tombent).
- Ne pas réutiliser une scène trop récente dans l'esprit des spectateurs (haricots refusés le 15/11) : machine à sous inversée et pommier dans un verger choisis à la place.

## Couvertures
- Style maison (`lib/cards_lib.py`) : fond du décor principal, titre court, question « Et toi… ? », Mister Coin expressif. Une couverture surchargée ou d'un autre style a été jugée « affreuse » (loto) : rester simple.
- Retirer les éléments décoratifs du haut et les accessoires qui détournent l'attention (cochon) ; Mister Coin avec les étoiles dans les yeux en bas a été apprécié.

## Textes et ton
- Script voix : ne pas laisser de balise [silence …] dans le texte envoyé à ElevenLabs, elle produit un bruit ; les silences de réaction se règlent au montage (21/11).
- Bulles : il les réécrit volontiers sur un ton familier et enjoué (« Pas de stress ma poule », « WHAOU ! Tout en un clic ! ») ; proposer ce ton d'emblée, bulles courtes, coupées en deux lignes à la ponctuation si longues.
- Question finale tournée vers le spectateur et en lien avec l'actualité (« Et toi, tu as acheté GTA 6 ? »).
- Formulations rigoureuses mais simples : expliquer un ratio par un exemple (« sur 100 € joués » incompris, reformulé).

## Ligne éditoriale (mi-novembre)
- Le sujet lié à l'actualité et la qualité priment sur le rythme de publication. Les séries d'entreprises sont en réserve.
- Le style cartoon 1930 marche (dividendes, loto). Sujets provocateurs d'éducation financière simple.
- Carrousels : les sigles utilisés dans nos vidéos (lexique du 17/11) et les News du vendredi.

## Site actionsbenefices.com (retours v1 du 21/11)
- Affichage mobile jugé pauvre : chantier important à mener (menu, en-têtes, graphiques, tuiles), suivi dans `site/A_FAIRE.md`. Vérifier chaque page en 390 px de large avant de livrer.
- Graphiques interactifs : chaque barre, bloc ou ruban donne son détail au survol (et au toucher sur mobile) ; reprendre les pictogrammes des carrousels dans les graphiques du site.
- Aucun chiffre caché par un tracé : étiquettes au-dessus des points, avec un halo de la couleur du fond.
- Marque affichée « Actions Bénéfices » (sans tiret bas) ; favicon rond, Mister Coin seul.
- Retours v2 (21/11) : les News doivent avoir du punch, kiosque en couverture et toutes les infos des diapos (galerie des diapos + texte) ; lexique en pop-up avec un exemple concret chiffré et un quiz ; courbe pour les intérêts composés ; comparateur PEA/CTO détaillé (durée, barème, titres d'avant 2018, dividendes US) ; vidéos consultables au choix TikTok ou Instagram (lecteur chargé au clic) ; lettre du dimanche signalée « en préparation ».
- Retours v3 (22/11) : bandeau défilant des marchés sur l'accueil ; Mister Coin vivant et cliquable (réactions avec son coupé par défaut, mini-jeu de pièces) ; quiz « Teste tes connaissances ! » avec une pose par question et une fin animée et sonore ; performances historiques comparées (Yahoo Finance) ; lecteur vidéo en pop-up avec logos TikTok et Instagram. Référence UX à étudier : more-nutrition.webflow.io.
- Qualité d'image (22/11) : les images pixelisées sont refusées. Toujours prévoir 2× la taille d'affichage (écrans Retina) : poses en WebP 720 px (site/outils/poses_hd.py), animations en WebM transparent + WebP pour Safari, agrandies par Real-ESRGAN quand la source est petite (site/outils/clips_coin.py), vignettes en 720×1280.
- Poses de Mister Coin jugées moches et retirées du site : « applaudit » (mains jointes) et « doigt levé ». Les expressions des carrousels sont appréciées.
- Direction artistique du site validée (22/11, « Là c'est parfait, applique ça à tout le site ») : sombre et or comme les vidéos (fond nuit #0B0E14, or lumineux #FFC24A, verre sombre à filet doré), pleine largeur, entrées à ressort et parallaxe façon More Nutrition, pièces peintes (props des épisodes, pas de pièces en CSS), étincelles vectorielles animées, Mister Coin centré sur son arc, pas de bulle au clic sur l'accueil. Thème dans site/assets/css/theme.css et site/assets/js/theme.js, graphiques en palette lumineuse. Rien de décoratif sur un titre ou un texte.
- Retours du 24/11 : mentions légales complètes (éditeur Nicolas Laur, particulier, contact actionsbenefices@gmail.com) ; plus d'air sous chaque couverture de page ; tuiles vidéos de même hauteur ; lexique porté à 75 termes en trois niveaux (débutant, initié, expert) avec un quiz par niveau, 10 questions tirées au hasard en évitant celles déjà vues ; comparateur de performances élargi aux actions américaines et européennes par secteur, au Brent, aux métaux et aux principales cryptos.
- Mode clair et sombre (24/11) : le site suit le réglage de l'appareil, un bouton soleil/lune dans l'en-tête fixe le choix (gardé dans le navigateur). Mode clair « papier crème et or » (fond #F6F0E3, or profond #A87508, encre marine), graphiques remappés en couleurs d'encre. Toute nouvelle couleur passe par les variables de theme.css (--fort, --l, --panneau…), jamais en dur.
- Lisibilité (24/11) : aucun texte sous le seuil WCAG AA dans les deux modes ; vérifier avec site/outils/contraste.py avant chaque mise en ligne d'une page ou d'un composant. Jamais de couleur de texte en dur dans le HTML (style="color:#fff" restait blanc en mode clair).
