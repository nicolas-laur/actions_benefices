"""Fiche entreprise n°1 : Nvidia. Chiffres et sources : episodes/2026-11-22_fiche_nvidia/sources.md (clôture du 20/11/2026, BCE 1,0990)."""
from composants import *

META = dict(slug='nvidia', titre='Que vaut Nvidia ?', nom='Nvidia', date='2026-11-21', date_txt='21/11/2026', chiffres_au='20/11/2026',
            description="Fiche entreprise Nvidia : croissance, rentabilité, solidité, dividende et PER face à AMD et Broadcom, chiffres au 20/11/2026, sources en lien.",
            accroche="−14 % vendredi, plus bas depuis mai 2025, premiers résultats sans Jensen Huang et une enquête de la SEC : on remet les chiffres à plat.",
            detient=True, pose='loupe', logo='nvda.png')
EUR = 1.0990
def e(x): return x/EUR

Q = [(2.05, 3.61), (2.37, 4.14), (2.94, 4.16), (3.26, 4.38), (3.75, 4.54), (3.81, 2.89), (3.83, 2.10), (3.62, 2.43), (4.28, 2.91), (10.32, 3.19), (14.51, 3.61),
     (18.40, 3.70), (22.56, 3.48), (26.27, 3.77), (30.77, 4.31), (35.58, 3.75), (39.11, 4.95), (41.10, 5.64), (51.2, 5.8), (62.3, 5.8), (75.2, 6.4), (89.0, 7.2), (107.6, 8.2)]

def _flux():
    v = dict(hy=e(60.1), ac=e(47.5), dc=e(107.6), ed=e(8.2), ca=e(115.844), mb=e(86.676), cv=e(29.168), re=e(77.52), ch=e(9.156), au=e(1.497), rn=e(65.287), im=e(13.73))
    N = {'hy': (130, 120, TEAL), 'ac': (130, 330, TEAL), 'dc': (300, 170, TEAL), 'ed': (300, 500, LIME), 'ca': (470, 200, INK), 'mb': (640, 150, GREEN), 'cv': (640, 440, RED),
         're': (800, 110, GREEN), 'ch': (800, 360, RED), 'au': (950, 70, GOLD), 'rn': (950, 95, GREEN), 'im': (950, 330, RED)}
    L = [('hy', 'dc', v['hy'], TEAL_R), ('ac', 'dc', v['ac'], TEAL_R), ('dc', 'ca', v['dc'], TEAL_R), ('ed', 'ca', v['ed'], LIME_R), ('ca', 'mb', v['mb'], GREEN_R),
         ('ca', 'cv', v['cv'], RED_R), ('mb', 're', v['re'], GREEN_R), ('mb', 'ch', v['ch'], RED_R), ('au', 'rn', v['au'], GOLD_R), ('re', 'rn', v['rn']-v['au'], GREEN_R), ('re', 'im', v['im'], RED_R)]
    lab = {'hy': ('l', [('Géants du cloud', 'n'), (fr(v['hy']), 'v'), ('+71 % sur 1 an', 's')]),
           'ac': ('l', [('Clouds IA,', 'n'), ('entreprises', 'n'), (fr(v['ac']), 'v'), ('+195 % sur 1 an', 's')]),
           'dc': ('t', [('Centres de données', 'n'), (fr(v['dc']), 'v'), ('+110 % sur 1 an', 's')]),
           'ed': ('b', [('Jeux, PC, auto', 'n'), (fr(v['ed']), 'v'), ('+42 % sur 1 an', 's')]),
           'ca': ('t', [("Chiffre d'affaires", 'n'), (fr(v['ca']), 'v'), ('+103 % sur 1 an', 's')]),
           'mb': ('t', [('Marge brute', 'n'), (fr(v['mb']), 'v'), ('75 % des ventes', 's')]),
           'cv': ('b', [('Coût des ventes', 'n'), ('('+fr(v['cv'])+')', 'v')]),
           're': ('t', [("Résultat d'exploitation", 'n'), (fr(v['re']), 'v'), ('67 % des ventes', 's')]),
           'ch': ('b', [('Recherche et frais', 'n'), ('('+fr(v['ch'])+')', 'v'), ('8 % des ventes', 's')]),
           'au': ('r', [('Autres +'+fr(v['au']), 'n')]),
           'rn': ('r', [('Résultat net', 'n'), (fr(v['rn']), 'v'), ('56 % des ventes', 's')]),
           'im': ('r', [('Impôts', 'n'), ('('+fr(v['im'])+')', 'v')])}
    return flux(N, L, v, 2.75, lab, "Compte de résultat de Nvidia au 3e trimestre en rubans : du chiffre d'affaires au résultat net")

