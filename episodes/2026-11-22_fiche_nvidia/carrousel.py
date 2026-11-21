"""Fiche entreprise n°1 : « Que vaut Nvidia ? » (chiffres arrêtés à la clôture du vendredi 20/11/2026), 9 diapos, thème clair (décision du 21/11).
Format : docs/formats/fiche_entreprise.md ; gabarit lib/carrousel.py (thème clair, flux, barres_empilees, graphique). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

R = 1.0990                                                                  # BCE, 20/11/2026 : 1 € = 1,0990 $
def e(usd): return usd/R
def md(v, d=1): return fmt(v, d)+NB+'Md€'
def rangee(c, y, items, h=90, x0=40, x1=1040, gap=16):
    """rangée de tuiles de même largeur, alignée sur les bords des cartes principales (40 → 1040), à garder au-dessus de y = 1000 (retour du 21/11)"""
    n = len(items); w = (x1-x0-gap*(n-1))/n; assert y+h <= 1000, (y, h)
    for j, it in enumerate(items): tuile(c, x0+j*(w+gap), y, w, *it, h=h)
def src(c, s_, y): text(c, s_, 40, y, 'sb', 19, CL_GREY, 'l')
CX = 950                                                                    # bord droit du contenu sous y = 1000 (icônes des applis)

def pied(cv, c, lect, pose, bul, y_libre, gras=()):
    """bas de diapo : Mister Coin en bas à gauche (hauteur automatique dans la place libre), encadré de lecture à sa droite, bulle au-dessus de lui"""
    k0 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); n = len(wrap(k0, lect, 'sb', 26, CX-300-90))
    h = int(n*26*1.36+44); y = 1488-h; lecture_claire(c, lect, 300, y, CX-300, 26, filet=None)
    ch = int(max(210, min(300, 1492-max(y_libre, y-40)-70)))
    bb = coin(cv, pose, 150, 1492, ch)
    if bul: bulle(c, bul, 150, bb[1]-46, (150, bb[1]+10), 27)
def bulle(c, s_, x, y, tip, size=27):
    """bulle bleu marine au-dessus de Mister Coin (fond clair)"""
    w = tw(c, s_, 'xb', size)+50; h = size*2.0; x = max(20+w/2, x)
    c.move_to(x-16, y+h/2-2); c.line_to(tip[0], tip[1]); c.line_to(x+16, y+h/2-2); c.close_path(); col(c, CL_NAVY); c.fill()
    rr(c, x-w/2, y-h/2, w, h, h/2); col(c, CL_NAVY); c.fill(); text(c, s_, x, y, 'xb', size, WHITE, 'c')

# ---------- 1. couverture ----------
def s_cover(cv, c):
    logo_plein(cv, 'NVDA_complet', 540-210, 300, 420)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "NVIDIA ?", 540, 600, 'k', 140, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "−14" + NB + "% vendredi", 540, 780, 'k', 76, CL_RED, 'c')
    text(c, "Plus bas depuis mai 2025", 540, 852, 'xb', 36, CL_INK, 'c')
    text(c, "Premiers résultats sans Jensen Huang, enquête", 540, 916, 'sb', 27, CL_GREY, 'c')
    text(c, "de la SEC : on remet les chiffres à plat.", 540, 954, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('chip', 'Croissance'), ('cash-multiple', 'Rentabilité'), ('bank', 'Solidité'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "Regardons|les comptes.", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
ACT = [("Centres de données", 89.7, CL_TEAL), ("Jeux vidéo", 7.4, CL_LIME), ("Automobile, robotique", 1.1, CL_LIME), ("Autres (visu. pro…)", 1.8, 'BDBDBD')]
REG = [("États-Unis", 69.3, CL_NAVY), ("Taïwan", 19.6, '4F79A8'), ("Chine", 9.1, '8FA9C8'), ("Autres", 2.0, 'BDBDBD')]
def barres_pct(c, rows, x, y, w):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*62; text(c, lab, x, yy, 'xb', 22, CL_INK, 'l'); text(c, fmt(p)+NB+'%', x+w, yy, 'k', 22, colr, 'r')
        rr(c, x, yy+18, w, 12, 6); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+18, max(w*p/100, 10), 12, 6); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Exercice clos fin janvier 2026")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'NVDA', 50, 450, 150)
    for j, l in enumerate(["Conçoit les puces qui font tourner l'IA.", "Les fait fabriquer par d'autres (surtout TSMC).", "Les vend aux géants du cloud et aux labos d'IA."]):
        text(c, l, 230, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "PAR ACTIVITÉ", ['ok'], 80, 608); barres_pct(c, ACT, 80, 652, 420)
    famille(c, "PAR RÉGION DU CLIENT", ['neutre'], 580, 608); barres_pct(c, REG, 580, 652, 420)
    rangee(c, 905, [('neutre', "En bourse depuis", "1999"), ('neutre', "Capitalisation", "≈" + NB + "2" + NB + "750 Md€"), ('ko', "Cours (20/11)", "114,22 €")])
    src(c, "Source : Nvidia, 10-K exercice 2026 ; cours Nasdaq ; 1 € = 1,0990 $ (BCE, 20/11).", 1030)
    pied(cv, c, "9 euros de ventes sur 10 viennent des centres de données. Les comptes publiés par Nvidia sont examinés par la SEC (enquête en cours, aucune conclusion).",
         'loupe', "Voyons voir…", 1060)

# ---------- 3. croissance : CA trimestriel ----------
Q = [(2.05, 3.61), (2.37, 4.14), (2.94, 4.16), (3.26, 4.38), (3.75, 4.54), (3.81, 2.89), (3.83, 2.10), (3.62, 2.43),
     (4.28, 2.91), (10.32, 3.19), (14.51, 3.61), (18.40, 3.70), (22.56, 3.48), (26.27, 3.77), (30.77, 4.31), (35.58, 3.75),
     (39.11, 4.95), (41.10, 5.64), (51.2, 5.8), (62.3, 5.8), (75.2, 6.4), (89.0, 7.2), (107.6, 8.2)]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires par trimestre, en milliards d'euros")
    carte(c, 40, 345, 1000, 545)
    data = [(e(a), e(b)) for a, b in Q]
    barres_empilees(c, data, 66, 790, 420, 31, 11.5, [CL_TEAL, CL_LIME], groupes=(4, lambda j: f"Ex. {2022+j}"),
                    etiq=lambda i: i >= len(Q)-6 or i % 4 == 3)
    picto(cv, 'server', 92, 862, 30, CL_TEAL); text(c, "Centres de données", 116, 862, 'sb', 22, CL_INK, 'l')
    picto(cv, 'gamepad-variant', 400, 862, 30, CL_LIME); text(c, "Jeux, PC, auto et autres", 424, 862, 'sb', 22, CL_INK, 'l')
    rangee(c, 905, [('ok', "Sur 4 ans", "+68" + NB + "%/an"), ('ok', "Dernier trimestre", "+103" + NB + "%"), ('ok', "12 derniers mois", "329 Md€")])
    src(c, "Source : Nvidia, communiqués trimestriels. Exercices clos fin janvier.", 1030)
    pied(cv, c, "En 4 ans, le chiffre d'affaires a été multiplié par 8. Le déclic : la course aux centres de données pour l'IA, lancée fin 2022 avec ChatGPT.",
         'court', "Fois 8 !", 1060)

# ---------- 4. d'où vient l'argent (flux du T3) ----------
def s_flux(cv, c):
    tt = "3e TRIMESTRE"; x_t = 540-(290+24+tw(c, tt, 'k', 58))/2; text(c, tt, x_t+290+24, 236, 'k', 58, CL_NAVY, 'l')
    logo_plein(cv, 'NVDA_complet', x_t, 230, 290)
    text(c, "D'où vient l'argent, où il va", 540, 300, 'xb', 34, CL_INK, 'c')
    text(c, "Clos le 25/10/2026, en milliards d'euros", 540, 346, 'sb', 24, CL_GREY, 'c')
    k = 4.1; X = [176, 336, 490, 646, 802, 900]
    v = dict(hy=e(60.1), ac=e(47.5), dc=e(107.6), ed=e(8.2), ca=e(115.844), mb=e(86.676), cv=e(29.168), re=e(77.52), ch=e(9.156), au=e(1.497), rn=e(65.287), im=e(13.73))
    L = etiquette; f = lambda x: fmt(x); p = lambda x: '('+fmt(x)+')'
    N = {
     'hy': dict(x=X[0], y=600, v=v['hy'], c=CL_TEAL, rib=CL_TEAL_R, side='l', lab=L('Géants|du cloud', f(v['hy']), ['+71 % sur 1 an'], CL_TEAL)),
     'ac': dict(x=X[0], y=890, v=v['ac'], c=CL_TEAL, rib=CL_TEAL_R, side='l', lab=L('Clouds IA,|entreprises', f(v['ac']), ['+195 % sur 1 an'], CL_TEAL)),
     'dc': dict(x=X[1], y=680, v=v['dc'], c=CL_TEAL, rib=CL_TEAL_R, side='t', lab=L('Centres de|données', f(v['dc']), ['+110 % sur 1 an'], CL_TEAL)),
     'ed': dict(x=X[1], y=1190, v=v['ed'], c=CL_LIME, rib=CL_LIME_R, side='b', lab=L('Jeux, PC,|auto', f(v['ed']), ['+42 % sur 1 an'], CL_LIME)),
     'ca': dict(x=X[2], y=740, v=v['ca'], c=CL_INK, rib=CL_TEAL_R, side='t', lab=L("Chiffre|d'affaires", f(v['ca']), ['+103 % sur 1 an'], CL_INK)),
     'mb': dict(x=X[3], y=660, v=v['mb'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L('Marge|brute', f(v['mb']), ['75 % des ventes', '+1 pt sur 1 an'], CL_GREEN)),
     'cv': dict(x=X[3], y=1110, v=v['cv'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Coût des|ventes', p(v['cv']), [], CL_RED)),
     're': dict(x=X[4], y=580, v=v['re'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L("Résultat|d'exploitation", f(v['re']), ['67 % des ventes', '+4 pts sur 1 an'], CL_GREEN)),
     'ch': dict(x=X[4], y=1040, v=v['ch'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Recherche|et frais', p(v['ch']), ['8 % des ventes'], CL_RED)),
     'au': dict(x=X[5], y=510, v=v['au'], c=CL_GOLD, rib=CL_GOLD_R, side='r', lab=[('Autres', 'xb', 21, CL_GOLD), ('+'+f(v['au']), 'k', 22, CL_GOLD)]),
     'rn': dict(x=X[5], y=540, v=v['rn'], c=CL_GREEN, rib=CL_GREEN_R, side='r', lab=L('Résultat|net', f(v['rn']), ['56 % des', 'ventes'], CL_GREEN, 23)),
     'im': dict(x=X[5], y=900, v=v['im'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Impôts', p(v['im']), [], CL_RED, 23)),
    }
    links = [('hy', 'dc', v['hy']), ('ac', 'dc', v['ac']), ('dc', 'ca', v['dc'], CL_TEAL_R), ('ed', 'ca', v['ed'], CL_LIME_R),
             ('ca', 'mb', v['mb']), ('ca', 'cv', v['cv']), ('mb', 're', v['re']), ('mb', 'ch', v['ch']),
             ('au', 'rn', v['au'], CL_GOLD_R), ('re', 'rn', v['rn']-v['au']), ('re', 'im', v['im'])]
    flux(c, N, links, k)
    picto(cv, 'cloud-outline', 112, 618, 54, CL_TEAL); picto(cv, 'domain', 112, 878, 50, CL_TEAL); picto(cv, 'server', 349, 492, 50, CL_TEAL)
    for j, n in enumerate(['gamepad-variant', 'laptop', 'car-side', 'robot-industrial']): picto(cv, n, 349+(j-1.5)*50, 1388, 40, CL_LIME)
    picto(cv, 'factory', 659, 1368, 46, CL_RED); picto(cv, 'flask-outline', 815, 1232, 42, CL_RED)
    picto(cv, 'bank', 1040, 940, 40, CL_RED); picto(cv, 'cash-multiple', 965, 765, 46, CL_GREEN)
    source(c, "Source : Nvidia, résultats du 17/11/2026", 1440, CX, 18); source(c, "(CA 115,8 Md$). 1 € = 1,0990 $ (BCE, 20/11).", 1462, CX, 18)
    text(c, "Mise en page inspirée de App Economy Insights (How They Make Money)", 600, 1488, 'sb', 17, CL_GREY, 'c')
    coin(cv, 'neutre', 105, 1450, 240)

# ---------- 5. rentabilité ----------
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net (Md€) et marge nette, par exercice")
    carte(c, 40, 345, 1000, 545)
    graphique(c, ["2022", "2023", "2024", "2025", "2026"], [e(x) for x in (9.752, 4.368, 29.760, 72.880, 120.067)], 80, 1000, 690, 430,
              courbe=[36.2, 16.2, 48.8, 55.8, 55.6], cbase=860, ctop=790, couleur=CL_GREEN)
    text(c, "Marge nette", 80, 752, 'xb', 21, CL_TEAL, 'l')
    rangee(c, 905, [('ok', "BPA 2026", "4,46 €", "×13 depuis 2022"), ('ok', "BPA, 12 derniers mois", "8,47 €", "9,31 $")])
    src(c, "Source : Nvidia, 10-K. BPA ajusté des divisions d'actions (2021, 2024).", 1030)
    pied(cv, c, "Sur 100 € de ventes, Nvidia garde 56 € de bénéfice net. Le creux de 2023 : ventes de cartes pour joueurs en chute et 1,35 Md$ de charge après l'abandon du rachat d'Arm.",
         'choc', "56 % de marge !", 1060)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Bilan fin octobre 2026, flux sur 9 mois")
    carte(c, 40, 345, 1000, 625)
    famille(c, "BILAN", ['ok', 'neutre'], 80, 385)
    tuile(c, 70, 410, 460, 'ok', "Trésorerie nette", "+19,2 Md€", "plus de cash que de dette", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'neutre', "Dette", "29,5 Md€", "32,4 Md$", fond='F5F3EE')
    famille(c, "ARGENT GÉNÉRÉ ET RENDU", ['ok', 'ok'], 80, 535)
    tuile(c, 70, 560, 460, 'ok', "Flux de trésorerie libre", "≈" + NB + "103 Md€", "en 9 mois", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'ok', "Rachats d'actions", "55,7 Md€", "en 9 mois", fond='F5F3EE')
    famille(c, "PROGRAMME DE RACHAT", ['ok'], 80, 685)
    tuile(c, 70, 710, 940, 'ok', "+150 Md$ annoncés le 28/09, plus gros relèvement de l'histoire", "Reste 207 Md€", "à racheter (227,3 Md$)", fond='F5F3EE')
    for j, l in enumerate(["Trésorerie nette = cash − dettes.", "Flux de trésorerie libre = l'argent qui reste après les investissements.",
                           "Rachat d'actions : chaque action restante pèse un peu plus."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Source : Nvidia, communiqué et commentaire du T3 (17/11/2026).", 1000)
    pied(cv, c, "Nvidia génère plus de 11 Md€ par mois une fois ses investissements payés. Elle en rend l'essentiel, surtout en rachetant ses propres actions.",
         'reflechit', "Une machine à cash.", 1030)

# ---------- 7. dividende ----------
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par exercice, en euros (actions d'aujourd'hui)")
    carte(c, 40, 345, 1000, 430)
    vals = [e(x) for x in (0.0143, 0.0153, 0.016, 0.016, 0.016, 0.016, 0.016, 0.034, 0.04, 0.76)]
    graphique(c, [str(y)[2:] for y in range(2018, 2027)] + ["27*"], vals, 70, 1010, 700, 430, couleur=CL_GOLD,
              fmt_b=lambda v: fmt(v, 2), hachure=(9,))
    text(c, "* exercice en cours, dont 0,25 $ versé le 23/12. Ajusté des divisions (×4 en 2021, ×10 en 2024).", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ok', "Dividende ×25 en mai", "0,25 $", "par trimestre"), ('neutre', "Rendement (20/11)", "0,8" + NB + "%", "1 $ par an")])
    rangee(c, 901, [('neutre', "Part du bénéfice", "11" + NB + "%", "versée"), ('ok', "Prochain versement", "23/12", "détachement vers le 2/12")])
    pied(cv, c, "Pendant 10 ans, le dividende était symbolique. Mais l'essentiel part ailleurs : en 9 mois, 5 fois plus de rachats d'actions que de dividendes.",
         'joie', "Enfin un vrai dividende !", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "12 derniers mois publiés, chiffres comptables")
    carte(c, 40, 345, 1000, 620)
    xs = [230, 540, 850]
    logo_plein(cv, 'NVDA_complet', xs[0]-110, 405, 220); logo_plein(cv, 'AVGO_complet', xs[1]-110, 405, 220); logo_plein(cv, 'AMD_complet', xs[2]-80, 405, 160)
    text(c, "MARGE NETTE", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", ""], [62.5, 42.9, 16.8], 80, 1000, 700, 520, couleur=CL_GREEN, fmt_b=lambda v: fmt(v)+NB+'%', bw=150)
    for lab, vals, cols_, y in [("CROISSANCE DU DERNIER TRIMESTRE", ["+103" + NB + "%", "+86" + NB + "%", "+45" + NB + "%"], [CL_GREEN]*3, 765),
                                ("PER (COURS ÷ BÉNÉFICE PAR ACTION)", ["13,5", "38,9", "92"], [CL_GREEN, CL_INK, CL_RED], 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, v, cc in zip(xs, vals, cols_): text(c, v, x, y+48, 'k', 40, cc, 'c')
    src(c, "Sources : résultats publiés ; cours du 20/11. Trimestres clos fin oct. (Nvidia),", 995)
    src(c, "fin sept. (AMD), début août (Broadcom).", 1019)
    pied(cv, c, "Nvidia est la plus rentable des trois et, après la chute de vendredi, la moins chère par rapport à ses bénéfices. L'autre rival : les puces maison des géants du cloud.",
         'rocking_chair', "PER de 13,5.", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('account-group-outline', "Le nouveau PDG", "Colette Kress assure l'intérim depuis le 12/11."),
                                     ('scale-balance' if False else 'bank', "L'enquête de la SEC", "Elle porte sur les comptes : aucune conclusion à ce jour."),
                                     ('chip', "Les résultats de fin février", "Nvidia vise 130 Md$ de ventes au 4e trimestre.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, tu regardes d'abord", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "la croissance, la marge ou le PER ?", 540, 868, 'k', 46, CL_GOLD, 'c')
    text(c, "Dis-le en commentaire", 540, 935, 'sb', 30, CL_GREY, 'c'); put_emoji(cv, '👇', 540, 985, 44)
    rr(c, 160, 1040, 760, 70, 35); col(c, CL_NAVY); c.fill(); text(c, "ENREGISTRE-LE POUR LES PROCHAINS RÉSULTATS", 540, 1075, 'xb', 24, WHITE, 'c'); put_emoji(cv, '📌', 935, 1072, 38)
    carte(c, 300, 1150, 650, 200, 22); logo(cv, 'PROFIL', 390, 1250, 120)
    text(c, "ABONNE-TOI", 470, 1205, 'k', 40, CL_GOLD, 'l'); text(c, "à Actions_Benefices", 470, 1252, 'xb', 26, CL_INK, 'l')
    text(c, "la bourse sans jargon,", 470, 1290, 'sb', 23, CL_GREY, 'l'); text(c, "chaque semaine", 470, 1320, 'sb', 23, CL_GREY, 'l'); put_emoji(cv, '🔔', 905, 1195, 40)
    coin(cv, 'salut_chapeau', 150, 1440, 260)
    text(c, "Je détiens des actions Nvidia.", 540, 1462, 'xb', 21, CL_INK, 'c')
    mention_pedago(c, 1490, CL_GREY, 1)

SLIDES = [s_cover, s_identite, s_croissance, s_flux, s_rentab, s_solid, s_div, s_rivaux, s_fin]
LOGOS |= {'PROFIL'}
NS = len(SLIDES)
def render(i):
    """deux calques : le dessin cairo (cartes, textes, graphiques) dessous, les images (logos, pictogrammes, Mister Coin, émojis) dessus"""
    im = Image.new('RGBA', (W, H), 0); s, c = surface()
    SLIDES[i](im, c); cv = fond_clair(); cv.alpha_composite(to_img(s)); cv.alpha_composite(im); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
