"""Carrousel « Les News » du 6/11/2026 : résultats contre bourse de la semaine du 2 au 4 novembre (Apple, Palantir, AMD, Novo Nordisk,
Booking, Ferrari, Uber, McDonald's, Snap) + Anthropic en bonus. Même format que le 31/10 (toile 1080×1920, contenu dans y = 200…1500,
version Instagram 4:5 découpée en y = 175…1525), avec le verre épais coloré selon l'information (lib/verre_epais.py).
Couverture : Mister Coin endormi dans son rocking-chair (clip Gemini détouré dans rock/), aussi en vidéo (couverture.mp4).
usage : python3 carrousel.py [planche] | python3 carrousel.py video"""
import sys, os, math, functools, subprocess
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from nty import text, surface, to_img, rr, col, tw, W, H
from logo import logo_symbol
from bglass import gpanel, place, glow_text, tilt_quad, surf, pil
from verre_epais import tplace
NB = ' '
CY = '35D6FF'; CY2 = 'A8EEFF'; GD = 'FFC24A'; GD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4D5E'; OR = 'FFA63D'; ICE = 'E8EEF8'; INK = '0B0E14'; WHITE = 'FFFFFF'
def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
def fmt(v, d=1): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',').replace(' ', NB)

# ---------- données (sources dans sources.md) ----------
EURUSD, EURDKK = 1.1267, 7.4738            # taux de référence BCE du 4/11/2026
def usd(x): return x/EURUSD
def dkk(x): return x/EURDKK
def md(v): return f"{fmt(v, 1 if v < 100 else 0)} Md€" if v >= 1 else f"{fmt(v*1000, 0)} M€"
# res / bfeu : 'v' vert, 'o' orange, 'r' rouge ; bourse = variation du cours à la première séance après l'annonce
DATA = {
 'AAPL': dict(nom="APPLE", per="JUILLET À SEPTEMBRE 2026", ca=usd(114.5), ca_g=12, bn=usd(30.71), bn_g=12,
              k3=("VENTES D'IPHONE", md(usd(57.6)), None, "+17,5 %", GR), k4=("MARGE PRÉVUE POUR NOËL", "45 à 46 %", "contre 47,9 %", "↓", RD),
              res='v', res_txt="SOLIDES", bourse=-1.9, bfeu='o', bnote="clôture du 3/11", pose='inquiet', bulle="La marge va maigrir…"),
 'PLTR': dict(nom="PALANTIR", per="JUILLET À SEPTEMBRE 2026", ca=usd(2.313), ca_g=96, bn=usd(1.128), bn_g=137,
              k3=("ENTREPRISES AMÉRICAINES", "+148 %", "sur un an", None, GR), k4=("VALEUR DES CONTRATS SIGNÉS", "+6 %", "contre +49 % au trimestre d'avant", None, OR),
              res='v', res_txt="ÉNORMES", bourse=-1.65, bfeu='o', bnote="clôture du 3/11", pose='facepalm', bulle="Trop cher, déjà ?"),
 'AMD':  dict(nom="AMD", per="JUILLET À SEPTEMBRE 2026", ca=usd(13.377), ca_g=45, bn=usd(2.428), bn_g=95,
              k3=("PUCES POUR DATA CENTERS", md(usd(8.546)), None, "+97 %", GR), k4=("PRÉVISION FIN D'ANNÉE", md(usd(17.0)), "≈ 17 Md$", "+66 %", GR),
              res='v', res_txt="SOLIDES", bourse=3.1, bfeu='v', bnote="clôture du 4/11", pose='joie', bulle="L'IA, ça paie !"),
 'NOVO': dict(nom="NOVO NORDISK", per="JUILLET À SEPTEMBRE 2026", ca=dkk(79.195), ca_g=6, bn=dkk(16.74), bn_g=-16,
              k3=("WEGOVY EN PILULE", md(dkk(5.394)), "nouveau", None, GR), k4=("OBJECTIFS 2026", "RELEVÉS", "−2 à +2 % au lieu de −6 à 0 %", "↑", GR),
              res='o', res_txt="MITIGÉS", bourse=5.5, bfeu='v', bnote="clôture du 4/11, Copenhague", pose='pouce', bulle="La pilule passe bien !"),
 'BKNG': dict(nom="BOOKING", per="JUILLET À SEPTEMBRE 2026", ca=usd(8.893), ca_g=-1, bn=usd(2.717), bn_g=-1,
              k3=("NUITÉES RÉSERVÉES", "+7 %", "sur un an", None, GR), k4=("LITIGE AUX ÉTATS-UNIS (FTC)", md(usd(0.9)), "déduits du chiffre d'affaires", None, RD),
              res='o', res_txt="MITIGÉS", bourse=9.8, bfeu='v', bnote="clôture du 4/11", pose='choc', bulle="Quoi, +10 % ?!"),
 'RACE': dict(nom="FERRARI", per="JUILLET À SEPTEMBRE 2026", ca=1.896, ca_g=7, bn=0.431, bn_g=13,
              k3=("MARGE (EBITDA)", "39,7 %", "contre 37,9 %", "↑", GR), k4=("VOITURES LIVRÉES", "3 368", None, "−1 %", OR),
              res='v', res_txt="SOLIDES", bourse=4.47, bfeu='v', bnote="clôture du 3/11, Milan", pose='rire', bulle="Ça roule !"),
 'UBER': dict(nom="UBER", per="JUILLET À SEPTEMBRE 2026", ca=usd(14.77), ca_g=10, bn=usd(0.512), bn_g=-92,
              k3=("COURSES ET REPAS RÉSERVÉS", md(usd(59.8)), None, "+20 %", GR), k4=("POURQUOI LE BÉNÉFICE CHUTE", "UN GAIN", "fiscal unique l'an dernier", None, GD),
              res='o', res_txt="MITIGÉS", bourse=4.91, bfeu='v', bnote="clôture du 4/11", pose='montre', bulle="Regarde l'activité !"),
 'MCD':  dict(nom="McDONALD'S", per="JUILLET À SEPTEMBRE 2026", ca=usd(7.157), ca_g=1, bn=usd(2.486), bn_g=9,
              k3=("VENTES DES RESTAURANTS", "+1,5 %", "à magasins comparables", None, OR), k4=("AUX ÉTATS-UNIS", "−0,2 %", "mieux que prévu (−0,5 %)", None, OR),
              res='o', res_txt="MITIGÉS", bourse=6.53, bfeu='v', bnote="clôture du 4/11", pose='question', bulle="Pas si mal, non ?"),
 'SNAP': dict(nom="SNAP", per="JUILLET À SEPTEMBRE 2026", ca=usd(1.7225), ca_g=14, bn=usd(0.0565), bn_g=None, bn_sub="contre une perte de "+md(usd(0.1035)),
              k3=("UTILISATEURS PAR JOUR", "495 M", "moins que prévu", "+4 %", OR), k4=("EBITDA AJUSTÉ", md(usd(0.3826)), None, "×2,1", GR),
              res='o', res_txt="MITIGÉS", bourse=-12.3, bfeu='r', bnote="clôture du 5/11", pose='triste', bulle="La douche froide…"),
}
KEYS = ('AAPL', 'PLTR', 'AMD', 'NOVO', 'BKNG', 'RACE', 'UBER', 'MCD', 'SNAP')
LECTURE = {
 'cover': "Neuf grandes entreprises ont publié leurs comptes cette semaine : leurs chiffres face à la réaction de la bourse.",
 'AAPL': "Trimestre record, mais la mémoire coûte plus cher : Apple annonce une marge en baisse pour les fêtes.",
 'PLTR': "Le chiffre d'affaires double, mais les nouveaux contrats ralentissent, et l'action était déjà très chère.",
 'AMD': "Les puces IA doublent et la prévision bat les attentes : AMD monte le jour où les fabricants de puces chutent.",
 'NOVO': "Bénéfice en baisse à cause d'une dépréciation, mais la pilule Wegovy cartonne : Novo relève ses objectifs.",
 'BKNG': "Hors litige américain, le trimestre bat les attentes, malgré des prévisions prudentes.",
 'RACE': "Un peu moins de voitures, mais plus chères et plus personnalisées : marge record et objectifs relevés.",
 'UBER': "Le bénéfice chute car l'an dernier comptait un gain fiscal de 4,9 Md$. L'activité, elle, grimpe de 20 %.",
 'MCD': "Les ventes stagnent, mais un peu mieux que prévu. Et mercredi, tout Wall Street montait (S&P 500 +1,6 %).",
 'SNAP': "Retour aux bénéfices, mais moins d'utilisateurs que prévu : l'action plonge le soir même.",
 'ANTH': "Pas encore en bourse : son entrée au Nasdaq est attendue ce mois-ci. Le plus gros dossier de l'année.",
 'match': "La bourse réagit à la surprise et aux prévisions, pas au chiffre brut. Et mercredi, tout Wall Street montait.",
 'fin': "Un bon trimestre ne fait pas une bonne action : regarde aussi le prix payé et les perspectives.",
}
FEU = {'v': '3FE08A', 'o': 'FFA63D', 'r': 'FF4D5E'}
MOOD = {'v': 'vert', 'o': 'orange', 'r': 'rouge', None: 'or'}
# ---------- fond : ciel étoilé + globe en points (rendu de la vidéo PEA/CTO), Amériques face à nous, qui tourne d'une diapo à l'autre ----------
GLOBE = ['0978', '0995', '1012', '1030', '1047', '1065', '1082', '1100']; GR_ = 514/600
@functools.lru_cache(maxsize=1)
def sky():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('04060B')); g.add_color_stop_rgb(.55, *rgb('070A12')); g.add_color_stop_rgb(1, *rgb('0B0F18')); c.set_source(g); c.paint()
    rng = np.random.default_rng(2)
    for x, y, r, a in zip(rng.uniform(0, W, 260), rng.uniform(0, H, 260), rng.uniform(.6, 1.7, 260), rng.uniform(.08, .35, 260)):
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a); c.fill()
    return to_img(s)
