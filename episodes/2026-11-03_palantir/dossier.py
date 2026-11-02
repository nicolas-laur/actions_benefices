"""Boîte à outils DA « dossier classifié » (inspirée du « Decision title card showreel » de Kenn Ejima, voir notes_da.md).
Fond noir ou papier, point rouge fil conducteur, viseur et étiquettes mono, typo grotesque très grasse contre serif italique rouge,
décodage de texte brouillé, panneau d'aéroport, lignes de mots inclinées, grille de points → trame, cotes d'architecte."""
import math, random, functools
import numpy as np, cairo
W, H = 1080, 1920
INK, PAPER, RED, WHITE, GREY = '0C0C0D', 'ECE6DA', 'E8412C', 'F4F1EA', '8C8A84'
def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
def col(c, h, a=1.0): c.set_source_rgba(*rgb(h), a)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
FONTS = {'black': ('Inter Display Black', cairo.FONT_SLANT_NORMAL), 'xb': ('Inter Display ExtraBold', cairo.FONT_SLANT_NORMAL),
         'serif': ('Instrument Serif', cairo.FONT_SLANT_ITALIC), 'serifr': ('Instrument Serif', cairo.FONT_SLANT_NORMAL),
         'mono': ('JetBrains Mono Medium', cairo.FONT_SLANT_NORMAL), 'monob': ('JetBrains Mono', cairo.FONT_SLANT_NORMAL)}
