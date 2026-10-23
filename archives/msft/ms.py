"""Microsoft : les montagnes russes de 2026. DA verre 3D, aurores, 60 i/s, ~62 s."""
import sys, math, re, subprocess
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/lvmh')
_a = sys.argv; sys.argv = ['x', 'info']
from lvmh import logo_symbol
sys.argv = _a
from ui import hx, col, tw, txt, rr, to_pil, W, H
from glass import aurora, coeffs, tilt_quad, surf, pil, pill, RED, GRN, BLU, YEL
FPS = 60

# ---------- chiffres vérifiés (8 octobre 2026) ----------
FX0, FX1, P0, P1 = 1.1569, 1/0.8927, 282.98, 522.69
SH = 1000*FX0/P0; VAL = SH*P1/FX1; DIV = SH*4*(0.62+0.68+0.75+0.83+0.91)/FX1; TOT = VAL+DIV
assert round(TOT, -1) == 1960

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_expo(x): x = clamp(x); return 1 if x >= 1 else 1-2**(-10*x)
def out_back(x, s=1.3): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def in_out(x): x = clamp(x); return 4*x**3 if x < .5 else 1-(-2*x+2)**3/2
def lerp(a, b, u): return a+(b-a)*u
def seg(t, a, d, f=out_expo): return f((t-a)/d)
def fmt(n): return f"{int(round(n)):,}".replace(',', ' ')

# ---------- script ----------
CAPS = [
 ("c01", "Microsoft a gagné [450 milliards] en UNE journée."),
 ("c02", "Le plus gros gain en un jour de l'[histoire] de la Bourse."),
 ("c03", "Et 1 000 € investis il y a 5 ans ? Réponse à la [fin]."),
 ("c04", "[1975] : Bill Gates et Paul Allen fondent Microsoft."),
 ("c05", "[1981] : IBM leur confie le système de son PC. MS-DOS."),
 ("c06", "Puis Windows s'installe sur [presque tous les PC]."),
 ("c07", "[2014] : Satya Nadella prend les commandes. Cap sur le cloud."),
 ("c08", "Azure dépasse aujourd'hui [100 milliards] de dollars par an."),
 ("c09", "Et Microsoft mise sur l'IA : [27 %] d'OpenAI."),
 ("c10", "Mais début 2026, les investisseurs [doutent]."),
 ("c11", "Des milliards dépensés, un Copilot qui peine à [convaincre]."),
 ("c12", "Résultat : [−35 %] entre le record et juin 2026."),
 ("c13", "30 juillet : Azure +43 %. L'action bondit de [15 %]."),
 ("c14", "[450 milliards] gagnés en une séance. Du jamais vu."),
 ("c15", "Sur l'exercice 2026 : [134 milliards] de bénéfice."),
 ("c16", "Mais [116 milliards] investis en un an, surtout dans l'IA."),
 ("c17", "Tes 1 000 € ? ≈ [1 960 €]. ×2 en 5 ans."),
 ("c18", "Et toi : tu achètes, tu vends ou tu [attends] ?"),
 ("c19", "Abonne-toi, like, partage."),
]
def build():
    tl, t = {}, 0.0
    for cid, s in CAPS:
        clean = s.replace('[', '').replace(']', '')
        d = max(2.1, len(clean)/20+0.55)
        if cid in ('c01', 'c12', 'c14', 'c17'): d += 0.5
        if cid == 'c18': d += 0.5
        if cid == 'c19': d = 3.2
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.12
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def E(c): return TL[c][0]+TL[c][1]
NB = '\u00a0'
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' $'): s = s.replace(a_, NB+a_[1:])
    s = s.replace('≈ ', '≈'+NB)
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def kcolor(cid): return RED if cid in ('c10', 'c11', 'c12') else (GRN if cid in ('c13', 'c14', 'c17') else BLU)
def draw_caption(c, t):
    size = 48
    for cid, s in CAPS:
        a, d = TL[cid]; b = a+d
        if not (a <= t < b): continue
        items = parse(s); sp = tw(c, ' ', "Poppins", size, True)
        wd = [tw(c, w, "Poppins", size, True)+(28 if k else 0) for w, k in items]
        lines, cur, cw = [], [], 0
        for i, w in enumerate(wd):
            need = w+(sp if cur else 0)
            if cur and cw+need > 760: lines.append((cur, cw)); cur, cw = [], 0; need = w
            cur.append(i); cw += need
        lines.append((cur, cw)); y0 = 1352-(len(lines)-1)*37; fo = 1-seg(t, b-0.15, 0.15, lambda x: clamp(x)**3); n_ = 0
        for li, (idx, lw) in enumerate(lines):
            x = 540-lw/2; y = y0+li*74
            for i in idx:
                w, k = items[i]; ti = a+n_*0.035; n_ += 1
                u = seg(t, ti, 0.25); al = clamp((t-ti)/0.12)*fo
                if al > 0:
                    yy = y+12*(1-u); sc = lerp(1.25, 1, out_back(clamp((t-ti)/0.25))) if k else 1
                    c.save(); c.translate(x+wd[i]/2, yy); c.scale(sc, sc); c.translate(-(x+wd[i]/2), -yy)
                    if k:
                        rr(c, x, yy-34, wd[i], 66, 33); g = cairo.LinearGradient(x, 0, x+wd[i], 0)
                        g.add_color_stop_rgba(0, *hx(kcolor(cid), al)); g.add_color_stop_rgba(1, *hx(kcolor(cid), .78*al)); c.set_source(g); c.fill()
                        txt(c, w, x+14, yy, "Poppins", size, 'FFFFFF', True, 'l', al)
                    else:
                        txt(c, w, x+2, yy+3, "Poppins", size, '000000', True, 'l', .5*al); txt(c, w, x, yy, "Poppins", size, 'FFFFFF', True, 'l', al)
                    c.restore()
                x += wd[i]+sp