SOURCES = [("Nvidia, résultats du 3e trimestre de l'exercice 2027 (17/11/2026)", "https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Third-Quarter-Fiscal-2027/default.aspx"),
           ("Nvidia, commentaire financier du 3e trimestre (SEC)", "https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000088/q3fy27cfocommentary.htm"),
           ("Nvidia, résultats de l'exercice 2026", "https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026"),
           ("Nvidia, rachat d'actions relevé de 150 Md$ (28/09/2026)", "https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-a-150-Billion-Share-Repurchase-Authorization-Increase/"),
           ("Motley Fool, la séance du 20/11/2026", "https://www.fool.com/investing/2026/11/20/here-is-why-nvidia-stock-crashed-on-friday/"),
           ("Yahoo Finance, enquête de la SEC (Reuters, WSJ)", "https://finance.yahoo.com/markets/article/nvidia-stock-extends-25-trillion-rout-as-sec-probe-reportedly-investigates-its-accounting-194945274.html"),
           ("AMD, résultats du 3e trimestre 2026", "https://mfn.se/all/a/advanced-micro-devices/amd-reports-third-quarter-2026-financial-results-f24509e4"),
           ("Broadcom, résultats du 3e trimestre de l'exercice 2026 (SEC)", "https://www.sec.gov/Archives/edgar/data/0001730168/000173016826000076/avgo-08022026x8kxex99.htm")]

