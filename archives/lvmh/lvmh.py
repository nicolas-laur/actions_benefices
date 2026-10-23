"""LVMH : la galaxie, la famille, la chute. DA luxe ivoire / encre / or champagne, 60 i/s."""
import sys, math, subprocess, random
import numpy as np, cairo
from PIL import Image, ImageFilter

W, H, FPS = 1080, 1920, 60
def hx(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
IVORY, IVORY_D, IVORY_L, INK, INK_2 = hx('F4EFE6'), hx('E6DDCC'), hx('FBF8F2'), hx('17140F'), hx('6E665A')
GOLD, GOLD_L, GOLD_D, BORDEAUX = hx('A8834C'), hx('D8C08E'), hx('7E6136'), hx('7A2632')
TEAL = hx('14A38B')
SERIF, SANS = "Bodoni Moda", "Poppins"

# ---------- chiffres vérifiés (au 8 octobre 2026) ----------
NOW, PERF5, PEAK, LOW25 = 384.65, -0.3812, 904.60, 436.50
P0 = NOW/(1+PERF5); SH = 1000/P0
DIV_PAID = [3.0, 7.0, 5.0, 7.0, 5.5, 7.5, 5.5, 7.5, 5.5, 7.5]       # détachements du 30/11/2021 au 28/04/2026
VAL, DIVT = SH*NOW, SH*sum(DIV_PAID); TOT = VAL+DIVT
assert round(VAL) == 619 and round(DIVT) == 98 and round(TOT) == 717 and round((TOT/1000-1)*100) == -28
assert round((NOW/PEAK-1)*100) == -57
DIVS = [("2021", 10.0), ("2022", 12.0), ("2023", 13.0), ("2024", 13.0), ("2025", 13.0)]

# ---------- courbes de mouvement ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_quint(x): x = clamp(x); return 1-(1-x)**5
def out_expo(x): x = clamp(x); return 1 if x >= 1 else 1-2**(-10*x)
def in_out(x): x = clamp(x); return 4*x**3 if x < 0.5 else 1-(-2*x+2)**3/2
def in_cubic(x): x = clamp(x); return x**3
def lerp(a, b, u): return a+(b-a)*u
def seg(t, a, d, f=out_quint): return f((t-a)/d)

# ---------- texte ----------
def src(c, col, a=1.0): c.set_source_rgba(col[0], col[1], col[2], col[3]*a)
def font(c, fam, size, bold=False, italic=False):
    c.select_font_face(fam, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
def tw(c, s, fam, size, bold=False, italic=False, track=0):
    font(c, fam, size, bold, italic)
    return sum(c.text_extents(ch).x_advance for ch in s)+track*(len(s)-1) if track else c.text_extents(s).x_advance
def txt(c, s, x, y, size, col, fam=SERIF, bold=False, italic=False, align='c', a=1.0, track=0):
    if a <= 0.003: return 0
    w = tw(c, s, fam, size, bold, italic, track)
    x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8; src(c, col, a)
    if track:
        for ch in s: c.move_to(x0, yy); c.show_text(ch); x0 += c.text_extents(ch).x_advance+track
    else: c.move_to(x0, yy); c.show_text(s)
    return w
def caps(c, s, x, y, size, col, a=1.0, align='c'):
    return txt(c, s, x, y, size, col, SANS, False, False, align, a, size*0.32)
def hair(c, x1, y1, x2, y2, col=GOLD, w=1.5, a=1.0):
    if a <= 0.003: return
    c.new_path(); c.move_to(x1, y1); c.line_to(x2, y2); src(c, col, a); c.set_line_width(w); c.stroke()
def rr(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path()
    c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()
def glow(c, x, y, r, col, a):
    if a <= 0.003: return
    g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *col[:3], a); g.add_color_stop_rgba(1, *col[:3], 0)
    c.set_source(g); c.new_path(); c.arc(x, y, r, 0, 2*math.pi); c.fill()

# ---------- flou et calques ----------
def to_pil(s):
    s.flush(); return Image.frombuffer('RGBA', (s.get_width(), s.get_height()), bytes(s.get_data()), 'raw', 'BGRA', s.get_stride(), 1)
def to_cairo(im):
    data = bytearray(im.tobytes('raw', 'BGRA'))
    return cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, im.width, im.height, im.width*4)
def layer(c, draw, a=1.0, blur=0.0, dx=0.0, dy=0.0, sc=1.0, pivot=(540, 960), box=None):
    if a <= 0.003: return
    if blur < 0.6:
        c.push_group(); c.save(); c.translate(dx, dy); c.translate(*pivot); c.scale(sc, sc); c.translate(-pivot[0], -pivot[1])
        draw(c); c.restore(); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); return
    bx, by, bw, bh = box or (0, 0, W, H); m = int(blur*3)+6
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(bw)+2*m, int(bh)+2*m); k = cairo.Context(s)
    k.translate(-bx+m, -by+m); k.translate(dx, dy); k.translate(*pivot); k.scale(sc, sc); k.translate(-pivot[0], -pivot[1])
    draw(k)
    b = to_cairo(to_pil(s).filter(ImageFilter.GaussianBlur(blur)))
    c.set_source_surface(b, bx-m, by-m); c.paint_with_alpha(min(1, a))
def reveal(t, t0, d=0.7, rise=26, blur0=14):
    u = seg(t, t0, d); return dict(a=clamp((t-t0)/(d*0.6)), blur=blur0*(1-u), dy=rise*(1-u))
def conceal(t, t0, d=0.5, drift=(0, -24), blur1=12):
    u = seg(t, t0, d, in_cubic); return dict(a=1-u, blur=blur1*u, dx=drift[0]*u, dy=drift[1]*u)
def merge(*ds):
    o = dict(a=1.0, blur=0.0, dx=0.0, dy=0.0)
    for d in ds:
        o['a'] *= d.get('a', 1); o['blur'] = max(o['blur'], d.get('blur', 0)); o['dx'] += d.get('dx', 0); o['dy'] += d.get('dy', 0)
    return o
def L(c, draw, st, box=None, sc=1.0, pivot=(540, 960)):
    layer(c, draw, st.get('a', 1), st.get('blur', 0), st.get('dx', 0), st.get('dy', 0), sc, pivot, box)

# ---------- fond « écrin » ----------
_BG = None
def paper():
    global _BG
    if _BG is not None: return _BG
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    src(c, IVORY); c.paint()
    g = cairo.RadialGradient(540, 820, 80, 540, 900, 1300)
    g.add_color_stop_rgba(0, 1, 0.995, 0.98, 0.9); g.add_color_stop_rgba(1, *IVORY_D[:3], 0.0); c.set_source(g); c.paint()
    v = cairo.RadialGradient(540, 960, 700, 540, 960, 1400)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0.35, 0.28, 0.18, 0.22); c.set_source(v); c.paint()
    rng = np.random.default_rng(3); n = (rng.standard_normal((H, W))*6).astype(np.int16)
    s.flush(); a = np.ndarray((H, W, 4), np.uint8, s.get_data())
    for k in range(3): a[:, :, k] = np.clip(a[:, :, k].astype(np.int16)+n, 0, 255)
    s.mark_dirty()
    for inset, w_, al in ((44, 1.2, 0.55), (54, 0.6, 0.35)):
        c.rectangle(inset, inset, W-2*inset, H-2*inset); src(c, GOLD, al); c.set_line_width(w_); c.stroke()
    _BG = s; return s

