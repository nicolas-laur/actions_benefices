"""Fiche entreprise Micron (carrousel n°4 du 25/11/2026). Chiffres et sources : episodes/2026-11-25_fiche_micron/sources.md (clôture du 24/11/2026, BCE 1,0963)."""
from composants import *

META = dict(slug='micron', titre='Que vaut Micron ?', nom='Micron', date='2026-11-25', date_txt='25/11/2026', chiffres_au='24/11/2026',
            # comptes : à mettre à jour après chaque publication trimestrielle (site/outils/MAJ_FICHES.md)
            comptes="trimestre de juin à début septembre 2026", comptes_officiel="4e trimestre de l'exercice 2026, clos le 03/09/2026 (Micron clôture fin août ou début septembre)", comptes_publies='2026-09-30',
            annee=2026, trimestre=3, version='2026-t3',   # trimestre civil des comptes, sert à l'historique
            prochains_resultats='2026-12-16', date_confirmee=False, prochains_txt='mi-décembre 2026 (date pas encore annoncée)', ticker='mu',
            description="Fiche entreprise Micron : croissance, rentabilité, solidité, dividende et rivaux (Samsung, SK hynix), comptes de l'exercice 2026, PER recalculé chaque soir, sources en lien.",
            accroche="Un bénéfice multiplié par 10 en un an, et pourtant une action divisée par deux depuis son record de juin. La mémoire marche en montagnes russes : on remet les chiffres à plat.",
            detient=False, pose='loupe', logo='mu.png')
EUR = 1.0963          # taux BCE du 24/11/2026, pour convertir les comptes (figés jusqu'au prochain trimestre)
def e(x): return x/EUR

# ---- ce qui bouge chaque soir avec le cours (site/cours.py) ; BPA, dividende et actions : derniers comptes publiés ----
from cours import cours, taux, per, fr_per, fr_var, jj_mm, jj_mm_aaaa
FIGE = False   # True dans la copie archivée d'une version (site/outils/MAJ_FICHES.md) : cours et taux gelés aux valeurs ci-dessous
BPA12 = 74.33          # BPA dilué de l'exercice 2026 (clos le 03/09/2026, donc les 12 derniers mois), en $ (sources.md, section 2)
ACTIONS = 1.131        # milliards d'actions (capitalisation de 712,56 Md$ au 24/11 ÷ 629,79 $, cohérent avec le 10-K 2026)
DIV_AN = 0.60          # dividende annuel actuel, 4 × 0,15 $
RECORD = 1213.56       # record de clôture MU, 25/06/2026
CN = cours('mu', 629.79, '2026-11-24', -11.01, fige=FIGE)
TX, TX_DATE = taux(1.0963, '2026-11-24', fige=FIGE)
JOUR = jj_mm(CN['date'])
PER_N = per(CN['c'], BPA12)

AN = list(range(2022, 2027))
CA = [30.758, 15.540, 25.111, 37.378, 133.188]; RN = [8.687, -5.833, 0.778, 8.539, 84.969]
MARGE = [28.2, -37.5, 3.1, 22.8, 63.8]; BPA = [7.75, -5.34, 0.70, 7.59, 74.33]

def _tips_croissance():
    t = []
    for i, x in enumerate(CA):
        l = [f"Exercice {AN[i]} (clos fin août ou début septembre)", f"{fr(e(x))} Md€ ({fr(x)} Md$)"]
        if i: l.append(f"{'+' if x >= CA[i-1] else '−'}{fr(abs(100*(x/CA[i-1]-1)), 0)} % sur un an")
        t.append('\n'.join(l))
    return t

