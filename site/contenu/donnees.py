"""Données des rubriques News, Lexique et Vidéos. Chaque chiffre vient du fichier de sources de l'épisode indiqué."""

# ---------- Les News (episodes/2026-11-20_les_news/sources.md, clôture du jeudi 19/11, BCE 1,0992) ----------
NEWS = [dict(
    slug='2026-11-20', date='2026-11-20', date_txt='20/11/2026', titre='Wall Street repasse sous les 50 000',
    chapo="Des records partout et pourtant la bourse recule : la semaine en 5 news, chiffres à la clôture du jeudi 19/11.",
    note="Montants convertis au taux BCE du 19/11/2026 (1 € = 1,0992 $). Indices hors dividendes.",
    items=[
        ('Nvidia', "Des records sans Jensen Huang, l'action recule encore",
         "Premier trimestre publié sous la direction de Colette Kress (PDG par intérim) : 115,8 Md$ de chiffre d'affaires (105,4 Md€), +103 % sur un an, et une prévision de 130 Md$ pour le trimestre suivant. "
         "Le programme de rachat d'actions est relevé de 150 Md$. Ça n'a pas suffi : 6e séance de baisse d'affilée le 19/11, à 145,98 $ (132,81 €), soit −10,4 % sur la semaine. "
         "En toile de fond, une règle américaine du 16/11 impose une licence pour exporter des puces avancées vers cinq pays, dont Singapour et le Brésil.", 'neutre',
         [("Communiqué Nvidia (TechPowerUp)", "https://www.techpowerup.com/354965/nvidia-reports-q3-2026-earnings-of-usd-115-8-billion"),
          ("Constellation Research", "https://www.constellationr.com/insights/news/nvidia-posts-strong-q3-ups-q4-outlook-amid-huang-resignation"),
          ("Al Jazeera", "https://aljazeera.com/economy/2026/11/17/us-moves-to-block-chinas-remote-access-to-ai-chips-amid-nvidia-scandal")]),
        ('Anthropic', "La plus grosse entrée en bourse de l'histoire",
         "980 millions d'actions vendues à 83 $ (75,51 €), soit 81,3 Md$ levés (73,96 Md€). Première cotation à 111,50 $ le 19/11, clôture à 97,17 $ (88,40 €) : +17,1 % sur le prix d'introduction, "
         "mais −12,9 % depuis la première cotation. Les estimations de valorisation divergent selon les sources, on ne les reprend pas.", 'joie',
         [("Forbes", "https://www.forbes.com/sites/fionariley/2026/11/19/anthropic-ipo-live-stock-closes-day-at-97-up-more-than-17/"),
          ("CNBC", "https://www.cnbc.com/2026/11/19/anthropic-ipo-ant-live-updates.html")]),
        ('GTA 6 et Take-Two', "Le jeu explose les ventes, l'action baisse",
         "Selon Sensor Tower, 19,1 millions d'exemplaires et 1,84 Md$ (1,67 Md€) dès le premier jour, plus du double de GTA 5 en 2013. L'action Take-Two avait pris 6,2 % le 18/11 sur les premières critiques, "
         "puis recule de 3,67 % le 19/11 à 208,65 $ (189,82 €). Depuis le 1er janvier : −18,5 %.", 'court',
         [("Yahoo Finance (Sensor Tower)", "https://finance.yahoo.com/media-advertising/articles/two-set-shatter-sales-records-162847652.html"),
          ("Fox Business", "https://www.foxbusiness.com/markets/take-two-stock-jumps-over-6-rockstars-long-awaited-gta-vi-arrives-after-13-year-wait"),
          ("Finviz", "https://finviz.com/stock?t=TTWO")]),
        ('Walmart et Home Depot', "De bons comptes, et l'action baisse quand même",
         "Walmart publie 188,8 Md$ de ventes (171,76 Md€, +5,2 %) et relève ses prévisions pour la 3e fois de l'année : l'action perd 1,04 % le 19/11. "
         "Home Depot affiche 43,4 Md$ de ventes (39,48 Md€, +4,9 %) et annonce un nouveau PDG, Richard McPhail : −2,45 % le 17/11, à 339,01 $.", 'reflechit',
         [("Communiqué Walmart (SEC)", "https://www.sec.gov/Archives/edgar/data/104169/000010416926000168/earningsreleasefy27q3.htm"),
          ("Home Depot", "https://corporate.homedepot.com/node/2041"), ("Forbes", "https://www.forbes.com/companies/home-depot/")]),
        ('Wall Street et Paris', "Le Dow Jones sous les 50 000 points",
         "Quatre séances rouges : le Dow Jones termine le 19/11 à 49 097,06 points (−2,19 % sur la séance, −6,2 % sur la semaine) et le S&P 500 enchaîne 6 baisses d'affilée. "
         "Le taux à 10 ans américain reste au-dessus de 5 % (5,10 % le 17/11). À Paris, le CAC 40 finit à 8 080,74 points, −3,44 % sur la semaine.", 'loupe',
         [("CNBC", "https://www.cnbc.com/2026/11/18/stock-market-today-live-updates.html"), ("FRED (Réserve fédérale)", "https://fred.stlouisfed.org/series/DGS10"),
          ("Zonebourse", "https://www.zonebourse.com/cours/indice/CAC-40-4941/")]),
    ])]

