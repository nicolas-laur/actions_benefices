"""Scène test « niveau studio » dans la DA Actions_Benefices.
Grammaire empruntée à la référence (pas sa DA) : entrées par flou qui se dissipe sans rebond,
continuité des éléments, conteneurs vides avant remplissage, mise au point qui se déplace,
flou de mouvement sur les déplacements rapides, 60 i/s."""
import sys, math, subprocess
import numpy as np, cairo
from PIL import Image, ImageFilter

W, H, FPS, DUR = 1080, 1920, 60, 16.0

def hx(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
CREAM, INK, SOFT, LINE, WHITE = hx('F6F4EF'), hx('15181F'), hx('7A7F8C'), hx('E4E0D8'), hx('FFFFFF')
TEAL, TEAL_L, TEAL_D = hx('14A38B'), hx('6FD6C3'), hx('0E7F6C')
CORAL, GOLD, GOLD_D, BLUE = hx('F0555D'), hx('F4B400'), hx('C98F00'), hx('2F6FEB')

# ---------- courbes de mouvement (aucun rebond) ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_quint(x): x = clamp(x); return 1-(1-x)**5
def out_expo(x): x = clamp(x); return 1 if x >= 1 else 1-2**(-10*x)
def in_out_cubic(x):
    x = clamp(x); return 4*x**3 if x < 0.5 else 1-(-2*x+2)**3/2
def in_cubic(x): x = clamp(x); return x**3
def lerp(a, b, u): return a+(b-a)*u
def seg(t, a, d, f=out_quint): return f((t-a)/d)

# ---------- texte ----------
def font(c, size, weight='bold'):
    fam = {'bold': ("Poppins", cairo.FONT_WEIGHT_BOLD), 'medium': ("Poppins Medium", cairo.FONT_WEIGHT_NORMAL),
           'regular': ("Poppins", cairo.FONT_WEIGHT_NORMAL), 'light': ("Poppins Light", cairo.FONT_WEIGHT_NORMAL)}[weight]
    c.select_font_face(fam[0], cairo.FONT_SLANT_NORMAL, fam[1]); c.set_font_size(size)
def tw(c, s, size, weight='bold'): font(c, size, weight); return c.text_extents(s).x_advance
def txt(c, s, x, y, size, col, weight='bold', align='c', a=1.0, track=0.0):
    if a <= 0.002: return
    font(c, size, weight)
    adv = [c.text_extents(ch).x_advance for ch in s] if track else None
    w = (sum(adv)+track*(len(s)-1)) if track else c.text_extents(s).x_advance
    x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.82
    c.set_source_rgba(col[0], col[1], col[2], col[3]*a)
    if track:
        for ch, ad in zip(s, adv): c.move_to(x0, yy); c.show_text(ch); x0 += ad+track
    else: c.move_to(x0, yy); c.show_text(s)

def rr(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path()
    c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()
def src(c, col, a=1.0): c.set_source_rgba(col[0], col[1], col[2], col[3]*a)

# ---------- flou (PIL) ----------
def to_pil(s):
    s.flush(); return Image.frombuffer('RGBA', (s.get_width(), s.get_height()), bytes(s.get_data()), 'raw', 'BGRA', s.get_stride(), 1)
def to_cairo(im):
    data = bytearray(im.tobytes('raw', 'BGRA'))
    return cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, im.width, im.height, im.width*4)

_SH = {}
def soft_rect(w, h, r, blur, col):
    """rectangle arrondi flouté (ombre ou halo), mis en cache"""
    key = (int(w)//4, int(h)//4, int(r), int(blur), col)
    if key not in _SH:
        m = int(blur*3)+4; s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w)+2*m, int(h)+2*m); c = cairo.Context(s)
        rr(c, m, m, w, h, r); src(c, col); c.fill()
        _SH[key] = (to_cairo(to_pil(s).filter(ImageFilter.GaussianBlur(blur))), m)
    return _SH[key]
def paint_soft(c, x, y, w, h, r, blur, col, a=1.0):
    s, m = soft_rect(w, h, r, blur, col); c.set_source_surface(s, x-m, y-m); c.paint_with_alpha(a)

