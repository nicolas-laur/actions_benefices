"""Micron : 37 s, voix off (ElevenLabs, fournie par Nicolas). Data center néon (Blender) + mémoire HBM 3D en héros + verre 3D.
Ouverture en impact : « 14 000 € » lisible dès l'image 0, zoom + flash + secousse."""
import sys, math, re, random, subprocess, os, functools, json
import numpy as np, cairo
from PIL import Image, ImageFilter
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/mu')
from kf import *
import bglass
FPS = 60; DUR = 37.0; NB = ' '
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

CAPS = [(0.0, "[Quatorze mille euros]."), (1.27, "C'est ce que seraient devenus tes [1 000 €]"), (3.36, "placés il y a 5 ans…"),
        (4.4, "dans une entreprise dont tu n'as"), (5.9, "sûrement [jamais entendu parler]."), (7.64, "Elle s'appelle [Micron],"),
        (8.9, "et elle fabrique la [mémoire]"), (10.4, "des serveurs de l'intelligence artificielle."), (12.86, "En un an, son bénéfice"),
        (14.5, "a été multiplié [par 10]."), (16.35, "Elle vaut aujourd'hui plus de"), (17.7, "[1 000 milliards] de dollars."),
        (19.8, "Mais attention :"), (20.85, "la mémoire, c'est un secteur [à cycles]."), (23.16, "En 2022, l'action avait perdu"),
        (25.62, "plus de [40 %]."), (26.86, "Et depuis juin, elle a déjà"), (28.3, "rechuté de [27 %]."), (30.35, "Alors, pépite ou [sommet] ?"),
        (32.54, "Dis-moi en commentaire :"), (33.81, "tu [achètes],"), (34.28, "tu [vends]"), (35.24, "ou tu [attends] ?")]
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

# ---------- couches 3D ----------
def _seq(d, n):
    p = f'{d}/f{n:04d}.png'
    return p if os.path.exists(p) else None
@functools.lru_cache(maxsize=8)
def dc_img(n):
    p = _seq('/home/claude/mu/seq_dc', n) or '/home/claude/mu/kf_dc.png'
    return Image.open(p).convert('RGB').resize((W, H), Image.BILINEAR)
def background(t, dim, blur):
    f = (t*30) % 90; i = int(f/2); fr = f/2-i
    a = dc_img(2*i+1); b = dc_img((2*i+2) % 90+1) if True else a
    im = Image.blend(a, b, fr) if fr > .05 else a
    if blur > .5: im = bglass.lowblur(im, blur, 2)
    return ImageEnhance.Brightness(im).enhance(dim).convert('RGBA')
@functools.lru_cache(maxsize=6)
def hbm_img(n):
    p = _seq('/home/claude/mu/seq_hbm', n) or '/home/claude/mu/hbm_kf1.png'
    im = Image.open(p).convert('RGBA')
    return Image.merge('RGBA', (*ImageEnhance.Contrast(im.convert('RGB')).enhance(1.18).split(), im.split()[3]))
PROJ = json.load(open('/home/claude/mu/proj.json'))
def hframe(t): return ((t-1.5)*20) % 120
def product(t, size, blur=0, bright=1.0):
    g = hframe(t); i = int(g/2); fr = g/2-i
    a = hbm_img(2*i+1); b = hbm_img((2*i+2) % 120+1)
    im = Image.blend(a, b, fr) if fr > .05 else a
    im = im.resize((size, size), Image.BILINEAR)
    if blur: im = bglass.lowblur(im, blur, 2)
    if bright != 1: im = Image.merge('RGBA', (*ImageEnhance.Brightness(im.convert('RGB')).enhance(bright).split(), im.split()[3]))
    return im
def proj(t, key):
    g = int(hframe(t))+1; return PROJ[str(min(120, max(1, g)))][key]
