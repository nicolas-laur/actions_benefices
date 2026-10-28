# Banque Mister Coin : prompts Gemini (Veo)

Texte fourni par Nicolas le 28/10 (prompts établis le 26/10). Statut au 28/10 : 12 clips classiques sur 26 reçus.
Le dernier bloc en bas est la version renforcée du bloc commun (cohérence du personnage, grandes marges vertes) : c'est celle à utiliser.
Formats : 16:9 avec l'image de référence `classique_reference_marges_16x9.jpg` (ou `aristocrate_reference_marges_16x9.jpg` pour la tenue aristocrate).
Nommage dans le dépôt : `classique_<nom>.mp4` dans `mister_coin/veo/`, puis `python3 mister_coin/veo_catalogue.py` ; les réactions sont marquées `type: reaction` dans `catalogue.json`.

---

Voici la banque complète. Toutes les vidéos se génèrent avec la même image jointe : Mister Coin en pose de base sur fond vert. J'ai corrigé les deux défauts que tu as relevés. Dans les vidéos où il parle, il garde les pieds plantés au sol et parle du début à la fin sans s'arrêter. Chaque vidéo commence et se termine dans la même pose neutre, ce qui me permet de les enchaîner sans à-coup et de les répéter en boucle.
Bloc commun, à mettre au début de chaque prompt :
Animate the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick outlines, same proportions, same top hat and bow tie. Flat solid green background (#00FF00) for the entire video, no floor, no shadow, no other object or character, no text. Static camera, full body always visible, centered, same size during the whole video. The video starts and ends in the same neutral pose: standing still facing the camera, arms relaxed at his sides, gentle smile. Smooth classic hand-drawn animation. No music, no sound.
Ajoute ensuite l'action voulue. Le nom entre crochets est celui à donner au fichier quand tu me l'envoies.
1. Il parle (le cœur de la banque : feet planted, il parle tout du long)
Pour chaque prompt, ajoute à la fin : « His feet stay planted on the ground the whole time, he does not walk or step. He talks continuously from the first to the last second, mouth always moving, no pause. »
* [parle_neutre] « He explains something calmly to the camera with small natural hand gestures and slight head movements. »  ⏳ à générer
* [parle_enthousiaste] « He talks enthusiastically to the camera, eyebrows raised, big expressive hand gestures, small happy bounces on the spot. »  ✅ reçu
* [parle_explique] « He explains something important to the camera, counting on his fingers, then opening his palms toward the camera. »  ✅ reçu
* [parle_inquiet] « He talks to the camera with a worried face, eyebrows raised in the middle, hands nervously clasped in front of him. »  ✅ reçu
* [parle_triste] « He talks to the camera with a sad, disappointed face, shoulders down, arms hanging. »  ✅ reçu
* [parle_confidence] « He leans slightly toward the camera and talks as if sharing a secret, one hand next to his mouth. »  ✅ reçu
* [parle_question] « He asks the camera a question with a curious, playful face, one eyebrow raised, both palms open toward the camera. »  ✅ reçu
2. Il entre, il sort, il se déplace
* [entre_gauche] « He enters from the left edge of the frame with a bouncy cartoon walk, stops at the center and smiles at the camera. »  ✅ reçu (ancienne génération : clip_b)
* [entre_droite] « He enters from the right edge of the frame with a bouncy cartoon walk, stops at the center and smiles at the camera. »  ⏳ à générer
* [sort_droite] « He waves goodbye to the camera, turns and walks out through the right edge of the frame. The video ends on the empty green background. »  ⏳ à générer
* [sort_gauche] « He waves goodbye to the camera, turns and walks out through the left edge of the frame. The video ends on the empty green background. »  ⏳ à générer
* [saut_place] « He bends his knees, jumps high in the air with a squash-and-stretch effect and lands back on the same spot. »  ✅ reçu
Pour les entrées et les sorties, il ne doit pas revenir à la pose neutre au bord de l'image : c'est normal, je cale ce bord sur celui de l'écran.
3. Les réactions (dans les silences de la voix, sans parler)
Pour chaque prompt, ajoute à la fin : « He does not talk. »
* [joie] « He jumps for joy with both arms up and laughs, then calms down. »  ✅ reçu
* [rire] « He bursts out laughing, holding his belly, then calms down. »  ✅ reçu
* [pouce] « He gives the camera a big thumbs up with a wink. »  ✅ reçu
* [montre_haut_droite] « He points enthusiastically with his index finger toward the top right corner of the frame and looks there. »  ✅ reçu
* [montre_haut_gauche] « He points enthusiastically with his index finger toward the top left corner of the frame and looks there. »  ⏳ à générer
* [deception] « His smile fades, his eyebrows rise in worry, his arms drop and he sighs. »  ⏳ à générer
* [choc] « He is shocked: his eyes go wide, his jaw drops, his hat jumps up off his head and lands back on it. »  ⏳ à générer
* [facepalm] « He slowly puts his hand on his face, embarrassed, then shakes his head. »  ⏳ à générer
* [haussement] « He shrugs with both palms up, as if saying I don't know. »  ⏳ à générer
* [reflechit] « He thinks, one hand on his chin, looking up, then has an idea and raises his index finger. »  ⏳ à générer
* [sueur] « He looks nervous, a drop of sweat runs down his face and he pulls at his bow tie. »  ⏳ à générer
* [applaudit] « He claps his hands happily. »  ⏳ à générer
4. Les attentes (en boucle quand rien ne se passe)
* [attente] « He stands still, breathing gently, blinks twice and looks around calmly. He does not talk. »  ⏳ à générer
* [attente_pied] « He waits, tapping his foot and looking at the camera with a slight smile. He does not talk. »  ⏳ à générer
Par où commencer
Avec ta limite Gemini, commence par les vidéos les plus utiles : parle_neutre, parle_enthousiaste, parle_inquiet, entre_gauche, sort_droite, joie, deception et montre_haut_droite. Avec ces huit-là, je peux déjà monter une vidéo complète. Le reste viendra enrichir la banque au fil des jours.
Pour les formats, choisis 16:9 pour les entrées, les sorties et les sauts, parce qu'il faut de la place pour marcher. Le reste peut être en 16:9 ou en 9:16.
À chaque vidéo reçue, je découpe le fond, je l'ajoute à la banque dans le dépôt GitHub avec son nom, et je la règle à la bonne taille une fois pour toutes.

Animate the attached character exactly as drawn: same 1930s rubber-hose cartoon style, same colors, same thick outlines, same proportions, same top hat and bow tie. Flat solid green background (#00FF00) for the entire video, no floor, no shadow, no other object or character, no text. Static camera, full body always visible, centered, same size during the whole video. The video starts and ends in the same neutral pose: standing still facing the camera, arms relaxed at his sides, gentle smile. Smooth classic hand-drawn animation. No music, no sound. Keep exactly the same character design as the attached image throughout the video: round golden coin body (never stretched), thick golden rubber-hose arms and legs (not black, not thin), white gloves, brown shoes. Wide shot: keep a large empty green margin around him on all sides, his hands and cane must never touch or leave the edges of the frame.
Action : 