# ---------- fonds : trois ambiances fondues ----------
BGS = {}
def backgrounds():
    if not BGS:
        BGS['blue'] = aurora([(250, 600, 800, '00A4EF', .55), (900, 1100, 700, '2D7BFF', .35), (600, 1650, 700, '5B3BFF', .35), (950, 350, 500, '00A4EF', .25)])
        BGS['red'] = aurora([(540, 700, 800, 'F25022', .45), (150, 1300, 600, '8A0F2A', .45), (950, 400, 500, 'FF7A3D', .2)], base=('050203', '120407'))
        BGS['green'] = aurora([(300, 600, 800, '00A4EF', .45), (850, 1000, 750, '7FBA00', .38), (600, 1650, 700, '5B3BFF', .3)])
    return BGS
def mood(t):
    """poids (bleu, rouge, vert)"""
    r = seg(t, T('c10')-0.2, 0.8, in_out)*(1-seg(t, T('c13'), 0.6, in_out))
    g = seg(t, T('c13'), 0.6, in_out)*(1-seg(t, T('c15'), 0.8, in_out)) + seg(t, T('c17'), 0.6, in_out)*(1-seg(t, T('c18'), 0.6, in_out))
    return r, g
def base_canvas(t):
    B = backgrounds(); r, g = mood(t)
    im = B['blue']
    if r > 0.002: im = Image.blend(im, B['red'], r)
    if g > 0.002: im = Image.blend(im, B['green'], g)
    return im.copy()

