"""SpaceX : 46 s. Compte à rebours radio (3, 2, 1, lift off) puis voix off (ElevenLabs, fournies par Nicolas).
La courbe boursière est la trajectoire de la fusée (design original). « 682 € » visible dès l'image 0."""
import sys, math, re, random, subprocess, os, functools
import numpy as np, cairo
from PIL import Image, ImageFilter
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/spcx')
from sty import *
import bglass
FPS = 60; VO = 3.45; DUR = VO+42.08+.6
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
def V(v): return VO+v   # temps de la voix -> temps vidéo
IGN, LIFT = 2.30, 2.75   # allumage sur « lift », décollage sur « off »
CD = [(0.0, "3"), (0.76, "2"), (1.46, "1")]

CAPS = [(0.0, "[Three]…"), (0.76, "Three… [two]…"), (1.46, "Three… two… [one]…"), (2.30, "[Lift off !]"),
        (V(0), "[Six cent quatre-vingts euros]."), (V(1.74), "C'est ce qu'il te resterait si tu avais"), (V(3.5), "mis 1 000 € dans SpaceX"),
        (V(4.3), "[au sommet], en juin."), (V(6.69), "Le 12 juin, c'est la plus grosse"), (V(8.6), "[introduction en Bourse] de l'histoire."),
        (V(10.53), "En quatre jours, l'action grimpe"), (V(12.2), "de [67 %],"), (V(13.81), "et Elon Musk, qui en détient"),
        (V(15.4), "environ [42 %],"), (V(16.79), "devient le [premier trillionnaire]"), (V(18.2), "de la planète."),
        (V(19.57), "Derrière lui, [Google] :"), (V(21.24), "900 millions misés en 2015…"), (V(23.63), "plus de [80 milliards] aujourd'hui."),
        (V(26.01), "Puis tout [s'effondre] :"), (V(27.44), "la moitié de sa valeur envolée"), (V(28.8), "en [6 semaines]."),
        (V(30.33), "Aujourd'hui, SpaceX vaut"), (V(31.4), "[2 000 milliards] de dollars…"), (V(33.72), "mais elle a perdu près de"),
        (V(34.7), "[9 milliards] sur un an."), (V(36.43), "Alors, génie ou [bulle] ?"), (V(38.6), "Dis-moi en commentaire :"),
        (V(39.82), "tu [achètes],"), (V(40.59), "tu [vends]"), (V(41.31), "ou tu [attends] ?")]
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $', ' !'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k

ALT = [(0, 0.05), (LIFT, .05), (V(6.5), .3), (V(13.8), .5), (V(19.5), .62), (V(26), .72), (V(30.3), .88), (DUR, .95)]
def alt_at(t): return float(np.interp(t, [a for a, _ in ALT], [b for _, b in ALT]))

# ---------- scènes ----------
import json
LPROJ = json.load(open('/home/claude/spcx/launch_proj.json'))
@functools.lru_cache(maxsize=6)
def lframe(n):
    p = f'/home/claude/spcx/seq_launch/f{n:04d}.png'
    if not os.path.exists(p): p = '/home/claude/spcx/l_test85.png'
    return Image.open(p).convert('RGBA').resize((W, H), Image.BICUBIC)
def launch_layer(t):
    f = min(156.0, t*15)+1; i = int(f); fr = f-i
    a = lframe(i); b = lframe(min(157, i+1))
    return Image.blend(a, b, fr) if fr > .05 else a