def background(i, cx=540, cy=1240, size=1560, al=.55, tint=None):
    tint = tint or CY
    cv = sky().copy()
    b = np.asarray(Image.open(f'{D}/globe/b_{GLOBE[i]}.png').convert('RGB'), np.float32); m = np.asarray(Image.open(f'{D}/globe/m_{GLOBE[i]}.png').convert('RGB'), np.float32)[..., :1]/255
    gl = b*(1-.5*m)+m*np.array(rgb(tint))*255*.75                      # terres en points teintées cyan, discrètes
    gl = Image.fromarray(np.clip(gl, 0, 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
    yy, xx = np.mgrid[0:size, 0:size]; r = np.hypot(xx-size/2+.5, yy-size/2+.5)/(size/2); A = np.clip((GR_-r)*size*.5, 0, 1)[..., None]*al
    arr = np.asarray(cv.convert('RGB'), np.float32); x0, y0 = cx-size//2, cy-size//2
    gx0, gy0 = max(0, -x0), max(0, -y0); gx1, gy1 = min(size, W-x0), min(size, H-y0)
    sub = arr[y0+gy0:y0+gy1, x0+gx0:x0+gx1]; G = np.asarray(gl, np.float32)[gy0:gy1, gx0:gx1]; AA = A[gy0:gy1, gx0:gx1]
    sub[:] = sub*(1-AA)+G*AA
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface(); R1 = size*GR_*.5*1.2; rg = cairo.RadialGradient(cx, cy, 0, cx, cy, R1)           # liseré d'atmosphère
    rg.add_color_stop_rgba(0, *rgb(tint), 0); rg.add_color_stop_rgba(.8, *rgb(tint), 0); rg.add_color_stop_rgba(.835, *rgb(tint), .30*al); rg.add_color_stop_rgba(1, *rgb(tint), 0)
    c.set_source(rg); c.arc(cx, cy, R1, 0, 2*math.pi); c.fill(); out.alpha_composite(to_img(s))
    s, c = surface(); g = cairo.LinearGradient(0, 0, 0, H)                                           # voile en haut : les titres restent sur fond calme
    g.add_color_stop_rgba(0, 0, 0, 0, .0); g.add_color_stop_rgba(.3, 0, 0, 0, .0); g.add_color_stop_rgba(1, 0, 0, 0, .25); c.set_source(g); c.paint(); out.alpha_composite(to_img(s))
    return out
def halos(cv, spots):
    s, c = surface()
    for (x, y, rad, colr, a) in spots:
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *rgb(colr), a); g.add_color_stop_rgba(1, *rgb(colr), 0)
        c.set_source(g); c.arc(x, y, rad, 0, 2*math.pi); c.fill()
    cv.alpha_composite(to_img(s))

# ---------- éléments ----------
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
def gpill(c, s, x, y, colr, size=34, fg=INK, a=1):
    w = tw(c, s, 'xb', size, 2)+60; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2); return w
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
def put_emoji(cv, ch, x, y, size):
    e = emoji(ch, size); cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
