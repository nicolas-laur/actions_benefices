"""Argumentaire Ubisoft, dans le souterrain derrière la brèche : panneaux de verre 3D (DA PEA/CTO), calés sur le fichier de voix 5.
Toutes les fonctions prennent u = temps écoulé depuis le début du fichier 5 (placé à V5 sur la timeline)."""
import os, sys, math, functools
import numpy as np, cairo
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from nty import text, surface, to_img, rr, col, tw, W, H
from bglass import gpanel, place, glow_text, tilt_quad, with_alpha
from verre_epais import tplace
import cv2
V5 = 26.4
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
CY = '35D6FF'; BL = '2E6BFF'; GD = 'FFC24A'; RD = 'FF4057'; ICE = 'E8EEF8'; INK = '0B0E14'; GR = '3FE08A'
def fmt(v, d=0): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()
def gpill(c, s, x, y, colr, size=30, a=1, fg=INK):
    w = tw(c, s, 'xb', size, 2)+56; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2)
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
@functools.lru_cache(maxsize=1)
def room_img():
    """décor du souterrain + fumée lente (statique : le verre est calculé dessus et mis en cache)"""
    import proto_breche as B
    base = np.asarray(B.room_base().convert('RGB')).astype(np.float32)/255
    rng = np.random.default_rng(7); acc = np.zeros((H, W), np.float32)
    for sc, wg in ((5, 1), (10, .55), (20, .3)):
        n = rng.random((int(H/(W/sc))+2, sc+2)).astype(np.float32); acc += wg*cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
    acc = cv2.GaussianBlur(acc, (0, 0), 28); acc = (acc-acc.min())/(acc.max()-acc.min())
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    smoke = (acc**2.4)*(1-.5*yy)
    base = np.clip(base+smoke[..., None]*np.array([.16, .17, .2], np.float32), 0, 1)
    return base, Image.fromarray((base*255).astype(np.uint8)).convert('RGBA')
def tp(cv, w, h, d, cx, cy, a, mood, rx=0.0, ry=0.0):
    """panneau de verre épais (contenu d inchangé : le biseau s'ajoute autour)"""
    bev = 36 if min(w, h) > 200 else 24; P = bev-10; W2, H2 = w+2*P, h+2*P
    def dd(k, ww, hh): k.translate(P, P); d(k, w, h)
    tplace(cv, room_img()[0], W2, H2, dd, tilt_quad(cx, cy, W2, H2, ry=ry, rx=rx), a, mood, bevel=bev, r=46 if min(w, h) > 200 else 34)
def win(u, a, b, fi=.35, fo=.3): return min(ease((u-a)/fi), 1-ease((u-b)/fo))

# ---------- sections (début, fin) en temps du fichier 5, tirées des pauses de la voix ----------
SEC = dict(fondation=(-4.0, 10.75), ventes=(10.75, 20.45), jeux=(20.45, 29.15), ingame=(29.15, 40.05), polem=(40.05, 46.4),
           janvier=(46.4, 55.35), mille=(55.35, 60.05), tencent=(60.05, 65.95), fin=(65.95, 99))
