# Site actionsbenefices.com : chantiers ouverts

## Affichage mobile (chantier du 25/11, fait)
Tout le réglage téléphone est dans `site/assets/css/mobile.css` (chargé après theme.css), vérifié en 390 et 360 px, modes clair et sombre, et sur ordinateur (inchangé) :
- En-tête sur une ligne (marque, « La lettre », ☰) ; le panneau du menu contient les rubriques, la lettre du dimanche et le choix clair/sombre (theme.js).
- Accueil centré ; pièces décoratives masquées sur téléphone quand elles recouvrent un texte (theme.js) et retirées du récit épinglé.
- Graphiques : sous 760 px, chaque SVG de `composants.py` est doublé d'une version en barres horizontales (`g-bureau` / `g-mobile`). Barres empilées : 8 derniers trimestres environ et bouton « Voir les N trimestres » ; flux : aperçu à toucher pour l'ouvrir en grand, puis deux barres empilées. Tout nouveau graphique passe par ces fonctions pour avoir sa version téléphone.
- Tableaux : une carte par ligne, intitulés de colonne ajoutés par `build.py` (`cartes_tableaux`, attribut data-l).
- Courbes des calculateurs : tracées à la largeur réelle sous 600 px (calculateurs.js, perf.js).
- Vidéos et termes du lexique sur deux colonnes.
- Typographie (build.py, `insecables`) : espace insécable avant ? ! : ; », après « et entre un nombre et €, %, $.
Reste à faire :
- Tester sur un vrai téléphone (iPhone et Android) : infobulles au toucher, vue en grand du flux, menu.
- Logo Amazon des rivaux d'Alphabet (`assets/img/amzn.png`, 80 px pour 48 affichés) : en fournir un de 96 px ou plus.
- Contrôle automatique : scripts de captures et de débordements utilisés le 25/11, rangés dans `site/outils/mobile/` (vue.py pour les captures, final.py pour les débordements, textes trop petits et images sous 2×).

## Mise à jour des News et des vidéos (à chaque vendredi)
1. Rendre le carrousel : `cd episodes/<date>_les_news && python3 carrousel.py planche` (pycairo requis).
2. `python3 site/outils/extraire_news.py` puis `python3 site/outils/ecrire_news.py` : diapos en webp, données de `site/contenu/news.py` (ajouter la semaine dans `SEM` d'ecrire_news.py et le dossier dans extraire_news.py).
3. Vidéos : ajouter la ligne (liens relevés dans Metricool) dans `site/outils/videos.py`, relancer, recopier la liste dans `site/contenu/donnees.py`.

## À vérifier en ligne
- Lecteurs TikTok et Instagram intégrés (non testables hors ligne) : un carrousel TikTok (« photo ») et un Reel.
- Pas de couverture dans le dépôt pour les vidéos du 15 au 27/10 : vignette Mister Coin à la place, à remplacer si Nicolas fournit les couvertures.

## Référence UX (22/11) : https://more-nutrition.webflow.io/
Nicolas aime l'UX et le fonctionnement de ce site et veut s'en inspirer. À étudier dans le navigateur (le site refuse la lecture automatique) avant le chantier mobile : relever les motifs (navigation, animations au défilement, cartes, éléments fixes, transitions) et proposer ceux qui conviennent à Actions Bénéfices, maquettes à l'appui.

## Animations et sons de Mister Coin
`python3 site/outils/clips_coin.py` (clips Veo → assets/anim/*.webp et *.mp3) puis `python3 site/outils/sons.py` (bruitages + volume des clips). Toujours dans cet ordre.

## Données de marché
`site/outils/marches.py`, lancé chaque nuit par le workflow ; dernier relevé sur la branche `donnees` (secours si Yahoo ne répond pas). Pour travailler en local : `git fetch origin donnees && git show origin/donnees:marches.json > site/donnees/marches.json`.