def frame_card(c, x, y, w, h, a=1.0, glow_a=0.0):
    """carte écrin : fond ivoire clair, double filet doré"""
    if glow_a > 0: glow(c, x+w/2, y+h/2, max(w, h)*0.7, GOLD_L, 0.5*glow_a)
    c.new_path(); c.rectangle(x+4, y+10, w, h); src(c, hx('3A2E1E'), 0.06*a); c.fill()
    c.rectangle(x, y, w, h); src(c, IVORY_L, a); c.fill()
    c.rectangle(x+0.5, y+0.5, w-1, h-1); src(c, GOLD, 0.8*a); c.set_line_width(1.4); c.stroke()
    c.rectangle(x+9, y+9, w-18, h-18); src(c, GOLD, 0.35*a); c.set_line_width(0.7); c.stroke()

def sweep(c, x, y, w, h, u):
    """reflet lumineux qui glisse sur un élément doré"""
    if not 0 < u < 1: return
    cx = lerp(x-120, x+w+120, u)
    g = cairo.LinearGradient(cx-90, y, cx+90, y+h)
    g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(0.5, 1, 0.98, 0.9, 0.55); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    c.save(); c.rectangle(x, y, w, h); c.clip(); c.set_operator(cairo.OPERATOR_ATOP); c.set_source(g); c.paint(); c.restore()

# ---------- script et minutage ----------
CAPS = [
 ("c01", "Le roi du luxe vaut [57_%] de moins qu'à son sommet."),
 ("c02", "1 000 € il y a 5 ans : combien aujourd'hui ? Réponse à la [fin]."),
 ("c03", "LVMH, c'est d'abord une [galaxie]."),
 ("c04", "[Mode_et_maroquinerie] : Louis Vuitton, Dior, Celine, Loewe, Fendi…"),
 ("c05", "[Vins_et_spiritueux] : Moët & Chandon, Dom Pérignon, Hennessy, Krug…"),
 ("c06", "[Montres_et_joaillerie] : Tiffany, Bvlgari, TAG Heuer, Hublot."),
 ("c07", "[Parfums], puis Sephora, Le Bon Marché…"),
 ("c08", "Plus de [75_Maisons], 211 000 salariés, 6 283 boutiques."),
 ("c09", "Près de la [moitié] des ventes vient de la mode."),
 ("c10", "Tout commence en [1743] avec Moët & Chandon, puis Hennessy en 1765."),
 ("c11", "[1854] : Louis Vuitton ouvre sa maison à Paris."),
 ("c12", "[1987] : Moët Hennessy et Louis Vuitton fusionnent. LVMH naît."),
 ("c13", "[1989] : Bernard Arnault prend les commandes."),
 ("c14", "Puis il achète : Bvlgari, Dior Couture, [Tiffany]."),
 ("c15", "Ses [cinq_enfants] occupent des postes clés."),
 ("c16", "La famille contrôle [66_%] des droits de vote."),
 ("c17", "Au printemps 2023, l'action dépasse les [900_€]."),
 ("c18", "Puis la Chine [ralentit], les touristes dépensent moins."),
 ("c19", "2025 : droits de douane, plus bas à [436_€] en juin."),
 ("c20", "2026 : taxes, Moyen-Orient, luxe en recul en [Chine]."),
 ("c21", "Depuis janvier : [−40_%]. Aujourd'hui : 385 €."),
 ("c22", "Pourtant, LVMH a gagné [10,9_milliards] d'euros en 2025."),
 ("c23", "Et le dividende tient : [13_€] par action."),
 ("c24", "Tes 1 000 € ? ≈ 619 € en actions et 98 € de dividendes."),
 ("c25", "Total : ≈ [717_€]."),
 ("c26", "Et toi, à 385 € : tu achètes, tu vends ou tu [attends] ?"),
 ("c27", "Abonne-toi, like, partage."),
]
def build():
    tl, t = {}, 0.0
    for cid, s in CAPS:
        clean = s.replace('[', '').replace(']', '').replace('_', ' ')
        d = max(2.1, len(clean)/21+0.55)
        if cid in ('c02', 'c21', 'c25', 'c26', 'c17', 'c19', 'c20'): d += 0.4
        if cid in ('c04', 'c05', 'c06', 'c07'): d += 0.2
        if cid == 'c27': d = 3.4
        if cid == 'c01': d += 0.9
        st = round(t/0.25)*0.25; tl[cid] = (st, d); t = st+d+0.15
    return tl, t+0.2
TL, DUR = build()
def T(c): return TL[c][0]
def E(c): return TL[c][0]+TL[c][1]

import re
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1_\2', s)
    for a_, b_ in ((' :', '_:'), (' ?', '_?'), (' €', '_€'), (' %', '_%'), ('≈ ', '≈_')): s = s.replace(a_, b_)
    out = []
    for tok in s.split(' '):
        k = '[' in tok; out.append((tok.replace('[', '').replace(']', '').replace('_', ' '), k))
    return out
def draw_caption(c, t):
    for cid, s in CAPS:
        a, d = TL[cid]; b = a+d
        if not (a <= t < b): continue
        size = 47; items = parse(s)
        wd = [tw(c, w, SERIF, size*1.12, True, True) if k else tw(c, w, SANS, size) for w, k in items]
        sp = tw(c, ' ', SANS, size)
        lines, cur, cw = [], [], 0
        for i in range(len(items)):
            need = wd[i]+(sp if cur else 0)
            if cur and cw+need > 750: lines.append((cur, cw)); cur, cw = [], 0; need = wd[i]
            cur.append(i); cw += need
        lines.append((cur, cw))
        y0 = 1352-(len(lines)-1)*37; fo = 1-seg(t, b-0.25, 0.25, in_cubic)
        n_ = 0
        for li, (idx, lw) in enumerate(lines):
            x = 540-lw/2; y = y0+li*74
            for i in idx:
                w, k = items[i]; ti = a+n_*0.05; n_ += 1
                u = seg(t, ti, 0.45); al = clamp((t-ti)/0.25)*fo; yy = y+12*(1-u)
                if al > 0:
                    if k:
                        txt(c, w, x, yy-2, size*1.12, GOLD_D, SERIF, True, True, 'l', al)
                        uu = seg(t, ti+0.15, 0.5, in_out); hair(c, x, yy+29, x+wd[i]*uu, yy+29, GOLD, 2, al)
                    else: txt(c, w, x, yy, size, INK, SANS, False, False, 'l', al)
                x += wd[i]+sp

def progress(c, t):
    hair(c, 140, 266, 940, 266, INK_2, 1.5, 0.22); hair(c, 140, 266, 140+800*clamp(t/DUR), 266, GOLD, 3)

