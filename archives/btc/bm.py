"""Bitcoin : 35 s, voix off (ElevenLabs, fournie par Nicolas). Pluie de pièces ₿ floue (Blender) + verre 3D + graphiques explosifs.
Promesse « 2 pizzas = 742 M€ » visible dès 0:00."""
import sys, math, re, random, subprocess, os, functools
import numpy as np, cairo
from PIL import Image
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc')
from bglass import *
FPS = 60; DUR = 35.2; NB = ' '
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def win(t, a, b, fi=.3, fo=.25):
    if t < a or t > b: return 0.0
    return min(1.0 if a <= 0 else ease((t-a)/fi), clamp((b-t)/fo))

# ---------- sous-titres (pauses mesurées sur la voix) ----------
CAPS = [(0.0, "Deux pizzas à [742 millions d'euros]."), (3.27, "C'est ce qu'un développeur a payé en [2010],"), (5.45, "avec [10 000 bitcoins]."),
        (7.47, "À l'époque, ça valait [41 dollars]."), (10.04, "[1 000 €] dans le bitcoin il y a 5 ans ?"), (12.11, "[1 500 euros]."),
        (13.42, "Il y a 10 ans ?"), (14.36, "[127 000 euros]."), (15.97, "Et il y a 13 ans…"), (17.31, "plus de [700 000 euros]."),
        (19.27, "Mais pour les garder, il fallait tenir"), (20.77, "quand il a perdu plus de [75 %]…"), (22.93, "[deux fois]."),
        (23.67, "Et aujourd'hui, il est encore"), (25.47, "[34 %] sous son record."), (28.19, "Alors, opportunité ou [piège] ?"),
        (30.58, "Dis-moi en commentaire :"), (31.88, "tu [achètes],"), (32.67, "tu [vends]"), (33.40, "ou tu [attends] ?")]
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k

# ---------- fond : pluie de pièces ----------
SEQ = '/home/claude/btc/seq_rain'
@functools.lru_cache(maxsize=12)
def rain(i):
    p = f'{SEQ}/f{i+1:04d}.png'
    if not os.path.exists(p): p = f'{SEQ}/f0001.png'
    return Image.open(p).convert('RGB').resize((W, H), Image.BILINEAR)
def background(t, dim, blur):
    f = (t*30) % 150; i = int(f); fr = f-i
    im = rain(i); im = Image.blend(im, rain((i+1) % 150), fr) if fr > .05 else im
    if blur > .5: im = lowblur(im, blur, 2)
    return ImageEnhance.Brightness(im).enhance(dim).convert('RGBA')

def burst(c, x, y, r0, r1, n=18, color=GOLD, a=1, seed=3, grow=1.0):
    rnd = random.Random(seed)
    for k in range(n):
        ang = 2*math.pi*k/n+rnd.uniform(-.08, .08); ra = r0+rnd.uniform(0, (r1-r0)*.4)*grow; rb = r1*rnd.uniform(.7, 1.1)*grow
        g = cairo.LinearGradient(x+ra*math.cos(ang), y+ra*math.sin(ang), x+rb*math.cos(ang), y+rb*math.sin(ang))
        g.add_color_stop_rgba(0, *hx(color, .9*a)); g.add_color_stop_rgba(1, *hx(color, 0)); c.set_source(g); c.set_line_width(rnd.uniform(3, 7)); c.set_line_cap(1)
        c.move_to(x+ra*math.cos(ang), y+ra*math.sin(ang)); c.line_to(x+rb*math.cos(ang), y+rb*math.sin(ang)); c.stroke()
    for k in range(40):
        ang = rnd.uniform(0, 2*math.pi); d = rnd.uniform(r0, r1*1.2)*grow; rr_ = rnd.uniform(2, 6)
        col(c, rnd.choice((GOLD, CREAM, ORANGE)), a*rnd.uniform(.4, 1)); c.arc(x+d*math.cos(ang), y+d*math.sin(ang), rr_, 0, 2*math.pi); c.fill()
def partial(pts, u):
    """points d'une polyligne jusqu'à la fraction u de l'axe x"""
    x0, x1 = pts[0][0], pts[-1][0]; xe = x0+(x1-x0)*u; out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if b[0] <= xe: out.append(b)
        else:
            f = (xe-a[0])/(b[0]-a[0]); out.append((xe, a[1]+(b[1]-a[1])*f)); break
    return out

