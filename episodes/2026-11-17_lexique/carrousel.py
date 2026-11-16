"""Carrousel lexique du 17/11/2026 : « 9 sigles de la bourse… et un piège » (PEA, CTO, ETF, MSCI World, DCA, PER x2, PFU, IPO, BCE),
une fiche par sigle (sigle, développé, explication, exemple), fonds = décors 1930 des vidéos récentes (affinés), Mister Coin sur chaque fiche.
Même format que Les News (toile 1080×1920, contenu dans y = 200…1500, version Instagram 4:5 découpée en y = 175…1525).
usage : python3 carrousel.py [planche]"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *
LOGOS |= {'PROFIL'}

# ---------- fiches ----------
FICHES = [  # (sigle, développé, explication, exemple, emoji de l'exemple, pose, bulle, fond, couleur du halo)
 ("PEA", "Plan d'épargne en actions", "Une enveloppe pour investir en actions européennes et en ETF éligibles, avec moins d'impôts après 5 ans.",
  f"Jusqu'à 150{NB}000{NB}€ de versements. Après 5 ans, plus d'impôt sur le revenu sur tes gains.", '🇫🇷', 'pouce', "Mon préféré !", 'banque', 'FFB020'),
 ("CTO", "Compte-titres ordinaire", "Le compte sans limite : toutes les actions du monde, pas de plafond… mais aucun avantage fiscal.",
  "Tes gains y sont taxés au PFU (voir plus loin).", '🌍', 'montre', "Direction le monde !", 'gare', 'FFB020'),
 ("ETF", "Fonds indiciel coté (« tracker »)", "Un panier d'entreprises que tu achètes en un seul clic. Il copie un indice, avec des frais très bas.",
  f"Un ETF MSCI World : environ 1{NB}250 entreprises d'un coup.", '🧺', 'joie', "WHAOU !|Tout en un clic !", 'rayons', '3FE08A'),
 ("MSCI World", "L'indice des pays développés", "Les grandes et moyennes entreprises de 23 pays développés. C'est l'indice que copient beaucoup d'ETF.",
  "Environ 73 % d'entreprises américaines, et ni la Chine ni l'Inde.", '🌐', 'montre', "Le monde entier ?|Pas tout à fait !", 'machine', '35D6FF'),
 ("DCA", "Dollar Cost Averaging", "Investir la même somme à intervalles réguliers, quoi qu'il arrive, pour lisser son prix d'achat.",
  "100 € le 5 de chaque mois, sans regarder les cours.", '📅', 'pouce', "Pas de stress ma poule", 'chambre', '3FE08A'),
 ("PER", "Plan d'épargne retraite", "Une épargne bloquée jusqu'à la retraite, et tes versements réduisent ton impôt sur le revenu (dans une limite).",
  "Un versement fait avant le 31 décembre compte pour les impôts de l'année.", '🏖️', 'joie', "Moins d'impôts !", 'verger', 'FFB020'),
 ("PER", "… Price Earnings Ratio !", "Le piège : même sigle, rien à voir. C'est le prix d'une action divisé par ce qu'elle gagne par action.",
  "PER de 20 : l'action coûte 20 ans de bénéfices (s'ils restent stables).", '🧮', 'joie', "Super important celui-ci,|retiens-le !", 'banque', 'FF5A3C'),
 ("PFU", "Prélèvement forfaitaire unique", "La « flat tax » sur tes gains hors PEA et assurance vie : 12,8 % d'impôt + 18,6 % de prélèvements sociaux.",
  f"1{NB}000{NB}€ de plus-value en CTO : 314{NB}€ pour l'État en 2026.", '💸', 'triste', "Aïe…", 'tabac', 'FF5A3C'),
 ("IPO", "Initial Public Offering", "L'introduction en bourse : le jour où une entreprise vend pour la première fois ses actions au public.",
  "Airbnb est entrée en bourse en décembre 2020.", '🔔', 'rire', "Oh, tiens,|voilà un petit nouveau !", 'tirage', 'FFB020'),
 ("BCE", "Banque centrale européenne", "Elle fixe les taux d'intérêt de la zone euro pour tenir l'inflation autour de 2 % par an.",
  "Son taux de change de référence sert aussi à nos conversions dollar → euro.", '🏦', 'montre', "Le chef d'orchestre", 'gare', '35D6FF'),
]
NS = len(FICHES)+2
def fiche(cv, c, i):
    sig, dev, expl, ex, emo, pose, bul, fd, glow = FICHES[i]
    text(c, f"{i+1} / {len(FICHES)}" + ("   ·   LE PIÈGE" if i == 6 else ""), 540, 238, 'xb', 26, GD2 if i != 6 else 'FF8A8A', 'c', .95, 4)
    glow_text(cv, sig, 540, 395, 200 if len(sig) <= 4 else 132, top='FFFFFF', bottom='FFE3A0', glow=glow, ga=.6)
    gpill(c, dev, 540, 555, GD if i != 6 else RD, 34 if len(dev) < 30 else 30, fg=INK if i != 6 else WHITE)
    h1 = hauteur(expl, 40); texte(cv, expl, 670+h1/2, '💡', size=40)
    y = 670+h1+GAP; h2 = hauteur("Ex. : "+ex, 37); texte(cv, "Ex. : "+ex, y+h2/2, emo, size=37, mood='bleu')
    bb = coin(cv, pose, 220, 1478, 330); bulle_pres(c, bul, bb, 36, .25)
def s_cover(cv, c):
    text(c, "LE PETIT LEXIQUE DE LA BOURSE", 540, 250, 'sb', 28, ICE, 'c', .9, 4)
    glow_text(cv, "9 SIGLES", 540, 390, 150, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "À CONNAÎTRE", 540, 520, 96, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6)
    gpill(c, "… ET UN PIÈGE", 540, 650, RD, 44, fg=WHITE)
    def dr(k, w, h):
        sig = ["PEA", "CTO", "ETF", "MSCI", "DCA", "PER", "PFU", "IPO", "BCE"]
        for j, s_ in enumerate(sig):
            x = 105+(j % 3)*270; yy = 70+(j//3)*120; text(k, s_, x+60, yy, 'a', 58, WHITE if s_ != "PER" else 'FF8A8A', 'c')
    tp(cv, 860, 380, dr, 540, 960, 'or', rx=.04)
    bb = coin(cv, 'question', 230, 1478, 260); bulle_pres(c, "Tu les connais tous ?|Allez viens, on révise ensemble !", bb, 30, .2)
    text(c, "SWIPE", 920, 1420, 'xb', 28, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 965, 1418, 48)
def s_fin(cv, c):
    glow_text(cv, "LEQUEL TU NE", 540, 330, 100, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "CONNAISSAIS PAS ?", 540, 450, 86, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 570, 'sb', 36, ICE, 'c', .9); put_emoji(cv, '👇', 540, 630, 50)
    gpill(c, "ENREGISTRE-LE POUR T'EN SOUVENIR", 540, 740, GD, 34); put_emoji(cv, '📌', 540+330, 735, 44)
    bloc_abonne(cv, c); coin(cv, 'pouce', 540, 1420, 260); mention_pedago(c)
FONDS = ['tirage']+[f[7] for f in FICHES]+['verger']
def render(i):
    cv = fond(FONDS[i]).copy(); s, c = surface()
    if i == 0: s_cover(cv, c)
    elif i == NS-1: s_fin(cv, c)
    else: fiche(cv, c, i-1)
    cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
