"""Fiche entreprise n°2 : Alphabet. Chiffres et sources : episodes/2026-11-23_fiche_alphabet/sources.md (clôture du 23/11/2026, BCE 1,0939)."""
from composants import *

META = dict(slug='alphabet', titre='Que vaut Alphabet ?', nom='Alphabet', date='2026-11-24', date_txt='24/11/2026', chiffres_au='23/11/2026',
            # comptes : à mettre à jour après chaque publication trimestrielle (site/outils/MAJ_FICHES.md)
            comptes="trimestre de juillet à septembre 2026", comptes_officiel="3e trimestre 2026, clos le 30/09/2026 (Alphabet compte en années civiles)", comptes_publies='2026-10-28',
            annee=2026, trimestre=3, version='2026-t3',   # trimestre civil des comptes, sert à l'historique
            prochains_resultats='2027-02-03', date_confirmee=False, prochains_txt='début février 2027 (date pas encore annoncée)', ticker='googl',
            description="Fiche entreprise Alphabet (Google) : croissance, rentabilité, solidité, dividende et investissements face à Microsoft, Meta et Amazon, comptes du 3e trimestre 2026, PER recalculé chaque soir, sources en lien.",
            accroche="Cloud +103 % en un an, et pourtant l'action reste loin de son record de mai. Alphabet emprunte, émet des actions et investit comme jamais : on remet les chiffres à plat.",
            detient=True, pose='loupe', logo='googl.png')
EUR = 1.0939          # taux BCE du 23/11/2026, pour convertir les comptes (figés jusqu'au prochain trimestre)
def e(x): return x/EUR

# ---- ce qui bouge chaque soir avec le cours (site/cours.py) ; BPA, dividende et actions : derniers comptes publiés ----
from cours import cours, taux, per, fr_per, fr_var, jj_mm, jj_mm_aaaa
FIGE = False   # True dans la copie archivée d'une version (site/outils/MAJ_FICHES.md) : cours et taux gelés aux valeurs ci-dessous
BPA12 = 10.94          # BPA dilué des 12 derniers mois hors réévaluation des participations (SpaceX, Anthropic), en $ (sources.md, section 3)
BPA12_PUBLIE = 19.15   # BPA dilué des 12 derniers mois tel que publié, en $
ACTIONS = 12.294       # milliards d'actions A, B et C (page de garde du 10-Q, 21/10/2026)
DIV_AN = 0.88          # dividende annuel actuel, 4 × 0,22 $
RECORD = 402.62        # record de clôture GOOGL, 13/05/2026
CN = cours('googl', 282.10, '2026-11-23', 6.34, fige=FIGE)
TX, TX_DATE = taux(1.0939, '2026-11-23', fige=FIGE)
JOUR = jj_mm(CN['date'])
PER_N = per(CN['c'], BPA12)

CA = [257.637, 282.836, 307.394, 350.018, 402.836]; CLOUD = [19.206, 26.280, 33.088, 43.229, 58.705]
RN = [76.033, 59.972, 73.795, 100.118, 132.170]; MARGE = [29.5, 21.2, 24.0, 28.6, 32.8]; BPA = [5.61, 4.56, 5.80, 8.04, 10.81]

def _tips_croissance():
    t = []
    for i, (tot, cl) in enumerate(zip(CA, CLOUD)):
        l = [f"Exercice {2021+i} (année civile)", f"{fr(e(tot))} Md€ ({fr(tot)} Md$)", f"Cloud : {fr(e(cl))} Md€ ({fr(100*cl/tot, 0)} % du total)",
             f"Recherche, YouTube, abonnements et autres : {fr(e(tot-cl))} Md€"]
        if i: l.insert(2, f"+{fr(100*(tot/CA[i-1]-1), 0)} % sur un an")
        t.append('\n'.join(l))
    return t