# ---------- composition rapide (flous à basse résolution) ----------
def lowblur(im, radius, f=4):
    w, h = im.size; return im.resize((w//f, h//f), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius/f)).resize((w, h), Image.BILINEAR)
def with_alpha(img, a):
    if a >= 0.999: return img
    im = img.copy(); im.putalpha(im.split()[3].point(lambda v: int(v*a))); return im
def place(cv, panel, quad, a=1.0, frost=24, shadow=0.5, dof=0.0):
    if a <= 0.01: return
    w, h = panel.size; cf = coeffs(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    warped = with_alpha(panel, a).transform((W, H), Image.PERSPECTIVE, cf, Image.BILINEAR)
    m = warped.split()[3].point(lambda v: 255 if v > 6 else 0)
    if shadow > 0:
        sh = lowblur(m.convert('RGBA'), 40).split()[0]; sh = ImageChops.offset(sh, 0, 30).point(lambda v: int(v*shadow*a))
        cv.paste((0, 0, 10, 255), (0, 0), sh)
    if frost > 0:
        mm = m.point(lambda v: int(v*a))
        cv.paste(lowblur(cv, frost), (0, 0), mm)
    if dof > 0: warped = lowblur(warped, dof, 2)
    cv.alpha_composite(warped)
def glass(w, h, draw=None, r=36, ta=0.12, edge=0.6):
    s, c = surf(w, h)
    rr(c, 1, 1, w-2, h-2, r); g = cairo.LinearGradient(0, 0, w*.6, h); g.add_color_stop_rgba(0, 1, 1, 1, ta*1.8); g.add_color_stop_rgba(1, 1, 1, 1, ta*.6); c.set_source(g); c.fill()
    c.save(); rr(c, 1, 1, w-2, h-2, r); c.clip(); g2 = cairo.LinearGradient(0, 0, w, h*.7)
    for o, v in ((0, 0), (.32, 0), (.38, .10), (.46, 0)): g2.add_color_stop_rgba(o, 1, 1, 1, v)
    c.set_source(g2); c.paint(); c.restore()
    rr(c, 1.5, 1.5, w-3, h-3, r); g3 = cairo.LinearGradient(0, 0, w, h)
    for o, v in ((0, edge), (.5, edge*.25), (1, edge*.6)): g3.add_color_stop_rgba(o, 1, 1, 1, v)
    c.set_source(g3); c.set_line_width(2.2); c.stroke()
    if draw: draw(c, w, h)
    return pil(s)
_GT = {}
def glow_text(cv, s, x, y, size, top='FFFFFF', bottom='A8E2FF', glow='00A4EF', ga=0.85, a=1.0, scale=1.0, reflect=True, track=-4):
    if a <= 0.01: return
    key = (s, size, top, bottom, glow, reflect)
    if key not in _GT:
        pad = int(size*0.6); w = int(tw(cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)), s, "Poppins", size, True, track))+2*pad; h = int(size*2.2)
        S, c = surf(w, h); c.select_font_face("Poppins", 0, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
        asc, desc = c.font_extents()[:2]; cy = h*0.38; yy = cy+(asc-desc)/2*0.8; xx = pad; c.new_path()
        for ch in s: c.move_to(xx, yy); c.text_path(ch); xx += c.text_extents(ch).x_advance+track
        g = cairo.LinearGradient(0, cy-size*.45, 0, cy+size*.4); g.add_color_stop_rgb(0, *hx(top)[:3]); g.add_color_stop_rgb(1, *hx(bottom)[:3]); c.set_source(g); c.fill()
        im = pil(S); al = im.split()[3]
        gl = Image.new('RGBA', im.size, tuple(int(v*255) for v in hx(glow)[:3])+(0,)); gl.putalpha(lowblur(al.convert('RGBA'), size*.2, 2).split()[0].point(lambda v: int(v*ga)))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(gl)
        if reflect:
            top_ = int(yy-asc*0.78); bot = int(yy+desc*0.3); band = im.crop((0, top_, w, bot)).transpose(Image.FLIP_TOP_BOTTOM)
            grad = np.linspace(0.16, 0, band.size[1])[:, None]; aa = (np.asarray(band.split()[3]).astype(float)*grad).astype(np.uint8)
            band.putalpha(Image.fromarray(aa)); out.alpha_composite(band.filter(ImageFilter.GaussianBlur(3)), (0, min(h-band.size[1], bot+6)))
        out.alpha_composite(im); _GT[key] = (out, cy)
    img, cy = _GT[key]
    if scale != 1.0: img = img.resize((int(img.width*scale), int(img.height*scale)), Image.BILINEAR); cy *= scale
    img = with_alpha(img, a); cv.alpha_composite(img, (int(x-img.width/2), int(y-cy)))

# ---------- éléments d'interface ----------
def mini_chart(c, w, h, pts, color=BLU, lw=6, u=1.0, dots=()):
    vmin = min(v for _, v in pts); vmax = max(v for _, v in pts)
    X = lambda q: 40+q*(w-80); Y = lambda v: h-50-(v-vmin)/(vmax-vmin)*(h-120)
    n = 120; us = [pts[0][0]+(pts[-1][0]-pts[0][0])*u*i/n for i in range(n+1)]
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts]); vals = np.interp(us, xs, ys)
    P = [(X(q), Y(v)) for q, v in zip(us, vals)]
    c.new_path(); c.move_to(P[0][0], h-40); [c.line_to(*p) for p in P]; c.line_to(P[-1][0], h-40); c.close_path()
    g = cairo.LinearGradient(0, 60, 0, h); g.add_color_stop_rgba(0, *hx(color, .32)); g.add_color_stop_rgba(1, *hx(color, 0)); c.set_source(g); c.fill()
    for k_, a_, w_ in ((1, .08, lw+22), (1, .16, lw+12), (1, 1, lw)):
        c.new_path(); c.move_to(*P[0]); [c.line_to(*p) for p in P[1:]]; col(c, color, a_); c.set_line_width(w_)
        c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    for q, v, cl in dots:
        if q <= pts[0][0]+(pts[-1][0]-pts[0][0])*u+1e-6:
            c.new_path(); c.arc(X(q), Y(v), 11, 0, 2*math.pi); col(c, cl); c.fill()
    return X, Y
import functools
@functools.lru_cache(maxsize=64)
def chip(text, color, w=None):
    k = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); w = w or int(tw(k, text, "JetBrains Mono", 26, True, 1)+100)
    return glass(w, 96, lambda c, w_, h: (c.new_path(), c.arc(40, h/2, 10, 0, 2*math.pi), col(c, color), c.fill(),
                                           txt(c, text, 64, h/2, "JetBrains Mono", 26, 'FFFFFF', True, 'l', 1, 1)), r=48, ta=.14)
def enter(t, t0, d=0.55, side=1, ry0=0.0, rx0=0.0):
    u = seg(t, t0, d); return u, ry0+side*0.9*(1-u), rx0, clamp((t-t0)/(d*0.5))
CURVE5 = [(0, 283), (.08, 336), (.22, 214), (.4, 330), (.55, 420), (.66, 470), (.72, 537.65), (.8, 505), (.86, 400), (.9, 349.2), (.92, 405), (.96, 500), (1, 522.69)]

