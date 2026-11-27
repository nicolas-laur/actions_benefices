# Format vidéo « 1930 » (Mister Coin, décors Gemini) — à lire avant toute vidéo de ce style

## Banque de clips Mister Coin (Gemini / Veo), méthode retenue le 27/10
- Nicolas génère les clips dans Gemini, en 16:9, avec l'image de référence à marges (`mister_coin/veo/*_reference_marges_16x9.jpg`) et le bloc de prompt commun (pieds au sol quand il parle, parle du début à la fin, pose neutre au début et à la fin, grandes marges).
- Chaque clip déposé dans `mister_coin/veo/` est analysé par `python3 mister_coin/veo_catalogue.py` (taille, position, plages où il parle / se tait) ; `veo_coin.py` les monte : il parle quand la voix parle, se tait dans les silences, change de clip en plein saut entre deux scènes. Détails : `mister_coin/README.md`, prompts : `mister_coin/veo/PROMPTS_GEMINI.md`.
- Éviter la répétition : un clip de parole différent par scène, réactions (joie, déception, choc…) dans les silences, jamais le même geste deux fois de suite. Prévoir 4 à 5 s de silence dans le script pour placer une réaction.
- Formats légers (recherche, 15 s ; décidé le 01/11) : Mister Coin présent mais avec 2 ou 3 clips seulement.
- Jamais de fondu entre deux poses différentes (double image) ni de saut d'image. Dans un clip, il rejoint la pose voulue en jouant les images ; entre deux clips, coupe franche pendant un petit saut sur place (`VeoCoin(..., lisse=True)`).
- Détourage : `VC._key` de `mister_coin/veo_coin.py` ; images recadrées à sd = h·0,62, y0 = h·0,21.

## Décors générés : affinage systématique (validé par Nicolas le 13/11)
Toute vidéo à décors générés (Gemini / Veo, 720×1280) passe par trois étapes avant le rendu, dans cet ordre :
1. `python3 sr_decors.py` : agrandissement Real-ESRGAN ×4 (modèle `lib/sr/realesr_animevideov3.onnx`, onnxruntime, sans PyTorch) puis ramené en 1080×1920, uniquement sur les images utilisées ; sortie `decors/sr/`.
2. `python3 decors_hd.py` : ralenti à la vitesse du passage puis interpolé en 60 i/s (minterpolate) ; sortie `decors/hd/`.
3. `VIDEO=video_col.py python3 render.py episodes/<dossier> --budget 7000 --workers 1`.
Les deux scripts sont dans `episodes/2026-11-14_millionnaire/` : les copier dans le nouvel épisode (ils lisent `BLOCS` de `video_col.py`). Compter environ 6 s par image sur la machine à 2 processeurs, soit à peu près 2 h pour six décors : lancer en tâche de fond avec le délai maximal ; en cas d'arrêt, relancer, chaque étape reprend où elle s'était arrêtée. Prévenir Nicolas de ce délai pour qu'il dépose les décors tôt. `APERCU=1` utilise les décors d'origine pour les maquettes.
Effet pellicule : pas d'ondulation de toute l'image, scintillement léger (0,010).

## Intégration de Mister Coin (obligatoire depuis le 27/11)
Toute scène avec Mister Coin utilise `lib/coin_integration.py` : `fluidite60` sur les clips Veo (24 → 60 i/s, couleur et alpha), `suivi_surface` pour accrocher ses pieds à la surface du décor pendant les travellings, `integrer` pour la lumière (teinte de la scène, lueur et flaque dorées, reflet coupé au bord de la surface, ombre de contact, light wrap, liseré chaud). `reflet=False` sur les surfaces mates. Exemple : `episodes/2026-11-28_patrimoine_age/test_anim.py`. Dans les prompts de décor, demander une surface brillante (parquet ciré, bois verni, laiton poli) assez profonde sous ses pieds.

## Rendu
- Aperçus : `python3 video.py png …` (une image par scène et chaque transition), maquettes envoyées à Nicolas avant tout rendu complet.
- Tranches de 120 images dans `tmp/chunks/c%06d.mp4` ; supprimer les tranches ou `mix.wav` pour forcer une reprise. Les tâches de fond meurent à 2 h : relancer, le rendu reprend.
- Mixage : ambiances par bloc (`BLOCS_MIX` de `video_col.py`), voix en 48 kHz mono.
- Épisode modèle le plus récent : `episodes/2026-11-16_loto/` (accroche refaite et recalée sur la voix, fondus enchaînés entre scènes, plongée dans une foule de Mister Coin `zoom_foule.py`).

## Exigences retenues (retours du 27/10 sur la vidéo carburant)
- Décors animés : pas de coupures ni de clignotements brusques (néons, lumières) ; mouvements lents et continus.
- Objets du réel animés comme dans la réalité (ex. compteur de pompe qui tourne à débit régulier, sans remise à zéro).
- Graphiques soignés (matière, reflets, dégradés, étiquettes reliées), apparition et disparition en fondu, accompagnés d'un son satisfaisant quand ils évoluent.
