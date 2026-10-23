# Actions_Bénéfices — chaîne de production

Vidéos courtes (9:16, 1080×1920) de vulgarisation bourse/finance publiées sur TikTok, YouTube Shorts et Instagram Reels.

## Arborescence

- `episodes/<AAAA-MM-JJ>_<sujet>/` : un dossier par vidéo, autonome.
  - `video.py` : le compositeur, avec trois commandes : `info` (durée), `png t1 t2 …` (images d'aperçu dans `prev/`) et `seg sortie.mp4 f0 f1` (rendu d'une plage d'images).
  - `mix.py` : la musique, les bruitages et la voix, qui produisent `mix.wav` et `mix_sans_musique.wav`.
  - `voice.mp3` : la voix de Thomas (ElevenLabs), générée par Nicolas à partir du script.
  - `timing.json` : le calage des phrases sur la voix (débuts de phrase et mots clés).
  - `decors/`, `poses/` : les images Gemini propres à l'épisode.
  - `couverture.py`, `description.txt`, `sources.md` : la publication.
- `mister_coin/` : la mascotte, en kit réutilisable (voir son README pour les règles de jeu validées).
- `lib/` : les outils communs (texte et typographie, logo officiel, cartes de couverture).
- `fonts/` : les polices (Anton, Inter Display, Poppins, JetBrains Mono).
- `archives/` : les scripts des vidéos précédentes (code seulement), à garder comme référence.

## Rendre une vidéo

```bash
python3 render.py episodes/2026-10-24_krachs_ep2        # relancer jusqu’à « TERMINÉ » si la durée des commandes est limitée
```

`render.py` installe les polices, convertit la voix, fait le mix, rend la vidéo par tranches de 120 images (3 en parallèle, reprenable), les assemble et normalise le son à −14 LUFS. Les fichiers finaux arrivent dans `out/`. Dépendances : `python3`, `numpy`, `scipy`, `pillow`, `pycairo` et `ffmpeg`.

## Flux de travail

1. Nicolas remplit la direction artistique dans la roadmap (artefact « Plan Actions_Bénéfices »).
2. Claude vérifie les chiffres, écrit le script (nombres en toutes lettres) et liste les décors et poses à demander à Gemini.
3. Nicolas génère la voix et les images, puis les dépose dans le dossier de l'épisode.
4. Claude cale `timing.json` sur la voix, place Mister Coin dans les silences et envoie des aperçus, puis lance le rendu.
5. Publication à 12h30 : cocher « Contenu généré par IA », mettre les sources en premier commentaire, envoyer en HD.