@functools.lru_cache(maxsize=16)
def coin_img(pose, h):
    im = Image.open(f'{D}/coin/{pose}.png').convert('RGBA'); return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
def coin(cv, pose, cx, feet, h=430, flip=False):
    """Mister Coin posé au sol, avec son ombre"""
    im = coin_img(pose, h)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    s, c = surface(); c.save(); c.translate(cx, feet); c.scale(im.width*.42, 18)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, .65); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-im.width/2), int(feet-h+6)))
    return (cx-im.width/2, feet-h, cx+im.width/2, feet)
def bulle_pres(c, s_, bb, size=34, k=.3):
    """bulle collée à Mister Coin : elle part juste à droite de lui, pointe courte vers sa tête"""
    w = tw(c, s_, 'xb', size)+60; h = size*2.0; x0 = bb[2]+26; y = bb[1]+(bb[3]-bb[1])*k
    c.move_to(x0+16, y-15); c.line_to(x0-22, y+24); c.line_to(x0+16, y+13); c.close_path(); col(c, WHITE); c.fill()
    rr(c, x0, y-h/2, w, h, h/2); col(c, WHITE); c.fill()
    text(c, s_, x0+w/2, y, 'xb', size, INK, 'c')
def bulle(c, s, x, y, tip, size=34):
    """bulle de BD blanche, pointe vers (tip) = la tête de Mister Coin"""
    w = tw(c, s, 'xb', size)+64; h = size*2.1; x0 = x-w/2; y0 = y-h/2
    tx, ty = tip; bx = min(max(tx, x0+50), x0+w-50); by = y0+h if ty > y else y0
    c.move_to(bx-22, by); c.line_to(tx, ty); c.line_to(bx+22, by); c.close_path(); col(c, WHITE); c.fill()
    rr(c, x0, y0, w, h, h/2); col(c, WHITE); c.fill()
    text(c, s, x, y, 'xb', size, INK, 'c')