# ---------- scène 1 : accroche ----------
def hook_static(c, show_new=1.0, show_old=0.0):
    caps(c, "LVMH  ·  SON SOMMET", 540, 520, 24, INK_2)
    if show_old > 0: txt(c, "904 €", 540, 720, 200, GOLD_D, SERIF, False, True, 'c', show_old)
    if show_new > 0: txt(c, "385 €", 540, 720, 200, BORDEAUX, SERIF, False, True, 'c', show_new)
def sc_hook(c, t):
    t0 = T('c01'); swap = t0+1.3
    caps(c, "LVMH  ·  SON SOMMET" if t < swap+0.3 else "LVMH  ·  AUJOURD'HUI", 540, 520, 24, INK_2,
         clamp(t/0.3) if t < swap else clamp((t-swap-0.3)/0.3) if t >= swap+0.3 else 1-clamp((t-swap)/0.3))
    o = merge(dict(a=1, blur=0) if t > 0.05 else dict(a=1), conceal(t, swap, 0.45, (0, -20), 16) if t >= swap else {})
    L(c, lambda k: txt(k, "904 €", 540, 720, 200, GOLD_D, SERIF, False, True), o, (90, 580, 900, 280))
    if t < swap+0.1: glow(c, 540, 720, 300, GOLD_L, 0.35*(1-clamp((t-swap)/0.3)))
    if t >= swap+0.25:
        n = reveal(t, swap+0.25, 0.8, 30, 18)
        L(c, lambda k: txt(k, "385 €", 540, 720, 200, BORDEAUX, SERIF, False, True), n, (90, 580, 900, 280))
        s = reveal(t, swap+0.9, 0.7, 16, 10)
        def seal(k):
            w = tw(k, "−57 %", SERIF, 50, False, True)+70
            k.rectangle(540-w/2, 875, w, 84); src(k, BORDEAUX); k.set_line_width(1.6); k.stroke()
            k.rectangle(540-w/2+7, 882, w-14, 70); src(k, BORDEAUX, 0.4); k.set_line_width(0.7); k.stroke()
            txt(k, "−57 %", 540, 917, 50, BORDEAUX, SERIF, False, True)
        L(c, seal, s, (300, 840, 480, 160))
    # au début de c02 : bascule vers le cadre de l'accroche
def sc_question_hook(c, t):
    t0 = T('c02')
    r = reveal(t, t0, 0.8, 30, 16)
    def fr(k):
        frame_card(k, 190, 500, 700, 520)
        caps(k, "1 000 € INVESTIS IL Y A 5 ANS", 540, 590, 22, INK_2)
        txt(k, "1 000 €", 540, 690, 110, INK, SERIF, False, True)
        hair(k, 400, 780, 680, 780, GOLD, 1.2)
        caps(k, "AUJOURD'HUI", 540, 830, 22, INK_2)
        if t < T('c02')+2.6:
            v = random.Random(int(t*18)).randint(300, 1900); s = f"{v:,} €".replace(',', ' ')
            txt(k, s, 540, 920, 90, GOLD_D, SERIF, False, True)
        else:
            txt(k, "? ? ? €", 540, 920, 90, GOLD_D, SERIF, False, True)
    L(c, fr, r, (150, 460, 780, 600))

# ---------- scène 2 : la galaxie ----------
GROUPS = [("Mode & Maroquinerie", 165, ["Louis Vuitton", "Dior", "Celine", "Loewe", "Fendi", "Loro Piana", "Givenchy", "Berluti"]),
          ("Vins & Spiritueux", 250, ["Moët & Chandon", "Dom Pérignon", "Hennessy", "Veuve Clicquot", "Krug", "Ruinart"]),
          ("Montres & Joaillerie", 330, ["Tiffany & Co.", "Bvlgari", "TAG Heuer", "Hublot", "Chaumet"]),
          ("Parfums & Cosmétiques", 405, ["Guerlain", "Parfums Christian Dior", "Benefit", "Acqua di Parma"]),
          ("Distribution sélective", 475, ["Sephora", "Le Bon Marché", "DFS", "La Samaritaine"])]
ANG = {"Louis Vuitton": 270, "Dior": 90, "Celine": 215, "Loewe": 325, "Fendi": 20, "Loro Piana": 155, "Givenchy": 50, "Berluti": 128,
       "Moët & Chandon": 305, "Dom Pérignon": 350, "Hennessy": 190, "Veuve Clicquot": 240, "Krug": 0, "Ruinart": 130,
       "Tiffany & Co.": 208, "Bvlgari": 333, "TAG Heuer": 35, "Hublot": 115, "Chaumet": 150,
       "Guerlain": 5, "Parfums Christian Dior": 100, "Benefit": 190 - 10, "Acqua di Parma": 270,
       "Sephora": 220, "Le Bon Marché": 295, "DFS": 15, "La Samaritaine": 60}
GC = (540, 845)
def orbit_times():
    return [T('c04')+0.2, T('c05')+0.2, T('c06')+0.2, T('c07')+0.2, T('c07')+1.6]
def name_time(gi, k):
    return orbit_times()[gi]+0.5+k*0.16
def draw_galaxy(c, t, groups=range(5), dim_outer=0.0):
    cx, cy = GC
    for gi in groups:
        gname, r, names = GROUPS[gi]; rx, ry = r*(0.80 if gi < 3 else 0.70), r*0.88; t0 = orbit_times()[gi]
        u = seg(t, t0, 1.1, in_out)
        if u <= 0: continue
        c.new_path(); c.save(); c.translate(cx, cy); c.scale(rx, ry)
        c.arc(0, 0, 1, -math.pi/2, -math.pi/2+2*math.pi*u); c.restore()
        src(c, GOLD, 0.5); c.set_line_width(1.1); c.stroke()
        # petite planète qui parcourt l'orbite (vie secondaire)
        if u >= 1:
            pa = -math.pi/2+(t-t0)*(0.35-gi*0.05)+gi
            glow(c, cx+rx*math.cos(pa), cy+ry*math.sin(pa), 10, GOLD_L, 0.9)
        for k, n in enumerate(names):
            tn = name_time(gi, k); al = clamp((t-tn)/0.35)
            if al <= 0: continue
            uu = seg(t, tn, 0.6)
            a = math.radians(ANG[n]); x, y = cx+rx*math.cos(a), cy+ry*math.sin(a)
            big = gi == 0 and k < 2
            c.new_path(); c.arc(x, y, (4.5 if big else 3)*lerp(2.2, 1, uu), 0, 2*math.pi); src(c, GOLD_D if k == 0 else GOLD, al); c.fill()
            size = 30 if big else 22
            right = math.cos(a) >= 0; lx = x+(13 if right else -13); aln = 'l' if right else 'r'
            if abs(math.cos(a)) < 0.3: lx, aln = x, 'c'; y = y+(22 if math.sin(a) > 0 else -22)
            txt(c, n, lx, y+8*(1-uu), size, INK, SERIF, False, False, aln, al*0.94)
