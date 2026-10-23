"""Images clés de la DA « luxe » pour la vidéo LVMH (validation avant animation)."""
import math, random, cairo
import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
def hx(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
IVORY, IVORY_D, INK, INK_2 = hx('F4EFE6'), hx('E6DDCC'), hx('17140F'), hx('6E665A')
GOLD, GOLD_L, GOLD_D, BORDEAUX = hx('A8834C'), hx('D8C08E'), hx('7E6136'), hx('7A2632')
SERIF, SANS = "Bodoni Moda", "Poppins"

def src(c, col, a=1.0): c.set_source_rgba(col[0], col[1], col[2], col[3]*a)
def font(c, fam, size, bold=False, italic=False):
    c.select_font_face(fam, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
def tw(c, s, fam, size, bold=False, italic=False, track=0):
    font(c, fam, size, bold, italic)
    return sum(c.text_extents(ch).x_advance for ch in s)+track*(len(s)-1) if track else c.text_extents(s).x_advance
def txt(c, s, x, y, size, col, fam=SERIF, bold=False, italic=False, align='c', a=1.0, track=0):
    font(c, fam, size, bold, italic); w = tw(c, s, fam, size, bold, italic, track)
    x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8; src(c, col, a)
    if track:
        for ch in s: c.move_to(x0, yy); c.show_text(ch); x0 += c.text_extents(ch).x_advance+track
    else: c.move_to(x0, yy); c.show_text(s)
    return w
def caps(c, s, x, y, size, col, a=1.0, align='c', track=None):
    return txt(c, s, x, y, size, col, SANS, False, False, align, a, track if track is not None else size*0.32)
def hair(c, x1, y1, x2, y2, col=GOLD, w=1.5, a=1.0):
    c.move_to(x1, y1); c.line_to(x2, y2); src(c, col, a); c.set_line_width(w); c.stroke()

def to_cairo(im):
    data = bytearray(im.tobytes('raw', 'BGRA'))
    return cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, im.width, im.height, im.width*4)
def paper():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    src(c, IVORY); c.paint()
    g = cairo.RadialGradient(540, 820, 80, 540, 900, 1300)
    g.add_color_stop_rgba(0, 1, 0.995, 0.98, 0.9); g.add_color_stop_rgba(1, *IVORY_D[:3], 0.0); c.set_source(g); c.paint()
    v = cairo.RadialGradient(540, 960, 700, 540, 960, 1400)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0.35, 0.28, 0.18, 0.22); c.set_source(v); c.paint()
    # grain de papier
    rng = np.random.default_rng(3); n = (rng.standard_normal((H, W))*6).astype(np.int16)
    s.flush(); a = np.ndarray((H, W, 4), np.uint8, s.get_data())
    for k in range(3): a[:, :, k] = np.clip(a[:, :, k].astype(np.int16)+n, 0, 255)
    s.mark_dirty()
    # double filet doré (écrin)
    for inset, w_, al in ((44, 1.2, 0.55), (54, 0.6, 0.35)):
        c.rectangle(inset, inset, W-2*inset, H-2*inset); src(c, GOLD, al); c.set_line_width(w_); c.stroke()
    return s
def glow(c, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *col[:3], a); g.add_color_stop_rgba(1, *col[:3], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2*math.pi); c.fill()
def progress(c, p):
    hair(c, 140, 266, 940, 266, INK_2, 1.5, 0.25); hair(c, 140, 266, 140+800*p, 266, GOLD, 3)
def caption(c, words, y=1350):
    """sous-titre : Poppins pour la lisibilité, mot clé en Bodoni italique doré souligné d'un filet"""
    size = 50; parts = []
    for w_ in words:
        kw = isinstance(w_, tuple); s = w_[0] if kw else w_
        wd = tw(c, s, SERIF, size*1.15, True, True) if kw else tw(c, s, SANS, size)
        parts.append((s, kw, wd))
    sp = tw(c, ' ', SANS, size); total = sum(p[2] for p in parts)+sp*(len(parts)-1)
    lines, cur, cw = [], [], 0
    for p in parts:
        need = p[2]+(sp if cur else 0)
        if cur and cw+need > 860: lines.append((cur, cw)); cur, cw = [], 0; need = p[2]
        cur.append(p); cw += need
    lines.append((cur, cw))
    for li, (ps, lw) in enumerate(lines):
        x = 540-lw/2; yy = y-(len(lines)-1)*38+li*78
        for s, kw, wd in ps:
            if kw:
                txt(c, s, x, yy-2, size*1.15, GOLD_D, SERIF, True, True, 'l'); hair(c, x, yy+30, x+wd, yy+30, GOLD, 2)
            else: txt(c, s, x, yy, size, INK, SANS, False, False, 'l')
            x += wd+sp