def logo(cv, c, key, cx, cy, size=96):
    """logo fourni par Nicolas (logos/<KEY>.png) ; tant qu'il manque, un emplacement en pointillés"""
    f = f'{D}/logos/{key}.png'
    if os.path.exists(f):
        im = Image.open(f).convert('RGBA'); im = im.crop(im.getbbox()); k = size/max(im.size); im = im.resize((max(1, int(im.width*k)), max(1, int(im.height*k))), Image.LANCZOS)
        cv.alpha_composite(im, (int(cx-im.width/2), int(cy-im.height/2)))
    else:
        c.set_dash([8, 8]); c.arc(cx, cy, size/2, 0, 2*math.pi); c.set_line_width(3); col(c, WHITE, .45); c.stroke(); c.set_dash([])
        text(c, "LOGO", cx, cy, 'xb', 18, WHITE, 'c', .5, 2)
def lampes(k, x, y, etat, r=15, gap=40):
    """trois lampes rouge / orange / vert, seule celle de l'état est allumée (halo)"""
    for j, e in enumerate('rov'):
        xx = x+(j-1)*gap; on = (e == etat)
        if on:
            g = cairo.RadialGradient(xx, y, 0, xx, y, r*3); g.add_color_stop_rgba(0, *rgb(FEU[e]), .55); g.add_color_stop_rgba(1, *rgb(FEU[e]), 0); k.set_source(g); k.arc(xx, y, r*3, 0, 2*math.pi); k.fill()
        k.arc(xx, y, r, 0, 2*math.pi); col(k, FEU[e], 1 if on else .16); k.fill_preserve(); k.set_line_width(2); col(k, WHITE if on else FEU[e], .7 if on else .35); k.stroke()