def sLaunch(cv, c, t, a):
    """compte à rebours + décollage 3D (fumée en volutes) + promesse"""
    power = 0 if t < IGN else min(1, (t-IGN)/.35)
    L = launch_layer(t)
    f = min(157, int(t*15)+1); nx, ny = LPROJ[str(f)]; nx *= W; ny *= H
    jx = 2*math.sin(t*61)*power*(1+1.5*clamp(1-(t-IGN)/1.5)); jy = 1.5*math.cos(t*47)*power
    if power > .02:   # flamme 2D sous la tuyère, puis la scène 3D (fumée devant le bas de la flamme)
        fl = flame(t, power, int(1100*power**.5), 230); cv.alpha_composite(fl, (int(nx-fl.width/2+jx), int(ny-8+jy)))
    cv.alpha_composite(L if not (jx or jy) else L.transform((W, H), Image.AFFINE, (1, 0, -jx, 0, 1, -jy), Image.BILINEAR))
    if power > .02:
        fl = flame(t, power, int(420*power**.5), 200); cv.alpha_composite(fl, (int(nx-fl.width/2+jx), int(ny-8+jy)))
        s, k = surface(); g = cairo.RadialGradient(nx, ny+80, 0, nx, ny+80, 520); g.add_color_stop_rgba(0, *hx(FIRE, .40*power)); g.add_color_stop_rgba(1, *hx(FIRE, 0))
        k.set_source(g); k.paint(); cv.alpha_composite(to_img(s))
    darkspot(cv, 540, 330, 600, 260, .35)
    chip = spanel(560, 96, lambda k, w, h: text(k, "1 000 € AU SOMMET DE JUIN", w/2, h/2, 'xb', 30, ICE, 'c', 1, 3), r=48)
    place(cv, chip, tilt_quad(540, 170, 560, 96, ry=-.2+.04*math.sin(t), rx=-.1), a, 14, .3)
    pop = 1.0 if t < V(0) else lerp(1.25, 1, back((t-V(0))/.4))
    gtw(cv, "682 €", 540, 360, 230, a=a, scale=pop)
    def d(c):
        if t < LIFT+.4:
            for t0, s_ in CD:
                if t0 <= t < t0+.72:
                    e = .6+.4*ease((t-t0)/.25); al = clamp((t0+.72-t)/.2)
                    c.save(); c.translate(540, 640); sc_ = lerp(1.6, 1, e); c.scale(sc_, sc_); text(c, s_, 0, 0, 'a', 220, WHITE, 'c', al*e); c.restore()
            if t >= IGN:
                e = ease((t-IGN)/.3); text(c, "LIFT OFF", 540, 640, 'a', 150, HOT, 'c', e*clamp((LIFT+.4-t)/.3+1))
        if t >= V(.8):
            pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 545, FIRE, INKB, ease((t-V(.8))/.3))
    grp(c, a, d)

def catmull(pts, n=24):
    """courbe de Catmull-Rom passant par les points (lissage des angles)"""
    P = [pts[0]]+list(pts)+[pts[-1]]; out = []
    for k in range(1, len(P)-2):
        p0, p1, p2, p3 = P[k-1], P[k], P[k+1], P[k+2]
        for i in range(n):
            u = i/n; u2, u3 = u*u, u*u*u
            out.append(tuple(.5*((2*p1[d])+(-p0[d]+p2[d])*u+(2*p0[d]-5*p1[d]+4*p2[d]-p3[d])*u2+(-p0[d]+3*p1[d]-3*p2[d]+p3[d])*u3) for d in (0, 1)))
    out.append(pts[-1]); return out
def py_(p): return 1190+(560-1190)*(p-130)/96
RISE = [(0, 135), (.18, 160), (.42, 180), (.7, 205), (1, 225.64)]
FALLP = [(0, 225.64), (.15, 200), (.3, 182), (.5, 150), (.7, 128), (1, 113.5)]
CTRL = [(u*550, py_(p)) for u, p in RISE]+[(550+u*700, py_(p)) for u, p in FALLP[1:]]+[(1420, py_(70)), (1700, py_(-20))]
WPTS = catmull(CTRL); WX = np.array([q[0] for q in WPTS]); WY = np.array([q[1] for q in WPTS])
def wpt(x): return float(x), float(np.interp(x, WX, WY))
def heading(x, win=70):
    """cap de la fusée : tangente moyennée sur une fenêtre (rotation douce aux changements de pente)"""
    xs = np.linspace(x-win, x+win, 9); ys = np.interp(xs, WX, WY)
    dx = np.gradient(xs); dy = np.gradient(ys); ang = np.degrees(np.arctan2(dx, -dy))
    w = np.exp(-((xs-x)/(win*.6))**2); return float((ang*w).sum()/w.sum())
# caméra : (t, zoom, ox, oy, échelle fusée)
CAM = [(V(6.5), 1.0, 150, 0, .42), (V(13.6), 1.0, 150, 0, .42), (V(14.5), .75, 487.5, -170, .24), (V(25.3), .75, 487.5, -170, .24),
       (V(26.35), 1.0, -380, -180, .44), (DUR, 1.0, -380, -180, .44)]
