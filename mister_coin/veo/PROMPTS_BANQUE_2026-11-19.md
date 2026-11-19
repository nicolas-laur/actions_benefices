# Banque Mister Coin : compléments (19/11/2026)

Deux familles. Les vidéos (Veo) complètent la banque de `PROMPTS_GEMINI.md` : je reprends les clips encore manquants et j'ajoute de nouvelles réactions. Les images fixes alimentent les carrousels, qui n'ont aujourd'hui que 9 poses (choc, facepalm, inquiet, joie, montre, pouce, question, rire, triste).

Image jointe pour tout : `mister_coin/veo/classique_reference_marges_16x9.jpg`. Le nom entre crochets est le nom de fichier à me renvoyer.

## 1. Vidéos (Veo, 16:9)

Bloc commun, à mettre au début de chaque prompt :

```
Animate the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick outlines, same proportions, same top hat and bow tie. Flat solid green background (#00FF00) for the entire video, no floor, no shadow, no other object or character, no text. Static camera, full body always visible, centered, same size during the whole video. The video starts and ends in the same neutral pose: standing still facing the camera, arms relaxed at his sides, gentle smile. Smooth classic hand-drawn animation. No music, no sound. Keep exactly the same character design as the attached image throughout the video: round golden coin body (never stretched), thick golden rubber-hose arms and legs (not black, not thin), white gloves, brown shoes. Wide shot: keep a large empty green margin around him on all sides, his hands and cane must never touch or leave the edges of the frame.
Action :
```

### Priorité 1 : les trous de la banque actuelle

Pour [parle_neutre], ajoute à la fin : « His feet stay planted on the ground the whole time, he does not walk or step. He talks continuously from the first to the last second, mouth always moving, no pause. » Pour toutes les réactions, ajoute : « He does not talk. »

- [parle_neutre] « He explains something calmly to the camera with small natural hand gestures and slight head movements. » C'est la pose de base quand il parle, celle qui manque le plus.
- [deception] « His smile fades, his eyebrows rise in worry, his arms drop and he sighs. »
- [haussement] « He shrugs with both palms up, as if saying I don't know. »
- [reflechit] « He thinks, one hand on his chin, looking up, then has an idea and raises his index finger. »
- [sueur] « He looks nervous, a drop of sweat runs down his face and he pulls at his bow tie. »
- [applaudit] « He claps his hands happily. »
- [sort_droite] « He waves goodbye to the camera, turns and walks out through the right edge of the frame. The video ends on the empty green background. »

### Priorité 2 : nouvelles réactions utiles pour la finance

- [salut_chapeau] « He lifts his top hat politely to greet the camera with a small bow, then puts it back on. He does not talk. » Pour l'ouverture et la fin des vidéos.
- [doigt_non] « He wags his index finger left and right with a friendly but firm face, as if saying no no no. He does not talk. » Pour les pièges et les idées reçues.
- [sceptique] « He crosses his arms, raises one eyebrow and squints doubtfully at the camera, then slowly uncrosses his arms. He does not talk. »
- [regarde_montre] « He pulls a small golden pocket watch from behind his body, checks the time with a raised eyebrow, then puts it away. He does not talk. » Pour les sujets sur le temps et les intérêts composés.
- [soulagement] « He wipes his forehead with the back of his glove and lets out a big relieved sigh, then smiles. He does not talk. » Pour un rebond après une baisse.
- [attente] « He stands still, breathing gently, blinks twice and looks around calmly. He does not talk. »

### Plus tard

[entre_droite], [sort_gauche] et [attente_pied] sont dans `PROMPTS_GEMINI.md`. [montre_haut_gauche] peut attendre, je l'obtiens déjà en retournant [montre_haut_droite] en miroir.

## 2. Images fixes pour les carrousels (9:16)

Bloc commun, à mettre au début de chaque prompt :

```
Redraw the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick outlines, same proportions, same top hat and bow tie, round golden coin body, thick golden rubber-hose arms and legs, white gloves, brown shoes. Full body, centered, same size as in the attached image. Flat solid green background (#00FF00), no floor, no shadow, no other object, no text. Vertical 9:16 framing with a large empty green margin around him on all sides, both hands fully visible.
Pose :
```

Par ordre d'utilité :

1. [reflechit] « He thinks, one hand on his chin, eyes looking up, one eyebrow raised. » Pour les diapos « piste de lecture ».
2. [haussement] « He shrugs with both palms up and a puzzled smile, as if saying who knows. » Pour les résultats incertains.
3. [sceptique] « He crosses his arms and raises one eyebrow, squinting doubtfully. »
4. [assis] « He sits on an invisible ledge, legs dangling in front of him, hands resting on the ledge at his sides, relaxed smile. The ledge itself is not drawn. » Pour le poser sur le bord haut d'un panneau, comme sur le comptoir que tu avais aimé.
5. [lit_journal] « He holds a big open blank newspaper with both hands and reads it with wide curious eyes, the newspaper pages are blank, no letters. » Pour la couverture des News du vendredi.
6. [doigt_non] « He wags his index finger with a friendly but firm face, as if saying no no no. »
7. [applaudit] « He claps his hands happily, eyes closed with joy. »
8. [sueur] « He looks nervous, a drop of sweat on his forehead, one finger pulling at his bow tie. »
9. [salut_chapeau] « He lifts his top hat politely with one hand and makes a small bow. » Pour la diapo finale « abonne-toi ».
10. [etoiles] « He is amazed, his eyes turned into two shining golden stars, mouth wide open in a happy O, hands on his cheeks. » Tu avais apprécié les étoiles dans les yeux sur une couverture : autant l'avoir en pose fixe.

Je détoure tout ce que tu m'envoies et je range les images fixes dans `mister_coin/poses/` pour que chaque carrousel puisse y piocher, au lieu de recopier le dossier `coin/` d'un épisode à l'autre.