def font(c, f, size):
    fam, sl = FONTS[f]; c.select_font_face(fam, sl, cairo.FONT_WEIGHT_BOLD if f == 'monob' else cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
def tw(c, s, f, size, track=0.0):
    font(c, f, size); return sum(c.text_extents(ch).x_advance for ch in s)+track*size*(len(s)-1)
def text(c, s, x, y, f, size, color=WHITE, a=1.0, align='c', track=0.0, outline=0.0):
    """texte centré verticalement sur y ; outline > 0 : seulement le contour"""
    font(c, f, size); w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*.82; xx = x0
    for ch in s:
        c.move_to(xx, yy); c.text_path(ch); xx += c.text_extents(ch).x_advance+track*size
    col(c, color, a)
    if outline: c.set_line_width(outline); c.stroke()
    else: c.fill()
    return x0, w

# ---------- fonds ----------
_rng = np.random.default_rng(3)
GRAIN = [(_rng.random((H//2, W//2))-.5) for _ in range(4)]
def background(c, mode, t):
    col(c, INK if mode == 'dark' else PAPER); c.paint()
    if mode == 'dark':                                                 # léger halo rouge chaud en haut, comme la référence
        g = cairo.RadialGradient(200, 260, 0, 200, 260, 900); g.add_color_stop_rgba(0, *rgb('3A1A10'), .55); g.add_color_stop_rgba(1, *rgb('3A1A10'), 0)
        c.set_source(g); c.paint()
def grain_layer(a, t, strength=10.0):
    g = GRAIN[int(t*24) % 4]; g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    return np.clip(a+g*strength, 0, 255)

# ---------- viseur et étiquettes ----------
def hud(c, t, mode, labels, a=1.0, rec=True):
    fg = WHITE if mode == 'dark' else INK
    x0, y0, x1, y1, L = 56, 214, 1024, 1486, 46
    c.set_line_width(3)
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        c.move_to(x, y+dy*L); c.line_to(x, y); c.line_to(x+dx*L, y); col(c, fg, .55*a); c.stroke()
    tl, tr, bl, br = labels
    text(c, tl, x0+62, y0+18, 'mono', 21, fg, .65*a, 'l', .04)
    text(c, tr, x1-62, y0+18, 'mono', 21, fg, .65*a, 'r', .04)
    text(c, bl, x0+62, y1-18, 'mono', 21, fg, .55*a, 'l', .04)
    tc = f"{int(t//60):02d}:{int(t%60):02d}:{int((t%1)*60):02d}"
    text(c, br+tc, x1-62, y1-18, 'mono', 21, fg, .55*a, 'r', .04)
    if rec and (t*1.6) % 1 < .6:
        c.arc(x1-62-tw(c, tr, 'mono', 21, .04)-20, y0+18, 7, 0, 2*math.pi); col(c, RED, a); c.fill()

# ---------- point rouge et cible ----------
def dot(c, x, y, r, a=1.0, glow=True):
    if glow:
        g = cairo.RadialGradient(x, y, 0, x, y, r*4); g.add_color_stop_rgba(0, *rgb(RED), .45*a); g.add_color_stop_rgba(1, *rgb(RED), 0)
        c.set_source(g); c.arc(x, y, r*4, 0, 2*math.pi); c.fill()
    c.arc(x, y, r, 0, 2*math.pi); col(c, RED, a); c.fill()
def target(c, x, y, k, mode, a=1.0, coords=("39.74 N", "104.99 W")):
    """cible qui se referme sur le point, avec coordonnées (k de 0 à 1)"""
    fg = WHITE if mode == 'dark' else INK; r = lerp(260, 70, ease(k))
    c.set_line_width(2.5); c.arc(x, y, r, 0, 2*math.pi); col(c, fg, .5*a*ease(k*2)); c.stroke()
    for ang in range(4):
        th = ang*math.pi/2; c.move_to(x+math.cos(th)*(r+12), y+math.sin(th)*(r+12)); c.line_to(x+math.cos(th)*(r+52), y+math.sin(th)*(r+52))
        col(c, fg, .7*a*ease(k*2)); c.stroke()
    if k > .5:
        text(c, f"LAT {coords[0]}", x+r+30, y-26, 'mono', 22, fg, .75*a*ease((k-.5)*3), 'l', .05)
        text(c, f"LON {coords[1]}", x+r+30, y+8, 'mono', 22, fg, .75*a*ease((k-.5)*3), 'l', .05)

# ---------- texte brouillé qui se décode ----------
GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&@$/<>"
def scramble(s, k, seed=1):
    """k de 0 à 1 : les lettres se figent de gauche à droite, les autres changent 20 fois par seconde"""
    r = random.Random(seed); out = []
    n = len(s)
    for i, ch in enumerate(s):
        lock = (i+1)/(n+1)
        if ch == ' ' or k >= lock: out.append(ch)
        else:
            r2 = random.Random(seed*1000+i*37+int(k*400)); out.append(r2.choice(GLYPHS))
    return ''.join(out)

# ---------- panneau d'aéroport ----------
def flap_board(c, s, x, y, cw, chh, k, mode='dark', seed=3, color=WHITE, red_last=False):
    """chaque case défile des caractères puis tombe sur le bon ; k de 0 à 1"""
    n = len(s); x0 = x-n*(cw+8)/2
    for i, ch in enumerate(s):
        cx = x0+i*(cw+8); lock = .25+.6*i/max(1, n-1)
        rr_(c, cx, y-chh/2, cw, chh, 10); col(c, '1C1C1E'); c.fill()
        if k >= lock: g = ch
        else:
            seq = "0123456789$,." if ch in "0123456789$,." else GLYPHS
            g = seq[int((k*30+i*7)) % len(seq)] if k > .05 else ' '
        phase = (k*30+i*7) % 1 if k < lock else 1.0
        sy = abs(math.cos(math.pi*min(1, phase*1.0))) if k < lock else 1.0
        c.save(); c.translate(cx+cw/2, y); c.scale(1, max(.15, sy))
        text(c, g, 0, 0, 'black', chh*.72, RED if (red_last and i == n-1) else color, 1, 'c'); c.restore()
        c.move_to(cx, y); c.line_to(cx+cw, y); c.set_line_width(3); col(c, INK); c.stroke()
def rr_(c, x, y, w, h, r):
    c.new_sub_path(); c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2); c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()

# ---------- lignes de mots inclinées ----------
def word_rows(c, words, t, k, angle=-.20, size=150, mode='dark', fill_color=RED, cy=850, rows=7, speed=180):
    """lignes inclinées qui défilent en sens contraires ; une ligne sur deux en contour"""
    fg = WHITE if mode == 'dark' else INK
    c.save(); c.translate(540, cy); c.rotate(angle)
    for r in range(rows):
        y = (r-(rows-1)/2)*size*.92; w = words[r % len(words)]
        unit = tw(c, w+'  ', 'black', size); dirn = 1 if r % 2 else -1
        off = (t*speed*dirn+r*137) % unit; x = -1400-off
        a = ease(k*3-r*.15)
        while x < 1400:
            if r % 2 == 0: text(c, w, x, y, 'black', size, fill_color if r == (rows//2) else fg, a, 'l')
            else: text(c, w, x, y, 'black', size, fg, a*.8, 'l', outline=2.5)
            x += unit
    c.restore()

# ---------- grille de points → trame ----------
def dot_grid(c, t, k, mode='dark', cx=540, cy=850, cols=11, rows_=15, step=82, red_k=0.0, square_k=0.0, rot=0.0, field=None):
    """grille de points ; red_k : vague rouge qui se propage ; square_k : les points deviennent des carrés qui tournent"""
    fg = WHITE if mode == 'dark' else INK
    for j in range(rows_):
        for i in range(cols):
            x = cx+(i-(cols-1)/2)*step; y = cy+(j-(rows_-1)/2)*step
            d = math.hypot(i-(cols-1)/2, j-(rows_-1)/2)/max(cols, rows_)
            ap = ease(k*2.2-d*1.6)
            if ap <= 0: continue
            v = field(i, j, t) if field else 1.0
            r = step*.28*ap*(.35+.65*v)
            red = clamp(red_k*2.5-d*2)
            colr = RED if red > .5 else fg
            sq = clamp(square_k*2-d)
            if sq > 0:
                c.save(); c.translate(x, y); c.rotate(rot*sq+d*2*sq); s_ = lerp(r*1.8, step*.62, sq)
                c.rectangle(-s_/2, -s_/2, s_, s_); col(c, colr, ap); c.fill(); c.restore()
            else:
                c.arc(x, y, r, 0, 2*math.pi); col(c, colr, ap); c.fill()

# ---------- cotes d'architecte ----------
def dims(c, x0, y0, x1, y1, k, labels=("", ""), color=RED):
    """lignes de cote rouges autour d'un bloc, avec petites étiquettes mono"""
    a = ease(k*2); c.set_line_width(2)
    xm = lerp(x0, x1, ease(k*1.5))
    c.move_to(x0, y0-34); c.line_to(xm, y0-34); col(c, color, a); c.stroke()
    for x in (x0, x1):
        c.move_to(x, y0-46); c.line_to(x, y0-22); col(c, color, a*(1 if x == x0 or k > .66 else 0)); c.stroke()
    ym = lerp(y0, y1, ease(k*1.5-.2))
    c.move_to(x1+34, y0); c.line_to(x1+34, ym); col(c, color, a); c.stroke()
    if labels[0]: text(c, labels[0], (x0+x1)/2, y0-62, 'mono', 22, color, a*ease(k*2-.6), 'c', .05)
    if labels[1]:
        c.save(); c.translate(x1+64, (y0+y1)/2); c.rotate(math.pi/2); text(c, labels[1], 0, 0, 'mono', 22, color, a*ease(k*2-.8), 'c', .05); c.restore()
