"""Carrousel « Les News » du 20/11/2026 : l'actualité des marchés du lundi 16 au jeudi 19 novembre (chiffres arrêtés à la clôture du 19/11),
un sujet par diapo (le fait, la réaction chiffrée, une piste de lecture), fonds Gemini 1930 (fonds/), gabarit lib/carrousel.py.
Chiffres et sources : sources.md. usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *
LOGOS |= {'PROFIL', 'NVDA', 'ANTH', 'TTWO', 'US', 'FR'}                       # pas de logo libre pour Walmart et Home Depot : émoji

TOP = [("NVDA", "Nvidia : premiers résultats sans Huang"), ("ANTH", "Anthropic entre en bourse"), ("TTWO", "GTA 6 est sorti : et Take-Two ?"),
       ("🛒", "Walmart face à Home Depot"), ("US", "Wall Street secouée, et Paris ?")]
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

SLIDES = [s_cover]
FONDS = ['couverture']
NS = len(SLIDES)
def render(i):
    cv = fond(FONDS[i]).copy(); s, c = surface()
    SLIDES[i](cv, c); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
