"""Carrousel « Les News » du 13/11/2026 : l'actualité des marchés de la semaine du 9 au 13 novembre, un sujet par diapo (le fait,
la réaction chiffrée, une piste de lecture), avec un fond Gemini 1930 Technicolor par sujet (fonds/). Même format que le 6/11
(toile 1080×1920, contenu dans y = 200…1500, version Instagram 4:5 découpée en y = 175…1525), verre épais (lib/verre_epais.py).
Chiffres et sources : sources.md. usage : python3 carrousel.py [planche]"""

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
EURUSD = 1.1214                                          # taux de référence BCE du 10/11/2026 (à remplacer par celui du 12/11)
def eur(x): return x/EURUSD
def md(v): return f"{fmt(v, 1 if v < 100 else 0)}{NB}Md€" if v >= 1 else f"{fmt(v*1000, 0)}{NB}M€"
TXT = {
 'nvda_fait': "Selon le Wall Street Journal, le conseil veut évincer Jensen Huang, le fondateur. En cause : sa liaison avec une cadre de Megaspeed, client que Washington soupçonne d'espionner pour la Chine.",
 'nvda_lect': "Le risque « homme clé » : quand un fondateur incarne l'entreprise, sa chute pèse sur l'action, même avec de bons comptes.",
 'inf_fait': "Les prix ont grimpé plus que prévu en octobre aux États-Unis, poussés par l'énergie et l'alimentation (guerre en Iran).",
 'inf_lect': "Guerre → pétrole → inflation → taux. Quand les taux montent, ce qui ne rapporte rien (or, bitcoin) et la tech souffrent.",
 'ipo_fait': "Anthropic a fixé le prix de son entrée en bourse : la plus grosse de l'histoire, attendue au Nasdaq vers le 19 novembre.",
 'ipo_lect': "Le grand test de l'appétit pour l'IA : 17 Md$ de chiffre d'affaires au 3e trimestre, mais 104 Md$ de pertes sur neuf mois.",
 'ia_fait': "Après une chute brutale la semaine d'avant, la tech rebondit : CoreWeave s'envole après ses résultats.",
 'ia_lect': "Le marché ne rejette pas l'IA, il trie : il récompense ceux qui montrent comment ils financent leurs investissements.",
 'cac_fait': "Pendant que la tech américaine tangue, Paris monte, porté par le luxe.",
 'cac_lect': "Taux en hausse : on quitte la croissance chère pour la valeur. C'est la rotation « growth » → « value ».",
 'cost_fait': "Costco reverse une partie de sa trésorerie à ses actionnaires, bien plus que prévu par les analystes.",
 'cost_lect': "Un dividende exceptionnel, c'est l'entreprise qui rend l'argent qu'elle n'a pas besoin d'investir.",
}

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
def logo(cv, key, cx, cy, size=96):
    im = Image.open(f'{D}/logos/{key}.png').convert('RGBA'); k = size/max(im.size); im = im.resize((int(im.width*k), int(im.height*k)), Image.LANCZOS)
    s, c = surface(); rr(c, cx-im.width/2+4, cy-im.height/2+8, im.width, im.height, im.width*.22); col(c, '000000', .35); c.fill()
    cv.alpha_composite(to_img(s)); cv.alpha_composite(im, (int(cx-im.width/2), int(cy-im.height/2)))


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
LOGOS = {'NVDA', 'US', 'ANTH', 'CRWV', 'FR', 'COST'}          # tuiles façon icône d'appli (Iconify : logos, simple-icons, flag ; Costco en tuile texte)
def pagination(c, i, n=9):
    for k in range(n):
        x = 540+(k-(n-1)/2)*24; c.arc(x, 1478, 6 if k == i else 4.5, 0, 2*math.pi); col(c, WHITE, .95 if k == i else .3); c.fill()
# ---------- fonds Gemini : recadrés en 1080×1920, assombris pour la lecture ----------
@functools.lru_cache(maxsize=8)
def fond(name):
    im = Image.open(f'{D}/fonds/fond_{name}.jpg').convert('RGB'); k = max(W/im.width, H/im.height)
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
# ---------- diapos ----------
TOP = [("NVDA", "Nvidia : le PDG sur la sellette"), ("US", "L'inflation repart, la Fed sort l'arme des taux"), ("ANTH", "Anthropic : l'entrée en bourse record"),
       ("CRWV", "Les montagnes russes de l'IA"), ("FR", "Paris tient bon grâce au luxe"), ("COST", "Bonus : le cadeau de Costco")]