FRANCH = [("RAYMAN", 6.0), ("ASSASSIN'S CREED", 7.1), ("FAR CRY", 8.6), ("RAINBOW SIX", 9.3)]
def s_fondation(cv, c, u, a):
    def d(k, w, h):
        text(k, "UNE HISTOIRE BRETONNE", w/2, 56, 'xb', 26, ICE, 'c', .85, 6)
        text(k, "les 5 frères Guillemot", w/2, h-58, 'xb', 34, 'D6E6FF', 'c', ease((u-3.2)/.4), 1)
    tp(cv, 820, 400, d, 540, 560, a, 'or', rx=.06+.2*(1-ease((u+1.5)/1)), ry=.07)
    glow_text(cv, "1986", 540, 545, 170, top='FFFFFF', bottom='FFE6B0', glow='F5A623', ga=.7, a=a*ease((u-2.4)/.25), scale=lerp(1.5, 1, back((u-2.4)/.4)), reflect=False)
    for i, (nm, t0) in enumerate(FRANCH):
        k = u-t0
        if k > 0:
            x = 540+((i % 2)*2-1)*205; y = 840+(i//2)*86
            grp(c, a*ease(k/.2), lambda c, nm=nm, x=x, y=y: gpill(c, nm, x, y, 'E8EEF8', 26), dy=14*(1-ease(k/.3)))
SALES = [("2023-24", 2321, "RECORD"), ("2024-25", 1846, ""), ("2025-26", 1525, "")]
def s_ventes(cv, c, u, a):
    k0 = u-10.75
    def d(k, w, h):
        text(k, "VENTES D'UBISOFT PAR EXERCICE", w/2, 52, 'xb', 24, ICE, 'c', .85, 4)
        base = h-90; bw = 150
        for j, (lab, v, tag) in enumerate(SALES):
            cx = w/2+(j-1)*230; t0 = .25+j*.25 if j == 0 else (2.95+(j-1)*1.9)
            g = ease((k0-t0)/.6); hb = 330*v/2400*g
            gr = cairo.LinearGradient(0, base-hb, 0, base); cc = rgb(GD if j == 0 else (CY if j == 1 else RD))
            gr.add_color_stop_rgba(0, *cc, .95); gr.add_color_stop_rgba(1, *cc, .45)
            rr(k, cx-bw/2, base-hb, bw, max(1, hb), 12); k.set_source(gr); k.fill()
            text(k, lab, cx, base+36, 'xb', 22, ICE, 'c', .8, 2)
            if g > .05: text(k, fmt(v*g)+" M€", cx, base-hb-28, 'xb', 28, 'FFFFFF', 'c', ease((k0-t0)/.3))
            if tag and g > .9: text(k, tag, cx, base-hb-66, 'xb', 18, GD, 'c', .9, 3)
        text(k, "Net bookings (chiffre d'affaires publié par Ubisoft)", w/2, h-30, 'sb', 18, ICE, 'c', .55)
    tp(cv, 860, 560, d, 540, 600, a, 'rouge', rx=.06+.25*(1-ease(k0/.4)), ry=-.06)
    ks = u-18.97
    if ks > 0:
        sc = lerp(1.8, 1, back(ks/.3, 2)); s_, cc = surface(); cc.translate(760, 430); cc.rotate(-.12); cc.scale(sc, sc)
        rr(cc, -150, -52, 300, 104, 14); cc.set_line_width(6); col(cc, RD, .95*ease(ks/.1)); cc.stroke()
        text(cc, "-34 %", 0, 0, 'k', 64, RD, 'c', .95*ease(ks/.1), 2); cv.alpha_composite(with_alpha(to_img(s_), a))
GAMES = [("STAR WARS OUTLAWS", "2024", "VENTES « PLUS FAIBLES QUE PRÉVU »", RD, 20.67), ("ASSASSIN'S CREED SHADOWS", "2025", "3 M DE JOUEURS EN 1 SEMAINE", GD, 23.9)]
def s_jeux(cv, c, u, a):
    for j, (nm, yr, info, colr, t0) in enumerate(GAMES):
        k = u-t0
        if k <= 0: continue
        def d(kk, w, h, nm=nm, yr=yr, info=info, colr=colr):
            text(kk, yr, 60, 52, 'xb', 22, ICE, 'l', .7, 3)
            text(kk, nm, w/2, 130, 'k', 46, 'FFFFFF', 'c', 1, 1)
            rr(kk, 50, 190, w-100, 66, 33); col(kk, colr, .95); kk.fill(); text(kk, info, w/2, 223, 'xb', 26, INK, 'c', 1, 1)
        y = 398+j*352
        tp(cv, 860, 270, d, 540+60*(1-ease(k/.4))*(1 if j else -1), y, a*ease(k/.3), 'vert' if j else 'rouge', rx=.05, ry=(1 if j else -1)*(.05+.2*(1-ease(k/.45))))
    kt = u-27.42
    if kt > 0: grp(c, a*ease(kt/.25), lambda c: gpill(c, "LA TENDANCE NE S'INVERSE PAS", 540, 975, RD, 28, fg='FFFFFF'), dy=12*(1-ease(kt/.3)))
def s_ingame(cv, c, u, a):
    k0 = u-29.43
    prog = ease(clamp((k0-6.2)/1.6))                                             # la jauge monte quand « grimpe » est prononcé
    share = lerp(43.7, 60.6, prog) if k0 > 6.2 else 43.7*ease(clamp((k0-.6)/1.2))
    def d(k, w, h):
        text(k, "ARGENT DÉPENSÉ DANS LES JEUX", w/2, 50, 'xb', 24, ICE, 'c', .85, 4)
        text(k, "objets, extensions, abonnements", w/2, 88, 'sb', 24, ICE, 'c', .7*ease((k0-2.5)/.4))
        cx, cy, R = w/2, 330, 170
        k.arc(cx, cy, R, 0, 2*math.pi); k.set_line_width(36); k.set_source_rgba(1, 1, 1, .08); k.stroke()
        k.arc(cx, cy, R, -math.pi/2, -math.pi/2+2*math.pi*share/100); k.set_line_width(36); k.set_line_cap(cairo.LINE_CAP_ROUND)
        g = cairo.LinearGradient(cx-R, cy-R, cx+R, cy+R); g.add_color_stop_rgb(0, *rgb(GD)); g.add_color_stop_rgb(1, *rgb('FF8A3D')); k.set_source(g); k.stroke(); k.set_line_cap(cairo.LINE_CAP_BUTT)
        text(k, fmt(share, 1)+" %", cx, cy-14, 'k', 76, 'FFFFFF', 'c', ease(k0/.4))
        text(k, "des ventes d'Ubisoft", cx, cy+50, 'xb', 22, ICE, 'c', .8*ease(k0/.4))
        text(k, "2024-25 : 43,7 %   →   2025-26 : 60,6 %", w/2, h-40, 'xb', 22, ICE, 'c', .75*ease((k0-7.4)/.4), 1)
    tp(cv, 860, 600, d, 540, 580, a, 'vert', rx=.06+.25*(1-ease(k0/.4)), ry=.06)
    kb = u-35.2
    if kb > 0:
        grp(c, a*ease(kb/.2), lambda c: gpill(c, "924,7 M€ EN 2025-26 · +14,7 %", 540, 960, GD, 28), dy=12*(1-ease(kb/.3)))
    ks = u-37.4
    if ks > 0: glow_text(cv, "6 € SUR 10", 540, 212, 84, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a*ease(ks/.2), scale=lerp(1.4, 1, back(ks/.35)), reflect=False)
POL = [("JEUX EN RETARD", 40.24), ("JEUX ANNULÉS", 41.9), ("POLÉMIQUES À RÉPÉTITION", 43.2)]
def s_polem(cv, c, u, a):
    for j, (s, t0) in enumerate(POL):
        k = u-t0
        if k <= 0: continue
        def d(kk, w, h, s=s):
            kk.arc(70, h/2, 22, 0, 2*math.pi); col(kk, RD); kk.fill(); text(kk, "!", 70, h/2, 'k', 30, 'FFFFFF', 'c', 1)
            text(kk, s, 120, h/2, 'k', 40, 'FFFFFF', 'l', 1, 1)
        tp(cv, 820, 130, d, 540+(1-ease(k/.35))*500, 400+j*170, a*ease(k/.25), 'orange', rx=.05, ry=-.05-.3*(1-ease(k/.4)))
    kh = u-44.5
    if kh > 0: grp(c, a*ease(kh/.25), lambda c: gpill(c, "LE HÉROS D'AC SHADOWS FAIT DÉBAT", 540, 930, 'E8EEF8', 26), dy=12*(1-ease(kh/.3)))
def s_janvier(cv, c, u, a):
    k0 = u-46.66
    def d(k, w, h):
        text(k, "22 JANVIER 2026", w/2, 54, 'xb', 26, ICE, 'c', .85, 5)
        text(k, "6 JEUX ARRÊTÉS", w/2, 150, 'k', 64, 'FFFFFF', 'c', ease((k0-1.2)/.3), 1)
        text(k, "dont le remake de Prince of Persia", w/2, 210, 'sb', 24, ICE, 'c', .7*ease((k0-1.6)/.4))
    tp(cv, 820, 270, d, 540, 400, a, 'rouge', rx=.06+.25*(1-ease(k0/.4)), ry=.06)
    kc = u-49.2
    if kc > 0:
        glow_text(cv, "-39,8 %", 540, 640, 150, top='FFFFFF', bottom='FFC2C9', glow=RD, ga=.8, a=a*ease(kc/.12), scale=lerp(1.7, 1, back(kc/.3, 2)), reflect=False)
        grp(c, a*ease((kc-.3)/.3), lambda c: text(c, "EN UNE SÉANCE, LA PIRE DE SON HISTOIRE", 540, 745, 'xb', 26, ICE, 'c', .85, 2))
    kp = u-52.48
    if kp > 0:
        def d2(k, w, h):
            text(k, "PERTE NETTE 2025-26", w/2, 46, 'xb', 22, ICE, 'c', .85, 4)
            text(k, "-1,24 MD€", w/2, 112, 'k', 60, 'FF8090', 'c', ease((kp-.3)/.2), 1)
        tp(cv, 560, 160, d2, 540, 885, a*ease(kp/.3), 'rouge', rx=.05+.3*(1-ease(kp/.4)), ry=-.06)
def s_mille(cv, c, u, a):
    k0 = u-55.6
    v = 1000-(1000-40)*inout(clamp((k0-1.0)/2.6)) if k0 > 1.0 else 1000.0
    done = k0 > 3.7
    def d(k, w, h):
        text(k, "1 000 € PLACÉS AU SOMMET, LE 18/07/2018", w/2, 56, 'xb', 24, ICE, 'c', .85, 2)
        text(k, "AUJOURD'HUI", w/2, h-56, 'xb', 24, ICE, 'c', .8*ease((k0-1.0)/.3), 4)
    tp(cv, 860, 420, d, 540, 560, a, 'rouge', rx=.06+.25*(1-ease(k0/.4)), ry=-.06)
    if not done: glow_text(cv, fmt(v)+" €", 540, 560, 150, top='FFFFFF', bottom='CFE0FF' if v > 500 else 'FFC2C9', glow=BL if v > 500 else RD, ga=.65, a=a, reflect=False)
    else: glow_text(cv, "MOINS DE 50 €", 540, 560, 118, top='FFFFFF', bottom='FFC2C9', glow=RD, ga=.85, a=a, scale=lerp(1.3, 1, back((k0-3.7)/.3)), reflect=False)
    if k0 > 4.0: grp(c, a*ease((k0-4.0)/.3), lambda c: gpill(c, "-95 % · HORS DIVIDENDES", 540, 860, RD, 28, fg='FFFFFF'))
def s_tencent(cv, c, u, a):
    k0 = u-60.27
    def d(k, w, h):
        text(k, "TENCENT INVESTIT DANS VANTAGE STUDIOS", w/2, 54, 'xb', 22, ICE, 'c', .85, 2)
        text(k, "26,32 % de la filiale", w/2, h-56, 'xb', 28, 'D6E6FF', 'c', ease((k0-1.6)/.4), 1)
    tp(cv, 860, 400, d, 540, 520, a, 'vert', rx=.06+.25*(1-ease(k0/.4)), ry=.06)
    glow_text(cv, "1,16 MD€", 540, 505, 150, top='FFFFFF', bottom='D4FFE2', glow=GR, ga=.7, a=a*ease((k0-.9)/.2), scale=lerp(1.5, 1, back((k0-.9)/.35)), reflect=False)
    for i, (nm, t0) in enumerate((("ASSASSIN'S CREED", 63.0), ("FAR CRY", 64.1), ("RAINBOW SIX", 64.8))):
        k = u-t0
        if k > 0: grp(c, a*ease(k/.2), lambda c, nm=nm, i=i: gpill(c, nm, 540+(i-1)*(300 if i != 1 else 0)+(0 if i != 1 else 0), 820+(70 if i == 1 else 0), 'E8EEF8', 24), dy=12*(1-ease(k/.3)))
def s_fin(cv, c, u, a):
    k0 = u-66.22
    flick = 1 if k0 > .5 else (1 if int(k0*30) % 3 else .4)
    glow_text(cv, "GAME OVER", 540, 360, 150, top='FFFFFF', bottom='FFC2C9', glow=RD, ga=.85, a=a*ease(k0/.08)*flick*(1-.55*ease((k0-1.1)/.4)), reflect=False)
    kq = u-67.3
    if kq > 0:
        glow_text(cv, "OU NOUVELLE", 540, 560, 104, top='FFFFFF', bottom='CFF4FF', glow=CY, ga=.7, a=a*ease(kq/.15), scale=lerp(1.4, 1, back(kq/.3)), reflect=False)
        glow_text(cv, "PARTIE ?", 540, 680, 104, top='FFFFFF', bottom='CFF4FF', glow=CY, ga=.7, a=a*ease((kq-.5)/.15), scale=lerp(1.4, 1, back((kq-.5)/.3)), reflect=False)
    kc = u-68.4
    if kc > 0:
        n = max(0, 9-int(kc/.5))
        grp(c, a*ease(kc/.2), lambda c: text(c, f"CONTINUE ?  {n}", 540, 800, 'k', 44, GD, 'c', .95 if int(kc*4) % 2 == 0 else .6, 4))
    kl = u-69.6
    if kl > 0:
        from logo import logo_symbol
        al = a*ease(kl/.35)
        def lg(c):
            c.push_group(); logo_symbol(c, 410, 900, 38); c.pop_group_to_source(); c.paint_with_alpha(1)
            text(c, "Actions_Benefices", 441, 900, 'b', 27, 'FFFFFF', 'l', 1)
            text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 950, 'sb', 20, ICE, 'c', .65)
            text(c, "Les performances passées ne préjugent pas des performances futures.", 540, 978, 'sb', 20, ICE, 'c', .65)
        grp(c, al, lg)
