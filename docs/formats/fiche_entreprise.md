# Fiche entreprise (carrousel, format à tester)

Idée du 19/11/2026, inspirée des carrousels « Que vaut l'entreprise qui… » de Les Finances de Papa (Take-Two, le jour de la sortie de GTA VI) : un déroulé d'analyste, toujours le même, appliqué à une entreprise qui fait l'actualité. On garde la structure et la précision, avec notre DA (1930, verre épais, Mister Coin) et notre ligne : des faits vérifiables, jamais de verdict ni de conseil.

## Objectif et programme (décision du 24/11/2026)
Dans un premier temps, le but est de produire une fiche pour chacune des valeurs des deux feuilles du fichier Google Sheets « Suivi Finance et Analyse de titres » de Nicolas : https://docs.google.com/spreadsheets/d/1SsAM1VUCHfy-8VlkOuY62tXBD0Mfmv9eU2tckIJs6_4/edit . La feuille « Analyse actions détenues » contient les valeurs que Nicolas détient (ligne de transparence « Je détiens des actions X. » sur la dernière diapo) ; la feuille « Analyse d'actions » contient les valeurs qu'il suit sans forcément les détenir (à vérifier avec lui avant chaque fiche). Liste relevée le 24/11/2026 (44 valeurs ; relire le fichier avant de choisir la suivante, il évolue) :
- Analyse actions détenues (20) : EssilorLuxottica, Capgemini, Porsche AG (préf.), GE Aerospace, L'Oréal, IBM, Alstom, Nokia, Publicis Groupe, Air Liquide, Vinci, Carrefour, AXA, Getlink, GE HealthCare, Engie, Intercontinental Exchange, Cisco Systems, GE Vernova, Kyndryl.
- Analyse d'actions (24) : Amazon, McDonald's, Microsoft, Apple, Broadcom, Visa, Coca-Cola, Schneider Electric, ASML, Tesla, SpaceX, Novo Nordisk, TotalEnergies, ExxonMobil, Micron, AstraZeneca, Pfizer, Samsung Electronics, Uber, Hermès, Spotify, Nestlé, AT&T, Airbus.
Fiches publiées : Nvidia (n°1, 22/11, hors liste) et Alphabet (n°2, 23-24/11, hors liste). L'actualité de la semaine choisit la valeur dans la liste ; les chiffres du fichier (exercice, CA, EBIT, dette nette, FCF…) servent de point de départ mais sont revérifiés sur les rapports annuels avant toute diapo.

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
Captures de référence partagées par Nicolas le 19/11 (Les Finances de Papa, Take-Two) : `docs/formats/references/fiche_entreprise/` (1_points_cles, 2_resultats, 3_cours_valorisation, 4_secteur, 5_avis). Les rouvrir avant chaque maquette de ce format pour viser juste. On en reprend la mise en page, pas le contenu (pas de note, pas de cours revalorisé, pas d'avis : voir Règles).

Repris de ces carrousels, parce qu'il est clair et dense sans être chargé :
- Tableau de bord en tuiles : indicateurs rangés par familles (croissance, rentabilité, santé financière, tendances), une tuile par chiffre avec son libellé, la valeur en gras et le contexte en petit gris (« +18,1 % vs 2025 »), une pastille ✓ / ✗ / – à gauche.
- Titres de famille en petites capitales espacées, suivis de 2 ou 3 points de couleur qui résument la famille d'un coup d'œil.
- Graphiques épurés : barres avec la valeur écrite au-dessus, négatifs en rouge sous l'axe, une courbe secondaire (marge) sous les barres, légende en bas, grille très légère.
- Encadré de lecture : bloc à filet vertical coloré à gauche, 3 ou 4 lignes, chiffres clés en gras.
- Mention « Source : … » sous chaque graphique, en petit, alignée à droite.

Décision du 21/11 (fiche Nvidia) : format clair, au plus près de la référence. Fond crème uni, cartes claires, accents or et vert ; aucun décor Gemini (un décor assombri derrière des panneaux qui couvrent tout l'écran ne se voyait presque pas et brouillait la lecture). Les points ci-dessous sur le verre et le décor sont remplacés par ce choix ; les couleurs sont à recalibrer pour un fond clair (or et vert plus foncés pour le contraste).
Retours du 21/11 sur la fiche Nvidia : rangées de tuiles alignées sur les bords des cartes principales (x = 40 → 1040) et gardées au-dessus de y = 1000 ; encadré de lecture du bas en carte blanche simple, sans filet doré (« trop signé Anthropic ») ; sources alignées à gauche ; graphique de flux en mise en page inspirée de App Economy Insights, avec logo et pictogrammes, crédit en bas de diapo.

Adaptation Actions_Bénéfices (avant le 21/11) :
- Les tuiles et les graphiques vivent dans nos panneaux de verre épais (`tp`), sur le décor 1930 assombri, pas sur un fond blanc.
- Couleurs maison (`lib/carrousel.py`) : or `GD` pour les titres et le filet de l'encadré, vert `GR` pour ✓ et les hausses, rouge `RD` pour ✗ et les baisses, cyan `CY` pour la courbe secondaire et les barres « tendance », blanc et `ICE` pour les textes. Barres principales en or dégradé (`GD` → `GD2`).
- Pastilles : nos émojis Noto (✅ ❌ ➖) ou des ronds pleins dans nos couleurs, au choix après maquette.
- Police : Inter Display (pas de police condensée hors couverture), chiffres en ExtraBold.
- Mister Coin sur chaque fiche, à la place du personnage de la référence : en bas à gauche, à côté de l'encadré de lecture (comme le présentateur sur 1_points_cles), dans une pose qui colle au chiffre (`reflechit`, `doigt_leve`, `sceptique`, `sueur`, `applaudit`, `etoiles`…), bulle courte sur le ton maison. Jamais devant un graphique ou une tuile.
- Une seule fonction de graphique à ajouter à `lib/carrousel.py` (barres + courbe, valeurs étiquetées), réutilisable dans les News pour la diapo bonus « tendance longue ».

## Règles
- Pas de note sur 10, pas de « cours revalorisé », pas d'objectif de cours, pas d'avis « bon ou mauvais investissement ». La dernière diapo liste des faits à venir, pas une opinion.
- Exercices fiscaux nommés tels quels (« exercice clos fin mars 2026 ») ; ne jamais mélanger année civile et exercice sans le dire.
- Une seule devise par graphique : montants convertis en euros au taux BCE du jour de clôture retenu, montant d'origine en dollars en petit.
- Sources : rapports annuels et communiqués de l'entreprise (10-K, 10-Q, S-1, document d'enregistrement) en priorité, puis presse financière ; tout dans `sources.md`.
- Dividendes : montants bruts, devise d'origine précisée ; dividende exceptionnel séparé du dividende ordinaire sur le graphique ; rappeler que la fiscalité dépend de l'enveloppe (PEA, CTO) sans entrer dans le détail.
- Ratios calculés nous-mêmes, formule écrite dans `sources.md` (ex. marge nette = résultat net / chiffre d'affaires).
- Un graphique par diapo au plus, toujours accompagné d'un encadré de 3 ou 4 lignes qui le traduit en français simple.

## Sur le site (décisions du 23/11)
- Cours, capitalisation, PER et rendement recalculés chaque soir avec la dernière clôture (`site/cours.py`) : aucun chiffre lié au cours écrit en dur.
- Comptes mis à jour à chaque publication trimestrielle, en session dédiée (`site/outils/MAJ_FICHES.md`) ; la tâche du soir signale les résultats sortis.
- Périodes en dates civiles (« trimestre de fin juillet à fin octobre 2026 ») ; la numérotation de l'entreprise (« T3 de l'exercice 2027 » chez Nvidia) seulement en complément, car elle prête à confusion.
- Historique dans chaque fiche : une section par année, un bloc par trimestre civil ; chaque version passée reste consultable avec ses chiffres et son cours de l'époque.

## À trancher avec Nicolas avant le premier épisode
- Fréquence : ponctuelle (quand l'actu s'y prête) ou rendez-vous fixe (ex. le mardi).
- Nom de la série (« Que vaut… ? », « La fiche de Mister Coin », « Sous le capot »…).
- Décor : un fond Gemini dédié par entreprise, ou un décor fixe de série (bureau d'analyste 1930) pour l'identifier d'un coup d'œil.