def corps(R):
    m = META
    S = []
    S.append(section(1, 'CARTE', "D'IDENTITÉ", "Exercice clos fin janvier 2026",
        carte(f'<div style="display:flex;gap:22px;align-items:center;flex-wrap:wrap"><img src="{R}assets/img/nvda.png" alt="Logo Nvidia" style="height:48px;width:auto">'
              '<p style="margin:0;flex:1 1 360px;font-size:18px">Conçoit les puces qui font tourner l\'intelligence artificielle, les fait fabriquer par d\'autres (surtout TSMC à Taïwan) et les vend aux géants du cloud et aux laboratoires d\'IA.</p></div>')
        + '<div class="grille" style="--min:320px">'
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Par activité</div>' + pbar('Centres de données', 89.7, TEAL) + pbar('Jeux vidéo', 7.4, LIME)
                + pbar('Automobile, robotique', 1.1, LIME) + pbar('Autres (visualisation pro…)', 1.8, '#8A8A8A') + '</div>')
        + carte('<div class="pile" style="gap:14px"><div class="surtitre">Par région du client</div>' + pbar('États-Unis', 69.3, NAVY) + pbar('Taïwan', 19.6, '#4F79A8')
                + pbar('Chine', 9.1, '#6F8FB5') + pbar('Autres', 2.0, '#8A8A8A') + '</div>') + '</div>'
        + grille(tuile('neutre', 'En bourse depuis', '1999', 'Nasdaq'), tuile('neutre', 'Capitalisation', '≈ 2 750 Md€', '≈ 3 025 Md$'),
                 tuile('ko', 'Cours au 20/11', '114,22 €', '125,53 $, −14 % sur la séance')),
        R, 'loupe', "9 euros de ventes sur 10 viennent des centres de données. Les comptes publiés par Nvidia sont examinés par la SEC (enquête en cours, aucune conclusion à ce jour).",
        "Source : Nvidia, rapport annuel 10-K de l'exercice 2026 ; cours Nasdaq ; 1 € = 1,0990 $ (BCE, 20/11/2026)."))
    S.append(section(2, 'LA', 'CROISSANCE', "Chiffre d'affaires par trimestre, en milliards d'euros",
        carte('<figure class="fin">' + barres_empilees(Q, "Chiffre d'affaires trimestriel de Nvidia en milliards d'euros, de l'exercice 2022 au 3e trimestre 2027", conv=EUR)
              + f'<figcaption class="petit" style="display:flex;gap:22px;flex-wrap:wrap;margin-top:8px"><span><i style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{TEAL};margin-right:6px"></i>Centres de données</span>'
              f'<span><i style="display:inline-block;width:12px;height:12px;border-radius:3px;background:{LIME};margin-right:6px"></i>Jeux, PC, auto et autres</span></figcaption></figure>')
        + grille(tuile('ok', 'Sur 4 ans', '+68 %/an', '2022 → 2026'), tuile('ok', 'Dernier trimestre', '+103 %', 'sur un an'), tuile('ok', '12 derniers mois', '329 Md€', '361,8 Md$')),
        R, 'court', "En 4 ans, le chiffre d'affaires a été multiplié par 8. Le déclic : la course aux centres de données pour l'IA, lancée fin 2022 avec ChatGPT.",
        "Source : Nvidia, communiqués trimestriels. Exercices clos fin janvier. 1 € = 1,0990 $."))
    S.append(section(3, "D'OÙ VIENT", "L'ARGENT", "3e trimestre clos le 25/10/2026, en milliards d'euros", carte('<figure>' + _flux() + '</figure>'), R, None, None,
        "Source : Nvidia, résultats du 17/11/2026 (CA 115,8 Md$). Mise en page inspirée de App Economy Insights (How They Make Money)."))
    S.append(section(4, 'LA', 'RENTABILITÉ', "Résultat net (Md€) et marge nette, par exercice",
        carte('<figure>' + barres([e(x) for x in (9.752, 4.368, 29.760, 72.880, 120.067)], ['2022', '2023', '2024', '2025', '2026'], fr, GREEN,
                                  "Résultat net de Nvidia par exercice en milliards d'euros et marge nette", [36.2, 16.2, 48.8, 55.8, 55.6], H=420, ident='hr') + '</figure>')
        + grille(tuile('ok', 'BPA 2026', '4,46 €', '×13 depuis 2022'), tuile('ok', 'BPA, 12 derniers mois', '8,47 €', '9,31 $'), mn=300),
        R, None, "Sur 100 € de ventes, Nvidia garde 56 € de bénéfice net. Le creux de 2023 : ventes de cartes pour joueurs en chute et 1,35 Md$ de charge après l'abandon du rachat d'Arm.",
        "Source : Nvidia, 10-K. BPA (bénéfice par action) ajusté des divisions d'actions (×4 en 2021, ×10 en 2024)."))
    S.append(section(5, 'LA', 'SOLIDITÉ', "Bilan fin octobre 2026, flux sur 9 mois",
        grille(tuile('ok', 'Trésorerie nette', '+19,2 Md€', 'plus de cash que de dette'), tuile('neutre', 'Dette', '29,5 Md€', '32,4 Md$'),
               tuile('ok', 'Flux de trésorerie libre', '≈ 103 Md€', 'en 9 mois'), tuile('ok', "Rachats d'actions", '55,7 Md€', 'en 9 mois'), mn=240)
        + carte('<div class="surtitre">Programme de rachat</div><p style="margin:6px 0 0;font-size:18px">+150 Md$ annoncés le 28/09, le plus gros relèvement de l\'histoire de Nvidia. <b>Reste 207 Md€</b> à racheter (227,3 Md$).</p>'),
        R, None, "Nvidia génère plus de 11 Md€ par mois une fois ses investissements payés. Elle en rend l'essentiel, surtout en rachetant ses propres actions.",
        "Source : Nvidia, communiqué et commentaire financier du 3e trimestre (17/11/2026)."))
    S.append(section(6, 'LE', 'DIVIDENDE', "Par action et par exercice, en euros (actions d'aujourd'hui)",
        carte('<figure>' + barres([e(x) for x in (0.0143, 0.0153, 0.016, 0.016, 0.016, 0.016, 0.016, 0.034, 0.04, 0.76)], [str(y) for y in range(2018, 2027)] + ['2027*'],
                                  lambda x: fr(x, 2), GOLD, "Dividende de Nvidia par action et par exercice, en euros", H=320, hach=9, ident='hd')
              + '<figcaption class="source">* exercice en cours, dont 0,25 $ versé le 23/12. Ajusté des divisions d\'actions (×4 en 2021, ×10 en 2024).</figcaption></figure>')
        + grille(tuile('ok', 'Dividende ×25 en mai', '0,25 $', 'par trimestre'), tuile('neutre', 'Rendement au 20/11', '0,8 %', '1 $ par an'),
                 tuile('neutre', 'Part du bénéfice versée', '11 %'), tuile('ok', 'Prochain versement', '23/12', 'détachement vers le 2/12'), mn=240),
        R, 'joie', "Pendant 10 ans, le dividende était symbolique. Mais l'essentiel part ailleurs : en 9 mois, 5 fois plus de rachats d'actions que de dividendes."))
    riv = [('Nvidia', 'nvda.png', 62.5, '+103 %', '13,5', GREEN), ('Broadcom', 'avgo.png', 42.9, '+86 %', '38,9', INK), ('AMD', 'amd.png', 16.8, '+45 %', '92', RED)]
    rows = ''.join(f'<tr><td><img src="{R}assets/img/{lg}" alt="{n}" style="height:24px;width:auto;max-width:130px"></td>'
                   f'<td><div style="display:flex;align-items:center;gap:10px"><span style="display:block;height:14px;border-radius:7px;background:{GREEN};width:{mg/62.5*100:.0f}%;max-width:70%"></span><b>{fr(mg)} %</b></div></td>'
                   f'<td style="font-weight:700;color:{GREEN}">{g}</td><td style="font-weight:800;font-size:20px;color:{pc}">{p}</td></tr>' for n, lg, mg, g, p, pc in riv)
    S.append(section(7, 'FACE À SES', 'RIVAUX', "12 derniers mois publiés, chiffres comptables",
        carte(f'<div class="tableau"><table><thead><tr><th scope="col">Entreprise</th><th scope="col">Marge nette</th><th scope="col">Croissance*</th><th scope="col">PER</th></tr></thead><tbody>{rows}</tbody></table></div>'),
        R, 'rocking', "Nvidia est la plus rentable des trois et, après la chute de vendredi, la moins chère par rapport à ses bénéfices. L'autre rival : les puces maison des géants du cloud (TPU de Google, Trainium d'Amazon).",
        "* croissance du chiffre d'affaires du dernier trimestre sur un an. PER = cours du 20/11 ÷ bénéfice par action des 12 derniers mois. Trimestres clos fin octobre (Nvidia), fin septembre (AMD), début août (Broadcom)."))
    surv = ''.join(f'<li style="display:flex;flex-direction:column;padding:14px 0;border-top:1px solid {LINE}"><b style="font-size:18px">{a}</b><span class="gris">{b}</span></li>'
                   for a, b in [("Le nouveau PDG", "Colette Kress assure l'intérim depuis le 12/11."), ("L'enquête de la SEC", "Elle porte sur les comptes : aucune conclusion à ce jour."),
                                ("Les résultats de fin février", "Nvidia vise 130 Md$ de ventes au 4e trimestre.")])
    S.append(section(8, "CE QU'IL FAUT", 'SURVEILLER', "Trois rendez-vous datés", f'<ul class="carte" style="list-style:none;margin:0;padding:4px 24px">{surv}</ul>'))
    src = ''.join(f'<li><a href="{u}">{n}</a></li>' for n, u in SOURCES)
    S.append(f'<section class="section" id="sources"><h3 style="font-size:22px">Sources et méthode</h3><ul style="margin:0;padding-left:20px;line-height:1.9;font-size:15px">{src}</ul>'
             '<p class="gris petit" style="margin:0">Ratios calculés par Actions_Bénéfices : marge nette = résultat net ÷ chiffre d\'affaires ; PER = cours ÷ bénéfice par action des 12 derniers mois ; '
             'BPA et dividendes ajustés des divisions d\'actions. Montants convertis au taux de référence BCE du 20/11/2026. Le détail de chaque chiffre est dans le fichier de sources de l\'épisode.</p></section>')
    toc = ''.join(f'<a href="#s{i}">{x}</a>' for i, x in enumerate(['Identité', 'Croissance', "D'où vient l'argent", 'Rentabilité', 'Solidité', 'Dividende', 'Rivaux', 'À surveiller'], 1))
    tete = (f'<p class="fil"><a href="{R}fiches/">Fiches entreprises</a> › {m["nom"]}</p><div class="hero"><div>'
            f'<img src="{R}assets/img/nvda.png" alt="Nvidia" style="height:40px;width:auto;align-self:flex-start">'
            f'<h1>QUE VAUT <em>NVIDIA ?</em></h1><p class="chapo">{m["accroche"]}</p>'
            f'<div class="pastilles"><span><b>Chiffres au {m["chiffres_au"]}</b> · 1 € = 1,0990 $ (BCE)</span><span class="alerte">Je détiens des actions Nvidia</span><span>Mise à jour à chaque trimestre</span></div></div>'
            f'<img src="{R}assets/img/loupe.png" alt="Mister Coin examine les comptes à la loupe"></div>'
            + grille(tuile('ok', "Chiffre d'affaires 12 mois", '329 Md€', '+103 % au dernier trimestre'), tuile('ok', 'Marge nette', '56 %', 'exercice 2026'),
                     tuile('ok', 'PER', '13,5', 'Broadcom 38,9, AMD 92'), tuile('neutre', 'Dividende', '0,8 %', '1 $ par an'))
            + f'<nav class="sommaire" aria-label="Sommaire de la fiche">{toc}</nav>')
    return tete + ''.join(S)