LOGP = [(2010.39, .0041), (2010.9, .3), (2011.45, 30), (2011.9, 2.5), (2012.6, 12), (2013.3, 230), (2013.5, 70), (2013.92, 1150), (2015.05, 200),
        (2016.5, 650), (2017.96, 19000), (2018.96, 3200), (2019.5, 12000), (2020.2, 5000), (2021.3, 60000), (2021.55, 31000), (2021.86, 67000),
        (2022.88, 15800), (2024.2, 70000), (2024.95, 98000), (2025.77, 124000), (2026.5, 58566), (2026.79, 82709)]

# ---------- scènes ----------
def sA(cv, c, t, a):
    fl = math.sin(t*.9)
    p = gpanel(560, 230, lambda k, w, h: (text(k, "MAI 2010 · 10 000 BTC", w/2, 58, 'sb', 26, 'FFE2A8', 'c', 1, 3),
                                           pizza_icon(k, 95, 150, .62), pizza_icon(k, w-95, 150, .62), text(k, "2 PIZZAS", w/2, 152, 'a', 86, CREAM, 'c', 1, 2)))
    place(cv, p, tilt_quad(540, 540+8*fl, 560, 230, ry=-.28+.06*fl, rx=-.12), a, 20, .5)
    glow_text(cv, "742 M€", 540, 840, 250, a=a)
    def d(c):
        text(c, "payées 41 $ à l'époque", 540, 1050, 'xb', 40, CREAM)
        pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1160)
        if t >= 5.45:   # « 10 000 bitcoins » : petit flash sur le panneau
            e = clamp(1-(t-5.45)/.6); burst(c, 540, 470, 40, 200, 14, GOLD, .7*e, 2, 1+.4*(1-e))
    grp(c, a, d)

def sB(cv, c, t, a):
    u = ease((t-7.6)/1.3)
    X0, X1, Y0, Y1 = 60, 800, 600, 90
    def px(y, p): return X0+(y-2010.39)/(2026.79-2010.39)*(X1-X0), Y0+(Y1-Y0)*(math.log10(p)+3)/(math.log10(150000)+3)
    def chart(k, w, h):
        text(k, "PRIX D'UN BITCOIN · ÉCHELLE LOG", 40, 46, 'sb', 24, 'FFE2A8', 'l', 1, 2)
        for p_, lab in ((.01, "0,01 $"), (1, "1 $"), (100, "100 $"), (10000, "10 000 $")):
            y = px(2010.39, p_)[1]; k.set_line_width(1); col(k, WHITE, .12); k.move_to(X0, y); k.line_to(w-40, y); k.stroke(); text(k, lab, X0+4, y-14, 'm', 20, SUB, 'l')
        pts = partial(LOGP, u)
        if len(pts) > 1:
            k.move_to(*px(*pts[0]))
            for q in pts[1:]: k.line_to(*px(*q))
            k.line_to(px(*pts[-1])[0], Y0); k.line_to(X0, Y0); k.close_path()
            g = cairo.LinearGradient(0, Y1, 0, Y0); g.add_color_stop_rgba(0, *hx(ORANGE, .45)); g.add_color_stop_rgba(1, *hx(ORANGE, 0)); k.set_source(g); k.fill()
            for a_, lw in ((.08, 34), (.18, 18), (1, 7)):
                k.move_to(*px(*pts[0]))
                for q in pts[1:]: k.line_to(*px(*q))
                k.set_line_width(lw); k.set_line_join(1); k.set_line_cap(1); col(k, GOLD, a_); k.stroke()
            x, y = px(*pts[-1]); k.arc(x, y, 12, 0, 2*math.pi); col(k, WHITE); k.fill()
        x, y = px(*LOGP[0]); k.arc(x, y, 11, 0, 2*math.pi); col(k, CREAM); k.fill(); text(k, "2010 · 0,004 $", x+10, y+40, 'xb', 26, CREAM, 'l')
        if t >= 8.9:
            e = clamp((t-8.9)/.7); x, y = px(*LOGP[-1]); burst(k, x, y, 16, 110, 16, GOLD, 1-e*.6, 5, .5+.8*ease(e*2))
            text(k, "82 700 $", x-30, y+70, 'xb', 32, CREAM, 'r', ease((t-8.9)/.25))
        for yy in (2010, 2014, 2018, 2022, 2026): text(k, str(yy), px(yy+.39 if yy == 2010 else yy, 1)[0], h-26, 'm', 22, SUB)
    e = ease((t-7.3)/.45)
    place(cv, gpanel(860, 680, chart), tilt_quad(540, 900+80*(1-e), 860, 680, ry=.24+.5*(1-e), rx=.1), a*e, 26, .55)
    if t >= 8.9:
        v = 20e6*ease((t-8.9)/.6); s = "×"+f"{int(v):,}".replace(',', ' ')
        glow_text(cv, s, 540, 360, 150, a=a, scale=lerp(1.25, 1, back((t-8.9)/.4)))
    grp(c, a, lambda c: text(c, "UN BITCOIN, DEPUIS LA PIZZA", 540, 230, 'sb', 32, 'FFE2A8', 'c', 1, 6))