def cam(t):
    for a, b in zip(CAM, CAM[1:]):
        if a[0] <= t <= b[0]:
            u = inout((t-a[0])/(b[0]-a[0]+1e-9)); return [lerp(x, y, u) for x, y in zip(a[1:], b[1:])]
    return list(CAM[0][1:] if t < CAM[0][0] else CAM[-1][1:])
def scr(x, y, cz): z, ox, oy, _ = cz; return x*z+ox, y*z+oy
def progress(t):
    """abscisse de la fusée sur la courbe : montée, vol stationnaire avant le sommet, chute"""
    if t < V(10.6): return 0.0
    if t < V(13.2): return 480*inout((t-V(10.6))/2.6)
    if t < V(26.42): return 480+6*(1-math.cos((t-V(13.2))*.6))
    u = (t-V(26.42))/3.4; return 480+940*(u*u*(1.4-.4*u) if u < 1 else 1+(u-1)*.8)
def world_layer(cv, t):
    """graphique-trajectoire continu + fusée, de l'introduction jusqu'à la chute"""
    if not (V(6.5) <= t < V(30.6)): return
    a = win(t, V(6.5), V(30.6), .35, .3)
    cz = cam(t); x = progress(t)
    dim = 1.0 if t < V(13.6) else (lerp(1, .3, inout((t-V(13.6))/.6)) if t < V(25.3) else lerp(.3, 1, inout((t-V(25.3))/.6)))
    s, k = surface()
    xr = 550 if t >= V(13.0) else min(x, 550)   # la courbe de montée va jusqu'au sommet
    rise = [scr(*q, cz) for q in WPTS if q[0] <= xr]+[scr(*wpt(xr), cz)]
    if len(rise) > 1: trail(k, rise, HOT, a*dim)
    if x > 550:
        fall = [scr(*q, cz) for q in WPTS if 550 <= q[0] <= min(x, 1250)]+[scr(*wpt(min(x, 1250)), cz)]
        if len(fall) > 1: trail(k, fall, RED_, a)
    x0, y0 = scr(*WPTS[0], cz); k.arc(x0, y0, 12*cz[0], 0, 2*math.pi); col(k, WHITE, a*dim); k.fill()
    text(k, "135 $ · 12 juin", x0+20, y0+46, 'xb', 30, ICE, 'l', a*dim)
    if t >= V(13.0):
        xp, yp = scr(*wpt(550), cz); text(k, "225 $ · 16 juin", xp+(30 if t < V(25.3) else -20), yp+(40 if t < V(25.3) else -40), 'xb', 30, ICE, 'l' if t < V(25.3) else 'r', a*(dim-.3)/.7*ease((t-V(13.0))/.3))
    if x >= 1250:
        xe, ye = scr(*wpt(1250), cz); text(k, "113 $ · fin juillet", xe-40, ye+50, 'xb', 30, ICE, 'r', a*ease((t-V(29.4))/.3))
    if t >= V(26.42):   # bouffées de fumée laissées par le moteur coupé
        for j in range(14):
            xs = x-30-j*42
            if xs < 550: break
            px_, py_2 = scr(*wpt(xs), cz); r = (10+j*4)*cz[0]; col(k, 'B8BCC8', .16*(1-j/14)); k.arc(px_, py_2, r, 0, 2*math.pi); k.fill()
    cv.alpha_composite(to_img(s))
    rx, ry = scr(*wpt(x), cz); ang = heading(x)
    pw = 1.0 if t < V(26.42) else clamp(1-(t-V(26.42))/.3)
    put_rocket(cv, t, rx, ry, cz[3], angle=ang, power=pw, shake=pw, a=a)

def sIPO(cv, c, t, a):
    if t < V(10.5):
        grp(c, a*ease((t-V(6.69))/.3), lambda c: text(c, "12 JUIN 2026", 540, 300, 'sb', 32, HOT, 'c', 1, 8))
        if t >= V(8.6): gtw(cv, "RECORD", 540, 420, 150, a=a, scale=lerp(1.3, 1, back((t-V(8.6))/.4)))
        grp(c, a*ease((t-V(8.6)-.3)/.3), lambda c: text(c, "plus grosse introduction en Bourse de l'histoire", 540, 530, 'xb', 30, ICE))
    else:
        if t >= V(12.4): gtw(cv, "+67 %", 360, 330, 170, a=a, scale=lerp(1.3, 1, back((t-V(12.4))/.4)))
        grp(c, a*ease((t-V(11.4))/.3), lambda c: text(c, "EN 4 JOURS", 360, 470, 'sb', 32, HOT, 'c', 1, 8))