def sgn(v, unit=' %', d=None):
    d = (1 if abs(v) < 1 else 0) if d is None else d
    if abs(v-round(v)) < 1e-9: d = 0
    return ("+" if v > 0 else "−")+fmt(abs(v), d)+unit.replace(' ', NB)
def wrap(c, s_, f, size, maxw):
    lines, cur = [], ''
    for w in s_.split(' '):
        t = (cur+' '+w).strip()
        if cur and tw(c, t, f, size) > maxw: lines.append(cur); cur = w
        else: cur = t
    return lines+[cur]
# ---------- verre épais : le panneau est calculé sur l'image en cours (il réfracte le globe et le ciel) ----------
def tp(cv, w, h, draw, cx, cy, mood='or', rx=.05, ry=0.0, bev=None):
    bev = bev or (34 if min(w, h) > 200 else 24); P = bev-10; W2, H2 = w+2*P, h+2*P
    base = np.asarray(cv.convert('RGB')).astype(np.float32)/255
    def dd(k, ww, hh): k.translate(P, P); draw(k, w, h)
    tplace(cv, base, W2, H2, dd, tilt_quad(cx, cy, W2, H2, ry=ry, rx=rx), 1.0, mood, bevel=bev, r=44 if min(w, h) > 200 else 30, frost=30, dim=.42, cache=False)   # image fixe : plateau plus dépoli et plus sombre pour la lecture
def feu(cv, titre, etat, valeur, cx, cy, ry, w=410, h=150):
    def dr(k, w, h):
        text(k, titre, w/2, 30, 'xb', 23, ICE, 'c', .9, 3)
        lampes(k, w/2, 68, etat, 13, 36)
        text(k, valeur, w/2, h-36, 'a', 48, FEU[etat] if etat else WHITE, 'c')
    tp(cv, w, h, dr, cx, cy, MOOD[etat], rx=.04, ry=ry, bev=22)
def kpi(cv, rows, cx, cy, mood, w=860, h=380):
    def dr(k, w, h):
        n = len(rows); rh = (h-30)/n
        for i, (lab, val, sub, dv, dcol) in enumerate(rows):
            y = 15+rh*i+rh/2
            if i: k.move_to(40, 15+rh*i); k.line_to(w-40, 15+rh*i); k.set_line_width(1.5); col(k, WHITE, .14); k.stroke()
            text(k, lab, 40, y-19, 'xb', 23, ICE, 'l', .85, 2)
            text(k, val, 40, y+20, 'a', 46, dcol if (dcol and not dv) else WHITE, 'l')
            if sub: text(k, sub, 40+tw(k, val, 'a', 46)+16, y+25, 'sb', 21, ICE, 'l', .85)
            if dv:
                pw = tw(k, dv, 'xb', 31)+40; rr(k, w-40-pw, y-27, pw, 54, 27); col(k, dcol, .18); k.fill_preserve(); k.set_line_width(2.5); col(k, dcol, .95); k.stroke()
                text(k, dv, w-40-pw/2, y, 'xb', 31, dcol, 'c')
    tp(cv, w, h, dr, cx, cy, mood, rx=.05, ry=.03, bev=30)
def lecture(cv, key, cy, w=860, size=29):
    k0 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); L = wrap(k0, LECTURE[key], 'sb', size, w-140); lh = size*1.32; h = int(len(L)*lh+36)
    def dr(k, w, h):
        rr(k, 18, 18, 6, h-36, 3); col(k, GD, .9); k.fill()
        for i, l in enumerate(L): text(k, l, 84, 18+lh*i+lh/2, 'sb', size, WHITE, 'l', .96)
    tp(cv, w, h, dr, 540, cy, 'or', rx=.03, ry=0, bev=20)
    assert len(L) <= 2, (key, L)
    put_emoji(cv, '💡', 540-w/2+50, cy, 30)
    return h
NS = 14
def pagination(c, i, n=NS):
    for k in range(n):
        x = 540+(k-(n-1)/2)*24; c.arc(x, 1478, 6 if k == i else 4.5, 0, 2*math.pi); col(c, WHITE, .95 if k == i else .3); c.fill()
