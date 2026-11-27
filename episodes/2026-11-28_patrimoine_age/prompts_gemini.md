# Prompts Gemini : les Français de ton âge ont combien d'argent ? (vidéo du 28/11/2026)

Cinq décors autour d'une toise de croissance dans une maison 1930, et trois clips de Mister Coin. Le nom entre crochets est le nom de fichier à me renvoyer. Dépose les décors dès qu'ils sont prêts : l'affinage (Real-ESRGAN puis 60 i/s) prend environ 2 h pour cinq décors.

## Étape 0 : l'image de référence de la toise (Gemini image, 9:16)

Pour que les trois décors de la toise montrent la même toise, génère d'abord une image fixe, puis donne-la comme image de départ à Veo pour decor_toise_bas, decor_toise_milieu et decor_toise_haut.

[ref_toise] « A tall vertical 1930s wooden growth chart board fixed on a painted door frame in a cozy family hallway, seen straight on, filling the frame from floor to ceiling. The board is warm honey-colored varnished wood. Five small, wide, mirror-polished brass plates stick out horizontally from the board at regular heights, like tiny shelves, each one wide enough for a small cartoon character to sit on. Next to each brass plate, short pencil marks on the wood. Floral wallpaper in soft teal and cream on both sides, a dark wooden skirting board at the bottom, a warm wall sconce on the left. 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette, soft film grain. Native vertical 9:16. No characters, no people, no text, no letters, no numbers, no logos. »

## Décors (vidéo Veo, verticale 9:16 native, 8 s)

Bloc commun, à coller à la fin de chaque prompt de décor :

```
Style: 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette (warm yellows, teal, coral, cream, honey wood, polished brass), soft film grain. Native vertical 9:16 video. No characters, no people, no text, no letters, no numbers, no logos, no signs. Very slow, smooth, continuous camera movement, no cuts, no flicker, no blinking lights, no shaking. Keep the upper middle of the frame fairly plain (information panels will be added there).
```

1. [decor_couloir] (accroche, définition, chute) : « A cozy 1930s family hallway in warm late-afternoon light: teal and cream floral wallpaper, a polished, glossy honey wooden floor that reflects the light (no rug in the center), a coat rack with a hat, a small table with a lamp, and on the right a painted door frame with a tall wooden growth chart board and small brass plates sticking out at regular heights. Dust motes float slowly in a sunbeam from a window. The camera very slowly pushes in along the glossy floor toward the growth chart. Keep the lower third calm: a character will stand on the floor. »

2. [decor_toise_bas] (moins de 30 ans), avec ref_toise en image de départ : « Close view of the bottom part of the wooden growth chart board on the door frame, starting at the skirting board and the floor. The lowest brass plate sticks out of the board in the lower middle of the frame. The camera very slowly tilts up along the board, keeping it centered, as if measuring a growing child. Warm sconce light, a few dust motes. »

3. [decor_toise_milieu] (30-39 ans), avec ref_toise en image de départ : « Close view of the middle part of the same wooden growth chart board: two brass plates stick out of the board, one in the lower part of the frame, one higher. Pencil marks next to each plate. The camera very slowly tilts up along the board, keeping it centered. Warm sconce light, floral wallpaper on both sides. »

4. [decor_toise_haut] (40-59 ans et le plateau), avec ref_toise en image de départ : « Close view of the top part of the same wooden growth chart board, the two highest brass plates sticking out of the board, the ceiling molding and a small warm ceiling lamp appearing at the top of the frame at the end. The camera very slowly tilts up along the board until it reaches the ceiling molding, then gently stops. »

5. [decor_horloge] (le pont : le temps fait grimper le patrimoine) : « A cozy 1930s living room corner: a tall wooden grandfather clock with a brass pendulum swinging slowly and regularly, next to it a window sill with a glass jar slowly filling with golden coins, a small potted sapling, warm lamp light, the same teal and cream floral wallpaper. The camera very slowly pushes in toward the clock. Keep the lower third calm: a character will stand on the floor in front of the clock. »

Pour la chute, je reprends la fin de decor_couloir (ou le haut de la toise si le rendu est plus beau) : pas besoin d'un sixième décor.

## Mister Coin

Banque existante utilisée, sans répéter le même geste deux fois de suite : parle_question (accroche), parle_explique (définition), parle_compte_doigts (assis sur le premier trait), parle_enthousiaste (30-39 ans), loupe_parle (40-59 ans, assis), parle_confidence (pont), danse_parle_prudent ou parle_question (fin). Poses fixes en secours : sueur, reflechit.

Clips à générer (bloc commun renforcé de `mister_coin/veo/PROMPTS_GEMINI.md`, image `classique_reference_marges_16x9.jpg`, format 16:9), par ordre d'utilité :

1. [classique_roule_entree] (la signature, inspirée de Miss Minutes) « He enters from the right edge of the frame rolling on his edge like a coin rolling on a table, seen from the side as a thin golden disc with his hat on top, slows down at the center, wobbles like a spinning coin settling down, then pops up and turns to face the camera with a smile, arms open, and ends in the neutral pose. He does not talk. »
2. [classique_sueur] « He looks at something huge in front of him, his eyes go wide, a drop of sweat appears on his forehead, he pulls out a handkerchief and wipes his forehead, then puts it away with a relieved sigh. He does not talk. » (silence après « à rembourser »)
3. [classique_reflechit] « He thinks, one hand on his chin, looking up, then has an idea and raises his index finger. He does not talk. » (silence après « ça plafonne » ; déjà demandé le 22/11, la pose fixe `reflechit` reste en secours)

Les sauts d'un trait de la toise au suivant sont faits en code (courbe avec anticipation et réception amortie, à partir de classique_saut_place) : pas de clip à générer pour ça.