_FIT = {}
def fit(gmax, hw=372, hv=405):
    if gmax in _FIT: return _FIT[gmax]
    k = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)); Rm = Vm = 0
    for gi in range(gmax+1):
        _, r, names = GROUPS[gi]; rx, ry = r*(0.80 if gi < 3 else 0.70), r*0.88
        for j, n in enumerate(names):
            size = 30 if gi == 0 and j < 2 else 22; a = math.radians(ANG[n]); x, y = abs(rx*math.cos(a)), abs(ry*math.sin(a))
            w = tw(k, n, SERIF, size)
            if abs(math.cos(a)) < 0.3: Rm = max(Rm, x+w/2); Vm = max(Vm, y+22+size*0.7)
            else: Rm = max(Rm, x+13+w); Vm = max(Vm, y+size*0.7)
    _FIT[gmax] = min(hw/Rm, hv/Vm); return _FIT[gmax]
def galaxy_camera(t):
    ot = orbit_times()
    keys = [(T('c03'), 2.5)]+[(ot[g], min(d, fit(g))) for g, d in enumerate((1.9, 1.5, 1.18, 1.0, 0.92))]+[(T('c08'), min(0.8, fit(4, 372, 370)))]
    s = keys[0][1]; cy = 845
    for (ta, sa), (tb, sb) in zip(keys, keys[1:]):
        if t >= tb: s = sb
        elif t >= ta + 0.0: s = lerp(sa, sb, in_out((t-tb+1.2)/1.2)) if t > tb-1.2 else sa
    lift = in_out((t-T('c08'))/1.0)
    return s, lerp(0, -95, lift)
def sc_galaxy(c, t):
    s, lift = galaxy_camera(t)
    cx, cy = GC
    # surtitre : groupe en cours, puis « 75 Maisons »
    labels = [(T('c03'), "LVMH", "Une galaxie")]+[(orbit_times()[i], f"GROUPE {i+1} SUR 5", GROUPS[i][0]) for i in range(5)] + \
             [(T('c08'), "UNE GALAXIE DE", "75 Maisons"), (T('c10')-0.25, "", "")]
    for i, (ta, sup, title) in enumerate(labels[:-1]):
        tb = labels[i+1][0]
        if t < ta or t > tb+0.4: continue
        st = merge(reveal(t, ta, 0.7, 18, 12), conceal(t, tb-0.05, 0.4, (0, -16), 10) if t >= tb-0.05 else {})
        if i == 0 and t < T('c03')+0.05: continue
        def lab(k, sup=sup, title=title):
            caps(k, sup, 540, 318, 22, INK_2); txt(k, title, 540, 382, 64, INK, SERIF, False, True)
        L(c, lab, st, (100, 280, 880, 150))
    glow_a = 0.55
    focus = seg(t, T('c09'), 0.8, in_out)
    fold = seg(t, T('c10')-0.1, 0.9, in_out)
    def inner(k):
        glow(k, cx, cy, 240, GOLD_L, glow_a)
        draw_galaxy(k, t, [0])
        txt(k, "LVMH", cx, cy-8, 70, INK, SERIF, True, False)
        hair(k, cx-56, cy+30, cx+56, cy+30, GOLD, 1.5); caps(k, "1987", cx, cy+54, 18, GOLD_D)
    def outer(k): draw_galaxy(k, t, [1, 2, 3, 4])
    sc_ = s*lerp(1, 0.25, fold)
    base = dict(a=1-fold, blur=14*fold, dx=0, dy=lift)
    o_st = merge(base, dict(a=1-0.72*focus, blur=7*focus))
    if o_st['blur'] < 0.6:
        layer(c, outer, o_st['a'], 0, 0, lift, sc_, (cx, cy))
    else:
        layer(c, outer, o_st['a'], o_st['blur'], 0, lift, sc_, (cx, cy), (50, 330, 980, 1000))
    i_st = merge(base, dict(a=clamp((t-T('c03')+0.1)/0.5)))
    if i_st['blur'] < 0.6: layer(c, inner, i_st['a'], 0, 0, lift, sc_, (cx, cy))
    else: layer(c, inner, i_st['a'], i_st['blur'], 0, lift, sc_, (cx, cy), (50, 330, 980, 1000))
    # chiffres clés (c08) puis part de la mode (c09)
    if T('c08') <= t < T('c10')+0.4:
        out = conceal(t, T('c09'), 0.4, (0, -14), 10) if t >= T('c09') else {}
        for j, (big, small) in enumerate([("75+", "MAISONS"), ("211 000", "SALARIÉS"), ("6 283", "BOUTIQUES")]):
            st = merge(reveal(t, T('c08')+0.7+j*0.15, 0.7, 20, 12), out, dict(a=1-fold))
            def fig(k, j=j, big=big, small=small):
                x = 290+j*250; txt(k, big, x, 1168, 54, GOLD_D, SERIF, False, True); caps(k, small, x, 1220, 16, INK_2)
            L(c, fig, st, (140+j*250, 1100, 300, 160))
        if t >= T('c09'):
            st = merge(reveal(t, T('c09')+0.4, 0.7, 20, 12), dict(a=1-fold, blur=10*fold))
            def share(k):
                txt(k, "37,8 Md€", 540, 1160, 60, GOLD_D, SERIF, False, True)
                caps(k, "MODE & MAROQUINERIE · SUR 80,8 MD€ EN 2025", 540, 1218, 15, INK_2)
            L(c, share, st, (100, 1090, 880, 150))

# ---------- scène 3 : l'histoire ----------
NODES = [('c10', 0.25, "1743", "Moët & Chandon"), ('c10', 1.6, "1765", "Hennessy"), ('c11', 0.2, "1854", "Louis Vuitton, Paris"),
         ('c12', 0.2, "1987", "Moët Hennessy + Louis Vuitton = LVMH"), ('c13', 0.2, "1989", "Bernard Arnault aux commandes")]
def sc_history(c, t):
    t0 = T('c10'); out = conceal(t, T('c14')-0.15, 0.5, (0, -30), 12) if t >= T('c14')-0.15 else {}
    head = merge(reveal(t, t0+0.05, 0.7, 18, 12), out)
    L(c, lambda k: (caps(k, "L'HISTOIRE", 540, 318, 22, INK_2), txt(k, "Trois siècles de luxe", 540, 382, 58, INK, SERIF, False, True)),
      head, (100, 280, 880, 150))
    ys = [500+i*165 for i in range(5)]
    tn = [T(cid)+dt for cid, dt, *_ in NODES]
    # filet vertical qui se dessine de nœud en nœud
    reach = ys[0]
    for i in range(5):
        if t >= tn[i]: reach = ys[i] if i == 0 else lerp(ys[i-1], ys[i], seg(t, tn[i]-0.15, 0.5, in_out))
    def spine(k): hair(k, 250, ys[0], 250, reach, GOLD, 1.4)
    L(c, spine, merge(dict(a=clamp((t-tn[0])/0.3)), out))
    for i, (cid, dt, yr, lab) in enumerate(NODES):
        if t < tn[i]: continue
        hl = seg(t, tn[i]+0.3, 0.6, in_out) if yr == "1987" else 0
        st = merge(reveal(t, tn[i], 0.7, 22, 12), out)
        def node(k, i=i, yr=yr, lab=lab, hl=hl):
            y = ys[i]
            if hl > 0: glow(k, 500, y+5, 330, GOLD_L, 0.45*hl)
            k.new_path(); k.arc(250, y, 7, 0, 2*math.pi); src(k, GOLD_D); k.fill()
            k.new_path(); k.arc(250, y, 15, 0, 2*math.pi); src(k, GOLD, 0.5); k.set_line_width(1); k.stroke()
            txt(k, yr, 295, y-14, 62, GOLD_D if yr in ("1987", "1989") else INK, SERIF, False, True, 'l')
            txt(k, lab, 297, y+40, 26, INK_2, SANS, False, False, 'l')
        L(c, node, st, (200, ys[i]-80, 840, 170))