# ---------- scènes (PIL canvas cv + calque cairo ov) ----------
def scene_hook(cv, c, t):
    t0, t1, t2 = T('c01'), T('c02'), T('c03'); ex = 1-seg(t, T('c04')-0.2, 0.2, lambda x: clamp(x))
    if t < t2:
        u, ry, rx, a = enter(t, t0+0.15, 0.6, 1, 0.55, -0.12)
        p1 = glass(520, 340, lambda k, w, h: (txt(k, "MSFT", 36, 50, "JetBrains Mono", 22, 'BFE6FF', False, 'l', 1, 3),
                                             mini_chart(k, w, h, [(0, 349), (.3, 360), (.55, 420), (.7, 470), (.85, 505), (1, 513)], GRN, 6, seg(t, t0+0.3, 1.2))))
        place(cv, p1, tilt_quad(290+40*math.sin(t*.6), 560, 520, 340, ry=ry, rx=rx), a*ex, 18, .5, 2.0)
        u2, ry2, rx2, a2 = enter(t, t0+0.3, 0.6, -1, -0.55, -0.1)
        p2 = glass(460, 250, lambda k, w, h: (txt(k, "30 JUILLET 2026", w/2, 80, "JetBrains Mono", 24, 'FFFFFF', False, 'c', 1, 3), txt(k, "+15,5 %", w/2, 165, "Poppins", 64, 'BDF56A', True)))
        place(cv, p2, tilt_quad(800-30*math.sin(t*.6), 500, 460, 250, ry=ry2, rx=rx2), a2*ex, 18, .5, 2.0)
        v = 450*out_expo(clamp((t-t0)/0.9)); sc = lerp(1.25, 1, out_back(clamp((t-t0)/0.5)))
        glow_text(cv, f"+{int(round(v))}", 540, 820, 300, a=clamp(t/0.15)*ex, scale=sc)
        pill(c, "MILLIARDS DE DOLLARS · EN 1 JOUR", 540, 1100, 'FFFFFF', 22) if t > t0+0.5 else None
        if t >= t1:
            # comparaison avec l'ancien record
            for i, (lab, val, cl) in enumerate((("MICROSOFT · JUIL. 2026", 450, GRN), ("NVIDIA · AVR. 2025", 441, 'FFFFFF'))):
                g = seg(t, t1+0.2+i*0.15, 0.6)
                y = 1165+i*48; txt(c, lab, 170, y, "JetBrains Mono", 20, cl, False, 'l', g, 1)
                rr(c, 470, y-10, 380*val/450*g, 20, 10); col(c, cl, .9 if i == 0 else .45); c.fill()
                txt(c, f"{val} Md$", 470+380*val/450*g+12, y, "JetBrains Mono", 20, cl, True, 'l', g)
    else:
        # 1 000 € ? panneau de chargement
        u, ry, rx, a = enter(t, t2, 0.5, 1, 0.0, 0.0)
        def b(k, w, h):
            txt(k, "1 000 € · IL Y A 5 ANS", w/2, 80, "JetBrains Mono", 26, 'BFE6FF', False, 'c', 1, 3)
            txt(k, "? ? ? €", w/2, 220, "Poppins", 130, 'FFFFFF', True)
            p = seg(t, t2+0.3, 2.2, in_out)*0.85; rr(k, 60, h-90, w-120, 22, 11); col(k, 'FFFFFF', .15); k.fill(); rr(k, 60, h-90, max(22, (w-120)*p), 22, 11); col(k, BLU); k.fill()
            txt(k, f"calcul en cours… {int(p*100)} %", w/2, h-130, "JetBrains Mono", 22, 'FFFFFF', False, 'c', .8)
        place(cv, glass(760, 470, b), tilt_quad(540, 720, 760, 470, ry=ry*0.6, rx=0.08), a*ex, 24)