def put_product(cv, im, cx, cy, a=1.0):
    w, h = im.size; x0, y0 = int(cx-w/2), int(cy-h/2)
    s, c = surface(); c.save(); c.translate(cx, cy+h*.18); c.scale(w*.55, h*.16)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, *hx('3FE7FF', .45*a)); g.add_color_stop_rgba(.5, *hx(VI, .18*a)); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore(); cv.alpha_composite(to_img(s))
    al = im.split()[3]; glow = Image.new('RGBA', im.size, (60, 200, 255, 0)); glow.putalpha(bglass.lowblur(al.convert('RGBA'), 28, 2).split()[0].point(lambda v: int(v*.45*a)))
    cv.alpha_composite(glow, (x0, y0)); cv.alpha_composite(bglass.with_alpha(im, a), (x0, y0))
def callout(c, x0, y0, x1, y1, label, sub, color=CY, side='l', u=1.0):
    e = ease(u); xm, ym = lerp(x0, x1, e), lerp(y0, y1, e)
    c.set_line_width(2.5); col(c, color, .9); c.move_to(x0, y0); c.line_to(xm, ym)
    if u >= 1: c.line_to(x1+(-60 if side == 'l' else 60), y1)
    c.stroke(); c.arc(x0, y0, 9, 0, 2*math.pi); col(c, color); c.fill(); c.arc(x0, y0, 14+10*(1-e), 0, 2*math.pi); c.set_line_width(2); col(c, color, .4); c.stroke()
    if u >= 1:
        xx = x1+(-70 if side == 'l' else 70); al = 'r' if side == 'l' else 'l'
        text(c, label, xx, y1-20, 'xb', 38, WHITE, al); text(c, sub, xx, y1+22, 'm', 26, ICE, al)

# placement de la puce par scène : (t, cx, cy, taille, flou, luminosité, opacité)
PK = [(0, 540, 560, 860, 0, 1, 1), (7.3, 540, 560, 860, 0, 1, 1), (7.9, 560, 840, 1000, 0, 1, 1), (12.4, 560, 840, 1000, 0, 1, 1),
      (13.0, 540, 520, 900, 10, .55, 1), (19.5, 540, 520, 900, 10, .55, 1), (20.2, 540, 520, 900, 16, .4, .7), (30.0, 540, 520, 900, 16, .4, .7),
      (30.6, 540, 1000, 760, 8, .6, .8), (DUR, 540, 1000, 760, 8, .6, .8)]
def pk(t):
    for a, b in zip(PK, PK[1:]):
        if a[0] <= t <= b[0]:
            u = inout((t-a[0])/(b[0]-a[0]+1e-9)); return [lerp(x, y, u) for x, y in zip(a[1:], b[1:])]
    return list(PK[-1][1:])

NI = [("2022", 8.69), ("2023", -5.83), ("2024", 0.78), ("2025", 8.54), ("2026", 84.97)]
# cours mensuel ajusté (approx.) oct. 2021 -> oct. 2026, converti en valeur des 1 000 € (17,142 actions)
MUP = [(2021.79, 67.5), (2022.1, 86.9), (2022.7, 49.1), (2023.1, 57.0), (2023.95, 84.7), (2024.45, 130.6), (2024.95, 83.8), (2025.3, 76.8),
       (2025.95, 285.3), (2026.2, 337.8), (2026.45, 1154.1), (2026.79, 914.1)]
def eur(p, y): fx = 1.16 if y < 2022.3 else (1.0 if y < 2023 else (1.09 if y < 2025.2 else 1.15)); return 17.142*p/fx
MUP_E = [(y, 1000 if i == 0 else (14000 if i == len(MUP)-1 else eur(p, y))) for i, (y, p) in enumerate(MUP)]
def partial(pts, u):
    x0, x1 = pts[0][0], pts[-1][0]; xe = x0+(x1-x0)*u; out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if b[0] <= xe: out.append(b)
        else: f = (xe-a[0])/(b[0]-a[0]); out.append((xe, a[1]+(b[1]-a[1])*f)); break
    return out