def sc_buy(c, t):
    t0 = T('c14'); out = conceal(t, T('c15')-0.2, 0.5, (0, -30), 12) if t >= T('c15')-0.2 else {}
    head = merge(reveal(t, t0+0.1, 0.7, 18, 12), out)
    L(c, lambda k: (caps(k, "LES GRANDES ACQUISITIONS", 540, 318, 22, INK_2), txt(k, "Il achète", 540, 382, 58, INK, SERIF, False, True)),
      head, (100, 280, 880, 150))
    items = [("2011", "Bvlgari", "Joaillier romain"), ("2017", "Dior Couture", "6,5 Md€"), ("2021", "Tiffany & Co.", "≈ 16 Md$")]
    for j, (yr, name, sub) in enumerate(items):
        tj = t0+0.5+j*0.55; st = merge(reveal(t, tj, 0.75, 28, 14), out)
        y = 520+j*230; last = j == 2
        def cardf(k, y=y, yr=yr, name=name, sub=sub, last=last, tj=tj):
            frame_card(k, 165, y, 745, 180, glow_a=seg(t, tj+0.6, 0.6, in_out) if last else 0)
            txt(k, yr, 205, y+90, 54, GOLD_D, SERIF, False, True, 'l')
            hair(k, 345, y+40, 345, y+140, GOLD, 1, 0.6)
            txt(k, name, 380, y+76, 46, INK, SERIF, False, False, 'l')
            caps(k, sub.upper(), 382, y+124, 18, INK_2, 1, 'l')
        L(c, cardf, st, (120, y-40, 840, 260))

# ---------- scène 4 : la famille ----------
KIDS = [("Delphine", "PDG de Christian Dior Couture"), ("Antoine", "Image et communication, Berluti"),
        ("Alexandre", "Directeur général délégué, Moët Hennessy"), ("Frédéric", "PDG de Loro Piana"),
        ("Jean", "Horlogerie Louis Vuitton")]
def sc_family(c, t):
    t0 = T('c15'); foc = seg(t, T('c16'), 0.7, in_out)
    out = conceal(t, T('c17')-0.2, 0.5, (0, -30), 12) if t >= T('c17')-0.2 else {}
    dimst = dict(a=1-0.85*foc, blur=9*foc)
    head = merge(reveal(t, t0+0.05, 0.8, 22, 14), dimst, out)
    def hd(k):
        caps(k, "UNE AFFAIRE DE FAMILLE", 540, 318, 22, INK_2)
        txt(k, "Bernard Arnault", 540, 400, 80, INK, SERIF, False, True)
        caps(k, "PDG DEPUIS 1989  ·  77 ANS", 540, 470, 20, GOLD_D)
    L(c, hd, head, (80, 270, 920, 240))
    tree = seg(t, t0+0.6, 0.8, in_out)
    def branch(k):
        hair(k, 540, 505, 540, 505+80*tree, GOLD, 1.4)
        if tree > 0.5:
            u = in_out((tree-0.5)*2); hair(k, 540-360*u, 585, 540+340*u, 585, GOLD, 1.2)
    L(c, branch, merge(dimst, out))
    for i, (n, role) in enumerate(KIDS):
        ti = t0+1.0+i*0.22; y = 650+i*122
        st = merge(reveal(t, ti, 0.7, 22, 12), dimst, out)
        def kid(k, y=y, n=n, role=role, i=i):
            k.new_path(); k.arc(180, y, 6, 0, 2*math.pi); src(k, GOLD); k.fill()
            txt(k, n, 215, y-16, 46, INK, SERIF, False, False, 'l')
            txt(k, role, 216, y+28, 24, INK_2, SANS, False, False, 'l')
            if i < 4: hair(k, 215, y+62, 880, y+62, GOLD, 0.8, 0.35)
        L(c, kid, st, (150, y-60, 820, 130))
    L(c, lambda k: hair(k, 180, 585, 180, lerp(585, 650+4*122, seg(t, t0+1.0, 1.1, in_out)), GOLD, 1.2, 0.8), merge(dimst, out))
    # jauge 66 %
    if t >= T('c16'):
        st = merge(reveal(t, T('c16')+0.2, 0.8, 24, 16), out)
        f = seg(t, T('c16')+0.5, 1.4, in_out)*0.6627
        def gauge(k):
            cx, cy, r = 540, 820, 230
            glow(k, cx, cy, 300, GOLD_L, 0.5)
            k.new_path(); k.arc(cx, cy, r, 0, 2*math.pi); src(k, GOLD, 0.25); k.set_line_width(14); k.stroke()
            if f > 0:
                k.new_path(); k.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*f); src(k, GOLD_D); k.set_line_width(14)
                k.set_line_cap(cairo.LINE_CAP_ROUND); k.stroke(); k.set_line_cap(cairo.LINE_CAP_BUTT)
            k.new_path(); k.arc(cx, cy, r-30, 0, 2*math.pi); src(k, GOLD, 0.35); k.set_line_width(0.8); k.stroke()
            txt(k, f"{round(f*100)} %", cx, cy-18, 120, INK, SERIF, False, True)
            caps(k, "DES DROITS DE VOTE", cx, cy+70, 18, INK_2)
            caps(k, "50,3 % DU CAPITAL", cx, cy+105, 16, GOLD_D)
        L(c, gauge, st, (250, 530, 580, 580))

# ---------- scène 5 : la bourse ----------
P = [(0, 621.6), (.23, 727), (.7, 570), (1.0, 640), (1.23, 679.9), (1.55, 904.6), (1.9, 760), (2.23, 733.6), (2.45, 886),
     (2.8, 690), (3.23, 635.5), (3.31, 754.8), (3.43, 605), (3.68, 436.5), (4.03, 640), (4.23, 645), (4.28, 583.7),
     (4.46, 460), (4.75, 470), (5.0, 384.65)]
_xs = np.array([p[0] for p in P]); _ys = np.array([p[1] for p in P])
def price(u):
    u = clamp(u, 0, 5); k = min(np.searchsorted(_xs, u, 'right')-1, len(_xs)-2)
    f = (u-_xs[k])/(_xs[k+1]-_xs[k]); f = f*f*(3-2*f); return _ys[k]+(_ys[k+1]-_ys[k])*f
def U(t):
    keys = [(T('c17'), 0.0), (T('c17')+2.2, 1.55), (T('c18'), 1.6), (T('c18')+2.0, 3.23), (T('c19'), 3.26), (T('c19')+1.6, 3.68),
            (T('c19')+2.4, 4.23), (T('c20'), 4.25), (T('c20')+2.4, 4.9), (T('c21'), 4.92), (T('c21')+0.9, 5.0)]
    if t <= keys[0][0]: return 0.0
    for (a, ua), (b, ub) in zip(keys, keys[1:]):
        if t <= b: return lerp(ua, ub, in_out((t-a)/(b-a)) if ub-ua > 0.2 else (t-a)/(b-a))
    return 5.0
