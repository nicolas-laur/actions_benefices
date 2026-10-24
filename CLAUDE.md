# Consignes pour Claude — Actions_Bénéfices

Langue : français, tutoiement, prose structurée, peu de gras, pas de tirets cadratins. Poser les questions avant un livrable complexe.

## Règles de production (validées par Nicolas)
- Format 9:16 natif 1080×1920, export CRF 15 / 16 Mb/s. Pas de barre de progression en haut.
- Chiffres exacts et vérifiés (sources dans `sources.md`), montants en euros convertis au taux BCE, indices hors dividendes précisés.
- Aucun logo de marque réelle ; le logo de la chaîne est `lib/logo.py` (ne pas le modifier).
- Le chiffre choc est visible à l'image 0. Sous-titres mot à mot, mot clé surligné, toujours lisibles.
- Zone sûre des applis (Reels, TikTok, Shorts) : rien d'important sous y = 1500 (pseudo, légende, son), ni au-dessus de y = 200 (en-tête), ni à droite de x = 950 entre y = 1000 et 1700 (icônes). Sous-titres centrés vers y ≈ 1035–1060, largeur de ligne max 760 px ; Mister Coin en dessous, pieds vers y ≈ 1650 (ses pieds peuvent passer sous l'interface, pas sa tête ni ses mains).
- Musique douce, bruitages discrets. Émojis Noto bienvenus.
- Script pour la voix : nombres écrits en toutes lettres ; Nicolas génère la voix (ElevenLabs refuse la génération depuis Claude).

## Mister Coin (voir `mister_coin/README.md`)
- Présent tout du long, taille constante, pas de gros plan ; il illustre le propos et apporte de l'âme.
- Mouvements lents et fluides ; grimaces, joie et poses à bouche figée uniquement dans les silences de la voix.
- Ses deux mains restent dans le cadre ; rien du décor ne passe devant lui (seuls les sous-titres sont au-dessus).
- Bulles de BD courtes, accrochées à lui, jamais sur un texte important ; pas de blague sur la question finale.

## Publication
- Nicolas publie lui-même, à la main, sur TikTok, YouTube Shorts et Instagram Reels (pas de programmation via Metricool : plan gratuit).
- Livrables de chaque vidéo : la vidéo, la couverture, la description TikTok, un titre YouTube Shorts, une légende Instagram et les sources pour le premier commentaire.

## Avant chaque rendu
Générer des aperçus (`python3 video.py png …`), vérifier une image par scène (texte lisible, mains dans le cadre, bulles accrochées), puis `python3 render.py episodes/<dossier>`.
