"""Série Krachs, ép. 1 : 2008. Corbeille 3D (euphorie -> panique), verre 3D, CAC 40 vs S&P 500.
Pas de barre de progression (TikTok a la sienne). Chiffre choc visible à l'image 0.
usage : python km.py png t1 t2 ... | python km.py seg out.mp4 f0 f1 | python km.py info"""
import sys, math, re, random, subprocess, os, functools, csv
import numpy as np, cairo
from PIL import Image, ImageEnhance
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc')
from bglass import *
FPS = 60; NB = ' '
RD = 'FF3B3B'; GR = '3FE08A'; AMB = 'FFC24A'; ICE = 'E8EEF8'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def win(t, a, b, fi=.3, fo=.25):
    if t < a or t > b: return 0.0
    return min(1.0 if a <= 0 else ease((t-a)/fi), clamp((b-t)/fo))
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

# ---------- minutage (provisoire tant que la voix n'est pas là ; recalé sur les pauses ensuite) ----------
T = dict(hook=0.0, date=7.18, lehman=12.73, stamp=14.05, six=14.84, b42=16.35, b46=18.06, spx=18.92, cac=21.76, cacm=22.96, today=24.49, cacv=25.23,
         spxv=28.03, x4=29.71, x4b=30.5, x4c=31.41, cta=32.4, buy=33.99, end=35.6)
DUR = T['end']
CAPS = [(T['hook'], "[7 764 euros]."), (2.03, "C'est ce que valent aujourd'hui 1 000 euros placés dans le S&P 500"), (5.19, "la veille de la faillite de Lehman Brothers."),
        (T['date'], "Vendredi [12 septembre 2008]."), (9.25, "Tu places 1 000 euros dans le [CAC 40],"), (11.1, "et 1 000 dans le [S&P 500]."),
        (T['lehman'], "Lundi,"), (13.36, "Lehman Brothers [s'effondre]."), (T['six'], "En six mois,"), (15.52, "le CAC perd [42 %]."), (17.23, "Le S&P,"), (T['b46'], "[46 %]."),
        (T['spx'], "Le S&P retrouve son niveau"), (20.27, "en [2 ans et 3 mois]."), (T['cac'], "Le CAC, lui…"), (T['cacm'], "[5 ans et 5 mois]."),
        (T['today'], "Et aujourd'hui ?"), (T['cacv'], "Ton CAC vaut [1 831 euros]."), (27.25, "Ton S&P :"), (T['spxv'], "[7 764]."),
        (T['x4'], "Même krach,"), (T['x4b'], "même mise."), (T['x4c'], "[Quatre fois plus]."), (T['cta'], "Au prochain krach…"), (33.39, "et toi,"), (T['buy'], "tu [achètes] ?")]
RED_CAPS = {13.36, 15.52, T['b46'], T['buy']}; GREEN_CAPS = {T['hook'], T['spxv'], T['x4c']}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('S&P 500', 'S&P'+NB+'500').replace('CAC 40', 'CAC'+NB+'40')
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1352, size=46, a=1):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 820: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, '0B0B0E' if hl != RD else WHITE, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- fond : boucles 3D euphorie / panique ----------
SEQ = {'up': '/home/claude/krach08/seq_up', 'down': '/home/claude/krach08/seq_down'}
@functools.lru_cache(maxsize=24)
def fr(mode, i):
    p = f'{SEQ[mode]}/f{i:04d}.png'
    if not os.path.exists(p):
        ks = sorted(os.listdir(SEQ[mode])) if os.path.isdir(SEQ[mode]) else []
        ks = [k for k in ks if k.endswith('.png')]
        p = f'{SEQ[mode]}/{ks[0]}' if ks else '/tmp/k08/t_up.png' if mode == 'up' else '/tmp/k08/t_dn.png'
    return Image.open(p).convert('RGB').resize((W, H), Image.BICUBIC)
