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
     "Jusqu'à 150 000 € de versements. Après 5 ans, plus d'impôt sur le revenu sur tes gains (les prélèvements sociaux restent dus).", [SP_PEA], ['cto', 'pfu', 'etf']),
    ('cto', 'CTO', 'Compte-titres ordinaire', "Le compte sans limite : toutes les actions du monde, pas de plafond… mais aucun avantage fiscal.",
     "Tes gains y sont taxés au PFU.", [SP_PFU], ['pea', 'pfu']),
    ('etf', 'ETF', 'Fonds indiciel coté (« tracker »)', "Un panier d'entreprises que tu achètes en un seul clic. Il copie un indice, avec des frais très bas.",
     "Un ETF MSCI World : environ 1 250 entreprises d'un coup.", [MSCI], ['msci-world', 'dca']),
    ('msci-world', 'MSCI World', "L'indice des pays développés", "Les grandes et moyennes entreprises de 23 pays développés. C'est l'indice que copient beaucoup d'ETF.",
     "Environ 73 % d'entreprises américaines, et ni la Chine ni l'Inde.", [MSCI], ['etf']),
    ('dca', 'DCA', 'Dollar Cost Averaging', "Investir la même somme à intervalles réguliers, quoi qu'il arrive, pour lisser son prix d'achat.",
     "100 € le 5 de chaque mois, sans regarder les cours.", [], ['etf', 'interets-composes']),
    ('per-retraite', 'PER', "Plan d'épargne retraite", "Une épargne bloquée jusqu'à la retraite, et tes versements réduisent ton impôt sur le revenu (dans une limite).",
     "Un versement fait avant le 31 décembre compte pour les impôts de l'année.", [SP_PER], ['per-price-earnings']),
    ('per-price-earnings', 'PER', 'Price Earnings Ratio (le piège)', "Même sigle, rien à voir : c'est le prix d'une action divisé par ce qu'elle gagne par action.",
     "PER de 20 : l'action coûte 20 ans de bénéfices (s'ils restent stables). Nvidia était à 13,5 le 20/11/2026.", [], ['per-retraite']),
    ('pfu', 'PFU', 'Prélèvement forfaitaire unique', "La « flat tax » sur tes gains hors PEA et assurance vie : 12,8 % d'impôt + 18,6 % de prélèvements sociaux, soit 31,4 % en 2026.",
     "1 000 € de plus-value en CTO : 314 € pour l'État en 2026.", [SP_PFU], ['cto', 'pea']),
    ('ipo', 'IPO', 'Initial Public Offering', "L'introduction en bourse : le jour où une entreprise vend pour la première fois ses actions au public.",
     "Airbnb est entrée en bourse en décembre 2020 ; Anthropic le 19/11/2026.", [], []),
    ('bce', 'BCE', 'Banque centrale européenne', "Elle fixe les taux d'intérêt de la zone euro pour tenir l'inflation autour de 2 % par an.",
     "Son taux de change de référence sert à toutes nos conversions dollar → euro.", [BCE], []),
]

# ---------- Vidéos publiées (roadmap, collection videos, statut « publié ») ----------
VIDEOS = [  # (date, titre, type)
    ('2026-11-21', 'Fiche entreprise n°1 : que vaut Nvidia ?', 'Carrousel'),
    ('2026-11-20', 'Les News : Nvidia, Anthropic, GTA 6, Walmart, Wall Street', 'Carrousel'),
    ('2026-11-19', 'GTA 6 sort aujourd\'hui : et si tu avais acheté des actions Take-Two plutôt que GTA 5 ?', 'Vidéo'),
    ('2026-11-17', 'Le lexique de la bourse', 'Carrousel'),
    ('2026-11-16', 'Le Loto toute ta vie contre la même somme placée', 'Vidéo'),
    ('2026-11-14', 'Combien placer par mois pour devenir millionnaire ?', 'Vidéo'),
    ('2026-11-13', 'Les News de la semaine', 'Carrousel'),
    ('2026-11-12', "L'or : ni propriétaire, ni prêteur", 'Vidéo'),
    ('2026-11-11', 'Action ou obligation : propriétaire ou prêteur ?', 'Vidéo'),
    ('2026-11-10', 'Boeing : de la confiance absolue aux portes qui s\'envolent', 'Vidéo'),
    ('2026-11-09', "Comment commencer à t'enrichir ?", 'Vidéo'),
    ('2026-11-07', 'Pourquoi tu restes pauvre ?', 'Vidéo'),
    ('2026-11-06', 'Combien il te faut pour vivre de tes dividendes ?', 'Vidéo'),
    ('2026-11-05', 'Les News : Apple, Palantir, AMD, Booking…', 'Carrousel'),
    ('2026-11-04', 'Ubisoft : −90 %', 'Vidéo'),
    ('2026-11-03', 'Ton iPhone ou des actions Apple ?', 'Vidéo'),
    ('2026-11-03', 'Palantir', 'Vidéo'),
    ('2026-11-02', "C'est quoi un ETF MSCI World ?", 'Vidéo'),
    ('2026-10-31', 'Les News : résultats contre bourse', 'Carrousel'),
    ('2026-10-30', 'Les intérêts composés', 'Vidéo'),
    ('2026-10-29', 'Comprendre le prix du carburant en France', 'Vidéo'),
    ('2026-10-28', 'Hermès', 'Vidéo'),
    ('2026-10-27', 'Kering (Gucci)', 'Vidéo'),
    ('2026-10-26', 'AMD', 'Vidéo'),
    ('2026-10-25', 'Novo Nordisk (Ozempic)', 'Vidéo'),
    ('2026-10-24', 'Série Krachs, ép. 2 : la bulle internet de 2000', 'Vidéo'),
    ('2026-10-23', 'Netflix, Tesla, Meta : les résultats', 'Vidéo'),
    ('2026-10-22', 'PEA ou CTO ?', 'Vidéo'),
    ('2026-10-21', 'Coca-Cola', 'Vidéo'),
    ('2026-10-20', 'Intel', 'Vidéo'),
    ('2026-10-19', 'Meta', 'Vidéo'),
    ('2026-10-17', 'Série Krachs, ép. 1 : 2008', 'Vidéo'),
]