def scene_history(cv, c, t):
    t4, t5, t6 = T('c04'), T('c05'), T('c06'); ex = 1-seg(t, T('c07')-0.2, 0.2, lambda x: clamp(x))
    if t < t5:
        sc = lerp(1.3, 1, out_back(clamp((t-t4)/0.4)))
        glow_text(cv, "1975", 540, 600, 260, a=clamp((t-t4)/0.15), scale=sc)
        u, ry, rx, a = enter(t, t4+0.4, 0.5, 1)
        place(cv, glass(700, 220, lambda k, w, h: (txt(k, "BILL GATES · PAUL ALLEN", w/2, 80, "JetBrains Mono", 28, 'FFFFFF', True, 'c', 1, 2),
                                                   txt(k, "Albuquerque, Nouveau-Mexique", w/2, 150, "Poppins", 30, 'BFE6FF'))),
              tilt_quad(540, 930, 700, 220, ry=ry*0.5, rx=0.1), a, 20)
    elif t < t6:
        glow_text(cv, "1981", 540, 470, 200, a=clamp((t-t5)/0.15), scale=lerp(1.3, 1, out_back(clamp((t-t5)/0.4))))
        u, ry, rx, a = enter(t, t5+0.2, 0.5, -1)
        def term(k, w, h):
            rr(k, 30, 30, w-60, h-60, 18); col(k, '000000', .55); k.fill()
            lines = ["IBM Personal Computer", "MS-DOS Version 1.0", "", "C:\\> "]
            n = int(clamp((t-t5-0.5)/1.2)*sum(len(l) for l in lines)); shown = 0
            for i, l in enumerate(lines):
                s_ = l[:max(0, min(len(l), n-shown))]; shown += len(l)
                txt(k, s_, 70, 90+i*60, "JetBrains Mono", 34, '9FFFA0', True, 'l')
            if int(t*2.5) % 2 == 0: col(k, '9FFFA0'); k.rectangle(70+tw(k, "C:\\> ", "JetBrains Mono", 34, True), 90+3*60-20, 20, 40); k.fill()
        place(cv, glass(780, 380, term), tilt_quad(540, 830, 780, 380, ry=ry*0.6, rx=0.12), a*ex if t > t6-0.3 else a, 22)
    else:
        u, ry, rx, a = enter(t, t6, 0.5, 1)
        def screens(k, w, h):
            n = 10
            for i in range(n):
                x = 50+(i % 5)*((w-100)/5); y = 70+(i//5)*170; lit = clamp((t-t6-0.3-i*0.08)/0.2)*(1 if i < 9 else 0)
                rr(k, x+8, y, (w-100)/5-16, 110, 10); col(k, 'FFFFFF', .08+.0); k.fill()
                if lit > 0: rr(k, x+8, y, (w-100)/5-16, 110, 10); col(k, BLU, .75*lit); k.fill()
                rr(k, x+8.5, y+.5, (w-100)/5-17, 109, 10); col(k, 'FFFFFF', .5); k.set_line_width(1.5); k.stroke()
                col(k, 'FFFFFF', .4); k.rectangle(x+(w-100)/10-12, y+116, 24, 14); k.fill()
            txt(k, "WINDOWS · PRESQUE PARTOUT", w/2, h-50, "JetBrains Mono", 24, 'FFFFFF', False, 'c', 1, 3)
        place(cv, glass(820, 480, screens), tilt_quad(540, 760, 820, 480, ry=ry*0.6, rx=0.08), a*ex, 22)
def scene_cloud(cv, c, t):
    t7, t8, t9 = T('c07'), T('c08'), T('c09'); ex = 1-seg(t, T('c10')-0.2, 0.2, lambda x: clamp(x))
    if t < t8:
        glow_text(cv, "2014", 540, 470, 200, a=clamp((t-t7)/0.15), scale=lerp(1.3, 1, out_back(clamp((t-t7)/0.4))))
        u, ry, rx, a = enter(t, t7+0.3, 0.5, 1)
        def cloud(k, w, h):
            txt(k, "SATYA NADELLA · PDG", w/2, 70, "JetBrains Mono", 26, 'FFFFFF', True, 'c', 1, 2)
            d = seg(t, t7+0.8, 1.2, in_out)
            k.save(); k.translate(w/2, 250); k.scale(1.6, 1.6)
            k.new_path(); k.move_to(-90, 40); k.curve_to(-140, 40, -140, -20, -90, -20); k.curve_to(-80, -70, -10, -80, 10, -40)
            k.curve_to(40, -80, 110, -60, 100, -10); k.curve_to(150, -10, 150, 40, 100, 40); k.close_path()
            p = k.copy_path_flat(); k.new_path()
            pts = [(q[1][0], q[1][1]) for q in p if q[0] in (0, 1)]; n = max(2, int(len(pts)*d))
            k.move_to(*pts[0]); [k.line_to(*q) for q in pts[1:n]]
            for w_, a_ in ((16, .12), (9, .25), (4, 1)): col(k, BLU, a_); k.set_line_width(w_); k.stroke_preserve()
            k.new_path(); k.restore()
            txt(k, "CLOUD", w/2, h-70, "JetBrains Mono", 30, 'BFE6FF', False, 'c', 1, 8)
        place(cv, glass(700, 470, cloud), tilt_quad(540, 860, 700, 470, ry=ry*0.6, rx=0.1), a*(ex if t > t8-0.3 else 1), 22)
    elif t < t9:
        v = 100*out_expo(clamp((t-t8)/0.8))
        glow_text(cv, f"{int(round(v))} Md$", 540, 640, 165, a=clamp((t-t8)/0.12), scale=lerp(1.2, 1, out_back(clamp((t-t8)/0.4))))
        pill(c, "AZURE · PAR AN", 540, 400, 'FFFFFF', 24)
        u, ry, rx, a = enter(t, t8+0.5, 0.5, -1)
        place(cv, chip("+43 % SUR UN AN", GRN), tilt_quad(540, 960, 380, 96, ry=ry*0.5), a, 14, .4)
    else:
        u, ry, rx, a = enter(t, t9, 0.5, 1)
        f = seg(t, t9+0.3, 1.0, in_out)*0.27
        def donut(k, w, h):
            cx, cy, r = w/2, h/2+10, 190
            k.new_path(); k.arc(cx, cy, r, 0, 2*math.pi); col(k, 'FFFFFF', .12); k.set_line_width(46); k.stroke()
            for w_, a_ in ((70, .12), (46, 1)):
                k.new_path(); k.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*f); col(k, BLU, a_); k.set_line_width(w_); k.stroke()
            txt(k, f"{round(f*100)} %", cx, cy-20, "Poppins", 110, 'FFFFFF', True); txt(k, "D'OPENAI", cx, cy+70, "JetBrains Mono", 26, 'BFE6FF', False, 'c', 1, 4)
        place(cv, glass(620, 560, donut), tilt_quad(540, 760, 620, 560, ry=ry*0.6, rx=0.06), a*ex, 22)
