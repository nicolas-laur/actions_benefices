"""Carrousel lexique du 17/11/2026 : « 9 sigles de la bourse… et un piège » (PEA, CTO, ETF, MSCI World, DCA, PER x2, PFU, IPO, BCE),
une fiche par sigle (sigle, développé, explication, exemple), fonds = décors 1930 des vidéos récentes (affinés), Mister Coin sur chaque fiche.
Même format que Les News (toile 1080×1920, contenu dans y = 200…1500, version Instagram 4:5 découpée en y = 175…1525).
usage : python3 carrousel.py [planche]"""

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
def bulle_pres(c, s_, bb, size=34, k=.3, xmax=930):
    """bulle collée à Mister Coin : elle part juste à droite de lui, pointe courte vers sa tête ; passe sur deux lignes si elle dépasserait x = xmax (icônes des applis)"""
    x0 = bb[2]+26; y = bb[1]+(bb[3]-bb[1])*k; lines = s_.split('|')
    if len(lines) == 1 and tw(c, s_, 'xb', size)+60 > xmax-x0:
        m = s_.split(' '); best = None
        for i in range(1, len(m)):
            a, b = ' '.join(m[:i]), ' '.join(m[i:]); v = max(tw(c, a, 'xb', size), tw(c, b, 'xb', size))
            if best is None or v < best[0]: best = (v, [a, b])
        lines = best[1]
    w = max(tw(c, l, 'xb', size) for l in lines)+60; lh = size*1.25; h = size*2.0+lh*(len(lines)-1)
    c.move_to(x0+16, y-15); c.line_to(x0-22, y+24); c.line_to(x0+16, y+13); c.close_path(); col(c, WHITE); c.fill()
    rr(c, x0, y-h/2, w, h, min(h/2, size)); col(c, WHITE); c.fill()
    for j, l in enumerate(lines): text(c, l, x0+w/2, y+(j-(len(lines)-1)/2)*lh, 'xb', size, INK, 'c')
    assert x0+w <= xmax+1, (s_, x0+w)
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
    tp(cv, w, h, dr, cx, cy, mood, rx=.05, ry=.03, bev=20)
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
@functools.lru_cache(maxsize=32)
def logo_rond(key, size):
    """tuile logo découpée en bulle ronde (retour du 12/11), suréchantillonnée pour un bord net"""
    B = size*4; im = Image.open(f'{D}/logos/{key}.png').convert('RGBA'); k = B*1.06/max(im.size)             # léger zoom : le cercle mange les coins de la tuile
    im = im.resize((round(im.width*k), round(im.height*k)), Image.LANCZOS); x0, y0 = (im.width-B)//2, (im.height-B)//2; im = im.crop((x0, y0, x0+B, y0+B))
    m = Image.new('L', (B, B), 0); ImageDraw.Draw(m).ellipse((0, 0, B-1, B-1), fill=255); im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel('A')), np.asarray(m))))
    ImageDraw.Draw(im).ellipse((2, 2, B-3, B-3), outline=(255, 255, 255, 170), width=max(4, B//48))
    return im.resize((size, size), Image.LANCZOS)
def logo(cv, key, cx, cy, size=96):
    im = logo_rond(key, int(size))
    s, c = surface(); c.arc(cx+3, cy+6, size/2, 0, 2*math.pi); col(c, '000000', .35); c.fill()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-size/2), int(cy-size/2)))


def texte(cv, s_, cy, emo='💡', w=860, size=29, mood='or'):
    k0 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); L = wrap(k0, s_, 'sb', size, w-140); lh = size*1.32; h = int(len(L)*lh+36)
    assert len(L) <= 4, (s_, L)
    def dr(k, w, h):
        rr(k, 18, 18, 6, h-36, 3); col(k, GD if mood == 'or' else CY, .9); k.fill()
        for i, l in enumerate(L): text(k, l, 84, 18+lh*i+lh/2, 'sb', size, WHITE, 'l', .96)
    tp(cv, w, h, dr, 540, cy, mood, rx=.03, ry=0, bev=14)
    if emo in LOGOS: logo(cv, emo, 540-w/2+50, cy, 44)
    else: put_emoji(cv, emo, 540-w/2+50, cy, 30)
    return h
NS = 9
LOGOS = {'NVDA', 'US', 'ANTH', 'CRWV', 'FR', 'COST', 'PROFIL'}          # tuiles façon icône d'appli (Iconify : logos, simple-icons, flag ; Costco en tuile texte)
def pagination(c, i, n=9):
    """pas de points de défilement : les réseaux les affichent déjà (retour du 12/11)"""
    return
