# Prompts Gemini : top 10 % des salaires (vidéo du 24/11/2026)

Six nouveaux décors autour d'un gratte-ciel Art déco inspiré de l'Empire State, aucun accessoire nouveau, trois clips Mister Coin à compléter dans la banque. Le nom entre crochets est le nom de fichier à me renvoyer. Pense à les déposer tôt : l'affinage des décors (Real-ESRGAN puis 60 i/s) prend environ 2 h pour six décors.

## Décors (vidéo Veo, verticale 9:16 native, 8 s)

Bloc commun, à coller à la fin de chaque prompt de décor :

```
Style: 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette (warm yellows, teal, coral red, cream, polished brass and chrome), soft film grain, Art Deco architecture. Native vertical 9:16 video. No characters, no people, no text, no letters, no numbers, no logos, no signs. Very slow, continuous camera movement, no cuts, no flicker, no blinking lights. Keep the lower third calm and uncluttered (a character will stand there) and keep the upper middle of the frame fairly plain (information panels will be added there).
```

1. [decor_rue] (accroche et question finale) : « A 1930s Manhattan-style street at the foot of a gigantic Art Deco skyscraper inspired by the Empire State Building, seen from below in a dramatic low angle: limestone facade with vertical stripes, setbacks rising toward a shining chrome spire, warm golden late-afternoon light, a few vintage cars parked along the sidewalk (no plates), small clouds drifting slowly around the top. The camera very slowly tilts up along the facade toward the spire. »

2. [decor_hall] (l'indicateur et le Smic, rez-de-chaussée) : « The grand Art Deco lobby of a 1930s skyscraper: black and gold marble walls, geometric sunburst patterns, a polished terrazzo floor, a row of brass elevator doors with engraved Art Deco motifs. Above the central elevator door, a semicircular brass floor indicator dial with a pointer and no numbers, the pointer resting on the left. Warm light from Art Deco wall sconces. The camera slowly pushes in toward the central elevator. »

3. [decor_cabine] (la médiane, l'ascenseur monte) : « Inside a 1930s Art Deco elevator cabin, seen from the back of the cabin toward its front: wood-paneled walls with brass trim, a small round ceiling lamp, and at the front a closed brass folding accordion gate through which we see the shaft and the floors sliding smoothly downward as the elevator rises, each floor landing passing by with warm light. Above the gate, a small brass floor indicator dial with a slowly turning pointer and no numbers. Smooth continuous upward motion, no shaking. Static camera inside the cabin. »

4. [decor_etage] (le top 10 %, étage élevé) : « A luxurious 1930s Art Deco executive office high up in a skyscraper: tall windows with a breathtaking view over a Manhattan-style city far below, a polished wooden desk with a green banker's lamp and a fountain pen, leather armchairs, a globe on a stand, geometric gold patterns on the walls. Late-afternoon golden light floods in, a few small clouds drift by the windows. The camera slowly pushes in toward the windows. »

5. [decor_sommet] (le top 1 %, tout en haut) : « The open-air observation deck at the very top of a 1930s Art Deco skyscraper, right below the chrome spire: a brass railing in the foreground, the city tiny far below, clouds drifting slowly at the level of the deck, a glowing golden sunset sky, an airship far away on the horizon. Dizzying height, majestic and calm. The camera slowly drifts sideways along the railing. »

6. [decor_chantier] (le pont : ce qu'on garde et qu'on place) : « A cheerful 1930s cartoon construction site at sunrise: steel girders and wooden scaffolding, a small new Art Deco building growing floor by floor as golden coin-shaped bricks are lifted by a crane and stacked neatly, cement mixers, lunch boxes on a beam, a blue sky with soft clouds. Optimistic, patient atmosphere. The camera very slowly pushes in as the building gains one floor. »

Pour la chute, je reprends decor_rue (ou decor_sommet si le rendu du coucher de soleil est plus beau) : pas besoin d'un septième décor.

## Accessoires

Aucun nouveau. Le cadran d'étage animé (aiguille qui tourne jusqu'au palier) et les plaques de verre sont faits en code ; tirelire et pièces reprises des épisodes précédents si besoin.

## Mister Coin

Banque existante utilisée (tenue classique), sans répéter le même geste deux fois de suite : parle_question (accroche), parle_explique (Smic), parle_enthousiaste (top 10 %) puis pouce, parle_confidence (pont), parle_question ou danse_parle_prudent (fin), choc en secours au sommet.

Clips à générer (bloc commun renforcé de `mister_coin/veo/PROMPTS_GEMINI.md`, image `classique_reference_marges_16x9.jpg`, format 16:9), par ordre d'utilité :

1. [classique_parle_neutre] « He explains something calmly to the camera with small natural hand gestures and slight head movements. His feet stay planted on the ground the whole time, he does not walk or step. He talks continuously from the first to the last second, mouth always moving, no pause. » (la médiane ; déjà demandé le 21/11, toujours absent de la banque)
2. [classique_vertige] « He glances down as if standing at a great height, his eyes go wide, his knees wobble, he holds his top hat with one hand and leans back slightly, then recovers with a relieved smile. He does not talk. » (silence au sommet, après « plus de sept fois le Smic »)
3. [classique_reflechit] « He thinks, one hand on his chin, looking up, then has an idea and raises his index finger. He does not talk. » (silence après la médiane ; une pose fixe `reflechit` existe déjà en secours)

Si un clip manque, je me rabats sur la banque existante (choc au sommet, pose reflechit fixe en fondu) sans répéter le même geste deux fois de suite.

## Son

Ding d'ascenseur, grille en accordéon, moteur et arrêt de cabine : sons de synthèse originaux dans `sons_ascenseur.py` (essai : `essai_ascenseur.mp3`). Un seul coup de carillon à chaque arrivée d'étage, comme les ascenseurs qui montent.