def scene_doubt(cv, c, t):
    t10, t11, t12 = T('c10'), T('c11'), T('c12'); ex = 1-seg(t, T('c13')-0.2, 0.2, lambda x: clamp(x))
    if t < t12:
        # le graphique bascule, les puces de doute apparaissent
        u, ry, rx, a = enter(t, t10, 0.6, 1, 0.0, 0.5)
        place(cv, glass(760, 460, lambda k, w, h: (txt(k, "MSFT · 2026", 40, 50, "JetBrains Mono", 22, 'FFD2C8', False, 'l', 1, 3),
              mini_chart(k, w, h, [(0, 537), (.15, 520), (.3, 470), (.45, 430), (.6, 400), (.75, 372), (.88, 360), (1, 349)], RED, 6, seg(t, t10+0.3, 2.6, in_out)))),
              tilt_quad(540, 640, 760, 460, ry=ry*0.3, rx=0.45), a, 22, .5, 2.5 if t >= t11 else 0)
        if t >= t11:
            for i, (s_, cl) in enumerate((("DÉPENSES IA EN HAUSSE", RED), ("COPILOT PEINE À PAYER", YEL), ("DÉPARTS DE DIRIGEANTS", RED))):
                u2, ry2, rx2, a2 = enter(t, t11+0.15+i*0.25, 0.45, -1 if i % 2 else 1)
                x = 540+(-40 if i % 2 else 40); place(cv, chip(s_, cl, 620), tilt_quad(x, 880+i*120, 620, 96, ry=ry2*0.6), a2*ex, 14, .4)
    else:
        place(cv, glass(760, 460, lambda k, w, h: mini_chart(k, w, h, [(0, 537), (.3, 470), (.6, 400), (1, 349)], RED, 6)),
              tilt_quad(540, 620, 760, 460, rx=0.5), 0.55*ex, 22, .4, 3.5)
        sc = lerp(1.5, 1, out_back(clamp((t-t12-0.2)/0.35)))
        glow_text(cv, "−35 %", 540, 900, 250, top='FFFFFF', bottom='FF9A80', glow='F25022', ga=1.0, a=clamp((t-t12-0.2)/0.1)*ex, scale=sc)
        if t > t12+0.6: pill(c, "537 $ EN OCT. 2025 · 349 $ EN JUIN 2026", 540, 1160, 'FFFFFF', 20)
def scene_rebound(cv, c, t):
    t13, t14 = T('c13'), T('c14'); ex = 1-seg(t, T('c15')-0.2, 0.2, lambda x: clamp(x))
    if t < t14:
        u, ry, rx, a = enter(t, t13, 0.6, -1, -0.45, 0.08)
        prog = lerp(0.86, 1.0, seg(t, t13+0.3, 1.8, in_out))
        def body(k, w, h):
            txt(k, "MSFT · 5 ANS", 44, 54, "JetBrains Mono", 24, 'BFE6FF', False, 'l', 1, 3)
            sub = [p for p in CURVE5]
            mini_chart(k, w, h, sub, BLU, 7, prog, dots=((.9, 349.2, RED), (.96, 500, GRN)))
        place(cv, glass(760, 560, body), tilt_quad(540, 700, 760, 560, ry=ry, rx=rx), a, 24)
        if t > t13+1.2:
            u2, ry2, rx2, a2 = enter(t, t13+1.2, 0.45, -1, -0.45)
            place(cv, chip("+15 % EN 1 JOUR", GRN), tilt_quad(760, 1080, 380, 96, ry=ry2), a2, 14, .4)
            u3, ry3, rx3, a3 = enter(t, t13+0.6, 0.45, 1, 0.45)
            place(cv, chip("349 $ · JUIN", RED), tilt_quad(330, 1080, 300, 96, ry=ry3), a3, 14, .4)
    else:
        sc = lerp(1.4, 1, out_back(clamp((t-t14)/0.4)))
        glow_text(cv, "+450 Md$", 540, 760, 150, top='FFFFFF', bottom='D9F7A8', glow='7FBA00', ga=.95, a=clamp((t-t14)/0.1)*ex, scale=sc)
        if t > t14+0.4:
            pill(c, "RECORD MONDIAL · ANCIEN : NVIDIA 441 MD$", 540, 1010, 'FFFFFF', 20)
            pill(c, "CAPITALISATION : 3 350 MD$", 540, 1080, 'FFFFFF', 20)