X0, X1, YB, YT = 175, 885, 1060, 500
def X(u): return X0+u/5*(X1-X0)
def Y(v): return YB-(v-300)/(1000-300)*(YB-YT)
EVENTS = [('c17', "Printemps 2023", "Plus de 450 Md€ en bourse"), ('c18', "2024", "La Chine ralentit"), ('c19', "Juin 2025", "Plus bas à 436,50 €"), ('c20', "2026", "Taxes · Moyen-Orient · Chine")]
def sc_chart(c, t):
    t0 = T('c17'); out = conceal(t, T('c22')-0.2, 0.5, (0, -30), 12) if t >= T('c22')-0.2 else {}
    u = U(t)
    head = merge(reveal(t, t0+0.05, 0.7, 18, 12), out)
    L(c, lambda k: (caps(k, "CINQ ANS DE BOURSE", 540, 318, 22, INK_2), txt(k, "LVMH", 540, 382, 58, INK, SERIF, True, False)),
      head, (100, 280, 880, 150))
    def chart(k):
        g = seg(t, t0+0.1, 0.8, in_out)
        for v in (400, 600, 800):
            hair(k, X0, Y(v), X0+(X1-X0)*g, Y(v), GOLD, 0.8, 0.3); txt(k, f"{v} €", X1, Y(v)-17, 19, INK_2, SANS, False, False, 'r', g*((1-seg(t, T('c20')+1.2, 0.5)) if v == 400 else 1))
        for j, yr in enumerate(["2022", "2023", "2024", "2025", "2026"]): caps(k, yr, X(0.23+j)+48, YB+34, 17, INK_2, g)
        if u <= 0: return
        n = max(2, int(u*60)); pts = [(X(u*i/n), Y(price(u*i/n))) for i in range(n+1)]
        k.new_path(); k.move_to(*pts[0]); [k.line_to(*p) for p in pts[1:]]; k.line_to(pts[-1][0], YB); k.line_to(pts[0][0], YB); k.close_path()
        gr = cairo.LinearGradient(0, YT, 0, YB); gr.add_color_stop_rgba(0, *GOLD_L[:3], 0.45); gr.add_color_stop_rgba(1, *GOLD_L[:3], 0)
        k.set_source(gr); k.fill()
        k.new_path(); k.move_to(*pts[0]); [k.line_to(*p) for p in pts[1:]]; src(k, GOLD_D); k.set_line_width(4); k.set_line_join(cairo.LINE_JOIN_ROUND); k.stroke()
        hx_, hy = pts[-1]; down = u > 3.2
        glow(k, hx_, hy, 34+6*math.sin(t*5), BORDEAUX if down else GOLD_L, 0.3 if down else 0.8)
        k.new_path(); k.arc(hx_, hy, 7, 0, 2*math.pi); src(k, BORDEAUX if down else GOLD_D); k.fill()
        if u >= 1.55:
            pa = seg(t, t0+2.2, 0.7)
            px, py = X(1.55), Y(PEAK)
            glow(k, px, py, 40, GOLD_L, 0.8*pa)
            txt(k, "904 €", px, py-62+10*(1-pa), 46, INK, SERIF, False, True, 'c', pa)
            caps(k, "PRINTEMPS 2023", px, py-22, 16, GOLD_D, pa)
        if u >= 3.68:
            pa = seg(t, T('c19')+1.6, 0.6); lx, ly = X(3.68), Y(LOW25)
            k.new_path(); k.arc(lx, ly, 6, 0, 2*math.pi); src(k, BORDEAUX, pa); k.fill()
            txt(k, "436 €", lx, ly+40, 32, BORDEAUX, SERIF, False, True, 'c', pa)
        if t >= T('c21'):
            pa = seg(t, T('c21')+0.9, 0.7)
            txt(k, "385 €", hx_-14, hy+58, 50, BORDEAUX, SERIF, False, True, 'r', pa)
    L(c, chart, merge(dict(a=1), out), (90, 300, 900, 920))
    for cid, d, lab in EVENTS:
        t1 = E(cid)
        if not (T(cid) <= t < t1+0.4): continue
        dl = 2.3 if cid == 'c17' else 0.1
        if t < T(cid)+dl: continue
        st = merge(reveal(t, T(cid)+dl, 0.7, 20, 12), conceal(t, t1-0.1, 0.4, (0, -14), 10) if t >= t1-0.1 else {}, out)
        def bub(k, d=d, lab=lab, cid=cid):
            w = max(tw(k, lab, SERIF, 34, False, True)+80, 340); x = 540-w/2
            frame_card(k, x, 1125, w, 112)
            caps(k, d.upper(), x+w/2, 1160, 16, BORDEAUX if cid in ('c19', 'c20') else GOLD_D)
            txt(k, lab, x+w/2, 1200, 32, INK, SERIF, False, True)
        L(c, bub, st, (60, 1090, 960, 190))
    if t >= T('c21'):
        st = merge(reveal(t, T('c21')+0.3, 0.7, 20, 12), out)
        def pill(k):
            w = tw(k, "−40 % depuis janvier", SERIF, 36, False, True)+70
            k.rectangle(540-w/2, 1140, w, 78); src(k, BORDEAUX); k.fill()
            txt(k, "−40 % depuis janvier", 540, 1179, 36, IVORY_L, SERIF, False, True)
        L(c, pill, st, (100, 1100, 880, 160))

# ---------- scène 6 : la nuance ----------
def sc_nuance(c, t):
    t0 = T('c22'); out = conceal(t, T('c23')-0.15, 0.45, (0, -24), 12) if t >= T('c23')-0.15 else {}
    st = merge(reveal(t, t0+0.1, 0.8, 26, 16), out)
    def big(k):
        caps(k, "BÉNÉFICE NET 2025", 540, 600, 22, INK_2)
        glow(k, 540, 760, 330, GOLD_L, 0.55)
        txt(k, "10,9 Md€", 540, 760, 150, GOLD_D, SERIF, False, True)
        sweep(k, 160, 650, 760, 220, seg(t, t0+0.9, 1.3, in_out))
        hair(k, 420, 880, 660, 880, GOLD, 1.2)
        caps(k, "−13 % SUR UN AN, MAIS TOUJOURS TRÈS RENTABLE", 540, 925, 16, GOLD_D)
    L(c, big, st, (100, 540, 880, 440))
