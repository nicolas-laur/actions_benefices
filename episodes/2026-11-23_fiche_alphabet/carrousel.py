"""Fiche entreprise n°2 : « Que vaut Alphabet ? » (chiffres arrêtés à la clôture du vendredi 20/11/2026), 9 diapos, thème clair.
Modèle : episodes/2026-11-22_fiche_nvidia/carrousel.py (mêmes fonctions de pied, rangées et bulles). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

R = 1.0990                                                                  # BCE, 20/11/2026 : 1 € = 1,0990 $
def e(usd): return usd/R
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
    logo_plein(cv, 'ALPH_complet', 540-170, 330, 340)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "ALPHABET ?", 540, 600, 'k', 124, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "Cloud +103" + NB + "%", 540, 772, 'k', 70, CL_GREEN, 'c')
    text(c, "et pourtant −34" + NB + "% en bourse", 540, 846, 'k', 46, CL_RED, 'c')
    text(c, "Depuis son record de mai. Et Nvidia vient", 540, 914, 'sb', 27, CL_GREY, 'c')
    text(c, "de passer derrière elle en bourse.", 540, 952, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('trending-up', 'Croissance'), ('cash-multiple', 'Rentabilité'), ('bank', 'Solidité'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "On ouvre|les comptes !", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
PUB = [("Recherche Google", 49.7, CL_TEAL), ("Publicité YouTube", 8.8, CL_TEAL), ("Réseau publicitaire", 5.8, CL_TEAL)]
HORS = [("Cloud", 24.1, CL_NAVY), ("Abonnements, Play, appareils", 11.2, '4F79A8'), ("Autres (Waymo…)", 0.4, 'BDBDBD')]
def barres_pct(c, rows, x, y, w):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*62; text(c, lab, x, yy, 'xb', 22, CL_INK, 'l'); text(c, fmt(p)+NB+'%', x+w, yy, 'k', 22, colr, 'r')
        rr(c, x, yy+18, w, 12, 6); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+18, max(w*p/100, 10), 12, 6); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Chiffre d'affaires du 3e trimestre 2026")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'GOOG', 70, 450, 120)
    for j, l in enumerate(["Maison mère de Google, YouTube et Waymo.", "Vit surtout de la publicité (64 % des ventes).", "Loue serveurs et puces d'IA aux entreprises."]):
        text(c, l, 230, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "PUBLICITÉ · 64,3 %", ['ok'], 80, 608); barres_pct(c, PUB, 80, 652, 420)
    famille(c, "HORS PUBLICITÉ · 35,7 %", ['ok'], 580, 608); barres_pct(c, HORS, 580, 652, 420)
    rangee(c, 905, [('neutre', "En bourse depuis", "2004"), ('neutre', "Capitalisation", "≈" + NB + "2" + NB + "970 Md€"), ('ko', "Cours (20/11)", "241,39 €")])
    src(c, "Source : Alphabet, communiqué du 28/10/2026 ; cours GOOGL (classe A) ; 1 € = 1,0990 $ (BCE, 20/11).", 1030)
    pied(cv, c, "La moitié des ventes vient encore de la recherche Google. Mais le Cloud pèse déjà un quart du total, contre moins d'un dixième en 2021. "
         "Alphabet détient aussi environ 10 % d'Anthropic, entrée en bourse cette semaine.", 'loupe', "Pas que Google !", 1060)

# ---------- 3. croissance : CA annuel ----------
CA = [257.637, 282.836, 307.394, 350.018, 402.836]; CLOUD = [19.206, 26.280, 33.088, 43.229, 58.705]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires annuel, en milliards d'euros, dont Cloud (vert foncé)")
    carte(c, 40, 345, 1000, 545)
    data = [(e(cl), e(t-cl)) for t, cl in zip(CA, CLOUD)]; bw, g, x0 = 120, 66, 112; base, top = 770, 440
    k = barres_empilees(c, data, x0, base, top, bw, g, [CL_TEAL, CL_LIME])
    gr = [None]+[t/p-1 for p, t in zip(CA, CA[1:])]
    for i, (d, gg) in enumerate(zip(data, gr)):
        cx = x0+i*(bw+g)+bw/2; tot = sum(d); text(c, fmt(tot), cx, base-tot*k-26, 'xb', 25, CL_INK, 'c')
        text(c, fmt(d[0]), cx, base+92, 'k', 22, CL_TEAL, 'c')
        text(c, str(2021+i), cx, base+30, 'sb', 22, CL_GREY, 'c')
        text(c, '–' if gg is None else '+'+fmt(gg*100, 0)+NB+'%', cx, base+60, 'xb', 21, CL_GREEN if gg else CL_GREY, 'c')
    picto(cv, 'cloud-outline', 70, 862, 30, CL_TEAL)
    rangee(c, 905, [('ok', "Sur 4 ans", "+11,8" + NB + "%/an"), ('ok', "Dernier trimestre", "+25" + NB + "%"), ('ok', "12 derniers mois", "428,7 Md€")])
    src(c, "Source : Alphabet, 10-K et communiqués. Exercices = années civiles.", 1030)
    pied(cv, c, "En 4 ans, le chiffre d'affaires a gagné 56 %. Et la croissance accélère : +25 % au dernier trimestre, 13e trimestre d'affilée au-dessus de +10 %. "
         "Le Cloud a doublé en un an.", 'court', "Ça accélère !", 1060)

# ---------- 4. d'où vient l'argent (flux du T3) ----------
def s_flux(cv, c):
    tt = "3e TRIMESTRE"; lw = 230; x_t = 540-(lw+24+tw(c, tt, 'k', 58))/2; text(c, tt, x_t+lw+24, 236, 'k', 58, CL_NAVY, 'l')
    logo_plein(cv, 'ALPH_complet', x_t, 240, lw)
    text(c, "D'où vient l'argent, où il va", 540, 300, 'xb', 34, CL_INK, 'c')
    text(c, "Clos le 30/09/2026, en milliards d'euros", 540, 346, 'sb', 24, CL_GREY, 'c')
    k = 4.0; X = [176, 336, 490, 646, 802, 900]
    v = dict(se=e(63.350), yt=e(11.207), ne=e(7.455), ab=e(14.290), sv=e(96.302), cl=e(30.709), ca=e(127.577), mb=e(76.158), cr=e(51.419),
             re=e(40.576), ch=e(35.582), rn=e(26.468), pa=e(8.221), im=e(5.887))
    L = etiquette; f = lambda x: fmt(x); p = lambda x: '('+fmt(x)+')'
    def lg(nom, val, colr, sz=22): return [(nom, 'xb', sz, colr), (val, 'k', sz+2, colr)]
    N = {
     'se': dict(x=X[0], y=470, v=v['se'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Recherche', f(v['se']), ['+12 % sur 1 an'], CL_LIME)),
     'ab': dict(x=X[0], y=760, v=v['ab'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=lg('Abonnements', f(v['ab']), CL_LIME)),
     'yt': dict(x=X[0], y=860, v=v['yt'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=lg('YouTube', f(v['yt']), CL_LIME)),
     'ne': dict(x=X[0], y=950, v=v['ne'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=lg('Réseau', f(v['ne']), CL_LIME)),
     'sv': dict(x=X[1], y=600, v=v['sv'], c=CL_LIME, rib=CL_LIME_R, side='t', lab=L('Google|Services', f(v['sv']), ['+11 % sur 1 an'], CL_LIME)),
     'cl': dict(x=X[1], y=1060, v=v['cl'], c=CL_TEAL, rib=CL_TEAL_R, side='b', lab=L('Cloud', f(v['cl']), ['+103 % sur 1 an'], CL_TEAL)),
     'ca': dict(x=X[2], y=660, v=v['ca'], c=CL_INK, rib=CL_LIME_R, side='t', lab=L("Chiffre|d'affaires", f(v['ca']), ['+25 % sur 1 an'], CL_INK)),
     'mb': dict(x=X[3], y=600, v=v['mb'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L('Marge|brute', f(v['mb']), ['60 % des ventes'], CL_GREEN)),
     'cr': dict(x=X[3], y=1000, v=v['cr'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Coût des|ventes', p(v['cr']), ['dont 14,9 aux', 'partenaires'], CL_RED)),
     're': dict(x=X[4], y=600, v=v['re'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L("Résultat|d'exploitation", f(v['re']), ['32 % des ventes', '+30 % sur 1 an'], CL_GREEN)),
     'ch': dict(x=X[4], y=900, v=v['ch'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Recherche|et frais', p(v['ch']), ['dont 18,8 de', 'recherche'], CL_RED)),
     'rn': dict(x=X[5], y=560, v=v['rn'], c=CL_GREEN, rib=CL_GREEN_R, side='r', lab=L('Résultat|net', f(v['rn']), ['21 % des', 'ventes'], CL_GREEN, 23)),
     'pa': dict(x=X[5], y=720, v=v['pa'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Participations', p(v['pa']), ['surtout SpaceX'], CL_RED, 21)),
     'im': dict(x=X[5], y=860, v=v['im'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Impôts', p(v['im']), [], CL_RED, 23)),
    }
    links = [('se', 'sv', v['se']), ('ab', 'sv', v['ab']), ('yt', 'sv', v['yt']), ('ne', 'sv', v['ne']),
             ('sv', 'ca', v['sv'], CL_LIME_R), ('cl', 'ca', v['cl'], CL_TEAL_R),
             ('ca', 'mb', v['mb']), ('ca', 'cr', v['cr']), ('mb', 're', v['re']), ('mb', 'ch', v['ch']),
             ('re', 'rn', v['rn']), ('re', 'pa', v['pa']), ('re', 'im', v['re']-v['rn']-v['pa'])]
    flux(c, N, links, k)
    picto(cv, 'magnify', 60, 470+v['se']*k/2-60, 40, CL_LIME); picto(cv, 'cloud-outline', 336+13, 1060+v['cl']*k+150, 46, CL_TEAL)
    picto(cv, 'server', 659, 1378, 36, CL_RED); picto(cv, 'flask-outline', 815, 900+v['ch']*k+205, 40, CL_RED)
    picto(cv, 'cash-multiple', 1030, 528, 36, CL_GREEN)
    source(c, "Source : Alphabet, résultats du 28/10/2026", 1440, CX, 18); source(c, "(CA 127,6 Md$). 1 € = 1,0990 $ (BCE, 20/11).", 1462, CX, 18)
    text(c, "Mise en page inspirée de App Economy Insights (How They Make Money)", 600, 1488, 'sb', 17, CL_GREY, 'c')
    coin(cv, 'neutre', 105, 1450, 240)

# ---------- 5. rentabilité ----------
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net (Md€) et marge nette, par exercice")
    carte(c, 40, 345, 1000, 545)
    graphique(c, [str(y) for y in range(2021, 2026)], [e(x) for x in (76.033, 59.972, 73.795, 100.118, 132.170)], 80, 1000, 690, 430,
              courbe=[29.5, 21.2, 24.0, 28.6, 32.8], cbase=860, ctop=790, couleur=CL_GREEN)
    text(c, "Marge nette", 80, 752, 'xb', 21, CL_TEAL, 'l')
    rangee(c, 880, [('ok', "BPA 2025", "9,84 €", "×1,9 depuis 2021"), ('neutre', "PER*", "24,2", "cours ÷ bénéfice par action, 12 mois")])
    src(c, "* Hors réévaluation de SpaceX et d'Anthropic : 99 Md$ de bénéfice sur papier en 9 mois. Avec elle,", 995)
    src(c, "le PER tombe à 13,9 et donne une image trompeuse. Source : Alphabet, 10-K et communiqués.", 1019)
    pied(cv, c, "Sur 100 € de ventes, Alphabet garde 33 € de bénéfice net en 2025. Le creux de 2022 : des pertes sur ses placements (après 12 Md$ de gains en 2021) et des coûts en hausse.",
         'sceptique', "Bénéfice… sur papier ?", 1050)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Bilan au 30/09/2026, flux sur 12 mois")
    carte(c, 40, 345, 1000, 625)
    famille(c, "BILAN", ['ok', 'ko'], 80, 385)
    tuile(c, 70, 410, 460, 'ok', "Trésorerie nette", "+126 Md€", "dont 68 d'actions SpaceX", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'ko', "Dette", "115 Md€", "×2,7 depuis janvier", fond='F5F3EE')
    famille(c, "ARGENT GÉNÉRÉ", ['ko', 'neutre'], 80, 535)
    tuile(c, 70, 560, 460, 'ko', "Flux de trésorerie libre", "−8,2 Md€", "au T3, 2e négatif", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'neutre', "Sur 12 mois", "+18,0 Md€", "66,7 Md€ en 2025", fond='F5F3EE')
    famille(c, "INVESTISSEMENTS", ['ko'], 80, 685)
    tuile(c, 70, 710, 940, 'ko', "Prévision 2026 : deux fois plus qu'en 2025, encore plus en 2027", "177 à 187 Md€", "(195 à 205 Md$)", fond='F5F3EE')
    for j, l in enumerate(["Trésorerie nette = cash − dettes.", "Flux de trésorerie libre = l'argent qui reste après les investissements.",
                           "Investissements = centres de données, serveurs, puces."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Source : Alphabet, communiqué et 10-Q du T3 ; émissions de novembre non incluses.", 1000)
    pied(cv, c, "Alphabet dépense plus qu'elle ne gagne pour construire ses centres de données. Pour payer, elle emprunte : encore 6 Md€ et 6 Md$ canadiens d'obligations ce mois-ci.",
         'sueur', "Ça chauffe !", 1030)

# ---------- 7. dividende ----------
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par année de versement, en euros")
    carte(c, 40, 345, 1000, 430)
    graphique(c, ["2024", "2025", "2026*"], [e(x) for x in (0.60, 0.83, 0.87)], 120, 960, 700, 450, couleur=CL_GOLD,
              fmt_b=lambda v: fmt(v, 2)+NB+'€', bw=170, hachure=(2,))
    text(c, "* dont 0,22 $ versé le 14/12. Premier dividende de l'histoire en juin 2024.", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ok', "+5 % par an", "0,22 $", "par trimestre"), ('neutre', "Rendement (20/11)", "0,3" + NB + "%", "0,88 $ par an")])
    rangee(c, 901, [('ko', "Rachats 2026", "0 €", "41,6 Md€ en 2025"), ('ko', "Nombre d'actions", "+1,7" + NB + "%", "depuis janvier")])
    pied(cv, c, "Le dividende monte, mais il reste petit. Le vrai changement : Alphabet ne rachète plus ses actions, elle en émet. Environ 50 Md$ levés en juin, "
         "dont 10 Md$ par Berkshire Hathaway. Action américaine : compte-titres, pas de PEA.", 'haussement', "Elle n'en rachète plus,|elle en émet !", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "Trimestre clos le 30/09/2026 pour les quatre")
    carte(c, 40, 345, 1000, 620)
    xs = [165, 415, 665, 915]
    for x, (kk, w) in zip(xs, [('ALPH_complet', 180), ('MSFT_complet', 190), ('META_complet', 170), ('AMZN_complet', 95)]): logo_plein(cv, kk, x-w/2, 405, w)
    text(c, "INVESTISSEMENTS POUR 100 € DE VENTES", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", "", ""], [40.3, 42.7, 54.0, 38.3], 40, 1040, 700, 530, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 0)+NB+'€', bw=130)
    for lab, vals, cols_, y in [("CROISSANCE SUR UN AN", ["+25" + NB + "%", "+19" + NB + "%", "+26" + NB + "%", "+12" + NB + "%"], [CL_GREEN]*4, 765),
                                ("MARGE D'EXPLOITATION", ["32" + NB + "%", "50" + NB + "%", "20" + NB + "%*", "14" + NB + "%"], [CL_INK]*4, 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, vv, cc in zip(xs, vals, cols_): text(c, vv, x, y+48, 'k', 40, cc, 'c')
    src(c, "Sources : résultats publiés. Investissements = achats d'immobilisations (Meta : y compris", 995)
    src(c, "location-financement). * Meta : 35 % hors charge judiciaire de 9,9 Md$.", 1019)
    pied(cv, c, "Les quatre géants réinvestissent 38 à 54 € pour 100 € de ventes. Alphabet croît plus vite que Microsoft et Amazon, avec une marge plus faible que Microsoft.",
         'reflechit', "Tous dans la même course !", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('cash-multiple', "Le dividende du 14 décembre", "0,22 $ par action, détachement le 7 décembre."),
                                     ('calendar-month-outline', "Les résultats de début février", "Avec le budget d'investissement 2027, annoncé en forte hausse."),
                                     ('chart-line' if False else 'trending-up', "Les émissions d'actions", "Encore 27,6 Md$ possibles dans le programme en cours.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, tu préfères une entreprise", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "qui investit ou qui te reverse ?", 540, 868, 'k', 46, CL_GOLD, 'c')
    text(c, "Dis-le en commentaire", 540, 935, 'sb', 30, CL_GREY, 'c'); put_emoji(cv, '👇', 540, 985, 44)
    rr(c, 160, 1040, 760, 70, 35); col(c, CL_NAVY); c.fill(); text(c, "ENREGISTRE-LE POUR LES PROCHAINS RÉSULTATS", 540, 1075, 'xb', 24, WHITE, 'c'); put_emoji(cv, '📌', 935, 1072, 38)
    carte(c, 300, 1150, 650, 200, 22); logo(cv, 'PROFIL', 390, 1250, 120)
    text(c, "ABONNE-TOI", 470, 1205, 'k', 40, CL_GOLD, 'l'); text(c, "à Actions_Benefices", 470, 1252, 'xb', 26, CL_INK, 'l')
    text(c, "la bourse sans jargon,", 470, 1290, 'sb', 23, CL_GREY, 'l'); text(c, "chaque semaine", 470, 1320, 'sb', 23, CL_GREY, 'l'); put_emoji(cv, '🔔', 905, 1195, 40)
    coin(cv, 'salut_chapeau', 150, 1440, 260)
    text(c, "Je détiens des actions Alphabet.", 540, 1462, 'xb', 21, CL_INK, 'c')
    mention_pedago(c, 1490, CL_GREY, 1)

SLIDES = [s_cover, s_identite, s_croissance, s_flux, s_rentab, s_solid, s_div, s_rivaux, s_fin]
LOGOS |= {'PROFIL'}
NS = len(SLIDES)
def render(i):
    """deux calques : le dessin cairo dessous, les images (logos, pictogrammes, Mister Coin, émojis) dessus"""
    im = Image.new('RGBA', (W, H), 0); s, c = surface()
    SLIDES[i](im, c); cv = fond_clair(); cv.alpha_composite(to_img(s)); cv.alpha_composite(im); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
