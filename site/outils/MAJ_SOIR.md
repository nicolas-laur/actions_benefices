# Mise à jour du site chaque soir (tâche planifiée)

Procédure suivie par la tâche planifiée du soir (créée le 22/11/2026) pour que actionsbenefices.com suive les publications de Nicolas sur TikTok et Instagram. Elle tourne sans personne pour répondre : en cas de doute, elle n'invente rien, elle laisse la publication de côté et le signale dans son compte rendu.

## 1. Relever les publications récentes
- Connecteur Metricool (marque Actions Bénéfices, `getBrandSettings` pour l'identifiant) : publications TikTok et Instagram des 4 derniers jours, avec date, texte, type (vidéo, carrousel) et lien.
- TikTok : l'identifiant est le nombre à la fin du lien. Instagram : le chemin `reel/<code>` ou `p/<code>`.
- Comparer avec la liste `V` de `site/outils/videos.py` : une publication est nouvelle si son identifiant TikTok ou son chemin Instagram n'y figure pas. Une même publication sur les deux réseaux = une seule ligne (rapprocher par date et sujet). Si l'une des deux plateformes n'est pas encore publiée, mettre `None` ; une ligne existante peut être complétée le lendemain.

## 2. Ajouter chaque nouvelle publication
- Retrouver l'épisode dans `episodes/` (dossier daté du jour ou de la veille, sujet correspondant).
- Titre : le titre court de l'épisode, dans le ton des lignes existantes (pas de hashtags, pas d'émoji).
- Couverture : `episodes/<dossier>/couverture.png` pour une vidéo ; pour un carrousel, `out/instagram_1.png` (format unique 4:5 depuis le 26/11 ; `out/tiktok_1.png` avant). Le dossier `out/` n'est pas dans le dépôt : rendre la première diapo avec `python3 episodes/<dossier>/carrousel.py 0` (installer pycairo si besoin : `pip install pycairo --break-system-packages`). `videos.py` centre une image 4:5 sur sa couleur de fond, sans la déformer. Vignettes des carrousels plus anciens : reprendre les fichiers `.webp` déjà publiés. Si le rendu échoue, `None` (Mister Coin s'affiche à la place) et le signaler.
- Ajouter la ligne en tête de `V` (ordre antichronologique), lancer `python3 site/outils/videos.py`, recopier la liste produite (`/tmp/videos.txt`) dans `site/contenu/donnees.py` à la place de l'ancienne `VIDEOS`.

## 3. Cas particuliers
- Carrousel « Les News » (vendredi) : suivre aussi la section « Mise à jour des News » de `site/A_FAIRE.md` (rendu des diapos, `extraire_news.py`, `ecrire_news.py`, ajout de la semaine dans `SEM`). Si le rendu échoue (pycairo absent…), ajouter quand même la vidéo et signaler que la page News reste à faire.
- Fiche entreprise publiée (carrousel « Que vaut … ? », décision de Nicolas du 27/11/2026) : ajouter la publication à la liste des vidéos ET créer sa page sur le site, sans attendre de validation, dès que le carrousel est en ligne sur au moins une plateforme.
  - Contenu : uniquement les chiffres, textes et sources de `episodes/<dossier>/textes.md` et `sources.md` (déjà validés pour le carrousel). Rien d'inventé ni de recalculé autrement ; un chiffre absent de sources.md n'apparaît pas.
  - Modèle : `site/contenu/fiche_micron.py` (comptes en dollars) ou `fiche_schneider.py` (comptes en euros), mêmes 8 sections. `META` complet (`prochains_resultats` = date habituelle avec `date_confirmee=False` tant que l'entreprise ne l'a pas annoncée).
  - Ticker de l'entreprise dans `SERIES` (s'il manque) et `COURS` de `site/outils/marches.py` ; logos de `episodes/<dossier>/logos/` recadrés à 120 px de haut dans `site/assets/img/` (nom en minuscules).
  - Importer le module dans `site/build.py` et l'ajouter en fin de `ENTREPRISES` (ordre de publication).
  - Vérifier la page en 1440 et 390 px (captures en faisant défiler : les sections apparaissent au défilement), puis publier avec le reste.
  - En cas de doute (sources.md incomplet, dossier introuvable, carrousel pas encore publié) : ne pas créer la page, ajouter seulement la vidéo et le signaler.

## 4. Construire, vérifier, publier
- `python3 site/build.py` doit passer sans erreur ; contrôler que `site/_site/videos/index.html` contient le nouveau titre et que le compteur de vidéos de l'accueil a bougé.
- Fiche créée : `python3 site/build.py` doit lister `/fiches/<slug>/`, la page apparaît dans `site/_site/fiches/index.html`.
- Commit en français (« Site : publications du JJ/MM ajoutées »), terminé par les lignes d'attribution de la session, puis poussée en 5 essais (`git -c push.negotiate=true push -q origin main`, comparaison avec `git ls-remote origin main`).
- Vérifier le déploiement : `gh run list --workflow site.yml -L 1` doit finir en `success`.
- S'il n'y a rien de nouveau : aucun commit.

## 5. Compte rendu
Si `python3 site/build.py` affiche une ligne « RAPPEL fiche … date à confirmer », chercher la date officielle des prochains résultats et, si elle est annoncée par l'entreprise, mettre à jour `prochains_resultats`, `date_confirmee=True` et `prochains_txt` dans la fiche (lien de l'annonce dans le message de commit), puis le signaler. Recopier les autres lignes « RAPPEL » telles quelles. Si `python3 site/build.py` affiche une ligne « ALERTE fiche … », la recopier telle quelle dans le compte rendu : des résultats trimestriels sont sortis et la fiche attend sa mise à jour (`site/outils/MAJ_FICHES.md`, session dédiée avec Nicolas).
Un message court à Nicolas : publications ajoutées (date, titre, plateformes), ce qui manque (couverture, page News, lien d'une plateforme) et le résultat du déploiement. Rien de nouveau : une ligne suffit.
