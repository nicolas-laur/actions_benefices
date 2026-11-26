# Compte rendu de veille : Les News du vendredi 27/11/2026

Préparé le jeudi 26/11 au soir par la tâche programmée. Semaine couverte : lundi 23 au jeudi 26 novembre 2026.

Point important avant tout : le carrousel du 27/11 existe déjà dans ce dossier (commit « Les News du 27/11 », 8 sujets, décors générés, `sources.md` et `description.txt`). Ce compte rendu ne le remplace pas. Il recoupe ses chiffres avec d'autres sources, signale les écarts, et ajoute les faits « portefeuille français » qui n'y figurent pas (Livret A, carburant, budget). Pour ne pas écraser les prompts déjà utilisés, les prompts des nouveaux sujets sont dans `prompts_gemini_veille.md` et non dans `prompts_gemini.md`.

Cadre des chiffres :
- Wall Street fermée le jeudi 26/11 (Thanksgiving) ; vendredi 27/11, séance écourtée, clôture à 13 h heure de New York (19 h à Paris) selon le calendrier repris par Stock Market Watch. Tous les cours américains ci-dessous sont donc des clôtures du mercredi 25/11.
- Paris : clôture du jeudi 26/11.
- Conversion au taux de référence BCE du 26/11/2026 : 1 € = 1,0975 $ (déjà retenu dans `sources.md`). Indices hors dividendes.

## 1. Les 10 faits marquants, classés pour notre public

### 1. Nvidia : Jensen Huang revient, l'action fait +31,48 % en un jour
Le 23/11, le conseil d'administration réintègre Jensen Huang comme président et directeur général, onze jours après sa démission. L'action passe de 125,53 $ à 165,05 $ (150,39 €) en une séance, sa plus forte hausse depuis mai 2003, soit environ 952 Md$ (867 Md€) de valeur gagnée. Elle reprend ensuite son souffle : 149,30 $ (136,04 €) à la clôture du mercredi 25/11 (−3,91 % ce jour-là). Leçon pédagogique : en bourse, la confiance dans un dirigeant a un prix.
Sources : communiqué Nvidia (8-K) https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000090/nov23pressrelease.htm ; CNN https://edition.cnn.com/2026/11/23/business/live-news/jensen-huang-reinstated-as-ceo-of-nvidia ; clôture du 25/11 : https://www.techi.com/chip-stocks-recover-early-slide-nasdaq-close-november-25/

### 2. Wall Street rebondit après sa pire semaine
La semaine précédente avait été très dure : vendredi 20/11, le S&P 500 finissait à 6 910,39 points (−8,6 % sur la semaine), le Nasdaq à 22 617,73 (−10 %), et le S&P 500 entrait en « correction » (plus de 10 % sous son record du 6 octobre). Du vendredi 20 au mercredi 25/11, le rebond est net : S&P 500 7 182,78 (+3,94 %), Dow Jones 50 182,95 (+4,23 %), Nasdaq 23 585,80 (+4,28 %), hors dividendes, calcul de notre part. Mercredi, le Dow a même effacé une baisse de plus de 1 100 points en séance. Bon sujet pour expliquer ce qu'est une correction.
Sources : AP via Yahoo Finance (clôtures du 20/11) https://finance.yahoo.com/markets/stocks/articles/major-us-stock-indexes-fared-213016263.html ; Motley Fool (25/11) https://www.fool.com/coverage/stock-market-today/2026/11/25/stock-market-today-nov-25-dow-erases-1-100-point-loss-as-wall-street-stages-dramatic-late-day-comeback/ ; Stock Market Watch https://stockmarketwatch.com/digest/2026-11-25