PX, PY, PW, PH = 110, 640, 860, 560; BASE = 440; SC = 260/127546
BARS = [("5 ans", 1503, GOLD, 12.11), ("10 ans", 127546, GOLD, 14.36), ("13 ans", 716608, ORANGE, 17.31)]
def bx(i): return 110+i*230
def sC(cv, c, t, a):
    def chart(k, w, h):
        text(k, "1 000 € PLACÉS IL Y A…", 40, 46, 'sb', 24, 'FFE2A8', 'l', 1, 2)
        k.set_line_width(2); col(k, WHITE, .3); k.move_to(40, BASE); k.line_to(w-40, BASE); k.stroke()
        for i, (lab, v, cl, t0) in enumerate(BARS):
            x = bx(i); text(k, lab, x+75, BASE+45, 'xb', 30, WHITE, 'c', .5+.5*(t >= t0))
            if t < t0 or i == 2: continue
            g = back((t-t0)/.55, 1.2); hh = max(6, v*SC*g)
            rr(k, x, BASE-hh, 150, hh, 10); col(k, cl); k.fill()
            lab2 = f"{int(v*clamp((t-t0)/.5)):,} €".replace(',', ' '); text(k, lab2, x+75, BASE-hh-28, 'xb', 32, CREAM)
        text(k, "valeur au 14 oct. 2026 · change €/$ inclus", w/2, h-36, 'm', 21, SUB, 'c', .85)
    e = ease((t-10.0)/.45)
    place(cv, gpanel(PW, PH, chart), [(PX, PY+60*(1-e)), (PX+PW, PY+60*(1-e)), (PX+PW, PY+PH+60*(1-e)), (PX, PY+PH+60*(1-e))], a*e, 26, .55)
    glow_text(cv, "1 000 €", 540, 420, 130, top='FFFFFF', bottom='FFE2A8', glow='F5B544', ga=.5, a=a*e*clamp((17.2-t)/.3))
    t0 = BARS[2][3]
    if t >= t0:
        def d(c):
            x = PX+bx(2); bot = PY+BASE; g = ease((t-t0)/.35); top = lerp(bot, -40, g)
            for a_, ex in ((.10, 40), (.2, 20), (.35, 8)):
                rr(c, x-ex, top, 150+2*ex, bot-top+ex, 16); col(c, ORANGE, a_); c.fill()
            gr = cairo.LinearGradient(0, top, 0, bot); gr.add_color_stop_rgb(0, *hx('FFE7B0')[:3]); gr.add_color_stop_rgb(.3, *hx(ORANGE)[:3]); gr.add_color_stop_rgb(1, *hx('C2600A')[:3])
            rr(c, x, top, 150, bot-top, 10); c.set_source(gr); c.fill()
            if top < PY:
                e2 = clamp((t-t0-.18)/.9); burst(c, x+75, PY+4, 30, 240, 22, GOLD, 1-.7*e2, 7, .4+.9*ease(e2*1.5))
                rnd = random.Random(4)
                for k in range(16):   # éclats de verre projetés
                    vx, vy = rnd.uniform(-420, 420), rnd.uniform(-700, -200); s_ = rnd.uniform(10, 26); r_ = rnd.uniform(0, 6.28); tt = t-t0-.18
                    sx, sy = x+75+vx*tt, PY+vy*tt+900*tt*tt
                    c.save(); c.translate(sx, sy); c.rotate(r_+tt*rnd.uniform(-8, 8)); c.move_to(0, -s_); c.line_to(s_*.6, s_*.4); c.line_to(-s_*.5, s_*.6); c.close_path()
                    col(c, 'FFF3D6', .35*(1-e2)); c.fill_preserve(); col(c, WHITE, .7*(1-e2)); c.set_line_width(1.5); c.stroke(); c.restore()
        grp(c, a, d)
        glow_text(cv, "716 600 €", 400, 330, 104, a=a*ease((t-t0-.2)/.25), scale=lerp(1.3, 1, back((t-t0-.2)/.4)))
        grp(c, a*ease((t-t0-.5)/.3), lambda c: text(c, "×717", 400, 450, 'xb', 44, GREEN))