# ---------- calque : opacité, flou, décalage, échelle ----------
def layer(c, draw, a=1.0, blur=0.0, dx=0.0, dy=0.0, sc=1.0, pivot=(540, 960), box=None):
    """draw(c) dessine en coordonnées écran. box = (x, y, w, h) zone utile pour le flou."""
    if a <= 0.003: return
    if blur < 0.6:
        c.push_group(); c.save(); c.translate(dx, dy); c.translate(*pivot); c.scale(sc, sc); c.translate(-pivot[0], -pivot[1])
        draw(c); c.restore(); c.pop_group_to_source(); c.paint_with_alpha(a); return
    bx, by, bw, bh = box or (0, 0, W, H); m = int(blur*3)+6
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(bw)+2*m, int(bh)+2*m); k = cairo.Context(s)
    k.translate(-bx+m, -by+m); k.translate(dx, dy); k.translate(*pivot); k.scale(sc, sc); k.translate(-pivot[0], -pivot[1])
    draw(k)
    b = to_cairo(to_pil(s).filter(ImageFilter.GaussianBlur(blur)))
    c.set_source_surface(b, bx-m, by-m); c.paint_with_alpha(a)

def reveal(t, t0, d=0.45, rise=26, blur0=16):
    """entrée signature : flou qui se dissipe, montée douce, aucune sur-oscillation"""
    u = seg(t, t0, d, out_quint)
    return dict(a=clamp((t-t0)/(d*0.6)), blur=blur0*(1-u), dy=rise*(1-u))
def conceal(t, t0, d=0.4, drift=(0, -20), blur1=12):
    u = seg(t, t0, d, in_cubic)
    return dict(a=1-u, blur=blur1*u, dx=drift[0]*u, dy=drift[1]*u)
def merge(*ds):
    out = dict(a=1.0, blur=0.0, dx=0.0, dy=0.0)
    for d in ds:
        out['a'] *= d.get('a', 1); out['blur'] = max(out['blur'], d.get('blur', 0))
        out['dx'] += d.get('dx', 0); out['dy'] += d.get('dy', 0)
    return out

# ---------- composants ----------
def card(c, x, y, w, h, r=30, highlight=0.0, glow_col=TEAL):
    paint_soft(c, x, y+18, w, h, r, 26, hx('1A1D24'), 0.10)
    paint_soft(c, x, y+3, w, h, r, 4, hx('1A1D24'), 0.06)
    if highlight > 0: paint_soft(c, x-6, y-6, w+12, h+12, r+6, 22, glow_col, 0.55*highlight)
    rr(c, x, y, w, h, r); src(c, WHITE); c.fill()
    g = cairo.LinearGradient(0, y, 0, y+h); g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(1, 0.96, 0.95, 0.93, 1)
    rr(c, x, y, w, h, r); c.set_source(g); c.fill()
    rr(c, x+0.5, y+0.5, w-1, h-1, r); src(c, LINE); c.set_line_width(1.5); c.stroke()
    if highlight > 0:
        rr(c, x+1, y+1, w-2, h-2, r); src(c, glow_col, highlight); c.set_line_width(3); c.stroke()

_BG = None
def background():
    global _BG
    if _BG is None:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
        src(c, hx('EFEBE3')); c.paint()
        g = cairo.RadialGradient(540, 860, 60, 540, 900, 1250)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.95); g.add_color_stop_rgba(0.55, 0.97, 0.96, 0.94, 0.6); g.add_color_stop_rgba(1, 0.91, 0.89, 0.85, 0)
        c.set_source(g); c.paint()
        c.set_line_width(1.5)
        for gx in range(0, W+1, 90): c.move_to(gx, 0); c.line_to(gx, H)
        for gy in range(0, H+1, 90): c.move_to(0, gy); c.line_to(W, gy)
        src(c, LINE, 0.35); c.stroke()
        _BG = s
    return _BG