def _flux():
    d = dict(dc=18.002, cm=16.283, mc=13.114, ae=6.824, ca=54.229, mb=47.047, cr=7.182, re=43.751, ch=3.296, rn=37.701, im=6.050)
    v = {i: e(x) for i, x in d.items()}
    N = {'dc': (170, 90, TEAL), 'cm': (170, 228, TEAL), 'mc': (170, 357, LIME), 'ae': (170, 468, LIME),
         'ca': (420, 150, INK), 'mb': (640, 110, GREEN), 'cr': (640, 430, RED), 're': (840, 90, GREEN), 'ch': (840, 380, RED),
         'rn': (990, 80, GREEN), 'im': (990, 330, RED)}
    L = [('dc', 'ca', v['dc'], TEAL_R), ('cm', 'ca', v['cm'], TEAL_R), ('mc', 'ca', v['mc'], LIME_R), ('ae', 'ca', v['ae'], LIME_R),
         ('ca', 'mb', v['mb'], GREEN_R), ('ca', 'cr', v['cr'], RED_R), ('mb', 're', v['re'], GREEN_R), ('mb', 'ch', v['ch'], RED_R),
         ('re', 'rn', v['rn'], GREEN_R), ('re', 'im', v['im'], RED_R)]
    def p(i): return f"{fr(100*d[i]/d['ca'], 0)} % des ventes"
    lab = {'dc': ('l', [('Centres de données', 'n'), (fr(v['dc']), 'v')]),
           'cm': ('l', [('Cloud', 'n'), (fr(v['cm']), 'v')]),
           'mc': ('l', [('Mobiles et PC', 'n'), (fr(v['mc']), 'v')]),
           'ae': ('l', [('Auto et industrie', 'n'), (fr(v['ae']), 'v')]),
           'ca': ('t', [("Chiffre d'affaires", 'n'), (fr(v['ca']), 'v'), ('+379 % sur 1 an', 's')]),
           'mb': ('t', [('Marge brute', 'n'), (fr(v['mb']), 'v'), (p('mb'), 's')]),
           'cr': ('b', [('Coût des ventes', 'n'), ('('+fr(v['cr'])+')', 'v')]),
           're': ('t', [("Résultat d'exploitation", 'n'), (fr(v['re']), 'v'), (p('re'), 's')]),
           'ch': ('b', [('Recherche et frais', 'n'), ('('+fr(v['ch'])+')', 'v')]),
           'rn': ('r', [('Résultat net', 'n'), (fr(v['rn']), 'v'), (p('rn'), 's')]),
           'im': ('r', [('Impôts', 'n'), ('('+fr(v['im'])+')', 'v'), ('nets des intérêts', 's')])}
    def m(i): return f"{fr(v[i])} Md€ ({fr(d[i])} Md$)"
    T = {'dc': ["Centres de données (Core Data Center)", m('dc'), p('dc'), "Mémoire vendue aux fabricants de serveurs et aux grandes entreprises."],
         'cm': ["Cloud (Cloud Memory)", m('cm'), p('cm'), "Mémoire vendue aux géants du cloud, dont la mémoire à haut débit (HBM) des puces d'IA."],
         'mc': ["Mobiles et PC (Mobile and Client)", m('mc'), p('mc'), "Mémoire des smartphones et des ordinateurs."],
         'ae': ["Auto et industrie (Automotive and Embedded)", m('ae'), p('ae'), "Mémoire des voitures, des machines et des objets connectés."],
         'ca': ["Chiffre d'affaires du trimestre", m('ca'), "+379 % sur un an", "4e trimestre de l'exercice 2026, clos le 03/09/2026. DRAM 73 %, NAND 26 %."],
         'cr': ["Coût des ventes", m('cr'), p('cr'), "Usines, matériaux et main-d'œuvre pour fabriquer les puces."],
         'mb': ["Marge brute", m('mb'), p('mb'), "Ce qui reste une fois les puces fabriquées."],
         'ch': ["Recherche et frais", m('ch'), p('ch'), f"Dont {fr(e(1.913))} Md€ de recherche et développement, puis frais commerciaux, généraux et autres charges."],
         're': ["Résultat d'exploitation", m('re'), p('re'), "Ce que rapporte l'activité elle-même, avant intérêts et impôts."],
         'im': ["Impôts, nets des intérêts reçus", m('im'), f"Impôts de {fr(e(6.583))} Md€, moins {fr(e(0.575))} Md€ d'intérêts reçus sur la trésorerie et autres éléments."],
         'rn': ["Résultat net", m('rn'), p('rn'), "Le bénéfice du trimestre."]}
    noms = dict(dc='Centres de données', cm='Cloud', mc='Mobiles et PC', ae='Auto et industrie', ca="Chiffre d'affaires", mb='Marge brute',
                cr='Coût des ventes', re="Résultat d'exploitation", ch='Recherche et frais', rn='Résultat net', im='Impôts')
    P = {'dc': ['server'], 'cm': ['cloud-outline'], 'mc': ['cellphone', 'laptop'], 'ae': ['car-side', 'robot-industrial'], 'cr': ['factory'], 'ch': ['flask-outline'], 'rn': ['cash-multiple']}
    return flux(N, L, v, 6, lab, "Compte de résultat de Micron au 4e trimestre de l'exercice 2026 en rubans : du chiffre d'affaires au résultat net",
                H=610, tips={i: '\n'.join(x) for i, x in T.items()}, noms=noms, pictos=P)

