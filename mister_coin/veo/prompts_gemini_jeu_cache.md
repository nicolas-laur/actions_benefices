# Prompts : le jeu caché « Mister Coin contre le Fisc » (26/11/2026)

Jeu de course automatique, déclenché par un appui long sur Mister Coin (souris ou doigt). Mister Coin court vers la droite, on touche l'écran pour sauter, il ramasse les pièces et évite les pièges pendant que ses poursuivants le talonnent par la gauche.

Mode d'emploi : une image par génération, 2 ou 3 essais, renvoie-moi le meilleur sous le nom indiqué en titre. Joins à chaque fois `classique_reference_marges_16x9.jpg` : pour Mister Coin c'est le modèle à redessiner, pour les autres personnages c'est la référence de style. Tous les éléments se font sur fond vert uni (je les détoure), sauf les décors. Aucun texte, chiffre ni logo dans les images : j'ajoute moi-même ce qui doit être écrit.

Les deux animations de Mister Coin (course et saut) passent par Veo, comme ses clips des vidéos : une image fixe ne suffit pas pour faire bouger ses jambes.

## 1. Mister Coin (Veo, 2 clips)

### jeu_coin_course.mp4

```
Animate the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick black outlines, same proportions, same top hat and bow tie, round golden coin body, thick golden rubber-hose arms and legs, white gloves, brown shoes. He is seen from the side in a three-quarter view, facing right, and runs in place in a joyful, bouncy 1930s cartoon run cycle: big strides, arms pumping, top hat bobbing, determined grin, glancing back over his shoulder once with a cheeky look. He stays centered in the frame and does not travel. Flat solid pure green background (#00FF00) everywhere, no floor, no shadow, no other character, no text. Static camera, no zoom, no cut. The run cycle loops seamlessly: the last frame matches the first.
```

### jeu_coin_saut.mp4

```
Animate the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick black outlines, same proportions, same top hat and bow tie, round golden coin body, thick golden rubber-hose arms and legs, white gloves, brown shoes. Seen from the side in a three-quarter view, facing right. He crouches, springs up in a big cartoon jump with knees tucked and arms raised, holds his top hat with one hand at the top of the jump, then lands softly back in the same spot with a little squash. He stays centered horizontally. Flat solid pure green background (#00FF00) everywhere, no floor, no shadow, no other character, no text. Static camera, no zoom, no cut.
```

## 2. Mister Coin, images fixes (Gemini)

Bloc commun à placer en tête des deux prompts suivants :

```
Redraw the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick black outlines, same proportions, same top hat and bow tie, round golden coin body, thick golden rubber-hose arms and legs, white gloves, brown shoes. Do not change his face design. Full body, centered, both hands fully visible. Flat solid pure green background (#00FF00) everywhere, no gradient, no floor, no cast shadow, no other character, no text. Clean crisp line art, highest resolution, square 1:1 framing with a wide empty green margin around him.
```

### jeu_coin_ko.png (fin de partie)

```
[bloc commun]
Pose: He sits on the ground, legs splayed, dazed after being caught, top hat crooked and squashed over one eye, three small cartoon stars and little birds circling above his head, dizzy spiral eyes, a goofy wobbly smile. Funny, never sad or hurt.
```

### jeu_coin_bouclier.png (avec le parapluie doré)

```
[bloc commun]
Pose: He runs to the right holding a big open golden umbrella above his head with both hands, a soft golden glow around the umbrella, confident grin.
```

## 3. Les poursuivants (Gemini)

Bloc commun à placer en tête de chaque prompt de cette partie :

```
Create an original cartoon character in exactly the same 1930s rubber-hose cartoon style as the attached reference image: same thick black outlines, same warm vintage colors, same simple shading, same pie-cut eyes and white gloves. Do NOT draw the golden coin character from the reference. Full body, seen from the side in a three-quarter view, running to the right in an exaggerated cartoon chase pose, comically villainous but friendly enough for all ages, never scary. Flat solid pure green background (#00FF00) everywhere, no gradient, no floor, no cast shadow, no other character, no text, no letters, no numbers, no logos, no flags, no real official insignia. Clean crisp line art, highest resolution, square 1:1 framing with a wide empty green margin around him.
```

### jeu_percepteur.png (le Fisc, chef des poursuivants)

```
[bloc commun]
Character: A tall, skinny 1930s tax collector in a black suit, bowler hat and round spectacles, a huge blank ledger tucked under one arm and a giant magnifying glass held out in front of him, pointing it at something ahead, sly grin, coattails flapping.
```

### jeu_banquier.png

```
[bloc commun]
Character: A round, short 1930s banker in a grey pinstripe waistcoat with a gold pocket-watch chain and a monocle, swinging a big butterfly net over his head, puffing cheeks, little legs running fast.
```

### jeu_frais.png (les frais, trois petits gremlins)

```
[bloc commun]
Character: Three small mischievous green gremlins in a row, each the size of a cat, sharp pointy ears, big grins with tiny teeth, scampering on all fours, one of them nibbling the edge of a blank golden coin. Group them close together as one sprite.
```

### jeu_taxe.png (la taxe volante)

```
[bloc commun, mais remplace « running to the right in an exaggerated cartoon chase pose » par « flying to the left toward the viewer's left side »]
Character: A flying blank cream-colored envelope with bat-like paper wings and a toothy cartoon grin where the flap opens, little angry eyes above the flap, no writing and no stamp on it.
```

### jeu_tampon.png (l'impôt, le tampon qui écrase)

