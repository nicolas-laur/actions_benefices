"""Carrousel « Les News » du 20/11/2026 : l'actualité des marchés du lundi 16 au jeudi 19 novembre (chiffres arrêtés à la clôture du 19/11),
un sujet par diapo (le fait, la réaction chiffrée, une piste de lecture), fonds Gemini 1930 (fonds/), gabarit lib/carrousel.py.
Chiffres et sources : sources.md. usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *
LOGOS |= {'PROFIL', 'NVDA', 'ANTH', 'TTWO', 'US', 'FR'}                       # pas de logo libre pour Walmart et Home Depot : émoji

TOP = [("NVDA", "Nvidia : premiers résultats sans Huang"), ("ANTH", "Anthropic entre en bourse"), ("TTWO", "GTA 6 est sorti : et Take-Two ?"),
       ("🛒", "Walmart face à Home Depot"), ("US", "Wall Street sous les 50 000")]
def puce(cv, key, cx, cy, size):
    if key in LOGOS: logo(cv, key, cx, cy, size)
    else: put_emoji(cv, key, cx, cy, int(size*.8))
def s_cover(cv, c):
    text(c, "SEMAINE DU 16 AU 19 NOVEMBRE 2026", 540, 240, 'sb', 27, ICE, 'c', .85, 4)
    glow_text(cv, "LES NEWS", 540, 360, 170, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    gpill(c, "CE QUI A FAIT BOUGER LES MARCHÉS", 540, 500, GD, 34)
    n = len(TOP); rh = 84; ph = n*rh+14; y0 = 598
    def dr(k, w, h):
        for j, (e, s_) in enumerate(TOP):
            y = 7+rh*j+rh/2; text(k, s_, 110, y, 'xb', 31, WHITE, 'l', .97)
            if j: k.move_to(30, 7+rh*j); k.line_to(w-30, 7+rh*j); k.set_line_width(1.2); col(k, WHITE, .12); k.stroke()
    tp(cv, 880, ph, dr, 540, y0+ph/2, 'or', rx=.04, frost=14, dim=.62)   # verre plus clair (dim = luminosité conservée) : on devine le kiosque (19/11)
    for j, (e, s_) in enumerate(TOP): puce(cv, e, 540-440+62, y0+7+rh*j+rh/2, 56)
    bb = coin(cv, 'lit_journal_v2_titre', 255, 1512, 450); bulle_pres(c, "Extra, extra !|Tu as tout suivi ?", bb, 32, .26)  # au premier plan, pieds sur le trottoir
    text(c, "SWIPE", 920, 1420, 'xb', 28, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 965, 1418, 48)

# ---------- chiffres de clôture du 19/11 (sources.md) ; à confirmer vendredi matin : NV_SEM, TT_19, WM_19 ----------
R = 1.0992                                                                    # BCE, 19/11/2026 : 1 € = 1,0992 $
def eur(usd): return usd/R
NV_SEM, NV_SEM_SUB = "−7,6 %", "6 séances de baisse d'affilée"
TT_19, TT_19_SUB = "≈ −3,7 %", "le jour de la sortie"
WM_19, WM_19_SUB = "≈ −1 %", "malgré des prévisions relevées"
TXT = {
 'nvda_fait': f"Premiers résultats sans Jensen Huang : 105,4 Md€ de chiffre d'affaires (115,8 Md$), +103{NB}% en un an. Prévision : {fmt(eur(130))} Md€ au trimestre suivant.",
 'nvda_lect': f"Les chiffres rassurent ; l'export et la gouvernance inquiètent. Pour l'instant, le marché retient surtout les doutes.",
 'ant_fait': f"Entrée au Nasdaq jeudi sous le code ANT : 980 millions d'actions vendues à {fmt(eur(83), 2)} € (83 $), au-dessus de la fourchette prévue.",
 'ant_lect': f"Le premier jour mesure l'appétit des investisseurs, pas la valeur de l'entreprise. Prochain test : ses premiers résultats.",
 'gta_fait': f"GTA 6 est sorti jeudi. Selon Sensor Tower : 19,1 millions d'exemplaires et {fmt(eur(1.84), 2)} Md€ de recettes (1,84 Md$) dès le 1er jour, plus du double de GTA 5.",
 'gta_lect': f"« Vendre la nouvelle » : un succès attendu est souvent déjà dans le prix. Notre vidéo du 19/11 raconte pourquoi.",
 'wmt_fait': f"Walmart : {fmt(eur(188.8))} Md€ de chiffre d'affaires (+5,2{NB}%) et des prévisions relevées pour la 3e fois. Home Depot : {fmt(eur(43.4))} Md€ (+4,9{NB}%) et un nouveau patron le 23/11.",
 'wmt_lect': f"Quand une action est déjà chère, elle doit dépasser les attentes, pas seulement les atteindre.",
 'ws_fait': f"Jeudi, le Dow Jones a perdu 2,19{NB}% et repasse sous les 50{NB}000 points. Le S&P 500 aligne 6 baisses d'affilée, du jamais vu depuis 2024.",
 'ws_lect': f"Quand un placement sans risque rapporte plus de 5{NB}%, les actions les plus chères doivent justifier leur prix.",
}
def s_nvda(cv, c):
    sujet(cv, c, 1, 1, "NVIDIA", "DES RECORDS, PAS DE REBOND", TXT['nvda_fait'],
          [("RACHAT D'ACTIONS EN PLUS", f"{fmt(eur(150), 0)}{NB}Md€", "150 Md$", None, GR),
           ("L'ACTION, SUR LA SEMAINE", NV_SEM, NV_SEM_SUB, None, RD),
           ("PUCES : LICENCE D'EXPORT EXIGÉE", "5 pays", "dont Singapour et la Malaisie", None, OR)],
          'rouge', TXT['nvda_lect'], 'sceptique', "Records… et ça baisse ?", glow='FF5A3C', tsize=78, emo='NVDA', ch='auto')
def s_ant(cv, c):
    sujet(cv, c, 2, 2, "ANTHROPIC", "UN DÉBUT EN BOURSE RECORD", TXT['ant_fait'],
          [("ARGENT LEVÉ", f"{fmt(eur(81.3), 0)}{NB}Md€", "81,3 Md$, record mondial", None, GD),
           ("1ER JOUR, À LA CLÔTURE", "+17,1 %", f"{fmt(eur(97.17), 2)}{NB}€ (97,17 $)", None, GR),
           ("DEPUIS LA 1RE COTATION", "−12,9 %", "ouverture à 111,50 $", None, RD)],
          'or', TXT['ant_lect'], 'etoiles', "Quel départ !", tsize=82, emo='ANTH', ch='auto')
def s_gta(cv, c):
    sujet(cv, c, 3, 3, "TAKE-TWO", "GTA 6 CARTONNE, L'ACTION RECULE", TXT['gta_fait'],
          [("MERCREDI 18/11", "+6,2 %", "critiques : 99 sur 100", None, GR),
           ("JEUDI 19/11", TT_19, TT_19_SUB, None, RD),
           ("DEPUIS LE 1ER JANVIER", "≈ −15 %", None, None, RD)],
          'bleu', TXT['gta_lect'], 'haussement', "Déjà dans le prix ?", glow='35D6FF', tsize=70, emo='TTWO', ch='auto')
def s_wmt(cv, c):
    sujet(cv, c, 4, 4, "WALMART ET HOME DEPOT", "LES BONS ÉLÈVES PUNIS", TXT['wmt_fait'],
          [("WALMART, JEUDI 19/11", WM_19, WM_19_SUB, None, RD),
           ("HOME DEPOT, MARDI 17/11", "−2,45 %", f"{fmt(eur(339.01), 2)}{NB}€ (339,01 $)", None, RD)],
          'orange', TXT['wmt_lect'], 'reflechit', "Mieux, mais pas assez ?", tsize=80, emo='🛒', ch='auto')
def s_ws(cv, c):
    sujet(cv, c, 5, 5, "MARCHÉS", "UNE SEMAINE SOUS LA PLUIE", TXT['ws_fait'],
          [("DOW JONES, SUR LA SEMAINE", "−6,2 %", f"49{NB}097 pts, hors dividendes", None, RD),
           ("CAC 40, SUR LA SEMAINE", "−3,44 %", f"8{NB}080,74 pts, hors dividendes", None, RD),
           ("TAUX À 10 ANS US  /  BRENT", f"5,10{NB}%  /  93{NB}$", "hausse de la Fed attendue en décembre", None, OR)],
          'rouge', TXT['ws_lect'], 'sueur', "Ça secoue…", glow='35D6FF', tsize=78, emo='US', ch='auto')
def s_fin(cv, c):
    glow_text(cv, "ET TOI,", 540, 320, 124, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5)
    glow_text(cv, "QUELLE NEWS", 540, 455, 96, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "T'A SURPRIS ?", 540, 570, 104, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 690, 'sb', 34, ICE, 'c', .85); put_emoji(cv, '👇', 540, 745, 48)
    gpill(c, "ENREGISTRE-LE POUR LA SEMAINE PROCHAINE", 540, 840, GD, 30); put_emoji(cv, '📌', 540+375, 835, 40)
    bloc_abonne(cv, c, 1060); coin(cv, 'salut_chapeau', 540, 1505, 320); mention_pedago(c)

SLIDES = [s_cover, s_nvda, s_ant, s_gta, s_wmt, s_ws, s_fin]
FONDS = ['couverture', 'nvidia', 'anthropic', 'gta6', 'walmart', 'wallstreet', 'couverture']
NS = len(SLIDES)
def render(i):
    cv = fond(FONDS[i]).copy(); s, c = surface()
    SLIDES[i](cv, c); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
