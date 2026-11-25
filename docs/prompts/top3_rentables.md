Épisode : vidéo du jeudi 26/11/2026, « Top 3 des entreprises les plus rentables de France », TikTok et Instagram Reels.

PREMIÈRE RÉPONSE, avant tout le reste :
1. Clone le dépôt nicolas-laur/actions_benefices.
2. Lis CLAUDE.md, docs/retours.md, docs/formats/video_1930.md et mister_coin/README.md, puis jette un œil à episodes/2026-11-25_black_friday (dernier épisode, pipeline à reprendre : nettoie_rue.py, sr_lance.py, interp_flow.py, interp_pan.py, hd_lance.py, video.py, video_col.py, mix.py, rendu.py, couverture.py avec lib/gros_plan.py).
3. Fais une recherche rapide et sourcée (derniers comptes annuels publiés, exercice 2025, et premiers chiffres 2026 si disponibles) et propose-moi l'angle en 5 lignes : l'accroche (« question »), le fil rouge chiffré, les 3 entreprises montrées, le repère qui fait réagir et la chute.
4. Pose tes questions à la fin de cette première réponse, en particulier sur la définition de « rentable » : bénéfice net le plus élevé en euros, ou marge nette (bénéfice pour 100 € de ventes), ou rentabilité des capitaux propres. Montre-moi le classement obtenu avec chaque définition pour que je choisisse.

Le fond du sujet :
- Le classement, daté et sourcé (rapports annuels, communiqués de résultats), entreprises cotées en France.
- Pour chacune : ce qu'elle fait en une phrase, le chiffre clé, d'où vient l'argent, et un repère à hauteur de spectateur (par exemple : combien elle gagne par seconde, ou sur 100 € que tu dépenses chez elle, combien lui reste).
- Le lien avec notre ligne : être actionnaire, c'est posséder un morceau de ces bénéfices (dividendes, rachats d'actions), sans conseil en investissement ni avis sur l'action.
- Leçon du bilan Metricool du 25/11 : les vidéos qui décollent sur Instagram sont celles qu'on enregistre. Tester une incitation discrète à enregistrer ou partager dès le début de la vidéo, et laisser le chiffre clé assez longtemps à l'écran.
- La chute : une question au spectateur (« Et toi, tu en as dans ton portefeuille ? » ou une variante), sans blague sur la question finale.

Leçons des dernières vidéos :
- Le « toi » dès la première phrase, l'accroche « question ».
- Un fil rouge visuel fort (gratte-ciel et cadran d'ascenseur, étiquette géante du rayon ont bien marché) ; texte posé sur un objet du décor : suivi par points sur tout le passage, jamais une détection par image.
- Durée cible 60 à 75 s, sans dépasser 80 s.
- Décors : mouvements de caméra lents, sens du mouvement vérifié, interpolation 60 i/s par flux optique (interp_flow.py), ou par translation (interp_pan.py) pour un travelling latéral sur textures répétitives ; enseignes et pseudo-lettres effacées.
- Mister Coin : pendant un travelling, il marche de face en parlant (clips danse_parle_*, joués vers l'avant avec VeoCoin(..., boucle=…)) ; assis au bord d'un objet, bord suivi image par image.

Règles :
- Format 1930 Technicolor habituel : décors Gemini, Mister Coin présent tout du long (banque mister_coin/veo/ et poses mister_coin/poses/), sous-titres mot à mot, zone sûre respectée, 9:16 natif 1080×1920, export CRF 15 / 16 Mb/s.
- Informations dans nos plaques de verre 3D, bien espacées, pas de rouge dans le verre, police Inter Display.
- Logos des entreprises seulement si je les autorise (dossier logos/ de l'épisode).
- Chiffres exacts, datés et sourcés dans sources.md ; montants en euros.
- Pas de conseil fiscal ni d'investissement, pas de prise de position politique ; mention pédagogique à la fin.
- Script pour la voix avec les nombres en toutes lettres et sans balise de silence ; je génère la voix moi-même (voice_full.wav en 48 kHz mono). Prévoir un script d'environ 200 mots : la voix de Thomas lit environ 3 mots par seconde.

Ordre de travail :
1. Angle et questions (première réponse).
2. Script à valider (texte affiché et texte voix).
3. Prompts Gemini des décors dans un fichier MD (bloc commun et un bloc par décor, vidéo verticale 9:16 native, mouvements de caméra lents), plus les clips ou poses de Mister Coin qui manqueraient.
4. Je génère la voix et les décors, tu les intègres.
5. Maquettes (images clés de chaque scène) à valider avant tout rendu.
6. Rendu complet et vérification (images clés, fluidité des décors, transitions, son).
7. Couverture (gros plan de Mister Coin via lib/gros_plan.py), description TikTok, légende Instagram et sources pour le premier commentaire.
8. Commit et push, puis roadmap (artefact EaRZLV81jk3EdfSYcU4t42, collection videos) en statut « publié » une fois que j'aurai publié.