# ---------- Lexique (episodes/2026-11-17_lexique/carrousel.py et sources.md) ----------
SP_PEA = ("service-public.gouv.fr, Plan d'épargne en actions", "https://www.service-public.gouv.fr/particuliers/vosdroits/F2385")
SP_PER = ("service-public.gouv.fr, Plan d'épargne retraite", "https://www.service-public.gouv.fr/particuliers/vosdroits/F34982")
SP_PFU = ("economie.gouv.fr, le prélèvement forfaitaire unique", "https://www.economie.gouv.fr/particuliers/impots-et-fiscalite/gerer-mes-autres-impots-et-taxes/comment-fonctionne-le-prelevement")
MSCI = ("MSCI, fiche de l'indice MSCI World", "https://www.msci.com/indexes/index/990100")
BCE = ("Banque centrale européenne", "https://www.ecb.europa.eu/home/html/index.fr.html")
LEXIQUE = [
    ('pea', 'PEA', "Plan d'épargne en actions", "Une enveloppe pour investir en actions européennes et en ETF éligibles, avec moins d'impôts après 5 ans.",
     "Tu verses 200 € par mois pendant 10 ans (24 000 €) et ton PEA vaut 34 000 € quand tu retires : sur les 10 000 € de gain, pas d'impôt sur le revenu, seulement 18,6 % de prélèvements sociaux, soit 1 860 €. Sur un compte-titres, la flat tax de 31,4 % en prendrait 3 140 €. Plafond : 150 000 € de versements.", [SP_PEA], ['cto', 'pfu', 'etf']),
    ('cto', 'CTO', 'Compte-titres ordinaire', "Le compte sans limite : toutes les actions du monde, pas de plafond… mais aucun avantage fiscal.",
     "Tu achètes 10 actions Apple à 200 € et tu les revends à 250 € : 500 € de plus-value, 157 € pour l'État (PFU de 31,4 %), il te reste 343 €. Apple n'est pas éligible au PEA : pour une action américaine, c'est le compte-titres.", [SP_PFU], ['pea', 'pfu']),
    ('etf', 'ETF', 'Fonds indiciel coté (« tracker »)', "Un panier d'entreprises que tu achètes en un seul clic. Il copie un indice, avec des frais très bas.",
     "Avec 100 € dans un ETF MSCI World, tu deviens copropriétaire d'environ 1 250 entreprises d'un coup. Avec des frais de 0,20 % par an (un niveau courant), ces 100 € te coûtent 20 centimes par an.", [MSCI], ['msci-world', 'dca']),
    ('msci-world', 'MSCI World', "L'indice des pays développés", "Les grandes et moyennes entreprises de 23 pays développés. C'est l'indice que copient beaucoup d'ETF.",
     "Sur 100 € placés dans un ETF MSCI World, environ 73 € vont à des entreprises américaines (Apple, Nvidia, Microsoft…). Pas un centime en Chine ni en Inde, classées pays émergents.", [MSCI], ['etf']),
    ('dca', 'DCA', 'Dollar Cost Averaging', "Investir la même somme à intervalles réguliers, quoi qu'il arrive, pour lisser son prix d'achat.",
     "100 € le 5 de chaque mois. En janvier l'ETF vaut 50 € : tu achètes 2 parts. En février il vaut 100 € : 1 part. Bilan : 200 € pour 3 parts, soit 66,67 € la part en moyenne, moins que la moyenne des deux prix (75 €).", [], ['etf', 'interets-composes']),
    ('per-retraite', 'PER', "Plan d'épargne retraite", "Une épargne bloquée jusqu'à la retraite, et tes versements réduisent ton impôt sur le revenu (dans une limite).",
     "Tu es dans la tranche à 30 % et tu verses 2 000 € avant le 31 décembre : ton impôt sur le revenu baisse de 600 €. En échange, l'argent est bloqué jusqu'à la retraite (sauf cas prévus, comme l'achat de ta résidence principale) et il sera imposé à la sortie.", [SP_PER], ['per-price-earnings']),
    ('per-price-earnings', 'PER', 'Price Earnings Ratio (le piège)', "Même sigle, rien à voir : c'est le prix d'une action divisé par ce qu'elle gagne par action.",
     "Une action vaut 100 € et l'entreprise gagne 5 € par action : PER de 20, l'action coûte 20 ans de bénéfices s'ils restent stables. Nvidia était à 13,5 le 20/11/2026 (125,53 $ ÷ 9,31 $).", [], ['per-retraite']),
    ('pfu', 'PFU', 'Prélèvement forfaitaire unique', "La « flat tax » sur tes gains hors PEA et assurance vie : 12,8 % d'impôt + 18,6 % de prélèvements sociaux, soit 31,4 % en 2026.",
     "1 000 € de plus-value sur un compte-titres : 128 € d'impôt et 186 € de prélèvements sociaux, soit 314 € pour l'État en 2026, il te reste 686 €. Pareil pour 1 000 € de dividendes.", [SP_PFU], ['cto', 'pea']),
    ('ipo', 'IPO', 'Initial Public Offering', "L'introduction en bourse : le jour où une entreprise vend pour la première fois ses actions au public.",
     "Le 19/11/2026, Anthropic a vendu 980 millions d'actions à 83 $ (81,3 milliards de dollars levés, un record). À la fin du premier jour, l'action valait 97,17 $ : +17,1 % pour ceux qui avaient pu en acheter au prix d'introduction.", [("Forbes, l'introduction d'Anthropic", "https://www.forbes.com/sites/fionariley/2026/11/19/anthropic-ipo-live-stock-closes-day-at-97-up-more-than-17/")], []),
    ('bce', 'BCE', 'Banque centrale européenne', "Elle fixe les taux d'intérêt de la zone euro pour tenir l'inflation autour de 2 % par an.",
     "Le 20/11/2026, son taux de référence était de 1 € = 1,0990 $. Une action Nvidia à 125,53 $ valait donc 114,22 € : c'est ce taux qu'on utilise pour toutes nos conversions.", [BCE], []),
]