def sMusk(cv, c, t, a):
    darkspot(cv, 540, 760, 680, 520, .5)
    if t >= V(15.6):
        e = ease((t-V(15.6))/.4)
        def card(k, w, h):
            text(k, "ELON MUSK DÉTIENT", 40, 46, 'sb', 24, ICE, 'l', 1, 3); text(k, "≈ 42 %", 40, 112, 'k', 64, WHITE, 'l'); text(k, "de SpaceX", 260, 118, 'xb', 30, SUBC, 'l')
        place(cv, spanel(560, 170, card), tilt_quad(540, 420+40*(1-e), 560, 170, ry=-.2, rx=-.08), a*e, 16, .4)
    if t >= V(17.6):
        e2 = clamp((t-V(17.6))/.9)
        def bst(c):
            rnd = random.Random(5)
            for k in range(24):
                ang = 2*math.pi*k/24; ra = 120; rb = (260+rnd.uniform(0, 120))*(.4+.9*ease(e2*1.4))
                g = cairo.LinearGradient(540+ra*math.cos(ang), 760+ra*math.sin(ang), 540+rb*math.cos(ang), 760+rb*math.sin(ang))
                g.add_color_stop_rgba(0, *hx(HOT, .8*(1-.6*e2))); g.add_color_stop_rgba(1, *hx(HOT, 0)); c.set_source(g); c.set_line_width(5); c.set_line_cap(1)
                c.move_to(540+ra*math.cos(ang), 760+ra*math.sin(ang)); c.line_to(540+rb*math.cos(ang), 760+rb*math.sin(ang)); c.stroke()
        grp(c, a, bst)
        gtw(cv, "1er", 540, 690, 110, a=a, scale=lerp(1.3, 1, back((t-V(17.6))/.4)))
        gtw(cv, "TRILLIONNAIRE", 540, 830, 130, a=a, scale=lerp(1.3, 1, back((t-V(17.75))/.4)))
        grp(c, a*ease((t-V(18.2))/.3), lambda c: text(c, "plus de 1 000 milliards de dollars de fortune", 540, 950, 'xb', 30, ICE))

HOLD = [("Elon Musk", 848, "≈ 42 %"), ("Google", 81.9, "900 M$ en 2015"), ("Fidelity", 45.0, ""), ("Gigafund", 25.5, ""), ("Fonds saoudien", 22.9, ""), ("Nvidia", 18.3, "")]
PX, PY, PW, PH = 90, 560, 900, 640; HSC = 640/90*.55
def sHold(cv, c, t, a):
    darkspot(cv, 540, 820, 700, 560, .55)
    def chart(k, w, h):
        text(k, "QUI POSSÈDE SPACEX ? · VALEUR AU 15 OCT.", 40, 46, 'sb', 22, ICE, 'l', 1, 2)
        for i, (n, v, sub) in enumerate(HOLD):
            y = 100+i*88; t0 = V(20.3)+i*.18 if i else V(19.6)
            al = ease((t-t0)/.3); text(k, n, 40, y+26, 'xb', 32, WHITE, 'l', al)
            if sub: text(k, sub, 40, y+60, 'm', 21, SUBC, 'l', al)
            if i == 0 or t < t0: continue
            g = back((t-t0)/.45, 1.2); bw = v*HSC*g; x0 = 330
            rr(k, x0, y+6, max(6, bw), 44, 10); col(k, HOT if i == 1 else 'C9D6EA', .95); k.fill()
            text(k, f"{v:.0f} Md$", x0+bw+14, y+28, 'xb', 28, HOT if i == 1 else ICE, 'l', al)
    e = ease((t-V(19.1))/.45)
    place(cv, spanel(PW, PH, chart), [(PX, PY+60*(1-e)), (PX+PW, PY+60*(1-e)), (PX+PW, PY+PH+60*(1-e)), (PX, PY+PH+60*(1-e))], a*e, 24, .5)
    t0 = V(19.75)
    if t >= t0:
        def d(c):
            x0 = PX+330; y = PY+100; x1 = lerp(x0, W+40, ease((t-t0)/.35))
            for a_, ee in ((.10, 26), (.2, 14), (.35, 6)): rr(c, x0-ee, y+6-ee, x1-x0+2*ee, 44+2*ee, 14); col(c, FIRE, a_); c.fill()
            g = cairo.LinearGradient(x0, 0, W, 0); g.add_color_stop_rgb(0, *hx('FF6A1A')[:3]); g.add_color_stop_rgb(1, *hx(HOT)[:3]); rr(c, x0, y+6, x1-x0, 44, 10); c.set_source(g); c.fill()
            text(c, "≈ 850 Md$", x0+20, y+28, 'k', 36, INKB, 'l', ease((t-t0-.25)/.2))
        grp(c, a, d)
    if t >= V(24.0):
        gtw(cv, "×91", 540, 300, 170, top='FFFFFF', bottom='7CF5B0', glow=GRN, a=a, scale=lerp(1.3, 1, back((t-V(24.0))/.4)))
        grp(c, a*ease((t-V(24.3))/.3), lambda c: text(c, "POUR GOOGLE DEPUIS 2015", 540, 430, 'sb', 30, ICE, 'c', 1, 6))

