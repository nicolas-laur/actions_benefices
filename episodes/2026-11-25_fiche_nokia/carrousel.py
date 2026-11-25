"""Fiche entreprise n°6 : « Que vaut Nokia ? » (cours : paramètres du jour ci-dessous), 9 diapos, thème clair, livrée en 4:5 seulement.
Modèle : episodes/2026-11-23_fiche_alphabet/carrousel.py (mêmes pieds, rangées et bulles). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

# ---------- paramètres du jour (seul bloc à changer pour mettre la fiche à jour ; voir sources.md, section 0) ----------
JOUR = "24/11"                    # date de clôture retenue
P = 6.662                         # clôture NOKIA (€), Nasdaq Helsinki
RECORD = 14.805                   # record de clôture (03/06/2026)
NA = 5598.644598                  # actions hors autodétention (M), Nokia, 30/06/2026
def e(x): return x                # montants déjà en euros
def md(x, d=1): return fmt(x, d)+NB+'Md€'
CAP = NA*P/1000                   # capitalisation (Md€)
CHUTE = round((P/RECORD-1)*100)   # variation depuis le record (%)
BPA_12M = 0.1397                  # bénéfice net des 12 derniers mois (782 M€, Stock Analysis) ÷ actions
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
    logo_plein(cv, 'NOKIA', 540-150, 330, 300)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "NOKIA ?", 540, 600, 'k', 128, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "Nvidia a vendu 56 % de ses actions", 540, 772, 'k', 46, CL_INK, 'c')
    text(c, fmt(CHUTE, 0).replace("-", "−")+NB+"% depuis le record de juin", 540, 846, 'k', 46, CL_RED, 'c')
    text(c, "L'IA a fait flamber l'action, puis l'a fait chuter.", 540, 914, 'sb', 27, CL_GREY, 'c')
    text(c, "Que disent vraiment ses comptes ?", 540, 952, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('trending-up', 'Croissance'), ('cash-multiple', 'Rentabilité'), ('bank', 'Dividende'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "On ouvre|les comptes !", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
ACT = [("Antennes mobiles (5G…)", 56.3, CL_TEAL), ("Réseaux fixes et optiques", 41.9, CL_NAVY), ("Autres activités", 1.9, 'BDBDBD')]
REG = [("Europe, Moyen-Orient, Afrique", 41.8, CL_TEAL), ("Amériques", 35.6, CL_NAVY), ("Asie-Pacifique", 22.7, '4F79A8')]
def barres_pct(c, rows, x, y, w, pas=74):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*pas; text(c, lab, x, yy, 'xb', 22, CL_INK, 'l'); text(c, fmt(p)+NB+'%', x+w, yy, 'k', 22, colr, 'r')
        rr(c, x, yy+18, w, 12, 6); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+18, max(w*p/100, 10), 12, 6); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Chiffre d'affaires du trimestre juillet-septembre 2026")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'NOKIA', 70, 450, 150)
    for j, l in enumerate(["Ne fait plus de téléphones depuis 2014 :", "elle équipe les réseaux des opérateurs", "et les centres de données (fibre, routeurs)."]):
        text(c, l, 250, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "PAR ACTIVITÉ", ['ok'], 80, 608); barres_pct(c, ACT, 80, 652, 420)
    famille(c, "PAR RÉGION", ['ok'], 580, 608); barres_pct(c, REG, 580, 652, 420)
    rangee(c, 905, [('neutre', "Cotée à", "Helsinki", "plus à Paris"), ('neutre', "Capitalisation", "≈"+NB+fmt(CAP, 0)+NB+"Md€"), ('ko', "Cours ("+JOUR+")", fmt(P, 2)+NB+"€")])
    src(c, "Source : Nokia, rapport du 3e trimestre 2026 (22/10/2026) ; cours NOKIA (Nasdaq Helsinki).", 1030)
    pied(cv, c, "Plus de la moitié des ventes vient encore des antennes 4G et 5G vendues aux opérateurs. Le reste, ce sont les réseaux "
         "en fibre et les routeurs, la partie qui profite de l'IA. Nokia a quitté la bourse de Paris fin 2025.", 'loupe', "Plus de téléphones !", 1060)

# ---------- 3. croissance : CA annuel ----------
CA = [22.202, 23.761, 21.138, 19.220, 19.889]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires annuel, en Md€")
    carte(c, 40, 345, 1000, 545)
    base = 770
    graphique(c, [str(2021+i) for i in range(5)], CA, 80, 1000, base, 470, couleur=CL_LIME, bw=120)
    gr = [None]+[t/p-1 for p, t in zip(CA, CA[1:])]; step = 920/5
    for i, gg in enumerate(gr):
        cx = 80+step*(i+.5)
        text(c, '–' if gg is None else ('+' if gg > 0 else '−')+fmt(abs(gg)*100, 0)+NB+'%', cx, base+62, 'xb', 21, CL_GREY if gg is None else (CL_GREEN if gg > 0 else CL_RED), 'c')
    text(c, "en petit : variation sur un an", 80, 868, 'sb', 18, CL_GREY, 'l')
    rangee(c, 905, [('ko', "Sur 4 ans", "−2,7" + NB + "%/an"), ('ok', "Dernier trimestre", "+9" + NB + "%", "à change constant"), ('ok', "Clients IA et cloud", "+123" + NB + "%")])
    src(c, "Source : Nokia, rapports annuels et trimestriels.", 1030)
    pied(cv, c, "Quatre ans de recul : les opérateurs ont freiné leurs achats d'antennes 5G. Depuis peu, ça repart grâce aux "
         "centres de données : les ventes aux clients de l'IA et du cloud ont plus que doublé sur un an au dernier trimestre.", 'court', "Ça repart ?", 1060)

# ---------- 4. d'où vient l'argent (flux du trimestre) ----------
def s_flux(cv, c):
    tt = "3e TRIMESTRE"; lw = 200; x_t = 540-(lw+24+tw(c, tt, 'k', 58))/2; text(c, tt, x_t+lw+24, 236, 'k', 58, CL_NAVY, 'l')
    logo_plein(cv, 'NOKIA', x_t, 236, lw)
    text(c, "D'où vient l'argent, où il va", 540, 300, 'xb', 34, CL_INK, 'c')
    text(c, "Juillet à septembre 2026, en milliards d'euros", 540, 346, 'sb', 24, CL_GREY, 'c')
    k = 89.0; X = [176, 336, 490, 646, 802, 900]
    v = dict(op=0.933, ip=0.839, fx=0.386, ni=2.158, mo=2.902, au=0.094, ca=5.154, mb=2.176, cr=2.979, ex=0.196, ch=1.980, rn=0.176, im=0.020)
    L = etiquette; f = lambda x: fmt(x, 2); p = lambda x: '('+f(x)+')'
    def lg(nom, val, colr, sz=21): return [(nom, 'xb', sz, colr), (val, 'k', sz+2, colr)]
    N = {
     'op': dict(x=X[0], y=460, v=v['op'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Optique', f(v['op']), ['+18 %'], CL_LIME)),
     'ip': dict(x=X[0], y=570, v=v['ip'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Routeurs IP', f(v['ip']), ['+43 %'], CL_LIME)),
     'fx': dict(x=X[0], y=680, v=v['fx'], c=CL_LIME, rib=CL_LIME_R, side='l', lab=L('Fixe', f(v['fx']), ['−22 %'], CL_LIME)),
     'ni': dict(x=X[1], y=520, v=v['ni'], c=CL_LIME, rib=CL_LIME_R, side='t', lab=L('Réseaux|fixes', fmt(v['ni']), ['+15 %'], CL_LIME)),
     'mo': dict(x=X[0], y=800, v=v['mo'], c=CL_TEAL, rib=CL_TEAL_R, side='l', lab=L('Antennes|mobiles', fmt(v['mo']), ['+5 %'], CL_TEAL)),
     'au': dict(x=X[0], y=1110, v=v['au'], c='9E9E9E', rib='DDDDDD', side='l', lab=lg('Autres', f(v['au']), CL_GREY)),
     'ca': dict(x=X[2], y=640, v=v['ca'], c=CL_INK, rib=CL_LIME_R, side='t', lab=L("Chiffre|d'affaires", fmt(v['ca']), ['+10 % sur 1 an'], CL_INK)),
     'mb': dict(x=X[3], y=600, v=v['mb'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L('Marge|brute', fmt(v['mb']), ['42 % des ventes'], CL_GREEN)),
     'cr': dict(x=X[3], y=860, v=v['cr'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Coût des|ventes', p(v['cr']), [], CL_RED)),
     'ex': dict(x=X[4], y=560, v=v['ex'], c=CL_GREEN, rib=CL_GREEN_R, side='t', lab=L("Résultat|d'exploitation", f(v['ex']), ['4 % des ventes'], CL_GREEN)),
     'ch': dict(x=X[4], y=660, v=v['ch'], c=CL_RED, rib=CL_RED_R, side='b', lab=L('Charges', p(v['ch']), ['dont 1,25 de recherche', 'et 0,36 de restructuration'], CL_RED)),
     'rn': dict(x=X[5], y=520, v=v['rn'], c=CL_GREEN, rib=CL_GREEN_R, side='r', lab=L('Résultat|net', f(v['rn']), [], CL_GREEN, 23)),
     'im': dict(x=X[5], y=720, v=v['im'], c=CL_RED, rib=CL_RED_R, side='r', lab=L('Impôts', p(v['im']), ['nets des', 'produits', 'financiers'], CL_RED, 21)),
    }
    links = [('op', 'ni', v['op']), ('ip', 'ni', v['ip']), ('fx', 'ni', v['fx']),
             ('ni', 'ca', v['ni'], CL_LIME_R), ('mo', 'ca', v['mo'], CL_TEAL_R), ('au', 'ca', v['au'], 'DDDDDD'),
             ('ca', 'mb', v['mb']), ('ca', 'cr', v['cr']), ('mb', 'ex', v['ex']), ('mb', 'ch', v['ch']),
             ('ex', 'rn', v['rn']), ('ex', 'im', v['im'])]
    flux(c, N, links, k)
    picto(cv, 'access-point-network', 60, 800+v['mo']*k/2-75, 40, CL_TEAL); picto(cv, 'lan', 60, 460-40, 36, CL_LIME)
    source(c, "Source : Nokia, rapport du 22/10/2026", 1440, CX, 18); source(c, "(chiffres publiés, croissance à change constant).", 1462, CX, 18)
    text(c, "Mise en page inspirée de App Economy Insights (How They Make Money)", 600, 1488, 'sb', 17, CL_GREY, 'c')
    coin(cv, 'site_calculatrice', 115, 1450, 240)

# ---------- 5. rentabilité ----------
RN = [1623, 4250, 665, 1277, 651]
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net (M€) et marge nette, par année")
    carte(c, 40, 345, 1000, 545)
    graphique(c, [str(y) for y in range(2021, 2026)], RN, 80, 1000, 690, 430, courbe=[x/y/10 for x, y in zip(RN, CA)], cbase=862, ctop=800,
              couleur=CL_GREEN, fmt_b=lambda v: fmt(v, 0))
    text(c, "Marge nette", 1000, 878, 'xb', 21, CL_TEAL, 'r')
    rangee(c, 905, [('neutre', "Marge d'exploitation", "3,8" + NB + "%", "11,7 % hors restructurations"), ('ko', "PER ("+JOUR+")", fmt(P/BPA_12M, 0), "bénéfice des 12 derniers mois")])
    src(c, "Source : Nokia, rapports annuels ; Stock Analysis (bénéfice des 12 derniers mois : 782 M€). Résultat net part du groupe.", 1030)
    pied(cv, c, "Nokia garde 3 à 7 € de bénéfice pour 100 € de ventes. Le pic de 2022 est un effet comptable : 2,5 Md€ d'impôts "
         "futurs déductibles inscrits au bilan. En 2026, les plans de départs pèsent encore : 1,1 Md€ prévus sur l'année.", 'sceptique', "Pas très|rentable…", 1060)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Bilan au 30/09/2026")
    carte(c, 40, 345, 1000, 625)
    famille(c, "BILAN", ['ok', 'ok'], 80, 385)
    tuile(c, 70, 410, 460, 'ok', "Trésorerie nette", "+"+md(2.584), "plus de cash que de dettes", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'ok', "Cash et placements", md(5.0, 1), "au total", fond='F5F3EE')
    famille(c, "ARGENT GÉNÉRÉ", ['ko', 'ok'], 80, 535)
    tuile(c, 70, 560, 460, 'ko', "Flux de trésorerie libre", "−0,2" + NB + "Md€", "en 9 mois", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'ok', "Sur l'année 2025", "+"+md(1.465), "", fond='F5F3EE')
    famille(c, "CE QUI PÈSE EN 2026", ['ko'], 80, 685)
    tuile(c, 70, 710, 940, 'ko', "Charges de restructuration prévues en 2026", "1,1" + NB + "Md€", "sur l'année", fond='F5F3EE')
    for j, l in enumerate(["Trésorerie nette = cash − dettes.", "Flux de trésorerie libre = l'argent qui reste après les investissements.",
                           "Restructuration = départs, fermetures, intégration d'Infinera."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Source : Nokia, rapport du 22/10/2026 et rapport annuel 2025.", 1000)
    pied(cv, c, "Pas de souci de dette : Nokia a plus de cash que d'emprunts. Mais sa réorganisation coûte cher cette année "
         "et le cash généré est négatif sur neuf mois.", 'site_tirelire', "Le cash|recule", 1030)

# ---------- 7. dividende ----------
DV = [0, 0.06, 0.11, 0.13, 0.14, 0.14]
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par année de versement, en euros")
    carte(c, 40, 345, 1000, 430)
    graphique(c, [str(2021+i) for i in range(6)], DV, 90, 990, 700, 470, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 2) if v else "0", bw=100)
    text(c, "Versé en 4 fois par an. Suspendu fin 2019, repris en 2022.", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ok', "Hausse depuis 2022", "0,06 → 0,14 €", ""), ('neutre', "Rendement ("+JOUR+")", fmt(0.14/P*100, 1)+NB+"%", "0,14 € par an")])
    rangee(c, 901, [('ko', "Distribution", "> 100" + NB + "%", "du bénéfice 2025"), ('neutre', "Prochain versement", "Février", "0,03 € au plus")])
    pied(cv, c, "Le dividende remonte depuis 2022, mais Nokia verse plus que son bénéfice de 2025 (environ 0,12 € par action) : "
         "il puise dans sa trésorerie. Action finlandaise : impôt retenu en Finlande, récupérable en partie.", 'etoiles', "2,1 %|de rendement", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "Trimestre juillet-septembre 2026 (août-octobre pour Cisco)")
    carte(c, 40, 345, 1000, 620)
    xs = [207, 540, 873]
    logo_plein(cv, 'NOKIA', xs[0]-90, 408, 180); logo_plein(cv, 'ERIC', xs[1]-95, 408, 34); text(c, "ERICSSON", xs[1]-50, 408, 'k', 34, '0082F0', 'l')
    logo_plein(cv, 'CSCO', xs[2]-60, 408, 120)
    text(c, "CHIFFRE D'AFFAIRES DU TRIMESTRE (MD€)", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", ""], [5.154, 59.478/11.221, 18.517/1.0963], 40, 1040, 700, 530, couleur=CL_GOLD, fmt_b=lambda v: fmt(v), bw=150)
    for lab, vals, cols_, y in [("CROISSANCE SUR UN AN", ["+9" + NB + "%", "+7" + NB + "%", "+24" + NB + "%"], [CL_GREEN]*3, 765),
                                ("MARGE D'EXPLOITATION PUBLIÉE", ["3,8" + NB + "%", "14,9" + NB + "%", "30,2" + NB + "%"], [CL_INK]*3, 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, vv, cc in zip(xs, vals, cols_): text(c, vv, x, y+48, 'k', 40, cc, 'c')
    src(c, "Croissance à change constant (Nokia, Ericsson), publiée (Cisco). Taux BCE du 24/11 : 1 € = 11,221 SEK ; 1 € = 1,0963 $.", 995)
    src(c, "Nokia : 11,7 % de marge hors restructurations. Sources : résultats publiés.", 1019)
    pied(cv, c, "Face à Ericsson, son jumeau suédois, Nokia vend autant mais gagne beaucoup moins ce trimestre, plombé par ses restructurations. "
         "Cisco, déjà passé en fiche, est trois fois plus gros.", 'site_longue_vue', "Même taille|qu'Ericsson", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('server', "Les commandes liées à l'IA", "1,5 Md€ de commandes IA et cloud au dernier trimestre."),
                                     ('calendar-month-outline', "Les résultats annuels, début 2027", "Objectif 2026 : 2,1 à 2,6 Md€ de résultat (hors restructurations)."),
                                     ('account-group-outline', "Les ventes d'actions de Nvidia", "Il lui en restait 72,9 millions fin septembre.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, tu crois plus à Nokia", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "côté 5G ou côté IA ?", 540, 868, 'k', 46, CL_GOLD, 'c')
    text(c, "Dis-le en commentaire", 540, 935, 'sb', 30, CL_GREY, 'c'); put_emoji(cv, '👇', 540, 985, 44)
    rr(c, 160, 1040, 760, 70, 35); col(c, CL_NAVY); c.fill(); text(c, "ENREGISTRE-LE POUR LES PROCHAINS RÉSULTATS", 540, 1075, 'xb', 24, WHITE, 'c'); put_emoji(cv, '📌', 935, 1072, 38)
    carte(c, 300, 1150, 650, 200, 22); logo(cv, 'PROFIL', 390, 1250, 120)
    text(c, "ABONNE-TOI", 470, 1205, 'k', 40, CL_GOLD, 'l'); text(c, "à Actions_Benefices", 470, 1252, 'xb', 26, CL_INK, 'l')
    text(c, "la bourse sans jargon,", 470, 1290, 'sb', 23, CL_GREY, 'l'); text(c, "chaque semaine", 470, 1320, 'sb', 23, CL_GREY, 'l'); put_emoji(cv, '🔔', 905, 1195, 40)
    coin(cv, 'salut_chapeau', 150, 1440, 260)
    text(c, "Je détiens des actions Nokia.", 540, 1462, 'xb', 21, CL_INK, 'c')
    mention_pedago(c, 1490, CL_GREY, 1)

SLIDES = [s_cover, s_identite, s_croissance, s_flux, s_rentab, s_solid, s_div, s_rivaux, s_fin]
LOGOS |= {'PROFIL'}
NS = len(SLIDES)
def render(i):
    """deux calques : le dessin cairo dessous, les images (logos, pictogrammes, Mister Coin, émojis) dessus"""
    im = Image.new('RGBA', (W, H), 0); s, c = surface()
    SLIDES[i](im, c); cv = fond_clair(); cv.alpha_composite(to_img(s)); cv.alpha_composite(im); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
