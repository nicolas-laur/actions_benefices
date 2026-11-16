"""Gabarit des carrousels Actions_Bénéfices (toile 1080×1920, contenu dans y = 200…1500, version Instagram 4:5 découpée en y = 175…1525).
Un épisode écrit seulement son contenu : `from carrousel import *`, ses diapos (fonctions (cv, c)), une fonction render(i), puis sortie(render, NS).
Fonds : <épisode>/fonds/fond_<nom>.jpg (assombris par fond()) ; poses : <épisode>/coin/<pose>.png ; logos : <épisode>/logos/<KEY>.png.
Exemple complet : episodes/2026-11-17_lexique/carrousel.py. Règles de mise en page : docs/formats/carrousel.md."""
import sys, os, math, functools, subprocess
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont
LIB = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(LIB)
D = os.path.dirname(os.path.abspath(sys.argv[0]))                          # dossier de l'épisode (celui du script lancé) : fonds/, coin/, logos/, out/, prev/
sys.path.insert(0, LIB); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
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
LOGOS = set()                                                               # clés des logos de l'épisode (logos/<KEY>.png) : l'épisode fait LOGOS |= {...}
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

# ---------- éléments communs de fin ----------
def bloc_abonne(cv, c, cy=960):
    """cadre « ABONNE-TOI » avec le logo rond de la chaîne (logos/PROFIL.png dans l'épisode) et la cloche"""
    def dr(k, w, h):
        text(k, "ABONNE-TOI", 210, 52, 'xb', 50, 'FFC93C', 'l', 1, 2)
        text(k, "à Actions_Benefices", 212, 104, 'b', 30, WHITE, 'l')
        text(k, "pour comprendre la bourse", 212, 146, 'sb', 27, ICE, 'l', .9)
        text(k, "sans jargon, chaque semaine", 212, 182, 'sb', 27, ICE, 'l', .9)
    tp(cv, 860, 210, dr, 540, cy, 'or', rx=.04)
    logo(cv, 'PROFIL', 205, cy, 150); put_emoji(cv, '🔔', 905, cy-48, 52)
def mention_pedago(c, y=1475):
    text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, y, 'sb', 20, ICE, 'c', .55)

# ---------- sortie ----------
def sortie(render, ns):
    """python3 carrousel.py [numéros…] [planche] : out/tiktok_N.png (1080×1920) et out/instagram_N.png (4:5, y = 175…1525), prev/planche.png"""
    os.makedirs(f'{D}/out', exist_ok=True); os.makedirs(f'{D}/prev', exist_ok=True)
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]; ims = {}
    for i in (only or range(ns)):
        im = render(i); ims[i] = im; im.save(f'{D}/out/tiktok_{i+1}.png'); im.crop((0, 175, W, 1525)).save(f'{D}/out/instagram_{i+1}.png')
    if 'planche' in sys.argv:
        th = [ims[i].resize((360, 640)) for i in sorted(ims)]; P = Image.new('RGB', (360*6, 640*((len(th)+5)//6)))
        [P.paste(t, ((k % 6)*360, (k//6)*640)) for k, t in enumerate(th)]; P.save(f'{D}/prev/planche.png')
    print('ok')
