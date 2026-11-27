"""Fiche entreprise Schneider Electric (carrousel n°7 du 26/11/2026). Chiffres et sources : episodes/2026-11-26_fiche_schneider/sources.md (clôture du 25/11/2026 ; ABB, Eaton et PTC convertis au taux BCE du 25/11/2026, 1,0935)."""
from composants import *

META = dict(slug='schneider-electric', titre='Que vaut Schneider Electric ?', nom='Schneider Electric', date='2026-11-26', date_txt='26/11/2026', chiffres_au='25/11/2026',
            # comptes : à mettre à jour après chaque publication (site/outils/MAJ_FICHES.md) ; Schneider publie des comptes complets par semestre et son chiffre d'affaires chaque trimestre
            comptes="1er semestre 2026 (ventes au 30/09)", comptes_officiel="Comptes semestriels au 30/06/2026 (publiés le 30/07/2026) et chiffre d'affaires du 3e trimestre 2026 (publié le 16/10/2026)", comptes_publies='2026-10-16',
            annee=2026, trimestre=3, version='2026-t3',   # trimestre civil des derniers chiffres publiés, sert à l'historique
            prochains_resultats='2027-02-18', date_confirmee=False, prochains_txt='18 février 2027 (résultats annuels 2026)', ticker='su',
            description="Fiche entreprise Schneider Electric : croissance, rentabilité, solidité, dividende, rachat de PTC et rivaux (ABB, Eaton), comptes du 1er semestre 2026, PER recalculé chaque soir, sources en lien.",
            accroche="Des ventes record, le plus gros rachat de son histoire, et une action en baisse depuis l'annonce. Schneider parie sur PTC et les centres de données : on remet les chiffres à plat.",
            detient=False, pose='loupe', logo='su.png')
USD = 1.0935          # taux BCE du 25/11/2026, pour ABB, Eaton et PTC (comptes en dollars)
def e(x): return x/USD

# ---- ce qui bouge chaque soir avec le cours (site/cours.py) ; BPA, dividende et actions : derniers comptes publiés ----
from cours import cours, per, fr_per, fr_var, jj_mm, jj_mm_aaaa
FIGE = False   # True dans la copie archivée d'une version (site/outils/MAJ_FICHES.md) : cours gelé à la valeur ci-dessous
BPA12 = 7.41           # BPA 2025 part du groupe, non dilué, en € (dernier exercice publié ; sources.md, section 4)
ACTIONS = 0.603605363  # milliards d'actions composant le capital au 31/10/2026 (communiqué du 25/11/2026)
DIV_AN = 4.20          # dernier dividende annuel, versé en 2026
AVANT_PTC = 303.00     # clôture du 02/10/2026, dernière séance avant l'annonce du rachat de PTC
CN = cours('su', 216.65, '2026-11-25', -4.18, fige=FIGE)
JOUR = jj_mm(CN['date'])
PER_N = per(CN['c'], BPA12)

AN = list(range(2021, 2026))
CA = [28.905, 34.176, 35.902, 38.153, 40.152]; RN = [3.204, 3.477, 4.003, 4.269, 4.163]; MARGE = [11.1, 10.2, 11.1, 11.2, 10.4]

def _tips_croissance():
    t = []
    for i, x in enumerate(CA):
        l = [f"Exercice {AN[i]}", f"{fr(x)} Md€"]
        if i: l.append(f"+{fr(100*(x/CA[i-1]-1), 0)} % sur un an (publié)")
        t.append('\n'.join(l))
    return t