def loop(mode, t):
    f = (t*30) % 60; i = int(f//2)*2; u = (f-i)/2
    a = fr(mode, i+1); b = fr(mode, (i+2) % 60+1)
    return Image.blend(a, b, u) if u > .05 else a
def panic(t):
    """0 = euphorie, 1 = panique"""
    if t < T['stamp']: return 0.0
    if t < T['spx']: return 1.0
    return 1-inout((t-T['spx'])/(T['today']-T['spx']))
def background(t, dim, blur, zoom):
    m = panic(t)
    im = loop('up', t) if m < .01 else loop('down', t) if m > .99 else Image.blend(loop('up', t), loop('down', t), m)
    if zoom != 1:
        w, h = int(W*zoom), int(H*zoom); im = im.resize((w, h), Image.BILINEAR).crop(((w-W)//2, (h-H)//2, (w-W)//2+W, (h-H)//2+H))
    if blur > .5: im = lowblur(im, blur, 2)
    return ImageEnhance.Brightness(im).enhance(dim).convert('RGBA')

# ---------- données du graphique ----------
PATH = []
with open('/home/claude/krach08/path.csv') as f:
    for r in csv.DictReader(f):
        y, m, d = map(int, r[list(r.keys())[0]].split('-'))
        PATH.append((y+(m-1)/12+d/365, float(r['cac']), float(r['spx'])))
Y0, Y1 = 2008.70, 2014.5
def partial(series, u):
    n = len(series); k = u*(n-1); i = int(k)
    pts = series[:i+1]
    if i < n-1: f_ = k-i; a, b = series[i], series[i+1]; pts = pts+[(a[0]+(b[0]-a[0])*f_, a[1]+(b[1]-a[1])*f_)]
    return pts
def series(idx): return [(p[0], p[idx]) for p in PATH]
def at_date(yr):
    for i, p in enumerate(PATH):
        if p[0] >= yr: return i/(len(PATH)-1)
    return 1.0
U_TROUGH = at_date(2009.18); U_SPX = at_date(2010.97); U_CAC = at_date(2014.13)

# ---------- scènes ----------
def sA(cv, c, t, a):
    """accroche : 7 764 € lisible à l'image 0, impact (zoom + flash)"""
    z = lerp(1.25, 1.0, back(t/.45, 1.3))
    glow_text(cv, "7 764 €", 540, 560, 210, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.75, a=a, scale=z)
    def sub(c):
        text(c, "1 000 € PLACÉS LA VEILLE", 540, 735, 'xb', 40, WHITE, 'c', 1, 2)
        text(c, "DE LA FAILLITE DE LEHMAN BROTHERS", 540, 790, 'xb', 40, WHITE, 'c', 1, 2)
    grp(c, a*ease((t-.25)/.3), sub)
    def pl(c):
        w = tw(c, "S&P 500 · 2008 → 2026", 'xb', 26, 1)+50; rr(c, 540-w/2, 840, w, 54, 27); col(c, AMB); c.fill(); text(c, "S&P 500 · 2008 → 2026", 540, 867, 'xb', 26, '0B0B0E', 'c', 1, 1)
    grp(c, a*ease((t-.6)/.3), pl)

def badge(c, a=1):
    """identité de série en haut, à la place de l'ancienne barre de progression"""
    rr(c, 70, 118, 250, 54, 10); col(c, RD, a); c.fill(); text(c, "KRACHS", 195, 145, 'a', 34, WHITE, 'c', a, 4)
    text(c, "ÉPISODE 1 · 2008", 340, 145, 'xb', 28, WHITE, 'l', .9*a, 2)

def tile(name, val, accent):
    def d(k, w, h):
        text(k, name, w/2, 62, 'sb', 30, ICE, 'c', 1, 3); text(k, val, w/2, 150, 'a', 92, WHITE, 'c')
        k.set_line_width(4); col(k, accent); k.move_to(w/2-40, 205); k.line_to(w/2+40, 205); k.stroke()
    return gpanel(380, 240, d, tint='DDEBFF', ta=.08, edge=.7)
def sB(cv, c, t, a):
    t0 = T['date']; e = ease((t-t0)/.45)
    glow_text(cv, "12.09.2008", 540, 470, 150, top='FFFFFF', bottom='DDEBFF', glow='7FA8FF', ga=.45, a=a*e, scale=lerp(1.2, 1, back((t-t0)/.45)))
    grp(c, a*e, lambda c: text(c, "VENDREDI · LA VEILLE", 540, 620, 'sb', 32, AMB, 'c', 1, 6))
    for i, (nm, x, ry, t1) in enumerate((("CAC 40", 300, .28, 10.3), ("S&P 500", 780, -.28, 12.0))):
        e2 = ease((t-t1)/.4)
        if e2 > 0: place(cv, tile(nm, "1 000 €", AMB), tilt_quad(x, 880+50*(1-e2), 380, 240, ry=ry*(1+(1-e2)), rx=.06), a*e2, 22, .5)

def sC(cv, c, t, a):
    """lundi 15 sept. : faillite. flash rouge + tampon"""
    t0 = T['lehman']; k = t-t0
    kk = t-T['stamp']
    if 0 <= kk < .3:
        s, c2 = surface(); c2.set_source_rgba(1, .2, .15, .6*(1-kk/.3)); c2.paint(); cv.alpha_composite(to_img(s))
    glow_text(cv, "15.09.2008", 540, 470, 150, top='FFFFFF', bottom='FF9A9A', glow='FF3B3B', ga=.7, a=a, scale=lerp(1.35, 1, back(k/.35)))
    def stamp(c):
        s_ = lerp(2.2, 1, back(clamp((t-T['stamp'])/.3), 1.2)); c.save(); c.translate(540, 650); c.rotate(-.08); c.scale(s_, s_)
        w = tw(c, "FAILLITE", 'a', 96, 6)+60; rr(c, -w/2, -64, w, 128, 10); c.set_line_width(8); col(c, RD); c.stroke()
        text(c, "FAILLITE", 0, 0, 'a', 96, RD, 'c', 1, 6); c.restore()
        text(c, "LEHMAN BROTHERS · 4e BANQUE D'AFFAIRES US", 540, 790, 'sb', 28, ICE, 'c', ease((t-T['stamp']-.3)/.3), 2)
    grp(c, a*clamp((t-T['stamp'])/.08), stamp)

PX, PY, PW, PH = 70, 560, 940, 640
def sD(cv, c, t, a):
    """la chute puis la remontée : courbes CAC (ambre) / S&P (blanc glacé) sur le verre"""
    t0 = T['six']
    if t < T['spx']: u = lerp(0, U_TROUGH, inout((t-t0)/(T['b46']-t0)))
    elif t < T['cac']: u = lerp(U_TROUGH, U_SPX, inout((t-T['spx'])/1.4))
    else: u = lerp(U_SPX, U_CAC, inout((t-T['cac'])/(T['cacm']-T['cac'])))
    X0, X1, YT, YB = 70, PW-50, 120, PH-90
    zx = inout((t-T['spx'])/1.4); Yr = lerp(2009.45, Y1, zx)      # l'axe du temps s'élargit quand la remontée commence
    def px(yr, v): return X0+(yr-Y0)/(Yr-Y0)*(X1-X0), YB-(v-450)/(1450-450)*(YB-YT)
    def chart(k, w, h):
        text(k, "TES 1 000 € PLACÉS LE 12.09.2008", 40, 52, 'sb', 24, ICE, 'l', 1, 2)
        y1000 = px(0, 1000)[1]; k.set_dash([10, 8]); k.set_line_width(2); col(k, WHITE, .45); k.move_to(X0, y1000); k.line_to(X1, y1000); k.stroke(); k.set_dash([])
        text(k, "1 000 €", X1, y1000-20, 'xb', 22, WHITE, 'r', .7)
        for yy, lb in ((2008.75, "OCT. 08"), (2009.0, "JANV. 09"), (2009.25, "AVR. 09")): text(k, lb, px(yy, 0)[0], h-40, 'm', 22, SUB, 'c', 1-zx)
        for yy in (2010, 2011, 2012, 2013, 2014): text(k, str(yy), px(yy, 0)[0], h-40, 'm', 22, SUB, 'c', zx)
        for idx, colr, lab in ((1, AMB, "CAC 40"), (2, ICE, "S&P 500")):
            pts = [p for p in partial(series(idx), u)]
            if len(pts) < 2: continue
            for a_, lw in ((.1, 24), (.22, 12), (1, 5)):
                k.move_to(*px(*pts[0]))
                for q in pts[1:]: k.line_to(*px(*q))
                k.set_line_width(lw); k.set_line_join(1); col(k, colr, a_); k.stroke()
            x, y = px(*pts[-1]); k.arc(x, y, 9, 0, 2*math.pi); col(k, colr); k.fill()
            text(k, f"{pts[-1][1]:,.0f} €".replace(',', ' '), min(x+18, w-130), y+(-30 if idx == 1 else 34), 'xb', 30, colr, 'l')
        # creux
        for idx, lab, tt, dy in ((1, "−42 %", T['b42'], 60), (2, "−46 %", T['b46'], 110)):
            if t < tt: continue
            tr = min(series(idx), key=lambda p: p[1]); x, y = px(*tr); s = back((t-tt)/.35); w_ = tw(k, lab, 'a', 44)+30
            k.save(); k.translate(x+(-95 if idx == 1 else 95), y+75); k.scale(s, s); rr(k, -w_/2, -32, w_, 64, 12); col(k, RD, 1-zx); k.fill(); text(k, lab, 0, 0, 'a', 44, WHITE, 'c', 1-zx); k.restore()
        # retours au niveau de départ
        for yr, lab, tt, colr in ((2010.97, "2 ANS 3 MOIS", 20.3, ICE), (2014.13, "5 ANS 5 MOIS", T['cacm'], AMB)):
            if t < tt: continue
            x, y = px(yr, 1000); s = back((t-tt)/.35); k.set_line_width(3); col(k, colr); k.arc(x, y, 16*s, 0, 2*math.pi); k.stroke()
            w_ = tw(k, lab, 'xb', 30)+30; bx_ = clamp(x-w_/2, 20, w-20-w_)
            rr(k, bx_, y-110, w_, 54, 10); col(k, colr, .95*clamp((t-tt)/.2)); k.fill(); text(k, lab, bx_+w_/2, y-83, 'xb', 30, '0B0B0E', 'c', clamp((t-tt)/.2))
    e = ease((t-t0)/.45)
    place(cv, gpanel(PW, PH, chart, tint='DDEBFF', ta=.07, edge=.7), tilt_quad(540, PY+PH/2+60*(1-e), PW, PH, ry=-.12-.4*(1-e), rx=.06), a*e, 26, .55)
    big = "−42 %" if t < T['b46'] else "−46 %"
    if T['b42'] <= t < T['spx']-.2: glow_text(cv, big, 540, 400, 170, top='FFFFFF', bottom='FF9A9A', glow='FF3B3B', ga=.7, a=a*ease((t-T['b42'])/.2)*clamp((T['spx']-.2-t)/.25), scale=lerp(1.25, 1, back((t-(T['b42'] if big == "−42 %" else T['b46']))/.35)))
    elif t < T['b42']: glow_text(cv, "6 MOIS", 540, 400, 150, top='FFFFFF', bottom='FF9A9A', glow='FF3B3B', ga=.5, a=a*e*clamp((T['b42']-t)/.2))
    elif t < T['cac']: glow_text(cv, "S&P 500", 540, 400, 140, top='FFFFFF', bottom='DDEBFF', glow='7FA8FF', ga=.45, a=a*ease((t-T['spx'])/.3)*clamp((T['cac']-t)/.2))
    else: glow_text(cv, "CAC 40", 540, 400, 140, top='FFFFFF', bottom='FFD27A', glow='FFB020', ga=.5, a=a*ease((t-T['cac'])/.3))

BASE = 470; SCL = 340/7764
def sE(cv, c, t, a):
    """aujourd'hui : barres qui jaillissent, celle du S&P traverse le verre"""
    tc, ts = T['cacv'], T['spxv']
    def chart(k, w, h):
        text(k, "TES 1 000 € AUJOURD'HUI", 40, 52, 'sb', 24, ICE, 'l', 1, 2)
        k.set_line_width(2); col(k, WHITE, .3); k.move_to(40, BASE); k.line_to(w-40, BASE); k.stroke()
        for i, (nm, v, cl, t0) in enumerate((("CAC 40", 1831, AMB, tc), ("S&P 500", 7764, ICE, ts))):
            x = 170+i*360; text(k, nm, x+90, BASE+46, 'xb', 32, WHITE, 'c', .5+.5*(t >= t0))
            if t < t0 or i == 1: continue
            hh = max(6, v*SCL*back((t-t0)/.5, 1.2)); rr(k, x, BASE-hh, 180, hh, 12); col(k, cl); k.fill()
            text(k, f"{int(v*clamp((t-t0)/.5)):,} €".replace(',', ' '), x+90, BASE-hh-30, 'xb', 40, WHITE)
        text(k, "indices hors dividendes · change €/$ BCE · 15 oct. 2026", w/2, h-34, 'm', 20, SUB, 'c', .85)
    e = ease((t-T['today'])/.45); PXE, PYE, PWE, PHE = 140, 640, 800, 600
    place(cv, gpanel(PWE, PHE, chart, tint='DDEBFF', ta=.07, edge=.7), [(PXE, PYE+50*(1-e)), (PXE+PWE, PYE+50*(1-e)), (PXE+PWE, PYE+PHE+50*(1-e)), (PXE, PYE+PHE+50*(1-e))], a*e, 26, .55)
    glow_text(cv, "ET AUJOURD'HUI ?", 540, 420, 110, top='FFFFFF', bottom='DDEBFF', glow='7FA8FF', ga=.4, a=a*e*clamp((ts-t)/.25))
    if t >= ts:
        def d(c):
            x = PXE+170+360; bot = PYE+BASE; g = ease((t-ts)/.35); top = lerp(bot, 120, g)
            for a_, ex in ((.10, 40), (.2, 20), (.35, 8)): rr(c, x-ex, top, 180+2*ex, bot-top+ex, 16); col(c, GR, a_); c.fill()
            gr = cairo.LinearGradient(0, top, 0, bot); gr.add_color_stop_rgb(0, *hx('E9FFF1')[:3]); gr.add_color_stop_rgb(.3, *hx(GR)[:3]); gr.add_color_stop_rgb(1, *hx('128A4A')[:3])
            rr(c, x, top, 180, bot-top, 12); c.set_source(gr); c.fill()
            if top < PYE:
                e2 = clamp((t-ts-.18)/.9); rnd = random.Random(4)
                for k in range(16):
                    vx, vy = rnd.uniform(-420, 420), rnd.uniform(-700, -200); s_ = rnd.uniform(10, 26); r_ = rnd.uniform(0, 6.28); tt = t-ts-.18
                    if tt < 0: break
                    sx, sy = x+90+vx*tt, PYE+vy*tt+900*tt*tt
                    c.save(); c.translate(sx, sy); c.rotate(r_+tt*rnd.uniform(-8, 8)); c.move_to(0, -s_); c.line_to(s_*.6, s_*.4); c.line_to(-s_*.5, s_*.6); c.close_path()
                    col(c, 'EAF2FF', .35*(1-e2)); c.fill_preserve(); col(c, WHITE, .7*(1-e2)); c.set_line_width(1.5); c.stroke(); c.restore()
        grp(c, a, d)
        glow_text(cv, "7 764 €", 330, 400, 110, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*ease((t-ts-.2)/.25), scale=lerp(1.3, 1, back((t-ts-.2)/.4)))

def sF(cv, c, t, a):
    grp(c, a*ease((t-T['x4'])/.25), lambda c: text(c, "MÊME KRACH", 540, 300, 'a', 80, WHITE, 'c', 1, 3))
    grp(c, a*ease((t-T['x4b'])/.25), lambda c: text(c, "MÊME MISE", 540, 400, 'a', 80, WHITE, 'c', 1, 3))
    t0 = T['x4c']; e = ease((t-t0)/.3)
    glow_text(cv, "×4,2", 540, 700, 330, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*e, scale=lerp(1.4, 1, back((t-t0)/.45)))
    grp(c, a*ease((t-t0-.4)/.3), lambda c: text(c, "S&P 500 : 7 764 €  ·  CAC 40 : 1 831 €", 540, 960, 'xb', 32, ICE, 'c', 1, 1))

def sG(cv, c, t, a):
    t0 = T['cta']; e = ease((t-t0)/.35)
    glow_text(cv, "AU PROCHAIN", 540, 470, 120, top='FFFFFF', bottom='FF9A9A', glow='FF3B3B', ga=.55, a=a*e)
    glow_text(cv, "KRACH…", 540, 610, 150, top='FFFFFF', bottom='FF9A9A', glow='FF3B3B', ga=.65, a=a*e)
    e2 = ease((t-T['buy'])/.3)
    glow_text(cv, "TU ACHÈTES ?", 540, 820, 130, top='FFFFFF', bottom='9DFFC6', glow='2FD27A', ga=.7, a=a*e2, scale=lerp(1.3, 1, back((t-T['buy'])/.4)))
    al = ease((t-T['buy']-.3)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 1135, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 445, 1135, 'b', 30, WHITE, 'l', al)
    grp(c, a, lg)
    grp(c, a*ease((t-T['buy']-.6)/.4), lambda c: text(c, "ÉPISODE 2 : LA BULLE INTERNET DE 2000", 540, 1210, 'sb', 26, AMB, 'c', 1, 2))

SCENES = [(sA, 0.0, T['date'], .62, 3), (sB, T['date']-.1, T['lehman'], .55, 6), (sC, T['lehman'], T['six'], .6, 4), (sD, T['six']-.1, T['today'], .45, 9),
          (sE, T['today']-.1, T['x4'], .45, 9), (sF, T['x4']-.1, T['cta'], .5, 8), (sG, T['cta']-.1, DUR+1, .5, 8)]
SHAKES = [(0.0, 14), (T['lehman'], 18), (T['stamp'], 26), (T['b42'], 8), (T['b46'], 8), (T['spxv'], 22), (T['x4c'], 12)]
def frame(t):
    dim, blur = .6, 6
    for fn, a0, b0, dm, bl in SCENES:
        if a0 <= t < b0: dim, blur = dm, bl
    # zoom lent sur la scène 3D, coup de zoom à chaque changement d'acte
    z = 1.02+.05*((t % 6)/6)
    if T['stamp'] <= t < T['stamp']+.4: z += .12*(1-ease((t-T['stamp'])/.4))
    if t < .45: z += .15*(1-ease(t/.45))
    cv = background(t, dim, blur, z); darkspot(cv, 540, 700, 700, 720, .55)
    darken_band(cv, 1240, 1470, .6)
    s, c = surface()
    for fn, a0, b0, *_ in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else win(t, a0, b0, .3, .25)
        if al > 0: fn(cv, c, t, al)
    if t >= T['date']-.1: badge(c, ease((t-T['date']+.1)/.3))
    k = cap_at(t)
    if k is not None and t < DUR:
        st = CAPS[k][0]; a = 1.0 if st == 0 else ease((t-st)/.12)
        hl = RD if st in RED_CAPS else GR if st in GREEN_CAPS else AMB
        grp(c, a, lambda c: caption(c, parse(CAPS[k][1]), hl), 14*(1-a))
    cv.alpha_composite(to_img(s))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(6, 6, 8, 255))
    return finish(cv, t, 5.0)

def events():
    return [(0.0, 'impact'), (0.0, 'boom'), (T['date'], 'swish'), (10.3, 'pop'), (12.0, 'pop'), (T['lehman']-.8, 'riser'),
            (T['lehman'], 'impact'), (T['stamp'], 'crash'), (T['stamp'], 'impact'), (T['six'], 'swish'), (T['b42'], 'low'), (T['b46'], 'low'),
            (20.3, 'glint'), (T['cacm'], 'glint'), (T['today'], 'swish'), (T['cacv'], 'pop'), (T['spxv']-.8, 'riser'), (T['spxv'], 'boom'),
            (T['spxv']+.18, 'shatter'), (T['spxv'], 'coins'), (T['x4'], 'tick'), (T['x4b'], 'tick'), (T['x4c'], 'impact'), (T['cta'], 'swish'), (T['buy'], 'pop'), (T['buy']+.3, 'click')]

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/krach08/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'/home/claude/krach08/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