# ---------- scènes ----------
GLYPHS = "#%&@0123456789XQZKVW"
def sA(cv, c, t, a):
    chip = cpanel(520, 100, lambda k, w, h: text(k, "1 000 € · IL Y A 5 ANS", w/2, h/2, 'xb', 32, ICE, 'c', 1, 3), r=50)
    place(cv, chip, tilt_quad(540, 220, 520, 100, ry=-.2+.04*math.sin(t), rx=-.1), a, 16, .35)
    gt(cv, "14 000 €", 540, 1010, 220, a=a)
    def d(c):
        pa = clamp((4.3-t)/.25)
        if pa > 0: pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1215, CY, INKB, pa)
    grp(c, a, d)
    if t >= 4.4:
        e = ease((t-4.4)/.4)
        def card(k, w, h):
            text(k, "UNE ENTREPRISE QUE TU NE CONNAIS PAS", w/2, 44, 'sb', 24, ICE, 'c', 1, 3)
            rnd = random.Random(int(t*12))
            for i in range(6):
                x = 70+i*((w-140)/6); rr(k, x, 78, (w-140)/6-14, 46, 8); col(k, CY, .25+.35*rnd.random()); k.fill()
        place(cv, cpanel(620, 150, card), tilt_quad(540, 1205+40*(1-e), 620, 150, ry=.15, rx=.1), a*e, 18, .4)

def sB(cv, c, t, a):
    t0 = 8.25
    if t < t0+.6:   # décodage du nom
        def d(c):
            s = ''.join(("MICRON"[i] if t >= t0+.09*i else random.Random(int(t*30)+i).choice(GLYPHS)) for i in range(6))
            text(c, s, 540, 250, 'a', 150, CY, 'c', ease((t-7.6)/.3), 6)
        grp(c, a, d)
    else: gt(cv, "MICRON", 540, 250, 150, a=a)
    grp(c, a*ease((t-8.9)/.3), lambda c: text(c, "LA MÉMOIRE DE L'IA", 540, 370, 'sb', 32, ICE, 'c', 1, 8))
    cx, cy, S, *_ = pk(t); ox, oy = cx-S/2, cy-S/2
    if t >= 9.3:
        px_, py_ = proj(t, 'mid'); u = clamp((t-9.3)/.45)
        grp(c, a, lambda c: callout(c, ox+px_*S, oy+py_*S, ox+.50*S, oy+.17*S, "HBM", "12 puces mémoire empilées", CY, 'r', u))
    if t >= 10.6:
        gx, gy = proj(t, 'gpu'); u = clamp((t-10.6)/.45)
        grp(c, a, lambda c: callout(c, ox+gx*S, oy+gy*S, ox+.48*S, oy+.86*S, "Processeur IA", "la mémoire est collée au calcul", VI, 'l', u))

