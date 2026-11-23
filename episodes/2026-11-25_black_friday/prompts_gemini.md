# Prompts Gemini : Black Friday, bonne affaire ou marketing ? (vidéo du 25/11/2026)

Cinq décors autour d'un grand magasin Art déco des années 1930, trois clips Mister Coin à compléter dans la banque. Le nom entre crochets est le nom de fichier à me renvoyer. Pense à les déposer tôt : l'affinage (Real-ESRGAN puis interpolation 60 i/s par flux optique avec `interp_flow.py`) prend environ 2 h pour cinq décors.

## Décors (vidéo Veo, verticale 9:16 native, 8 s)

Bloc commun, à coller à la fin de chaque prompt de décor :

```
Style: 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette (warm yellows, teal, coral red, cream, polished brass and chrome), soft film grain, Art Deco architecture. Native vertical 9:16 video. No text, no letters, no numbers, no logos, no brand names, no signs with writing. Very slow, smooth, continuous camera movement, no cuts, no shaking, no flicker, no blinking or flashing lights. Keep the lower third calm and uncluttered (a character will stand there) and keep the upper middle of the frame fairly plain (information panels will be added there).
```

1. [decor_rue] (l'origine du nom, accroche) : « A busy 1930s American city street in late November, in front of a grand Art Deco department store with tall display windows and striped awnings: a slow traffic jam of round vintage cars and a tram, bumper to bumper, crawling forward very slowly, crowds of tiny shoppers seen as simple silhouettes on the far sidewalks carrying gift boxes, and in the middle of the crossroads, far away, a single traffic policeman seen from behind as a small silhouette raising one white-gloved hand. Warm golden afternoon light, a few autumn leaves drifting down. No character in the foreground. The camera slowly pushes in toward the department store entrance. »

2. [decor_hall] (le panier moyen et l'inflation) : « The grand ground-floor hall of a 1930s Art Deco department store, with no people: polished marble floor, brass and glass display counters, a sweeping double staircase, a row of ornate brass cash registers on a long wooden counter, shopping bags and wrapped gift boxes stacked neatly, garlands of red and gold ribbons hanging from the balconies, warm light from Art Deco chandeliers. Calm, empty, shining. The camera slowly glides forward along the counter of cash registers. »

3. [decor_rayon] (les fausses promotions et la règle des 30 jours) : « A single aisle inside a 1930s Art Deco department store, with no people: elegant shelves of boxed gramophones, radios, hat boxes and perfume bottles, and hanging in the center from two brass chains, a giant blank cream-colored paper price tag with a brass eyelet and a red string, completely blank with nothing written on it, swaying very gently. Soft spotlight on the giant tag, the rest of the aisle in warm shadow. The camera slowly pushes in toward the giant blank price tag. »

4. [decor_enquete] (les trois réflexes de l'investisseur) : « A cozy 1930s detective-style office at the back of a department store, with no people: a wide polished wooden desk seen from the front at eye level, its flat top running across the lower third of the frame with a clear empty space in the middle of the desktop (a character will sit on its front edge), a large brass magnifying glass, an open blank ledger, a brass desk lamp with a green shade, a tidy stack of paper receipts with no writing, a brass pocket watch, an empty corkboard on the back wall with pinned blank cards and red strings between them, a window with soft evening light. Calm, focused, a little mysterious. The camera slowly pushes in toward the desk. »

5. [decor_vitrine] (la question finale) : « The same grand Art Deco department store seen from the street at dusk, with no people: warm glowing display windows full of wrapped gifts, toy trains and gramophones, light snow falling slowly, a deep teal and violet evening sky, street lamps with a steady warm glow, wet cobblestones reflecting the windows. Peaceful and tempting. The camera slowly drifts sideways along the display windows. »

Sens du mouvement à vérifier à la réception : rue (avance vers l'entrée), hall (glisse le long des caisses), rayon et bureau (avancent), vitrine (glisse latéralement). Les voitures de la rue doivent avancer, pas reculer.

## Accessoires

Aucun à générer. L'étiquette de prix (prix barré, prix réel), les colonnes du panier 2022 à 2025, les jauges +8 % et +22 %, la courbe d'historique de prix et le compte à rebours barré sont faits en code dans nos plaques de verre.

## Mister Coin

Banque existante (tenue classique), sans répéter le même geste deux fois de suite :
1. Origine : parle_question, puis parle_explique.
2. Panier : parle_enthousiaste (on dépense toujours plus), reflechit en pose fixe dans le court silence.
3. Fausses promos : parle_confidence, puis choc et sceptique dans le silence.
4. Réflexes : assis sur le bord du bureau (jamais derrière : rien du décor devant lui, mains toujours visibles), assis_parle puis assis_loupe_parle (nouveaux), sinon pose fixe `assis` et parle_explique debout sur le bureau.
5. Chute : parle_question ou danse_parle_prudent.

Clips à générer (bloc commun renforcé de `mister_coin/veo/PROMPTS_GEMINI.md`, image `classique_reference_marges_16x9.jpg`, format 16:9), par ordre d'utilité :

1. [classique_assis_parle] « He is sitting on an invisible ledge at the height of his knees, facing the camera, legs bent and dangling forward, feet slightly apart, and explains something to the camera with small natural hand gestures, counting on his fingers. He stays seated in the same spot the whole time, his body does not move up or down. He talks continuously from the first to the last second, mouth always moving, no pause. » (début et fin : assis, mains sur les genoux, au lieu de la pose neutre debout)
2. [classique_assis_loupe_parle] « He is sitting on an invisible ledge at the height of his knees, facing the camera, legs dangling forward. He holds a large brass magnifying glass in one hand, examines something just in front of him with a sharp, curious look, his eye enlarged through the lens, then turns to the camera and keeps explaining. He stays seated in the same spot the whole time. He talks continuously from the first to the last second, mouth always moving, no pause. » (même pose assise au début et à la fin que le clip précédent)
3. [classique_sceptique] « He narrows his eyes, raises one eyebrow, crosses his arms and slowly shakes his head, unconvinced, as if looking at a suspicious price. He does not talk. »
4. [classique_parle_neutre] (toujours absent de la banque, en secours) « He explains something calmly to the camera with small natural hand gestures and slight head movements. His feet stay planted on the ground the whole time, he does not walk or step. He talks continuously from the first to the last second, mouth always moving, no pause. »

Si un clip manque : poses fixes `assis`, `loupe` et `sceptique` en fondu dans les silences, et parle_explique debout sur le bureau pour la scène 4.
Pour les deux clips assis, dans le bloc commun, remplace la phrase « The video starts and ends in the same neutral pose: standing still facing the camera, arms relaxed at his sides, gentle smile. » par : « The video starts and ends in the same seated pose: sitting on an invisible ledge facing the camera, legs dangling, hands resting on his knees, gentle smile. He remains seated for the entire video, he never stands up. »