def logo(cv, key, cx, cy, size=96):
    im = Image.open(f'{D}/logos/{key}.png').convert('RGBA'); k = size/max(im.size); im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS)
    s, c = surface(); rr(c, cx-im.width/2+4, cy-im.height/2+8, im.width, im.height, im.width*.22); col(c, '000000', .35); c.fill()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-im.width/2), int(cy-im.height/2)))

# ---------- couverture : Mister Coin endormi dans son rocking-chair ----------
ROCK = sorted(f for f in os.listdir(f'{D}/rock') if f.endswith('.png')) if os.path.isdir(f'{D}/rock') else []
@functools.lru_cache(maxsize=4)
def rock_img(i, h=440):
    im = Image.open(f'{D}/rock/{ROCK[i]}').convert('RGBA'); im = im.crop((100, 250, 710, 1030))
    return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)
def cover_static(cv, c):
    text(c, "RÉSULTATS DU 2 AU 4 NOVEMBRE 2026", 540, 240, 'sb', 27, ICE, 'c', .8, 4)
    glow_text(cv, "LES NEWS", 540, 360, 170, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    gpill(c, "RÉSULTATS VS BOURSE", 540, 500, GD, 38)
    text(c, "De bons chiffres = une action qui monte ?", 540, 585, 'xb', 36, WHITE, 'c')
    def grid(k, w, h):
        for j, kk in enumerate(KEYS):
            x = 95+(j % 3)*265; y = 70+(j//3)*120
            text(k, DATA[kk]['nom'] if kk != 'NOVO' else "NOVO", x+60, y, 'xb', 22, WHITE, 'l', .95, 1)
            lampes(k, x+115, y+36, None, 9, 24)
    tp(cv, 860, 360, grid, 540, 815, 'or', rx=.05)
    for j, kk in enumerate(KEYS):
        x = 540-430+95+(j % 3)*265; y = 815-180+70+(j//3)*120+14
        logo(cv, kk, x-10, y, 62)
def cover_coin(cv, c, fr):
    if not ROCK: return
    im = rock_img(fr % len(ROCK)); x0, y0 = 120, 1490-im.height
    s, k = surface(); k.save(); k.translate(x0+im.width*.55, 1478); k.scale(im.width*.42, 16)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, .6); g.add_color_stop_rgba(1, 0, 0, 0, 0); k.set_source(g); k.arc(0, 0, 1, 0, 2*math.pi); k.fill(); k.restore()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (x0, y0))
    bulle_pres(c, "Réveille-moi si ça monte…", (x0+40, y0+60, x0+im.width-30, 1490), 30, .12)
    text(c, "SWIPE", 920, 1420, 'xb', 28, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 965, 1418, 48)
def s_cover(cv, c): cover_static(cv, c); cover_coin(cv, c, 120)

# ---------- une diapo par entreprise ----------
def entreprise(key, idx):
    def s(cv, c):
        d = DATA[key]
        text(c, "RÉSULTATS · "+d['per'], 540, 232, 'sb', 24, ICE, 'c', .7, 3)
        size = 104 if len(d['nom']) < 9 else 86
        nw = tw(c, d['nom'], 'a', size); x0 = 540-(nw+112)/2
        logo(cv, key, x0+44, 318, 88); glow_text(cv, d['nom'], x0+112+nw/2, 318, size, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.4, reflect=False)
        lecture(cv, key, 452)
        b = d['bourse']
        feu(cv, "LES RÉSULTATS", d['res'], d['res_txt'], 300, 625, .12)
        feu(cv, "LA BOURSE", d['bfeu'], sgn(b, ' %', 1), 780, 625, -.12)
        text(c, d['bnote'], 780, 736, 'sb', 22, ICE, 'c', .8)
        bn_txt = md(d['bn'])
        rows = [("CHIFFRE D'AFFAIRES", md(d['ca']), None, sgn(d['ca_g']), GR if d['ca_g'] > 2 else (OR if d['ca_g'] >= 0 else RD)),
                ("BÉNÉFICE NET", bn_txt, d.get('bn_sub'), sgn(d['bn_g']) if d['bn_g'] is not None else "RETOUR", GR if (d['bn_g'] is None or d['bn_g'] > 0) else RD),
                d['k3'], d['k4']]
        kpi(cv, rows, 540, 972, MOOD[d['res']])
        bb = coin(cv, d['pose'], 245, 1478, 255)
        bulle_pres(c, d['bulle'], bb, 32)
        pagination(c, idx)
    return s
def s_anthropic(cv, c):
    text(c, "BONUS · À SURVEILLER", 540, 232, 'sb', 24, ICE, 'c', .75, 4)
    nw = tw(c, "ANTHROPIC", 'a', 104); x0 = 540-(nw+112)/2
    logo(cv, 'ANTH', x0+44, 318, 88); glow_text(cv, "ANTHROPIC", x0+112+nw/2, 318, 104, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.45, reflect=False)
    lecture(cv, 'ANTH', 452)
    rows = [("CHIFFRE D'AFFAIRES DU TRIMESTRE", md(usd(16.96)), "≈ 17 Md$", "+47 %", GR),
            ("PERTE NETTE DU TRIMESTRE", "−"+md(usd(23.29)), "surtout comptable", None, RD),
            ("PERTE D'EXPLOITATION", "−"+md(usd(0.567)), "contre un bénéfice au trimestre d'avant", None, OR),
            ("PUISSANCE DE CALCUL DÉJÀ PROMISE", md(usd(895.4)), "≈ 895 Md$", None, GD)]
    kpi(cv, rows, 540, 790, 'or', h=440)
    text(c, "+47 % : par rapport au trimestre précédent (avril à juin).", 540, 1068, 'sb', 22, ICE, 'c', .7)
    bb = coin(cv, 'montre', 245, 1478, 255)
    bulle_pres(c, "Prochaine star de la bourse ?", bb, 30)
    pagination(c, 10)
def s_match(cv, c):
    text(c, "LE MATCH DE LA SEMAINE", 540, 232, 'sb', 26, ICE, 'c', .8, 4)
    glow_text(cv, "RÉSULTATS VS BOURSE", 540, 312, 80, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.45, reflect=False)
    ST = 80; PH = 60+ST*9; PY = 390+PH/2
    def dr(k, w, h):
        text(k, "RÉSULTATS", 500, 34, 'xb', 21, ICE, 'c', .85, 3); text(k, "BOURSE", 735, 34, 'xb', 21, ICE, 'c', .85, 3)
        for j, kk in enumerate(KEYS):
            d = DATA[kk]; y = 60+ST*j+ST/2+4
            if j: k.move_to(26, y-ST/2); k.line_to(w-26, y-ST/2); k.set_line_width(1.2); col(k, WHITE, .12); k.stroke()
            text(k, d['nom'], 112, y, 'xb', 25, WHITE, 'l', 1, 1)
            lampes(k, 440, y, d['res'], 9, 24); text(k, d['res_txt'], 560, y, 'a', 30, FEU[d['res']], 'c')
            lampes(k, 690, y, d['bfeu'], 9, 24); text(k, sgn(d['bourse'], ' %', 1), 800, y, 'a', 32, FEU[d['bfeu']], 'c')
    tp(cv, 880, PH, dr, 540, PY, 'or', rx=.03)
    for j, kk in enumerate(KEYS): logo(cv, kk, 170, 390+60+ST*j+ST/2+4, 50)
    lecture(cv, 'match', 1262, size=27)
    bb = coin(cv, 'question', 170, 1480, 150)
    bulle_pres(c, "Pas le même verdict !", bb, 28, .3)
    pagination(c, 11)
def s_paradoxe(cv, c):
    halos(cv, [(540, 640, 600, GR, .07), (540, 980, 520, RD, .06)])
    text(c, "LE PARADOXE DE LA SEMAINE", 540, 240, 'sb', 27, ICE, 'c', .8, 4)
    def a(k, w, h):
        text(k, "PALANTIR", w/2, 46, 'xb', 26, ICE, 'c', .9, 3)
        text(k, "chiffre d'affaires", w/2, 98, 'sb', 26, ICE, 'c', .75); text(k, "+96 %", w/2, 168, 'a', 84, GR, 'c')
        text(k, "l'action", w/2, 238, 'sb', 26, ICE, 'c', .75); text(k, "−1,7 %", w/2, 300, 'a', 70, OR, 'c')
    def b(k, w, h):
        text(k, "BOOKING", w/2, 46, 'xb', 26, ICE, 'c', .9, 3)
        text(k, "chiffre d'affaires", w/2, 98, 'sb', 26, ICE, 'c', .75); text(k, "−1 %", w/2, 168, 'a', 84, OR, 'c')
        text(k, "l'action", w/2, 238, 'sb', 26, ICE, 'c', .75); text(k, "+9,8 %", w/2, 300, 'a', 70, GR, 'c')
    tp(cv, 390, 350, a, 300, 520, 'orange', ry=.12); tp(cv, 390, 350, b, 780, 520, 'vert', ry=-.12)
    logo(cv, 'PLTR', 300, 300, 64); logo(cv, 'BKNG', 780, 300, 64)
    def m(k, w, h):
        text(k, "La bourse ne paie pas les chiffres :", w/2, 62, 'xb', 34, WHITE, 'c')
        text(k, "elle paie la surprise.", w/2, 112, 'xb', 34, WHITE, 'c')
        text(k, "Palantir était attendu au sommet et coûte cher ;", w/2, 186, 'sb', 28, GD2, 'c')
        text(k, "Booking avait perdu 29 % depuis janvier.", w/2, 228, 'sb', 28, GD2, 'c')
    tp(cv, 860, 280, m, 540, 900, 'or', rx=.05)
    bb = coin(cv, 'question', 245, 1478, 270)
    bulle_pres(c, "Logique… ou pas ?", bb, 32)
    pagination(c, 12)
def s_fin(cv, c):
    halos(cv, [(540, 600, 640, CY, .10), (540, 900, 500, GD, .08)])
    glow_text(cv, "ET TOI,", 540, 330, 124, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5)
    glow_text(cv, "LAQUELLE TU AURAIS", 540, 470, 88, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "ACHETÉE ?", 540, 590, 104, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 730, 'sb', 34, ICE, 'c', .85); put_emoji(cv, '👇', 540, 790, 52)
    lecture(cv, 'fin', 915)
    coin(cv, 'question', 540, 1330, 280)
    c.push_group(); logo_symbol(c, 395, 1398, 40); c.pop_group_to_source(); c.paint()
    text(c, "Actions_Benefices", 428, 1398, 'b', 28, WHITE, 'l')
    text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 1462, 'sb', 20, ICE, 'c', .55)
