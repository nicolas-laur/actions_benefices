"""Fiche entreprise n°7 : « Que vaut Schneider Electric ? » (cours : paramètres du jour ci-dessous), 9 diapos, thème clair, livrée en 4:5 seulement.
Modèle : episodes/2026-11-23_fiche_alphabet/carrousel.py (mêmes pieds, rangées et bulles). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

# ---------- paramètres du jour (seul bloc à changer pour mettre la fiche à jour ; voir sources.md, section 0) ----------
JOUR = "25/11"                    # date de clôture retenue
P = 216.65                        # clôture SU (€), Euronext Paris
AVANT = 303.00                    # clôture du 02/10/2026, veille de l'annonce du rachat de PTC
NA = 603.605363                   # actions composant le capital au 31/10/2026 (M), Schneider Electric
R = 1.0935                        # taux BCE du 25/11/2026 : 1 € = 1,0935 $
def md(x, d=1): return fmt(x, d)+NB+'Md€'
CAP = NA*P/1000                   # capitalisation (Md€)
CHUTE = round((P/AVANT-1)*100)    # variation depuis l'annonce (%)
BPA_2025 = 7.41                   # bénéfice net part du groupe par action 2025 (€)

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
def logo_se(cv, c, x, cy, h, size):
    """symbole Schneider + nom écrit en texte (le symbole seul est peu connu)"""
    logo_plein(cv, 'SU', x, cy, h); text(c, "Schneider Electric", x+h+16, cy+size*.36, 'k', size, '3DCD58', 'l')
def s_cover(cv, c):
    w = 70+16+tw(c, "Schneider Electric", 'k', 46); logo_se(cv, c, 540-w/2, 330, 70, 46)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "SCHNEIDER ?", 540, 600, 'k', 116, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "PTC : le plus gros rachat de son histoire", 540, 772, 'k', 40, CL_INK, 'c')
    text(c, fmt(CHUTE, 0).replace("-", "−")+NB+"% depuis l'annonce", 540, 846, 'k', 46, CL_RED, 'c')
    text(c, "Pourtant, ses ventes n'ont jamais été aussi hautes.", 540, 914, 'sb', 27, CL_GREY, 'c')
    text(c, "Que disent vraiment ses comptes ?", 540, 952, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('trending-up', 'Croissance'), ('cash-multiple', 'Rentabilité'), ('bank', 'Dividende'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "On ouvre|les comptes !", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
ACT = [("Gestion de l'énergie", 83.4, CL_TEAL), ("Automatismes industriels", 16.6, CL_NAVY)]
REG = [("Amérique du Nord", 39.6, CL_TEAL), ("Europe", 24.3, CL_NAVY), ("Chine et Asie de l'Est", 18.2, '4F79A8'), ("Asie du Sud et international", 17.9, 'BDBDBD')]
def barres_pct(c, rows, x, y, w, pas=74):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*pas; text(c, lab, x, yy, 'xb', 22, CL_INK, 'l'); text(c, fmt(p)+NB+'%', x+w, yy, 'k', 22, colr, 'r')
        rr(c, x, yy+18, w, 12, 6); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+18, max(w*p/100, 10), 12, 6); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Chiffre d'affaires des 9 premiers mois de 2026 (32,7 Md€)")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'SU', 80, 450, 110)
    for j, l in enumerate(["Français, il fabrique tout ce qui distribue", "l'électricité : disjoncteurs, onduleurs,", "tableaux, refroidissement… et des logiciels."]):
        text(c, l, 230, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "PAR ACTIVITÉ", ['ok'], 80, 608); barres_pct(c, ACT, 80, 652, 420, 70)
    text(c, "Les centres de données", 80, 820, 'sb', 21, CL_GREY, 'l'); text(c, "tirent la gestion de l'énergie.", 80, 848, 'sb', 21, CL_GREY, 'l')
    famille(c, "PAR RÉGION", ['ok'], 580, 608); barres_pct(c, REG, 580, 652, 420, 56)
    rangee(c, 905, [('neutre', "Cotée à", "Paris", "éligible PEA"), ('neutre', "Capitalisation", "≈"+NB+fmt(CAP, 0)+NB+"Md€"), ('ko', "Cours ("+JOUR+")", fmt(P, 2)+NB+"€")])
    src(c, "Source : Schneider Electric, chiffre d'affaires du 3e trimestre 2026 (16/10/2026) ; cours SU (Euronext Paris).", 1030)
    pied(cv, c, "Plus de 8 euros sur 10 viennent de la gestion de l'énergie (matériel, logiciels, services), portée par les centres de données de l'IA. "
         "L'Amérique du Nord pèse désormais plus que l'Europe.", 'loupe', "Tout ce qui|est électrique", 1060)

# ---------- 3. croissance : CA annuel ----------
CA = [28.905, 34.176, 35.902, 38.153, 40.152]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires annuel, en Md€")
    carte(c, 40, 345, 1000, 545)
    base = 770
    graphique(c, [str(2021+i) for i in range(5)], CA, 80, 1000, base, 470, couleur=CL_LIME, bw=120)
    gr = [None]+[t/p-1 for p, t in zip(CA, CA[1:])]; step = 920/5
    for i, gg in enumerate(gr):
        cx = 80+step*(i+.5)
        text(c, '–' if gg is None else ('+' if gg > 0 else '−')+fmt(abs(gg)*100, 0)+NB+'%', cx, base+62, 'xb', 21, CL_GREY if gg is None else (CL_GREEN if gg > 0 else CL_RED), 'c')
    text(c, "en petit : variation sur un an (publiée)", 80, 868, 'sb', 18, CL_GREY, 'l')
    rangee(c, 905, [('ok', "Sur 4 ans", "+8,6" + NB + "%/an"), ('ok', "3e trimestre 2026", "+17" + NB + "%", "record"), ('ok', "Objectif 2026", "+12 à +14" + NB + "%")])
    src(c, "Source : Schneider Electric, rapports annuels et communiqué du 16/10/2026. « Hors change » = croissance organique.", 1030)
    pied(cv, c, "Les ventes montent chaque année, et ça accélère : +17 % au dernier trimestre, du jamais vu depuis 2021. "
         "La demande des centres de données a plus que doublé sur un an.", 'court', "Ça accélère !", 1060)

# ---------- 4. d'où vient l'argent (flux du semestre) ----------
def s_flux(cv, c):
    tt = "1er SEMESTRE"; lw = 70; x_t = 540-(lw+20+tw(c, tt, 'k', 58))/2; text(c, tt, x_t+lw+20, 236, 'k', 58, CL_NAVY, 'l')
    logo_plein(cv, 'SU', x_t, 216, lw)
    text(c, "D'où vient l'argent, où il va", 540, 300, 'xb', 34, CL_INK, 'c')
    text(c, "Janvier à juin 2026, en milliards d'euros", 540, 346, 'sb', 24, CL_GREY, 'c')
    k = 21.5; X = [240, 440, 625, 810, 900]
    v = dict(na=8.312, eu=5.305, ce=3.796, sa=3.813, ca=21.226, mb=9.014, cr=12.212, ex=3.613, ch=5.401, rn=2.548, im=1.065)
    L = etiquette; f = lambda x: fmt(x, 1); p = lambda x: '('+f(x)+')'
    N = {
     'na': dict(x=X[0], y=430, v=v['na'], c=CL_TEAL, rib=CL_TEAL_R, side='l', lab=L('Amérique|du Nord', f(v['na']), ['39 %'], CL_TEAL)),
     'eu': dict(x=X[0], y=640, v=v['eu'], c=CL_NAVY, rib='B9C6D6', side='l', lab=L('Europe', f(v['eu']), ['25 %'], CL_NAVY)),
     'ce': dict(x=X[0], y=790, v=v['ce'], c='4F79A8', rib='C3D0E2', side='l', lab=L('Chine et|Asie de l\'Est', f(v['ce']), ['18 %'], '4F79A8')),
     'sa': dict(x=X[0], y=925, v=v['sa'], c='8C8C8C', rib='DDDDDD', side='l', lab=L('Asie du Sud|et international', f(v['sa']), ['18 %'], CL_GREY)),
     'ca': dict(x=X[1], y=560, v=v['ca'], c=CL_INK, rib=CL_LIME_R, side='t', lab=L("Chiffre|d'affaires", f(v['ca']), ['+10 % sur 1 an'], CL_INK)),
     'mb': dict(x=X[2], y=500, v=v['mb'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L('Marge|brute', f(v['mb']), ['42 % des ventes'], CL_GREEN)),
     'cr': dict(x=X[2], y=740, v=v['cr'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Coût des|ventes', p(v['cr']), [], CL_RED)),
     'ex': dict(x=X[3], y=460, v=v['ex'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L("Résultat|d'exploitation", f(v['ex']), ['17 % des ventes'], CL_GREEN)),
     'ch': dict(x=X[3], y=600, v=v['ch'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Charges', p(v['ch']), ['dont 4,1 de frais', 'commerciaux et généraux', 'et 0,8 de recherche'], CL_RED)),
     'rn': dict(x=X[4], y=440, v=v['rn'], c=CL_GREEN, rib=CL_GREEN_R, side='r', lab=L('Résultat|net', f(v['rn']), [], CL_GREEN, 23)),
     'im': dict(x=X[4], y=640, v=v['im'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Impôts', p(v['im']), ['et frais', 'financiers'], CL_RED, 21)),
    }
    links = [('na', 'ca', v['na'], CL_TEAL_R), ('eu', 'ca', v['eu'], 'B9C6D6'), ('ce', 'ca', v['ce'], 'C3D0E2'), ('sa', 'ca', v['sa'], 'DDDDDD'),
             ('ca', 'mb', v['mb']), ('ca', 'cr', v['cr']), ('mb', 'ex', v['ex']), ('mb', 'ch', v['ch']),
             ('ex', 'rn', v['rn']), ('ex', 'im', v['im'])]
    flux(c, N, links, k)
    source(c, "Source : Schneider Electric, comptes du 1er semestre 2026", 1440, CX, 18); source(c, "(publiés le 30/07/2026, croissance publiée).", 1462, CX, 18)
    text(c, "Mise en page inspirée de App Economy Insights (How They Make Money)", 600, 1488, 'sb', 17, CL_GREY, 'c')
    coin(cv, 'site_calculatrice', 115, 1450, 240)

# ---------- 5. rentabilité ----------
RN = [3204, 3477, 4003, 4269, 4163]
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net part du groupe (M€) et marge nette, par année")
    carte(c, 40, 345, 1000, 545)
    graphique(c, [str(y) for y in range(2021, 2026)], RN, 80, 1000, 690, 430, courbe=[x/y/10 for x, y in zip(RN, CA)], cbase=862, ctop=800,
              couleur=CL_GREEN, fmt_b=lambda v: fmt(v, 0))
    text(c, "Marge nette", 1000, 878, 'xb', 21, CL_TEAL, 'r')
    rangee(c, 905, [('ok', "Marge d'exploitation ajustée", "19,3" + NB + "%", "1er semestre 2026"), ('ko', "PER ("+JOUR+")", fmt(P/BPA_2025, 0), "bénéfice 2025 : 7,41 € par action")])
    src(c, "Source : Schneider Electric, rapports annuels et comptes semestriels 2026.", 1030)
    pied(cv, c, "Une régularité rare : environ 11 € de bénéfice pour 100 € de ventes, chaque année. "
         "Au 1er semestre 2026, le bénéfice monte de 30 %, à 2,5 Md€.", 'reflechit', "Une vraie|machine", 1060)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Dette, cash et financement du rachat de PTC")
    carte(c, 40, 345, 1000, 625)
    famille(c, "AVANT PTC", ['neutre', 'ok'], 80, 385)
    tuile(c, 70, 410, 460, 'neutre', "Dette nette (30/06/2026)", md(14.9), "dettes − trésorerie", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'ok', "Cash-flow libre 2025", md(4.6), "record", fond='F5F3EE')
    famille(c, "LE RACHAT DE PTC", ['ko', 'neutre'], 80, 535); logo_plein(cv, 'PTC', 890, 532, 110)
    tuile(c, 70, 560, 460, 'ko', "Prix (dette de PTC incluse)", "≈" + NB + md(21.7), "23,7 Md$", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'neutre', "Actions nouvelles", md(6.0), "25 M d'actions à 240 €", fond='F5F3EE')
    famille(c, "FINANCÉ AUSSI PAR DETTE", ['ko'], 80, 685)
    tuile(c, 70, 710, 940, 'ko', "Obligations : 6 Md€ + 10 Md$ (≈" + NB + "9,1 Md€, coupon moyen 5,7 %)", "≈" + NB + md(15.1), "de dette nouvelle", fond='F5F3EE')
    for j, l in enumerate(["Cash-flow libre = l'argent qui reste après les investissements.",
                           "Notes de crédit confirmées : A (S&P) et A2 (Moody's).",
                           "Les actions nouvelles diluent les actionnaires d'environ 4 %."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Sources : Schneider Electric, comptes semestriels 2026, communiqués des 05/10, 20/10, 26/10 et 18/11/2026.", 1000)
    pied(cv, c, "Schneider paie PTC en cash : il a émis 6 Md€ d'actions nouvelles et emprunte environ 15 Md€. "
         "Sa dette va donc fortement grimper, mais il génère plus de 4 Md€ de cash par an.", 'site_tirelire', "Gros chèque !", 1030)

# ---------- 7. dividende ----------
DV = [2.60, 2.90, 3.15, 3.50, 3.90, 4.20]
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par année de versement, en euros")
    carte(c, 40, 345, 1000, 430)
    graphique(c, [str(2021+i) for i in range(6)], DV, 90, 990, 700, 470, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 2), bw=100)
    text(c, "Versé une fois par an, en mai. 16e hausse d'affilée en 2026.", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ok', "Hausse sur 5 ans", "+62" + NB + "%", "2,60 → 4,20 €"), ('neutre', "Rendement ("+JOUR+")", fmt(4.20/P*100, 1)+NB+"%", "4,20 € par an")])
    rangee(c, 901, [('ok', "Distribution", "57" + NB + "%", "du bénéfice 2025"), ('neutre', "Prochain versement", "12 mai 2027", "")])
    pied(cv, c, "Le dividende augmente tous les ans et ne prend qu'un peu plus de la moitié du bénéfice : il reste de la marge. "
         "Mais à ce cours, le rendement reste modeste.", 'etoiles', "Il monte|chaque année", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "Trimestre juillet-septembre 2026")
    carte(c, 40, 345, 1000, 620)
    xs = [207, 540, 873]
    logo_plein(cv, 'SU', xs[0]-110, 408, 50); text(c, "Schneider", xs[0]-48, 418, 'k', 32, '3DCD58', 'l'); logo_plein(cv, 'ABB', xs[1]-80, 408, 160); logo_plein(cv, 'ETN', xs[2]-90, 408, 180)
    text(c, "CHIFFRE D'AFFAIRES DU TRIMESTRE (MD€)", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", ""], [11.460, 9.701/R, 8.947/R], 40, 1040, 700, 530, couleur=CL_GOLD, fmt_b=lambda v: fmt(v), bw=150)
    for lab, vals, cols_, y in [("CROISSANCE SUR UN AN, HORS CHANGE", ["+17" + NB + "%", "+14" + NB + "%", "+19" + NB + "%"], [CL_GREEN]*3, 765),
                                ("MARGE D'EXPLOITATION AJUSTÉE", ["19,3" + NB + "%", "20,8" + NB + "%", "25,3" + NB + "%"], [CL_INK]*3, 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, vv, cc in zip(xs, vals, cols_): text(c, vv, x, y+48, 'k', 40, cc, 'c')
    src(c, "Marges : Schneider au 1er semestre 2026 ; ABB (EBITA opérationnel) et Eaton (marge des activités) au 3e trimestre.", 995)
    src(c, "Taux BCE du 25/11/2026 : 1 € = 1,0935 $. Sources : résultats publiés.", 1019)
    pied(cv, c, "Le Suisse ABB et l'Américain Eaton profitent eux aussi des centres de données. Schneider est le plus gros des trois, "
         "mais pas le plus rentable : Eaton garde une marge nettement plus élevée.", 'site_longue_vue', "Le plus gros|des trois", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('handshake-outline', "Le rachat de PTC", "Accord des autorités et finalisation, prévue d'ici fin 2027."),
                                     ('calendar-month-outline', "Les résultats annuels du 18 février", "Objectif 2026 : ventes en hausse de 12 à 14 % hors change."),
                                     ('server', "La demande des centres de données", "Elle a plus que doublé sur un an au 3e trimestre.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, ce rachat de PTC :", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "pari d'avenir ou trop cher ?", 540, 868, 'k', 46, CL_GOLD, 'c')
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