# ---------- sous-titres (mot à mot, fondu + montée, pas de rebond) ----------
CAPS = [(0.25, 2.55, ["Le", "géant", "discret", "du", ("CAC 40.", INK)]),
        (2.85, 5.55, [("27 Md€", TEAL), "de", "ventes,", "65 000", "salariés,", "59", "pays."]),
        (5.85, 9.55, ["Dividende :", "de", "2,90 €", "à", ("3,70 €", GOLD), "par", "action."]),
        (9.85, 12.95, ["Tous", "les", "deux", "ans :", ("1 action gratuite", TEAL), "pour", "10."]),
        (13.15, 15.85, ["Tes", "1 000 € ?", "Environ", ("1 735 €", TEAL), "aujourd'hui."])]
def captions(c, t):
    for a, b, words in CAPS:
        if not (a <= t < b): continue
        size = 54; items = [(w, None) if isinstance(w, str) else w for w in words]
        sp = tw(c, ' ', size); wd = [tw(c, w, size) for w, _ in items]; pad = [18 if k else 0 for _, k in items]
        lines, cur, cw = [], [], 0
        for i in range(len(items)):
            need = wd[i]+2*pad[i]+(sp if cur else 0)
            if cur and cw+need > 880: lines.append((cur, cw)); cur, cw = [], 0; need = wd[i]+2*pad[i]
            cur.append(i); cw += need
        lines.append((cur, cw))
        y0 = 1350-(len(lines)-1)*41; fo = 1-seg(t, b-0.22, 0.22, in_cubic)
        for li, (idx, lw) in enumerate(lines):
            x = 540-lw/2; y = y0+li*82
            for i in idx:
                w, k = items[i]; x += pad[i]
                u = seg(t, a+i*0.055, 0.32); al = clamp((t-a-i*0.055)/0.18)*fo
                yy = y+14*(1-u)
                if al > 0:
                    if k:
                        rr(c, x-14, yy-38, wd[i]+28, 76, 16); src(c, k, al); c.fill()
                        txt(c, w, x, yy, size, INK if k == GOLD else WHITE, 'bold', 'l', al)
                    else: txt(c, w, x, yy, size, INK, 'bold', 'l', al)
                x += wd[i]+pad[i]+sp

# ---------- scène ----------
CARDS = [("27 Md€", "chiffre d'affaires"), ("65 000", "salariés"), ("59", "pays")]
DIVS = [("2021", 2.90), ("2022", 2.95), ("2023", 3.20), ("2024", 3.30), ("2025", 3.70)]
RING_C, RING_R, RING_T = (540, 800), 230, 46

def title_block(c):
    txt(c, "Air Liquide", 540, 760, 120, INK)
def title_rule(c, u):
    w = 260*u; c.move_to(540-w/2, 850); c.line_to(540+w/2, 850); src(c, TEAL); c.set_line_width(3); c.stroke()
def title_sub(c):
    txt(c, "DEPUIS 1902  ·  CAC 40", 540, 905, 26, SOFT, 'medium', 'c', 1, track=6)