### 3. Livret A : 9,54 Md€ retirés depuis janvier, plus que sur toute l'année 2015
Chiffres de la Caisse des Dépôts publiés le 24/11 : en octobre, le Livret A perd 2,62 Md€ nets (encours 440,1 Md€), le LDDS 0,94 Md€, le LEP 1,51 Md€. Depuis janvier, le Livret A a perdu 9,54 Md€, plus que sur toute l'année 2015 (9,29 Md€), jusqu'ici la pire depuis 2009. Raisons avancées : taux de 1,7 % inférieur à l'inflation (3,4 % en octobre selon l'AOF), impôts et taxe foncière d'octobre. Le Premier ministre a annoncé le 3/11 un relèvement du plafond (aujourd'hui 22 950 €) et du taux en février, montant et taux pas encore fixés. Le 2,6 % au 1er février 2027 est une prévision du Cercle de l'Épargne, pas une décision. Sujet très proche de notre public.
Sources : Caisse des Dépôts https://www.caissedesdepots.fr/presse/epargne-reglementee-collecte-mensuelle-en-octobre-2026-du-livret-et-du-ldds-ainsi-que-du-lep (PDF : https://www.caissedesdepots.fr/sites/cdc.fr/files/2026-11/2026%2011%2024%20-%20Communiqu%C3%A9%20Collecte%20mensuelle%20LA-LDDS%20-%20LEP%20octobre26.pdf) ; France Épargne https://www.france-epargne.fr/news/livret-a-954-milliards-deuros-de-retraits-nets-depuis-janvier-deja-plus-quen-2015 ; Boursorama (AOF) https://www.boursorama.com/bourse/actualites/livret-a-une-huitieme-decollecte-record-en-octobre-sur-fond-d-inflation-et-d-impots-3296d508f3d1e5b9c3abb59107390c2e

