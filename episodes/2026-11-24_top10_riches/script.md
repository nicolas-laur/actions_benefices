# 24/11 : Combien il faut gagner pour faire partie des 10 % les plus riches ?

1930 Technicolor, Mister Coin tout du long, accroche question, cible 60 à 75 s (80 s maximum). Roadmap : s-top10-riches. Script validé par Nicolas le 22/11.

Fil rouge : un gratte-ciel Art déco inspiré de l'Empire State, Mister Coin monte en ascenseur, chaque étage est un palier de salaire. Un seul indicateur, dit à l'écran : salaire net mensuel en équivalent temps plein, salariés du privé, données 2025 (Insee). Ding d'ascenseur à chaque arrêt (`sons_ascenseur.py`, un seul coup de carillon à la montée).

## Chiffres (détail dans sources.md)

| Palier | Valeur | Voix | Écran |
|---|---|---|---|
| Smic net mensuel temps plein (en vigueur depuis le 01/06/2026) | 1 477,93 € | environ mille cinq cents euros | 1 478 € |
| Médiane 2025 | 2 238 € | deux mille deux cent trente-huit euros | 2 238 € |
| Seuil des 10 % les mieux payés (D9) 2025 | 4 441 € | quatre mille quatre cent quarante et un euros | 4 441 € |
| Seuil du 1 % (C99) 2025 | 10 552 € | dix mille cinq cent cinquante-deux euros | 10 552 € |

Rapports : D9 / médiane = 1,98 (« à peine le double ») ; C99 / médiane = 4,71 (« presque cinq fois ») ; C99 / Smic = 7,14 (« plus de sept fois »).

## Texte pour la voix (sans balise de silence, à coller tel quel)

Combien tu dois gagner pour faire partie des dix pour cent les mieux payés de France ? Monte avec moi, on va voir à quel étage tu t'arrêtes.
On parle salaire net par mois, à temps plein, dans le privé. Rez-de-chaussée : le Smic, environ mille cinq cents euros.
Premier arrêt : deux mille deux cent trente-huit euros. C'est la médiane : la moitié des salariés gagne moins que ça.
On continue de monter. Quatre mille quatre cent quarante et un euros : à partir de là, tu fais partie des dix pour cent les mieux payés. À peine le double de la médiane.
Et tout en haut ? Pour entrer dans le un pour cent, il faut dix mille cinq cent cinquante-deux euros par mois. Presque cinq fois la médiane, plus de sept fois le Smic.
Mais le salaire ne fait pas tout. Sur une vie, ce qui compte, c'est ce que tu gardes chaque mois et ce que tu en fais.
Et toi, tu es à quel étage ?

Silences de réaction réglés au montage : après « gagne moins que ça » (Mister Coin réfléchit), après « plus de sept fois le Smic » (vertige au sommet).

## Découpage et écrans (texte affiché dans les plaques de verre)

| # | Décor | Voix | Plaques | Mister Coin |
|---|---|---|---|---|
| 1 | decor_rue | accroche | « Top 10 % : combien faut-il gagner ? » | parle_question |
| 2 | decor_hall | indicateur + Smic | « Salaire net mensuel · temps plein · salariés du privé », puis « RDC · Smic 1 478 € » | parle_explique |
| 3 | decor_cabine | médiane | cadran d'étage + « 2 238 € · Médiane : la moitié gagne moins » | parle_neutre, puis reflechit |
| 4 | decor_etage | top 10 % | « 4 441 € · Top 10 % · ≈ 2 × la médiane » | parle_enthousiaste, pouce |
| 5 | decor_sommet | top 1 % | « 10 552 € · Top 1 % · ≈ 5 × la médiane » | parle_question ou confidence, puis vertige |
| 6 | decor_chantier | pont | « Le salaire classe. L'épargne construit. » | parle_confidence |
| 7 | decor_rue (soir) ou decor_sommet | chute | « Et toi, tu es à quel étage ? », puis « Source : Insee, salaires du privé 2025 · Contenu pédagogique, pas un conseil en investissement » | parle_question (clip différent de la scène 1 si possible) |
