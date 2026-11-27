# 28/11 : Les Français de ton âge ont combien d'argent ?

1930 Technicolor, Mister Coin tout du long, accroche question, cible 60 à 75 s (80 s maximum). Roadmap : s-patrimoine-age. Angle, accroche et script validés par Nicolas le 27/11 (source à citer à la voix).

Fil rouge : une toise sur un chambranle de porte, dans une maison 1930. La caméra monte le long de la toise ; à chaque trait (petite plaque de laiton en saillie), une plaque de verre s'allume avec la tranche d'âge et sa médiane. Mister Coin saute de trait en trait et s'assoit au bord, jambes pendantes (bord suivi image par image). « Combien tu mesures, en euros ? »

Un seul indicateur : patrimoine brut médian du ménage (crédits non déduits), selon l'âge de la personne de référence, Insee, enquête Histoire de vie et Patrimoine 2023-2024, situation début 2024. Médiane seule (choix de Nicolas). Détail dans sources.md.

## Chiffres

| Repère | Valeur | Voix | Écran |
|---|---|---|---|
| Médiane, moins de 30 ans | 26 100 € | vingt-six mille cent euros | 26 100 € |
| Médiane, 30-39 ans | 146 200 € | cent quarante-six mille deux cents euros | 146 200 € |
| Rapport 30-39 / moins de 30 | 5,6 | plus de cinq fois plus | × 5,6 |
| Reste à rembourser, médiane des ménages endettés, 30-39 ans (toutes dettes) | 119 800 € | cent dix-neuf mille huit cents euros | 119 800 € |
| Médiane, 40-49 ans | 215 200 € | deux cent quinze mille deux cents euros | 215 200 € |
| Médiane, 50-59 ans (le sommet) | 254 100 € | deux cent cinquante-quatre mille cent euros | 254 100 € |
| Plateau : 60-69 ans et 70 ans ou plus | 245 000 € et 247 600 € | « après, ça plafonne » | non affiché |

## Texte pour la voix (sans balise de silence, à coller tel quel)

Les Français de ton âge ont combien d'argent ? Enregistre cette vidéo : tu reviendras te mesurer dans cinq ans.
Les chiffres viennent de la dernière enquête Patrimoine de l'Insee, début deux mille vingt-quatre. On compte tout ce que possède le ménage : livrets, placements, logement, sans retirer les crédits.
Moins de trente ans : la moitié des ménages a moins de vingt-six mille cent euros.
Trente à trente-neuf ans : cent quarante-six mille deux cents euros. Plus de cinq fois plus ! Le secret ? Souvent, un logement. Mais acheté à crédit : selon l'Insee, chez ceux qui empruntent, il reste en médiane cent dix-neuf mille huit cents euros à rembourser.
Quarante à quarante-neuf ans : deux cent quinze mille deux cents euros. Cinquante à cinquante-neuf ans : deux cent cinquante-quatre mille cent euros. Le sommet. Après, ça plafonne.
Ce qui fait grimper la marque, ce n'est pas que le salaire. C'est le temps : l'épargne de chaque mois, le crédit qui se rembourse, parfois un héritage, et des intérêts qui rapportent à leur tour.
Et toi, ta marque est au-dessus ou en dessous de ton âge ?

Silences de réaction réglés au montage : après « à rembourser » (Mister Coin s'éponge le front), après « ça plafonne » (il réfléchit).

## Découpage et écrans (texte des plaques de verre, Inter Display, pas de rouge)

Chaque plaque chiffrée porte en petit « Insee, enquête Patrimoine, début 2024 ».

| # | Décor | Voix | Plaques | Mister Coin |
|---|---|---|---|---|
| 1 | decor_couloir | accroche | « Les Français de ton âge ont combien ? », puis plaque « 🔖 Enregistre : remesure-toi dans 5 ans » (aime, enregistre, partage en grand, trois pictos) | entre en roulant sur sa tranche puis pivote (clip roule_entree), puis parle_question |
| 2 | decor_couloir (suite) | définition et source | « Patrimoine brut du ménage · crédits non déduits », « Source : Insee, enquête Histoire de vie et Patrimoine · début 2024 », en petit « Âge de la personne qui apporte le plus de revenus » | parle_explique |
| 3 | decor_toise_bas | moins de 30 ans | « Moins de 30 ans · 26 100 € · la moitié a moins » | assis sur le premier trait (compte_doigts) |
| 4 | decor_toise_milieu | 30-39 ans, crédit | « 30-39 ans · 146 200 € · × 5,6 », puis « Reste à rembourser (médiane, 30-39 ans endettés) · 119 800 € » | saute au trait suivant, parle_enthousiaste, puis sueur dans le silence |
| 5 | decor_toise_haut | 40-49 et 50-59 ans | « 40-49 ans · 215 200 € », puis « 50-59 ans · 254 100 € · le sommet », puis « Après 60 ans : ça plafonne » | saute de trait en trait, puis reflechit dans le silence |
| 6 | decor_horloge | le pont | quatre pictos en verre : épargne 🐖, crédit remboursé 🏠, héritage 🎁, intérêts composés 📈 | parle_confidence |
| 7 | decor_couloir (soir) ou decor_toise_haut | chute | « Et toi, ta marque est où ? », puis « Contenu pédagogique, pas un conseil en investissement » | parle_question (autre clip que la scène 1 si possible) |

## Animation (test du 27/11, décor bibliothèque)
- Clips de Mister Coin passés de 24 à 60 i/s par flux optique avant détourage (couleur et alpha déformés ensemble).
- Pieds accrochés au décor : suivi de caméra par points sur la surface où il se tient, lissé ; taille liée au travelling.
- Lumière : ombre de contact serrée plus ombre douce, reflet sur les surfaces vernies, flaque de lumière dorée et lueur autour de lui, light wrap sur les contours, teinte calée sur la couleur du décor, liseré chaud en haut de la pièce.