# ---------- 1. la galaxie des Maisons ----------
GROUPS = [("MODE & MAROQUINERIE", 165, ["Louis Vuitton", "Dior", "Celine", "Loewe", "Fendi", "Loro Piana", "Givenchy", "Berluti"]),
          ("VINS & SPIRITUEUX", 250, ["Moët & Chandon", "Dom Pérignon", "Hennessy", "Veuve Clicquot", "Krug", "Ruinart"]),
          ("MONTRES & JOAILLERIE", 330, ["Tiffany & Co.", "Bvlgari", "TAG Heuer", "Hublot", "Chaumet"]),
          ("PARFUMS & COSMÉTIQUES", 405, ["Guerlain", "Parfums Christian Dior", "Benefit", "Acqua di Parma"]),
          ("DISTRIBUTION SÉLECTIVE", 475, ["Sephora", "Le Bon Marché", "DFS", "La Samaritaine"])]
ANG = {"Louis Vuitton": 270, "Dior": 90, "Celine": 215, "Loewe": 325, "Fendi": 20, "Loro Piana": 155, "Givenchy": 50, "Berluti": 128,
       "Moët & Chandon": 305, "Dom Pérignon": 335, "Hennessy": 190, "Veuve Clicquot": 240, "Krug": 0, "Ruinart": 130,
       "Tiffany & Co.": 200, "Bvlgari": 350, "TAG Heuer": 35, "Hublot": 115, "Chaumet": 150,
       "Guerlain": 5, "Parfums Christian Dior": 140, "Benefit": 180, "Acqua di Parma": 270,
       "Sephora": 220, "Le Bon Marché": 320, "DFS": 15, "La Samaritaine": 60}
def galaxy(path):
    s = paper(); c = cairo.Context(s); cx, cy = 540, 845
    progress(c, 0.08)
    caps(c, "UNE GALAXIE DE", 540, 318, 24, INK_2)
    txt(c, "75 Maisons", 540, 382, 76, INK, SERIF, False, True)
    glow(c, cx, cy, 240, GOLD_L, 0.55)
    for gi, (gname, r, names) in enumerate(GROUPS):
        rx, ry = r*0.80, r*0.88
        c.new_path(); c.save(); c.translate(cx, cy); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2*math.pi); c.restore()
        src(c, GOLD, 0.45); c.set_line_width(1.1); c.stroke()
        for k, n in enumerate(names):
            a = math.radians(ANG[n]); x, y = cx+rx*math.cos(a), cy+ry*math.sin(a)
            c.new_path(); c.arc(x, y, 4.5 if gi == 0 and k < 2 else 3, 0, 2*math.pi); src(c, GOLD_D if k == 0 else GOLD); c.fill()
            size = 30 if gi == 0 and k < 2 else 22
            right = math.cos(a) >= 0; lx = x+(13 if right else -13); al = 'l' if right else 'r'
            if abs(math.cos(a)) < 0.3: lx, al = x, 'c'; y = y+(22 if math.sin(a) > 0 else -22)
            txt(c, n, lx, y, size, INK, SERIF, False, False, al, 0.92)
    c.new_path()
    txt(c, "LVMH", cx, cy-8, 70, INK, SERIF, True, False)
    hair(c, cx-56, cy+30, cx+56, cy+30, GOLD, 1.5); caps(c, "1987", cx, cy+54, 18, GOLD_D)
    caption(c, ["Derrière", "un", "seul", "nom,", ("75 Maisons", 1), "de", "luxe."])
    s.write_to_png(path)

# ---------- 2. la famille ----------
KIDS = [("Delphine", "PDG de Christian Dior Couture"), ("Antoine", "Image, communication, Berluti"),
        ("Alexandre", "Directeur général délégué, Moët Hennessy"), ("Frédéric", "PDG de Loro Piana"),
        ("Jean", "Horlogerie Louis Vuitton")]
