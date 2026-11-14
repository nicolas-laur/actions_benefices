# Consignes pour Claude — Actions_Bénéfices

Langue : français, tutoiement, prose structurée, peu de gras, pas de tirets cadratins. Poser les questions avant un livrable complexe.

## Règles de production (validées par Nicolas)
- Format 9:16 natif 1080×1920, export CRF 15 / 16 Mb/s. Pas de barre de progression en haut.
- Chiffres exacts et vérifiés (sources dans `sources.md`), montants en euros convertis au taux BCE, indices hors dividendes précisés.
- Aucun logo de marque réelle, sauf ceux que Nicolas fournit ou demande pour un contenu (ex. carrousel GAFAM du 31/10, ETF MSCI World du 2/11 : dossier `logos/` de l'épisode, tuiles façon icône d'appli tirées des favicons ou du jeu « logos » d'Iconify) ; le logo de la chaîne est `lib/logo.py` (ne pas le modifier).
- Accroche (depuis le 01/11) : test « accroche question » (elle ouvre une question, la réponse arrive ensuite) contre « chiffre choc à l'image 0 », 4 vidéos chacune ; voir les notes de chaque vidéo dans la roadmap. Durée 20 à 30 s (15 s pour le format court). Sous-titres mot à mot, mot clé surligné, toujours lisibles.
- Zone sûre des applis (Reels, TikTok, Shorts) : rien d'important sous y = 1500 (pseudo, légende, son), ni au-dessus de y = 200 (en-tête), ni à droite de x = 950 entre y = 1000 et 1700 (icônes). Sous-titres centrés vers y ≈ 1035–1060, largeur de ligne max 760 px ; Mister Coin en dessous, pieds vers y ≈ 1650 (ses pieds peuvent passer sous l'interface, pas sa tête ni ses mains).
- Musique douce, bruitages discrets. Émojis Noto bienvenus.
- Script pour la voix : nombres écrits en toutes lettres ; Nicolas génère la voix (ElevenLabs refuse la génération depuis Claude).
- `voice_full.wav` toujours en 48 kHz mono (`ffmpeg -i voix_src.mp3 -ac 1 -ar 48000 voice_full.wav`) : le mixage lit la voix à 48 kHz ; un fichier en 44,1 kHz rend la voix accélérée et aiguë (erreur du 01/11, corrigée).

## Mister Coin (voir `mister_coin/README.md`)
- Présent tout du long, taille constante, pas de gros plan ; il illustre le propos et apporte de l'âme.
- Mouvements lents et fluides ; grimaces, joie et poses à bouche figée uniquement dans les silences de la voix.
- Ses deux mains restent dans le cadre ; rien du décor ne passe devant lui (seuls les sous-titres sont au-dessus).
- Bulles de BD courtes, accrochées à lui, jamais sur un texte important ; pas de blague sur la question finale.

## Banque de clips Mister Coin (Gemini / Veo), méthode retenue le 27/10
- Nicolas génère les clips dans Gemini, en 16:9, avec l'image de référence à marges (`mister_coin/veo/*_reference_marges_16x9.jpg`) et le bloc de prompt commun (pieds au sol quand il parle, parle du début à la fin, pose neutre au début et à la fin, grandes marges).
- Chaque clip déposé dans `mister_coin/veo/` est analysé par `python3 mister_coin/veo_catalogue.py` (taille, position, plages où il parle / se tait) ; `veo_coin.py` les monte : il parle quand la voix parle, se tait dans les silences, change de clip en plein saut entre deux scènes.
- Éviter la répétition : un clip de parole différent par scène, réactions (joie, déception, choc…) dans les silences, jamais le même geste deux fois de suite.
- Formats légers (recherche, 15 s ; décidé le 01/11) : Mister Coin présent mais avec 2 ou 3 clips seulement.

## Exigences retenues (retours du 27/10 sur la vidéo carburant)
- Niveau d'exigence élevé : vérifier soi-même chaque version avant de l'envoyer (images clés, transitions, son), pas seulement une image par scène.
- Mister Coin : jamais de fondu entre deux poses différentes (double image) ni de saut d'image. Dans un clip, il rejoint la pose voulue en jouant les images ; entre deux clips, coupe franche pendant un petit saut sur place (`VeoCoin(..., lisse=True)`).
- Décors animés : pas de coupures ni de clignotements brusques (néons, lumières) ; mouvements lents et continus.
- Objets du réel animés comme dans la réalité (ex. compteur de pompe qui tourne à débit régulier, sans remise à zéro).
- Graphiques soignés (matière, reflets, dégradés, étiquettes reliées) et accompagnés d'un son satisfaisant quand ils évoluent.

## Publication
- Nicolas publie lui-même, à la main, sur TikTok, YouTube Shorts et Instagram Reels (pas de programmation via Metricool : plan gratuit).
- Livrables de chaque vidéo : la vidéo, la couverture, la description TikTok, un titre YouTube Shorts, une légende Instagram et les sources pour le premier commentaire.

## Avant chaque rendu
Toujours envoyer des maquettes (images clés de chaque scène) à Nicolas et attendre sa validation avant de lancer le rendu complet d'une vidéo (demandé le 05/11).
Générer des aperçus (`python3 video.py png …`), vérifier une image par scène (texte lisible, mains dans le cadre, bulles accrochées), puis `python3 render.py episodes/<dossier>`.

## Police « façon GTA » (choisie le 14/11 pour l'épisode Take-Two / GTA 6)
`fonts/PassionOne-Black.ttf` (licence libre OFL, `fonts/OFL_PassionOne.txt`) : minuscules très grasses, texte blanc, contour violet-noir épais, ombre portée, sur dégradé coucher de soleil rose-orange vers violet. Remplace Pricedown (police d'origine de GTA), dont la licence gratuite interdit l'usage sur serveurs et services cloud. Pas de flèche « → » dans la police : utiliser un autre glyphe ou la dessiner. Ne jamais reproduire le logo GTA, ses personnages ni ses visuels officiels.

## Décors générés : affinage systématique (validé par Nicolas le 13/11)
Toute vidéo à décors générés (Gemini / Veo, 720×1280) passe par trois étapes avant le rendu, dans cet ordre :
1. `python3 sr_decors.py` : agrandissement Real-ESRGAN ×4 (modèle `lib/sr/realesr_animevideov3.onnx`, onnxruntime, sans PyTorch) puis ramené en 1080×1920, uniquement sur les images utilisées ; sortie `decors/sr/`.
2. `python3 decors_hd.py` : ralenti à la vitesse du passage puis interpolé en 60 i/s (minterpolate) ; sortie `decors/hd/`.
3. `VIDEO=video_col.py python3 render.py episodes/<dossier> --budget 7000 --workers 1`.
Les deux scripts sont dans `episodes/2026-11-14_millionnaire/` : les copier dans le nouvel épisode (ils lisent `BLOCS` de `video_col.py`). Compter environ 6 s par image sur la machine à 2 processeurs, soit à peu près 2 h pour six décors : lancer en tâche de fond avec le délai maximal ; en cas d'arrêt, relancer, chaque étape reprend où elle s'était arrêtée. Prévenir Nicolas de ce délai pour qu'il dépose les décors tôt. `APERCU=1` utilise les décors d'origine pour les maquettes.
Effet pellicule : pas d'ondulation de toute l'image, scintillement léger (0,010).
