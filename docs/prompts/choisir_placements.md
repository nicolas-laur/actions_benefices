Épisode : vidéo « Comment bien choisir ses placements ? » (titre de travail : « La bourse, ce n'est pas la roulette »), TikTok et Instagram Reels. Date de publication à fixer avec moi. Le sujet n'est pas encore dans la roadmap : crée le document s-choisir-placements dans la collection videos (statut « idée », format 1930).

PREMIÈRE RÉPONSE, avant tout le reste :
1. Clone le dépôt nicolas-laur/actions_benefices.
2. Lis CLAUDE.md, docs/retours.md, docs/formats/video_1930.md, mister_coin/README.md et lib/coin_integration.py, puis regarde episodes/2026-11-28_patrimoine_age (dernier épisode, gros succès : pipeline à reprendre tel quel, video.py, video_col.py, sr_tout.py, hd_lance.py, interp_flow.py, mix.py, rendu.py, couverture.py, suivi des surfaces) et docs/fiches_entreprises.md (la méthode de nos fiches « Que vaut… ? », que la vidéo présente sous forme générale).
3. Recherche rapide et sourcée, uniquement pour ce qui sera affirmé comme un fait : ce que mesure le PER et ses ordres de grandeur, l'intérêt de la diversification et de l'horizon de placement (par exemple, la part des périodes de 1, 10 et 20 ans en perte sur un indice mondial, avec l'indice, la période et la source précisés, hors ou avec dividendes).
4. Propose-moi l'angle en 5 lignes : l'accroche (« question »), le fil rouge visuel, les 6 critères, le passage diversification et horizon, la chute.
5. Pose tes questions à la fin de cette première réponse, en particulier la date de publication et les chiffres d'exemple de l'entreprise fictive.

Décisions déjà prises avec moi (28/11) :
- Méthode générale avec des chiffres d'exemple (entreprise fictive, aucune vraie marque ni vrai ticker), pas de démonstration sur une vraie entreprise.
- 6 critères : l'entreprise (ce qu'elle vend, à qui), ses ventes et bénéfices dans le temps, sa dette, son prix par rapport à ses bénéfices (PER expliqué par un exemple simple), son secteur et ses concurrents, l'actualité qui peut tout changer.
- Diversification et horizon de placement mentionnés : ce sont les garde-fous du particulier.
- Message : on ne supprime pas le risque, on met toutes les chances de son côté. Formule retenue : « savoir pourquoi tu achètes, et ce qui te ferait changer d'avis ». Jamais de promesse de gain ni « acheter en toute confiance ».

Fil rouge visuel :
- Une roulette de casino 1930 : les joueurs misent au hasard, Mister Coin recule (« Moi, je ne joue pas, je regarde »). Le cylindre de la roulette devient un cadran de contrôle ; chaque case qui s'allume est un des 6 critères, avec sa plaque de verre.
- La bille ne tombe jamais « toujours sur son pari » (image refusée : elle promettrait un gain certain).
- Chute possible : « La roulette, c'est le hasard. La bourse, c'est du risque : tu ne le supprimes pas, tu le choisis. Et toi, tu regardes quoi avant d'acheter ? » (ou mieux).

Leçons du 28/11 à appliquer d'emblée :
- Mister Coin intégré partout par lib/coin_integration.py : clips en 60 i/s par flux optique, pieds verrouillés sur une surface suivie (poser_au_sol), ombre, reflet, lueur, light wrap, même lumière en l'air qu'au sol. Il se tient sur une vraie surface du décor (tapis vert de la table de jeu, rebord du cylindre, comptoir) ; prompts de décor avec une surface brillante et assez profonde sous ses pieds pour le reflet.
- Vidéos Gemini : mesurer le mouvement image par image avant de les utiliser (fondus parasites, sauts de plan, accélérations) et ne garder que les plages saines ; un saut de plan peut se cacher sous un saut de Mister Coin.
- Compteurs : la valeur exacte est atteinte au moment où la voix commence à la dire, jamais après.
- Pictogrammes et textes des plaques : texte aligné à gauche après le pictogramme, jamais de chevauchement ; vérifier chaque plaque à chaque apparition.
- Couverture : couleurs vives (le gabarit n'assombrit que derrière le texte), fond où l'objet du fil rouge se reconnaît, Mister Coin à 78 % de la largeur ; vérifier les mains en taille réelle (plusieurs poses sont coupées au bord, voir docs/retours.md).
- Le « toi » dès la première phrase, accroche « question », invitation aime / enregistre / commente en grand dès le début.

Règles :
- Format 1930 Technicolor habituel : décors Gemini, Mister Coin présent tout du long (banque mister_coin/veo/ et poses mister_coin/poses/), sous-titres mot à mot, zone sûre respectée, 9:16 natif 1080×1920, export CRF 15 / 16 Mb/s. Durée cible 60 à 75 s, sans dépasser 80 s.
- Informations dans nos plaques de verre 3D, bien espacées, pas de rouge dans le verre, police Inter Display.
- Aucun logo de marque ; casino sans enseigne ni nom réel, pseudo-lettres effacées.
- Chiffres exacts, datés et sourcés dans sources.md ; montants en euros ; chiffres d'exemple signalés comme tels à l'écran (« exemple »).
- Pas de conseil fiscal ni d'investissement, pas de prise de position politique ; mention pédagogique à la fin.
- Script pour la voix avec les nombres en toutes lettres et sans balise de silence ; je génère la voix moi-même (voice_full.wav en 48 kHz mono). Environ 200 mots : la voix de Thomas lit environ 3 mots par seconde. Citer la source à la voix pour les chiffres réels.

Ordre de travail :
1. Angle et questions (première réponse).
2. Script à valider (texte affiché et texte voix).
3. Prompts Gemini des décors dans un fichier MD (bloc commun et un bloc par décor, vidéo verticale 9:16 native, mouvements de caméra lents), plus les clips ou poses de Mister Coin qui manqueraient.
4. Je génère la voix et les décors, tu les intègres.
5. Maquettes (images clés de chaque scène et transitions, pieds vérifiés en gros plan) à valider avant tout rendu.
6. Rendu complet et vérification (images clés, fluidité des décors, transitions, lumière de Mister Coin, compteurs calés sur la voix, son).
7. Couverture (gros plan de Mister Coin via lib/gros_plan.py), description TikTok, légende Instagram et sources pour le premier commentaire.
8. Commit et push (boucle de 5 essais), puis roadmap (artefact EaRZLV81jk3EdfSYcU4t42, collection videos, document s-choisir-placements) : date et statut mis à jour, « publié » une fois que j'aurai publié.