def _flux():
    d = dict(se=63.350, ab=14.290, yt=11.207, ne=7.455, sv=96.302, cl=30.709, ca=127.577, mb=76.158, cr=51.419, re=40.576, ch=35.582, rn=26.468, pa=8.221, im=5.887)
    v = {i: e(x) for i, x in d.items()}
    N = {'se': (130, 60, LIME), 'ab': (130, 270, LIME), 'yt': (130, 345, LIME), 'ne': (130, 415, LIME), 'sv': (300, 110, LIME), 'cl': (300, 420, TEAL),
         'ca': (470, 160, INK), 'mb': (640, 110, GREEN), 'cr': (640, 370, RED), 're': (800, 80, GREEN), 'ch': (800, 280, RED),
         'rn': (950, 50, GREEN), 'pa': (950, 160, RED), 'im': (950, 225, RED)}
    L = [('se', 'sv', v['se'], LIME_R), ('ab', 'sv', v['ab'], LIME_R), ('yt', 'sv', v['yt'], LIME_R), ('ne', 'sv', v['ne'], LIME_R),
         ('sv', 'ca', v['sv'], LIME_R), ('cl', 'ca', v['cl'], TEAL_R), ('ca', 'mb', v['mb'], GREEN_R), ('ca', 'cr', v['cr'], RED_R),
         ('mb', 're', v['re'], GREEN_R), ('mb', 'ch', v['ch'], RED_R), ('re', 'rn', v['rn'], GREEN_R), ('re', 'pa', v['pa'], RED_R), ('re', 'im', v['re']-v['rn']-v['pa'], RED_R)]
    lab = {'se': ('l', [('Recherche', 'n'), (fr(v['se']), 'v'), ('+12 % sur 1 an', 's')]),
           'ab': ('l', [('Abonnements', 'n'), (fr(v['ab']), 'v')]),
           'yt': ('l', [('YouTube', 'n'), (fr(v['yt']), 'v')]),
           'ne': ('l', [('Réseau', 'n'), (fr(v['ne']), 'v')]),
           'sv': ('t', [('Google Services', 'n'), (fr(v['sv']), 'v'), ('+11 % sur 1 an', 's')]),
           'cl': ('b', [('Cloud', 'n'), (fr(v['cl']), 'v'), ('+103 % sur 1 an', 's')]),
           'ca': ('t', [("Chiffre d'affaires", 'n'), (fr(v['ca']), 'v'), ('+25 % sur 1 an', 's')]),
           'mb': ('t', [('Marge brute', 'n'), (fr(v['mb']), 'v'), ('60 % des ventes', 's')]),
           'cr': ('b', [('Coût des ventes', 'n'), ('('+fr(v['cr'])+')', 'v'), (f"dont {fr(e(16.366))} aux partenaires", 's')]),
           're': ('t', [("Résultat d'exploitation", 'n'), (fr(v['re']), 'v'), ('32 % des ventes', 's')]),
           'ch': ('b', [('Recherche et frais', 'n'), ('('+fr(v['ch'])+')', 'v'), (f"dont {fr(e(20.640))} de recherche", 's')]),
           'rn': ('r', [('Résultat net', 'n'), (fr(v['rn']), 'v'), ('21 % des ventes', 's')]),
           'pa': ('r', [('Participations', 'n'), ('('+fr(v['pa'])+')', 'v')]),
           'im': ('r', [('Impôts', 'n'), ('('+fr(v['im'])+')', 'v')])}
    def m(i): return f"{fr(v[i])} Md€ ({fr(d[i])} Md$)"
    def pc(i): return f"{fr(100*d[i]/d['ca'])} % des ventes"
    T = {'se': ["Recherche Google", m('se'), "+12 % sur un an", "La publicité affichée dans les résultats de recherche, plus de la moitié des ventes de Google Services."],
         'ab': ["Abonnements, plateformes et appareils", m('ab'), "+11 % sur un an", "YouTube Premium, Google One, Play Store, téléphones Pixel."],
         'yt': ["Publicité YouTube", m('yt'), "+9 % sur un an", "Les publicités diffusées sur YouTube."],
         'ne': ["Réseau publicitaire", m('ne'), "+1 % sur un an", "Les publicités de Google placées sur les sites et applications de ses partenaires."],
         'sv': ["Google Services", m('sv'), "+11 % sur un an", f"{fr(100*d['sv']/d['ca'], 0)} % du chiffre d'affaires : recherche, YouTube, Android, Chrome, Play."],
         'cl': ["Google Cloud", m('cl'), "+103 % sur un an", f"{fr(100*d['cl']/d['ca'], 0)} % du chiffre d'affaires : serveurs, puces TPU et outils d'IA loués aux entreprises."],
         'ca': ["Chiffre d'affaires du trimestre", m('ca'), "+25 % sur un an", "3e trimestre 2026, clos le 30/09/2026. Dont 0,5 Md€ d'Other Bets (Waymo…) et de couvertures de change."],
         'cr': ["Coût des ventes", m('cr'), pc('cr'), f"Centres de données, contenus YouTube et {fr(e(16.366))} Md€ reversés aux partenaires qui apportent le trafic (Apple, sites, opérateurs)."],
         'mb': ["Marge brute", m('mb'), pc('mb'), "Ce qui reste une fois les ventes payées."],
         'ch': ["Recherche et frais", m('ch'), pc('ch'), f"Dont {fr(e(20.640))} Md€ de recherche et développement, puis marketing et frais généraux."],
         're': ["Résultat d'exploitation", m('re'), pc('re') + ", +30 % sur un an", "Ce que rapporte l'activité elle-même, avant éléments financiers et impôts."],
         'pa': ["Participations et éléments financiers", m('pa'), "Surtout la baisse de valeur des actions SpaceX détenues par Alphabet (perte comptable, sans sortie d'argent)."],
         'im': ["Impôts", m('im'), f"{fr(100*d['im']/(d['re']-d['pa']))} % du résultat avant impôts"],
         'rn': ["Résultat net", m('rn'), pc('rn'), "Le bénéfice du trimestre, dont 0,3 Md$ de dividende aux actions privilégiées émises en juin."]}
    noms = dict(se='Recherche', ab='Abonnements', yt='YouTube', ne='Réseau', sv='Google Services', cl='Cloud', ca="Chiffre d'affaires", mb='Marge brute',
                cr='Coût des ventes', re="Résultat d'exploitation", ch='Recherche et frais', rn='Résultat net', pa='Participations', im='Impôts')
    P = {'sv': ['magnify', 'youtube', 'google-play'], 'cl': ['cloud-outline'], 'cr': ['server'], 'ch': ['flask-outline'], 'pa': [], 'rn': ['cash-multiple']}
    return flux(N, L, v, 2.75, lab, "Compte de résultat d'Alphabet au 3e trimestre 2026 en rubans : du chiffre d'affaires au résultat net",
                H=660, tips={i: '\n'.join(x) for i, x in T.items()}, noms=noms, pictos=P)

