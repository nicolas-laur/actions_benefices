# Actions_Bénéfices : mémoire du projet (état au 28 octobre 2026)

Ce document rassemble tout ce qui a été décidé, produit et appris depuis le début du projet. Il complète `CLAUDE.md` (consignes de production), `mister_coin/README.md` (kit historique de la mascotte) et l'historique Git.

## 1. La chaîne

Actions_Bénéfices publie des vidéos courtes de vulgarisation bourse et finance personnelle, au format vertical 1080×1920. Les comptes sont @actions_bnfices sur TikTok, actions_benefices sur Instagram et une chaîne YouTube Shorts, tous trois suivis dans Metricool (marque « actions_bnfices », plan gratuit).

L'objectif est de devenir une chaîne à succès qui produit un contenu de qualité et fédère son audience. Le parti pris visuel est la 3D et le motion design soigné, pour se démarquer des chaînes concurrentes en 2D à voix robotique. Nicolas est très exigeant : pas de flou, pas de gadget, pas de basse qualité, et un niveau d'exigence élevé à chaque version.

Nicolas propose la direction artistique (DA) de chaque vidéo, génère lui-même la voix (Thomas, ElevenLabs) à partir du script, génère les décors et les clips de Mister Coin dans Gemini, et publie à la main sur les trois réseaux à 19 h. Claude écrit et vérifie les scripts, prépare les prompts, monte la vidéo (décors animés, graphiques, sous-titres, Mister Coin, son), produit la couverture et les textes de publication, et analyse les statistiques.

## 2. Outils et emplacements

