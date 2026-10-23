"""Typographie Visa : bleu nuit, or, chiffres en Inter Display Black, mots clés en or (pas de ruban)."""
import math, cairo
from PIL import Image
W, H = 1080, 1920
GOLD = 'E9C27A'; GOLD2 = 'B8873B'; WH = 'F5F3EE'; GR = '9AA4B5'; NAVY = '0A1430'; GREEN = '3DDC84'; RED = 'FF5A4E'
GOLDG = [(0, 'FFE7B0'), (.45, 'E9C27A'), (1, 'A87632')]
def hx(h, a=1): return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
def col(c, h, a=1): c.set_source_rgba(*hx(h, a))
FAM = {'k': ('Inter Display Black', 0), 'xb': ('Inter Display ExtraBold', 0), 'b': ('Inter Display', 1), 'sb': ('Inter Display SemiBold', 0),
       'm': ('Inter Display Medium', 0), 'l': ('Inter Display Light', 0), 'p': ('Poppins', 1)}
def font(c, f, size):
    fam, bold = FAM[f]; c.select_font_face(fam, 0, cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c, s, f, size, track=0):
    font(c, f, size); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def _path(c, s, x0, yy, f, size, track):
    font(c, f, size); xx = x0
    for ch in s: c.move_to(xx, yy); c.text_path(ch); xx += c.text_extents(ch).x_advance+track
def text(c, s, x, y, f, size, color, align='c', a=1, track=0, shadow=True):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    if shadow: col(c, '000000', .5*a); _path(c, s, x0+2, yy+4, f, size, track); c.fill()
    col(c, color, a); _path(c, s, x0, yy, f, size, track); c.fill(); return w
def gtext(c, s, x, y, f, size, stops=GOLDG, align='c', track=0, shadow=True):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    if shadow: col(c, '000000', .5); _path(c, s, x0+2, yy+5, f, size, track); c.fill()
    g = cairo.LinearGradient(0, yy-size*0.8, 0, yy+size*0.1)
    for p, h in stops: g.add_color_stop_rgba(p, *hx(h))
    _path(c, s, x0, yy, f, size, track); c.set_source(g); c.fill(); return w
def rr(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path(); c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2); c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()
def kicker(c, s, y=350, color=GOLD, size=26): text(c, s, 540, y, 'sb', size, color, 'c', 1, 6, False)
def rule(c, y=395, w=90): col(c, GOLD, .7); c.rectangle(540-w/2, y, w, 2); c.fill()
def pill(c, s, x, y, size=44, color=GOLD, ink='0A1020'):
    w = tw(c, s, 'xb', size)+60; rr(c, x-w/2, y-size*0.75, w, size*1.5, size*0.75); col(c, color); c.fill(); text(c, s, x, y, 'xb', size, ink, 'c', 1, 0, False)
def caption(c, words, y=1352, size=46):
    sp = tw(c, ' ', 'p', size); wd = [tw(c, w, 'p', size) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 790: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: gtext(c, w, x, yy, 'p', size, GOLDG, 'l')
            else: text(c, w, x, yy, 'p', size, WH, 'l')
            x += wd[i]+sp
def progress(c, u):
    col(c, 'FFFFFF', .15); rr(c, 140, 260, 800, 5, 2.5); c.fill(); col(c, GOLD); rr(c, 140, 260, max(5, 800*u), 5, 2.5); c.fill()
def vignette(c):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, 0, 0, .02, .8); g.add_color_stop_rgba(.2, 0, 0, .02, .5); g.add_color_stop_rgba(.4, 0, 0, 0, 0)
    g.add_color_stop_rgba(.6, 0, 0, 0, 0); g.add_color_stop_rgba(.78, 0, 0, .02, .6); g.add_color_stop_rgba(1, 0, 0, .02, .8); c.set_source(g); c.paint()
    r = cairo.RadialGradient(540, 960, 500, 540, 960, 1200); r.add_color_stop_rgba(0, 0, 0, 0, 0); r.add_color_stop_rgba(1, 0, 0, .02, .55); c.set_source(r); c.paint()
def compose(bg, draw, out):
    im = Image.open(bg).convert('RGBA').resize((W, H), Image.LANCZOS)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); vignette(c); draw(c); s.flush()
    ov = Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1); im.alpha_composite(ov); im.convert('RGB').save(out)
