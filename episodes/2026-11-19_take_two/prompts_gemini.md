# Prompts Gemini : Take-Two / GTA 6 (19/11/2026)

4 décors (vidéo 9:16, 8 s) dans l'esprit de l'ambiance de GTA 6, sans rien copier du jeu. Pas de logo, pas de texte, pas de personnage reconnaissable du jeu. Noms entre crochets = noms de fichier à me renvoyer. Les cases de BD seront assemblées au montage à partir de ces décors.

Bloc commun (à coller à la fin de chaque prompt de décor) :
"Style: bold illustrated video game loading-screen art, thick dark ink outlines, cel shading, saturated sunset palette of hot pink, orange, purple and teal, 1980s tropical neon city vibe. Vertical 9:16 framing. No people, no characters, no text, no letters, no numbers, no logos, no brand names. Very slow, continuous camera movement, no cuts, no flicker, neon lights glow steadily. Keep the lower third calm (a character will stand there)."

1. [decor_boulevard] (accroche) : "A tropical seaside boulevard at sunset: tall palm trees, art deco hotels with glowing pink and teal neon outlines, a shiny convertible sports car slowly cruising along the ocean, the sun setting into the sea. The camera slowly glides forward along the boulevard."
2. [decor_2013] (2013) : "A cozy late-night bedroom gaming setup from the early 2010s: a bulky TV glowing with abstract colorful light (no recognizable game), a game console and a controller on a low table, a window showing a neon city skyline at night, posters without any text. The camera slowly pushes in."
3. [decor_tour] (le résultat, l'action qui monte) : "A futuristic glass skyscraper at golden sunset seen from below, its windows reflecting pink and orange clouds, a rooftop helipad, money bills gently floating in the warm wind around the tower. The camera slowly tilts up the tower."
4. [decor_plage_nuit] (le piège et la fin) : "A beach at dusk under a violet sky, a lifeguard tower with soft neon lights, palm trees silhouetted, gentle waves, a pier with a Ferris wheel slowly turning in the distance. Static camera, smooth continuous motion."

## Mister Coin en action (plans complets, Veo, 9:16, 8 s)

Ce sont des plans finis, avec le décor : pas de fond vert, pas besoin de refaire toutes ses attitudes. Image jointe : `mister_coin/veo/classique_reference_marges_16x9.jpg`.

Bloc commun (à coller à la fin de chaque prompt de plan) :
"The attached character, exactly as drawn: same 1930s rubber-hose cartoon coin with face, same colors, thick outlines and proportions, same top hat, now wearing a colorful flowered Hawaiian shirt and round dark sunglasses. He is placed in a bold illustrated video game loading-screen world with thick ink outlines, cel shading, saturated sunset colors. Vertical 9:16. Cartoon action, playful and fun, no blood, no real weapons, no people from any existing game, no text, no logos, no brand names. Smooth continuous motion, no cuts."

Partie 1, Los Angeles (l'époque GTA 5) :
1. [mc_venice] « He rollerblades along the Venice Beach boardwalk in Los Angeles at golden hour, palm trees, skate park and muscle beach in the background, waving at the camera. Tracking shot following him. »
2. [mc_cabriolet] « He drives a shiny red convertible along a coastal highway above the Pacific at sunset, one hand on the wheel, the other arm on the door, wind in his shirt. Side tracking shot, then the car speeds away. »
3. [mc_pier] « He stands on the hood of his convertible parked near a Santa Monica style pier with a Ferris wheel, at dusk, raising his arms like a winner, neon lights turning on behind him. »

Partie 2, bascule dans l'ambiance GTA 6 (Miami néon) :
4. [mc_billets] « On a neon-lit Miami street at night, he stands on the roof of his convertible and fires a money gun into the air: a cartoon stream of banknotes flies everywhere and rains down, cartoon police sirens flash pink and blue in the background. Low angle shot. »
5. [mc_poursuite] « Cartoon car chase at night through a neon tropical city: he drives his convertible fast, cartoon police cars with flashing lights behind him, the car jumps over a small ramp in slow motion, banknotes flying out of the car. »
6. [mc_yacht] (fin) « He relaxes on the deck of a white yacht at sunset off a tropical skyline, sunglasses on, holding a video game controller, then turns to the camera with a big smile. Slow orbit around him. »

Pourquoi un pistolet à billets et pas une vraie fusillade : TikTok et Instagram réduisent la diffusion des vidéos avec des armes (et Veo refuse souvent de les générer). Le pistolet à billets garde l'esprit GTA, et il colle au sujet : l'argent.

## Transition « changement de personnage » (demandée le 16/11)
Référence : `references/transition_gta.mp4` (capture d'écran d'une vidéo YouTube, non versionnée, à ne pas réutiliser telle quelle). Le principe, emblématique du jeu : la caméra quitte la scène en montant d'un coup jusqu'à une vue satellite de la ville (léger voile vert/gris, grille de carte), glisse au-dessus de la carte, puis replonge en trois paliers vers la scène suivante, avec un « whoosh » sourd à chaque palier. On la recrée avec nos propres images, sans rien reprendre du jeu.
Images fixes à générer (Gemini image, format 9:16, la plus haute définition possible), même ville fictive vue strictement de dessus :
1. [carte_ville] « Strict top-down satellite photo of a fictional tropical coastal city at golden hour: grid of streets, palm-lined boulevards, beaches, a marina with yachts, a pier, glass towers casting long shadows, no text, no labels, no logos, photorealistic aerial imagery. »
2. [carte_quartier] « Same fictional tropical city, strict top-down satellite view closer in: one neighbourhood with a palm-lined seaside boulevard, art deco rooftops, pools, parked convertibles, no text, no labels, no logos. »
3. [carte_rue] « Same city, strict top-down aerial view very close: a single seaside street corner from above, palm tree crowns, cars, sidewalk, beach edge, no text, no labels, no logos. »
Montage : la scène quitte vers le haut (zoom arrière rapide), fondu vers carte_rue puis carte_quartier puis carte_ville (zoom arrière continu), court glissement, puis chemin inverse vers la scène suivante. Deux usages prévus : passage Los Angeles → nouvelle ambiance Miami, et éventuellement retour vers la fin.

## Reçus le 16/11
Décors : decor_boulevard, decor_2013, decor_tour, decor_plage_nuit (dans `decors/`). Plans de Mister Coin : mc_venice, mc_cabriolet, mc_pier, mc_billets, mc_poursuite (dans `plans/`). Manquent : mc_yacht et les trois images de carte pour la transition.
Cartes reçues le 16/11 (dossier `cartes/`) : carte_rue et carte_quartier (vue verticale, midi, cohérentes), carte_quartier_marina (même quartier avec marina et jetée, même altitude), carte_ville_v2_oblique_midi (vue oblique, lumière cohérente ; v1 au coucher du soleil écartée). Décision : on s'arrête là ; le sommet de la montée utilise carte_ville_v2, très bref, flouté par le mouvement et sous le voile de carte.
Son de la transition (16/11) : partie essentielle de l'effet. La référence enchaîne des impacts nets à chaque palier. On fabrique nos propres sons, sans rien reprendre du jeu ni de la capture : un « whoosh » montant (bruit filtré en balayage) à la montée, un impact sourd et grave à chaque palier (onde basse en chute de fréquence avec une attaque de bruit), un glissement aérien pendant le survol, des « whoosh » descendants à la plongée et un impact plus fort à l'arrivée. Musique et voix étouffées par un filtre passe-bas pendant la transition, puis rouvertes à l'arrivée. Vérifier le mixage à l'oreille (crêtes sous −1 dB).
Décision du 16/11 : Nicolas voulait reprendre les sons du jeu ; écarté (droits de Rockstar, détection automatique YouTube/Instagram, son compressé de la capture). À la place : sons fabriqués au plus près de l'original, en mesurant dans `references/transition_gta.mp4` le rythme des impacts, leur timbre et le souffle entre eux. Faire écouter la transition seule (avec et sans musique) à Nicolas avant de l'intégrer.