SLIDES = [s_cover]+[entreprise(k, i+1) for i, k in enumerate(KEYS)]+[s_anthropic, s_match, s_paradoxe, s_fin]
assert len(SLIDES) == NS
WARM = {'v': CY, 'o': 'FF9A3C', 'r': 'FF5A3C'}
TINTS = [CY]+[WARM[DATA[k]['res']] for k in KEYS]+[GD, CY, CY, CY]
GL = [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]
def render(i):
    cv = background(GL[i], tint=TINTS[i]); s, c = surface()
    SLIDES[i](cv, c); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
def video():
    """couverture animée (9:16, 24 i/s, ~8,7 s en boucle), sans son : Nicolas pose sa musique country dans l'appli"""
    cv0 = background(0, tint=TINTS[0]); s, c = surface(); cover_static(cv0, c); cv0.alpha_composite(to_img(s))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                           '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', f'{D}/out/couverture_animee_9x16.mp4'], stdin=subprocess.PIPE)
    for fr in range(len(ROCK)):
        cv = cv0.copy(); s, c = surface(); cover_coin(cv, c, fr); cv.alpha_composite(to_img(s)); ff.stdin.write(cv.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('vidéo ok')
if __name__ == '__main__':
    os.makedirs(f'{D}/out', exist_ok=True); os.makedirs(f'{D}/prev', exist_ok=True)
    if 'video' in sys.argv: video(); sys.exit()
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    ims = {}
    for i in (only or range(NS)):
        im = render(i); ims[i] = im; im.save(f'{D}/out/tiktok_{i+1}.png'); im.crop((0, 175, W, 1525)).save(f'{D}/out/instagram_{i+1}.png')
    if 'planche' in sys.argv:
        th = [ims[i].resize((360, 640)) for i in sorted(ims)]; P = Image.new('RGB', (360*7, 640*((len(th)+6)//7)))
        [P.paste(t, ((k % 7)*360, (k//7)*640)) for k, t in enumerate(th)]; P.save(f'{D}/prev/planche.png')
    print('ok')