def sFall(cv, c, t, a):
    if t >= V(27.5): gtw(cv, "−50 %", 540, 300, 190, bottom='FF8A95', glow=RED_, a=a, scale=lerp(1.3, 1, back((t-V(27.5))/.4)))
    grp(c, a*ease((t-V(28.8))/.3), lambda c: text(c, "EN 6 SEMAINES", 540, 450, 'sb', 32, 'FF8A95', 'c', 1, 8))

def sVal(cv, c, t, a):
    darkspot(cv, 540, 760, 700, 640, .5)
    def card(title, val, sub, colv):
        def d(k, w, h):
            text(k, title, w/2, 50, 'sb', 24, ICE, 'c', 1, 3); text(k, val, w/2, 150, 'k', 84, colv, 'c'); text(k, sub, w/2, 232, 'm', 24, SUBC, 'c')
        return d
    if t >= V(30.3):
        e = ease((t-V(30.3))/.45)
        place(cv, spanel(820, 280, card("VALEUR EN BOURSE", "2 000 Md$", "≈ 88 fois son chiffre d'affaires annuel", HOT)), tilt_quad(540, 520+40*(1-e), 820, 280, ry=-.18, rx=-.08), a*e, 20, .45)
    if t >= V(33.72):
        e = ease((t-V(33.72))/.45)
        place(cv, spanel(820, 280, card("RÉSULTAT SUR 12 MOIS", "−8,9 Md$", "23 Md$ de chiffre d'affaires", RED_)), tilt_quad(540, 900+40*(1-e), 820, 280, ry=.18, rx=.08), a*e, 20, .45)
    if t >= V(31.9): grp(c, a*clamp(1-(t-V(31.9))/.8), lambda c: (c.arc(540, 520, 200+400*ease((t-V(31.9))/.8), 0, 2*math.pi), c.set_line_width(4), col(c, HOT, .5), c.stroke()))
    if t >= V(34.8): grp(c, a*clamp(1-(t-V(34.8))/.8), lambda c: (c.arc(540, 900, 200+400*ease((t-V(34.8))/.8), 0, 2*math.pi), c.set_line_width(4), col(c, RED_, .5), c.stroke()))

CH = (("1", "J'achète", V(39.82), V(40.59)), ("2", "Je vends", V(40.59), V(41.31)), ("3", "J'attends", V(41.31), DUR+1))
def sEnd(cv, c, t, a):
    put_rocket(cv, t, 540, 1350, .3, power=.8)   # nouveau départ, en bas
    if t >= V(36.98): gtw(cv, "GÉNIE", 540, 330, 140, a=a, scale=lerp(1.3, 1, back((t-V(36.98))/.4)))
    if t >= V(37.67): gtw(cv, "OU BULLE ?", 540, 480, 120, bottom='FF8A95', glow=RED_, a=a, scale=lerp(1.3, 1, back((t-V(37.67))/.4)))
    def choices(k, w, h):
        for i, (n, s, t0, t1) in enumerate(CH):
            on = t0 <= t < t1; y = 30+i*92
            rr(k, 30, y, w-60, 74, 37); col(k, FIRE if on else WHITE, .95 if on else .1); k.fill()
            text(k, n, 80, y+37, 'a', 40, INKB if on else WHITE); text(k, s, 130, y+37, 'xb', 34, INKB if on else WHITE, 'l')
    e = ease((t-V(38.4))/.45)
    place(cv, spanel(620, 330, choices, r=48), tilt_quad(540, 760+50*(1-e), 620, 330, ry=-.2+.05*math.sin(t*1.1), rx=.1), a*e, 22, .5)
    if t >= V(38.8):
        al = a*ease((t-V(38.8))/.4)
        def lg(c):
            c.push_group(); logo_symbol(c, 410, 990, 50); c.pop_group_to_source(); c.paint_with_alpha(al)
            text(c, "Actions_Benefices", 445, 990, 'b', 30, WHITE, 'l', al)
        grp(c, 1, lg)

