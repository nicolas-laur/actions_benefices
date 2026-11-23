# Mise à jour du site chaque soir (tâche planifiée)

Procédure suivie par la tâche planifiée du soir (créée le 22/11/2026) pour que actionsbenefices.com suive les publications de Nicolas sur TikTok et Instagram. Elle tourne sans personne pour répondre : en cas de doute, elle n'invente rien, elle laisse la publication de côté et le signale dans son compte rendu.

## 1. Relever les publications récentes
- Connecteur Metricool (marque Actions Bénéfices, `getBrandSettings` pour l'identifiant) : publications TikTok et Instagram des 4 derniers jours, avec date, texte, type (vidéo, carrousel) et lien.
- TikTok : l'identifiant est le nombre à la fin du lien. Instagram : le chemin `reel/<code>` ou `p/<code>`.
- Comparer avec la liste `V` de `site/outils/videos.py` : une publication est nouvelle si son identifiant TikTok ou son chemin Instagram n'y figure pas. Une même publication sur les deux réseaux = une seule ligne (rapprocher par date et sujet). Si l'une des deux plateformes n'est pas encore publiée, mettre `None` ; une ligne existante peut être complétée le lendemain.

## 2. Ajouter chaque nouvelle publication
- Retrouver l'épisode dans `episodes/` (dossier daté du jour ou de la veille, sujet correspondant).
- Titre : le titre court de l'épisode, dans le ton des lignes existantes (pas de hashtags, pas d'émoji).
- Couverture : `episodes/<dossier>/couverture.png` pour une vidéo, `out/tiktok_1.png` pour un carrousel. Si aucune n'existe, `None` (Mister Coin s'affiche à la place) et le signaler.
- Ajouter la ligne en tête de `V` (ordre antichronologique), lancer `python3 site/outils/videos.py`, recopier la liste produite (`/tmp/videos.txt`) dans `site/contenu/donnees.py` à la place de l'ancienne `VIDEOS`.

## 3. Cas particuliers
- Carrousel « Les News » (vendredi) : suivre aussi la section « Mise à jour des News » de `site/A_FAIRE.md` (rendu des diapos, `extraire_news.py`, `ecrire_news.py`, ajout de la semaine dans `SEM`). Si le rendu échoue (pycairo absent…), ajouter quand même la vidéo et signaler que la page News reste à faire.
- Nouvelle fiche entreprise : ne pas la créer automatiquement (contenu à valider par Nicolas) ; ajouter seulement la publication à la liste des vidéos et le signaler.

## 4. Construire, vérifier, publier
- `python3 site/build.py` doit passer sans erreur ; contrôler que `site/_site/videos/index.html` contient le nouveau titre et que le compteur de vidéos de l'accueil a bougé.
- Commit en français (« Site : publications du JJ/MM ajoutées »), terminé par les lignes d'attribution de la session, puis poussée en 5 essais (`git -c push.negotiate=true push -q origin main`, comparaison avec `git ls-remote origin main`).
- Vérifier le déploiement : `gh run list --workflow site.yml -L 1` doit finir en `success`.
- S'il n'y a rien de nouveau : aucun commit.

## 5. Compte rendu
Si `python3 site/build.py` affiche une ligne « RAPPEL fiche … date à confirmer », chercher la date officielle des prochains résultats et, si elle est annoncée par l'entreprise, mettre à jour `prochains_resultats`, `date_confirmee=True` et `prochains_txt` dans la fiche (lien de l'annonce dans le message de commit), puis le signaler. Recopier les autres lignes « RAPPEL » telles quelles. Si `python3 site/build.py` affiche une ligne « ALERTE fiche … », la recopier telle quelle dans le compte rendu : des résultats trimestriels sont sortis et la fiche attend sa mise à jour (`site/outils/MAJ_FICHES.md`, session dédiée avec Nicolas).
Un message court à Nicolas : publications ajoutées (date, titre, plateformes), ce qui manque (couverture, page News, lien d'une plateforme) et le résultat du déploiement. Rien de nouveau : une ligne suffit.