def _flux():
    v = dict(an=8.312, eu=5.305, as_=3.796, ai=3.813, ca=21.226, mb=9.014, cr=12.212, re=3.613, ch=5.401, rn=2.548, im=1.065)
    N = {'an': (170, 90, TEAL), 'eu': (170, 236, TEAL), 'as_': (170, 340, LIME), 'ai': (170, 423, LIME),
         'ca': (420, 150, INK), 'mb': (640, 110, GREEN), 'cr': (640, 280, RED), 're': (840, 90, GREEN), 'ch': (840, 190, RED),
         'rn': (990, 80, GREEN), 'im': (990, 150, RED)}
    L = [('an', 'ca', v['an'], TEAL_R), ('eu', 'ca', v['eu'], TEAL_R), ('as_', 'ca', v['as_'], LIME_R), ('ai', 'ca', v['ai'], LIME_R),
         ('ca', 'mb', v['mb'], GREEN_R), ('ca', 'cr', v['cr'], RED_R), ('mb', 're', v['re'], GREEN_R), ('mb', 'ch', v['ch'], RED_R),
         ('re', 'rn', v['rn'], GREEN_R), ('re', 'im', v['im'], RED_R)]
    def p(i): return f"{fr(100*v[i]/v['ca'], 0)} % des ventes"
    lab = {'an': ('l', [('Amérique du Nord', 'n'), (fr(v['an']), 'v')]),
           'eu': ('l', [('Europe', 'n'), (fr(v['eu']), 'v')]),
           'as_': ('l', [('Chine et Asie de l\'Est', 'n'), (fr(v['as_']), 'v')]),
           'ai': ('l', [('Asie du Sud et international', 'n'), (fr(v['ai']), 'v')]),
           'ca': ('t', [("Chiffre d'affaires", 'n'), (fr(v['ca']), 'v'), ('+9,8 % sur 1 an', 's')]),
           'mb': ('t', [('Marge brute', 'n'), (fr(v['mb']), 'v'), (p('mb'), 's')]),
           'cr': ('b', [('Coût des ventes', 'n'), ('('+fr(v['cr'])+')', 'v')]),
           're': ('t', [("Résultat d'exploitation", 'n'), (fr(v['re']), 'v'), (p('re'), 's')]),
           'ch': ('b', [('Recherche et frais', 'n'), ('('+fr(v['ch'])+')', 'v')]),
           'rn': ('r', [('Résultat net', 'n'), (fr(v['rn']), 'v'), (p('rn'), 's')]),
           'im': ('r', [('Impôts et frais financiers', 'n'), ('('+fr(v['im'])+')', 'v')])}
    def m(i): return f"{fr(v[i])} Md€"
    T = {'an': ["Amérique du Nord", m('an'), p('an'), "Premier marché du groupe."],
         'eu': ["Europe", m('eu'), p('eu')],
         'as_': ["Chine et Asie de l'Est", m('as_'), p('as_')],
         'ai': ["Asie du Sud et international", m('ai'), p('ai'), "Inde, Moyen-Orient, Afrique, Amérique du Sud et Océanie."],
         'ca': ["Chiffre d'affaires du semestre", m('ca'), "+9,8 % sur un an (publié)", "1er semestre 2026, clos le 30/06/2026."],
         'cr': ["Coût des ventes", m('cr'), p('cr'), "Usines, composants et main-d'œuvre."],
         'mb': ["Marge brute", m('mb'), p('mb'), "Ce qui reste une fois les produits fabriqués."],
         'ch': ["Recherche et frais", m('ch'), p('ch'), "Recherche et développement (0,8 Md€), frais commerciaux et généraux (4,1 Md€), restructurations, amortissement des acquisitions et autres charges."],
         're': ["Résultat d'exploitation", m('re'), p('re'), "Ce que rapporte l'activité elle-même, avant frais financiers et impôts. EBITA ajusté : 4,1 Md€, soit 19,3 % des ventes."],
         'im': ["Impôts et frais financiers", m('im'), "Impôts de 0,8 Md€ et résultat financier de −0,3 Md€, moins la part des sociétés mises en équivalence."],
         'rn': ["Résultat net", m('rn'), p('rn'), "Dont 2,5 Md€ pour les actionnaires de Schneider (part du groupe), +30 % sur un an."]}
    noms = dict(an='Amérique du Nord', eu='Europe', as_="Chine et Asie de l'Est", ai='Asie du Sud et international', ca="Chiffre d'affaires", mb='Marge brute',
                cr='Coût des ventes', re="Résultat d'exploitation", ch='Recherche et frais', rn='Résultat net', im='Impôts et frais financiers')
    P = {'cr': ['factory'], 'ch': ['flask-outline'], 'rn': ['cash-multiple']}
    return flux(N, L, v, 14, lab, "Compte de résultat de Schneider Electric au 1er semestre 2026 en rubans : du chiffre d'affaires au résultat net",
                H=570, tips={i: '\n'.join(x) for i, x in T.items()}, noms=noms, pictos=P)