def scene_money(cv, c, t):
    t15, t16 = T('c15'), T('c16'); ex = 1-seg(t, T('c17')-0.2, 0.2, lambda x: clamp(x))
    if t < t16:
        v = 133.7*out_expo(clamp((t-t15)/0.9))
        glow_text(cv, f"{int(round(v))} Md$", 540, 640, 165, a=clamp((t-t15)/0.12), scale=lerp(1.2, 1, out_back(clamp((t-t15)/0.4))))
        pill(c, "BÉNÉFICE NET · EXERCICE 2026", 540, 400, 'FFFFFF', 22)
        for i, (s_, cl) in enumerate((("CHIFFRE D'AFFAIRES : 332 MD$", BLU), ("CROISSANCE : +18 %", GRN))):
            u, ry, rx, a = enter(t, t15+0.5+i*0.2, 0.45, 1 if i == 0 else -1)
            place(cv, chip(s_, cl, 640), tilt_quad(540, 920+i*120, 640, 96, ry=ry*0.5), a*(ex if t > t16-0.3 else 1), 14, .4)
    else:
        v = 115.9*out_expo(clamp((t-t16)/0.9))
        glow_text(cv, f"{int(round(v))} Md$", 540, 640, 165, top='FFFFFF', bottom='FFE29A', glow='FFB900', ga=.9, a=clamp((t-t16)/0.12)*ex, scale=lerp(1.2, 1, out_back(clamp((t-t16)/0.4))))
        pill(c, "INVESTIS EN 1 AN · DATA CENTERS, IA", 540, 400, 'FFFFFF', 22)
        u, ry, rx, a = enter(t, t16+0.5, 0.45, -1)
        place(cv, chip("SOIT 87 % DU BÉNÉFICE", YEL, 560), tilt_quad(540, 940, 560, 96, ry=ry*0.5), a*ex, 14, .4)
def scene_reveal(cv, c, t):
    t17 = T('c17'); ex = 1-seg(t, T('c18')-0.2, 0.2, lambda x: clamp(x))
    u, ry, rx, a = enter(t, t17, 0.6, 1, 0.0, 0.0)
    v = 1000+(TOT-1000)*out_expo(clamp((t-t17-0.4)/0.9))
    def card(k, w, h):
        txt(k, "1 000 € INVESTIS IL Y A 5 ANS", w/2, 80, "JetBrains Mono", 24, 'BFE6FF', False, 'c', 1, 2)
        txt(k, "AUJOURD'HUI", w/2, 170, "JetBrains Mono", 24, 'FFFFFF', False, 'c', 1, 4)
        s_ = fmt(round(v, -1) if v < TOT-15 else 1960)+" €"; w1 = tw(k, "≈ ", "Poppins", 70, True); w2 = tw(k, s_, "Poppins", 140, True)
        x0 = w/2-(w1+w2)/2; txt(k, "≈", x0, 300, "Poppins", 70, 'FFFFFF', True, 'l'); txt(k, s_, x0+w1, 300, "Poppins", 140, 'FFFFFF', True, 'l')
        txt(k, f"actions ≈ {fmt(VAL)} € · dividendes ≈ {round(DIV)} €", w/2, 430, "Poppins", 26, 'D6E4F5')
        txt(k, "change €/$ inclus · avant impôts et frais", w/2, 480, "Poppins", 22, 'D6E4F5', False, 'c', .8)
    place(cv, glass(800, 560, card), tilt_quad(540, 760, 800, 560, ry=ry*0.5, rx=0.05), a*ex, 26)
    if t > t17+1.35:
        sc = lerp(1.8, 1, out_back(clamp((t-t17-1.35)/0.3)))
        place(cv, glass(220, 110, lambda k, w, h: txt(k, "×2", w/2, h/2, "Poppins", 66, 'FFFFFF', True), r=55, ta=.25),
              tilt_quad(770, 470, 220*sc, 110*sc, ry=-0.3), clamp((t-t17-1.35)/0.1)*ex, 12, .4)
def scene_question(cv, c, t):
    t18 = T('c18'); ex = 1-seg(t, T('c19')-0.2, 0.2, lambda x: clamp(x))
    glow_text(cv, "Et toi ?", 540, 470, 150, a=clamp((t-t18)/0.15)*ex, reflect=False, scale=lerp(1.2, 1, out_back(clamp((t-t18)/0.35))))
    for j, (lab, cl) in enumerate((("J'ACHÈTE", GRN), ("JE VENDS", RED), ("J'ATTENDS", BLU))):
        u, ry, rx, a = enter(t, t18+0.3+j*0.15, 0.45, 1 if j % 2 == 0 else -1)
        b = glass(600, 120, lambda k, w, h, lab=lab, cl=cl: (k.new_path(), k.arc(60, h/2, 14, 0, 2*math.pi), col(k, cl), k.fill(), txt(k, lab, w/2+20, h/2, "Poppins", 50, 'FFFFFF', True)), r=60, ta=.14)
        place(cv, b, tilt_quad(540, 700+j*160, 600, 120, ry=ry*0.5), a*ex, 14, .4)