def sD(cv, c, t, a):
    X0, X1, Y0, Y1 = 50, 810, 510, 150
    def px(y, v): return X0+(y-2016.79)/10*(X1-X0), Y0+(Y1-Y0)*v/190000
    u = ease((t-19.4)/1.6)
    def chart(k, w, h):
        text(k, "TES 1 000 € DE 2016, EN EUROS", 40, 50, 'sb', 24, 'FFE2A8', 'l', 1, 2)
        pts = partial(PATH10, u)
        k.move_to(*px(*pts[0]))
        for q in pts[1:]: k.line_to(*px(*q))
        k.line_to(px(*pts[-1])[0], Y0); k.line_to(X0, Y0); k.close_path()
        g = cairo.LinearGradient(0, Y1, 0, Y0); g.add_color_stop_rgba(0, *hx(ORANGE, .38)); g.add_color_stop_rgba(1, *hx(ORANGE, 0)); k.set_source(g); k.fill()
        for a_, lw in ((.1, 26), (.2, 14), (1, 6)):
            k.move_to(*px(*pts[0]))
            for q in pts[1:]: k.line_to(*px(*q))
            k.set_line_width(lw); k.set_line_join(1); col(k, GOLD, a_); k.stroke()
        for yr, v, lab, t0 in ((2018.96, PATH10[4][1], "−84 %", 21.9), (2022.88, PATH10[12][1], "−77 %", 22.93)):
            if t < t0: continue
            x, y = px(yr, v); s = back((t-t0)/.35); w_ = (tw(k, lab, 'a', 44)+30)*s
            k.save(); k.translate(x+30, y-60); k.scale(s, s); rr(k, -w_/2/s, -32, w_/s, 64, 12); col(k, RED); k.fill(); text(k, lab, 0, 0, 'a', 44, WHITE); k.restore()
            k.set_line_width(3); col(k, RED, .8); k.arc(x, y, 14, 0, 2*math.pi); k.stroke()
        for yy in (2017, 2019, 2021, 2023, 2025): text(k, str(yy), px(yy, 0)[0], h-28, 'm', 22, SUB)
    e = ease((t-19.2)/.45)
    place(cv, gpanel(860, 600, chart), tilt_quad(540, 820+60*(1-e), 860, 600, ry=-.2-.5*(1-e), rx=.08), a*e, 26, .55)
    grp(c, a*e, lambda c: text(c, "IL FALLAIT TENIR…", 540, 400, 'a', 96, CREAM, 'c', 1, 2))

def sE(cv, c, t, a):
    t0 = 25.47
    def card(k, w, h):
        text(k, "RECORD · OCT. 2025", 40, 50, 'sb', 24, 'FFE2A8', 'l', 1, 2); text(k, "126 000 $", 40, 115, 'a', 64, CREAM, 'l')
        text(k, "AUJOURD'HUI", w-40, 50, 'sb', 24, 'FFE2A8', 'r', 1, 2); text(k, "82 700 $", w-40, 115, 'a', 64, RED, 'r')
        k.set_line_width(4); col(k, WHITE, .4); k.move_to(330, 110); k.line_to(w-330, 110); k.stroke(); k.move_to(w-345, 98); k.line_to(w-330, 110); k.line_to(w-345, 122); k.stroke()
    e = ease((t-23.67)/.45)
    place(cv, gpanel(860, 180, card), tilt_quad(540, 900+40*(1-e), 860, 180, ry=.18, rx=-.1), a*e, 22, .5)
    if t >= t0: glow_text(cv, "−34 %", 540, 520, 250, top='FFFFFF', bottom='FF6B6B', glow='E5484D', ga=.6, a=a, scale=lerp(1.35, 1, back((t-t0)/.4)))
    grp(c, a*ease((t-t0-.3)/.3), lambda c: text(c, "SOUS SON RECORD", 540, 720, 'sb', 32, 'FFE2A8', 'c', 1, 6))