SOURCES = [("Schneider Electric, chiffre d'affaires du 3e trimestre 2026 (16/10/2026)", "https://www.webdisclosure.com/press-release/third-quarter-revenues-2026-odiihfxJLgs"),
           ("Schneider Electric, comptes du 1er semestre 2026 (30/07/2026, AMF)", "https://echanges.dila.gouv.fr/OPENDATA/AMF/298/2026/07/FC298640083_20260730.pdf"),
           ("Schneider Electric, résultats annuels 2025 (26/02/2026, AMF)", "https://echanges.dila.gouv.fr/OPENDATA/AMF/ECO/2026/02/FCECO081067_20260226.pdf"),
           ("Schneider Electric, émission obligataire de 10 Md$ (17/11/2026)", "https://www.webdisclosure.com/press-release/successful-pricing-of-us-10-billion-of-bonds-as-part-of-the-financing-of-the-ptc-acquisition-1VOBncKNIlE"),
           ("ABC Bourse, comptes publiés de Schneider Electric", "https://www.abcbourse.com/analyses/chiffres/SUp"),
           ("Boursorama, cours de Schneider Electric", "https://www.boursorama.com/cours/1rPSU/"),
           ("ABB, résultats du 3e trimestre 2026", "https://www.abb.com/global/en/news/139696/q3-2026-results"),
           ("Eaton, résultats du 3e trimestre 2026 (SEC)", "https://www.sec.gov/Archives/edgar/data/0001551182/000155118226000037/etn09302026exhibit99.htm"),
           ("Banque de France, taux de référence BCE du 25/11/2026", "https://www.banque-france.fr/fr/statistiques/taux-et-cours/taux-de-change-parites-quotidiennes-2026-11-25")]

