# Mister Coin, présentateur d'Actions_Bénéfices

Mascotte cartoon 2D animée à partir de 9 illustrations Gemini (fond vert), validée le 22 octobre 2026 sur l'actu Netflix, Tesla, Meta.

## Contenu du dossier

- `src/` : les 9 dessins de base, tous alignés au pixel (1792×2400). Les bouches sont `bouche_fermee`, `bouche_mi`, `bouche_ouverte` et `bouche_o`. Les autres fichiers sont `yeux_fermes`, `ravi`, `inquiet`, `thumb` (pouce levé) et `point` (doigt pointé).
- `puppet.py` : détourage du vert, synchro labiale sur le volume de la voix, clignements, expressions. La pose « souci » combine les sourcils d'`inquiet` avec une bouche qui parle.
- `rig.py` : découpage en pièces articulées (deux jambes, bras qui salue, corps), avec des articulations cachées derrière la pièce.
- `mister_coin.py` : le calque prêt à l'emploi (classe `MisterCoin`) et le placement automatique des expressions selon les silences de la voix.

## Utilisation

```python
import sys; sys.path.insert(0, '/chemin/vers/mister_coin')
from mister_coin import MisterCoin
mc = MisterCoin('voix.wav',
                places={'bas': (540, 1655, .40), 'gauche': (305, 1100, .30), 'cta': (540, 1665, .27)},
                debut='bas',
                moments=[(3.5, 'negatif'), (9.9, 'pouce'), (11.7, 'montre'), (36.0, 'positif')],
                sauts_de_place=[(11.05, 'gauche'), (38.55, 'cta')],
                petits_sauts=[9.9, 31.25, 34.9, 39.25],
                coucous=[(.2, 3.3), (40.3, 41.6)],
                entree=(0.0, 1.3, 1350))
cadre.alpha_composite(mc.layer(t))   # après les panneaux, avant les sous-titres
```

Une place s'écrit `(x du centre de la pièce, y des pieds, zoom)` dans un cadre de 1080×1920. Les types de moments sont les suivants :

- `negatif` : sourcils inquiets pendant qu'il parle, puis grimace dans le silence qui suit, s'il dure au moins 0,3 s.
- `positif` : il a l'air ravi dans le prochain silence.
- `montre` : il pointe du doigt vers la droite pendant 1 s.
- `pouce` : il lève le pouce pendant 1 s.

### Version dynamique (validée le 22 oct. au soir sur PEA/CTO)

- Une place peut aussi s'écrire `(x, y, zoom, miroir, inclinaison)`. Avec `miroir=True`, il regarde et pointe vers la gauche : place-le en miroir sur la moitié droite de l'écran pour qu'il désigne toujours le contenu. Il se retourne en plein saut.
- `sauts_de_place` accepte deux formes : `(t, place)` pour un saut en arc, de graphique en graphique, ou `(t, place, 'marche', durée)` pour un déplacement à pied, par exemple le long du bord d'un panneau.
- `marches=[(t0, t1)]` le fait marcher sur place, `assis=[(t0, t1)]` l'assoit, jambes tendues, par exemple sur un chiffre, et `danses=[(t0, t1)]` le fait danser.
- `bulles=[(t0, t1, "texte", côté)]` affiche une blague courte dans une bulle de BD, en cinq mots au maximum. Le côté vaut `'haut'` par défaut, ou `'gauche'` / `'droite'`. La bulle suit Mister Coin image par image et sa pointe arrive toujours sur lui (chapeau ou bouche). Choisis le côté qui ne cache aucun texte. Pas de blague sur la question finale.
- Ordre des calques : décor, panneaux et textes des scènes, puis Mister Coin, puis les sous-titres. Rien du décor ne doit passer devant lui.
- Ses deux mains restent dans le cadre si x est compris entre 207 et 873 au zoom 0,2. Tout texte de la vidéo doit rester lisible : vérifie une image par scène avant de lancer le rendu.

- `largeur=lambda t: …` épaissit ou amincit Mister Coin quand il parle (1,3 = gros, 0,6 = mince), pour rester cohérent avec les poses dessinées « gros » et « mince » placées dans les silences.

Tu peux aussi passer `actions=[(début, fin, pose), ...]` pour tout régler à la main.

Test rapide : `python3 mister_coin.py voix.wav` produit `apercu_mister_coin.png`.

## Règles de jeu validées

- Pas de gros plan. Il garde une taille constante et sert à illustrer ce qui est dit, sans voler la vedette aux infos.
- Les mouvements sont lents et continus. L'énergie de la voix est lissée sur environ 0,3 s. Il respire, se balance doucement et passe d'une pose à l'autre par un fondu enchaîné de 0,14 s. Les sauts suivent une courbe continue : anticipation, envol, réception amortie.
- Il ne grimace et n'a l'air ravi que dans les silences de la voix, jamais pendant qu'il parle.
- Ses deux mains doivent toujours rester dans le cadre. Sur la place de gauche, vérifie le bras qui salue.
- Pour la mise en page avec Mister Coin à gauche, place à droite un panneau compact (540 de large, centré en x ≈ 788) qu'il désigne du doigt, et mets la carte des chiffres en dessous.
- La voix reste celle de Thomas (ElevenLabs).

Rendu : comptez environ 45 min pour 42 s en 60 i/s sur 2 cœurs, en deux segments rendus en parallèle.