def family(path):
    s = paper(); c = cairo.Context(s)
    progress(c, 0.22)
    caps(c, "UNE AFFAIRE DE FAMILLE", 540, 330, 24, INK_2)
    txt(c, "Bernard Arnault", 540, 410, 82, INK, SERIF, False, True)
    caps(c, "PDG DEPUIS 1989  ·  77 ANS", 540, 480, 22, GOLD_D)
    hair(c, 540, 515, 540, 585, GOLD, 1.5)
    hair(c, 160, 585, 920, 585, GOLD, 1.2)
    for i, (n, role) in enumerate(KIDS):
        y = 650+i*128
        hair(c, 160, 585, 160, y, GOLD, 1.2, 0.0)
        c.arc(180, y, 6, 0, 2*math.pi); src(c, GOLD); c.fill()
        txt(c, n, 215, y-16, 48, INK, SERIF, False, False, 'l')
        txt(c, role, 216, y+30, 25, INK_2, SANS, False, False, 'l')
        if i < 4: hair(c, 215, y+66, 920, y+66, GOLD, 0.8, 0.35)
    hair(c, 180, 585, 180, 650+4*128, GOLD, 1.2, 0.8)
    # bloc contrôle
    c.rectangle(160, 1300-60-40, 760, 0)
    caption(c, ["La", "famille", "contrôle", ("66 %", 1), "des", "droits", "de", "vote."], y=1360)
    s.write_to_png(path)

# ---------- 3. la courbe ----------
P = [(0, 621.6), (.23, 727), (.7, 570), (1.0, 640), (1.23, 679.9), (1.55, 904.6), (1.9, 760), (2.23, 733.6), (2.45, 886),
     (2.8, 690), (3.23, 635.5), (3.31, 754.8), (3.43, 605), (3.68, 436.5), (4.03, 640), (4.23, 645), (4.28, 583.7), (4.46, 460), (4.75, 470), (5.0, 384.6)]
def smooth_pts(P, n=240):
    xs = np.array([p[0] for p in P]); ys = np.array([p[1] for p in P]); out = []
    for i in range(n+1):
        u = 5*i/n; k = min(np.searchsorted(xs, u, 'right')-1, len(xs)-2)
        f = (u-xs[k])/(xs[k+1]-xs[k]); f = f*f*(3-2*f); out.append((u, ys[k]+(ys[k+1]-ys[k])*f))
    return out
def chart(path):
    s = paper(); c = cairo.Context(s)
    progress(c, 0.58)
    caps(c, "LVMH  ·  CINQ ANS DE BOURSE", 540, 330, 24, INK_2)
    x0, x1, yb, yt = 150, 930, 1130, 520
    X = lambda u: x0+u/5*(x1-x0); Y = lambda v: yb-(v-300)/(950-300)*(yb-yt)
    for v in (400, 600, 800):
        hair(c, x0, Y(v), x1, Y(v), GOLD, 0.8, 0.3); txt(c, f"{v} €", x1, Y(v)-18, 20, INK_2, SANS, False, False, 'r')
    for k, yr in enumerate(["2022", "2023", "2024", "2025", "2026"]):
        caps(c, yr, X(0.23+k)+50, yb+36, 18, INK_2)
    pts = [(X(u), Y(v)) for u, v in smooth_pts(P)]
    c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.line_to(pts[-1][0], yb); c.line_to(pts[0][0], yb); c.close_path()
    g = cairo.LinearGradient(0, yt, 0, yb); g.add_color_stop_rgba(0, *GOLD_L[:3], 0.45); g.add_color_stop_rgba(1, *GOLD_L[:3], 0)
    c.set_source(g); c.fill()
    c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; src(c, GOLD_D); c.set_line_width(4); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    # sommet
    px, py = X(1.55), Y(904.6); glow(c, px, py, 40, GOLD_L, 0.8); c.arc(px, py, 7, 0, 2*math.pi); src(c, GOLD_D); c.fill()
    txt(c, "904 €", px, py-62, 46, INK, SERIF, False, True); caps(c, "PRINTEMPS 2023", px, py-22, 16, GOLD_D)
    # aujourd'hui
    ex, ey = pts[-1]; glow(c, ex, ey, 40, BORDEAUX, 0.25); c.arc(ex, ey, 7, 0, 2*math.pi); src(c, BORDEAUX); c.fill()
    txt(c, "385 €", ex-12, ey+56, 46, BORDEAUX, SERIF, False, True, 'r')
    # carte événement
    c.rectangle(160, 1205, 760, 0)
    caption(c, ["Depuis", "janvier,", "l'action", "a", "perdu", ("40 %", 1), "de", "sa", "valeur."], y=1350)
    s.write_to_png(path)

if __name__ == '__main__':
    galaxy('/home/claude/lvmh/k1_galaxie.png'); family('/home/claude/lvmh/k2_famille.png'); chart('/home/claude/lvmh/k3_courbe.png')
    ims = [Image.open(f'/home/claude/lvmh/{n}.png').convert('RGB').resize((540, 960)) for n in ('k1_galaxie', 'k2_famille', 'k3_courbe')]
    sheet = Image.new('RGB', (3*540+40, 960), (60, 60, 60))
    for i, im in enumerate(ims): sheet.paste(im, (i*560, 0))
    sheet.save('/home/claude/lvmh/sheet.png')