SCENES = [(sLaunch, 0.0, V(6.75)), (sIPO, V(6.5), V(13.95)), (sMusk, V(13.7), V(19.3)), (sHold, V(19.05), V(25.6)),
          (sFall, V(25.4), V(30.5)), (sVal, V(30.2), V(36.6)), (sEnd, V(36.3), DUR+1)]
SHAKES = [(IGN, 14), (LIFT, 10), (V(0), 12), (V(12.4), 8), (V(17.6), 12), (V(19.75), 8), (V(24.0), 8), (V(26.42), 14), (V(27.5), 10), (V(31.9), 6), (V(34.8), 8), (V(36.98), 6)]
def frame(t):
    alt = alt_at(t)
    cv = sky(t, alt)
    cl = clouds(t, alt, .3 if t < LIFT else 1+3*clamp((t-LIFT)/2))
    if cl: cv.alpha_composite(cl)
    world_layer(cv, t)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else win(t, a0, b0, .3, .25)
        if al > 0: fn(cv, c, t, al)
    darken_band(cv, 1240, 1470, .55)
    sbar(c, clamp(t/DUR))
    k = cap_at(t)
    if k is not None:
        st = CAPS[k][0]; a = 1.0 if st == 0 else ease((t-st)/.12)
        grp(c, a, lambda c: capw(c, parse(CAPS[k][1])), 14*(1-a))
    cv.alpha_composite(to_img(s))
    if len(bglass._GT) > 60: bglass._GT.clear()
    if IGN <= t < IGN+.4:   # flash d'allumage
        cv.alpha_composite(Image.new('RGBA', (W, H), (255, 200, 140, int(90*(1-ease((t-IGN)/.4))))))
    dx = dy = 0
    for t0, amp in SHAKES:
        if 0 <= t-t0 < .5:
            d = amp*math.exp(-(t-t0)*9); dx += d*math.sin((t-t0)*90); dy += d*math.cos((t-t0)*77)
    if LIFT <= t < LIFT+2.5: d = 3*(1-(t-LIFT)/2.5); dx += d*math.sin(t*70); dy += d*math.cos(t*53)
    if dx or dy: cv = cv.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR, fillcolor=(4, 6, 12, 255))
    return finish(cv, t, 4.0)

def events():
    ev = [(0.0, 'cdbeep'), (0.76, 'cdbeep'), (1.46, 'cdbeep'), (IGN, 'ignite'), (LIFT, 'boom'), (V(0), 'impact'), (V(0), 'glint'), (V(6.5), 'swish'),
          (V(8.6), 'impact'), (V(10.6), 'riser'), (V(12.4), 'impact'), (V(12.4), 'glint'), (V(13.7), 'swish'), (V(15.6), 'pop'),
          (V(17.6), 'boom'), (V(17.6), 'coins'), (V(19.05), 'swish'), (V(19.75), 'impact')]+[(V(20.3)+i*.18, 'pop') for i in range(5)]+[
          (V(24.0), 'impact'), (V(24.0), 'glint'), (V(25.4), 'swish'), (V(26.42), 'cutoff'), (V(26.6), 'crash'), (V(27.5), 'impact'),
          (V(30.2), 'swish'), (V(31.9), 'impact'), (V(33.72), 'swish'), (V(34.8), 'impact'), (V(36.3), 'swish'), (V(36.98), 'impact'), (V(37.67), 'pop'),
          (V(38.4), 'swish'), (V(38.8), 'pop'), (V(39.82), 'click'), (V(40.59), 'click'), (V(41.31), 'click')]
    return ev

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/spcx/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).save(f'/home/claude/spcx/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
