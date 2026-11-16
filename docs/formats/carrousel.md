# Carrousels (News du vendredi, lexique, thématiques)
- Gabarit : `lib/carrousel.py`. Un épisode = un `carrousel.py` court qui fait `from carrousel import *`, décrit ses diapos et appelle `sortie(render, NS)`. Exemple : `episodes/2026-11-17_lexique/carrousel.py` ; News : `episodes/2026-11-13_les_news/` (ancien script autonome, encore valable).
- Dossier de l'épisode : `fonds/fond_<nom>.jpg` (repris des décors affinés des vidéos), `coin/<pose>.png` (choc, facepalm, inquiet, joie, montre, pouce, question, rire, triste), `logos/PROFIL.png` et logos autorisés.
- Sorties : `out/tiktok_N.png` (1080×1920) et `out/instagram_N.png` (4:5, recadrage y = 175…1525) ; planche de contrôle `prev/planche.png` (`python3 carrousel.py planche`).
- Mise en page : contenu entre y = 200 et 1500 ; rien à droite de x = 950 entre y = 1000 et 1700 (la bulle de Mister Coin passe sur deux lignes avec « | » si besoin) ; cadres de verre espacés de GAP = 58 ; pas de points de pagination (les réseaux les affichent) ; jamais de texte sur du texte ; logos en bulle ronde.
- Dernière diapo : question d'engagement, « enregistre-le », `bloc_abonne`, `mention_pedago`.
- Vérifier la planche puis au moins une diapo en pleine taille avant d'envoyer.