def s_cover(cv, c):
    text(c, "SEMAINE DU 9 AU 13 NOVEMBRE 2026", 540, 240, 'sb', 27, ICE, 'c', .85, 4)
    glow_text(cv, "LES NEWS", 540, 360, 170, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    gpill(c, "CE QUI A FAIT BOUGER LES MARCHÉS", 540, 500, GD, 34)
    def dr(k, w, h):
        for j, (e, s_) in enumerate(TOP):
            y = 50+j*86; text(k, s_, 110, y, 'xb', 31, WHITE, 'l', .97)
            if j: k.move_to(30, y-43); k.line_to(w-30, y-43); k.set_line_width(1.2); col(k, WHITE, .12); k.stroke()
    tp(cv, 880, 6*86+14, dr, 540, 600+(6*86+14)/2+20, 'or', rx=.04)
    for j, (e, s_) in enumerate(TOP): logo(cv, e, 540-440+62, 600+20+7+50+j*86, 56)
    bb = coin(cv, 'question', 230, 1478, 250); bulle_pres(c, "Tu as tout suivi ?", bb, 30, .2)
    text(c, "SWIPE", 920, 1420, 'xb', 28, WHITE, 'r', .85, 4); put_emoji(cv, '👉', 965, 1418, 48)
def s_nvda(cv, c):
    sujet(cv, c, 1, 1, "NVIDIA", "LE PDG SUR LA SELLETTE", TXT['nvda_fait'],
          [("L'ACTION, SEMAINE DU 2 AU 6/11", "−9,5 %", "enquête interne révélée", None, RD),
           ("L'ACTION, JEUDI 12/11", NV_12, NV_12_SUB, None, RD),
           ("ANALYSTES À L'ACHAT", "57 sur 62", "avant la crise", None, OR)],
          'rouge', TXT['nvda_lect'], 'choc', "Sans son patron ?!", glow='FF5A3C', emo='NVDA')
def s_inf(cv, c):
    sujet(cv, c, 2, 2, "INFLATION AUX ÉTATS-UNIS", "LA FED VA MONTER SES TAUX", TXT['inf_fait'],
          [("PRIX EN OCTOBRE (ÉTATS-UNIS)", "+0,4 %", "en un mois", None, RD),
           ("HAUSSE DES TAUX EN DÉCEMBRE", "90 %", "de probabilité environ, selon les marchés", None, OR),
           ("TAUX AMÉRICAIN À 10 ANS", "5 %", "le 10/11", None, OR),
           ("L'OR", f"< 4{NB}000 $", f"≈ {OR_EUR}", None, OR)],
          'orange', TXT['inf_lect'], 'inquiet', "Ça chauffe…", tsize=78, emo='US')
def s_ipo(cv, c):
    sujet(cv, c, 3, 3, "ANTHROPIC", "L'ENTRÉE EN BOURSE RECORD", TXT['ipo_fait'],
          [("PRIX PAR ACTION", f"{fmt(eur(70), 0)} à {fmt(eur(78), 0)}{NB}€", "70 à 78 $", None, GD),
           ("VALORISATION", f"jusqu'à {fmt(eur(1404), 0)}{NB}Md€", f"1{NB}404 Md$", None, GD),
           ("ARGENT LEVÉ", f"{fmt(eur(57.75), 0)} à {fmt(eur(64.35), 0)}{NB}Md€", "le record : Aramco, 29,4 Md$ en 2019", None, GR),
           ("POUR LES PARTICULIERS", "jusqu'à 20 %", "des actions proposées", None, GD)],
          'or', TXT['ipo_lect'], 'montre', "Le plus gros de l'histoire !", tsize=82, emo='ANTH')
def s_ia(cv, c):
    sujet(cv, c, 4, 4, "TECH ET IA", "LES MONTAGNES RUSSES", TXT['ia_fait'],
          [("NASDAQ, JEUDI 5/11", "−5,5 %", "en correction", None, RD),
           ("COREWEAVE, MERCREDI 11/11", "+24,7 %", "après ses résultats", None, GR),
           ("NASDAQ, MERCREDI 11/11", "+1,6 %", None, None, GR)],
          'bleu', TXT['ia_lect'], 'rire', "Accroche-toi !", glow='35D6FF', tsize=86, emo='CRWV')
def s_cac(cv, c):
    sujet(cv, c, 5, 5, "BOURSE DE PARIS", "LE LUXE PORTE LE CAC 40", TXT['cac_fait'],
          [("CAC 40, JEUDI 12/11", CAC_12, CAC_12_SUB, None, GR),
           ("LVMH / HERMÈS / BURBERRY", "+2 % / +1,9 % / +9,4 %", "jeudi 12/11", None, GR)],
          'vert', None, 'pouce', "Cocorico !", tsize=80, extra=growth_value, emo='FR')
def s_cost(cv, c):
    sujet(cv, c, 6, "BONUS", "COSTCO", "LE CHÈQUE SURPRISE", TXT['cost_fait'],
          [("DIVIDENDE EXCEPTIONNEL", f"{fmt(eur(30), 1)}{NB}€", "par action (30 $)", None, GR),
           ("AU TOTAL", md(eur(13.3)), "13,3 Md$ reversés", None, GR),
           ("L'ACTION, MERCREDI 11/11", "+2 %", None, None, GR)],
          'vert', TXT['cost_lect'], 'joie', "Merci patron !", emo='COST')
RET = [("NVDA", "Nvidia : la crise de gouvernance fait trembler la star de l'IA"), ("US", "Inflation : la Fed s'apprête à remonter ses taux"),
       ("ANTH", "Anthropic : la plus grosse entrée en bourse de l'histoire"), ("CRWV", "IA : le marché trie les gagnants"),
       ("FR", "Paris : le luxe amortit le choc"), ("COST", "Costco : 30 $ par action en cadeau")]
def s_ret(cv, c):
    entete(cv, c, "EN BREF", "CETTE SEMAINE", "CE QU'IL FAUT RETENIR", size=78)
    def dr(k, w, h):
        for j, (e, s_) in enumerate(RET):
            y = 56+j*112; L = wrap(k, s_, 'xb', 28, w-150)
            for m, l in enumerate(L): text(k, l, 110, y-(len(L)-1)*17+m*34, 'xb', 28, WHITE, 'l', .96)
            if j: k.move_to(30, y-56); k.line_to(w-30, y-56); k.set_line_width(1.2); col(k, WHITE, .12); k.stroke()
    tp(cv, 880, 6*112, dr, 540, 430+6*112/2, 'or', rx=.04)
    for j, (e, s_) in enumerate(RET): logo(cv, e, 540-440+62, 430+56+j*112, 60)
    bb = coin(cv, 'montre', 230, 1478, 230); bulle_pres(c, "Enregistre-le 📌"[:-2], bb, 30, .25)
    pagination(c, 7)
def s_fin(cv, c):
    glow_text(cv, "ET TOI,", 540, 330, 124, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5)
    glow_text(cv, "QUELLE NEWS", 540, 470, 96, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    glow_text(cv, "T'A MARQUÉ ?", 540, 590, 104, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7)
    text(c, "Dis-le en commentaire", 540, 730, 'sb', 34, ICE, 'c', .85); put_emoji(cv, '👇', 540, 790, 52)
    texte(cv, "Les marchés réagissent aux surprises : inflation, patrons, introductions en bourse. Garde le cap sur le long terme.", 920)
    coin(cv, 'question', 540, 1330, 280)
    c.push_group(); logo_symbol(c, 395, 1398, 40); c.pop_group_to_source(); c.paint()
    text(c, "Actions_Benefices", 428, 1398, 'b', 28, WHITE, 'l')
    text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 1462, 'sb', 20, ICE, 'c', .55)
# chiffres de clôture du 12/11 (mis à jour le soir)
NV_12, NV_12_SUB = "≈ −6 %", "avant l'ouverture"
CAC_12, CAC_12_SUB = f"≈ 8{NB}390 pts", "+0,7 % en séance"
OR_EUR = f"3{NB}560{NB}€ l'once"
SLIDES = [s_cover, s_nvda, s_inf, s_ipo, s_ia, s_cac, s_cost, s_ret, s_fin]
FONDS = ['couverture', 'nvidia', 'inflation', 'ipo', 'ia', 'paris', 'costco', 'couverture', 'couverture']
assert len(SLIDES) == NS
def render(i):
    cv = fond(FONDS[i]).copy(); s, c = surface()
    SLIDES[i](cv, c); cv.alpha_composite(to_img(s)); return cv.convert('RGB')
if __name__ == '__main__':
    os.makedirs(f'{D}/out', exist_ok=True); os.makedirs(f'{D}/prev', exist_ok=True)
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    ims = {}
    for i in (only or range(NS)):
        im = render(i); ims[i] = im; im.save(f'{D}/out/tiktok_{i+1}.png'); im.crop((0, 175, W, 1525)).save(f'{D}/out/instagram_{i+1}.png')
    if 'planche' in sys.argv:
        th = [ims[i].resize((360, 640)) for i in sorted(ims)]; P = Image.new('RGB', (360*5, 640*((len(th)+4)//5)))
        [P.paste(t, ((k % 5)*360, (k//5)*640)) for k, t in enumerate(th)]; P.save(f'{D}/prev/planche.png')
    print('ok')