```
[bloc commun, mais remplace « running to the right in an exaggerated cartoon chase pose » par « hovering, seen from the front »]
Character: A giant old-fashioned wooden rubber stamp with a round handle, cartoon eyes and frowning eyebrows on its handle, small rubber-hose arms with white gloves on its sides, ready to slam down. The rubber face underneath is plain red with no letters.
```

## 4. Les pièges (Gemini)

Bloc commun :

```
Draw a single object in exactly the same 1930s rubber-hose cartoon style as the attached reference image: same thick black outlines, same warm vintage colors, same simple shading. Do NOT draw the golden coin character. Seen from the side, slightly from above, resting on an invisible ground line at the bottom. Flat solid pure green background (#00FF00) everywhere, no gradient, no cast shadow, no character, no text, no letters, no numbers, no logos. Clean crisp line art, highest resolution, square 1:1 framing with a wide empty green margin around it.
```

### jeu_banane.png

```
[bloc commun]
Object: A big cartoon banana peel lying on the ground, bright yellow with brown tips, splayed open, glossy highlight.
```

### jeu_machoire.png

```
[bloc commun]
Object: An open spring-loaded jaw trap made of shiny gold metal with rounded cartoon teeth, a blank golden coin sitting in the middle as bait.
```

### jeu_egout.png

```
[bloc commun]
Object: An open round manhole in cobblestone pavement, its heavy cast-iron cover lying tilted beside it, a dark hole with two small glowing cartoon eyes peeking out from inside.
```

### jeu_factures.png

```
[bloc commun]
Object: A wobbly tall stack of blank cream papers and envelopes, slightly leaning, a few sheets sliding off the top, no writing on any sheet.
```

## 5. Les bonus (Gemini)

Même bloc commun que les pièges, en remplaçant « resting on an invisible ground line at the bottom » par « floating, centered ».

### jeu_lingot.png (vaut 10 pièces)

```
[bloc commun modifié]
Object: A shiny gold bar with a big cartoon sparkle on one corner and a soft golden glow, no engraving.
```

### jeu_parapluie.png (bouclier : protège d'un piège ou d'une prise)

```
[bloc commun modifié]
Object: A closed golden umbrella with a curved wooden handle, standing upright, wrapped in a soft golden glow and small sparkles.
```

### jeu_tirelire.png (aimant : attire les pièces pendant quelques secondes)

```
[bloc commun modifié]
Object: A round cream ceramic piggy bank with gold trim and a horseshoe magnet attached to its snout, little blue magnetic waves around the magnet.
```

Les pièces à ramasser existent déjà (pièces peintes du site), pas besoin d'en générer.

## 6. Les décors (Gemini, format 16:9)

Trois couches qui défilent à des vitesses différentes pour donner de la profondeur. Pas de fond vert ici. Demande-les en 16:9 à la meilleure définition. Le bord gauche et le bord droit doivent se raccorder ; si ce n'est pas parfait, je corrige le raccord moi-même.

Bloc commun :

```
Wide 16:9 background for a side-scrolling platform game, in exactly the same 1930s rubber-hose cartoon style as the attached reference image: thick black outlines, warm vintage colors, simple shading, slightly faded print texture. Do NOT draw the golden coin character, no characters at all, no text, no letters, no numbers, no signs with writing, no logos. The image must tile seamlessly horizontally: the left edge continues exactly into the right edge. Highest resolution.
```

### jeu_fond_ciel.png (couche lointaine)

```
[bloc commun]
Layer: A golden-hour sky with soft peach and gold gradient, big puffy cartoon clouds with thick outlines, a low warm sun near the horizon, nothing on the ground.
```

### jeu_fond_ville.png (couche du milieu)

```
[bloc commun]
Layer: A distant 1930s city skyline of Art Deco towers and grand bank buildings with columns and domes, in muted blue-grey tones, seen against a plain flat pale sky colour (#CFE3F0) that fills everything above the rooftops, so it can be cut out. The buildings fill only the lower two thirds of the image.
```

### jeu_fond_rue.png (couche proche, avec le sol)

```
[bloc commun]
Layer: A 1930s city street seen from the side: a cobblestone pavement running along the bottom fifth of the image as a flat walkable ground, old-fashioned street lamps, shop fronts with blank awnings and empty windows, a few potted plants. Everything above the shop fronts is a plain flat pale sky colour (#CFE3F0) so it can be cut out. Bright and cheerful.
```

## 7. L'écran titre (Gemini, 16:9)

### jeu_titre.png

```
Wide 16:9 illustration in exactly the same 1930s rubber-hose cartoon style as the attached reference, which shows the golden coin character Mister Coin: redraw him exactly as drawn (same top hat, bow tie, white gloves, brown shoes, same face design). He sprints to the right across a 1930s cobblestone street, holding his top hat on with one hand, grinning and glancing back. Behind him on the left, a comical chase: a skinny tax collector in a bowler hat waving a giant magnifying glass, a round banker with a monocle swinging a butterfly net, three small green gremlins, and a flying envelope with paper wings and a toothy grin. Golden coins scattered in the air. Leave the upper third of the image as calm sky with no important detail, for a title I will add. No text, no letters, no numbers, no logos. Highest resolution.
```

## Ordre conseillé

Commence par le clip de course et le percepteur : avec eux deux je peux monter une première version jouable, avec des décors provisoires. Les autres éléments s'ajoutent au fur et à mesure que tu me les envoies. En tout : 2 clips Veo et 18 images.
