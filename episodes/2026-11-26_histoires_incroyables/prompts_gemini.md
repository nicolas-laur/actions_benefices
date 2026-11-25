# Prompts Gemini : 3 histoires incroyables que tu ne connaissais peut-être pas ! (vidéo du 26/11/2026)

Quatre décors (prêteur sur gages, garage d'Apple, bibliothèque de Google, cinéma de Netflix). La chute revient au prêteur sur gages : pas de cinquième décor à générer, je le passe en lumière du soir au montage. Aucun clip Mister Coin à générer. Le nom entre crochets est le nom de fichier à me renvoyer. Dépose-les tôt : l'affinage (Real-ESRGAN puis interpolation 60 i/s par flux optique avec `interp_flow.py`) prend environ 2 h pour quatre décors.

## Décors (vidéo Veo, verticale 9:16 native, 8 s)

Bloc commun, à coller à la fin de chaque prompt de décor :

```
Style: 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette (warm yellows, teal, coral red, cream, polished brass and chrome), soft film grain, Art Deco architecture. Native vertical 9:16 video. No text, no letters, no numbers, no logos, no brand names, no signs with writing, no people, no characters. Very slow, smooth, continuous camera movement, no cuts, no shaking, no flicker, no blinking or flashing lights, all lights steady. Keep the lower third calm and uncluttered (a character will stand there) and keep the upper middle of the frame fairly plain (information panels will be added there).
```

1. [decor_preteur] (accroche et chute) : « The interior of a cozy 1930s Art Deco pawnshop, with no people: a long polished wooden counter seen from the front at eye level, its flat top running across the lower third of the frame with a clear empty space in the middle (a character will stand on it), a brass teller grille with a small arched window behind the counter, shelves full of pocket watches, gramophones, trumpets, cameras and jewelry boxes, a brass scale and a small pile of gold coins at one end of the counter, warm light from Art Deco wall lamps. Inviting and a little mysterious. The camera slowly pushes in toward the counter. »

2. [decor_garage] (Apple, 1976) : « A small suburban garage turned into an electronics workshop, painted in the 1930s cartoon style, with no people: a long wooden workbench seen from the front, its flat top running across the lower third of the frame with a clear empty space in the middle, covered on the sides with vintage radios, vacuum tubes, coils of copper wire, a soldering iron on its stand, a circuit board and screwdrivers; blank blueprints pinned on the wooden wall, the garage door wide open at the back onto a sunny street with palm trees and a blue sky, warm afternoon light coming in. Hopeful, handmade, the beginning of something big. The camera slowly pushes in toward the workbench. »

3. [decor_bibliotheque] (Google, 1999) : « A grand Art Deco library hall, with no people: endless walls of small wooden card catalog drawers with brass handles reaching up to a high painted ceiling, rolling brass ladders, tall bookshelves, rows of green banker's lamps with a steady warm glow, and in the foreground a long polished reading table seen from the front, its flat top running across the lower third of the frame with a clear empty space in the middle. Calm, vast, a place where you can find anything. The camera slowly pushes in along the central aisle toward the far end of the hall. »

4. [decor_cinema] (Netflix, 2000) : « The interior of a grand 1930s Art Deco movie palace, with no people: rows of red velvet seats seen from the center aisle, gold ornaments and sculpted columns on the walls, a large stage with a heavy red velvet curtain slowly opening on a blank, softly glowing white screen, a steady beam of light from the projection booth above, warm golden light. Magical, the start of a show. The camera slowly glides forward down the center aisle toward the screen. »

Sens du mouvement à vérifier à la réception : prêteur, garage et cinéma avancent ; bibliothèque avance le long de l'allée. Le rideau du cinéma doit s'ouvrir, pas se refermer. Si Gemini dessine malgré tout des pseudo-lettres (étiquettes, dos de livres, tiroirs), je les efface au nettoyage.

## Accessoires

Aucun à générer. L'étiquette de prix géante qui grimpe, le tampon « REFUSÉ », les montants barrés, les cadres Polaroïd et les tuiles logos (Apple, Google, Netflix, glyphes Simple Icons) sont faits en code dans nos plaques de verre.

## Photos des personnes (à fournir par Nicolas)

Une photo par personne, de face, nette, cadrage poitrine, dans `photos/` : `wayne.jpg`, `jobs.jpg`, `wozniak.jpg`, `page.jpg`, `brin.jpg`, `hastings.jpg`, `randolph.jpg`. En bonus : `bell.jpg` (Excite) et `antioco.jpg` (Blockbuster). Pour Wayne, Jobs et Wozniak, une photo des années 1970 renforcerait l'effet « avant et après ». Elles seront posées dans des cadres Polaroïd avec une courte fiche (nom, rôle, année).

## Mister Coin

Banque existante (tenue classique), sans répéter le même geste deux fois de suite :
1. Accroche (prêteur) : parle_question debout sur le comptoir, choc dans le court silence après « huit cents dollars » si le rythme le permet.
2. Apple (garage) : parle_explique debout sur l'établi, choc dans le silence après la revente.
3. Google (bibliothèque) : loupe_parle assis au bord de la table de lecture, jambes pendantes, bord suivi image par image pendant le travelling (il « cherche », clin d'œil au moteur de recherche), facepalm dans le silence après « Refusé encore ».
4. Netflix (cinéma) : danse_parle_swing pendant le travelling dans l'allée (de face, joué vers l'avant), puis parle_enthousiaste, rire dans le silence après « fait faillite ».
5. Chute (prêteur, lumière du soir) : parle_confidence pour « Une action, c'est un morceau d'entreprise », puis parle_question.

Aucun clip à générer pour cet épisode.
