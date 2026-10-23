"""Nvidia : la machine à cash de l'IA, mais jusqu'où ? DA néon verte, 60 i/s, ~63 s."""
import sys, math, random, subprocess, re
sys.path.insert(0, '/home/claude/lvmh')
_argv = sys.argv; sys.argv = ['x', 'info']
from lvmh import layer, reveal, conceal, merge, seg, clamp, out_quint, out_expo, in_out, in_cubic, lerp
sys.argv = _argv
import numpy as np, cairo
from PIL import Image, ImageFilter
import da
from da import W, H, hx, col, tw, txt, background, circuits, BG, GRN, GRN_L, GRN_D, WHITE, GREY, RED, to_pil, to_cairo
FPS = 60

# ---------- chiffres (vérifiés le 9 octobre 2026) ----------
FX0, FX1, P0, P1 = 1.1569, 1/0.8927, 20.73, 230.55
SH = 1000*FX0/P0; VAL = SH*P1/FX1; DIV = SH*(10*0.004+8*0.01+2*0.25)/FX1; TOT = VAL+DIV
assert round(TOT, -2) == 11500 and round(VAL) == 11486

def out_back(x, s=1.4): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def L(c, draw, st, box=None, sc=1.0, pivot=(540, 960)):
    layer(c, draw, st.get('a', 1), st.get('blur', 0), st.get('dx', 0), st.get('dy', 0), sc, pivot, box)
def approx(k, s, x, y, size, color, a=1):
    w1 = tw(k, "≈ ", "Poppins", size*0.55, True); w2 = tw(k, s, "Anton", size); x0 = x-(w1+w2)/2
    txt(k, "≈", x0, y, "Poppins", size*0.55, color, True, 'l', a); txt(k, s, x0+w1, y, "Anton", size, color, False, 'l', a)
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')

