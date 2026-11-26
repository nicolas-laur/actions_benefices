"""Carrousel « Les News » du 27/11/2026 : l'actualité des marchés du lundi 23 au jeudi 26 novembre (Wall Street arrêté à la clôture du 25/11,
fermé le 26/11 pour Thanksgiving ; Paris à la clôture du 26/11). Un sujet par diapo (le fait, la réaction chiffrée, une piste de lecture),
8 sujets, fonds Gemini 1930 (fonds/, prompts dans prompts_gemini.md), gabarit lib/carrousel.py. Chiffres et sources : sources.md.
usage : python3 carrousel.py [numéros…] [planche]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
from carrousel import *
LOGOS |= {'PROFIL', 'NVDA', 'ANTH', 'DELL', 'SAN', 'SU', 'BTC', 'EU', 'US', 'FR'}
import carrousel as _lib
_kpi0 = _lib.kpi
def kpi_logos(cv, rows, cx, cy, mood, w=860, h=380):
    """kpi du gabarit, plus un logo rond dans la plaque, à gauche du montant, pour les lignes à 6 champs (retour du 25/11 : logos dans le verre)"""
    keys = [r[5] if len(r) > 5 else None for r in rows]
    if not any(keys): return _kpi0(cv, rows, cx, cy, mood, w, h)
    rows2 = []
    for r, k in zip(rows, keys):
        lab, val, sub, dv, dcol = r[:5]
        rows2.append((lab, ('\u2007'*3 + val) if k else val, sub, dv, dcol))
    _kpi0(cv, rows2, cx, cy, mood, w, h)
    rh = (h-30)/len(rows)
    for i, k in enumerate(keys):
        if k: logo(cv, k, cx-w/2+40+26, cy-h/2+15+rh*i+rh/2+20, 50)
_lib.kpi = kpi_logos

# ---------- conversions : taux de référence BCE (sources.md) ----------
R = 1.0975          # taux de référence BCE du 26/11/2026 (1 € = 1,0975 $)
def eur(usd): return usd/R
def e2(usd): return f"{fmt(eur(usd), 2)}{NB}€"
def md(usd): return f"{fmt(eur(usd), 1)}{NB}Md€"
# ---------- Paris : clôtures (sources.md) ----------
CAC_20, CAC_23, CAC_25 = 7927.75, 8044.84, 7980.57
CAC_26 = 8108.74
def cac_sem(): return f"{'+' if CAC_26 >= CAC_20 else '−'}{fmt(abs(CAC_26/CAC_20-1)*100, 2)}{NB}%" if CAC_26 else "…"
def cac_sub(): return f"{fmt(CAC_26, 2)}{NB}pts jeudi, hors dividendes" if CAC_26 else "clôture du 26/11 à venir"

TOP = [("NVDA", "Nvidia : le retour de Jensen Huang"), ("EU", "Trump taxe l'Europe à 15 %"), ("US", "Inflation : la Fed sous pression"),
       ("FR", "Paris : les montagnes russes"), ("ANTH", "Anthropic sous son prix d'entrée"), ("DELL", "Dell : record… et chute"),
       ("🪙", "L'or loin de son record"), ("BTC", "Bitcoin dans le froid")]
def puce(cv, key, cx, cy, size):
    if key in LOGOS: logo(cv, key, cx, cy, size)
    else: put_emoji(cv, key, cx, cy, int(size*.8))
def s_cover(cv, c):
    text(c, "SEMAINE DU 23 AU 26 NOVEMBRE 2026", 540, 240, 'sb', 27, ICE, 'c', .85, 4)
    glow_text(cv, "LES NEWS", 540, 360, 170, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    gpill(c, "8 NEWS QUI ONT SECOUÉ LES MARCHÉS", 540, 500, GD, 34)
    n = len(TOP); rh = 62; ph = n*rh+14; y0 = 572
    def dr(k, w, h):
        for j, (e, s_) in enumerate(TOP):
            y = 7+rh*j+rh/2; text(k, s_, 104, y, 'xb', 28, WHITE, 'l', .97)
            if j: k.move_to(30, 7+rh*j); k.line_to(w-30, 7+rh*j); k.set_line_width(1.2); col(k, WHITE, .12); k.stroke()
    tp(cv, 880, ph, dr, 540, y0+ph/2, 'or', rx=.04, frost=14, dim=.62)
    for j, (e, s_) in enumerate(TOP): puce(cv, e, 540-440+58, y0+7+rh*j+rh/2, 44)
    bb = coin(cv, 'lit_journal_v2_titre', 235, 1512, 400); bulle_pres(c, "SAPRISTI !|Tu as vu ce qu’il se passe ?!", bb, 32, .26)
    text(c, "SWIPE", 920, 1420, 'xb', 28, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 965, 1418, 48)

TXT = {
 'nvda_fait': f"Onze jours après sa démission, Jensen Huang reprend la tête de Nvidia lundi 23/11. En une seule séance, l'entreprise gagne 952{NB}Md$ de valeur ({md(952)}).",
 'nvda_lect': f"Un seul dirigeant peut peser des centaines de milliards en bourse{NB}: c'est le « risque homme clé ».",
 'tax_fait': f"Washington propose de nouveaux droits de douane sur 14 économies, dont l'Union européenne. Pour l'UE{NB}: 15{NB}%, le plafond prévu par l'accord signé avec les États-Unis.",
 'tax_lect': f"Ce n'est qu'une proposition{NB}: consultation publique d'abord, application en 2027 au plus tôt.",
 'fed_fait': f"L'inflation PCE, la mesure suivie par la Fed, accélère à 3,8{NB}% sur un an en octobre. La croissance du 3e trimestre est relevée à 4,3{NB}% (en rythme annuel).",
 'fed_lect': f"La Fed vise 2{NB}% d'inflation. Quand on en est loin, monter les taux sert à freiner la demande.",
 'cac_fait': f"Paris bondit lundi avec le retour de Huang, rechute mercredi, rebondit jeudi. Sanofi rachète l'américain Insmed pour 41{NB}Md$ ({md(41.0)}).",
 'cac_lect': f"Tout le CAC 40 ne bouge pas ensemble{NB}: la tech et l'électricité baissent, la santé monte.",
 'ant_fait': f"Une semaine après son entrée en bourse, Anthropic clôture mardi sous son prix d'introduction de 83{NB}$ ({e2(83)}), pour la première fois.",
 'ant_lect': f"Le prix d'introduction n'est pas un plancher{NB}: il peut être franchi dans les deux sens.",
 'dell_fait': f"Dell publie mardi soir un chiffre d'affaires record de 54,9{NB}Md$ ({md(54.9)}), +103{NB}% en un an, et relève sa prévision annuelle à 202{NB}Md$.",
 'dell_lect': f"Une action anticipe{NB}: elle peut chuter juste avant de bons résultats, puis ne presque pas réagir.",
 'or_fait': f"L'or glisse sous 3{NB}500{NB}$ l'once mercredi, au plus bas depuis 14 mois. Les taux qui montent le rendent moins attractif.",
 'or_lect': f"L'or ne verse ni intérêt ni dividende{NB}: quand les taux montent, le garder « coûte » plus cher.",
 'btc_fait': f"Le bitcoin passe sous 58{NB}000{NB}$ mercredi ({fmt(eur(58000), 0)}{NB}€). Les fonds bitcoin cotés aux États-Unis ont perdu 4,94{NB}Md$ de dépôts en novembre.",
 'btc_lect': f"Ce mois-ci, le bitcoin a baissé avec les actions de la tech{NB}: il n'a pas joué le rôle de valeur refuge.",
}
def s_nvda(cv, c):
    sujet(cv, c, 1, 1, "NVIDIA", "LE RETOUR DU PATRON", TXT['nvda_fait'],
          [("LUNDI 23/11, À LA CLÔTURE", f"+31,48{NB}%", f"{e2(165.05)} (165,05 $), meilleure séance depuis 2003", None, GR),
           ("MARDI PUIS MERCREDI", f"−5,9{NB}%  /  −3,9{NB}%", f"{e2(149.30)} (149,30 $) mercredi", None, RD),
           ("SUR LA SEMAINE", f"+18,9{NB}%", "depuis la clôture du vendredi 20/11", None, GR)],
          'or', TXT['nvda_lect'], 'site_saut_joie', "Il est de retour !", tsize=76, emo='NVDA', ch='auto')
def s_tax(cv, c):
    sujet(cv, c, 2, 2, "DROITS DE DOUANE", "TRUMP REMET ÇA", TXT['tax_fait'],
          [("UNION EUROPÉENNE", f"15{NB}%", f"jusqu'à 20{NB}% si l'accord n'est pas respecté", None, OR),
           ("CHINE", f"+20{NB}%", f"en plus d'environ 25{NB}% déjà en place", None, RD),
           ("ENTRÉE EN VIGUEUR", "2027", "au plus tôt, après consultation", None, GD)],
          'orange', TXT['tax_lect'], 'site_balance', "Ça pèse lourd…", tsize=80, emo='EU', ch='auto')
def s_fed(cv, c):
    sujet(cv, c, 3, 3, "ÉTATS-UNIS", "L'INFLATION CHAUFFE", TXT['fed_fait'],
          [("INFLATION PCE, OCTOBRE", f"3,8{NB}%", f"hors énergie et alimentation : 3,3{NB}%", None, RD),
           ("HAUSSE DES TAUX EN DÉCEMBRE", f"97{NB}%", "de probabilité selon les marchés (CME)", None, OR),
           ("RÉUNION DE LA FED", "8-9 déc.", f"taux actuel : 3,75 à 4{NB}%", None, GD)],
          'rouge', TXT['fed_lect'], 'site_longue_vue', "Rendez-vous|le 9 décembre !", glow='FF5A3C', tsize=76, emo='US', ch='auto')
def s_cac(cv, c):
    sujet(cv, c, 4, 4, "BOURSE DE PARIS", "LES MONTAGNES RUSSES", TXT['cac_fait'],
          [("CAC 40, LUNDI 23/11", f"+1,48{NB}%", f"8{NB}044,84 pts", None, GR),
           ("CAC 40, SUR LA SEMAINE", cac_sem(), cac_sub(), None, GD),
           ("SANOFI, MERCREDI 25/11", f"+4,89{NB}%", f"98,16{NB}€, après le rachat d'Insmed", None, GR, 'SAN'),
           ("SCHNEIDER ELECTRIC, MERCREDI 25/11", f"−4,18{NB}%", f"216,65{NB}€, pris dans la baisse de la tech", None, RD, 'SU')],
          'bleu', TXT['cac_lect'], 'site_graphique', "Ça monte,|ça descend !", glow='35D6FF', tsize=70, emo='FR', ch='auto')
def s_ant(cv, c):
    sujet(cv, c, 5, 5, "ANTHROPIC", "RETOUR SOUS LES 83 $", TXT['ant_fait'],
          [("MARDI 24/11, À LA CLÔTURE", f"81,90{NB}$", f"{e2(81.90)}, −6,55{NB}% sur la journée", None, RD),
           ("MERCREDI, AU PLUS BAS", f"73,85{NB}$", f"−11{NB}% sous le prix d'entrée, clôture à 82,79 $", None, RD),
           ("DEPUIS LA 1RE COTATION", f"−25,7{NB}%", "ouverture à 111,50 $ le 19/11", None, RD)],
          'bleu', TXT['ant_lect'], 'site_parapluie', "Il pleut des pièces…", glow='35D6FF', tsize=74, emo='ANTH', ch='auto')
def s_dell(cv, c):
    sujet(cv, c, 6, 6, "DELL", "UN RECORD QUI NE SUFFIT PAS", TXT['dell_fait'],
          [("LUNDI 23/11", f"+20,46{NB}%", "dans l'élan de Nvidia", None, GR),
           ("MARDI 24/11, AVANT LES RÉSULTATS", f"−11,83{NB}%", f"{e2(295.28)} (295,28 $)", None, RD),
           ("MERCREDI 25/11", f"+0,6{NB}%", f"{e2(297.06)} (297,06 $)", None, GD)],
          'bleu', TXT['dell_lect'], 'site_trophee', "Record…|et alors ?", glow='35D6FF', tsize=62, emo='DELL', ch='auto')
def s_or(cv, c):
    sujet(cv, c, 7, 7, "OR", "L'OR PERD SON ÉCLAT", TXT['or_fait'],
          [("MERCREDI 25/11, 15 H", f"{fmt(eur(3471.52), 0)}{NB}€", "l'once (3 471,52 $)", None, OR),
           ("DEPUIS SON PLUS HAUT", f"−37,1{NB}%", "record de janvier : 5 518,21 $ l'once", None, RD),
           ("SUR UN AN", f"−16{NB}%", "4 133,41 $ il y a un an", None, RD)],
          'orange', TXT['or_lect'], 'triste', "Pas en or,|ce mois-ci…", tsize=80, emo='🪙', ch='auto')
def s_btc(cv, c):
    sujet(cv, c, 8, 8, "BITCOIN", "L'HIVER CRYPTO", TXT['btc_fait'],
          [("DEPUIS LE 1ER NOVEMBRE", f"−25{NB}%", "au plus bas de mercredi (CoinGlass)", None, RD),
           ("DEPUIS LE 1ER JANVIER", f"−34{NB}%", "environ, selon CoinGlass", None, RD)],
          'bleu', TXT['btc_lect'], 'choc', "Brrr, ça caille !", glow='35D6FF', tsize=84, emo='BTC', ch='auto')
def s_fin(cv, c):
    glow_text(cv, "ET TOI,", 540, 320, 124, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5)
    glow_text(cv, "QUELLE NEWS", 540, 455, 96, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "T'A SURPRIS ?", 540, 570, 104, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 690, 'sb', 34, ICE, 'c', .85); put_emoji(cv, '👇', 540, 745, 48)
    gpill(c, "ENREGISTRE-LE POUR LA SEMAINE PROCHAINE", 540, 840, GD, 30); put_emoji(cv, '📌', 540+375, 835, 40)
    bloc_abonne(cv, c, 1060); coin(cv, 'salut_chapeau', 540, 1442, 265); mention_pedago(c)

SLIDES = [s_cover, s_nvda, s_tax, s_fed, s_cac, s_ant, s_dell, s_or, s_btc, s_fin]
FONDS = ['couverture', 'huang', 'douane', 'fed', 'cac40', 'anthropic2', 'dell', 'or', 'bitcoin', 'couverture']
NS = len(SLIDES)
def fond_ep(name):
    """fond Gemini de l'épisode ; tant que Nicolas ne l'a pas déposé, un dégradé neutre pour caler la mise en page"""
    if os.path.exists(f'{D}/fonds/fond_{name}.jpg'): return fond(name)
    a = np.zeros((H, W, 3), np.float32); a[:] = np.interp(np.arange(H), [0, H], [40, 12])[:, None, None]; a[..., 2] += 18
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')
def render(i):
    cv = fond_ep(FONDS[i]).copy(); s, c = surface()
    SLIDES[i](cv, c); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__': sortie(render, NS)