def sc_div(c, t):
    t0 = T('c23'); out = conceal(t, T('c24')-0.15, 0.45, (0, -24), 12) if t >= T('c24')-0.15 else {}
    head = merge(reveal(t, t0+0.05, 0.7, 18, 12), out)
    L(c, lambda k: (caps(k, "DIVIDENDE PAR ACTION", 540, 318, 22, INK_2), txt(k, "Il tient", 540, 382, 58, INK, SERIF, False, True)),
      head, (100, 280, 880, 150))
    base, top = 1110, 560; hmax = base-top
    for i, (yr, v) in enumerate(DIVS):
        cx = 230+i*155; tf = t0+0.6+i*0.22
        st = merge(reveal(t, t0+0.2+i*0.06, 0.6, 18, 10), out)
        f = seg(t, tf, 0.7); h = hmax*(v/14)*f
        def bar(k, cx=cx, h=h, yr=yr, v=v, f=f):
            k.new_path(); k.rectangle(cx-46, top, 92, hmax); src(k, GOLD, 0.35); k.set_line_width(1); k.stroke()
            if h > 1:
                g = cairo.LinearGradient(0, base-h, 0, base); g.add_color_stop_rgba(0, *GOLD_L[:3], 1); g.add_color_stop_rgba(1, *GOLD_D[:3], 1)
                k.rectangle(cx-46, base-h, 92, h); k.set_source(g); k.fill()
            caps(k, yr, cx, base+34, 17, INK_2)
            txt(k, f"{int(v)} €", cx, base-hmax*(v/14)-32, 34, INK, SERIF, False, True, 'c', clamp((f-0.6)/0.4))
        L(c, bar, st, (cx-80, top-80, 160, hmax+140))
    st = merge(reveal(t, t0+2.0, 0.7, 16, 10), out)
    L(c, lambda k: caps(k, "≈ 3,4 % DE RENDEMENT AU COURS ACTUEL", 540, 1205, 17, GOLD_D), st, (100, 1170, 880, 80))

# ---------- scène 7 : la révélation ----------
def sc_reveal(c, t):
    t0 = T('c24'); out = conceal(t, T('c26')-0.2, 0.45, (0, -24), 12) if t >= T('c26')-0.2 else {}
    st = merge(reveal(t, t0, 0.8, 30, 16), out)
    a1 = seg(t, t0+0.4, 1.2, out_expo); a2 = seg(t, t0+1.6, 0.9, out_expo)
    tot = seg(t, T('c25'), 1.0, out_expo)
    def fr(k):
        frame_card(k, 190, 500, 700, 600, glow_a=seg(t, T('c25')+0.6, 0.8, in_out))
        caps(k, "1 000 € INVESTIS IL Y A 5 ANS", 540, 590, 22, INK_2)
        txt(k, "Actions", 260, 680, 36, INK, SERIF, False, False, 'l'); txt(k, f"≈ {round(VAL*a1)} €", 820, 680, 40, INK, SERIF, False, True, 'r')
        txt(k, "Dividendes", 260, 760, 36, INK, SERIF, False, False, 'l', clamp((t-t0-1.4)/0.3))
        txt(k, f"+ {round(DIVT*a2)} €", 820, 760, 40, GOLD_D, SERIF, False, True, 'r', clamp((t-t0-1.4)/0.3))
        hair(k, 260, 820, 820, 820, GOLD, 1.2, clamp((t-t0-2.0)/0.3))
        caps(k, "AUJOURD'HUI", 540, 870, 22, INK_2, clamp((t-T('c25'))/0.3))
        if t >= T('c25'):
            txt(k, f"≈ {round(lerp(VAL+DIVT*0, TOT, tot)) if tot < 1 else 717} €", 540, 975, 110, INK, SERIF, False, True)
            sweep(k, 240, 910, 600, 130, seg(t, T('c25')+1.0, 1.1, in_out))
    L(c, fr, st, (150, 460, 780, 680))
    if t >= T('c25')+0.9:
        s_ = seg(t, T('c25')+0.9, 0.35, out_expo); sc_ = lerp(1.6, 1.0, s_)
        def seal(k):
            k.save(); k.translate(775, 512); k.rotate(-0.12); k.scale(sc_, sc_)
            k.rectangle(-110, -44, 220, 88); src(k, BORDEAUX); k.fill()
            k.rectangle(-102, -36, 204, 72); src(k, IVORY_L, 0.6); k.set_line_width(1); k.stroke()
            txt(k, "−28 %", 0, 0, 52, IVORY_L, SERIF, False, True); k.restore()
        L(c, seal, merge(dict(a=clamp(s_*2)), out))
    if t >= T('c24')+0.5:
        L(c, lambda k: txt(k, "Calcul simplifié : dividendes bruts non réinvestis, avant impôts et frais", 540, 1160, 19, INK_2, SANS),
          merge(dict(a=clamp((t-t0-0.5)/0.5)), out))

# ---------- scène 8 : la question et le CTA ----------
def sc_question(c, t):
    t0 = T('c26'); out = conceal(t, T('c27')-0.15, 0.45, (0, -24), 12) if t >= T('c27')-0.15 else {}
    L(c, lambda k: (caps(k, "À 385 € L'ACTION", 540, 430, 22, INK_2), txt(k, "Et toi ?", 540, 500, 90, INK, SERIF, False, True)),
      merge(reveal(t, t0+0.05, 0.7, 20, 14), out), (100, 380, 880, 200))
    for j, lab in enumerate(["J'achète", "Je vends", "J'attends"]):
        st = merge(reveal(t, t0+0.4+j*0.2, 0.7, 24, 12), out)
        def btn(k, j=j, lab=lab):
            y = 640+j*165; frame_card(k, 240, y, 600, 120)
            txt(k, lab, 540, y+60, 48, INK if j != 1 else BORDEAUX, SERIF, False, True)
        L(c, btn, st, (200, 600+j*165, 680, 200))
def logo_symbol(k, x, y, size):
    k.save(); k.translate(x-size/2, y-size/2); k.scale(size/200, size/200)
    k.new_path(); k.arc(100, 100, 100, 0, 2*math.pi); src(k, TEAL); k.fill()
    k.move_to(36, 138); k.curve_to(56, 136, 64, 112, 84, 114); k.curve_to(104, 116, 112, 128, 128, 98); k.curve_to(144, 68, 146, 62, 160, 56)
    src(k, hx('FFFFFF')); k.set_line_width(13); k.set_line_cap(cairo.LINE_CAP_ROUND); k.stroke()
    k.new_path(); k.arc(160, 56, 11, 0, 2*math.pi); k.fill(); k.restore()
def icon(k, kind, x, y, t, ti):
    src(k, GOLD_D); k.set_line_width(3.5); k.set_line_cap(cairo.LINE_CAP_ROUND); k.new_path()
    if kind == 0:
        k.save(); k.translate(x, y); k.rotate(0.3*math.sin((t-ti)*16)*math.exp(-max(0, t-ti-0.2)*2.5))
        k.move_to(-20, 14); k.curve_to(-18, -26, 18, -26, 20, 14); k.close_path(); k.stroke()
        k.new_path(); k.arc(0, 22, 5, 0, 2*math.pi); k.fill(); k.restore()
    elif kind == 1:
        s = 1+0.25*math.sin(clamp((t-ti-0.2)/0.35)*math.pi)
        k.save(); k.translate(x, y); k.scale(s, s)
        k.move_to(0, 18); k.curve_to(-38, -6, -24, -36, 0, -16); k.curve_to(24, -36, 38, -6, 0, 18); k.close_path(); k.stroke(); k.restore()
    else:
        k.move_to(x-18, y+16); k.curve_to(x-18, y-6, x, y-14, x+14, y-14); k.stroke()
        k.new_path(); k.move_to(x+8, y-26); k.line_to(x+24, y-14); k.line_to(x+8, y-2); k.stroke()
