# Fiche entreprise (carrousel, format à tester)

Idée du 19/11/2026, inspirée des carrousels « Que vaut l'entreprise qui… » de Les Finances de Papa (Take-Two, le jour de la sortie de GTA VI) : un déroulé d'analyste, toujours le même, appliqué à une entreprise qui fait l'actualité. On garde la structure et la précision, avec notre DA (1930, verre épais, Mister Coin) et notre ligne : des faits vérifiables, jamais de verdict ni de conseil.

## Quand l'utiliser
- Une entreprise au cœur de l'actualité de la semaine : résultats, introduction en bourse, sortie de produit, changement de patron.
- Idéalement en complément d'un sujet déjà sourcé (vidéo ou News du vendredi), pour réutiliser les chiffres vérifiés.
- Premiers candidats : Walmart, Anthropic (première publication de résultats comme société cotée), Nvidia.

## Structure (7 diapos, gabarit `lib/carrousel.py`)
1. Couverture : « Que vaut [entreprise] ? », l'accroche d'actualité en une ligne, Mister Coin `reflechit` ou `lit_journal_v2_titre`, décor 1930 lié au métier de l'entreprise.
2. Carte d'identité : ce qu'elle fait (3 lignes), où elle gagne son argent (répartition du chiffre d'affaires par activité ou par région), date d'entrée en bourse, capitalisation en euros.
3. Croissance : chiffre d'affaires sur 5 exercices en barres (lib `dataviz`), croissance annuelle moyenne, encadré « ce qu'il faut retenir » en 3 lignes.
4. Rentabilité : résultat net et marge nette sur 5 exercices ; si l'entreprise perd de l'argent, expliquer pourquoi en une phrase (dépréciation, investissements…).
5. Solidité : dette nette, flux de trésorerie disponible (free cash flow), dividende ou rachats d'actions. Une ligne d'explication par notion (lexique maison).
6. Face à son secteur : croissance de l'entreprise contre celle de son marché, ou ratios comparés à 2 concurrents (PER, marge). Source du chiffre de marché obligatoire.
7. Fin : « Ce qu'il faut surveiller » (2 ou 3 faits à venir, datés : prochains résultats, sortie, échéance), question d'engagement, « enregistre-le », `bloc_abonne`, `mention_pedago`.

## Règles
- Pas de note sur 10, pas de « cours revalorisé », pas d'objectif de cours, pas d'avis « bon ou mauvais investissement ». La dernière diapo liste des faits à venir, pas une opinion.
- Exercices fiscaux nommés tels quels (« exercice clos fin mars 2026 ») ; ne jamais mélanger année civile et exercice sans le dire.
- Une seule devise par graphique : montants convertis en euros au taux BCE du jour de clôture retenu, montant d'origine en dollars en petit.
- Sources : rapports annuels et communiqués de l'entreprise (10-K, 10-Q, S-1, document d'enregistrement) en priorité, puis presse financière ; tout dans `sources.md`.
- Ratios calculés nous-mêmes, formule écrite dans `sources.md` (ex. marge nette = résultat net / chiffre d'affaires).
- Un graphique par diapo au plus, toujours accompagné d'un encadré de 3 ou 4 lignes qui le traduit en français simple.

## À trancher avec Nicolas avant le premier épisode
- Fréquence : ponctuelle (quand l'actu s'y prête) ou rendez-vous fixe (ex. le mardi).
- Nom de la série (« Que vaut… ? », « La fiche de Mister Coin », « Sous le capot »…).
- Décor : un fond Gemini dédié par entreprise, ou un décor fixe de série (bureau d'analyste 1930) pour l'identifier d'un coup d'œil.