SOURCES = [("Micron, résultats du 4e trimestre de l'exercice 2026 (30/09/2026, SEC)", "https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000018/a2026q4ex991-pressrelease.htm"),
           ("Micron, commentaires de la direction du 30/09/2026", "https://s25.q4cdn.com/621799436/files/doc_financials/2026/q4/Q4-FY26-Prepared-Remarks.pdf"),
           ("Micron, rapport annuel 10-K de l'exercice 2023", "https://www.sec.gov/Archives/edgar/data/723125/000072312523000054/mu-20230831.htm"),
           ("Micron, résultats du 4e trimestre de l'exercice 2023", "https://www.sec.gov/Archives/edgar/data/723125/000072312523000051/a2023q4ex991-pressrelease.htm"),
           ("Micron, lancement du dividende (02/08/2021)", "https://www.sec.gov/Archives/edgar/data/723125/000072312521000056/exhibit991-pressreleaseq42.htm"),
           ("Stock Analysis, comptes et cours de Micron", "https://stockanalysis.com/stocks/mu/financials/"),
           ("Admiral Markets, abaissement de BNP Paribas (24/11/2026)", "https://admiralmarkets.com/analytics/traders-blog/micron-stock-downgrade-bnp-paribas-775-target"),
           ("Trefis, record de clôture du 25/06/2026", "https://www.trefis.com/stock/mu/articles/625793/why-did-micron-stock-fall-nearly-8/2026-11-17"),
           ("Benzinga, rachats d'actions après le 9 décembre", "https://www.benzinga.com/markets/earnings/26/10/62098102"),
           ("Counterpoint Research, parts du marché de la DRAM", "https://www.counterpointresearch.com/en/insights/dram-super-cycle-nears-dollar-200b"),
           ("SK hynix, résultats du 3e trimestre 2026", "https://news.skhynix.com/en/q3-2026-business-results/"),
           ("Samsung Electronics, résultats du 3e trimestre 2026", "https://news.samsung.com/global/samsung-electronics-announces-third-quarter-2026-results?full=1"),
           ("Samsung Electronics, résultats du 3e trimestre 2025", "https://news.samsung.com/be_fr/samsung-electronics-announces-third-quarter-2025-results"),
           ("Banque de France, taux de référence BCE du 24/11/2026", "https://www.banque-france.fr/fr/statistiques/taux-et-cours/taux-de-change-parites-quotidiennes-2026-11-24")]

