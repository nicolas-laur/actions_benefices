# Mise à jour des fiches entreprises

Deux rythmes (décision de Nicolas du 23/11/2026).

## Chaque soir, automatique
Le workflow `.github/workflows/site.yml` relance `site/outils/marches.py` du mardi au samedi après la clôture de Wall Street : dernier cours de clôture des valeurs de `COURS` (Yahoo Finance) et dernier taux de référence BCE. `site/cours.py` les met à disposition des fiches, qui recalculent cours, capitalisation, PER (cours ÷ BPA des 12 derniers mois publiés), rendement du dividende et rang du PER face aux rivaux. Si Yahoo ou la BCE ne répondent pas, la fiche garde les dernières valeurs connues avec leur date.
Pour une nouvelle fiche : ajouter le ticker de l'entreprise et de ses rivaux dans `SERIES` et `COURS` de `marches.py`, et suivre le modèle de `site/contenu/fiche_nvidia.py` (`cours()`, `per()`, `BPA12`, `ACTIONS`, `DIV_AN`). Aucun chiffre lié au cours ne doit être écrit en dur.

## À chaque trimestre, après la publication des résultats
1. Repérer la date : `META['prochains_resultats']` de la fiche. Une fois la date passée, `site/build.py` affiche une ALERTE à chaque construction, et la tâche du soir la relaie à Nicolas dans son compte rendu (elle ne met pas la fiche à jour elle-même).
2. Ouvrir une session dédiée « Mise à jour de la fiche <entreprise> T<n> » : relever le communiqué et le 10-Q (ou 10-K), compléter `episodes/<dossier de la fiche>/sources.md` (nouvelle section datée, anciens chiffres conservés).
3. Mettre à jour la fiche du site : trimestre ajouté au graphique de croissance, flux du trimestre, résultat net et BPA, bilan et rachats, dividende, `BPA12` des 4 derniers trimestres (entreprise et rivaux s'ils ont publié), `ACTIONS`, `DIV_AN`, et dans `META` : `comptes`, `comptes_publies`, `prochains_resultats`, `prochains_txt`. Encadrés de lecture relus : un texte vrai au trimestre précédent peut ne plus l'être.
4. Taux BCE des comptes (`EUR`) : celui du jour de publication des résultats.
5. Vérifier la page en 1440 et 390 px, pousser, contrôler le déploiement. Proposer à Nicolas un carrousel « mise à jour » seulement si les chiffres ont nettement bougé.