# ---------- Quiz du lexique : (question, choix, indice de la bonne réponse, explication, pose de Mister Coin) ----------
QUIZ = [
    ("Tu veux acheter des actions Apple. Sur quel compte ?", ["Un PEA", "Un compte-titres (CTO)", "Un livret A"], 1,
     "Apple est une entreprise américaine : elle n'est pas éligible au PEA, réservé aux actions européennes et aux ETF éligibles.", 'reflechit'),
    ("Après combien d'années un PEA n'est-il plus soumis à l'impôt sur le revenu ?", ["2 ans", "5 ans", "8 ans"], 1,
     "Après 5 ans, seuls les prélèvements sociaux (18,6 % en 2026) restent dus sur les gains.", 'loupe'),
    ("Combien l'État prend-il sur 1 000 € de plus-value en compte-titres en 2026 ?", ["128 €", "186 €", "314 €"], 2,
     "Le PFU fait 31,4 % : 12,8 % d'impôt et 18,6 % de prélèvements sociaux.", 'sueur'),
    ("Un ETF, c'est…", ["Une action d'une seule entreprise", "Un panier d'entreprises qui copie un indice", "Un compte bancaire rémunéré"], 1,
     "Un ETF copie un indice : avec un seul achat, tu détiens un morceau de toutes ses entreprises.", 'question'),
    ("Dans un ETF MSCI World, quelle part environ va aux entreprises américaines ?", ["Environ un quart", "Environ la moitié", "Environ les trois quarts"], 2,
     "Environ 73 % : le MSCI World est très concentré sur les États-Unis, et ne contient ni la Chine ni l'Inde.", 'montre'),
    ("Tu investis 100 € le 5 de chaque mois, quoi qu'il arrive. Comment s'appelle cette méthode ?", ["Le DCA", "Le PFU", "L'IPO"], 0,
     "Le DCA (Dollar Cost Averaging) lisse ton prix d'achat : tu achètes plus de parts quand c'est bas, moins quand c'est haut.", 'court'),
    ("Une action vaut 100 € et l'entreprise gagne 5 € par action. Quel est son PER ?", ["5", "20", "500"], 1,
     "PER = prix ÷ bénéfice par action = 100 ÷ 5 = 20 : l'action coûte 20 ans de bénéfices.", 'sceptique'),
    ("Le PER « plan d'épargne retraite », c'est…", ["Une épargne bloquée jusqu'à la retraite qui réduit ton impôt", "Un ratio pour savoir si une action est chère", "Un livret sans risque disponible à tout moment"], 0,
     "Même sigle que le Price Earnings Ratio, mais rien à voir : c'est une enveloppe d'épargne retraite.", 'haussement'),
    ("Que désigne une IPO ?", ["Le versement d'un dividende", "L'introduction d'une entreprise en bourse", "Une baisse de plus de 20 %"], 1,
     "Initial Public Offering : le jour où une entreprise vend ses actions au public pour la première fois, comme Anthropic le 19/11/2026.", 'etoiles'),
    ("Quel est le rôle principal de la BCE ?", ["Fixer les taux d'intérêt de la zone euro", "Gérer la Bourse de Paris", "Collecter les impôts"], 0,
     "La Banque centrale européenne ajuste ses taux pour tenir l'inflation autour de 2 % par an.", 'lit_journal_v2_titre'),
]