def corps(R):
    m = META
    S = []
    cap = CN['c']*ACTIONS
    var = CN['var'] or 0
    logo = f'<span style="display:flex;align-items:center;gap:10px"><img src="{R}assets/img/su.png" alt="" style="height:40px;width:auto"><b style="font-size:20px">Schneider Electric</b></span>'
    S.append(section(1, 'CARTE', "D'IDENTITÉ", "Chiffre d'affaires des 9 premiers mois de 2026",
        carte(f'<div style="display:flex;gap:22px;align-items:center;flex-wrap:wrap">{logo}'
              '<p style="margin:0;flex:1 1 360px;font-size:18px">Groupe français de matériel électrique et d\'automatismes : de quoi distribuer et piloter l\'électricité dans les bâtiments, les usines et les centres de données, avec les logiciels qui vont avec.</p></div>')
        + '<div class="grille" style="--min:320px">'
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Par activité</div>' + pbar("Gestion de l'énergie", 83.4, TEAL) + pbar('Automatismes industriels', 16.6, LIME) + '</div>')
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Par région</div>' + pbar('Amérique du Nord', 39.6, '#7FB2EA') + pbar('Europe', 24.3, '#7FB2EA')
                + pbar("Chine et Asie de l'Est", 18.2, '#9AA6B8') + pbar('Asie du Sud et international', 17.9, '#9AA6B8') + '</div>') + '</div>'
        + grille(tuile('neutre', 'Cotée à', 'Paris', 'CAC 40, éligible au PEA'), tuile('neutre', 'Capitalisation', f"≈ {fr(cap, 0)} Md€", "603,6 millions d'actions"),
                 tuile('ok' if var > 0 else 'ko' if var < 0 else 'neutre', f'Cours au {JOUR}', f"{fr(CN['c'], 2)} €", fr_var(CN['var']) if CN['var'] is not None else '')),
        R, 'loupe', "Plus de 8 euros de ventes sur 10 viennent de la gestion de l'énergie. Et l'Amérique du Nord pèse déjà 4 euros sur 10, loin devant l'Europe.",
        f"Source : Schneider Electric, communiqué du 16/10/2026 ; cours de clôture SU du {jj_mm_aaaa(CN['date'])} (Euronext Paris, via Yahoo Finance), recalculé chaque soir. "
        "Capitalisation ≈ cours × 603,6 millions d'actions (capital au 31/10/2026)."))
    S.append(section(2, 'LA', 'CROISSANCE', "Chiffre d'affaires annuel, en milliards d'euros",
        carte('<figure>' + barres(CA, [str(a) for a in AN], fr, LIME, "Chiffre d'affaires annuel de Schneider Electric en milliards d'euros, de 2021 à 2025", H=380, ident='sc',
                                  tips=_tips_croissance(), nom_barres="Chiffre d'affaires (Md€)") + '</figure>')
        + grille(tuile('ok', 'Sur 4 ans', '+8,6 %/an', '2021 → 2025'), tuile('ok', '3e trimestre 2026', '+17 %', 'organique, record'), tuile('ok', 'Objectif 2026', '+12 à +14 %', 'organique, relevé en octobre')),
        R, 'court', "Les ventes montent chaque année depuis 2021. Au 3e trimestre 2026 : +17 % hors effets de change et d'acquisitions, la plus forte hausse depuis 2021, avec une demande des centres de données en hausse « à trois chiffres ».",
        "Source : Schneider Electric, communiqués annuels et du 16/10/2026. Croissance organique = à taux de change et périmètre constants."))
    S.append(section(3, "D'OÙ VIENT", "L'ARGENT", "1er semestre 2026, clos le 30/06/2026, en milliards d'euros", carte('<figure>' + _flux() + '</figure>'), R, None, None,
        "Source : Schneider Electric, comptes semestriels du 30/07/2026 (CA 21,2 Md€). Mise en page inspirée de App Economy Insights (How They Make Money)."))
    S.append(section(4, 'LA', 'RENTABILITÉ', "Résultat net part du groupe (Md€) et marge nette, par exercice",
        carte('<figure>' + barres(RN, [str(a) for a in AN], fr, GREEN, "Résultat net part du groupe de Schneider Electric par exercice en milliards d'euros et marge nette", MARGE, H=420, ident='sr',
                                  tips=[f"Exercice {a}\n{fr(rn)} Md€ de résultat net part du groupe\nMarge nette : {fr(mg)} %" for a, rn, mg in zip(AN, RN, MARGE)]) + '</figure>')
        + grille(tuile('ok', '1er semestre 2026', '2,5 Md€', 'résultat net part du groupe, +30 %'), tuile('ok', 'EBITA ajusté', '19,3 %', 'des ventes, 1er semestre 2026'),
                 tuile('neutre', f'PER au {JOUR}', fr_per(PER_N), 'cours ÷ BPA 2025 (7,41 €)'), mn=260),
        R, 'reflechit', "Sur 100 € de ventes, Schneider garde 10 à 11 € de bénéfice net, une marge stable depuis cinq ans. En 2025, le bénéfice a reculé de 2,5 % malgré des ventes en hausse, avant de rebondir au 1er semestre 2026.",
        "Source : Schneider Electric, communiqués annuels et comptes semestriels. EBITA ajusté = résultat d'exploitation avant amortissement des acquisitions, restructurations et éléments exceptionnels."))
    S.append(section(5, 'LA', 'SOLIDITÉ', "Bilan au 30/06/2026 et rachat de PTC",
        grille(tuile('neutre', 'Dette nette', '14,9 Md€', '13,2 Md€ fin 2025'), tuile('ok', 'Cash-flow libre 2025', '4,6 Md€', 'record ; 1,6 Md€ au 1er semestre 2026'),
               tuile('ko', 'Prix de PTC', f"≈ {fr(e(23.7))} Md€", '23,7 Md$ de valeur d\'entreprise'), tuile('ok', 'Notes de crédit', 'A / A2', 'S&P et Moody\'s, confirmées le 06/10'), mn=240)
        + carte(f'<div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap"><img src="{R}assets/img/ptc.png" alt="Logo PTC" style="height:30px;width:auto">'
                f'<p style="margin:0;flex:1 1 360px;font-size:18px">Annoncé le 05/10/2026 : 205 $ par action en numéraire pour l\'éditeur américain de logiciels industriels PTC. Pour payer, Schneider a émis <b>25 millions d\'actions nouvelles</b> à 240 € (6,0 Md€, environ 4,3 % du capital) '
                f'et environ <b>{fr(6.0 + e(10))} Md€ d\'obligations</b> (6,0 Md€ et 10 Md$). Finalisation attendue d\'ici le 3e trimestre 2027, sous réserve des autorisations.</p></div>'),
        R, 'site_tirelire', "Le plus gros rachat de son histoire coûte près de cinq années de cash-flow libre record. Schneider le finance surtout par la dette, et ses notes de crédit restent solides.",
        "Source : Schneider Electric, comptes semestriels, communiqués d'octobre et de novembre 2026. Dette nette hors engagements de rachat de minoritaires. 1 € = 1,0935 $ (BCE, 25/11/2026)."))
    S.append(section(6, 'LE', 'DIVIDENDE', "Par action et par année de versement, en euros",
        carte('<figure>' + barres([2.60, 2.90, 3.15, 3.50, 3.90, 4.20], [str(a) for a in range(2021, 2027)], lambda x: fr(x, 2), GOLD,
                                  "Dividende de Schneider Electric par action et par année de versement, en euros", H=320, ident='sd',
                                  tips=[f"{a}\n{fr(x, 2)} € par action\nAu titre de l'exercice {a-1}" for a, x in zip(range(2021, 2027), [2.60, 2.90, 3.15, 3.50, 3.90, 4.20])])
              + '<figcaption class="source">Un versement par an, en mai. Prochain : le 12/05/2027 (détachement le 10/05).</figcaption></figure>')
        + grille(tuile('ok', 'Sur 5 ans', '+62 %', '2,60 € → 4,20 €'), tuile('neutre', f'Rendement au {JOUR}', f"{fr(100*DIV_AN/CN['c'])} %", '4,20 € par an'),
                 tuile('neutre', 'Part du bénéfice versée', f"{fr(100*DIV_AN/BPA12, 0)} %", 'dividende ÷ BPA 2025'), tuile('ok', 'Hausses d\'affilée', '16', 'jusqu\'en 2026'), mn=240),
        R, 'etoiles', "Seize hausses d'affilée, et plus de la moitié du bénéfice reversée aux actionnaires. Action française : éligible au PEA.",
        "Source : Schneider Electric, communiqués et BALO ; 2,60 € (versé en 2021) recoupé sur DivvyDiary."))
    riv = [('Schneider Electric', 'su.png', 11.46, '+17 %', '19,3 %*'), ('ABB', 'abb.png', e(9.701), '+14 %', '20,8 %'), ('Eaton', 'etn.png', e(8.947), '+19 %', '25,3 %')]
    rows = ''.join(f'<tr><td><img src="{R}assets/img/{lg}" alt="{n}" style="height:24px;width:auto;max-width:130px"></td>'
                   f'<td><div style="display:flex;align-items:center;gap:10px"><span style="display:block;height:14px;border-radius:7px;background:{GOLD};width:{ca/12*70:.0f}%"></span><b>{fr(ca)} Md€</b></div></td>'
                   f'<td style="font-weight:700;color:{GREEN}">{g}</td><td style="font-weight:800;font-size:20px">{mo}</td></tr>' for n, lg, ca, g, mo in riv)
    _illus = lambda coin: (lambda *a, **k: section(*a, coin=coin, **k))   # section avec Mister Coin illustré à droite du titre
    S.append(_illus('site_balance')(7, 'FACE À SES', 'RIVAUX', "Trimestre juillet-septembre 2026 pour les trois",
        carte(f'<div class="tableau"><table><thead><tr><th scope="col">Entreprise</th><th scope="col">Chiffre d\'affaires du trimestre</th><th scope="col">Croissance hors change</th><th scope="col">Marge</th></tr></thead><tbody>{rows}</tbody></table></div>'),
        R, 'reflechit', "Schneider est le plus gros des trois par les ventes. Eaton grandit un peu plus vite et affiche la marge la plus haute, mais chacun calcule sa marge à sa façon.",
        "Croissance organique (Schneider, Eaton) ou comparable (ABB), sur un an. Marges : * EBITA ajusté du 1er semestre 2026 (Schneider ne publie pas de marge au 3e trimestre) ; EBITA opérationnel (ABB) ; "
        "marge des activités hors frais centraux (Eaton). ABB et Eaton convertis à 1 € = 1,0935 $ (BCE, 25/11/2026)."))
    surv = ''.join(f'<li style="display:flex;flex-direction:column;padding:14px 0;border-top:1px solid {LINE}"><b style="font-size:18px">{a}</b><span class="gris">{b}</span></li>'
                   for a, b in [("Le rachat de PTC", "Les autorisations, puis la finalisation attendue d'ici le 3e trimestre 2027."),
                                ("Les résultats du 18 février", "Les comptes annuels 2026, face à l'objectif de +12 à +14 % de ventes organiques."),
                                ("Les centres de données", "Leur demande a progressé « à trois chiffres » au 3e trimestre : le moteur de la croissance actuelle.")])
    S.append(_illus('site_longue_vue')(8, "CE QU'IL FAUT", 'SURVEILLER', "Trois rendez-vous", R=R, corps=f'<ul class="carte" style="list-style:none;margin:0;padding:4px 24px">{surv}</ul>'))
    src = ''.join(f'<li><a href="{u}">{n}</a></li>' for n, u in SOURCES)
    S.append(f'<section class="section" id="sources"><h3 style="font-size:22px">Sources et méthode</h3><ul style="margin:0;padding-left:20px;line-height:1.9;font-size:15px">{src}</ul>'
             '<p class="gris petit" style="margin:0">Ratios calculés par Actions Bénéfices : marge nette = résultat net part du groupe ÷ chiffre d\'affaires ; PER = cours ÷ bénéfice par action 2025 (part du groupe, non dilué) ; '
             'part du bénéfice versée = dividende ÷ bénéfice par action. Comptes en euros ; ABB, Eaton et le prix de PTC convertis au taux de référence BCE du 25/11/2026. '
             'Cours, capitalisation, PER et rendement recalculés chaque soir avec le dernier cours de clôture. Le détail de chaque chiffre est dans le fichier de sources de l\'épisode.</p></section>')
    toc = ''.join(f'<a href="#s{i}">{x}</a>' for i, x in enumerate(['Identité', 'Croissance', "D'où vient l'argent", 'Rentabilité', 'Solidité', 'Dividende', 'Rivaux', 'À surveiller'], 1)) + '<a href="#historique">Historique</a>'
    chute = 100*(CN['c']/AVANT_PTC-1)
    tete = (f'<p class="fil"><a href="{R}fiches/">Fiches entreprises</a> › {m["nom"]}</p><div class="hero"><div>'
            f'<img src="{R}assets/img/su.png" alt="Schneider Electric" style="height:40px;width:auto;align-self:flex-start">'
            f'<h1>QUE VAUT <em>SCHNEIDER ELECTRIC ?</em></h1><p class="chapo">{m["accroche"]}</p>'
            f'<div class="pastilles"><span title="{m['comptes_officiel']}"><b>Comptes du {m["comptes"]}</b>, publiés le {jj_mm_aaaa(m["comptes_publies"])}</span><span><b>Cours et PER au {jj_mm_aaaa(CN["date"])}</b>, {'recalculés chaque soir' if not FIGE else 'figés (version archivée)'}</span>'
            f'<span>Prochaine mise à jour des comptes : après les résultats du {m["prochains_txt"]}</span></div></div>'
            f'<img src="{R}assets/img/loupe.webp" alt="Mister Coin examine les comptes à la loupe"></div>'
            + grille(tuile('ok', "Chiffre d'affaires 2025", '40,2 Md€', '+5 % sur un an'), tuile('ok', '3e trimestre 2026', '+17 %', 'organique, record'),
                     tuile('ko' if chute < 0 else 'ok', "Depuis l'annonce de PTC", ('+' if chute >= 0 else '−') + fr(abs(chute), 0) + ' %', f"cours au {JOUR} contre 303 € le 02/10"),
                     tuile('neutre', f'PER au {JOUR}', fr_per(PER_N), 'sur le BPA 2025'))
            + f'<nav class="sommaire" aria-label="Sommaire de la fiche">{toc}</nav>')
    return tete + ''.join(S)
