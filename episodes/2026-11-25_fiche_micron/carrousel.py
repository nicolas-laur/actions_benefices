"""Fiche entreprise n°4 : « Que vaut Micron ? » (cours et taux BCE : paramètres du jour ci-dessous), 9 diapos, thème clair, livrée en 4:5 seulement.
Modèle : episodes/2026-11-23_fiche_alphabet/carrousel.py (mêmes pieds, rangées et bulles). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

# ---------- paramètres du jour (seul bloc à changer pour mettre la fiche à jour ; voir sources.md, section 0) ----------
JOUR = "24/11"                    # date de clôture retenue
R = 1.0963                        # taux de référence BCE du même jour : 1 € = R $
P = 629.79                        # clôture MU ($)
RECORD = 1213.56                  # record de clôture (25/06/2026)
NA = 1131.4                       # actions en circulation (M) : capitalisation Stock Analysis ÷ cours (recoupé : 1,13 Md)
BPA_12M = 74.33                   # BPA dilué de l'exercice 2026, clos le 03/09/2026 = 12 derniers mois ($)
DIV = 0.60                        # dividende annuel au rythme actuel (4 × 0,15 $)
def e(usd): return usd/R
def md(usd, d=1): return fmt(e(usd), d)+NB+'Md€'
CAP = NA*P/1000                   # capitalisation (Md$)
CHUTE = round((P/RECORD-1)*100)   # variation depuis le record (%)
PER = P/BPA_12M
def rangee(c, y, items, h=90, x0=40, x1=1040, gap=16):
    """rangée de tuiles de même largeur, alignée sur les bords des cartes principales (40 → 1040), au-dessus de y = 1000 (retour du 21/11)"""
    n = len(items); w = (x1-x0-gap*(n-1))/n; assert y+h <= 1000, (y, h)
    for j, it in enumerate(items): tuile(c, x0+j*(w+gap), y, w, *it, h=h)
def src(c, s_, y): text(c, s_, 40, y, 'sb', 19, CL_GREY, 'l')
CX = 950                                                                    # bord droit du contenu sous y = 1000 (icônes des applis)

def pied(cv, c, lect, pose, bul, y_libre):
    """bas de diapo : Mister Coin en bas à gauche, encadré de lecture (carte blanche simple) à sa droite, bulle au-dessus de lui"""
    k0 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); n = len(wrap(k0, lect, 'sb', 26, CX-300-90))
    h = int(n*26*1.36+44); y = 1488-h; lecture_claire(c, lect, 300, y, CX-300, 26, filet=None)
    ch = int(max(210, min(300, 1492-max(y_libre, y-40)-70)))
    bb = coin(cv, pose, 150, 1492, ch)
    if bul: bulle(c, bul, 150, bb[1]-46, (150, bb[1]+10), 27)
def bulle(c, s_, x, y, tip, size=27):
    """bulle bleu marine au-dessus de Mister Coin ; '|' = deux lignes"""
    L = s_.split('|'); w = max(tw(c, l, 'xb', size) for l in L)+50; lh = size*1.22; h = size*2.0+lh*(len(L)-1); x = max(20+w/2, x); y = y-lh*(len(L)-1)/2
    c.move_to(x-16, y+h/2-2); c.line_to(tip[0], tip[1]); c.line_to(x+16, y+h/2-2); c.close_path(); col(c, CL_NAVY); c.fill()
    rr(c, x-w/2, y-h/2, w, h, min(h/2, size)); col(c, CL_NAVY); c.fill()
    for j, l in enumerate(L): text(c, l, x, y+(j-(len(L)-1)/2)*lh, 'xb', size, WHITE, 'c')

# ---------- 1. couverture ----------
def s_cover(cv, c):
    logo_plein(cv, 'MU', 540-140, 330, 280)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "MICRON ?", 540, 600, 'k', 128, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "Bénéfice ×10", 540, 772, 'k', 70, CL_GREEN, 'c')
    text(c, "et pourtant "+fmt(CHUTE, 0).replace("-", "−")+NB+"% en bourse", 540, 846, 'k', 46, CL_RED, 'c')
    text(c, "Depuis son record du 25 juin.", 540, 914, 'sb', 27, CL_GREY, 'c')
    text(c, "Que disent vraiment ses comptes ?", 540, 952, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('trending-up', 'Croissance'), ('cash-multiple', 'Rentabilité'), ('bank', 'Solidité'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "On ouvre|les comptes !", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
CLI = [("Centres de données", 33.2, CL_TEAL), ("Cloud", 30.0, CL_TEAL), ("Mobiles et PC", 24.2, CL_NAVY), ("Auto et industrie", 12.6, '4F79A8')]
PROD = [("Mémoire vive (DRAM)", 73.0, CL_TEAL), ("Stockage (NAND)", 26.0, CL_NAVY), ("Autres", 1.0, 'BDBDBD')]
def barres_pct(c, rows, x, y, w, pas=62):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*pas; text(c, lab, x, yy, 'xb', 22, CL_INK, 'l'); text(c, fmt(p, 0 if p == int(p) and p in (73.0, 26.0, 1.0) else 1)+NB+'%', x+w, yy, 'k', 22, colr, 'r')
        rr(c, x, yy+18, w, 12, 6); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+18, max(w*p/100, 10), 12, 6); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Chiffre d'affaires du trimestre clos le 03/09/2026")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'MU', 70, 450, 140)
    for j, l in enumerate(["Fabrique les puces mémoire", "des serveurs d'IA, des téléphones,", "des ordinateurs et des voitures."]):
        text(c, l, 250, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "PAR CLIENT", ['ok'], 80, 608); barres_pct(c, CLI, 80, 652, 420, pas=58)
    famille(c, "PAR PRODUIT", ['ok'], 580, 608); barres_pct(c, PROD, 580, 652, 420, pas=74)
    rangee(c, 905, [('neutre', "En bourse depuis", "1984"), ('neutre', "Capitalisation", "≈"+NB+fmt(round(e(CAP), -1), 0)+NB+"Md€"), ('ko', "Cours ("+JOUR+")", fmt(e(P), 2)+NB+"€")])
    src(c, "Source : Micron, communiqué et commentaires du 30/09/2026 ; cours MU ; 1 € = "+fmt(R, 4)+" $ (BCE, "+JOUR+").", 1030)
    pied(cv, c, "Plus de 6 euros sur 10 viennent des centres de données et du cloud, dopés par l'IA. "
         "La mémoire vive (DRAM) pèse près des trois quarts des ventes, le stockage (NAND) un quart.", 'loupe', "Que de la mémoire !", 1060)

# ---------- 3. croissance : CA annuel ----------
CA = [30.758, 15.540, 25.111, 37.378, 133.188]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires par exercice (clos fin août), en Md€")
    carte(c, 40, 345, 1000, 545)
    base = 770
    graphique(c, [str(2022+i) for i in range(5)], [e(x) for x in CA], 80, 1000, base, 470, couleur=CL_LIME, bw=120)
    gr = [None]+[t/p-1 for p, t in zip(CA, CA[1:])]; step = 920/5
    for i, gg in enumerate(gr):
        cx = 80+step*(i+.5)
        text(c, '–' if gg is None else ('+' if gg > 0 else '−')+fmt(abs(gg)*100, 0)+NB+'%', cx, base+62, 'xb', 21, CL_GREY if gg is None else (CL_GREEN if gg > 0 else CL_RED), 'c')
    text(c, "en petit : variation sur un an", 80, 868, 'sb', 18, CL_GREY, 'l')
    rangee(c, 905, [('ok', "Sur 4 ans", "+44" + NB + "%/an"), ('ok', "Dernier trimestre", "+379" + NB + "%"), ('ok', "Exercice 2026", "×3,6", "sur un an")])
    src(c, "Source : Micron, 10-K et communiqués. Exercice 2026 = septembre 2025 à début septembre 2026.", 1030)
    pied(cv, c, "Un métier en montagnes russes : ventes divisées par deux en 2023, puis multipliées par 3,6 en 2026 "
         "avec la ruée sur la mémoire pour l'IA. Ce sont les prix de la mémoire qui font la loi.", 'court', "×3,6 en un an !", 1060)

# ---------- 4. d'où vient l'argent (flux du trimestre) ----------
def s_flux(cv, c):
    tt = "4e TRIMESTRE"; lw = 190; x_t = 540-(lw+24+tw(c, tt, 'k', 58))/2; text(c, tt, x_t+lw+24, 236, 'k', 58, CL_NAVY, 'l')
    logo_plein(cv, 'MU', x_t, 240, lw)
    text(c, "D'où vient l'argent, où il va", 540, 300, 'xb', 34, CL_INK, 'c')
    text(c, "Juin à début septembre 2026 (exercice 2026), en Md€", 540, 346, 'sb', 24, CL_GREY, 'c')
    k = 9.3; X = [176, 336, 490, 646, 802, 900]
    v = dict(dc=e(18.002), cl=e(16.283), mo=e(13.114), au=e(6.824), ca=e(54.229), mb=e(47.047), cr=e(7.182),
             ex=e(43.751), ch=e(3.296), rn=e(37.701), im=e(43.751-37.701))
    L = etiquette; f = lambda x: fmt(x); p = lambda x: '('+f(x)+')'
    def lg(nom, val, colr, sz=21): return [(nom, 'xb', sz, colr), (val, 'k', sz+2, colr)]
    N = {
     'dc': dict(x=X[0], y=430, v=v['dc'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Centres de|données', f(v['dc']), [], CL_LIME)),
     'cl': dict(x=X[0], y=630, v=v['cl'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Cloud', f(v['cl']), [], CL_LIME)),
     'mo': dict(x=X[0], y=820, v=v['mo'], c=CL_TEAL, rib=CL_TEAL_R, side='l', lab=L('Mobiles|et PC', f(v['mo']), [], CL_TEAL)),
     'au': dict(x=X[0], y=980, v=v['au'], c=CL_TEAL, rib=CL_TEAL_R, side='l', lab=L('Auto et|industrie', f(v['au']), [], CL_TEAL)),
     'ca': dict(x=X[2], y=620, v=v['ca'], c=CL_INK, rib=CL_LIME_R, side='t', lab=L("Chiffre|d'affaires", f(v['ca']), ['+379 % sur 1 an'], CL_INK)),
     'mb': dict(x=X[3], y=600, v=v['mb'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L('Marge|brute', f(v['mb']), ['87 % des ventes'], CL_GREEN)),
     'cr': dict(x=X[3], y=1080, v=v['cr'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Coût des|ventes', p(v['cr']), [], CL_RED)),
     'ex': dict(x=X[4], y=600, v=v['ex'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L("Résultat|d'exploitation", f(v['ex']), ['81 % des ventes'], CL_GREEN)),
     'ch': dict(x=X[4], y=1060, v=v['ch'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Charges', p(v['ch']), ['dont '+fmt(e(1.913))+' de', 'recherche'], CL_RED)),
     'rn': dict(x=X[5], y=580, v=v['rn'], c=CL_GREEN, rib=CL_GREEN_R, side='r', lab=L('Résultat|net', f(v['rn']), ['70 % des', 'ventes'], CL_GREEN, 23)),
     'im': dict(x=X[5], y=960, v=v['im'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Impôts', p(v['im']), ['nets des', 'intérêts', 'reçus'], CL_RED, 21)),
    }
    links = [('dc', 'ca', v['dc']), ('cl', 'ca', v['cl']), ('mo', 'ca', v['mo'], CL_TEAL_R), ('au', 'ca', v['au'], CL_TEAL_R),
             ('ca', 'mb', v['mb']), ('ca', 'cr', v['cr']), ('mb', 'ex', v['ex']), ('mb', 'ch', v['ch']),
             ('ex', 'rn', v['rn']), ('ex', 'im', v['im'])]
    flux(c, N, links, k)
    picto(cv, 'server', 60, 430+v['dc']*k/2-70, 40, CL_LIME); picto(cv, 'cellphone', 60, 820+v['mo']*k/2-70, 40, CL_TEAL)
    picto(cv, 'flask-outline', 815, 1060+v['ch']*k+150, 40, CL_RED)
    picto(cv, 'cash-multiple', 1030, 548, 36, CL_GREEN)
    source(c, "Source : Micron, résultats du 30/09/2026", 1440, CX, 18); source(c, "(CA 54,2 Md$). 1 € = "+fmt(R, 4)+" $ (BCE, "+JOUR+").", 1462, CX, 18)
    text(c, "Mise en page inspirée de App Economy Insights (How They Make Money)", 600, 1488, 'sb', 17, CL_GREY, 'c')
    coin(cv, 'site_calculatrice', 115, 1450, 240)

# ---------- 5. rentabilité ----------
RN = [8.687, -5.833, 0.778, 8.539, 84.969]
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net (Md€) et marge nette, par exercice")
    carte(c, 40, 345, 1000, 545)
    graphique(c, [""]*5, [e(x) for x in RN], 80, 1000, 690, 430, courbe=[x/y*100 for x, y in zip(RN, CA)], cbase=862, ctop=800,
              couleur=CL_GREEN, fmt_b=lambda v: fmt(v).replace('-', '−'), fmt_c=lambda v: fmt(v, 0).replace('-', '−')+NB+'%')
    for i in range(5): text(c, str(2022+i), 80+184*(i+.5), 748, 'sb', 22, CL_GREY, 'c')     # années sous la barre négative (sinon chevauchement)
    text(c, "Marge nette", 80, 878, 'xb', 21, CL_TEAL, 'l')
    rangee(c, 905, [('ok', "BPA 2026", fmt(e(74.33), 2)+NB+"€", "(74,33 $)"), ('ok', "Marge nette 2026", "64" + NB + "%", ""),
                    ('neutre', "PER ("+JOUR+")", fmt(PER, 1), "")])
    src(c, "Source : Micron, 10-K et communiqués. BPA dilué. PER = cours ÷ bénéfice par action de l'exercice 2026.", 1030)
    pied(cv, c, "En 2023, les prix de la mémoire se sont effondrés : stocks dépréciés et 5,8 Md$ de perte. En 2026, Micron garde 64 € "
         "pour 100 € de ventes. Son PER de 8,5 est calculé sur cet exercice record.", 'sueur', "De −5,8 à|+85 Md$ !", 1060)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Bilan au 03/09/2026, flux de l'exercice 2026")
    carte(c, 40, 345, 1000, 625)
    famille(c, "BILAN", ['ok', 'ok'], 80, 385)
    tuile(c, 70, 410, 460, 'ok', "Cash et placements", md(73.480), "", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'ok', "Dette", md(5.179), "−64 % en un an", fond='F5F3EE')
    famille(c, "ARGENT GÉNÉRÉ", ['ok', 'neutre'], 80, 535)
    tuile(c, 70, 560, 460, 'ok', "Flux de trésorerie libre", md(62.308), "contre 3,4 Md€ en 2025", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'neutre', "Investissements", md(27.367), "en hausse en 2027", fond='F5F3EE')
    famille(c, "AU TOTAL", ['ok'], 80, 685)
    tuile(c, 70, 710, 940, 'ok', "Trésorerie nette : plus de cash que de dettes", "+"+md(68.301), "(68,3 Md$)", fond='F5F3EE')
    for j, l in enumerate(["Trésorerie nette = cash − dettes.", "Flux de trésorerie libre = l'argent qui reste après les investissements.",
                           "Investissements = usines et machines de fabrication des puces."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Source : Micron, communiqué et commentaires du 30/09/2026. Flux libre « ajusté » publié par Micron.", 1000)
    pied(cv, c, "Il y a trois ans, Micron perdait de l'argent. Aujourd'hui, elle a 62 Md€ de plus que ses dettes et finance seule "
         "des investissements record dans ses usines.", 'site_tirelire', "Une montagne|de cash !", 1030)

# ---------- 7. dividende ----------
DV = [0.10, 0.43, 0.46, 0.46, 0.46, 0.565]
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par année de versement, en euros")
    carte(c, 40, 345, 1000, 430)
    graphique(c, [str(2021+i) for i in range(6)], [e(x) for x in DV], 90, 990, 700, 470, couleur=CL_GOLD,
              fmt_b=lambda v: fmt(v, 2), bw=100)
    text(c, "Dividende lancé en octobre 2021 (un seul versement cette année-là).", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ok', "Hausse en 2026", "+30" + NB + "%", "0,115 → 0,15 $"), ('neutre', "Rendement ("+JOUR+")", fmt(DIV/P*100, 1)+NB+"%", "0,60 $ par an")])
    rangee(c, 901, [('neutre', "Distribution", fmt(DIV/BPA_12M*100, 1)+NB+"%", "du bénéfice"), ('neutre', "Rachats 2026", md(0.650), "(650 M$)")])
    pied(cv, c, "Le dividende reste symbolique. Le rendez-vous, c'est le 9 décembre : la fin d'une limite liée aux aides publiques américaines. "
         "Micron dit vouloir rendre à terme tout son cash en trop, surtout en rachetant ses actions.", 'haussement', "0,1 %…|c'est tout ?", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "Trimestre clos le 03/09 (Micron) ou le 30/09/2026")
    carte(c, 40, 345, 1000, 620)
    xs = [207, 540, 873]
    for x, (kk, w) in zip(xs, [('MU', 170), ('SSNLF', 210), ('SKH', 150)]): logo_plein(cv, kk, x-w/2, 408, w)
    text(c, "PART DU MARCHÉ DE LA MÉMOIRE VIVE (DRAM)", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", ""], [21, 38, 29], 40, 1040, 700, 530, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 0)+NB+'%', bw=150)
    for lab, vals, cols_, y in [("CROISSANCE SUR UN AN", ["+379" + NB + "%", "+344" + NB + "%*", "+328" + NB + "%"], [CL_GREEN]*3, 765),
                                ("MARGE D'EXPLOITATION", ["81" + NB + "%", "72" + NB + "%*", "80" + NB + "%"], [CL_INK]*3, 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, vv, cc in zip(xs, vals, cols_): text(c, vv, x, y+48, 'k', 40, cc, 'c')
    src(c, "Sources : Counterpoint Research (part de marché, 3e trimestre 2026) ; résultats publiés.", 995)
    src(c, "* Samsung : division semi-conducteurs (mémoire, mais aussi fonderie et processeurs).", 1019)
    pied(cv, c, "Trois géants se partagent 88 % de la mémoire vive, avec des marges de 70 à 80 %. Micron, numéro 3, a perdu "
         "5 points de part de marché en un an ; le chinois CXMT monte (9 %).", 'reflechit', "Le n°3|du trio", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('cash-multiple', "Le 9 décembre", "Micron prévoit d'accélérer ses rachats d'actions."),
                                     ('calendar-month-outline', "Les résultats de mi-décembre", "Prévision : 61,5 Md$ de ventes au trimestre (± 1,5)."),
                                     ('memory', "Les prix de la mémoire", "Tendus en 2027 selon Micron, excès d'offre selon BNP.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, tu savais que la mémoire", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "marchait en montagnes russes ?", 540, 868, 'k', 46, CL_GOLD, 'c')
    text(c, "Dis-le en commentaire", 540, 935, 'sb', 30, CL_GREY, 'c'); put_emoji(cv, '👇', 540, 985, 44)
    rr(c, 160, 1040, 760, 70, 35); col(c, CL_NAVY); c.fill(); text(c, "ENREGISTRE-LE POUR LES PROCHAINS RÉSULTATS", 540, 1075, 'xb', 24, WHITE, 'c'); put_emoji(cv, '📌', 935, 1072, 38)
    carte(c, 300, 1150, 650, 200, 22); logo(cv, 'PROFIL', 390, 1250, 120)
    text(c, "ABONNE-TOI", 470, 1205, 'k', 40, CL_GOLD, 'l'); text(c, "à Actions_Benefices", 470, 1252, 'xb', 26, CL_INK, 'l')
    text(c, "la bourse sans jargon,", 470, 1290, 'sb', 23, CL_GREY, 'l'); text(c, "chaque semaine", 470, 1320, 'sb', 23, CL_GREY, 'l'); put_emoji(cv, '🔔', 905, 1195, 40)
    coin(cv, 'salut_chapeau', 150, 1440, 260)
    mention_pedago(c, 1475, CL_GREY, 1)

SLIDES = [s_cover, s_identite, s_croissance, s_flux, s_rentab, s_solid, s_div, s_rivaux, s_fin]
LOGOS |= {'PROFIL'}
NS = len(SLIDES)
def render(i):
    """deux calques : le dessin cairo dessous, les images (logos, pictogrammes, Mister Coin, émojis) dessus"""
    im = Image.new('RGBA', (W, H), 0); s, c = surface()
    SLIDES[i](im, c); cv = fond_clair(); cv.alpha_composite(to_img(s)); cv.alpha_composite(im); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