SOURCES = [("Alphabet, résultats du 3e trimestre 2026 (28/10/2026, SEC)", "https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000080/googexhibit991q32026.htm"),
           ("Alphabet, rapport trimestriel 10-Q du 3e trimestre 2026", "https://s206.q4cdn.com/479360582/files/doc_financials/2026/q3/GOOG-10-Q-Q3-2026.pdf"),
           ("Alphabet, résultats de l'exercice 2025", "https://s206.q4cdn.com/479360582/files/doc_financials/2025/q4/2025q4-alphabet-earnings-release.pdf"),
           ("Alphabet, rapport trimestriel 10-Q du 1er trimestre 2026 (rachats, dividende)", "https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000048/goog-20260331.htm"),
           ("Alphabet, levée de fonds de juin 2026", "https://s206.q4cdn.com/479360582/files/doc_news/2026/Jun/01/attachments/2026-June-Alphabet-Equity-Capital-Raise-Press-Release-PDF.pdf"),
           ("TechCrunch, part d'Alphabet dans Anthropic après son introduction (13,7 %)", "https://techcrunch.com/2026/11/17/amazon-and-google-will-together-own-nearly-30-of-anthropic-after-its-ipo/"),
           ("Motley Fool, émissions obligataires de novembre et record de mai", "https://www.fool.com/investing/2026/11/21/alphabet-stock-just-hit-a-1-year-low-why-is-google-s-parent-borrowing-so-much-money/"),
           ("Microsoft, résultats du 1er trimestre de l'exercice 2027", "https://redmondmag.com/articles/2026/10/30/microsoft-revenue-jumps-as-azure-and-ai-demand--fuel-growth.aspx"),
           ("Meta, résultats du 3e trimestre 2026", "https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/default.aspx"),
           ("Amazon, résultats du 3e trimestre 2026 (SEC)", "https://www.sec.gov/Archives/edgar/data/0001018724/000101872426000038/amzn-20260930xex991.htm")]