def scene_cta(cv, c, t):
    t19 = T('c19'); a = clamp((t-t19)/0.3)
    s_ = lerp(0.6, 1, out_back(clamp((t-t19)/0.45)))
    c.save(); c.push_group(); logo_symbol(c, 540, 470, 200*s_); txt(c, "Actions_Benefices", 540, 640, "Poppins", 46, 'FFFFFF', True); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    for j, lab in enumerate(("ABONNE-TOI", "LIKE", "PARTAGE")):
        u, ry, rx, al = enter(t, t19+0.3+j*0.25, 0.45, 1 if j % 2 == 0 else -1)
        place(cv, glass(540, 110, lambda k, w, h, lab=lab: txt(k, lab, w/2, h/2, "Poppins", 46, 'FFFFFF', True), r=55, ta=.15), tilt_quad(540, 780+j*140, 540, 110, ry=ry*0.5), al, 14, .4)
    txt(c, "CONTENU PÉDAGOGIQUE, PAS UN CONSEIL EN INVESTISSEMENT", 540, 1200, "JetBrains Mono", 17, 'D6E4F5', False, 'c', clamp((t-t19-1.2)/0.3), 1)

SCENES = [(0, T('c04'), scene_hook), (T('c04'), T('c07'), scene_history), (T('c07'), T('c10'), scene_cloud), (T('c10'), T('c13'), scene_doubt),
          (T('c13'), T('c15'), scene_rebound), (T('c15'), T('c17'), scene_money), (T('c17'), T('c18'), scene_reveal),
          (T('c18'), T('c19'), scene_question), (T('c19'), DUR+0.1, scene_cta)]
IMPACTS = [T('c01')+0.0, T('c12')+0.2, T('c14')+0.0, T('c17')+1.35]
def frame(t):
    cv = base_canvas(t)
    # dérive de caméra : léger zoom lent
    ov_s, c = surf(W, H)
    for a, b, fn in SCENES:
        if a <= t < b: fn(cv, c, t)
    r, g = mood(t)
    pc = RED if r > .5 else (GRN if g > .5 else BLU)
    col(c, 'FFFFFF', .15); rr(c, 140, 260, 800, 6, 3); c.fill(); rr(c, 140, 260, max(6, 800*clamp(t/DUR)), 6, 3); col(c, pc); c.fill()
    if T('c10') <= t < T('c15'): txt(c, "Courbe simplifiée · Pas un conseil en investissement", 540, 1458, "JetBrains Mono", 16, 'D6E4F5', False, 'c', .8)
    draw_caption(c, t)
    for ts in IMPACTS:
        if 0 <= t-ts < 0.22: col(c, 'FFFFFF', 0.18*(1-(t-ts)/0.22)); c.paint()
    if t > DUR-0.35: col(c, '000000', clamp((t-(DUR-0.35))/0.35)); c.paint()
    cv.alpha_composite(to_pil(ov_s))
    # secousse
    dx = dy = 0
    for ts in IMPACTS:
        if 0 <= t-ts < 0.4: e = math.exp(-(t-ts)*11)*14; dx += e*math.sin((t-ts)*90); dy += e*math.cos((t-ts)*70)
    if dx or dy: cv = ImageChops.offset(cv, int(dx), int(dy))
    return cv

def events():
    ev = [(0.0, 'hit'), (0.05, 'count'), (0.15, 'whoosh'), (0.3, 'whoosh'), (T('c02')+0.2, 'click'), (T('c02')+0.35, 'click'),
          (T('c03'), 'whoosh'), (T('c03')+0.3, 'load'), (T('c04'), 'hit'), (T('c04')+0.4, 'whoosh'), (T('c05'), 'hit'), (T('c05')+0.5, 'type'),
          (T('c06'), 'whoosh')] + [(T('c06')+0.3+i*0.08, 'blip', i) for i in range(9)]
    ev += [(T('c07'), 'hit'), (T('c07')+0.3, 'whoosh'), (T('c07')+0.8, 'rise'), (T('c08'), 'count'), (T('c08')+0.05, 'drop'), (T('c08')+0.5, 'pop'),
           (T('c09'), 'whoosh'), (T('c09')+0.3, 'rise')]
    ev += [(T('c10')-0.2, 'tension'), (T('c10'), 'whoosh'), (T('c10')+0.3, 'fall')] + [(T('c11')+0.15+i*0.25, 'error') for i in range(3)]
    ev += [(T('c12')+0.2, 'drop'), (T('c13'), 'whoosh'), (T('c13')+0.3, 'riser'), (T('c13')+1.2, 'pop'), (T('c14'), 'drop'), (T('c14')+0.4, 'click')]
    ev += [(T('c15'), 'count'), (T('c15')+0.05, 'hit'), (T('c15')+0.5, 'pop'), (T('c15')+0.7, 'pop'), (T('c16'), 'count'), (T('c16')+0.5, 'pop')]
    ev += [(T('c17'), 'whoosh'), (T('c17')+0.4, 'count'), (T('c17')+1.35, 'drop'), (T('c18'), 'whoosh')] + [(T('c18')+0.3+j*0.15, 'pop') for j in range(3)]
    ev += [(T('c19'), 'shimmer')] + [(T('c19')+0.3+j*0.25, 'pop') for j in range(3)]
    return ev

def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 2) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            frame(tt).convert('RGB').save(f'/home/claude/msft/prev_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
