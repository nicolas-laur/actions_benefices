"""Fiche entreprise n°3 : « Que vaut Cisco ? » (cours et taux BCE : paramètres du jour ci-dessous), 9 diapos, thème clair, livrée en 4:5 seulement.
Modèle : episodes/2026-11-23_fiche_alphabet/carrousel.py (mêmes pieds, rangées et bulles). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

# ---------- paramètres du jour (seul bloc à changer pour mettre la fiche à jour ; voir sources.md, section 0) ----------
JOUR = "24/11"                    # date de clôture retenue
R = 1.0963                        # taux de référence BCE du même jour : 1 € = R $
P = 93.99                         # clôture CSCO ($)
RECORD = 130.00                   # record de clôture des 12 derniers mois (04/06/2026)
NA = 3942.448184                  # actions en circulation (M), page de garde du 10-Q, 12/11/2026
BPA_12M = 3.75                    # BPA dilué des 12 derniers mois ($)
DIV = 1.68                        # dividende annuel au rythme actuel (4 × 0,42 $)
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
CSCO_BLEU = '1B8FC4'                                                        # bleu Cisco un peu assombri pour le contraste sur fond clair

# ---------- 1. couverture ----------
def s_cover(cv, c):
    logo_plein(cv, 'CSCO', 540-120, 330, 240)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "CISCO ?", 540, 600, 'k', 128, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "Ventes +24" + NB + "%", 540, 772, 'k', 70, CL_GREEN, 'c')
    text(c, "et pourtant "+fmt(CHUTE, 0).replace("-", "−")+NB+"% en bourse", 540, 846, 'k', 46, CL_RED, 'c')
    text(c, "Depuis son record du 4 juin.", 540, 914, 'sb', 27, CL_GREY, 'c')
    text(c, "Que disent vraiment ses comptes ?", 540, 952, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('trending-up', 'Croissance'), ('cash-multiple', 'Rentabilité'), ('bank', 'Dividende'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "On ouvre|les comptes !", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
ACT = [("Équipements réseau", 60.1, CL_TEAL), ("Services (maintenance…)", 20.8, '4F79A8'), ("Cybersécurité", 11.4, CL_NAVY),
       ("Collaboration (Webex)", 6.1, '4F79A8'), ("Observabilité (Splunk)", 1.5, 'BDBDBD')]
REG = [("Amériques", 62.1, CL_TEAL), ("Europe, Moyen-Orient, Afrique", 24.1, CL_NAVY), ("Asie-Pacifique", 13.8, '4F79A8')]
def barres_pct(c, rows, x, y, w, pas=52):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*pas; text(c, lab, x, yy, 'xb', 21, CL_INK, 'l'); text(c, fmt(p)+NB+'%', x+w, yy, 'k', 21, colr, 'r')
        rr(c, x, yy+17, w, 11, 5.5); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+17, max(w*p/100, 10), 11, 5.5); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Chiffre d'affaires du trimestre clos le 24/10/2026")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'CSCO', 70, 450, 120)
    for j, l in enumerate(["Fabrique ce qui relie les ordinateurs :", "routeurs, commutateurs, Wi-Fi.", "Vend aussi cybersécurité et logiciels."]):
        text(c, l, 230, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "D'OÙ VIENT L'ARGENT", ['ok'], 80, 606); barres_pct(c, ACT, 80, 646, 440)
    famille(c, "PAR RÉGION", ['ok'], 600, 606); barres_pct(c, REG, 600, 646, 400, pas=70)
    rangee(c, 905, [('neutre', "En bourse depuis", "1990"), ('neutre', "Capitalisation", "≈"+NB+fmt(e(CAP), 0)+NB+"Md€"), ('ko', "Cours ("+JOUR+")", fmt(e(P), 2)+NB+"€")])
    src(c, "Source : Cisco, communiqué du 12/11/2026 ; cours CSCO ; 1 € = "+fmt(R, 4)+" $ (BCE, "+JOUR+").", 1030)
    pied(cv, c, "6 euros sur 10 viennent encore du matériel réseau. Le rachat de Splunk en 2024 (28 Md$, le plus gros de son histoire) a ajouté "
         "logiciels et cybersécurité. Plus de 6 ventes sur 10 se font sur le continent américain.", 'loupe', "Le réseau d'abord !", 1060)

# ---------- 3. croissance : CA annuel ----------
CA = [51.557, 56.998, 53.803, 56.654, 63.325]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires par exercice (clos fin juillet), en Md€")
    carte(c, 40, 345, 1000, 545)
    base = 770
    graphique(c, [str(2022+i) for i in range(5)], [e(x) for x in CA], 80, 1000, base, 470, couleur=CL_LIME, bw=120)
    gr = [None]+[t/p-1 for p, t in zip(CA, CA[1:])]; step = 920/5
    for i, gg in enumerate(gr):
        cx = 80+step*(i+.5)
        text(c, '–' if gg is None else ('+' if gg > 0 else '−')+fmt(abs(gg)*100, 0)+NB+'%', cx, base+62, 'xb', 21, CL_GREY if gg is None else (CL_GREEN if gg > 0 else CL_RED), 'c')
    text(c, "en petit : variation sur un an", 80, 868, 'sb', 18, CL_GREY, 'l')
    rangee(c, 905, [('ok', "Sur 4 ans", "+5,3" + NB + "%/an"), ('ok', "Dernier trimestre", "+24" + NB + "%"), ('ok', "12 derniers mois", md(66.959))])
    src(c, "Source : Cisco, 10-K et communiqués. Exercice 2026 = août 2025 à juillet 2026.", 1030)
    pied(cv, c, "Croissance lente pendant 4 ans, avec un recul en 2024 : les clients finissaient d'installer le matériel déjà commandé. "
         "Puis +24 % au dernier trimestre, du jamais vu depuis plus de 15 ans, grâce à l'IA.", 'court', "Ça repart !", 1060)

# ---------- 4. d'où vient l'argent (flux du trimestre) ----------
def s_flux(cv, c):
    tt = "1er TRIMESTRE"; lw = 150; x_t = 540-(lw+24+tw(c, tt, 'k', 58))/2; text(c, tt, x_t+lw+24, 236, 'k', 58, CL_NAVY, 'l')
    logo_plein(cv, 'CSCO', x_t, 236, lw)
    text(c, "D'où vient l'argent, où il va", 540, 300, 'xb', 34, CL_INK, 'c')
    text(c, "Août à octobre 2026 (1er trimestre de l'exercice 2027), en Md€", 540, 346, 'sb', 24, CL_GREY, 'c')
    k = 27.0; X = [176, 336, 490, 646, 802, 900]
    v = dict(re=e(11.132), se=e(2.120), co=e(1.136), ob=e(0.279), pr=e(14.667), sv=e(3.850), ca=e(18.517), mb=e(11.788), cr=e(6.729),
             ex=e(5.598), ch=e(6.190), rn=e(4.552), im=e(5.598-4.552))
    L = etiquette; f = lambda x: fmt(x, 2) if x < 1 else fmt(x); p = lambda x: '('+f(x)+')'
    def lg(nom, val, colr, sz=21): return [(nom, 'xb', sz, colr), (val, 'k', sz+2, colr)]
    N = {
     're': dict(x=X[0], y=430, v=v['re'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Réseau', f(v['re']), ['+43 % sur 1 an'], CL_LIME)),
     'se': dict(x=X[0], y=760, v=v['se'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=lg('Sécurité', f(v['se']), CL_LIME)),
     'co': dict(x=X[0], y=860, v=v['co'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=lg('Collaboration', f(v['co']), CL_LIME)),
     'ob': dict(x=X[0], y=950, v=v['ob'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=lg('Observabilité', f(v['ob']), CL_LIME)),
     'pr': dict(x=X[1], y=600, v=v['pr'], c=CL_LIME, rib=CL_LIME_R, side='t', lab=L('Produits', f(v['pr']), ['+32 % sur 1 an'], CL_LIME)),
     'sv': dict(x=X[1], y=1060, v=v['sv'], c=CL_TEAL, rib=CL_TEAL_R, side='b', lab=L('Services', f(v['sv']), ['+1 % sur 1 an'], CL_TEAL)),
     'ca': dict(x=X[2], y=680, v=v['ca'], c=CL_INK, rib=CL_LIME_R, side='t', lab=L("Chiffre|d'affaires", f(v['ca']), ['+24 % sur 1 an'], CL_INK)),
     'mb': dict(x=X[3], y=620, v=v['mb'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L('Marge|brute', f(v['mb']), ['64 % des ventes'], CL_GREEN)),
     'cr': dict(x=X[3], y=1000, v=v['cr'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Coût des|ventes', p(v['cr']), [], CL_RED)),
     'ex': dict(x=X[4], y=620, v=v['ex'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L("Résultat|d'exploitation", f(v['ex']), ['30 % des ventes', '+66 % sur 1 an'], CL_GREEN)),
     'ch': dict(x=X[4], y=880, v=v['ch'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Charges', p(v['ch']), ['dont '+fmt(e(2.423))+' de', 'recherche'], CL_RED)),
     'rn': dict(x=X[5], y=600, v=v['rn'], c=CL_GREEN, rib=CL_GREEN_R, side='r', lab=L('Résultat|net', f(v['rn']), ['25 % des', 'ventes'], CL_GREEN, 23)),
     'im': dict(x=X[5], y=790, v=v['im'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Impôts et', p(v['im']), ['intérêts'], CL_RED, 21)),
    }
    links = [('re', 'pr', v['re']), ('se', 'pr', v['se']), ('co', 'pr', v['co']), ('ob', 'pr', v['ob']),
             ('pr', 'ca', v['pr'], CL_LIME_R), ('sv', 'ca', v['sv'], CL_TEAL_R),
             ('ca', 'mb', v['mb']), ('ca', 'cr', v['cr']), ('mb', 'ex', v['ex']), ('mb', 'ch', v['ch']),
             ('ex', 'rn', v['rn']), ('ex', 'im', v['im'])]
    flux(c, N, links, k)
    picto(cv, 'lan', 60, 430+v['re']*k/2-62, 40, CL_LIME); picto(cv, 'wrench-outline', 336+13, 1060+v['sv']*k+150, 42, CL_TEAL)
    picto(cv, 'flask-outline', 815, 880+v['ch']*k+150, 40, CL_RED)
    picto(cv, 'cash-multiple', 1030, 568, 36, CL_GREEN)
    source(c, "Source : Cisco, résultats du 12/11/2026", 1440, CX, 18); source(c, "(CA 18,5 Md$). 1 € = "+fmt(R, 4)+" $ (BCE, "+JOUR+").", 1462, CX, 18)
    text(c, "Mise en page inspirée de App Economy Insights (How They Make Money)", 600, 1488, 'sb', 17, CL_GREY, 'c')
    coin(cv, 'site_calculatrice', 115, 1450, 240)

# ---------- 5. rentabilité ----------
RN = [11.812, 12.613, 10.320, 10.180, 13.267]
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net (Md€) et marge nette, par exercice")
    carte(c, 40, 345, 1000, 545)
    graphique(c, [str(y) for y in range(2022, 2027)], [e(x) for x in RN], 80, 1000, 690, 430,
              courbe=[x/y*100 for x, y in zip(RN, CA)], cbase=860, ctop=790, couleur=CL_GREEN)
    text(c, "Marge nette", 80, 878, 'xb', 21, CL_TEAL, 'l')
    rangee(c, 905, [('ok', "BPA 2026", fmt(e(3.33), 2)+NB+"€", "(3,33 $)"), ('ok', "12 derniers mois", "+22,3" + NB + "%", "de marge"),
                    ('neutre', "PER ("+JOUR+")", fmt(PER, 1), "")])
    src(c, "Source : Cisco, 10-K et communiqués. BPA dilué. PER = cours ÷ bénéfice par action des 12 derniers mois.", 1030)
    pied(cv, c, "Sur 100 € de ventes, Cisco garde 21 € de bénéfice net. Le creux de 2024-2025 : des ventes en recul, "
         "puis le coût du rachat de Splunk (amortissements, intérêts de la dette).", 'reflechit', "21 € sur 100 €", 1060)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Bilan au 24/10/2026, flux sur 12 mois")
    carte(c, 40, 345, 1000, 625)
    famille(c, "BILAN", ['ko', 'ok'], 80, 385)
    tuile(c, 70, 410, 460, 'ko', "Dette", md(29.799), "surtout pour Splunk", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'ok', "Trésorerie", md(15.845), "cash et placements", fond='F5F3EE')
    famille(c, "ARGENT GÉNÉRÉ", ['ok', 'neutre'], 80, 535)
    tuile(c, 70, 560, 460, 'ok', "Flux de trésorerie libre", md(13.733), "sur 12 mois", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'neutre', "Dette nette", md(13.954), "≈ 1 an de flux libre", fond='F5F3EE')
    famille(c, "RENDU AUX ACTIONNAIRES", ['ok'], 80, 685)
    tuile(c, 70, 710, 940, 'ok', "Exercice 2026 : 99 % du flux de trésorerie libre", md(12.659), "("+md(6.553)+" de dividendes, "+md(6.106)+" de rachats)", fond='F5F3EE')
    for j, l in enumerate(["Dette nette = dettes − cash.", "Flux de trésorerie libre = l'argent qui reste après les investissements.",
                           "Rachat d'actions = chaque action restante pèse un peu plus."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Source : Cisco, communiqués du 12/08 et du 12/11/2026 ; 10-Q du 1er trimestre.", 1000)
    pied(cv, c, "Cisco s'est endettée pour racheter Splunk, mais un an de flux de trésorerie libre suffirait à rembourser sa dette nette. "
         "En attendant, elle rend presque tout ce qu'elle gagne à ses actionnaires.", 'site_tirelire', "Presque tout|est reversé !", 1030)

# ---------- 7. dividende ----------
DV = [1.13, 1.28, 1.38, 1.43, 1.47, 1.51, 1.55, 1.59, 1.63, 1.67]
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par année de versement, en euros")
    carte(c, 40, 345, 1000, 430)
    graphique(c, [str(2017+i)[2:] for i in range(10)], [e(x) for x in DV], 70, 1010, 700, 470, couleur=CL_GOLD,
              fmt_b=lambda v: fmt(v, 2), bw=66)
    text(c, "Années 2017 à 2026. Premier dividende en 2011.", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ok', "15 hausses d'affilée", "0,42 $", "par trimestre"), ('neutre', "Rendement ("+JOUR+")", fmt(DIV/P*100, 1)+NB+"%", "1,68 $ par an")])
    rangee(c, 901, [('ok', "Distribution", fmt(DIV/BPA_12M*100, 0)+NB+"%", "du bénéfice"), ('neutre', "Prochain versement", "20/01", "détachement le 04/01")])
    pied(cv, c, "Cisco relève son dividende chaque année depuis 2012 : +48 % depuis 2017. Il reste moins de la moitié de son bénéfice, "
         "le reste part surtout en rachats d'actions. Action américaine : compte-titres, pas de PEA.", 'etoiles', "15 hausses|d'affilée !", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "Douze derniers mois publiés par chacun")
    carte(c, 40, 345, 1000, 620)
    xs = [207, 540, 873]
    for x, (kk, w) in zip(xs, [('CSCO', 120), ('ANET', 230), ('HPE', 150)]): logo_plein(cv, kk, x-w/2, 405, w)   # logos des marques (retour du 25/11)
    text(c, "BÉNÉFICE NET POUR 100 € DE VENTES", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", ""], [22.3, 40.0, 6.4], 40, 1040, 700, 530, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 0)+NB+'€', bw=150)
    for lab, vals, cols_, y in [("CROISSANCE DU DERNIER TRIMESTRE", ["+24" + NB + "%", "+58" + NB + "%", "+34" + NB + "%"], [CL_GREEN]*3, 765),
                                ("CHIFFRE D'AFFAIRES SUR 12 MOIS", [md(66.959, 0), md(11.890, 0), md(41.870, 0)], [CL_INK]*3, 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, vv, cc in zip(xs, vals, cols_): text(c, vv, x, y+48, 'k', 40, cc, 'c')
    src(c, "Sources : résultats publiés. Derniers trimestres clos fin octobre (Cisco), fin septembre (Arista), fin juillet (HPE).", 995)
    src(c, "HPE (serveurs, stockage, réseau) a racheté Juniper en 2025.", 1019)
    pied(cv, c, "Arista, spécialiste des réseaux de centres de données, grandit plus vite et garde 40 € pour 100 € de ventes. "
         "Cisco reste le géant : six fois les ventes d'Arista.", 'haussement', "Arista court|plus vite !", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('cash-multiple', "Le dividende du 20 janvier", "0,42 $ par action, détachement le 4 janvier."),
                                     ('calendar-month-outline', "Les résultats de mi-février", "Prévision : 18,0 à 18,2 Md$ de ventes au trimestre."),
                                     ('server', "Les commandes liées à l'IA", "9 Md$ de ventes visées sur l'exercice, 2 fois plus qu'en 2026.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, tu préfères un dividende", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "qui monte ou une forte croissance ?", 540, 868, 'k', 46, CL_GOLD, 'c')
    text(c, "Dis-le en commentaire", 540, 935, 'sb', 30, CL_GREY, 'c'); put_emoji(cv, '👇', 540, 985, 44)
    rr(c, 160, 1040, 760, 70, 35); col(c, CL_NAVY); c.fill(); text(c, "ENREGISTRE-LE POUR LES PROCHAINS RÉSULTATS", 540, 1075, 'xb', 24, WHITE, 'c'); put_emoji(cv, '📌', 935, 1072, 38)
    carte(c, 300, 1150, 650, 200, 22); logo(cv, 'PROFIL', 390, 1250, 120)
    text(c, "ABONNE-TOI", 470, 1205, 'k', 40, CL_GOLD, 'l'); text(c, "à Actions_Benefices", 470, 1252, 'xb', 26, CL_INK, 'l')
    text(c, "la bourse sans jargon,", 470, 1290, 'sb', 23, CL_GREY, 'l'); text(c, "chaque semaine", 470, 1320, 'sb', 23, CL_GREY, 'l'); put_emoji(cv, '🔔', 905, 1195, 40)
    coin(cv, 'salut_chapeau', 150, 1440, 260)
    text(c, "Je détiens des actions Cisco.", 540, 1462, 'xb', 21, CL_INK, 'c')
    mention_pedago(c, 1490, CL_GREY, 1)

SLIDES = [s_cover, s_identite, s_croissance, s_flux, s_rentab, s_solid, s_div, s_rivaux, s_fin]
LOGOS |= {'PROFIL'}
NS = len(SLIDES)
def render(i):
    """deux calques : le dessin cairo dessous, les images (logos, pictogrammes, Mister Coin, émojis) dessus"""
    im = Image.new('RGBA', (W, H), 0); s, c = surface()
    SLIDES[i](im, c); cv = fond_clair(); cv.alpha_composite(to_img(s)); cv.alpha_composite(im); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
