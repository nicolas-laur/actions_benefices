# Prompts Gemini : action, obligation, fonds euros (11/11/2026)

3 décors animés (vidéo 9:16, 8 s) et 9 accessoires sur fond vert. Rien de réutilisé des épisodes précédents.

## Décors

Common block (paste at the end of each décor prompt):
"Style: 1930s rubber hose cartoon background, hand-painted gouache, Fleischer and early Disney Technicolor palette (warm yellows, teal, coral red, cream), soft film grain. Vertical 9:16 framing. No characters, no text, no logos. Very slow, continuous camera movement, no cuts, no flicker. Keep the lower third calm and uncluttered (a character will stand there)."

1. decor_rue : "A cozy 1930s town street with a charming bakery storefront in the center, striped awning, big shop window with loaves and pastries, a blank wooden sign above the door, a second empty shop next door with a 'for rent' feeling (empty window), cobblestones, warm morning light, gentle steam from a chimney."
2. decor_fournil : "Inside a warm 1930s bakery: wooden counter, shelves full of golden loaves and croissants, a big brick bread oven glowing softly in the background, flour dust floating in sunbeams, copper scales on the counter."
3. decor_coffres : "A grand 1930s bank vault hall: a huge round steel vault door half open in the background, marble floor, brass railings, rows of safe deposit boxes on the walls, warm chandelier light, calm and reassuring atmosphere."

## Accessoires (image fixe, fond vert uni #00FF00)

Common block (paste at the end of each prop prompt):
"1930s rubber hose cartoon style, Technicolor palette, thick dark brown outlines, soft painted shading and a small glossy highlight. Single object, centered, fully visible with generous margins, no shadow on the ground, isolated on a flat pure green background (#00FF00), no text, no logos."

1. certificat_action : "An ornate vintage share certificate on cream paper with a decorative green guilloche border, a blank title area and a red wax seal, slightly curled corners."
2. obligation_coupons : "An ornate vintage bond certificate on pale blue paper with a row of small detachable coupons along the bottom edge, decorative border, blank text areas."
3. croissant : "A golden flaky croissant, appetizing and glossy."
4. pain : "A golden crusty baguette loaf, slightly tilted."
5. coffre : "A sturdy round-cornered steel safe with a brass dial and a big handle, door closed, cartoon style."
6. parapluie : "An open red umbrella seen slightly from below, wooden curved handle, sheltering gesture."
7. pancarte : "A blank wooden hanging sign on two short ropes, light wood with a dark brown border, no text."
8. tirelire_fissuree : "A pink ceramic piggy bank with a big crack on its side, a few coins falling out."
9. poignee_de_main : "Two cartoon hands in white gloves shaking hands, seen from the side, friendly and sealing a deal."

## Mister Coin Boulanger (second personnage)

Étape 1, l'image de référence (Gemini image, en joignant `mister_coin/veo/classique_reference_marges_16x9.jpg`) :
"Redraw the attached character as his cousin, a baker: same 1930s rubber-hose cartoon style, same round coin body, same thick outlines, same rubber-hose arms and legs, white gloves, brown shoes, same size. Differences: his coin body is warm copper instead of gold, he has a big curly black mustache, rosy cheeks with a little flour on them, a tall white baker's toque instead of the top hat, a white apron tied around his body, a red neckerchief instead of the bow tie. Standing still facing the camera, arms relaxed at his sides, gentle proud smile. Flat solid green background (#00FF00), no floor, no shadow, no text. 16:9 wide shot with a large empty green margin around him on all sides."

Étape 2, les clips (Veo, 16:9, avec l'image de l'étape 1 jointe). Bloc commun en tête de chaque prompt :
"Animate the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick outlines, same proportions, same white baker's toque, mustache, apron and red neckerchief. Flat solid green background (#00FF00) for the entire video, no floor, no shadow, no other object or character, no text. Static camera, full body always visible, centered, same size during the whole video. The video starts and ends in the same neutral pose: standing still facing the camera, arms relaxed at his sides, gentle smile. Smooth classic hand-drawn animation. No music, no sound. Keep exactly the same character design throughout: round copper coin body (never stretched), thick rubber-hose arms and legs, white gloves, brown shoes. Wide shot: keep a large empty green margin around him on all sides, his hands must never touch or leave the edges of the frame. He does not talk, his mouth stays closed or smiling. His feet stay planted on the ground."

Puis l'action (le nom entre crochets est le nom du fichier) :
1. [boulanger_attente] "He stands proudly, breathing gently, dusts a little flour off his apron, blinks and smiles."
2. [boulanger_salut] "He waves warmly at the camera with one hand, proud and welcoming."
3. [boulanger_offre_gauche] "He turns slightly to the left of the frame and holds out both open hands toward the left, as if offering something precious to someone standing there, with a proud smile."
4. [boulanger_main_gauche] "He turns slightly to the left of the frame and holds out his right hand toward the left for a friendly handshake, nodding."
5. [boulanger_joie] "He is overjoyed: he throws both arms up and does a little happy dance on the spot, his toque wobbling, then calms down."
6. [boulanger_paie] "He counts out coins one by one from his left palm with his right hand, then holds them out toward the left of the frame, generous and honest."
7. [boulanger_triste] "He is devastated: his mustache droops, his toque slowly flops over, he wipes a tear with his glove and his shoulders drop."
8. [boulanger_reflechit] "He scratches his head under his toque, thinking hard, then raises his index finger with an idea."

Les 4 indispensables si tu dois choisir : attente, offre_gauche, main_gauche, triste.
