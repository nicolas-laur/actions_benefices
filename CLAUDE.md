# Consignes pour Claude — Actions_Bénéfices

Langue : français, tutoiement, prose structurée, peu de gras, pas de tirets cadratins. Poser les questions avant un livrable complexe.

## En début de session (une session par épisode)
Lire `docs/retours.md` (leçons et retours de Nicolas), puis la fiche du format concerné : `docs/formats/video_1930.md` (vidéos Mister Coin et décors Gemini), `docs/formats/gta.md` (DA GTA, Take-Two), `docs/formats/carrousel.md`. Historique général : `MEMOIRE_PROJET.md` ; mascotte : `mister_coin/README.md` ; planning : roadmap (artefact https://claude.ai/artifact/EaRZLV81jk3EdfSYcU4t42, collection `videos`).

## Règles de production (validées par Nicolas)
- Format 9:16 natif 1080×1920, export CRF 15 / 16 Mb/s. Pas de barre de progression en haut.
- Chiffres exacts et vérifiés (sources dans `sources.md`), montants en euros convertis au taux BCE, indices hors dividendes précisés.
- Aucun logo de marque réelle, sauf ceux que Nicolas fournit ou demande pour un contenu (dossier `logos/` de l'épisode, tuiles tirées des favicons ou du jeu « logos » d'Iconify) ; le logo de la chaîne est `lib/logo.py` (ne pas le modifier).
- Accroche : « question » ou « chiffre choc à l'image 0 » (test depuis le 01/11, notes dans la roadmap). Sous-titres mot à mot, mot clé surligné, toujours lisibles, jamais de texte sur du texte.
- Zone sûre des applis : rien d'important sous y = 1500, ni au-dessus de y = 200, ni à droite de x = 950 entre y = 1000 et 1700. Sous-titres vers y ≈ 1035–1060, ligne de 760 px max ; Mister Coin dessous, pieds vers y ≈ 1650.
- Musique douce, bruitages discrets. Émojis Noto bienvenus.
- Script pour la voix : nombres en toutes lettres ; Nicolas génère la voix (ElevenLabs refuse la génération depuis Claude). `voice_full.wav` toujours en 48 kHz mono (`ffmpeg -i voix_src.mp3 -ac 1 -ar 48000 voice_full.wav`).

## Mister Coin
Présent tout du long, taille constante, pas de gros plan ; mouvements lents ; grimaces et joie seulement dans les silences ; ses deux mains dans le cadre ; rien du décor devant lui ; bulles courtes accrochées à lui, jamais sur un texte important ; pas de blague sur la question finale.

## Avant chaque rendu
Envoyer les maquettes (images clés de chaque scène) et attendre la validation de Nicolas (05/11). Vérifier soi-même chaque version : images clés, transitions, son.

## Publication
Nicolas publie lui-même, à la main, sur TikTok et Instagram Reels (plus sur YouTube depuis le 18/11 : ne plus produire de titre ni de description YouTube). Livrables : la vidéo, la couverture, la description TikTok, une légende Instagram et les sources pour le premier commentaire.

## Dépôt
Commits terminés par les lignes d'attribution de la session ; pousser avec une boucle de 5 essais (`git push` puis comparaison avec `git ls-remote`).