def scene(c, t):
    c.set_source_surface(background(), 0, 0); c.paint()

    # --- titre : entrée floue, puis il monte et rétrécit (continuité), puis sort par le haut
    if t < 6.4:
        up = seg(t, 2.6, 0.7, in_out_cubic); sc_ = lerp(1.0, 0.62, up); dy = lerp(0, -400, up)
        out = conceal(t, 5.7, 0.45, (0, -30)) if t >= 5.7 else {}
        r1 = merge(reveal(t, 0.15, 0.55, 30, 20), out)
        layer(c, title_block, r1['a'], r1['blur'], 0, r1['dy']+dy, sc_, (540, 760), (60, 660, 960, 220))
        rule_u = seg(t, 0.5, 0.5, in_out_cubic)
        r2 = merge(dict(a=1 if rule_u > 0 else 0), out)
        layer(c, lambda k: title_rule(k, rule_u), r2['a'], r2['blur'], 0, r2['dy']+dy, sc_, (540, 760), (300, 820, 480, 60))
        r3 = merge(reveal(t, 0.7, 0.45, 18, 12), out)
        layer(c, title_sub, r3['a'], r3['blur'], 0, r3['dy']+dy, sc_, (540, 760), (160, 870, 760, 80))

    # --- cartes chiffres : entrée en cascade, puis mise au point sur la première qui devient « Dividende »
    if 2.9 <= t < 10.2:
        for i, (big, small) in enumerate(CARDS):
            y = 590+i*210
            if i == 0:
                mv = seg(t, 5.65, 0.65, in_out_cubic)
                yy = lerp(y, 470, mv); xw = lerp(780, 640, mv)
                old_out = seg(t, 5.6, 0.22, in_cubic); new_in = seg(t, 5.95, 0.4, out_quint)
                def d0(k, yy=yy, xw=xw, old_out=old_out, new_in=new_in):
                    card(k, 540-xw/2, yy, xw, 160, 30)
                    if old_out < 1:
                        k.push_group(); txt(k, big, 540-xw/2+56, yy+80-12*old_out, 64, TEAL, 'bold', 'l')
                        txt(k, small, 540+xw/2-56, yy+82-12*old_out, 30, SOFT, 'medium', 'r'); k.pop_group_to_source(); k.paint_with_alpha(1-old_out)
                    if new_in > 0:
                        k.push_group(); txt(k, "Dividende par action", 540, yy+80+14*(1-new_in), 42, INK, 'bold', 'c')
                        k.pop_group_to_source(); k.paint_with_alpha(new_in)
                rv = reveal(t, 3.0, 0.45, 30, 16)
                out = conceal(t, 9.4, 0.4, (0, -30)) if t >= 9.4 else {}
                r = merge(rv, out)
                layer(c, d0, r['a'], r['blur'], r['dx'], r['dy'], 1, (540, 960), (100, 400, 880, 420))
            else:
                rv = reveal(t, 3.0+i*0.14, 0.45, 30, 16)
                foc = seg(t, 5.6, 0.5, in_out_cubic)          # mise au point qui s'en va
                gone = conceal(t, 5.85+i*0.06, 0.45, (40, 0), 14) if t >= 5.85 else {}
                r = merge(rv, dict(a=1-0.6*foc, blur=8*foc), gone)
                def di(k, y=y, big=big, small=small):
                    card(k, 150, y, 780, 160, 30)
                    txt(k, big, 206, y+80, 64, TEAL, 'bold', 'l'); txt(k, small, 874, y+82, 30, SOFT, 'medium', 'r')
                layer(c, di, r['a'], r['blur'], r['dx'], r['dy'], 1, (540, 960), (100, y-40, 880, 260))

    # --- barres de dividende : conteneurs vides, puis remplissage un par un
    if 6.0 <= t < 10.3:
        base, top = 1180, 720; hmax = base-top
        out = conceal(t, 9.45, 0.4, (0, 30), 14) if t >= 9.45 else {}
        for i, (yr, v) in enumerate(DIVS):
            cx = 230+i*155
            ghost = reveal(t, 6.1+i*0.07, 0.4, 20, 10)
            fill = seg(t, 6.75+i*0.24, 0.55, out_quint)
            h = hmax*(v/3.9)*fill; last = i == 4
            def bar(k, cx=cx, h=h, last=last, yr=yr):
                rr(k, cx-50, top, 100, hmax, 22); src(k, hx('E9E5DD')); k.fill()
                rr(k, cx-50, top, 100, hmax, 22); src(k, LINE); k.set_line_width(1.5); k.stroke()
                if h > 2:
                    if last: paint_soft(k, cx-56, base-h-6, 112, h+12, 26, 20, GOLD, 0.45)
                    g = cairo.LinearGradient(0, base-h, 0, base)
                    c1, c2 = (GOLD, GOLD_D) if last else (TEAL_L, TEAL_D)
                    g.add_color_stop_rgba(0, *c1[:3], 1); g.add_color_stop_rgba(1, *c2[:3], 1)
                    rr(k, cx-50, base-h, 100, h, 22); k.set_source(g); k.fill()
                    rr(k, cx-48, base-h+3, 96, 10, 5); src(k, WHITE, 0.35); k.fill()
                txt(k, yr, cx, base+38, 26, SOFT, 'medium')
            r = merge(ghost, out)
            layer(c, bar, r['a'], r['blur'], r['dx'], r['dy'], 1, (540, 960), (cx-90, top-40, 180, hmax+120))
            lab = merge(reveal(t, 7.1+i*0.24, 0.35, 14, 8), out)
            vh = hmax*(v/3.9)
            layer(c, lambda k, cx=cx, v=v, vh=vh: txt(k, f"{v:.2f} €".replace('.', ','), cx, base-vh-34, 30, INK),
                  lab['a'], lab['blur'], lab['dx'], lab['dy'], 1, (540, 960), (cx-90, base-vh-70, 180, 70))
        # ligne de référence pointillée, tracée de gauche à droite
        lu = seg(t, 8.35, 0.6, in_out_cubic)
        if lu > 0:
            y_ref = base-hmax*(2.90/3.9)
            def refl(k):
                k.set_dash([10, 9]); k.move_to(180, y_ref); k.line_to(180+(880-180)*lu, y_ref)
                src(k, SOFT, 0.8); k.set_line_width(2.5); k.stroke(); k.set_dash([])
            r = merge(dict(a=1), out); layer(c, refl, r['a'], r['blur'], r['dx'], r['dy'])
        pr = merge(reveal(t, 8.85, 0.45, 16, 12), out)
        def pill(k):
            w = tw(k, "+28 % en 4 ans", 32)+56; paint_soft(k, 540-w/2, 610, w, 66, 33, 16, TEAL, 0.35)
            rr(k, 540-w/2, 610, w, 66, 33); src(k, TEAL); k.fill(); txt(k, "+28 % en 4 ans", 540, 643, 32, WHITE)
        layer(c, pill, pr['a'], pr['blur'], pr['dx'], pr['dy'], 1, (540, 960), (200, 560, 680, 160))

    # --- anneau segmenté : 10 actions, remplies une à une, puis la 11e offerte
    if 9.7 <= t < 13.7:
        foc = seg(t, 13.0, 0.5, in_out_cubic)
        gr = merge(reveal(t, 9.72, 0.5, 20, 14), dict(a=1-0.75*foc, blur=10*foc))
        cx, cy = RING_C
        def ring(k):
            for i in range(10):
                a0 = -math.pi/2+i*2*math.pi/10+0.045; a1 = a0+2*math.pi/10-0.09
                k.new_path(); k.arc(cx, cy, RING_R, a0, a1); k.set_line_width(RING_T); k.set_line_cap(cairo.LINE_CAP_BUTT)
                src(k, hx('E3DED4')); k.stroke()
                f = seg(t, 10.35+i*0.11, 0.22, out_quint)
                if f > 0:
                    col = tuple(lerp(TEAL_L[j], TEAL_D[j], i/9) for j in range(3))+(1,)
                    k.new_path(); k.arc(cx, cy, RING_R, a0, a0+(a1-a0)*f); src(k, col); k.stroke()
            txt(k, "10", cx, cy-24, 110, INK); txt(k, "ACTIONS", cx, cy+58, 24, SOFT, 'medium', 'c', 1, track=5)
        layer(c, ring, gr['a'], gr['blur'], 0, gr['dy'], 1, (540, 960), (250, 510, 580, 580))
        # la pièce offerte : apparition par échelle douce + halo, sans rebond
        g = seg(t, 11.6, 0.5, out_expo)
        if g > 0:
            gx, gy = cx+RING_R*0.78, cy-RING_R*0.78
            def gift(k):
                paint_soft(k, gx-70, gy-70, 140, 140, 70, 24, GOLD, 0.6)
                k.arc(gx, gy, 58, 0, 2*math.pi); rg = cairo.RadialGradient(gx-18, gy-18, 5, gx, gy, 60)
                rg.add_color_stop_rgba(0, 1, 0.86, 0.35, 1); rg.add_color_stop_rgba(1, *GOLD_D[:3], 1); k.set_source(rg); k.fill()
                k.arc(gx, gy, 44, 0, 2*math.pi); src(k, hx('FFFFFF'), 0.35); k.set_line_width(3); k.stroke()
                txt(k, "+1", gx, gy, 46, WHITE)
            r = merge(dict(a=clamp((t-11.6)/0.2), blur=12*(1-g)), dict(a=1-0.75*foc, blur=10*foc))
            layer(c, gift, r['a'], r['blur'], 0, 0, lerp(0.6, 1.0, g), (gx, gy), (gx-120, gy-120, 240, 240))
        lab = merge(reveal(t, 11.9, 0.45, 16, 10), dict(a=1-0.75*foc, blur=10*foc))
        layer(c, lambda k: txt(k, "1 action offerte pour 10 détenues", 540, 1100, 34, INK, 'medium'),
              lab['a'], lab['blur'], 0, lab['dy'], 1, (540, 960), (120, 1060, 840, 90))

    # --- résultat : carte mise en valeur, compteur qui défile
    if t >= 13.1:
        rv = reveal(t, 13.15, 0.55, 30, 18)
        n = seg(t, 13.35, 1.1, out_expo); val = round(lerp(1000, 1735, n))
        hl = seg(t, 14.4, 0.5, in_out_cubic)
        def res(k):
            card(k, 170, 560, 740, 420, 40, highlight=hl)
            txt(k, "1 000 € IL Y A 5 ANS", 540, 650, 24, SOFT, 'medium', 'c', 1, track=5)
            txt(k, f"≈ {val:,} €".replace(',', ' '), 540, 770, 104, TEAL)
            k.move_to(400, 850); k.line_to(680, 850); src(k, LINE); k.set_line_width(2); k.stroke()
            txt(k, "dividendes et actions gratuites compris", 540, 905, 26, SOFT, 'regular')
        layer(c, res, rv['a'], rv['blur'], 0, rv['dy'], 1, (540, 960), (130, 520, 820, 520))
        pv = reveal(t, 14.55, 0.45, 16, 12)
        def pill(k):
            paint_soft(k, 750, 520, 190, 76, 38, 18, CORAL, 0.4)
            rr(k, 750, 520, 190, 76, 38); src(k, CORAL); k.fill(); txt(k, "+73 %", 845, 558, 38, WHITE)
        layer(c, pill, pv['a'], pv['blur'], 0, pv['dy'], 1, (540, 960), (700, 480, 300, 160))

    captions(c, t)
    rr(c, 140, 262, 800, 8, 4); src(c, LINE); c.fill(); rr(c, 140, 262, max(8, 800*t/DUR), 8, 4); src(c, INK); c.fill()
    txt(c, "Scène test · Contenu pédagogique, pas un conseil en investissement", 540, 1458, 19, SOFT, 'regular')

