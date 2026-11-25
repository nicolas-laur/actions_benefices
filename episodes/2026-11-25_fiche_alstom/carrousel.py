"""Fiche entreprise n°5 : « Que vaut Alstom ? » (cours : paramètres du jour ci-dessous), 9 diapos, thème clair, livrée en 4:5 seulement.
Modèle : episodes/2026-11-23_fiche_alphabet/carrousel.py (mêmes pieds, rangées et bulles). Chiffres et formules : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *

# ---------- paramètres du jour (seul bloc à changer pour mettre la fiche à jour ; voir sources.md, section 0) ----------
JOUR = "24/11"                    # date de clôture retenue
P = 8.648                         # clôture ALO (€), Euronext Paris
P_MOIS = 15.915                   # clôture du 22/10/2026 (un mois plus tôt)
NA = 462.616024                   # actions (M), ABC Bourse
def e(x): return x                # montants déjà en euros
def md(x, d=1): return fmt(x, d)+NB+'Md€'
CAP = NA*P/1000                   # capitalisation (Md€)
CHUTE = round((P/P_MOIS-1)*100)   # variation sur un mois (%)
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
    logo_plein(cv, 'ALO', 540-170, 330, 340)
    text(c, "QUE VAUT", 540, 470, 'k', 128, CL_INK, 'c'); text(c, "ALSTOM ?", 540, 600, 'k', 128, CL_GOLD, 'c')
    carte(c, 90, 700, 900, 300)
    text(c, "111 Md€ de commandes", 540, 772, 'k', 62, CL_GREEN, 'c')
    text(c, "et pourtant "+fmt(CHUTE, 0).replace("-", "−")+NB+"% en un mois", 540, 846, 'k', 46, CL_RED, 'c')
    text(c, "Au plus bas depuis 5 ans.", 540, 914, 'sb', 27, CL_GREY, 'c')
    text(c, "Que disent vraiment ses comptes ?", 540, 952, 'sb', 27, CL_GREY, 'c')
    for j, (pc, t) in enumerate([('trending-up', 'Croissance'), ('alert-outline', 'La perte'), ('bank', 'Solidité'), ('account-group-outline', 'Rivaux')]):
        x = 180+j*240; picto(cv, pc, x, 1080, 54, CL_TEAL); text(c, t, x, 1135, 'xb', 24, CL_INK, 'c')
    bb = coin(cv, 'lit_journal_v2_titre', 250, 1500, 400); bulle_pres(c, "On ouvre|les comptes !", bb, 30, .28, bg=CL_NAVY, fg=WHITE)
    text(c, "SWIPE", 905, 1440, 'xb', 28, CL_INK, 'r', .8, 4); put_emoji(cv, '👉', 935, 1438, 44)

# ---------- 2. carte d'identité ----------
ACT = [("Trains et métros", 51.6, CL_TEAL), ("Services (maintenance…)", 25.9, CL_TEAL), ("Signalisation", 13.6, CL_NAVY), ("Systèmes clés en main", 8.9, '4F79A8')]
REG = [("Europe", 62.3, CL_TEAL), ("Amériques", 15.1, CL_NAVY), ("Asie-Pacifique", 13.0, '4F79A8'), ("Afrique, Moyen-Orient", 9.6, 'BDBDBD')]
def barres_pct(c, rows, x, y, w, pas=58):
    for j, (lab, p, colr) in enumerate(rows):
        yy = y+j*pas; text(c, lab, x, yy, 'xb', 22, CL_INK, 'l'); text(c, fmt(p)+NB+'%', x+w, yy, 'k', 22, colr, 'r')
        rr(c, x, yy+18, w, 12, 6); col(c, 'EEEBE4'); c.fill(); rr(c, x, yy+18, max(w*p/100, 10), 12, 6); col(c, colr); c.fill()
def s_identite(cv, c):
    titre_clair(c, "CARTE", "D'IDENTITÉ", "Chiffre d'affaires du semestre avril-septembre 2026")
    carte(c, 40, 350, 1000, 200)
    logo_plein(cv, 'ALO', 70, 450, 150)
    for j, l in enumerate(["Construit TGV, métros, tramways", "et trains régionaux, les entretient", "et installe leur signalisation."]):
        text(c, l, 250, 400+j*50, 'sb', 28, CL_INK, 'l')
    carte(c, 40, 570, 1000, 315)
    famille(c, "PAR ACTIVITÉ", ['ok'], 80, 608); barres_pct(c, ACT, 80, 652, 420)
    famille(c, "PAR RÉGION", ['ok'], 580, 608); barres_pct(c, REG, 580, 652, 420)
    rangee(c, 905, [('neutre', "Salariés", "87 800", "61 pays"), ('neutre', "Capitalisation", "≈"+NB+fmt(CAP, 1)+NB+"Md€"), ('ko', "Cours ("+JOUR+")", fmt(P, 2)+NB+"€")])
    src(c, "Source : Alstom, résultats semestriels du 17/11/2026 ; cours ALO (Euronext Paris).", 1030)
    pied(cv, c, "Un peu plus de la moitié des ventes vient de la fabrication de trains, un quart de leur entretien. "
         "Six euros sur dix sont réalisés en Europe. Ses clients : surtout des États et des opérateurs publics.", 'loupe', "Du TGV au tram !", 1060)

# ---------- 3. croissance : CA annuel ----------
CA = [15.471, 16.507, 17.619, 18.489, 19.171]
def s_croissance(cv, c):
    titre_clair(c, "LA", "CROISSANCE", "Chiffre d'affaires par exercice (clos fin mars), en Md€")
    carte(c, 40, 345, 1000, 545)
    base = 770
    graphique(c, ["21/22", "22/23", "23/24", "24/25", "25/26"], CA, 80, 1000, base, 470, couleur=CL_LIME, bw=120)
    gr = [None]+[t/p-1 for p, t in zip(CA, CA[1:])]; step = 920/5
    for i, gg in enumerate(gr):
        cx = 80+step*(i+.5)
        text(c, '–' if gg is None else ('+' if gg > 0 else '−')+fmt(abs(gg)*100, 0)+NB+'%', cx, base+62, 'xb', 21, CL_GREY if gg is None else (CL_GREEN if gg > 0 else CL_RED), 'c')
    text(c, "en petit : variation sur un an", 80, 868, 'sb', 18, CL_GREY, 'l')
    rangee(c, 905, [('ok', "Sur 4 ans", "+5,5" + NB + "%/an"), ('neutre', "Dernier semestre", "+3" + NB + "%"), ('ok', "Carnet de commandes", "111" + NB + "Md€", "≈ 6 ans")])
    src(c, "Source : Alstom, communiqués annuels et semestriels. Exercice 2025/26 = avril 2025 à mars 2026.", 1030)
    pied(cv, c, "Les ventes montent chaque année et les commandes en attente représentent près de 6 ans de chiffre d'affaires. "
         "Le problème d'Alstom n'est pas de vendre : c'est de livrer à temps et au bon coût.", 'reflechit', "Des commandes,|il y en a !", 1060)

# ---------- 4. avant / après (même semestre, deux années) : piste A validée le 25/11, la cascade était illisible ----------
AVAP = [("Chiffre d'affaires", 9059, 9330, "+3" + NB + "%"), ("Résultat d'exploitation", 580, -396, "−976" + NB + "M€"), ("Résultat net", 220, -954, "−1" + NB + "174" + NB + "M€")]
def s_avap(cv, c):
    titre_clair(c, "AVANT /", "APRÈS", "Avril à septembre : 2025 contre 2026, en millions d'euros")
    carte(c, 40, 345, 1000, 540)
    for b, (lab, a, n, var) in enumerate(AVAP):
        y = 385+b*170
        text(c, lab.upper(), 80, y, 'xb', 22, CL_GREY, 'l', 1, 3)
        text(c, var, 1000, y, 'k', 26, CL_GREEN if var.startswith('+') else CL_RED, 'r')
        neg = min(a, n) < 0; ax = 620 if neg else 160; L = 370/954 if neg else 700/max(a, n)    # même échelle pour les deux résultats
        for k_, (an, v) in enumerate((("2025", a), ("2026", n))):
            yy = y+40+k_*56; w = abs(v)*L
            colr = ('9BC98F' if k_ == 0 else CL_GREEN) if v >= 0 else CL_RED
            x = ax if v >= 0 else ax-w
            rr(c, x, yy, max(w, 4), 40, 8); col(c, colr); c.fill()
            sv = ('+' if v > 0 and neg else ('−' if v < 0 else ''))+fmt(abs(v), 0)
            if v >= 0: text(c, sv, x+w+14, yy+20, 'k', 26, CL_INK, 'l')
            else: text(c, sv, x+14, yy+20, 'k', 26, WHITE, 'l')                                # valeur dans la barre rouge
            text(c, an, 80 if not neg else 80, yy+20, 'sb', 22, CL_GREY, 'l')
        if neg: c.move_to(ax, y+30); c.line_to(ax, y+146); col(c, CL_INK, .5); c.set_line_width(2); c.stroke()
    rangee(c, 905, [('ko', "Coradia Max", "Marges", "revues"), ('ko', "Production", "Arrêtée", "au 1er trim."), ('ko', "Impôts", "−100" + NB + "M€", "dépréciés")])
    src(c, "Source : Alstom, résultats du 17/11/2026. Résultat d'exploitation ajusté ; résultat net part du groupe.", 1030)
    pied(cv, c, "Les ventes progressent encore, mais les profits s'effondrent : en Allemagne, les trains régionaux Coradia Max "
         "accumulent les retards de fabrication et d'homologation, et Alstom a revu à la baisse la marge de ces contrats.", 'sueur', "Aïe, l'Allemagne…", 1060)

# ---------- 5. rentabilité ----------
RN = [-581, -132, -309, 149, 324]
def s_rentab(cv, c):
    titre_clair(c, "LA", "RENTABILITÉ", "Résultat net (M€) et marge nette, par exercice")
    carte(c, 40, 345, 1000, 545)
    graphique(c, [""]*5, RN, 80, 1000, 690, 450, courbe=[x/y/10 for x, y in zip(RN, CA)], cbase=862, ctop=800,
              couleur=CL_GREEN, fmt_b=lambda v: ('+' if v > 0 else '−')+fmt(abs(v), 0), fmt_c=lambda v: fmt(v, 1).replace('-', '−')+NB+'%')
    for i, l in enumerate(["21/22", "22/23", "23/24", "24/25", "25/26"]): text(c, l, 80+184*(i+.5), 752, 'sb', 22, CL_GREY, 'c')
    text(c, "Marge nette", 1000, 878, 'xb', 21, CL_TEAL, 'r')
    rangee(c, 905, [('ko', "Semestre avril-sept. 2026", "−954 M€", "perte nette"), ('ko', "Marge d'exploitation", "−4,2" + NB + "%", "contre +6,4 %")])
    src(c, "Source : Alstom, communiqués ; ABC Bourse (exercices 2021/22 à 2023/24). Résultat net part du groupe.", 1030)
    pied(cv, c, "Même dans ses bonnes années, Alstom garde moins de 2 € de bénéfice pour 100 € de ventes. "
         "Le semestre d'avril à septembre efface deux fois les bénéfices des deux derniers exercices (473 M€).", 'sceptique', "Moins de 2 €|sur 100 €", 1060)

# ---------- 6. solidité ----------
def s_solid(cv, c):
    titre_clair(c, "LA", "SOLIDITÉ", "Bilan au 30/09/2026, flux du semestre")
    carte(c, 40, 345, 1000, 625)
    famille(c, "BILAN", ['ko', 'ok'], 80, 385)
    tuile(c, 70, 410, 460, 'ko', "Dette nette", md(1.104), "0,4 fin mars", fond='F5F3EE')
    tuile(c, 550, 410, 460, 'ok', "Lignes de crédit", md(6.25, 2), "non utilisées", fond='F5F3EE')
    famille(c, "ARGENT GÉNÉRÉ", ['ko', 'ko'], 80, 535)
    tuile(c, 70, 560, 460, 'ko', "Flux de trésorerie libre", "−"+md(1.248), "en 6 mois", fond='F5F3EE')
    tuile(c, 550, 560, 460, 'ko', "Objectif sur l'exercice", "−"+md(1.5), "", fond='F5F3EE')
    famille(c, "PLAN ANNONCÉ", ['neutre'], 80, 685)
    tuile(c, 70, 710, 940, 'neutre', "Réduire la dette d'environ 2 Md€ d'ici septembre 2027", "Options :", "cessions, levée de capitaux…", fond='F5F3EE')
    for j, l in enumerate(["Dette nette = dettes − cash.", "Flux de trésorerie libre = l'argent qui reste après les investissements.",
                           "Note Baa3 (Moody's) : le dernier cran de la « bonne » catégorie."]):
        text(c, l, 80, 855+j*40, 'sb', 23, CL_GREY, 'l')
    src(c, "Source : Alstom, résultats du 17/11/2026 ; note confirmée par Moody's le 09/11/2026.", 1000)
    pied(cv, c, "Alstom brûle du cash : 1,2 Md€ en six mois. Sa dette reste modeste, mais il veut la réduire de 2 Md€ "
         "pour garder sa note, quitte à vendre des activités ou à lever de l'argent auprès des actionnaires.", 'haussement', "Il faut|du cash !", 1030)

# ---------- 7. dividende ----------
DV = [0.25, 0.25, 0.25, 0, 0, 0]
def s_div(cv, c):
    titre_clair(c, "LE", "DIVIDENDE", "Par action et par année de versement, en euros")
    carte(c, 40, 345, 1000, 430)
    graphique(c, [str(2021+i) for i in range(6)], DV, 90, 990, 700, 520, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 2) if v else "0", bw=100)
    text(c, "Payé en espèces ou en actions, au choix de l'actionnaire.", 70, 752, 'sb', 18, CL_GREY, 'l')
    rangee(c, 795, [('ko', "Dernier dividende", "0,25 €", "juillet 2023"), ('ko', "Exercice 2025/26", "Aucun", "dividende")])
    rangee(c, 901, [('neutre', "Rendement ("+JOUR+")", "0" + NB + "%", ""), ('ok', "Action française", "PEA", "éligible")])
    pied(cv, c, "Plus de dividende depuis 2023 : Alstom garde son cash pour réduire sa dette. Une levée d'argent auprès des actionnaires "
         "fait partie des pistes étudiées : elle diviserait le bénéfice entre plus d'actions.", 'site_parapluie', "Rien depuis|2023", 1030)

# ---------- 8. face à ses rivaux ----------
def s_rivaux(cv, c):
    titre_clair(c, "FACE À SES", "RIVAUX", "Dernières périodes publiées par chacun")
    carte(c, 40, 345, 1000, 620)
    xs = [207, 540, 873]
    for x, (kk, w) in zip(xs, [('ALO', 210), ('SIE', 220), ('SRAIL', 240)]): logo_plein(cv, kk, x-w/2, 408, w)
    text(c, "CARNET DE COMMANDES (MD€)", 80, 470, 'xb', 21, CL_GREY, 'l', 1, 3)
    graphique(c, ["", "", ""], [111, 65, 36.3], 40, 1040, 700, 530, couleur=CL_GOLD, fmt_b=lambda v: fmt(v, 0), bw=150)
    for lab, vals, cols_, y in [("CROISSANCE DES VENTES", ["+3" + NB + "%", "+4" + NB + "%", "+40" + NB + "%"], [CL_GREEN]*3, 765),
                                ("MARGE D'EXPLOITATION", ["−4,2" + NB + "%", "8,5" + NB + "%", "4,0" + NB + "%"], [CL_RED, CL_INK, CL_INK], 865)]:
        text(c, lab, 80, y, 'xb', 21, CL_GREY, 'l', 1, 3)
        for x, vv, cc in zip(xs, vals, cols_): text(c, vv, x, y+48, 'k', 40, cc, 'c')
    src(c, "Alstom : semestre avril-sept. 2026 ; Siemens Mobility : exercice clos le 30/09/2026 ; Stadler : 1er semestre 2026.", 995)
    src(c, "Stadler : 33,3 Md CHF convertis au taux BCE du 24/11 (1 € = 0,9183 CHF).", 1019)
    pied(cv, c, "Alstom a le plus gros carnet de commandes des trois, mais c'est le seul des trois à perdre de l'argent ce semestre. "
         "Siemens Mobility gagne 8,50 € pour 100 € de ventes.", 'site_longue_vue', "Les voisins|s'en sortent", 1050)

# ---------- 9. ce qu'il faut surveiller ----------
def s_fin(cv, c):
    titre_clair(c, "CE QU'IL FAUT", "SURVEILLER", None)
    carte(c, 40, 320, 1000, 420)
    for j, (pc, t, s_) in enumerate([('alert-outline', "Les décisions d'ici fin 2026", "Organisation, ventes d'activités, levée d'argent ?"),
                                     ('calendar-month-outline', "Le 19 janvier", "Commandes et ventes du trimestre octobre-décembre."),
                                     ('train', "Le 12 mai", "Résultats annuels : objectif de marge d'environ 1 %.")]):
        y = 400+j*120; picto(cv, pc, 110, y+6, 50, CL_TEAL); text(c, t, 160, y-10, 'xb', 31, CL_INK, 'l'); text(c, s_, 160, y+30, 'sb', 24, CL_GREY, 'l')
    text(c, "Et toi, tu regardes d'abord", 540, 810, 'k', 46, CL_INK, 'c'); text(c, "le carnet ou la marge ?", 540, 868, 'k', 46, CL_GOLD, 'c')
    text(c, "Dis-le en commentaire", 540, 935, 'sb', 30, CL_GREY, 'c'); put_emoji(cv, '👇', 540, 985, 44)
    rr(c, 160, 1040, 760, 70, 35); col(c, CL_NAVY); c.fill(); text(c, "ENREGISTRE-LE POUR LES PROCHAINS RÉSULTATS", 540, 1075, 'xb', 24, WHITE, 'c'); put_emoji(cv, '📌', 935, 1072, 38)
    carte(c, 300, 1150, 650, 200, 22); logo(cv, 'PROFIL', 390, 1250, 120)
    text(c, "ABONNE-TOI", 470, 1205, 'k', 40, CL_GOLD, 'l'); text(c, "à Actions_Benefices", 470, 1252, 'xb', 26, CL_INK, 'l')
    text(c, "la bourse sans jargon,", 470, 1290, 'sb', 23, CL_GREY, 'l'); text(c, "chaque semaine", 470, 1320, 'sb', 23, CL_GREY, 'l'); put_emoji(cv, '🔔', 905, 1195, 40)
    coin(cv, 'salut_chapeau', 150, 1440, 260)
    text(c, "Je détiens des actions Alstom.", 540, 1462, 'xb', 21, CL_INK, 'c')
    mention_pedago(c, 1490, CL_GREY, 1)

SLIDES = [s_cover, s_identite, s_croissance, s_avap, s_rentab, s_solid, s_div, s_rivaux, s_fin]
LOGOS |= {'PROFIL'}
NS = len(SLIDES)
def render(i):
    """deux calques : le dessin cairo dessous, les images (logos, pictogrammes, Mister Coin, émojis) dessus"""
    im = Image.new('RGBA', (W, H), 0); s, c = surface()
    SLIDES[i](im, c); cv = fond_clair(); cv.alpha_composite(to_img(s)); cv.alpha_composite(im); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