### 4. Inflation américaine à 3,8 % : la Fed pourrait remonter ses taux
Le 25/11, l'indice PCE d'octobre (celui que suit la Fed) ressort à +3,8 % sur un an, +3,3 % hors énergie et alimentation. La croissance du 3e trimestre est révisée à +4,3 % en rythme annualisé. Après ces chiffres, les marchés donnent 97 % de probabilité à une hausse du taux directeur (aujourd'hui 3,75-4 %) lors de la réunion des 8 et 9 décembre. Pour un débutant : une hausse de taux rend le crédit plus cher et pèse souvent sur les actions.
Sources : BEA https://www.bea.gov/news/2026/personal-income-and-outlays-october-2026 et https://www.bea.gov/news/2026/gdp-second-estimate-and-corporate-profits-3rd-quarter-2026 ; Fox Business (FedWatch) https://www.foxbusiness.com/markets/stocks-11-25-2026

### 5. Droits de douane : 15 % proposés sur l'Union européenne
Le 25/11, les États-Unis proposent des droits de douane sur 14 économies après une enquête de huit mois (Section 301) : 15 % pour l'UE au départ (possible hausse à 20 %), 20 % pour la Chine et le Vietnam. Rien n'entre en vigueur avant janvier 2027 au plus tôt, après consultation publique. À présenter de façon factuelle, sans commentaire politique.
Sources : CNN https://www.cnn.com/2026/11/25/economy/trump-new-tariffs ; RTÉ https://www.rte.ie/news/us/2026/1125/1600630-us-tariffs/

### 6. Paris : le CAC 40 repasse au-dessus des 8 100 points
Le CAC 40 finit jeudi à 8 108,74 points (+1,61 %), avec 39 valeurs sur 40 en hausse, malgré des volumes faibles (Wall Street fermée). Sur la semaine, du vendredi 20 au jeudi 26/11 : +2,28 % hors dividendes. Jeudi, Stellantis +8,9 %, Soitec +7 %, Renault +5,7 %, STMicroelectronics +4,5 % ; seule baisse, EssilorLuxottica (−0,20 %).
Sources : BFM Bourse https://www.tradingsat.com/cac-40-FR0003500008/actualites/cac-40-alors-que-wall-street-celebre-thanksgiving-le-cac-40-cede-a-l-euphorie-et-termine-en-hausse-d-16-1174500.html ; clôture du 20/11 : https://www.zonebourse.com/cours/indice/CAC-40-4941/

### 7. Sanofi s'offre Insmed pour 41 Md$
Annonce du 24/11 : Sanofi rachète l'américain Insmed 175 $ par action (159,45 €) en numéraire, soit une prime d'environ 46 % et environ 41 Md$ (37,6 Md€ selon le communiqué). Le 25/11, l'action Sanofi gagne 4,89 % à 98,16 €. Bon exemple pour expliquer une « prime de rachat » et une valeur du CAC qui concerne beaucoup de PEA.
Sources : communiqué Sanofi https://www.sec.gov/Archives/edgar/data/0001104506/000114036126045364/ef20086426_ex99-1.htm ; Idéal Investisseur https://www.ideal-investisseur.fr/bourse-cryptos/le-cac-40-recule-en-cloture-plombe-par-les-semi-conducteurs-et-lelectrique-34079.html

### 8. Anthropic passe sous son prix d'introduction
Une semaine après une introduction record (près de 120 Md$ levés, environ 109 Md€, prix fixé à 83 $ soit 75,63 €), l'action clôture le 24/11 à 81,90 $, sous ce prix, après un pic à 115,10 $ le jour de l'introduction. Clôture du 25/11 : 82,79 $ (75,44 €). Leçon : une introduction très médiatisée ne garantit pas la hausse.
Sources : BFM Bourse https://www.tradingsat.com/actualites/informations-societes/apres-des-debuts-en-fanfare-a-wall-street-anthropic-efface-plus-de-la-totalite-de-sa-hausse-perd-30-par-rapport-a-son-pic-et-repasse-sous-son-cours-d-introduction-1174353.html ; Yahoo Finance https://finance.yahoo.com/quote/ANT/

### 9. Carburant : le gazole recule encore
Moyenne nationale du gazole : 2,150 €/L le lundi 16/11, 2,077 €/L le jeudi 26/11 (−7,3 centimes) ; SP95-E10 de 1,990 à 1,936 €/L. Depuis le 1er novembre (2,339 €/L), le gazole a perdu 26,2 centimes, mais reste très au-dessus de son niveau du début d'année. Les relevés varient selon la méthode (Roole donnait 2,125 €/L le 24/11 au matin contre 2,108 €/L pour Carbu.fr) : citer une seule source.
Sources : Carbu.fr https://carbu.fr/actu/2026-11/ ; Roole https://media.roole.fr/quotidien/au-volant/prix-des-carburants-voici-les-tarifs-en-france-ce-mardi-24-novembre-2026

### 10. Dell, l'or et le bitcoin : trois chutes, trois raisons
Dell publie le 24/11 un chiffre d'affaires record de 54,9 Md$ (50,0 Md€, +103 %) et relève sa prévision annuelle à 202 Md$, mais l'action perd 11,83 % le lendemain, après +20,46 % la veille. L'or passe sous 3 500 $ l'once (environ 3 163 € à 3 471,52 $), à −37 % de son plus haut. Le bitcoin passe sous 58 000 $ (environ 52 850 €), −25 % depuis le 1er novembre. Utile pour montrer que « bonne nouvelle » ne veut pas dire « hausse ».
Sources : communiqué Dell https://www.sec.gov/Archives/edgar/data/0001571996/000157199626000050/exhibit991earnings8kq3fy27.htm ; Yahoo Finance (or) https://finance.yahoo.com/markets/commodities/articles/gold-price-today-november-25-110850194.html ; KuCoin/CoinGlass (bitcoin) https://www.kucoin.com/news/flash/bitcoin-falls-below-58k-as-november-losses-exceed-25

### À surveiller, sans en faire une news
Budget 2027 : l'Assemblée a rejeté la partie recettes le 4/11 (458 voix contre 0) ; le Sénat examine le texte initial depuis le 20/11, vote prévu le 9/12. Pour l'épargne : flat tax à 31,4 % inchangée, aucun article sur le PEA ; le relèvement du plafond du PEA-PME à 300 000 € (aujourd'hui 225 000 €), voté par les députés, est tombé avec le rejet. Rien n'est acté : à garder pour une news quand le texte sera voté, sans prise de position.
Sources : NosParlementaires https://nosparlementaires.fr/actualites/budget-2027-epargnants-ce-qui-change ; La Centrale des SCPI https://www.centraledesscpi.com/article/budget-2027-rejete-assemblee-epargne-ce-que-le-senat-examine ; Meilleurtaux Placement https://placement.meilleurtaux.com/bourse/actualites/2026-novembre/pea-pme-plafond-300000-eur-tombe-budget-peut-il-revenir-senat.html

## 2. Proposition pour le carrousel

Le carrousel déjà monté compte 8 sujets (Nvidia, douane, inflation et Fed, CAC 40, Anthropic, Dell, or, bitcoin). Il ne parle d'aucun fait qui touche directement l'épargne d'un Français. Ma proposition, si tu veux le resserrer à 6 :

1. Nvidia : le retour qui vaut +31 % (décor déjà prêt, `fond_huang.jpg`).
2. Livret A : 9,54 Md€ retirés depuis janvier (nouveau décor, prompt dans `prompts_gemini_veille.md`).
3. Inflation à 3,8 % et hausse des taux probable (`fond_fed.jpg`).
4. Droits de douane : 15 % pour l'Europe (`fond_douane.jpg`).
5. Paris : CAC 40 à +2,28 %, avec Sanofi qui rachète Insmed en exemple (`fond_cac40.jpg`, ou nouveau décor Sanofi si tu préfères une diapo dédiée).
6. Anthropic sous son prix d'introduction (`fond_anthropic2.jpg`).

Si tu gardes 8 sujets, le plus simple est de remplacer Dell (ou le bitcoin) par le Livret A. Le carburant peut tenir en une ligne dans la diapo CAC 40 ou en bonus.

Angle de couverture : garder le kiosque déjà généré, titre « Le patron de Nvidia est de retour 😱 » (c'est le fait le plus spectaculaire). Variante plus proche du public : « Les Français vident leur Livret A 😱 », avec Mister Coin qui lit le journal.

Question d'engagement, liée à l'actualité et tournée vers le spectateur : « Et toi, ton Livret A : tu le gardes ou tu le vides ? 👇 ». Variante si le Livret A n'est pas retenu : « Et toi, tu aurais gardé tes actions Nvidia quand le patron est parti ? 👇 ».

## 3. Chiffres à revérifier vendredi matin

- Or : écart entre sources sur le 25/11. Yahoo Finance donne 3 471,52 $ à 9 h (New York, −2,24 %), Motley Fool 3 572,40 $ à la clôture (+0,29 %), Stock Market Watch 3 609,20 $ (probablement le contrat à terme). Choisir un seul repère (cours au comptant) et vérifier le « −37 % depuis le plus haut » avec le cours du vendredi.
- S&P 500 du 25/11 : 7 182,78 points ; la variation du jour varie selon les sources (−0,21 % ou −0,25 %). Seule la clôture compte pour la diapo.
- Vendredi 27/11 : séance américaine écourtée (clôture 19 h à Paris), donc la semaine américaine ne sera complète que vendredi soir ; si une diapo annonce une variation sur la semaine, préciser « du vendredi 20 au mercredi 25 ».
- CAC 40 : la séance de vendredi changera la variation sur la semaine (+2,28 % au jeudi soir).
- Nvidia, Anthropic, Dell : cours à reprendre à l'ouverture américaine du vendredi (15 h 30 à Paris) si la diapo affiche un cours « actuel ». Pour Anthropic, BFM donnait 80,43 $ en séance le 24/11 ; la clôture retenue est 81,90 $.
- Bitcoin : il cote en continu, cours à reprendre vendredi matin.
- Carburant : nouvelle moyenne du jour sur Carbu.fr (et bulletin hebdomadaire du ministère publié le vendredi).
- Livret A : le « 2,6 % en février » est une prévision ; le plafond relevé est annoncé sans montant fixé. Ne pas les présenter comme des décisions.
- Taux de change : vérifier le taux BCE du vendredi 27/11 (publié vers 16 h) si tu veux convertir au taux du jour de publication.

## 4. Ce que je n'ai pas pu vérifier
- L'avis officiel de l'USTR au Federal Register sur les droits de douane (déjà signalé dans `sources.md`).
- Le rapport USAGold du 25/11 et la page WTOP des indices du 25/11 : accès refusé, les chiffres viennent d'autres sources.
- Aucune introduction en bourse notable cette semaine à Paris ou New York n'a été trouvée en dehors des suites d'Anthropic : rubrique écartée faute de source.

Contenu pédagogique, pas un conseil en investissement.