# ---------- fonds Gemini : recadrés en 1080×1920, assombris pour la lecture ----------
@functools.lru_cache(maxsize=8)
def fond(name):
    im = Image.open(f'{D}/fonds/fond_{name}.jpg').convert('RGB')
    sd = np.asarray(im.convert('L'), np.float32).std(1); y1 = len(sd)
    while y1 > 0 and sd[y1-1] < 6: y1 -= 1                 # bande unie laissée par Gemini en bas de certaines images : on la retire
    im = im.crop((0, 0, im.width, y1)); k = max(W/im.width, H/im.height)
    im = im.resize((round(im.width*k), round(im.height*k)), Image.LANCZOS); x0 = (im.width-W)//2; im = im.crop((x0, 0, x0+W, H))
    a = np.asarray(im, np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 200, 520, 1100, 1450, H], [.55, .45, .38, .38, .5, .7])
    a *= 1-dark
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')
def entete(cv, c, num, sujet, titre, glow='FFB020', size=92, flag=None):
    text(c, f"{num} · {sujet}", 540, 232, 'xb', 26, GD2, 'c', .95, 4)
    if flag: logo(cv, flag, 540-tw(c, f"{num} · {sujet}", 'xb', 26, 4)/2-44, 230, 54)
    glow_text(cv, titre, 540, 320, size, top='FFFFFF', bottom='FFE3A0', glow=glow, ga=.55, reflect=False)
GAP = 58                                                                     # espace entre deux cadres de verre (retour du 12/11)
def hauteur(s_, size=29): k0 = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); return int(len(wrap(k0, s_, 'sb', size, 720))*size*1.32+36)
def sujet(cv, c, i, num, nom, titre, fait, rows, mood, lect, pose, bul, glow='FFB020', tsize=92, emo='📰', extra=None):
    entete(cv, c, num, nom, titre, glow, tsize, flag=emo if emo in LOGOS else None)
    h = hauteur(fait); texte(cv, fait, 392+h/2, emo, mood='or'); kh = len(rows)*100+30; ky = 392+h+GAP+kh/2
    kpi(cv, rows, 540, ky, mood, h=kh); y = ky+kh/2+GAP
    if extra: y = extra(cv, c, y)+GAP
    if lect: hl = hauteur(lect); texte(cv, lect, y+hl/2, '💡')
    bb = coin(cv, pose, 200, 1478, 200); bulle_pres(c, bul, bb, 30, .3)
    pagination(c, i)
def growth_value(cv, c, y0):
    """deux cadres côte à côte : GROWTH (croissance) et VALUE (valeur), puis la phrase de lecture"""
    h = 236
    def g(k, w, h):
        text(k, "GROWTH", w/2, 38, 'a', 40, CY, 'c'); text(k, "la croissance", w/2, 76, 'sb', 23, ICE, 'c', .8)
        for j, l in enumerate(("Tech, IA : on paie cher", "les bénéfices de demain.", "Souffre quand", "les taux montent.")): text(k, l, w/2, 122+j*31, 'sb', 23, WHITE if j < 2 else 'FF8A8A', 'c', .95)
    def v(k, w, h):
        text(k, "VALUE", w/2, 38, 'a', 40, GR, 'c'); text(k, "la valeur", w/2, 76, 'sb', 23, ICE, 'c', .8)
        for j, l in enumerate(("Luxe, banques : bénéfices", "déjà là, prix plus sages.", "Résiste quand", "les taux montent.")): text(k, l, w/2, 122+j*31, 'sb', 23, WHITE if j < 2 else '9DF2B5', 'c', .95)
    tp(cv, 400, h, g, 300, y0+h/2, 'bleu', rx=.04, ry=.10, bev=14); tp(cv, 400, h, v, 780, y0+h/2, 'vert', rx=.04, ry=-.10, bev=14)
    put_emoji(cv, '🚀', 300-170, y0+38, 34); put_emoji(cv, '🏛️', 780-170, y0+38, 34)
    y = y0+h+GAP; hl = hauteur(TXT['cac_lect']); texte(cv, TXT['cac_lect'], y+hl/2, '💡')
    return y+hl

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
    def dr(k, w, h):
        text(k, "ABONNE-TOI", 210, 52, 'xb', 50, 'FFC93C', 'l', 1, 2)
        text(k, "à Actions_Benefices", 212, 104, 'b', 30, WHITE, 'l')
        text(k, "pour comprendre la bourse", 212, 146, 'sb', 27, ICE, 'l', .9)
        text(k, "sans jargon, chaque semaine", 212, 182, 'sb', 27, ICE, 'l', .9)
    tp(cv, 860, 210, dr, 540, 960, 'or', rx=.04)
    logo(cv, 'PROFIL', 205, 960, 150); put_emoji(cv, '🔔', 905, 912, 52)
    coin(cv, 'pouce', 540, 1420, 260)
    text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 1475, 'sb', 20, ICE, 'c', .55)
FONDS = ['tirage']+[f[7] for f in FICHES]+['verger']
def render(i):
    cv = fond(FONDS[i]).copy(); s, c = surface()
    if i == 0: s_cover(cv, c)
    elif i == NS-1: s_fin(cv, c)
    else: fiche(cv, c, i-1)
    cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__':
    os.makedirs(f'{D}/out', exist_ok=True); os.makedirs(f'{D}/prev', exist_ok=True)
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    ims = {}
    for i in (only or range(NS)):
        im = render(i); ims[i] = im; im.save(f'{D}/out/tiktok_{i+1}.png'); im.crop((0, 175, W, 1525)).save(f'{D}/out/instagram_{i+1}.png')
    if 'planche' in sys.argv:
        th = [ims[i].resize((360, 640)) for i in sorted(ims)]; P = Image.new('RGB', (360*6, 640*((len(th)+5)//6)))
        [P.paste(t, ((k % 6)*360, (k//6)*640)) for k, t in enumerate(th)]; P.save(f'{D}/prev/planche.png')
    print('ok')