PX, PY, PW, PH = 110, 640, 860, 560; BASE = 360; SC = 2.2
def sC(cv, c, t, a):
    ab = a*clamp((16.3-t)/.3)
    if ab > 0:
        def chart(k, w, h):
            text(k, "BÉNÉFICE NET ANNUEL · MILLIARDS $", 40, 46, 'sb', 24, ICE, 'l', 1, 2)
            k.set_line_width(2); col(k, WHITE, .3); k.move_to(40, BASE); k.line_to(w-40, BASE); k.stroke()
            for i, (y, v) in enumerate(NI):
                x = 60+i*160; text(k, y, x+55, h-40, 'xb' if i == 4 else 'm', 24, ICE if i == 4 else SUBC)
                t0 = 13.6+i*.3
                if i == 4 or t < t0: continue
                g = back((t-t0)/.4, 1.2); hh = abs(v)*SC*6*g
                if v >= 0: rr(k, x, BASE-hh, 110, max(4, hh), 8); col(k, CY); k.fill(); text(k, f"{v:.1f}".replace('.', ','), x+55, BASE-hh-26, 'xb', 28, ICE)
                else: rr(k, x, BASE, 110, hh, 8); col(k, MG); k.fill(); text(k, f"−{abs(v):.1f}".replace('.', ','), x+55, BASE+hh+26, 'xb', 28, MG)
        e = ease((t-12.7)/.45)
        place(cv, cpanel(PW, PH, chart), [(PX, PY+60*(1-e)), (PX+PW, PY+60*(1-e)), (PX+PW, PY+PH+60*(1-e)), (PX, PY+PH+60*(1-e))], ab*e, 26, .55)
        t5 = 15.6
        if t >= t5:
            def d(c):
                x = PX+60+4*160; bot = PY+BASE; top = lerp(bot, -40, ease((t-t5)/.3))
                for a_, ex in ((.10, 40), (.2, 20), (.35, 8)): rr(c, x-ex, top, 110+2*ex, bot-top+ex, 16); col(c, CY, a_); c.fill()
                gr = cairo.LinearGradient(0, top, 0, bot); gr.add_color_stop_rgb(0, 1, 1, 1); gr.add_color_stop_rgb(.3, *hx(CY)[:3]); gr.add_color_stop_rgb(1, *hx('0077A8')[:3])
                rr(c, x, top, 110, bot-top, 8); c.set_source(gr); c.fill()
                if top < PY:
                    e2 = clamp((t-t5-.15)/.9); burst(c, x+55, PY+4, 30, 230*(.4+.9*ease(e2*1.5)), 22, CY, 1-.7*e2, 7)
                    rnd = random.Random(4); tt = t-t5-.15
                    for k in range(14):
                        vx, vy = rnd.uniform(-420, 420), rnd.uniform(-700, -200); s_ = rnd.uniform(10, 26)
                        sx, sy = x+55+vx*tt, PY+vy*tt+900*tt*tt
                        c.save(); c.translate(sx, sy); c.rotate(rnd.uniform(0, 6.28)+tt*rnd.uniform(-8, 8)); c.move_to(0, -s_); c.line_to(s_*.6, s_*.4); c.line_to(-s_*.5, s_*.6); c.close_path()
                        col(c, ICE, .35*(1-e2)); c.fill_preserve(); col(c, WHITE, .7*(1-e2)); c.set_line_width(1.5); c.stroke(); c.restore()
            grp(c, ab, d)
            gt(cv, "85 Md$", 380, 330, 140, a=ab*ease((t-t5-.1)/.2), scale=lerp(1.3, 1, back((t-t5-.1)/.4)))
            grp(c, ab*ease((t-t5-.4)/.3), lambda c: text(c, "×10 en un an", 380, 450, 'xb', 42, '3FD08A'))
    if t >= 16.35:
        a2 = a*ease((t-16.35)/.35)
        def ring(c):
            e = ease((t-17.75)/.6)
            for k_ in range(3):
                r = 200+k_*90+160*e; c.arc(540, 760, r, 0, 2*math.pi); c.set_line_width(3); col(c, CY if k_ != 1 else VI, .35*(1-e*.6)); c.stroke()
        grp(c, a2, ring)
        grp(c, a2, lambda c: text(c, "CAPITALISATION BOURSIÈRE", 540, 560, 'sb', 32, ICE, 'c', 1, 6))
        if t >= 17.75:
            gt(cv, "1 000", 540, 740, 230, a=a2, scale=lerp(1.3, 1, back((t-17.75)/.4)))
            gt(cv, "MILLIARDS $", 540, 910, 110, a=a2*ease((t-17.95)/.25))
            grp(c, a2*ease((t-18.3)/.3), lambda c: (pill(c, "≈ 1 030 Md$ au 14 octobre", 1080, VI, WHITE)))

