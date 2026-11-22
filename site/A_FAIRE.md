# Site actionsbenefices.com : chantiers ouverts

## Affichage mobile (priorité, retour de Nicolas du 21/11 : « pauvre, à corriger »)
Travail dédié à conduire, page par page, en 390 px de large (iPhone) et 360 px (Android) :
- En-tête : le menu de 6 rubriques et le bouton « La lettre du dimanche » s'empilent ; prévoir un menu repliable (bouton ☰) et un en-tête compact.
- Héros : Mister Coin et le titre se partagent mal la largeur ; tailles de titre et d'image à revoir.
- Graphiques de la fiche : aujourd'hui défilement horizontal (largeur mini 720 px) ; étudier une version verticale du flux et des barres plus lisibles sans défilement.
- Tuiles, tableau des rivaux, calculateurs, pied de page : espacements et tailles de texte.
- Infobulles au toucher : vérifier sur un vrai téléphone.
Méthode : maquettes (captures mobiles) envoyées à Nicolas avant de tout reprendre.

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