# fenêtres de déplacement rapide : flou de mouvement par sur-échantillonnage
MB = [(2.55, 3.4), (5.55, 6.4), (9.35, 10.3), (12.95, 13.6)]
def render(t, surf, ctx, n=5):
    if not any(a <= t < b for a, b in MB):
        scene(ctx, t); surf.flush(); return np.ndarray((H, W, 4), np.uint8, surf.get_data()).copy()
    acc = np.zeros((H, W, 4), np.float32)
    for k in range(n):
        scene(ctx, t+(k/n-0.5)*(0.5/FPS)); surf.flush()
        acc += np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return (acc/n).astype(np.uint8)

EVENTS = [(0.15, 'shimmer'), (0.5, 'line'), (2.6, 'whoosh'), (3.0, 'click'), (3.14, 'click'), (3.28, 'click'),
          (5.6, 'whoosh'), (6.1, 'tick'), (6.17, 'tick'), (6.24, 'tick'), (6.31, 'tick'), (6.38, 'tick')]
EVENTS += [(6.75+i*0.24, 'fill', i) for i in range(5)] + [(8.35, 'line'), (8.85, 'chime'), (9.6, 'whoosh')]
EVENTS += [(10.35+i*0.11, 'seg', i) for i in range(10)] + [(11.6, 'gift'), (13.0, 'whoosh'), (13.15, 'shimmer')]
EVENTS += [(13.35+k*0.08, 'count', k) for k in range(12)] + [(14.4, 'chime')]

def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]:
            a = render(float(ts), surf, ctx)
            Image.frombuffer('RGBA', (W, H), a.tobytes(), 'raw', 'BGRA', W*4, 1).save(f'/home/claude/v7/prev_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                           '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))):
        ff.stdin.write(render(i/FPS, surf, ctx).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))

if __name__ == '__main__': main()