def corps(R):
    m = META
    S = []
    cap = CN['c']*ACTIONS
    var = CN['var'] or 0
    S.append(section(1, 'CARTE', "D'IDENTITÉ", "Chiffre d'affaires du 3e trimestre 2026",
        carte(f'<div style="display:flex;gap:22px;align-items:center;flex-wrap:wrap"><img src="{R}assets/img/googl.png" alt="Logo Alphabet" style="height:44px;width:auto">'
              '<p style="margin:0;flex:1 1 360px;font-size:18px">Maison mère de Google, YouTube et Waymo. Vit surtout de la publicité, et loue de plus en plus ses serveurs et ses puces d\'IA aux entreprises (Google Cloud).</p></div>')
        + '<div class="grille" style="--min:320px">'
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Publicité · 64,3 %</div>' + pbar('Recherche Google', 49.7, LIME) + pbar('Publicité YouTube', 8.8, LIME)
                + pbar('Réseau publicitaire', 5.8, LIME) + '</div>')
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Hors publicité · 35,7 %</div>' + pbar('Cloud', 24.1, TEAL) + pbar('Abonnements, Play, appareils', 11.2, '#7FB2EA')
                + pbar('Autres (Waymo…)', 0.4, '#9AA6B8') + '</div>') + '</div>'
        + grille(tuile('neutre', 'En bourse depuis', '2004', 'Nasdaq'), tuile('neutre', 'Capitalisation', f"≈ {fr(cap/TX, 0)} Md€", f"≈ {fr(cap, 0)} Md$"),
                 tuile('ok' if var > 0 else 'ko' if var < 0 else 'neutre', f'Cours au {JOUR}', f"{fr(CN['c']/TX, 2)} €", f"{fr(CN['c'], 2)} $" + (', ' + fr_var(CN['var']) if CN['var'] is not None else ''))),
        R, 'loupe', "La moitié des ventes vient encore de la recherche Google. Mais le Cloud pèse déjà un quart du total, contre moins d'un dixième en 2021. Alphabet détient aussi 13,7 % d'Anthropic, entrée en bourse le 19 novembre.",
        f"Source : Alphabet, communiqué du 28/10/2026 ; cours de clôture GOOGL (action de classe A) du {jj_mm_aaaa(CN['date'])} (Nasdaq, via Yahoo Finance), recalculé chaque soir ; 1 € = {fr(TX, 4)} $ (BCE, {jj_mm_aaaa(TX_DATE)}). "
        "Capitalisation ≈ cours GOOGL × 12,3 milliards d'actions A, B et C (la classe C cote quelques dollars de moins)."))
    S.append(section(2, 'LA', 'CROISSANCE', "Chiffre d'affaires annuel, en milliards d'euros",
        carte('<figure class="fin">' + barres_empilees(list(zip(CLOUD, [t-c for t, c in zip(CA, CLOUD)])), "Chiffre d'affaires annuel d'Alphabet en milliards d'euros, de 2021 à 2025, dont Google Cloud",
                                                      groupes=1, premier=2021, conv=EUR, tips=_tips_croissance())
              + f'<figcaption class="petit" style="display:flex;gap:22px;flex-wrap:wrap;margin-top:8px"><span><i style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{TEAL};margin-right:6px"></i>Cloud</span>'
              f'<span><i style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{LIME};margin-right:6px"></i>Recherche, YouTube, abonnements et autres</span></figcaption></figure>')
        + grille(tuile('ok', 'Sur 4 ans', '+11,8 %/an', '2021 → 2025'), tuile('ok', 'Dernier trimestre', '+25 %', 'Cloud +103 %'), tuile('ok', '12 derniers mois', f"{fr(e(471.097))} Md€", '471,1 Md$')),
        R, 'court', "En 4 ans, le chiffre d'affaires a gagné 56 %. Et la croissance accélère : +25 % au dernier trimestre, 13e trimestre d'affilée au-dessus de +10 %. Le Cloud a doublé en un an.",
        f"Source : Alphabet, rapports annuels 10-K et communiqués. Exercices = années civiles. 1 € = {fr(EUR, 4)} $."))
    S.append(section(3, "D'OÙ VIENT", "L'ARGENT", "3e trimestre clos le 30/09/2026, en milliards d'euros", carte('<figure>' + _flux() + '</figure>'), R, None, None,
        "Source : Alphabet, résultats du 28/10/2026 (CA 127,6 Md$). Mise en page inspirée de App Economy Insights (How They Make Money)."))
    S.append(section(4, 'LA', 'RENTABILITÉ', "Résultat net (Md€) et marge nette, par exercice",
        carte('<figure>' + barres([e(x) for x in RN], [str(y) for y in range(2021, 2026)], fr, GREEN, "Résultat net d'Alphabet par exercice en milliards d'euros et marge nette", MARGE, H=420, ident='hr',
                                  tips=[f"Exercice {a}\n{fr(e(rn))} Md€ de résultat net ({fr(rn/1, 1)} Md$)\nMarge nette : {fr(mg)} %\nBPA : {fr(b/EUR, 2)} € ({fr(b, 2)} $)"
                                        for a, rn, mg, b in zip(range(2021, 2026), RN, MARGE, BPA)]) + '</figure>')
        + grille(tuile('ok', 'BPA 2025', f"{fr(e(10.81), 2)} €", '×1,9 depuis 2021'),
                 tuile('neutre', f'PER au {JOUR}*', fr_per(PER_N), 'cours ÷ bénéfice par action, 12 mois'), mn=300)
        + f'<p class="source">* Hors réévaluation des participations (SpaceX, Anthropic) : elles ont ajouté 99 Md$ de bénéfice sur papier en 9 mois. Avec elles, le PER tombe à {fr_per(per(CN["c"], BPA12_PUBLIE))} et donne une image trompeuse.</p>',
        R, 'sceptique', "Sur 100 € de ventes, Alphabet garde 33 € de bénéfice net en 2025. Le creux de 2022 : des pertes sur ses placements (après 12 Md$ de gains en 2021) et des coûts en hausse.",
        "Source : Alphabet, 10-K et communiqués. BPA (bénéfice par action) ajusté de la division par 20 de juillet 2022."))
    S.append(section(5, 'LA', 'SOLIDITÉ', "Bilan au 30/09/2026, flux sur 12 mois",
        grille(tuile('ok', 'Trésorerie nette', f"+{fr(e(138.980), 0)} Md€", f"dont {fr(e(75.2), 0)} d'actions SpaceX"), tuile('ko', 'Dette', f"{fr(e(126.118), 0)} Md€", '×2,7 depuis janvier'),
               tuile('ko', 'Flux de trésorerie libre', f"−{fr(e(9.065))} Md€", 'au 3e trimestre, 2e négatif'), tuile('neutre', 'Sur 12 mois', f"+{fr(e(19.747))} Md€", f"{fr(e(73.266))} Md€ en 2025"), mn=240)
        + carte(f'<div class="surtitre">Investissements</div><p style="margin:6px 0 0;font-size:18px">Prévision 2026 : <b>{fr(e(195), 0)} à {fr(e(205), 0)} Md€</b> (195 à 205 Md$), deux fois plus qu\'en 2025, '
                'pour des centres de données, des serveurs et des puces. Hausse « significative » annoncée pour 2027. Pour payer, Alphabet emprunte (6 Md€ et 6 Md$ canadiens d\'obligations en novembre) '
                'et a levé environ 50 Md$ en actions en juin, dont 10 Md$ apportés par Berkshire Hathaway.</p>'),
        R, 'sueur', "Alphabet dépense plus qu'elle ne gagne pour construire ses centres de données. Elle garde plus de cash que de dette, mais une bonne part de ce cash est en actions SpaceX qu'elle ne peut pas encore vendre.",
        "Source : Alphabet, communiqué et 10-Q du 3e trimestre ; émissions de novembre non incluses dans le bilan. Flux de trésorerie libre = flux d'exploitation − investissements."))
    S.append(section(6, 'LE', 'DIVIDENDE', "Par action et par année de versement, en euros",
        carte('<figure>' + barres([e(x) for x in (0.60, 0.83, 0.87)], ['2024', '2025', '2026*'], lambda x: fr(x, 2), GOLD, "Dividende d'Alphabet par action et par année de versement, en euros", H=320, hach=2, ident='hd',
                                  tips=[f"{a}\n{fr(x/EUR, 2)} € par action ({fr(x, 2)} $)\n{t}" for a, x, t in [(2024, 0.60, '3 versements de 0,20 $, le premier en juin 2024'),
                                        (2025, 0.83, '0,20 $ puis 3 × 0,21 $'), (2026, 0.87, '0,21 $ puis 3 × 0,22 $, dont 0,22 $ versé le 14/12')]])
              + '<figcaption class="source">* dont 0,22 $ versé le 14/12. Premier dividende de l\'histoire d\'Alphabet en juin 2024.</figcaption></figure>')
        + grille(tuile('ok', 'Hausse de 5 % par an', '0,22 $', 'par trimestre'), tuile('neutre', f'Rendement au {JOUR}', f"{fr(100*DIV_AN/CN['c'])} %", '0,88 $ par an'),
                 tuile('ko', "Rachats d'actions 2026", '0 €', f"{fr(e(45.709))} Md€ en 2025"), tuile('ko', "Nombre d'actions", '+1,7 %', 'depuis janvier'), mn=240),
        R, 'haussement', "Le dividende monte, mais il reste petit. Le vrai changement : Alphabet ne rachète plus ses actions, elle en émet. Action américaine : compte-titres, pas de PEA."))
    # investissements = achats d'immobilisations ÷ CA du trimestre clos le 30/09/2026 (Md$, sources.md section 7)
    riv = [(n, lg, 100*cx/ca, g, mo) for n, lg, cx, ca, g, mo in [('Alphabet', 'googl.png', 51.355, 127.577, '+25 %', 32), ('Microsoft', 'msft.png', 39.367, 92.3, '+19 %', 50),
                                                                    ('Meta', 'meta.png', 33.942, 64.601, '+26 %', 20), ('Amazon', 'amzn.png', 77.259, 201.944, '+12 %', 14)]]
    rows = ''.join(f'<tr><td><img src="{R}assets/img/{lg}" alt="{n}" style="height:24px;width:auto;max-width:130px"></td>'
                   f'<td><div style="display:flex;align-items:center;gap:10px"><span style="display:block;height:14px;border-radius:7px;background:{GOLD};width:{iv/55*70:.0f}%"></span><b>{fr(iv, 0)} €</b></div></td>'
                   f'<td style="font-weight:700;color:{GREEN}">{g}</td><td style="font-weight:800;font-size:20px">{mo} %{"*" if n == "Meta" else ""}</td></tr>' for n, lg, iv, g, mo in riv)
    _illus = lambda coin: (lambda *a, **k: section(*a, coin=coin, **k))   # section avec Mister Coin illustré à droite du titre
    S.append(_illus('site_balance')(7, 'FACE À SES', 'RIVAUX', "Trimestre clos le 30/09/2026 pour les quatre",
        carte(f'<div class="tableau"><table><thead><tr><th scope="col">Entreprise</th><th scope="col">Investissements pour 100 € de ventes</th><th scope="col">Croissance</th><th scope="col">Marge d\'exploitation</th></tr></thead><tbody>{rows}</tbody></table></div>'),
        R, 'reflechit', "Les quatre géants réinvestissent 38 à 53 € pour 100 € de ventes. Alphabet croît plus vite que Microsoft et Amazon, avec une marge plus faible que Microsoft.",
        "Investissements = achats d'immobilisations du trimestre (tableau des flux) ÷ chiffre d'affaires. Croissance du chiffre d'affaires sur un an. * Meta : 35 % hors charge judiciaire de 9,9 Md$. "
        "Pas de PER comparé ici : celui d'Alphabet est retraité des participations, ceux des rivaux ne le sont pas."))
    surv = ''.join(f'<li style="display:flex;flex-direction:column;padding:14px 0;border-top:1px solid {LINE}"><b style="font-size:18px">{a}</b><span class="gris">{b}</span></li>'
                   for a, b in [("Le dividende du 14 décembre", "0,22 $ par action, détachement le 7 décembre."), ("Les résultats de début février", "Avec le budget d'investissement 2027, annoncé en forte hausse."),
                                ("Les émissions d'actions", "Encore 27,6 Md$ possibles dans le programme en cours.")])
    S.append(_illus('site_longue_vue')(8, "CE QU'IL FAUT", 'SURVEILLER', "Trois rendez-vous datés", R=R, corps=f'<ul class="carte" style="list-style:none;margin:0;padding:4px 24px">{surv}</ul>'))
    src = ''.join(f'<li><a href="{u}">{n}</a></li>' for n, u in SOURCES)
    S.append(f'<section class="section" id="sources"><h3 style="font-size:22px">Sources et méthode</h3><ul style="margin:0;padding-left:20px;line-height:1.9;font-size:15px">{src}</ul>'
             '<p class="gris petit" style="margin:0">Ratios calculés par Actions Bénéfices : marge nette = résultat net ÷ chiffre d\'affaires ; PER = cours ÷ bénéfice par action des 12 derniers mois, hors réévaluation des participations ; '
             'investissements pour 100 € de ventes = achats d\'immobilisations ÷ chiffre d\'affaires du trimestre ; BPA ajusté de la division par 20 de 2022. Comptes convertis au taux de référence BCE du 23/11/2026 ; '
             'cours, capitalisation, PER et rendement recalculés chaque soir avec le dernier cours de clôture et le dernier taux BCE. Le détail de chaque chiffre est dans le fichier de sources de l\'épisode.</p></section>')
    toc = ''.join(f'<a href="#s{i}">{x}</a>' for i, x in enumerate(['Identité', 'Croissance', "D'où vient l'argent", 'Rentabilité', 'Solidité', 'Dividende', 'Rivaux', 'À surveiller'], 1)) + '<a href="#historique">Historique</a>'
    chute = 100*(CN['c']/RECORD-1)
    tete = (f'<p class="fil"><a href="{R}fiches/">Fiches entreprises</a> › {m["nom"]}</p><div class="hero"><div>'
            f'<img src="{R}assets/img/googl.png" alt="Alphabet" style="height:40px;width:auto;align-self:flex-start">'
            f'<h1>QUE VAUT <em>ALPHABET ?</em></h1><p class="chapo">{m["accroche"]}</p>'
            f'<div class="pastilles"><span title="{m['comptes_officiel']}"><b>Comptes du {m["comptes"]}</b>, publiés le {jj_mm_aaaa(m["comptes_publies"])}</span><span><b>Cours et PER au {jj_mm_aaaa(CN["date"])}</b>, {'recalculés chaque soir' if not FIGE else 'figés (version archivée)'}</span>'
            f'<span>Prochaine mise à jour des comptes : après les résultats de {m["prochains_txt"]}</span><span class="alerte">Je détiens des actions Alphabet</span></div></div>'
            f'<img src="{R}assets/img/loupe.webp" alt="Mister Coin examine les comptes à la loupe"></div>'
            + grille(tuile('ok', "Chiffre d'affaires 12 mois", f"{fr(e(471.097), 0)} Md€", '+25 % au dernier trimestre'), tuile('ok', 'Marge nette', '33 %', 'exercice 2025'),
                     tuile('ko' if chute < 0 else 'ok', 'Depuis le record du 13/05', ('+' if chute >= 0 else '−') + fr(abs(chute), 0) + ' %', f"cours au {JOUR}"),
                     tuile('neutre', f'PER au {JOUR}', fr_per(PER_N), 'hors participations'))
            + f'<nav class="sommaire" aria-label="Sommaire de la fiche">{toc}</nav>')
    return tete + ''.join(S)
