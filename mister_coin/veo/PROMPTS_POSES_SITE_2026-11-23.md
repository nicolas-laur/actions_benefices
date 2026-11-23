# Poses de Mister Coin pour le site actionsbenefices.com (23/11/2026)

Images fixes pour illustrer le site : en-têtes de pages, récit de l'accueil, états du quiz et des outils. Chaque pose répond à un endroit précis du site où l'on réutilise aujourd'hui une pose de carrousel faute de mieux, ou qui n'a pas d'illustration du tout.

Ce qu'on a déjà, à ne pas refaire : choc, court, etoiles, facepalm, haussement, inquiet, joie, journal, loupe, montre, neutre, pouce, question, reflechit, rire, rocking, salut, sceptique, sueur, triste, assis. Écartées du site par Nicolas (jugées moches) : applaudit et doigt levé ; aucune pose ci-dessous n'en reprend le geste.

## Mode d'emploi

- Outil : Gemini (image), une pose par génération, avec l'image de référence jointe : `mister_coin/veo/classique_reference_marges_16x9.jpg`. Générer 2 ou 3 essais et garder le plus fidèle au personnage.
- Résolution : la plus haute proposée. Sur le site, les poses s'affichent jusqu'à 380 px de haut et sont exportées en 720 px pour les écrans Retina : il faut au moins 1 400 px de haut sur le personnage.
- Le nom entre crochets est le nom de fichier à me renvoyer. Je détoure le fond vert (`mister_coin/detoure_poses.py`), je range l'original dans `mister_coin/poses/` et j'exporte en WebP pour le site.
- Accessoires toujours vierges : aucune lettre, aucun chiffre, aucun logo, aucune marque. Le texte, c'est le site qui le pose à côté.

## Bloc commun, à coller au début de chaque prompt

```
Redraw the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick black outlines, same proportions, same top hat and bow tie, round golden coin body, thick golden rubber-hose arms and legs, white gloves, brown shoes. Do not change his face design or add any clothing or accessory other than the prop described below. Full body, centered, same size as in the attached image, both hands fully visible. Flat solid pure green background (#00FF00) everywhere, no gradient, no floor, no cast shadow, no other character, no text. Any prop is blank: no letters, no numbers, no logos, no brand marks. Clean crisp line art, highest resolution, vertical 3:4 framing with a wide empty green margin around him on all sides.
Pose:
```

## Priorité 1 : un en-tête par page

1. [site_calculatrice] Page Calculateurs. « He holds a chunky 1930s brass mechanical adding machine against his body with one arm and presses one of its round blank keys with the other index finger, focused and pleased, tongue slightly out. »
2. [site_dictionnaire] Page Lexique, à la place de « question ». « He holds a thick open leather-bound book in both hands, the pages are blank, and looks up from it at the viewer with a knowing, friendly smile, one eyebrow raised. »
3. [site_clap] Page Vidéos. « He holds a vintage black-and-white film clapperboard in both hands, blank slate, the striped clapstick open and about to snap shut, big cheerful grin and a wink. »
4. [site_enveloppe] Page Lettre du dimanche. « He holds out a cream-colored sealed envelope toward the viewer with both hands, closed with a round golden wax seal without any mark, proud and warm smile, as if handing over a gift. »
5. [site_carte_perdu] Page 404. « He holds a large unfolded blank parchment map upside down, scratches his head under his lifted top hat with the other hand, puzzled crooked smile, looking at the viewer. No question mark drawn. »

## Priorité 2 : les rubriques et les outils

6. [site_tirelire] Comparateur PEA/CTO, épargne. « He hugs a round cream ceramic piggy bank with gold trim, coin slot on top, cheek resting on it, eyes closed, content smile. »
7. [site_arrosoir] Intérêts composés. « He waters a small potted sapling whose round leaves are tiny shiny gold coins, using a vintage tin watering can, gentle droplets falling, patient happy smile. The pot and sapling stand beside him on the same invisible ground line. »
8. [site_longue_vue] Rubrique « À surveiller » des fiches, long terme. « He looks to the right through a long brass telescope held with both hands, one eye closed, the other wide behind the lens, leaning forward with curiosity. »
9. [site_balance] Comparaisons (rivaux, PEA contre CTO). « He holds an old brass balance scale up in one hand, a gold coin on each pan, the beam slightly tilted, and looks at it thoughtfully, other hand on his hip. »
10. [site_parapluie] Volatilité, baisses, risques. « He stands calmly under an open classic black umbrella held in one hand, a few gold coins falling around him like rain and bouncing off the umbrella, relaxed confident smile, other hand in a reassuring open-palm gesture. »
11. [site_graphique] Performances historiques. « He leans on a tall blank wooden easel board with one elbow; on the board a single hand-painted green arrow zigzags upward from bottom left to top right, no axis, no numbers. He looks at the viewer with a satisfied smile. »

## Priorité 3 : états et réactions du site

12. [site_trophee] Quiz réussi sans faute. « He lifts a small shiny golden trophy cup high above his head with both hands, jumping slightly, eyes closed with joy, mouth wide open in a happy shout. »
13. [site_ardoise] Quiz à retenter. « He holds a small blank school chalkboard in one hand and a piece of chalk in the other, kind encouraging teacher smile, head slightly tilted. »
14. [site_megaphone] Nouveautés, News de la semaine. « He shouts happily into a vintage cone-shaped brass megaphone held in one hand, pointing it to the right, other arm raised in excitement. »
15. [site_dort] Marchés fermés (week-end, nuit) dans le bandeau. « He sleeps standing up, leaning back slightly, arms crossed, eyes closed, peaceful smile, top hat tilted over one eye. No letters or z symbols. »
16. [site_coucou] Bords de page et pied de page. « He peeks in from the right edge of the frame: only his left half is visible, one gloved hand gripping the edge, waving with the other hand, friendly curious face. The cut at the right edge is clean and straight. »
17. [site_saut_joie] Inscription réussie, confettis. « He jumps high in a joyful star jump, arms and legs spread wide, top hat lifted a little off his head, huge open smile. »

## Pour plus tard (animations Veo, si on veut les faire bouger sur le site)

Les poses 3, 7, 12 et 15 gagneraient à exister en clip court (même bloc commun que les vidéos de `PROMPTS_BANQUE_2026-11-19.md`), pour le même traitement que les réactions actuelles de l'accueil.