# ---------- Vidéos publiées : (date, titre, type, id TikTok, chemin Instagram, vignette dans assets/videos/) ; liens relevés dans Metricool le 22/11/2026 ----------
VIDEOS = [('2026-11-21', "Buy, borrow, die : vivre comme un milliardaire sans presque payer d'impôt", 'Vidéo', None, 'reel/DgArlrFxBNN', '2026-11-21_bbd.webp'),
 ('2026-11-21', 'Fiche entreprise n°1 : que vaut Nvidia ?', 'Carrousel', '7710547145409056032', 'p/Df_2BH0Ef5Z', '2026-11-21_00.webp'),
 ('2026-11-20', 'Les News : Nvidia, Anthropic, GTA 6, Walmart, Wall Street', 'Carrousel', '7710154619095092513', 'p/Df9GqsdEUOK', '2026-11-20_01.webp'),
 ('2026-11-19', "GTA 6 sort aujourd'hui : et si tu avais acheté des actions Take-Two plutôt que GTA 5 ?", 'Vidéo', '7709778351606484257', 'reel/Df6gLndxqzh', '2026-11-19_02.webp'),
 ('2026-11-17', 'Le lexique de la bourse', 'Carrousel', '7709038655997873441', 'p/Df1YHfjEVxa', '2026-11-17_03.webp'),
 ('2026-11-16', 'Le Loto toute ta vie contre la même somme placée', 'Vidéo', '7708668836953820448', 'reel/Dfy0PE6RsEy', '2026-11-16_04.webp'),
 ('2026-11-14', 'Combien placer par mois pour devenir millionnaire ?', 'Vidéo', '7707944420561161504', 'reel/Dftylyxx0bh', '2026-11-14_05.webp'),
 ('2026-11-13', 'Les News : le PDG de Nvidia démissionne', 'Carrousel', '7707556708968582422', 'p/DfrFH6NkXy9', '2026-11-13_06.webp'),
 ('2026-11-12', "L'or : valeur refuge ou placement qui dort ?", 'Vidéo', '7707186405159537952', 'reel/Dfohzs8xEvQ', '2026-11-12_07.webp'),
 ('2026-11-11', 'Action ou obligation : propriétaire ou prêteur ?', 'Vidéo', '7706810365534817568', 'reel/Dfl62PjR3r3', '2026-11-11_08.webp'),
 ('2026-11-10', "Boeing : de la confiance absolue aux portes qui s'envolent", 'Vidéo', '7706457101366775072', 'reel/DfjYBFexB5y', '2026-11-10_09.webp'),
 ('2026-11-09', "Comment commencer à t'enrichir ?", 'Vidéo', '7706145405276359969', 'reel/DfhTadiRB5m', '2026-11-09_10.webp'),
 ('2026-11-07', 'Pourquoi tu restes pauvre ?', 'Vidéo', '7705340095951392033', 'reel/DfbtR-HRa2c', '2026-11-07_11.webp'),
 ('2026-11-06', 'Combien il te faut pour vivre de tes dividendes ?', 'Vidéo', '7705042332793556257', 'reel/DfZpb5qRqjs', '2026-11-06_12.webp'),
 ('2026-11-05', 'Les News : résultats contre bourse (Apple, Palantir, AMD…)', 'Carrousel', '7704609363557633312', 'p/DfWkAaykZci', '2026-11-05_13.webp'),
 ('2026-11-04', 'Ubisoft : −95 % depuis son record', 'Vidéo', '7704369685340507425', 'reel/DfU_bdexzsx', '2026-11-04_14.webp'),
 ('2026-11-03', 'Ton iPhone ou des actions Apple ?', 'Vidéo', '7703926277924801824', 'reel/DfR7mmcRW9P', '2026-11-03_15.webp'),
 ('2026-11-03', 'Palantir : génie ou bulle ?', 'Vidéo', '7703841962729770272', 'reel/DfRUyuTxGVL', '2026-11-03_16.webp'),
 ('2026-11-02', "C'est quoi un ETF MSCI World ?", 'Vidéo', '7703529906122034464', 'reel/DfPKPUmxRgv', '2026-11-02_17.webp'),
 ('2026-10-31', 'Les News : résultats contre bourse (Microsoft, Alphabet, Amazon, Intel)', 'Carrousel', '7702807478500724000', 'p/DfJt69_EfrP', '2026-10-31_18.webp'),
 ('2026-10-30', 'Les intérêts composés', 'Vidéo', '7702421765330455840', 'reel/DfHd8MexK8w', '2026-10-30_19.webp'),
 ('2026-10-29', 'Comprendre le prix du carburant en France', 'Vidéo', '7702046743424453920', 'reel/DfE3d3Lxo3M', '2026-10-29_20.webp'),
 ('2026-10-28', 'Hermès : −57 % depuis le record', 'Vidéo', '7701678895824669984', 'reel/DfCUGHlRc5i', '2026-10-28_21.webp'),
 ('2026-10-27', 'Kering (Gucci) : −78 % depuis le sommet', 'Vidéo', '7701312236496768289', 'reel/De_w9r_Rt0l', None),
 ('2026-10-26', 'AMD : la puce qui revient de très loin', 'Vidéo', '7700916898443119905', 'reel/De8_zUsxdae', '2026-10-26_23.webp'),
 ('2026-10-25', 'Novo Nordisk (Ozempic) : −74 %', 'Vidéo', '7700514706540236064', 'reel/De6P514o6_5', '2026-10-25_24.webp'),
 ('2026-10-24', 'Série Krachs, ép. 2 : la bulle internet de 2000', 'Vidéo', '7700137755430505760', 'reel/De3nx4mxKIo', None),
 ('2026-10-23', 'Netflix, Tesla, Meta : les résultats', 'Vidéo', '7699804935331843361', 'reel/DezYSO8ug65', None),
 ('2026-10-22', 'PEA ou CTO ?', 'Vidéo', '7699583850996895009', 'reel/De1Uzlcx90b', None),
 ('2026-10-21', 'Coca-Cola : 848 millions de dollars par an pour Buffett', 'Vidéo', '7699060312200285473', 'reel/Dew2a7hRYUt', None),
 ('2026-10-20', 'Intel : de 18 $ à plus de 140 $', 'Vidéo', '7698685768293731616', 'reel/DeyjbinRvN1', None),
 ('2026-10-19', 'Meta : 1 000 € le jour du changement de nom', 'Vidéo', '7698322188255956257', 'reel/DexX12JRYhh', None),
 ('2026-10-17', 'Série Krachs, ép. 1 : 2008', 'Vidéo', '7697557532348386592', None, None),
 ('2026-10-16', 'SpaceX : 1 000 € au sommet', 'Vidéo', '7697148430807780640', 'reel/DexD6ppxqUx', None),
 ('2026-10-15', 'Micron : 1 000 € il y a 5 ans', 'Vidéo', '7696932405025738017', None, None),
 ('2026-10-15', "Bitcoin : 2 pizzas = 742 millions d'euros", 'Vidéo', '7696850629188160801', 'reel/Dewu6C5oJXw', None)]