def sD(cv, c, t, a):
    X0, X1, Y0, Y1 = 50, 810, 520, 150
    def px(y, v): return X0+(y-2021.79)/5*(X1-X0), Y0+(Y1-Y0)*v/17500
    u = ease((t-21.0)/2.0)
    def chart(k, w, h):
        text(k, "TES 1 000 € DANS MICRON · OCT. 2021 → OCT. 2026", 40, 50, 'sb', 22, ICE, 'l', 1, 2)
        pts = partial(MUP_E, u)
        k.move_to(*px(*pts[0]))
        for q in pts[1:]: k.line_to(*px(*q))
        k.line_to(px(*pts[-1])[0], Y0); k.line_to(X0, Y0); k.close_path()
        g = cairo.LinearGradient(0, Y1, 0, Y0); g.add_color_stop_rgba(0, *hx(CY, .38)); g.add_color_stop_rgba(1, *hx(CY, 0)); k.set_source(g); k.fill()
        for a_, lw in ((.1, 26), (.2, 14), (1, 6)):
            k.move_to(*px(*pts[0]))
            for q in pts[1:]: k.line_to(*px(*q))
            k.set_line_width(lw); k.set_line_join(1); col(k, CY, a_); k.stroke()
        x, y = px(*pts[-1]); k.arc(x, y, 10, 0, 2*math.pi); col(k, WHITE); k.fill()
        k.set_dash([8, 8]); k.set_line_width(2); col(k, WHITE, .3); yb = px(2021.79, 1000)[1]; k.move_to(X0, yb); k.line_to(X1, yb); k.stroke(); k.set_dash([])
        for yr, v, lab, t0, dx in ((2022.7, MUP_E[2][1], "−43 %", 25.85, 70), (2026.79, 14000, "−27 %", 28.75, -170)):
            if t < t0: continue
            x, y = px(yr, v); s = back((t-t0)/.35); w_ = tw(k, lab, 'a', 46)+30
            k.save(); k.translate(x+dx, y-70); k.scale(s, s); rr(k, -w_/2, -34, w_, 68, 12); col(k, MG); k.fill(); text(k, lab, 0, 0, 'a', 46, WHITE); k.restore()
            k.set_line_width(3); col(k, MG, .9); k.arc(x, y, 15, 0, 2*math.pi); k.stroke()
        for yy in (2022, 2023, 2024, 2025, 2026): text(k, str(yy), px(yy, 0)[0], h-28, 'm', 22, SUBC)
        text(k, "14 000 €", 40, 112, 'a', 52, ICE, 'l', ease((t-23.0)/.3))
    e = ease((t-20.85)/.45)
    place(cv, cpanel(860, 600, chart), tilt_quad(540, 830+60*(1-e), 860, 600, ry=-.2-.5*(1-e), rx=.08), a*e, 26, .55)
    grp(c, a*ease((t-19.8)/.3), lambda c: text(c, "MAIS ATTENTION", 540, 330, 'sb', 32, MG, 'c', 1, 8))
    if t >= 20.85: gt(cv, "SECTEUR À CYCLES", 540, 430, 104, a=a*ease((t-20.85)/.3), bottom='FF9AE0', glow=MG, ga=.6)