def corps(R):
    m = META
    S = []
    cap = CN['c']*ACTIONS
    var = CN['var'] or 0
    S.append(section(1, 'CARTE', "D'IDENTITÉ", "Chiffre d'affaires du 4e trimestre de l'exercice 2026",
        carte(f'<div style="display:flex;gap:22px;align-items:center;flex-wrap:wrap"><img src="{R}assets/img/mu.png" alt="Logo Micron" style="height:40px;width:auto">'
              '<p style="margin:0;flex:1 1 360px;font-size:18px">Fabricant américain de puces mémoire : la DRAM, mémoire de travail des ordinateurs et des serveurs, et la NAND, qui stocke les données. Ses plus gros clients sont aujourd\'hui les centres de données et le cloud, portés par l\'IA.</p></div>')
        + '<div class="grille" style="--min:320px">'
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Par client</div>' + pbar('Centres de données', 33.2, TEAL) + pbar('Cloud', 30.0, TEAL)
                + pbar('Mobiles et PC', 24.2, LIME) + pbar('Auto et industrie', 12.6, LIME) + '</div>')
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Par produit</div>' + pbar('DRAM', 73, '#7FB2EA') + pbar('NAND', 26, '#9AA6B8') + '</div>') + '</div>'
        + grille(tuile('neutre', 'En bourse depuis', '1984', 'Nasdaq'), tuile('neutre', 'Capitalisation', f"≈ {fr(cap/TX, 0)} Md€", f"≈ {fr(cap, 0)} Md$"),
                 tuile('ok' if var > 0 else 'ko' if var < 0 else 'neutre', f'Cours au {JOUR}', f"{fr(CN['c']/TX, 2)} €", f"{fr(CN['c'], 2)} $" + (', ' + fr_var(CN['var']) if CN['var'] is not None else ''))),
        R, 'loupe', "Que de la mémoire ! Plus de 6 euros de ventes sur 10 viennent des centres de données et du cloud. Et près des trois quarts, de la DRAM.",
        f"Source : Micron, communiqué et commentaires du 30/09/2026 ; cours de clôture MU du {jj_mm_aaaa(CN['date'])} (Nasdaq, via Yahoo Finance), recalculé chaque soir ; 1 € = {fr(TX, 4)} $ (BCE, {jj_mm_aaaa(TX_DATE)}). "
        "Capitalisation ≈ cours × 1,13 milliard d'actions."))
    S.append(section(2, 'LA', 'CROISSANCE', "Chiffre d'affaires annuel, en milliards d'euros",
        carte('<figure>' + barres([e(x) for x in CA], [str(a) for a in AN], fr, LIME, "Chiffre d'affaires annuel de Micron en milliards d'euros, exercices 2022 à 2026", H=380, ident='mc',
                                  tips=_tips_croissance(), nom_barres="Chiffre d'affaires (Md€)") + '</figure>')
        + grille(tuile('ok', 'Sur 4 ans', '+44 %/an', '2022 → 2026'), tuile('ok', 'Dernier trimestre', '+379 %', 'sur un an'), tuile('ok', 'Exercice 2026', '×3,6', f"{fr(e(133.188))} Md€")),
        R, 'court', "Les ventes ont été divisées par deux en 2023, puis multipliées par 3,6 en 2026. Le marché de la mémoire alterne pénuries et excès d'offre, et les prix suivent.",
        f"Source : Micron, 10-K 2023 et communiqué du 30/09/2026 ; Stock Analysis pour 2024. Exercices clos fin août ou début septembre. 1 € = {fr(EUR, 4)} $."))
    S.append(section(3, "D'OÙ VIENT", "L'ARGENT", "4e trimestre de l'exercice 2026, clos le 03/09/2026, en milliards d'euros", carte('<figure>' + _flux() + '</figure>'), R, None, None,
        "Source : Micron, résultats du 30/09/2026 (CA 54,2 Md$). Mise en page inspirée de App Economy Insights (How They Make Money)."))
    S.append(section(4, 'LA', 'RENTABILITÉ', "Résultat net (Md€) et marge nette, par exercice",
        carte('<figure>' + barres([e(x) for x in RN], [str(a) for a in AN], fr, GREEN, "Résultat net de Micron par exercice en milliards d'euros et marge nette", MARGE, H=420, ident='mr',
                                  tips=[f"Exercice {a}\n{fr(e(rn))} Md€ de résultat net ({fr(rn)} Md$)\nMarge nette : {fr(mg)} %\nBPA : {fr(b/EUR, 2)} € ({fr(b, 2)} $)"
                                        for a, rn, mg, b in zip(AN, RN, MARGE, BPA)]) + '</figure>')
        + grille(tuile('ok', 'BPA 2026', f"{fr(e(74.33), 2)} €", '×9,8 sur un an'),
                 tuile('neutre', f'PER au {JOUR}', fr_per(PER_N), 'cours ÷ bénéfice par action, 12 mois'), mn=300),
        R, 'sueur', "De −5,8 à +85 Md$ de bénéfice en trois ans ! En 2023, les prix de la mémoire s'étaient effondrés et Micron a dû déprécier ses stocks. En 2026, il garde 64 € de bénéfice pour 100 € de ventes.",
        "Source : Micron, 10-K et communiqués. BPA = bénéfice par action dilué. Le PER se calcule ici sur un bénéfice record : BNP Paribas craint un excès d'offre de mémoire dès mi-2027."))
    S.append(section(5, 'LA', 'SOLIDITÉ', "Bilan au 03/09/2026, flux de l'exercice 2026",
        grille(tuile('ok', 'Trésorerie nette', f"+{fr(e(68.3))} Md€", '68,3 Md$ selon Micron'), tuile('ok', 'Dette', f"{fr(e(5.179))} Md€", '−64 % en un an'),
               tuile('ok', 'Flux de trésorerie libre', f"{fr(e(62.308))} Md€", f"{fr(e(3.721))} Md€ en 2025"), tuile('neutre', 'Investissements', f"{fr(e(27.367))} Md€", 'exercice 2026, nets'), mn=240)
        + carte(f'<div class="surtitre">Cash et placements</div><p style="margin:6px 0 0;font-size:18px"><b>{fr(e(73.48))} Md€</b> (73,5 Md$) de cash, placements et trésorerie bloquée, contre {fr(e(5.179))} Md€ de dette. '
                'Micron prévoit environ 25 Md$ d\'investissements au 1er semestre de l\'exercice 2027, et davantage au 2e, pour de nouvelles usines.</p>'),
        R, 'site_tirelire', "Micron a remboursé près des deux tiers de sa dette en un an. Une fois ses investissements payés, il lui est resté 57 Md€ de cash sur l'exercice, contre 3,4 Md€ un an plus tôt.",
        "Source : Micron, communiqué et commentaires du 30/09/2026. Flux de trésorerie libre ajusté selon Micron = flux d'exploitation − investissements nets."))
    S.append(section(6, 'LE', 'DIVIDENDE', "Par action et par année de versement, en euros",
        carte('<figure>' + barres([e(x) for x in (0.10, 0.43, 0.46, 0.46, 0.46, 0.565)], [str(a) for a in range(2021, 2027)], lambda x: fr(x, 2), GOLD,
                                  "Dividende de Micron par action et par année de versement, en euros", H=320, ident='md',
                                  tips=[f"{a}\n{fr(x/EUR, 2)} € par action ({fr(x, 3 if x == 0.565 else 2)} $)\n{t}" for a, x, t in [(2021, 0.10, 'Premier versement le 18/10/2021'), (2022, 0.43, '0,10 $ puis 0,115 $'),
                                        (2023, 0.46, '4 × 0,115 $'), (2024, 0.46, '4 × 0,115 $'), (2025, 0.46, '4 × 0,115 $'), (2026, 0.565, '0,115 $ puis 3 × 0,15 $')]])
              + '<figcaption class="source">Dividende lancé en août 2021. Dernier versement : 0,15 $ le 29/10/2026.</figcaption></figure>')
        + grille(tuile('ok', 'Hausse en 2026', '+30 %', '0,15 $ par trimestre'), tuile('neutre', f'Rendement au {JOUR}', f"{fr(100*DIV_AN/CN['c'])} %", '0,60 $ par an'),
                 tuile('neutre', 'Part du bénéfice versée', f"{fr(100*DIV_AN/BPA12)} %", 'dividende ÷ BPA'), tuile('neutre', "Rachats d'actions", f"{fr(e(0.650))} Md€", 'exercice 2026'), mn=240),
        R, 'haussement', "Le dividende reste symbolique : moins de 1 % du bénéfice. Micron veut surtout rendre son cash par des rachats d'actions, qu'il prévoit d'augmenter après le 9 décembre. Action américaine : compte-titres, pas de PEA.",
        "Source : Micron, communiqués ; historique des versements recoupé sur Stock Analysis."))
    riv = [('Micron', 'mu.png', 21, '+379 %', '81 %'), ('Samsung', 'ssnlf.png', 38, '+344 %*', '72 %*'), ('SK hynix', 'skh.png', 29, '+328 %', '80 %')]
    rows = ''.join(f'<tr><td><img src="{R}assets/img/{lg}" alt="{n}" style="height:{34 if lg == "skh.png" else 24}px;width:auto;max-width:130px"></td>'
                   f'<td><div style="display:flex;align-items:center;gap:10px"><span style="display:block;height:14px;border-radius:7px;background:{GOLD};width:{pm/40*70:.0f}%"></span><b>{pm} %</b></div></td>'
                   f'<td style="font-weight:700;color:{GREEN}">{g}</td><td style="font-weight:800;font-size:20px">{mo}</td></tr>' for n, lg, pm, g, mo in riv)
    _illus = lambda coin: (lambda *a, **k: section(*a, coin=coin, **k))   # section avec Mister Coin illustré à droite du titre
    S.append(_illus('site_balance')(7, 'FACE À SES', 'RIVAUX', "Trimestre juillet-septembre 2026 (clos le 03/09 pour Micron)",
        carte(f'<div class="tableau"><table><thead><tr><th scope="col">Entreprise</th><th scope="col">Part du marché de la DRAM</th><th scope="col">Croissance</th><th scope="col">Marge d\'exploitation</th></tr></thead><tbody>{rows}</tbody></table></div>'),
        R, 'reflechit', "Le n°3 du trio. Les trois profitent de la même envolée des prix, mais Micron a perdu 5 points de part de marché en un an, et le chinois CXMT monte (9 %).",
        "Part du marché de la DRAM en chiffre d'affaires au 3e trimestre 2026 (Counterpoint Research). Croissance du chiffre d'affaires sur un an. "
        "* Samsung : division semi-conducteurs, qui comprend aussi la fonderie et les puces logiques."))
    surv = ''.join(f'<li style="display:flex;flex-direction:column;padding:14px 0;border-top:1px solid {LINE}"><b style="font-size:18px">{a}</b><span class="gris">{b}</span></li>'
                   for a, b in [("Le 9 décembre", "Deuxième anniversaire des aides du CHIPS Act : Micron prévoit d'augmenter ses rachats d'actions ensuite."),
                                ("Les résultats de mi-décembre", "Prévision de Micron : 61,5 Md$ de chiffre d'affaires, à 1,5 Md$ près, et une marge brute d'environ 86 %."),
                                ("Les prix de la mémoire", "Micron voit l'offre et la demande plus tendues en 2027 et 2028 ; BNP Paribas craint un excès d'offre dès mi-2027.")])
    S.append(_illus('site_longue_vue')(8, "CE QU'IL FAUT", 'SURVEILLER', "Trois rendez-vous", R=R, corps=f'<ul class="carte" style="list-style:none;margin:0;padding:4px 24px">{surv}</ul>'))
    src = ''.join(f'<li><a href="{u}">{n}</a></li>' for n, u in SOURCES)
    S.append(f'<section class="section" id="sources"><h3 style="font-size:22px">Sources et méthode</h3><ul style="margin:0;padding-left:20px;line-height:1.9;font-size:15px">{src}</ul>'
             '<p class="gris petit" style="margin:0">Ratios calculés par Actions Bénéfices : marge nette = résultat net ÷ chiffre d\'affaires ; PER = cours ÷ bénéfice par action des 12 derniers mois (exercice 2026) ; '
             'part du bénéfice versée = dividende annuel ÷ bénéfice par action. Comptes convertis au taux de référence BCE du 24/11/2026 ; '
             'cours, capitalisation, PER et rendement recalculés chaque soir avec le dernier cours de clôture et le dernier taux BCE. Le détail de chaque chiffre est dans le fichier de sources de l\'épisode.</p></section>')
    toc = ''.join(f'<a href="#s{i}">{x}</a>' for i, x in enumerate(['Identité', 'Croissance', "D'où vient l'argent", 'Rentabilité', 'Solidité', 'Dividende', 'Rivaux', 'À surveiller'], 1)) + '<a href="#historique">Historique</a>'
    chute = 100*(CN['c']/RECORD-1)
    tete = (f'<p class="fil"><a href="{R}fiches/">Fiches entreprises</a> › {m["nom"]}</p><div class="hero"><div>'
            f'<img src="{R}assets/img/mu.png" alt="Micron" style="height:40px;width:auto;align-self:flex-start">'
            f'<h1>QUE VAUT <em>MICRON ?</em></h1><p class="chapo">{m["accroche"]}</p>'
            f'<div class="pastilles"><span title="{m['comptes_officiel']}"><b>Comptes du {m["comptes"]}</b>, publiés le {jj_mm_aaaa(m["comptes_publies"])}</span><span><b>Cours et PER au {jj_mm_aaaa(CN["date"])}</b>, {'recalculés chaque soir' if not FIGE else 'figés (version archivée)'}</span>'
            f'<span>Prochaine mise à jour des comptes : après les résultats de {m["prochains_txt"]}</span></div></div>'
            f'<img src="{R}assets/img/loupe.webp" alt="Mister Coin examine les comptes à la loupe"></div>'
            + grille(tuile('ok', "Chiffre d'affaires 12 mois", f"{fr(e(133.188), 0)} Md€", '+256 % sur un an'), tuile('ok', 'Marge nette', '64 %', 'exercice 2026'),
                     tuile('ko' if chute < 0 else 'ok', 'Depuis le record du 25/06', ('+' if chute >= 0 else '−') + fr(abs(chute), 0) + ' %', f"cours au {JOUR}"),
                     tuile('neutre', f'PER au {JOUR}', fr_per(PER_N), '12 derniers mois'))
            + f'<nav class="sommaire" aria-label="Sommaire de la fiche">{toc}</nav>')
    return tete + ''.join(S)
