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
- Aucun chiffre caché par un tracé : étiquettes au-dessus des points, avec halo blanc.
- Marque affichée « Actions Bénéfices » (sans tiret bas) ; favicon rond, Mister Coin seul.
- Retours v2 (21/11) : les News doivent avoir du punch, kiosque en couverture et toutes les infos des diapos (galerie des diapos + texte) ; lexique en pop-up avec un exemple concret chiffré et un quiz ; courbe pour les intérêts composés ; comparateur PEA/CTO détaillé (durée, barème, titres d'avant 2018, dividendes US) ; vidéos consultables au choix TikTok ou Instagram (lecteur chargé au clic) ; lettre du dimanche signalée « en préparation ».
- Poses de Mister Coin jugées moches et retirées du site : « applaudit » (mains jointes) et « doigt levé ». Les expressions des carrousels sont appréciées.