CH = (("1", "J'achète", 33.81, 34.5), ("2", "Je vends", 34.5, 35.24), ("3", "J'attends", 35.24, DUR+1))
def sE(cv, c, t, a):
    if t >= 31.0: gt(cv, "PÉPITE", 540, 330, 140, a=a, scale=lerp(1.25, 1, back((t-31.0)/.4)))
    if t >= 31.63: gt(cv, "OU SOMMET ?", 540, 480, 120, bottom='FF9AE0', glow=MG, a=a, scale=lerp(1.25, 1, back((t-31.63)/.4)))
    def choices(k, w, h):
        for i, (n, s, t0, t1) in enumerate(CH):
            on = t0 <= t < t1; y = 30+i*92
            rr(k, 30, y, w-60, 74, 37); col(k, CY if on else WHITE, .95 if on else .1); k.fill()
            text(k, n, 80, y+37, 'a', 40, INKB if on else WHITE); text(k, s, 130, y+37, 'xb', 34, INKB if on else WHITE, 'l')
    e = ease((t-32.3)/.45)
    place(cv, cpanel(620, 330, choices, r=48), tilt_quad(540, 760+50*(1-e), 620, 330, ry=-.2+.05*math.sin(t*1.1), rx=.1), a*e, 22, .5)
    if t >= 32.8:
        al = a*ease((t-32.8)/.4)
        def lg(c):
            c.push_group(); logo_symbol(c, 410, 1180, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
            text(c, "Actions_Benefices", 445, 1180, 'b', 30, WHITE, 'l', al)
        grp(c, 1, lg)

SCENES = [(sA, 0.0, 7.7), (sB, 7.55, 12.75), (sC, 12.6, 20.0), (sD, 19.75, 30.5), (sE, 30.3, DUR+1)]
SHAKES = [(0.0, 18), (15.75, 22), (17.75, 10), (25.85, 8), (28.75, 8), (31.0, 6)]
def frame(t):
    cx, cy, S, pb, pbr, pa = pk(t)
    dim = .5 if t < 7.5 else .45; blur = 7 if t < 7.5 else 9
    cv = background(t, dim, blur); darkspot(cv, 540, 760, 720, 760, .55)
    put_product(cv, product(t, int(S), pb, pbr), cx, cy, pa)
    if 12.9 < t < 30.2: darkspot(cv, 540, 820, 700, 640, .45)
    darken_band(cv, 1240, 1470, .6)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else win(t, a0, b0, .3, .25)
        if al > 0: fn(cv, c, t, al)
    bar(c, clamp(t/DUR))
    k = cap_at(t)
    if k is not None:
        st = CAPS[k][0]; a = 1.0 if st == 0 else ease((t-st)/.12)
        grp(c, a, lambda c: cap(c, parse(CAPS[k][1])), 14*(1-a))
    cv.alpha_composite(to_img(s))
    if len(bglass._GT) > 60: bglass._GT.clear()
    # ouverture en impact : zoom + flash
    if t < .45:
        z = lerp(1.12, 1.0, ease(t/.45)); w2, h2 = int(W*z), int(H*z)
        cv = cv.resize((w2, h2), Image.BILINEAR).crop(((w2-W)//2, (h2-H)//2, (w2-W)//2+W, (h2-H)//2+H))
        fl = Image.new('RGBA', (W, H), (200, 245, 255, int(70*(1-ease(t/.25))))); cv.alpha_composite(fl)
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(4, 8, 14, 255))
    return finish(cv, t, 4.0)

def events():
    return [(0.0, 'boom'), (0.0, 'glint'), (4.4, 'swish'), (7.55, 'swish'), (7.6, 'riser'), (8.25, 'key'), (8.34, 'key'), (8.43, 'key'), (8.52, 'key'), (8.61, 'key'), (8.7, 'key'),
            (8.75, 'impact'), (8.75, 'glint'), (9.3, 'tick'), (10.6, 'tick'), (12.6, 'swish')]+[(13.6+i*.3, 'pop') for i in range(4)]+[
            (14.7, 'riser'), (15.6, 'boom'), (15.75, 'shatter'), (16.35, 'swish'), (17.75, 'impact'), (17.75, 'glint'), (19.75, 'swish'), (20.85, 'low'),
            (21.0, 'tick'), (25.85, 'impact'), (28.75, 'impact'), (30.3, 'swish'), (31.0, 'impact'), (31.63, 'pop'), (32.3, 'swish'), (32.8, 'pop'),
            (33.81, 'click'), (34.5, 'click'), (35.24, 'click')]

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/mu/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).save(f'/home/claude/mu/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