# ---------- halo néon rapide (flou à demi-résolution) ----------
def neon(c, draw, blur=16, strength=1.0, a=1.0):
    if a <= 0.003: return
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); k = cairo.Context(s); draw(k)
    im = to_pil(s).resize((W//3, H//3), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur/3)).resize((W, H), Image.BILINEAR)
    g = to_cairo(im)
    c.save(); c.set_operator(cairo.OPERATOR_ADD); c.set_source_surface(g, 0, 0); c.paint_with_alpha(strength*a); c.restore()
    c.set_source_surface(s, 0, 0); c.paint_with_alpha(a)

# ---------- script ----------
CAPS = [
 ("c01", "1 000 € dans [Nvidia] il y a 5 ans ?"),
 ("c02", "Aujourd'hui : ≈ [11 500 €]. ×11,5."),
 ("c03", "Comment une boîte de [jeux vidéo] est devenue le roi de l'IA ?"),
 ("c04", "[1993] : trois ingénieurs fondent Nvidia dans un Denny's."),
 ("c05", "Leur produit : des [cartes graphiques] pour les jeux vidéo."),
 ("c06", "Leur force : des milliers de [calculs en même temps]."),
 ("c07", "Exactement ce qu'il faut pour entraîner une [IA]."),
 ("c08", "Fin 2022, ChatGPT arrive. Tout le monde veut ses [puces]."),
 ("c09", "L'action passe de 11 $ à 243 $ : [×21]."),
 ("c10", "Aujourd'hui, Nvidia vaut [5 500 milliards] de dollars."),
 ("c11", "Presque [2 CAC 40] entiers. N°1 mondial."),
 ("c12", "En un trimestre : [96 milliards] de ventes. +106 % en un an."),
 ("c13", "Et [62 centimes] de bénéfice sur chaque dollar vendu."),
 ("c14", "Mais plus de [90 %] des ventes viennent des data centers."),
 ("c15", "Ses clients ? Une poignée de géants. S'ils [freinent]…"),
 ("c16", "La [Chine] ? Exclue des prévisions."),
 ("c17", "8 octobre : doute sur OpenAI, [−2,9 %]."),
 ("c18", "Tes 1 000 € ? ≈ [11 500 €] aujourd'hui."),
 ("c19", "Et toi : tu achètes, tu vends ou tu [attends] ?"),
 ("c20", "Abonne-toi, like, partage."),
]
def build():
    tl, t = {}, 0.0
    for cid, s in CAPS:
        clean = s.replace('[', '').replace(']', '')
        d = max(2.0, len(clean)/20+0.5)
        if cid in ('c02', 'c09', 'c10', 'c18'): d += 0.5
        if cid == 'c19': d += 0.6
        if cid == 'c20': d = 3.2
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.12
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def E(c): return TL[c][0]+TL[c][1]

def parse(s):
    NB = '\u00a0'
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    out = []
    for tok in s.split(' '):
        k = '[' in tok; out.append((tok.replace('[', '').replace(']', '').replace(NB, ' '), k))
    return out
def draw_caption(c, t):
    size = 48
    for cid, s in CAPS:
        a, d = TL[cid]; b = a+d
        if not (a <= t < b): continue
        items = parse(s); sp = tw(c, ' ', "Poppins", size, True)
        wd = [tw(c, w, "Poppins", size, True)+(24 if k else 0) for w, k in items]
        lines, cur, cw = [], [], 0
        for i, w in enumerate(wd):
            need = w+(sp if cur else 0)
            if cur and cw+need > 760: lines.append((cur, cw)); cur, cw = [], 0; need = w
            cur.append(i); cw += need
        lines.append((cur, cw)); y0 = 1352-(len(lines)-1)*37; fo = 1-seg(t, b-0.15, 0.15, in_cubic); n_ = 0
        for li, (idx, lw) in enumerate(lines):
            x = 540-lw/2; y = y0+li*74
            for i in idx:
                w, k = items[i]; ti = a+n_*0.035; n_ += 1
                u = seg(t, ti, 0.22, out_expo); al = clamp((t-ti)/0.12)*fo
                if al > 0:
                    sc = lerp(1.35, 1, out_back(clamp((t-ti)/0.22))) if k else 1
                    yy = y+10*(1-u)
                    c.save(); c.translate(x+wd[i]/2, yy); c.scale(sc, sc); c.translate(-(x+wd[i]/2), -yy)
                    if k:
                        c.save(); c.translate(x+wd[i]/2, yy); c.rotate(-0.025)
                        col(c, RED if cid in ('c15', 'c16', 'c17') else GRN, al); c.rectangle(-wd[i]/2, -33, wd[i], 64); c.fill(); c.restore()
                        txt(c, w, x+12, yy, "Poppins", size, '050505', True, 'l', al)
                    else:
                        txt(c, w, x+2, yy+3, "Poppins", size, '000000', True, 'l', .6*al); txt(c, w, x, yy, "Poppins", size, WHITE, True, 'l', al)
                    c.restore()
                x += wd[i]+sp

def progress(c, t):
    col(c, 'FFFFFF', .15); c.rectangle(140, 262, 800, 5); c.fill()
    col(c, RED if T('c14') <= t < T('c18') else GRN); c.rectangle(140, 262, 800*clamp(t/DUR), 5); c.fill()
def tag(c, s, y, color=GRN, a=1.0):
    if a <= 0: return
    w = tw(c, s, "JetBrains Mono", 24, False, 3)+40
    c.new_path(); c.rectangle(540-w/2, y-24, w, 48); col(c, color, .12*a); c.fill(); col(c, color, .8*a); c.set_line_width(1.5); c.rectangle(540-w/2, y-24, w, 48); c.stroke()
    txt(c, s, 540, y, "JetBrains Mono", 24, color, False, 'c', a, 3)
def slam(t, t0, d=0.22, s0=1.7):
    """entrée « coup de poing » : échelle, opacité"""
    u = clamp((t-t0)/d); return lerp(s0, 1.0, out_back(u, 1.2)), clamp((t-t0)/0.08)

# ---------- impacts : secousse et flash ----------
SLAMS = []
def impacts():
    return [T('c02')+0.15, T('c09')+0.55, T('c10')+0.3, T('c12')+0.25, T('c17')+0.3, T('c18')+1.25]
def shake(t):
    dx = dy = 0
    for ts in impacts():
        if 0 <= t-ts < 0.45:
            e = math.exp(-(t-ts)*11)*16
            dx += e*math.sin((t-ts)*95); dy += e*math.cos((t-ts)*77)
    return dx, dy
def flash(c, t):
    for ts in impacts():
        if 0 <= t-ts < 0.25: col(c, 'FFFFFF', 0.22*(1-(t-ts)/0.25)); c.paint()

# ---------- glitch ----------
def glitch(c, draw, t, amount, box=(0, 300, W, 800)):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); k = cairo.Context(s); draw(k)
    if amount <= 0.01: c.set_source_surface(s, 0, 0); c.paint(); return
    rnd = random.Random(int(t*30)); x0, y0, bw, bh = box; y = y0
    while y < y0+bh:
        h = rnd.randint(8, 60); off = rnd.choice([0, 0, 1, -1])*rnd.randint(4, 40)*amount
        c.save(); c.rectangle(0, y, W, h); c.clip()
        if rnd.random() < 0.35*amount:
            c.set_source_surface(s, off+8*amount, 0); c.paint_with_alpha(0.5)
        c.set_source_surface(s, off, 0); c.paint(); c.restore(); y += h
    c.save(); c.rectangle(0, 0, W, y0); c.rectangle(0, y0+bh, W, H-y0-bh); c.clip(); c.set_source_surface(s, 0, 0); c.paint(); c.restore()

# ---------- scènes ----------
def sc_hook(c, t):
    t1 = T('c02')
    u = seg(t, 0.15, 0.6, out_expo)
    neon(c, lambda k: circuits(k, u, 5, GRN, .28), 14, .6)
    L(c, lambda k: tag(k, "NVDA · 5 ANS", 360), reveal(t, 0.0, 0.35, 16, 10), (300, 320, 480, 80))
    # 1 000 € qui se fait barrer
    st = reveal(t, 0.05, 0.35, 24, 12)
    def thousand(k):
        txt(k, "1 000 €", 540, 470 if t >= t1 else 760, "Anton", 110 if t >= t1 else 200, GREY if t >= t1 else WHITE)
        if t >= t1:
            v = seg(t, t1, 0.25, out_expo); k.new_path(); k.move_to(390, 472); k.line_to(390+300*v, 456); col(k, RED, .9); k.set_line_width(6); k.stroke()
    if t < t1:
        # compteur qui s'emballe
        L(c, thousand, st, (100, 560, 880, 400))
        if t > 1.2:
            v = 1000+(TOT-1000)*in_cubic(clamp((t-1.2)/(t1-1.3)))
            neon(c, lambda k: txt(k, fmt(v)+" €", 540, 1060, "Anton", 110, GRN), 14, .7)
    else:
        thousand(c)
        sc, a = slam(t, t1)
        neon(c, lambda k: (k.save(), k.translate(540, 790), k.scale(sc, sc), k.translate(-540, -790), txt(k, "×11,5", 540, 790, "Anton", 250, GRN), k.restore()), 28, 1.1, a)
        L(c, lambda k: approx(k, "11 500 €", 540, 1070, 110, WHITE), reveal(t, t1+0.25, 0.3, 20, 10), (100, 980, 880, 180))
def sc_shift(c, t):
    t0 = T('c03'); sw = t0+1.0
    neon(c, lambda k: circuits(k, 1, 5, GRN, .2), 14, .5)
    g = clamp(1-abs(t-sw)/0.35)
    def words(k):
        if t < sw: txt(k, "JEUX VIDÉO", 540, 700, "Anton", 170, WHITE)
        else:
            txt(k, "IA", 540, 700, "Anton", 330, GRN)
        txt(k, "1993", 540, 470, "JetBrains Mono", 30, GREY, False, 'c', 1, 6) if t < sw else txt(k, "2026", 540, 470, "JetBrains Mono", 30, GRN, False, 'c', 1, 6)
    st = reveal(t, t0, 0.3, 20, 12)
    if st['blur'] > 0.6: L(c, words, st, (60, 380, 960, 520))
    else: glitch(c, words, t, g, (0, 400, W, 500))
    # pad de jeu → puce, en petit au-dessus
def gamepad(k, cx, cy, s, color=GRN, a=1):
    k.save(); k.translate(cx, cy); k.scale(s, s)
    k.new_path(); k.move_to(-120, -40); k.curve_to(-60, -60, 60, -60, 120, -40); k.curve_to(170, -30, 190, 70, 160, 90)
    k.curve_to(130, 110, 100, 60, 70, 40); k.line_to(-70, 40); k.curve_to(-100, 60, -130, 110, -160, 90); k.curve_to(-190, 70, -170, -30, -120, -40); k.close_path()
    col(k, color, a); k.set_line_width(5/s if s else 5); k.stroke()
    for dx, dy in ((80, -10), (100, 10), (80, 30), (60, 10)): k.new_path(); k.arc(dx, dy, 7, 0, 2*math.pi); k.fill()
    k.rectangle(-100, 3, 50, 12); k.fill(); k.rectangle(-81, -16, 12, 50); k.fill(); k.restore()
def gpu_card(k, cx, cy, t, a=1):
    k.save(); k.translate(cx, cy)
    col(k, '0C0F11', a); k.rectangle(-270, -110, 540, 220); k.fill()
    col(k, GRN, a); k.set_line_width(4); k.rectangle(-270, -110, 540, 220); k.stroke()
    for fx in (-130, 130):
        k.new_path(); k.arc(fx, 0, 82, 0, 2*math.pi); col(k, GRN, .9*a); k.set_line_width(4); k.stroke()
        for i in range(7):
            ang = t*9+i*2*math.pi/7; k.new_path(); k.move_to(fx, 0)
            k.curve_to(fx+40*math.cos(ang), 40*math.sin(ang), fx+70*math.cos(ang+0.5), 70*math.sin(ang+0.5), fx+76*math.cos(ang+0.8), 76*math.sin(ang+0.8))
            col(k, GRN, .7*a); k.set_line_width(3); k.stroke()
        k.new_path(); k.arc(fx, 0, 14, 0, 2*math.pi); col(k, GRN, a); k.fill()
    for i in range(18): col(k, GRN_L, .8*a); k.rectangle(-200+i*18, 110, 10, 26); k.fill()
    col(k, GREY, a); k.rectangle(270, -130, 12, 260); k.fill(); k.restore()
def sc_origin(c, t):
    t0, t1 = T('c04'), T('c05')
    out = conceal(t, T('c06')-0.12, 0.25, (0, -30), 14) if t >= T('c06')-0.12 else {}
    if t < t1:
        sc, a = slam(t, t0+0.05, 0.22, 1.5)
        neon(c, lambda k: (k.save(), k.translate(540, 640), k.scale(sc, sc), k.translate(-540, -640), txt(k, "1993", 540, 640, "Anton", 280, GRN), k.restore()), 24, 1.0, a)
        L(c, lambda k: tag(k, "SAN JOSÉ · CALIFORNIE", 860), reveal(t, t0+0.35, 0.3, 16, 8), (200, 820, 680, 80))
        for i, n in enumerate(("JENSEN HUANG", "CHRIS MALACHOWSKY", "CURTIS PRIEM")):
            L(c, lambda k, n=n, i=i: txt(k, n, 540, 960+i*52, "JetBrains Mono", 30, WHITE, False, 'c', 1, 2),
              reveal(t, t0+0.6+i*0.12, 0.3, 14, 8), (100, 920+i*52, 880, 80))
    else:
        st = merge(reveal(t, t1, 0.3, 30, 14), out)
        neon(c, lambda k: gpu_card(k, 540, 720, t), 18, .9, st['a'])
        L(c, lambda k: tag(k, "CARTES GRAPHIQUES · GAMING", 980), merge(reveal(t, t1+0.3, 0.3, 16, 8), out), (180, 940, 720, 80))
        L(c, lambda k: gamepad(k, 540, 460, .8, GREY, .8), merge(reveal(t, t1+0.45, 0.3, 16, 8), out), (300, 380, 480, 160))
def sc_parallel(c, t):
    t0, t1 = T('c06'), T('c07')
    out = conceal(t, T('c08')-0.12, 0.25, (0, -30), 14) if t >= T('c08')-0.12 else {}
    if t < t1:
        st = reveal(t, t0, 0.3, 24, 12)
        def cpu(k):
            txt(k, "CPU", 300, 470, "JetBrains Mono", 30, GREY, False, 'c', 1, 6)
            on = int((t-t0)*5) % 4
            for i in range(4):
                x, y = 210+(i % 2)*95, 540+(i//2)*95
                col(k, GRN if i == on else '1A1F22'); k.rectangle(x, y, 80, 80); k.fill()
            txt(k, "4 cœurs", 300, 780, "Poppins", 26, GREY)
        def gpu(k):
            txt(k, "GPU", 780, 470, "JetBrains Mono", 30, GRN, False, 'c', 1, 6)
            n = 16
            for i in range(n):
                for j in range(n):
                    v = 0.5+0.5*math.sin((t-t0)*12-(i+j)*0.35)
                    col(k, GRN, 0.15+0.85*v); k.rectangle(660+i*15, 540+j*15, 11, 11); k.fill()
            txt(k, "des milliers", 780, 820, "Poppins", 26, GRN)
        L(c, cpu, merge(st, out), (150, 420, 330, 420))
        neon(c, gpu, 12, .8, merge(reveal(t, t0+0.2, 0.3, 24, 12), out)['a'])
        L(c, lambda k: txt(k, "VS", 540, 650, "Anton", 70, WHITE), merge(reveal(t, t0+0.35, 0.25, 10, 8), out), (440, 590, 200, 120))
    else:
        u = seg(t, t1, 0.9, out_quint)
        def net(k):
            layers = [(240, 4), (440, 6), (640, 6), (840, 3)]
            pts = [[(x, 700+(j-(n-1)/2)*95) for j in range(n)] for x, n in layers]
            for li in range(3):
                for p in pts[li]:
                    for q in pts[li+1]:
                        f = clamp(u*3-li)
                        if f <= 0: continue
                        k.new_path(); k.move_to(*p); k.line_to(p[0]+(q[0]-p[0])*f, p[1]+(q[1]-p[1])*f)
                        col(k, GRN, .35); k.set_line_width(1.5); k.stroke()
            for li, row in enumerate(pts):
                for j, p in enumerate(row):
                    if u*3 < li-0.2: continue
                    v = 0.5+0.5*math.sin(t*10-li*1.3-j)
                    k.new_path(); k.arc(*p, 16, 0, 2*math.pi); col(k, GRN, .4+.6*v); k.fill()
            txt(k, "IA", 540, 430, "Anton", 150, WHITE)
        neon(c, net, 16, 1.0, merge(reveal(t, t1, 0.3, 20, 10), out)['a'])

# courbe : points (années depuis le 8 oct. 2021, cours ajusté en $)
P = [(0, 20.7), (.14, 33.3), (.25, 29.4), (.45, 26.5), (.7, 15.6), (.9, 12.5), (1.01, 11.2), (1.14, 16.9), (1.3, 19.5), (1.45, 27.8),
     (1.62, 37.9), (1.85, 46.5), (2.0, 43.5), (2.23, 49.5), (2.38, 79.0), (2.55, 95), (2.7, 123.5), (2.83, 109.6), (3.0, 132.7),
     (3.12, 138), (3.23, 134.3), (3.32, 120), (3.48, 94.3), (3.7, 157.8), (3.85, 180), (4.06, 207.0), (4.23, 186.5), (4.37, 175),
     (4.6, 205), (4.81, 191.1), (4.91, 230.5), (4.99, 243.4), (5.0, 230.55)]
_xs = np.array([p[0] for p in P]); _ys = np.array([p[1] for p in P])
def price(u):
    u = clamp(u, 0, 5); i = min(np.searchsorted(_xs, u, 'right')-1, len(_xs)-2)
    f = (u-_xs[i])/(_xs[i+1]-_xs[i]); return _ys[i]+(_ys[i+1]-_ys[i])*f
X0, X1, YB, YT = 160, 850, 1180, 470
def X(u): return X0+u/5*(X1-X0)
def Y(v): return YB-v/260*(YB-YT)
def U(t):
    a, b = T('c08')+0.2, T('c09')+0.5
    if t < a: return 0.0
    if t < a+1.1: return lerp(0, 1.14, in_out((t-a)/1.1))
    return lerp(1.14, 5.0, in_out(clamp((t-a-1.1)/(b-a-1.1))))
def sc_chart(c, t):
    t0 = T('c08'); u = U(t)
    out = conceal(t, T('c10')-0.12, 0.25, (0, -30), 14) if t >= T('c10')-0.12 else {}
    a = merge(reveal(t, t0, 0.3, 20, 10), out)
    def grid(k):
        tag(k, "COURS NVDA · $", 340)
        for v in (50, 100, 150, 200, 250):
            col(k, 'FFFFFF', .06); k.rectangle(X0, Y(v), X1-X0, 1); k.fill(); txt(k, f"{v}", X1+12, Y(v), "JetBrains Mono", 18, GREY, False, 'l')
        for j, yr in enumerate(("2022", "2023", "2024", "2025", "2026")): txt(k, yr, X(.23+j)+40, YB+34, "JetBrains Mono", 18, GREY)
    L(c, grid, a, (100, 300, 900, 960))
    if u <= 0: return
    n = max(2, int(u*80)); pts = [(X(u*i/n), Y(price(u*i/n))) for i in range(n+1)]
    c.save(); c.translate(a.get('dx', 0), a.get('dy', 0))
    c.new_path(); c.move_to(X(0), YB); [c.line_to(*p) for p in pts]; c.line_to(pts[-1][0], YB); c.close_path()
    g = cairo.LinearGradient(0, YT, 0, YB); g.add_color_stop_rgba(0, *hx(GRN, .28*a['a'])); g.add_color_stop_rgba(1, *hx(GRN, 0)); c.set_source(g); c.fill()
    def curve(k):
        k.new_path(); k.move_to(*pts[0]); [k.line_to(*p) for p in pts[1:]]; col(k, GRN); k.set_line_width(5); k.set_line_join(cairo.LINE_JOIN_ROUND); k.stroke()
        k.new_path(); k.arc(*pts[-1], 9, 0, 2*math.pi); col(k, GRN_L); k.fill()
    neon(c, curve, 14, 1.2, a['a'])
    if u >= 1.01:
        pa = seg(t, T('c08')+0.9, 0.3)*a['a']
        c.new_path(); c.arc(X(1.01), Y(11.2), 9, 0, 2*math.pi); col(c, RED, pa); c.fill()
        txt(c, "11,2 $ · OCT. 2022", X(1.01)+16, Y(11.2)-46, "JetBrains Mono", 22, RED, False, 'l', pa, 1)
    if u >= 1.14:
        pa = seg(t, T('c08')+1.3, 0.3)*a['a']
        col(c, WHITE, .5*pa); c.rectangle(X(1.14), YB-300, 2, 300); c.fill()
        txt(c, "CHATGPT", X(1.14)+12, YB-150, "JetBrains Mono", 22, WHITE, False, 'l', pa, 3)
    if u >= 4.99:
        pa = seg(t, T('c09')+0.3, 0.3)*a['a']
        txt(c, "243 $ · RECORD", X(4.99)-10, Y(243.4)-30, "JetBrains Mono", 22, GRN, False, 'r', pa, 1)
    if t >= T('c09')+0.55:
        sc, al = slam(t, T('c09')+0.55)
        neon(c, lambda k: (k.save(), k.translate(X(1.3), Y(205)), k.scale(sc, sc), k.translate(-X(1.3), -Y(205)), txt(k, "×21", X(1.3), Y(205), "Anton", 170, WHITE), k.restore()), 18, .6, al*a['a'])
    c.restore()
def sc_monster(c, t):
    t0, t1 = T('c10'), T('c11')
    out = conceal(t, T('c12')-0.12, 0.25, (0, -30), 14) if t >= T('c12')-0.12 else {}
    a = merge(reveal(t, t0, 0.3, 20, 10), out)
    neon(c, lambda k: (circuits(k, seg(t, t0, 0.6), 9, GRN, .25), da.chip(k, 540, 560, 230)), 16, .9, a['a'])
    v = 5500*out_expo(clamp((t-t0-0.05)/0.45)); sc, al = slam(t, t0+0.3, 0.2, 1.25)
    def big(k):
        k.save(); k.translate(540, 880); k.scale(sc, sc); k.translate(-540, -880)
        txt(k, fmt(v), 540, 880, "Anton", 230, WHITE); k.restore()
        txt(k, "MILLIARDS DE DOLLARS", 540, 1025, "JetBrains Mono", 30, GRN, False, 'c', 1, 4)
    L(c, big, a, (60, 700, 960, 380))
    if t >= t1:
        for i, (lab, val, cl) in enumerate((("NVIDIA", 5.5, GRN), ("TOUT LE CAC 40", 3.0, GREY))):
            g = seg(t, t1+0.1+i*0.15, 0.45, out_expo)
            def bar(k, i=i, lab=lab, val=val, cl=cl, g=g):
                y = 1105+i*62; txt(k, lab, 170, y, "JetBrains Mono", 22, cl, False, 'l', 1, 2)
                col(k, cl, .9 if i == 0 else .5); k.rectangle(440, y-15, 380*val/5.5*g, 30); k.fill()
                if g > .9: txt(k, ("5,5" if i == 0 else "≈ 3") + " T$", 440+380*val/5.5+12, y, "JetBrains Mono", 20, cl, False, 'l')
            L(c, bar, merge(reveal(t, t1+0.1+i*0.15, 0.25, 12, 6), out), (150, 1070+i*62, 880, 70))
        L(c, lambda k: tag(k, "N°1 MONDIAL", 340), merge(reveal(t, t1+0.5, 0.25, 12, 8), out), (300, 300, 480, 80))
def sc_cash(c, t):
    t0, t1 = T('c12'), T('c13')
    out = conceal(t, T('c14')-0.12, 0.25, (0, -30), 14) if t >= T('c14')-0.12 else {}
    if t < t1:
        a = merge(reveal(t, t0, 0.25, 20, 10), out)
        v = 96.2*out_expo(clamp((t-t0)/0.5)); sc, al = slam(t, t0+0.25, 0.2, 1.3)
        neon(c, lambda k: (k.save(), k.translate(540, 680), k.scale(sc, sc), k.translate(-540, -680),
                           txt(k, f"{v:.1f}".replace('.', ',')+" Md$", 540, 680, "Anton", 165, GRN), k.restore()), 22, 1.0, a['a'])
        L(c, lambda k: tag(k, "VENTES · 1 TRIMESTRE", 480), a, (250, 440, 580, 80))
        def pill(k):
            w = 300; k.new_path(); k.rectangle(540-w/2, 870, w, 90); col(k, GRN); k.fill(); txt(k, "+106 % / 1 AN", 540, 915, "Anton", 54, '050505')
        L(c, pill, merge(reveal(t, t0+0.6, 0.25, 20, 10), out), (300, 840, 480, 150))
    else:
        a = merge(reveal(t, t1, 0.3, 20, 10), out)
        f = seg(t, t1+0.2, 0.8, in_out)*0.62
        def gauge(k):
            cx, cy, r = 540, 760, 250
            k.new_path(); k.arc(cx, cy, r, 0, 2*math.pi); col(k, '1A1F22'); k.set_line_width(36); k.stroke()
            if f > 0: k.new_path(); k.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*f); col(k, GRN); k.set_line_width(36); k.stroke()
            txt(k, f"{round(f*100)} %", cx, cy-30, "Anton", 150, WHITE)
            txt(k, "DE MARGE NETTE", cx, cy+75, "JetBrains Mono", 24, GRN, False, 'c', 1, 3)
        neon(c, gauge, 18, .8, a['a'])
        L(c, lambda k: tag(k, "1 $ VENDU = 0,62 $ DE BÉNÉFICE", 1090), merge(reveal(t, t1+0.8, 0.25, 12, 8), out), (120, 1050, 840, 80))
def sc_doubt(c, t):
    t0, t1, t2, t3 = T('c14'), T('c15'), T('c16'), T('c17')
    out = conceal(t, T('c18')-0.12, 0.25, (0, -30), 14) if t >= T('c18')-0.12 else {}
    # voile rouge qui monte
    r = cairo.RadialGradient(540, 860, 0, 540, 860, 1000); r.add_color_stop_rgba(0, *hx('3A0A10', .55*seg(t, t0, 0.8))); r.add_color_stop_rgba(1, *hx('000000', 0)); c.set_source(r); c.paint()
    if t < t1:
        a = merge(reveal(t, t0, 0.3, 20, 10), conceal(t, t1-0.12, 0.2, (0, -20), 10) if t >= t1-0.12 else {})
        f = seg(t, t0+0.2, 0.8, in_out)*0.925
        def donut(k):
            cx, cy, r_ = 540, 740, 240
            k.new_path(); k.arc(cx, cy, r_, 0, 2*math.pi); col(k, '1A1F22'); k.set_line_width(60); k.stroke()
            k.new_path(); k.arc(cx, cy, r_, -math.pi/2, -math.pi/2+2*math.pi*f); col(k, GRN); k.set_line_width(60); k.stroke()
            txt(k, f"{f*100:.1f}".replace('.', ',')+" %", cx, cy-20, "Anton", 120, WHITE)
            txt(k, "DATA CENTERS", cx, cy+70, "JetBrains Mono", 26, GRN, False, 'c', 1, 4)
        neon(c, donut, 16, .7, a['a'])
        L(c, lambda k: tag(k, "UN SEUL MOTEUR", 400, RED), a, (250, 360, 580, 80))
    elif t < t2:
        a = merge(reveal(t, t1, 0.3, 20, 10), conceal(t, t2-0.12, 0.2, (0, -20), 10) if t >= t2-0.12 else {})
        def giants(k):
            txt(k, "NVIDIA", 540, 1010, "Anton", 80, GRN)
            for i in range(4):
                x = 210+i*220; s_ = 1+0.04*math.sin(t*6+i)
                k.save(); k.translate(x, 600); k.scale(s_, s_)
                k.rectangle(-80, -80, 160, 160); col(k, '15191C'); k.fill_preserve(); col(k, WHITE, .7); k.set_line_width(3); k.stroke()
                txt(k, "?", 0, 0, "Anton", 90, WHITE); k.restore()
                fl = 0.5+0.5*math.sin(t*8-i)
                k.new_path(); k.move_to(x, 690); k.line_to(540+(x-540)*0.3, 950); col(k, GRN if t < t1+1.6 else RED, .3+.5*fl); k.set_line_width(4); k.stroke()
            txt(k, "GÉANTS DE LA TECH", 540, 460, "JetBrains Mono", 26, WHITE, False, 'c', 1, 4)
        L(c, giants, a, (60, 400, 960, 700))
    elif t < t3:
        a = merge(reveal(t, t2, 0.3, 20, 10), conceal(t, t3-0.12, 0.2, (0, -20), 10) if t >= t3-0.12 else {})
        sc, al = slam(t, t2+0.5, 0.2, 2.0)
        def china(k):
            txt(k, "CHINE", 540, 640, "Anton", 230, WHITE)
            k.save(); k.translate(540, 870); k.rotate(-0.12); k.scale(sc, sc)
            w = 640; col(k, RED, al); k.set_line_width(8); k.rectangle(-w/2, -70, w, 140); k.stroke()
            txt(k, "EXCLUE", 0, 0, "Anton", 110, RED, False, 'c', al); k.restore()
            txt(k, "PRÉVISIONS SANS LA CHINE", 540, 1040, "JetBrains Mono", 26, GREY, False, 'c', 1, 3)
        L(c, china, a, (40, 450, 1000, 680))
    else:
        a = merge(reveal(t, t3, 0.25, 20, 10), out)
        g = clamp(1-abs(t-(t3+0.3))/0.3)
        def drop(k):
            tag(k, "8 OCTOBRE 2026", 420, RED)
            txt(k, "−2,9 %", 540, 700, "Anton", 260, RED)
            txt(k, "UN DOUTE SUR OPENAI", 540, 900, "JetBrains Mono", 28, WHITE, False, 'c', 1, 3)
            # bougie rouge
            k.new_path(); k.move_to(540, 990); k.line_to(540, 1160); col(k, RED); k.set_line_width(4); k.stroke()
            k.rectangle(505, 1010, 70, 120); k.fill()
        if a.get('blur', 0) > 0.6: L(c, drop, a, (40, 360, 1000, 830))
        else: glitch(c, drop, t, g, (0, 560, W, 300))
_COIN = None
def coin_img():
    global _COIN
    if _COIN is None: _COIN = cairo.ImageSurface.create_from_png('/home/claude/struck/piece_frappee_seule.png')
    return _COIN
def sc_reveal(c, t):
    t0 = T('c18'); out = conceal(t, T('c19')-0.12, 0.25, (0, -30), 14) if t >= T('c19')-0.12 else {}
    a = merge(reveal(t, t0, 0.3, 30, 14), out)
    v = 1000+(TOT-1000)*out_expo(clamp((t-t0-0.4)/0.85))
    def card(k):
        k.new_path(); k.rectangle(170, 470, 740, 640); col(k, '0B0E10'); k.fill(); col(k, GRN, .9); k.set_line_width(3); k.rectangle(170, 470, 740, 640); k.stroke()
        txt(k, "1 000 € INVESTIS IL Y A 5 ANS", 540, 540, "JetBrains Mono", 24, GREY, False, 'c', 1, 2)
        txt(k, "AUJOURD'HUI", 540, 640, "JetBrains Mono", 24, GRN, False, 'c', 1, 4)
        approx(k, fmt(round(v, -1) if v < TOT-20 else 11500)+" €", 540, 790, 160, WHITE)
        txt(k, f"actions ≈ {fmt(VAL)} € · dividendes ≈ {round(DIV)} €", 540, 930, "Poppins", 26, GREY)
        txt(k, "change €/$ inclus · avant impôts et frais", 540, 1040, "Poppins", 22, GREY)
    neon(c, card, 18, .6, a['a'])
    if t >= t0+1.25:
        sc, al = slam(t, t0+1.25, 0.2, 1.8)
        def seal(k):
            k.save(); k.translate(800, 432); k.rotate(-0.15); k.scale(sc, sc)
            col(k, GRN, al); k.rectangle(-120, -50, 240, 100); k.fill(); txt(k, "×11,5", 0, 0, "Anton", 70, '050505', False, 'c', al); k.restore()
        L(c, seal, merge(dict(a=1), out))
def sc_question(c, t):
    t0 = T('c19'); out = conceal(t, T('c20')-0.12, 0.25, (0, -30), 14) if t >= T('c20')-0.12 else {}
    L(c, lambda k: (tag(k, "À 230 $ L'ACTION", 420), txt(k, "ET TOI ?", 540, 540, "Anton", 140, WHITE)), merge(reveal(t, t0, 0.3, 20, 12), out), (100, 360, 880, 260))
    for j, (lab, cl) in enumerate((("J'ACHÈTE", GRN), ("JE VENDS", RED), ("J'ATTENDS", WHITE))):
        st = merge(reveal(t, t0+0.3+j*0.15, 0.3, 24, 12), out)
        def btn(k, j=j, lab=lab, cl=cl):
            y = 680+j*150; k.rectangle(240, y, 600, 115); col(k, cl, .1); k.fill(); col(k, cl); k.set_line_width(3); k.rectangle(240, y, 600, 115); k.stroke()
            txt(k, lab, 540, y+58, "Anton", 64, cl)
        L(c, btn, st, (200, 640+j*150, 680, 200))
def sc_cta(c, t):
    t0 = T('c20')
    st = reveal(t, t0, 0.35, 20, 12)
    def head(k):
        from lvmh import logo_symbol
        logo_symbol(k, 540, 475, 200)
        txt(k, "Actions_Benefices", 540, 650, "Poppins", 44, WHITE, True)
    neon(c, head, 20, .35, st['a'])
    for j, lab in enumerate(("ABONNE-TOI", "LIKE", "PARTAGE")):
        s2 = reveal(t, t0+0.3+j*0.3, 0.3, 22, 12)
        def b(k, j=j, lab=lab):
            y = 730+j*140; k.rectangle(270, y, 540, 105); col(k, GRN, .12); k.fill(); col(k, GRN); k.set_line_width(3); k.rectangle(270, y, 540, 105); k.stroke()
            txt(k, lab, 540, y+53, "Anton", 58, WHITE)
        L(c, b, s2, (230, 690+j*140, 620, 180))
    L(c, lambda k: txt(k, "CONTENU PÉDAGOGIQUE, PAS UN CONSEIL EN INVESTISSEMENT", 540, 1190, "JetBrains Mono", 17, GREY, False, 'c', 1, 1), reveal(t, t0+1.2, 0.3, 8, 6))

SCENES = [(0, T('c03'), sc_hook), (T('c03'), T('c04'), sc_shift), (T('c04'), T('c06'), sc_origin), (T('c06'), T('c08'), sc_parallel),
          (T('c08'), T('c10'), sc_chart), (T('c10'), T('c12'), sc_monster), (T('c12'), T('c14'), sc_cash), (T('c14'), T('c18'), sc_doubt),
          (T('c18'), T('c19'), sc_reveal), (T('c19'), T('c20'), sc_question), (T('c20'), DUR+0.1, sc_cta)]
WHIPS = [T(k) for k in ('c03', 'c04', 'c06', 'c08', 'c10', 'c12', 'c14', 'c18', 'c19', 'c20')]
MB = [(w-0.12, w+0.12) for w in WHIPS]

def scene(c, t):
    c.set_source_surface(background(), 0, 0); c.paint()
    dx, dy = shake(t)
    # coupe « whip » : glissement rapide vers le haut à chaque changement de scène
    wy = 0
    for w in WHIPS:
        if 0 <= t-w < 0.18: wy = 120*(1-out_expo((t-w)/0.18))
    c.save(); c.translate(dx, dy+wy)
    for a, b, fn in SCENES:
        if a <= t < b: fn(c, t)
    c.restore()
    flash(c, t)
    if T('c08') <= t < T('c14'): txt(c, "Cours ajustés des divisions · Pas un conseil en investissement", 540, 1458, "JetBrains Mono", 16, GREY, False, 'c', .9)
    draw_caption(c, t); progress(c, t)
    if t > DUR-0.35: col(c, '000000', clamp((t-(DUR-0.35))/0.35)); c.paint()

def render(t, surf, ctx, n=4):
    if not any(a <= t < b for a, b in MB):
        scene(ctx, t); surf.flush(); return np.ndarray((H, W, 4), np.uint8, surf.get_data()).copy()
    acc = np.zeros((H, W, 4), np.float32)
    for k in range(n):
        scene(ctx, t+(k/n-0.5)*(0.6/FPS)); surf.flush(); acc += np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return (acc/n).astype(np.uint8)

def events():
    ev = [(0.0, 'riser'), (0.05, 'hit'), (1.2, 'count'), (T('c02'), 'whoosh'), (T('c02')+0.15, 'drop'), (T('c02')+0.4, 'click')]
    ev += [(T('c03'), 'whoosh'), (T('c03')+1.0, 'glitch')]
    ev += [(T('c04'), 'whoosh'), (T('c04')+0.1, 'hit')] + [(T('c04')+0.6+i*0.12, 'blip', i) for i in range(3)]
    ev += [(T('c05'), 'whoosh'), (T('c05')+0.1, 'spin')]
    ev += [(T('c06'), 'whoosh')] + [(T('c06')+0.2+i*0.2, 'blip', i % 4) for i in range(8)]
    ev += [(T('c07'), 'whoosh'), (T('c07')+0.1, 'rise')]
    ev += [(T('c08'), 'whoosh'), (T('c08')+0.9, 'low'), (T('c08')+1.3, 'click'), (T('c08')+1.4, 'riser'), (T('c09')+0.3, 'click'), (T('c09')+0.55, 'drop')]
    ev += [(T('c10'), 'whoosh'), (T('c10')+0.05, 'count'), (T('c10')+0.3, 'drop')] + [(T('c11')+0.1+i*0.15, 'blip', i) for i in range(2)] + [(T('c11')+0.5, 'click')]
    ev += [(T('c12'), 'whoosh'), (T('c12')+0.25, 'drop'), (T('c12')+0.6, 'click'), (T('c13'), 'whoosh'), (T('c13')+0.2, 'rise')]
    ev += [(T('c14'), 'tension'), (T('c14')+0.2, 'rise'), (T('c15'), 'whoosh'), (T('c15')+1.6, 'low')]
    ev += [(T('c16'), 'whoosh'), (T('c16')+0.5, 'stamp'), (T('c17'), 'glitch'), (T('c17')+0.3, 'fall')]
    ev += [(T('c18'), 'whoosh'), (T('c18')+0.4, 'count'), (T('c18')+1.25, 'drop')]
    ev += [(T('c19'), 'whoosh')] + [(T('c19')+0.3+j*0.15, 'click') for j in range(3)]
    ev += [(T('c20'), 'whoosh'), (T('c20')+0.05, 'shimmer')] + [(T('c20')+0.3+j*0.3, 'click') for j in range(3)]
    return ev

def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 2) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            a = render(tt, surf, ctx)
            Image.frombuffer('RGBA', (W, H), a.tobytes(), 'raw', 'BGRA', W*4, 1).convert('RGB').save(f'/home/claude/nvda/prev_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(render(i/FPS, surf, ctx).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))

if __name__ == '__main__': main()
