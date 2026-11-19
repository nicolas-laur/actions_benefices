# Fiche entreprise (carrousel, format à tester)

Idée du 19/11/2026, inspirée des carrousels « Que vaut l'entreprise qui… » de Les Finances de Papa (Take-Two, le jour de la sortie de GTA VI) : un déroulé d'analyste, toujours le même, appliqué à une entreprise qui fait l'actualité. On garde la structure et la précision, avec notre DA (1930, verre épais, Mister Coin) et notre ligne : des faits vérifiables, jamais de verdict ni de conseil.

## Quand l'utiliser
- Une entreprise au cœur de l'actualité de la semaine : résultats, introduction en bourse, sortie de produit, changement de patron.
- Idéalement en complément d'un sujet déjà sourcé (vidéo ou News du vendredi), pour réutiliser les chiffres vérifiés.
- Premiers candidats : Walmart, Anthropic (première publication de résultats comme société cotée), Nvidia.

## Structure (8 diapos, gabarit `lib/carrousel.py`)
1. Couverture : « Que vaut [entreprise] ? », l'accroche d'actualité en une ligne, Mister Coin `reflechit` ou `lit_journal_v2_titre`, décor 1930 lié au métier de l'entreprise.
2. Carte d'identité : ce qu'elle fait (3 lignes), où elle gagne son argent (répartition du chiffre d'affaires par activité ou par région), date d'entrée en bourse, capitalisation en euros.
3. Croissance : chiffre d'affaires sur 5 exercices en barres (lib `dataviz`), croissance annuelle moyenne, encadré « ce qu'il faut retenir » en 3 lignes.
4. Rentabilité : résultat net et marge nette sur 5 exercices ; si l'entreprise perd de l'argent, expliquer pourquoi en une phrase (dépréciation, investissements…).
5. Solidité : dette nette, flux de trésorerie disponible (free cash flow). Une ligne d'explication par notion (lexique maison).
6. Dividende : dividende par action sur 10 ans en barres (en euros), rendement au cours retenu, taux de distribution (dividende / bénéfice par action), nombre d'années de hausse ou de maintien d'affilée, dates de détachement et de versement à venir. S'il n'y a pas de dividende, le dire et expliquer ce que l'entreprise fait de son argent à la place (rachats d'actions, investissements, désendettement), avec les montants.
7. Face à son secteur : croissance de l'entreprise contre celle de son marché, ou ratios comparés à 2 concurrents (PER, marge). Source du chiffre de marché obligatoire.
8. Fin : « Ce qu'il faut surveiller » (2 ou 3 faits à venir, datés : prochains résultats, sortie, échéance), question d'engagement, « enregistre-le », `bloc_abonne`, `mention_pedago`.

## Style graphique (retour du 19/11 : « vraiment bien », à adapter à nos couleurs)
Repris des carrousels de référence, parce qu'il est clair et dense sans être chargé :
- Tableau de bord en tuiles : indicateurs rangés par familles (croissance, rentabilité, santé financière, tendances), une tuile par chiffre avec son libellé, la valeur en gras et le contexte en petit gris (« +18,1 % vs 2025 »), une pastille ✓ / ✗ / – à gauche.
- Titres de famille en petites capitales espacées, suivis de 2 ou 3 points de couleur qui résument la famille d'un coup d'œil.
- Graphiques épurés : barres avec la valeur écrite au-dessus, négatifs en rouge sous l'axe, une courbe secondaire (marge) sous les barres, légende en bas, grille très légère.
- Encadré de lecture : bloc à filet vertical coloré à gauche, 3 ou 4 lignes, chiffres clés en gras.
- Mention « Source : … » sous chaque graphique, en petit, alignée à droite.

Adaptation Actions_Bénéfices :
- Les tuiles et les graphiques vivent dans nos panneaux de verre épais (`tp`), sur le décor 1930 assombri, pas sur un fond blanc.
- Couleurs maison (`lib/carrousel.py`) : or `GD` pour les titres et le filet de l'encadré, vert `GR` pour ✓ et les hausses, rouge `RD` pour ✗ et les baisses, cyan `CY` pour la courbe secondaire et les barres « tendance », blanc et `ICE` pour les textes. Barres principales en or dégradé (`GD` → `GD2`).
- Pastilles : nos émojis Noto (✅ ❌ ➖) ou des ronds pleins dans nos couleurs, au choix après maquette.
- Police : Inter Display (pas de police condensée hors couverture), chiffres en ExtraBold.
- Une seule fonction de graphique à ajouter à `lib/carrousel.py` (barres + courbe, valeurs étiquetées), réutilisable dans les News pour la diapo bonus « tendance longue ».

## Règles
- Pas de note sur 10, pas de « cours revalorisé », pas d'objectif de cours, pas d'avis « bon ou mauvais investissement ». La dernière diapo liste des faits à venir, pas une opinion.
- Exercices fiscaux nommés tels quels (« exercice clos fin mars 2026 ») ; ne jamais mélanger année civile et exercice sans le dire.
- Une seule devise par graphique : montants convertis en euros au taux BCE du jour de clôture retenu, montant d'origine en dollars en petit.
- Sources : rapports annuels et communiqués de l'entreprise (10-K, 10-Q, S-1, document d'enregistrement) en priorité, puis presse financière ; tout dans `sources.md`.
- Dividendes : montants bruts, devise d'origine précisée ; dividende exceptionnel séparé du dividende ordinaire sur le graphique ; rappeler que la fiscalité dépend de l'enveloppe (PEA, CTO) sans entrer dans le détail.
- Ratios calculés nous-mêmes, formule écrite dans `sources.md` (ex. marge nette = résultat net / chiffre d'affaires).
- Un graphique par diapo au plus, toujours accompagné d'un encadré de 3 ou 4 lignes qui le traduit en français simple.

## À trancher avec Nicolas avant le premier épisode
- Fréquence : ponctuelle (quand l'actu s'y prête) ou rendez-vous fixe (ex. le mardi).
- Nom de la série (« Que vaut… ? », « La fiche de Mister Coin », « Sous le capot »…).
- Décor : un fond Gemini dédié par entreprise, ou un décor fixe de série (bureau d'analyste 1930) pour l'identifier d'un coup d'œil.
