# Prompts Gemini : buy, borrow, die (vidéo du 21/11/2026)

7 nouveaux décors (aucune reprise du verger ni du tabac du Loto, trop récents), 2 nouveaux accessoires (les autres sont repris des épisodes précédents) et 5 clips Mister Coin à compléter dans la banque. Le nom entre crochets est le nom de fichier à me renvoyer.

## Décors (vidéo Veo, format vertical 9:16, 8 s)

Bloc commun, à coller à la fin de chaque prompt de décor :

```
Style: 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette (warm yellows, teal, coral red, cream), soft film grain. Vertical 9:16 framing. No characters, no people, no text, no letters, no numbers, no logos, no flags with symbols. Very slow, continuous camera movement, no cuts, no flicker, no blinking lights. Keep the lower third calm and uncluttered (a character will stand there) and keep the upper middle of the frame fairly plain (information panels will be added there).
```

1. [decor_manoir] (accroche, le chiffre ProPublica, les trois mots, question finale) : « A lavish 1930s billionaire's mansion drawing room: marble columns, a grand fireplace with a crackling fire, a crystal chandelier gently swaying, velvet armchairs, oil paintings in gilded frames, and on one side a huge round steel safe with its door wide open, overflowing with gold coins and stock certificates. Warm golden evening light. The camera slowly pushes in. »

2. [decor_coffres] (1. Buy) : « A 1930s bank vault room seen from inside: walls lined with small brass safe deposit boxes, a huge round vault door with gears and bolts slowly turning closed in the background, polished checkered floor, warm lamps. In the center, neat stacks of stock certificates tied with ribbons rest on a velvet pedestal under a glass dome. Calm, secure atmosphere. Static camera, very slow movement of the vault gears. »

3. [decor_guichet] (2. Borrow et le cas réel) : « A grand 1930s bank hall: a long polished wooden counter with brass bars and teller windows, green banker's lamps, a big wall clock, marble floor, tall arched windows with sunlight streaming in. On the counter, a few bundles of banknotes and a small brass scale. The counter top runs horizontally across the lower middle of the frame (a character will stand on it). The camera slowly pushes in. »

4. [decor_notaire] (3. Die et droits de succession) : « A solemn 1930s notary's office: dark wood paneling, a heavy desk with an ink pot, a quill, a wax seal and a rolled parchment tied with a red ribbon, a tall grandfather clock whose pendulum swings slowly, bookshelves full of old ledgers, a window with soft rain outside. Muted warm light, a touch of melancholy but not sad. Static camera, only the pendulum and the rain move. »

5. [decor_hemicycle] (le volet France et la taxe Zucman) : « A 1930s cartoon version of a French parliament hemicycle seen from the upper benches: semicircular rows of red velvet seats, wooden desks, a speaker's rostrum at the bottom, a big bronze chandelier, empty seats, warm light from a glass ceiling. No people, no flag, no emblem. The camera slowly drifts sideways. »

6. [decor_salon] (à ton échelle : PEA et intérêts composés) : « A cozy, modest 1930s family living room: a small fireplace, a radio set, a rocking chair with a knitted blanket, a window with a sunny garden outside. On a small round table, a terracotta pot with a little money tree whose leaves are gold coins, slowly growing and gaining new coin leaves. Warm, simple and reassuring. The camera slowly pushes in toward the money tree. »

7. [decor_krach] (le risque de l'emprunt sur titres) : « A 1930s stock exchange trading floor during a storm: a huge chalkboard wall with zigzag lines going down (no numbers, no letters), ticker tape paper slowly falling like snow, scattered papers on the floor, a big glass roof with dark storm clouds and soft lightning glow (no sudden flashes). Dramatic but not violent. Static camera, smooth continuous falling paper. »

## Accessoires (image fixe, fond vert uni #00FF00)

Bloc commun, à coller à la fin de chaque prompt d'accessoire :

```
1930s rubber hose cartoon style, Technicolor palette, thick dark brown outlines, soft painted shading and a small glossy highlight. Single object, centered, fully visible with generous margins, no shadow on the ground, isolated on a flat pure green background (#00FF00), no text, no numbers, no logos.
```

1. [cadenas] : « A big shiny brass padlock, closed, with a small key hanging from it on a ring, slightly tilted. » (posé sur la pile d'actions : « ne jamais vendre »)
2. [testament] : « A rolled old parchment scroll partly unrolled, tied with a red ribbon and sealed with a red wax seal, blank parchment with no writing. » (la transmission aux héritiers)

Repris des épisodes précédents : certificat_action, billet_dollar, coffre_deborde, chaines, tirelire.

## Mister Coin

Banque existante utilisée (tenue classique) : parle_question (accroche), parle_explique (le chiffre), choc (silence après 3,4 %), parle_confidence (les trois mots, ton du secret), parle_enthousiaste (Buy), danse_parle_billets (Borrow), montre_haut_droite (la fiche Ellison), réaction bouche bée dans le silence après « effacée », parle_inquiet (droits de succession), parle_triste ou inquiet (risque), parle_question (fin).

Clips à générer pour éviter les répétitions (bloc commun renforcé de `mister_coin/veo/PROMPTS_GEMINI.md`, image `classique_reference_marges_16x9.jpg`, format 16:9), par ordre d'utilité :

1. [classique_parle_neutre] « He explains something calmly to the camera with small natural hand gestures and slight head movements. His feet stay planted on the ground the whole time, he does not walk or step. He talks continuously from the first to the last second, mouth always moving, no pause. » (volet France)
2. [classique_doigt_non] « He wags his index finger left and right with a friendly but firm face, as if saying no no no. He does not talk. » (après « la banque peut vendre »)
3. [classique_sceptique] « He crosses his arms, raises one eyebrow and squints doubtfully at the camera, then slowly uncrosses his arms. He does not talk. » (silence après le rejet de la taxe Zucman, si on en garde un)
4. [classique_sueur] « He looks nervous, a drop of sweat runs down his face and he pulls at his bow tie. He does not talk. » (scène du krach)
5. [classique_deception] « His smile fades, his eyebrows rise in worry, his arms drop and he sighs. He does not talk. » (droits de succession)

Si un clip manque, je me rabats sur la banque existante sans répéter le même geste deux fois de suite.