SCENES = [(s_fondation, 'fondation'), (s_ventes, 'ventes'), (s_jeux, 'jeux'), (s_ingame, 'ingame'), (s_polem, 'polem'), (s_janvier, 'janvier'),
          (s_mille, 'mille'), (s_tencent, 'tencent'), (s_fin, 'fin')]
def draw(cv, u):
    """dessine les panneaux visibles à l'instant u (fondus croisés de 0,35 s entre sections)"""
    s, c = surface()
    for fn, nm in SCENES:
        a0, b0 = SEC[nm]; a = 1.0 if nm == 'fondation' and u < b0-.3 else win(u, a0, b0, .35, .3)
        if a > 0: fn(cv, c, u, a)
    cv.alpha_composite(to_img(s))
def events(off):
    """bruitages de l'argumentaire, en temps global (off = V5)"""
    ev = [(2.4, 'impact'), (3.2, 'swish')] + [(t0, 'pop') for _, t0 in FRANCH]
    ev += [(10.75, 'whoosh'), (11.3, 'tick'), (13.95, 'tick'), (15.85, 'tick'), (18.97, 'thud'), (19.0, 'impact')]
    ev += [(20.45, 'whoosh'), (20.67, 'swish'), (23.9, 'swish'), (27.42, 'pop')]
    ev += [(29.15, 'whoosh'), (30.0, 'tick'), (35.6, 'riser'), (35.2, 'pop'), (37.4, 'impact'), (37.45, 'coins')]
    ev += [(40.05, 'whoosh')] + [(t0, 'thud') for _, t0 in POL] + [(44.5, 'pop')]
    ev += [(46.4, 'whoosh'), (47.86, 'impact'), (49.2, 'crash'), (49.22, 'impact'), (52.48, 'thud')]
    ev += [(55.35, 'whoosh'), (56.6, 'count'), (59.3, 'impact'), (59.6, 'pop')]
    ev += [(60.05, 'whoosh'), (61.17, 'impact'), (61.2, 'coins'), (63.0, 'pop'), (64.1, 'pop'), (64.8, 'pop')]
    ev += [(65.95, 'whoosh'), (66.22, 'crash'), (66.25, 'low'), (67.3, 'swish'), (67.8, 'swish')] + [(68.4+i*.5, 'beep') for i in range(3)] + [(69.6, 'glint')]
    return [(off+t, k) for t, k in ev]