def sc_cta(c, t):
    t0 = T('c27')
    st = reveal(t, t0, 0.8, 20, 14)
    def head(k):
        logo_symbol(k, 540, 470, 130); txt(k, "Actions_Benefices", 540, 590, 40, INK, SERIF, False, True)
    L(c, head, st, (200, 380, 680, 260))
    for j, lab in enumerate(["Abonne-toi", "Like", "Partage"]):
        ti = t0+0.4+j*0.45; s2 = reveal(t, ti, 0.7, 22, 12)
        def b(k, j=j, lab=lab, ti=ti):
            y = 690+j*155; frame_card(k, 260, y, 560, 112)
            icon(k, j, 340, y+56, t, ti); txt(k, lab, 400, y+56, 44, INK, SERIF, False, True, 'l')
        L(c, b, s2, (220, 650+j*155, 640, 190))
    L(c, lambda k: caps(k, "CONTENU PÉDAGOGIQUE, PAS UN CONSEIL EN INVESTISSEMENT", 540, 1205, 15, INK_2), reveal(t, t0+1.6, 0.6, 10, 8))

SCENES = [(0, T('c02'), sc_hook), (T('c02'), T('c03'), sc_question_hook), (T('c03')-0.1, T('c10')+0.9, sc_galaxy),
          (T('c10')-0.2, T('c14')+0.4, sc_history), (T('c14'), T('c15')+0.4, sc_buy), (T('c15'), T('c17')+0.4, sc_family),
          (T('c17'), T('c22')+0.4, sc_chart), (T('c22'), T('c23')+0.4, sc_nuance), (T('c23'), T('c24')+0.4, sc_div),
          (T('c24'), T('c26')+0.4, sc_reveal), (T('c26'), T('c27')+0.4, sc_question), (T('c27'), DUR+0.1, sc_cta)]
FADES = {sc_hook: (0, 0.35), sc_question_hook: (0.0, 0.35)}
MB = [(T('c10')-0.15, T('c10')+0.8)]

def scene(c, t):
    c.set_source_surface(paper(), 0, 0); c.paint()
    for a, b, fn in SCENES:
        if not (a <= t < b): continue
        fi, fo = FADES.get(fn, (0, 0))
        al = 1.0
        if fo and t > b-fo: al = clamp((b-t)/fo)
        if fn is sc_question_hook and t < a+0.01: al = 0
        if al <= 0: continue
        if al < 1:
            c.push_group(); fn(c, t); c.pop_group_to_source(); c.paint_with_alpha(al)
        else: fn(c, t)
    # boucle : la dernière demi-seconde rejoint l'image d'ouverture
    if t > DUR-0.6:
        u = clamp((t-(DUR-0.6))/0.5)
        c.push_group(); c.set_source_surface(paper(), 0, 0); c.paint(); hook_static(c, 0, 1)
        caps(c, "LVMH  ·  SON SOMMET", 540, 520, 24, INK_2); c.pop_group_to_source(); c.paint_with_alpha(u)
    if T('c17') <= t < T('c22'): txt(c, "Courbe simplifiée · Pas un conseil en investissement", 540, 1458, 18, INK_2, SANS)
    draw_caption(c, t); progress(c, t)

def render(t, surf, ctx, n=5):
    if not any(a <= t < b for a, b in MB):
        scene(ctx, t); surf.flush(); return np.ndarray((H, W, 4), np.uint8, surf.get_data()).copy()
    acc = np.zeros((H, W, 4), np.float32)
    for k in range(n):
        scene(ctx, t+(k/n-0.5)*(0.5/FPS)); surf.flush(); acc += np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return (acc/n).astype(np.uint8)

def events():
    ev = [(0.0, 'swell'), (T('c01')+1.3, 'whoosh'), (T('c01')+1.55, 'thud'), (T('c01')+2.2, 'seal'),
          (T('c02')-0.3, 'whoosh'), (T('c02'), 'roll'), (T('c02')+2.6, 'stop'), (T('c03')-0.3, 'whoosh'), (T('c03'), 'shimmer')]
    for gi in range(5):
        ev.append((orbit_times()[gi], 'orbit'))
        for k in range(len(GROUPS[gi][2])): ev.append((name_time(gi, k), 'ting', gi*2+k))
    ev += [(T('c08')+0.7+j*0.15, 'click') for j in range(3)] + [(T('c09')+0.4, 'chime')]
    ev += [(T('c10')-0.1, 'whoosh')] + [(T(cid)+dt, 'node', i) for i, (cid, dt, *_) in enumerate(NODES)] + [(T('c12')+0.5, 'chime')]
    ev += [(T('c14')-0.2, 'whoosh')] + [(T('c14')+0.5+j*0.55, 'click') for j in range(3)] + [(T('c14')+1.7, 'chime')]
    ev += [(T('c15')-0.2, 'whoosh'), (T('c15')+0.05, 'shimmer')] + [(T('c15')+1.0+i*0.22, 'ting', 6+i) for i in range(5)]
    ev += [(T('c16')+0.2, 'whoosh'), (T('c16')+0.5, 'rise')]
    ev += [(T('c17')-0.2, 'whoosh'), (T('c17')+2.2, 'chime'), (T('c18')+0.1, 'click'), (T('c19')+0.1, 'click'), (T('c19')+1.6, 'thud'),
           (T('c20')+0.1, 'click'), (T('c21')+0.3, 'thud'), (T('c21')+0.9, 'seal')]
    ev += [(T('c22')-0.2, 'whoosh'), (T('c22')+0.1, 'shimmer'), (T('c22')+0.9, 'sweep')]
    ev += [(T('c23')-0.2, 'whoosh')] + [(T('c23')+0.6+i*0.22, 'node', i) for i in range(5)]
    ev += [(T('c24')-0.2, 'whoosh'), (T('c24')+0.4, 'roll'), (T('c25'), 'roll'), (T('c25')+0.9, 'seal'), (T('c25')+1.0, 'sweep')]
    ev += [(T('c26')-0.2, 'whoosh')] + [(T('c26')+0.4+j*0.2, 'click') for j in range(3)]
    ev += [(T('c27')-0.2, 'whoosh'), (T('c27'), 'shimmer')] + [(T('c27')+0.4+j*0.45, 'click') for j in range(3)] + [(DUR-0.6, 'whoosh')]
    return ev

def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    if sys.argv[1] == 'info': print(round(DUR, 2), {k: round(v[0], 2) for k, v in TL.items()}); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]:
            tt = float(ts) if ts[0].isdigit() else T(ts.split('+')[0])+float(ts.split('+')[1] if '+' in ts else 0)
            a = render(tt, surf, ctx)
            Image.frombuffer('RGBA', (W, H), a.tobytes(), 'raw', 'BGRA', W*4, 1).convert('RGB').save(f'/home/claude/lvmh/prev_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out],
                          stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(render(i/FPS, surf, ctx).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))

if __name__ == '__main__': main()