- Dépôt GitHub : `nicolas-laur/actions_benefices` (cloné dans `/home/claude/actions_benefices` en session). Chaque épisode vit dans `episodes/<date>_<sujet>/` avec `video.py`, `mix.py`, `decors/`, `couverture.py`, `description.txt`, `sources.md`, la voix et les sorties dans `out/`.
- Plan éditorial publié (artefact) : https://claude.ai/artifact/EaRZLV81jk3EdfSYcU4t42. Base de données : collection `videos` (une fiche par vidéo, `v<date>` pour le plan, `h00`…`h13` pour l'historique, `b…` pour les bilans) et collection `meta` (`compte` = abonnés TikTok, `instagram` = abonnés, vues par jour, `succes`). La page affiche les phases, les succès, une section Instagram et le calendrier ; les stats TikTok et Instagram de chaque vidéo s'y saisissent.
- Rendu : `python3 render.py episodes/<dossier>` (par tranches de 120 images, reprenable ; relancer jusqu'à « TERMINÉ »). Avec 6 clips de Mister Coin ou plus, utiliser `--workers 1` (la mémoire ne suffit pas à deux processus) ; compter environ 55 min pour 60 s.
- Le Mac de Nicolas peut servir au rendu via le pont de l'application de bureau, dans `$HOME/mnt/projects/actions_benefices`, quand il est connecté.
- ElevenLabs refuse les générations lancées par Claude : la voix vient toujours de Nicolas. Aucune reconnaissance vocale n'est disponible (hôtes bloqués) : les sous-titres sont calés à partir des silences de la voix et du nombre de syllabes.
- Nicolas ne veut ni programmation via Metricool (plan payant), ni connexion supplémentaire.

## 3. Règles de production

Elles sont dans `CLAUDE.md`, à relire avant chaque vidéo. En résumé :

- Vidéo 1080×1920 native, export CRF 15 / 16 Mb/s, pas de barre de progression.
- Chiffres exacts et sourcés (`sources.md`), euros au taux BCE, indices hors dividendes précisés, formulations rigoureuses (exemple du 28/10 : l'État est « celui qui encaisse le plus », pas « le plus gros gagnant », car une taxe n'est pas une marge et le poste produit pèse plus lourd que les taxes).
- Aucun logo de marque réelle. Logo de la chaîne : `lib/logo.py`.
- Chiffre choc visible à l'image 0. Sous-titres phrase par phrase avec mot clé surligné, toujours lisibles.
- Zone sûre (à partir de Novo Nordisk) : rien d'important sous y = 1500 ni au-dessus de y = 200 ; rien à droite de x = 950 entre y = 1000 et 1700 ; sous-titres vers y ≈ 1035-1060, lignes de 760 px au plus ; Mister Coin dessous, pieds vers y ≈ 1650-1700.
- Musique douce, bruitages discrets ; émojis Noto bienvenus.
- Script pour la voix : nombres en toutes lettres, tutoiement du spectateur.
- Livrables : vidéo (avec et sans musique), couverture, description TikTok, titre YouTube Shorts, légende Instagram, sources du premier commentaire. Cocher « contenu généré par IA ».
- Couvertures : DA historique (fond noir, rubans de lumière aux couleurs du sujet, nom épuré, « Et toi, tu achètes ? » sauf pour les sujets « utiles »), Mister Coin dessus.

Exigences ajoutées le 27-28/10 (retours sur la vidéo carburant) :

- Contrôle complet par Claude avant tout envoi : mesure de l'écart entre images successives sur toute la vidéo (pour détecter sauts et coupures), vérification image par image des transitions, du compteur, des sous-titres.
- Mister Coin : jamais de fondu entre deux poses différentes (double image), jamais de saut d'image.
- Décors animés sans coupure ni clignotement brusque.
- Objets réels animés comme dans la réalité (compteur de pompe à débit régulier).
- Graphiques précis et design, avec un son satisfaisant quand ils évoluent ; panneaux qui changent de contenu en fondu enchaîné, jamais d'un coup.

## 4. Mister Coin

Pièce d'or cartoon années 30 : haut-de-forme, nœud papillon, gants blancs. Présentateur permanent, taille constante, pas de gros plan ; il illustre le propos et apporte de l'âme ; ses mains restent dans le cadre ; rien du décor ne passe devant lui ; bulles de BD courtes accrochées à lui ; pas de blague sur la question finale.

Méthodes successives :

1. Marionnette découpée à partir de 9 dessins Gemini (`puppet.py`, `rig.py`, `mister_coin.py`, poses gros/mince/bling…), utilisée jusqu'à Kering.
2. Rig dessiné en code (`rig2.py`, `coin2.py`) : abandonné le 26/10 (« c'est moins bien »).
3. Méthode retenue le 27/10 : banque de clips Gemini (Veo) sur fond vert, détourés et montés par `mister_coin/veo_coin.py`.

Génération des clips (Nicolas, dans Gemini) : format 16:9, image de référence à marges (`mister_coin/veo/classique_reference_marges_16x9.jpg`, `aristocrate_reference_marges_16x9.jpg`), bloc de prompt commun (pieds au sol quand il parle, il parle du début à la fin, pose neutre au début et à la fin, grandes marges vertes). Objectif : 26 clips classiques.

Chaque clip déposé dans `mister_coin/veo/` est analysé par `python3 mister_coin/veo_catalogue.py` (taille, position, plages de parole et de silence) puis vérifié à l'œil (noms parfois inversés à la livraison, plages à corriger). `veo/catalogue.json` fait foi.

Montage (`VeoCoin(..., lisse=True)`, version du 27-28/10) :

- Il parle quand la voix parle (images de parole) et revient à sa pose neutre dans les silences, en jouant les images qui y mènent.
- Le planning fixe l'humeur par passage : liste `(début, clips autorisés, 'voix')`, changements placés dans des silences.
- Dans un même clip, une reprise de parole ne repart d'une autre image que si la pose est quasi identique (comparaison des silhouettes).
- Entre deux clips (humeur, ou variété après 8 s), coupe franche au sommet d'un petit saut sur place, avec un « boing » discret. Les poses neutres des clips ne se superposent pas, d'où ce choix.
- Les réactions (`type: reaction` dans le catalogue) se jouent d'un bloc dans un silence, jamais pour parler.
- Mise à l'échelle commune sur la hauteur du personnage, ombre au sol qui rétrécit en l'air.

Banque au 28/10 (9 clips classiques sur 26) :

- Parole : `classique_parle_enthousiaste`, `classique_parle_explique`, `classique_parle_inquiet`, `classique_parle_triste`, `classique_parle_confidence` (main devant la bouche, pour une révélation), `classique_parle_question` (haussement d'épaules, bras ouverts).
- Réactions : `classique_saut_place` (format portrait, élan, saut, réception), `classique_joie` (saute de joie, bras en l'air). Il faut 4 à 5 s de silence prévu dans le script pour les placer.
- Entrée : `clip_b` (entrée par la gauche, ancienne génération).
- Tenue aristocrate (Hermès) : `aristo_parle_neutre`, `aristo_parle_enthousiaste_16x9`, `aristo_parle_explique` (images 88-130 exclues : troisième main), `aristo_entre_gauche` ; `aristo_parle_enthousiaste` (portrait) rejeté, mains coupées.
- Images de référence : `aristocrate_reference_hd.jpg`, `*_reference_marges_16x9.jpg`.

Le texte complet des 26 prompts Gemini, avec le statut de chaque clip, est dans `mister_coin/veo/PROMPTS_GEMINI.md`.

## 5. Épisodes produits

- Avant le 23/10 : LVMH, Air Liquide, Nvidia, Microsoft, Amazon, Apple, Visa, Google, Tesla, McDonald's, Netflix, Bitcoin, Micron, SpaceX (historique), puis Krachs ép. 1 (2008), Meta, Intel, Coca-Cola, PEA ou compte-titres, actu Netflix/Tesla/Meta (première vidéo avec Mister Coin).
- 24/10 Krachs ép. 2 (bulle internet). 25/10 Novo Nordisk (laboratoire, Mister Coin gros puis mince). 26/10 AMD (ville futuriste vue de haut, gag du cri Wilhelm réel de La Sonothèque ; voix rééchantillonnée à 48 kHz pour corriger l'effet « hélium »). 27/10 Kering (Gucci ; tenue bling révélée par surprise à une sortie de champ ; couverture avec Mister Coin et son sac de billets, sous-titre des marques du groupe).
- 28/10 Hermès (v6) : atelier 1837, avion 1984 (Birkin), salon, bibliothèque (camembert 3D LVMH vs famille), salle de Bourse ; Mister Coin aristocrate qui saute de scène en scène ; couverture avec Mister Coin aristocrate et sa canne.
- 29/10 Carburant (v5, prête) : « 118 € le plein de gazole, où part ton argent ? ». Vue du ciel d'une station néo-rétro aux néons rouges (voix off d'ouverture), plongée de caméra jusqu'à la pompe, Mister Coin qui tombe du ciel. Compteur de pompe en afficheur 7 segments rouge néon qui grésille et tourne à débit régulier jusqu'à 117,78 € pour 50,00 L. Tableau de décomposition à gauche (barre empilée graduée, une ligne par poste, total) : pétrole et raffinage 53,35 €, transport et station 14,42 €, accise 30,38 €, TVA 19,63 €, État 50,01 € (42 %) ; paradoxe 54 % → 42 % de taxes en un an. Humeurs de Mister Coin selon le propos (enthousiaste, inquiet, confidence, triste, question). Sources DGEC (semaine du 2 octobre), Kelwatt, Transitions & Énergies ; partage brut/raffinage estimé (≈ 43 € / ≈ 10 €).

## 6. Statistiques et analyse (relevé du 27/10)

- Abonnés : TikTok 15, Instagram 89 (dont +61 le 26/10, jour de la pub Instagram sur les reels PEA et Novo Nordisk), YouTube 1.
- TikTok : plafond de 800 à 950 vues par vidéo jusqu'au 21/10 ; creux à environ 250 vues du 22 au 25 ; reprise avec AMD (764) et Kering (429 en quelques heures) après le passage à 19 h. Le temps de visionnage TikTok n'est pas remonté par Metricool : le relever dans TikTok Studio.
- Instagram : meilleurs reels Intel (1 184 vues) et Coca-Cola (22 likes, 5 enregistrements, 8 partages) ; visionnage moyen de 8 à 14 s ; les contenus utiles se font enregistrer et partager.
- YouTube : aucun Short visible dans Metricool après le 23/10 ; à vérifier dans YouTube Studio.
- Les promotions Instagram ne sont pas visibles dans Metricool (Meta Ads non connecté) : demander le bilan à Nicolas pour calculer le coût par abonné, et promouvoir plutôt un reel qui retient déjà bien.
- Les vidéos Mister Coin durent 60 à 85 s alors que le plan prévoyait 25 à 35 s : à trancher avec les chiffres de visionnage.
- Point d'étape prévu le 1er novembre (fin de la phase 1).

## 7. Idées et tests à faire

- Test 15 s : décliner une vidéo longue en 2 ou 3 vidéos de 15 s (un fait par vidéo, chiffre choc à 0 s, chute ou boucle à la fin, 35 à 40 mots), même décor et mêmes clips ; premier candidat le carburant (« l'État prend 50 € sur ton plein », « la TVA sur la taxe »).
- Carrousel Instagram (validé) : version carrousel du carburant publiée le lendemain de la vidéo, 8 images (118 € le plein, pétrole, transport et station, accise, TVA sur la taxe, total État, paradoxe des 42 %, question + « enregistre-le ») ; à tester aussi en carrousel photo sur TikTok.
- Prévoir dans les scripts des silences de 4 à 5 s pour placer les réactions de Mister Coin (joie, saut).