CH = (("1", "J'achète", 31.88, 32.67), ("2", "Je vends", 32.67, 33.40), ("3", "J'attends", 33.40, 34.6))
def sF(cv, c, t, a):
    def choices(k, w, h):
        for i, (n, s, t0, t1) in enumerate(CH):
            on = t0 <= t < t1; y = 30+i*92
            rr(k, 30, y, w-60, 74, 37); col(k, ORANGE if on else WHITE, .95 if on else .1); k.fill()
            text(k, n, 80, y+37, 'a', 40, INK if on else WHITE); text(k, s, 130, y+37, 'xb', 34, INK if on else WHITE, 'l')
    e = ease((t-28.1)/.45); fl = math.sin(t*1.1)
    place(cv, gpanel(620, 330, choices, r=48), tilt_quad(540, 900+60*(1-e), 620, 330, ry=-.2+.05*fl, rx=.1), a*e, 22, .5)
    glow_text(cv, "OPPORTUNITÉ", 540, 470, 120, a=a*e)
    glow_text(cv, "OU PIÈGE ?", 540, 610, 120, top='FFFFFF', bottom='FF6B6B', glow='E5484D', ga=.6, a=a*ease((t-29.3)/.3))
    if t >= 30.6:
        al = ease((t-30.6)/.4)
        def lg(c):
            c.push_group(); logo_symbol(c, 410, 1135, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
            text(c, "Actions_Benefices", 445, 1135, 'b', 30, WHITE, 'l', al)
        grp(c, a, lg)

def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

SCENES = [(sA, 0.0, 7.45, 0.62, 3), (sB, 7.3, 10.1, .5, 8), (sC, 10.0, 19.2, .5, 8), (sD, 19.1, 23.75, .5, 8), (sE, 23.6, 28.25, .5, 8), (sF, 28.1, DUR+1, .5, 8)]
SHAKES = [(17.5, 22), (8.9, 8), (14.4, 6), (25.47, 10)]
def frame(t):
    dim = blur = None
    for fn, a0, b0, dm, bl in SCENES:
        if a0 <= t < b0: dim, blur = dm, bl
    if t < 7.6: dim, blur = lerp(.62, .5, clamp((t-7.0)/.6)), lerp(3, 8, clamp((t-7.0)/.6))
    cv = background(t, dim, blur); darkspot(cv, 540, 760, 700, 760, .6 if t < 7.3 else .7)
    darken_band(cv, 1240, 1470, .6)
    s, c = surface()
    for fn, a0, b0, *_ in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else win(t, a0, b0, .3, .25)
        if al > 0: fn(cv, c, t, al)
    scrub(c, 150, clamp(t/DUR))
    k = cap_at(t)
    if k is not None and t < DUR:
        st = CAPS[k][0]; a = 1.0 if st == 0 else ease((t-st)/.12)
        grp(c, a, lambda c: caption(c, parse(CAPS[k][1])), 14*(1-a))
    cv.alpha_composite(to_img(s))
    # secousse de caméra sur les explosions
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy:
        cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(10, 6, 2, 255))
    return finish(cv, t, 5.0)

def events():
    ev = [(0.0, 'impact'), (0.0, 'coins'), (3.27, 'swish'), (5.45, 'glint'), (7.3, 'swish'), (7.6, 'riser'), (8.9, 'impact'), (8.9, 'glint'),
          (10.0, 'swish'), (12.11, 'pop'), (14.36, 'impact'), (14.36, 'tick'), (16.0, 'riser'), (17.31, 'boom'), (17.49, 'shatter'), (17.6, 'glint'),
          (19.1, 'swish'), (21.9, 'crash'), (21.9, 'impact'), (22.93, 'impact'), (23.6, 'swish'), (25.47, 'impact'), (28.1, 'swish'), (29.3, 'pop'),
          (30.6, 'pop'), (31.88, 'click'), (32.67, 'click'), (33.40, 'click')]
    return ev

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/btc/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).save(f'/home/claude/btc/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
