"""DA Alphabet : univers clair, barre de recherche générique, cartes de résultats. Aucun logo ni interface Google."""
import math, cairo, random
from PIL import Image, ImageFilter
W, H = 1080, 1920
INK = '202124'; SUB = '5F6368'; LINE = 'DADCE0'; BG = 'F8F9FA'
BLUE = '4285F4'; RED = 'EA4335'; YELLOW = 'FBBC05'; GREEN = '34A853'   # palette Google (couleurs seules, jamais le logo)
GCOLS = [BLUE, RED, YELLOW, GREEN]
AIG = [(0, '4285F4'), (1, '4285F4')]
def hx(h, a=1): return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
def col(c, h, a=1): c.set_source_rgba(*hx(h, a))
FAM = {'k': ('Inter Display Black', 0), 'xb': ('Inter Display ExtraBold', 0), 'b': ('Inter Display', 1), 'sb': ('Inter Display SemiBold', 0),
       'm': ('Inter Display Medium', 0), 'l': ('Inter Display Light', 0)}
def font(c, f, size):
    fam, bold = FAM[f]; c.select_font_face(fam, 0, cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c, s, f, size, track=0):
    font(c, f, size); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def _path(c, s, x0, yy, f, size, track):
    font(c, f, size); xx = x0
    for ch in s: c.move_to(xx, yy); c.text_path(ch); xx += c.text_extents(ch).x_advance+track
def text(c, s, x, y, f, size, color=INK, align='c', a=1, track=0):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    col(c, color, a); _path(c, s, x0, yy, f, size, track); c.fill(); return w
def gtext(c, s, x, y, f, size, stops=AIG, align='c', track=0):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    g = cairo.LinearGradient(x0, 0, x0+w, 0)
    for p, h in stops: g.add_color_stop_rgba(p, *hx(h))
    _path(c, s, x0, yy, f, size, track); c.set_source(g); c.fill(); return w
def rr(c, x, y, w, h, r):
    r = min(r, w/2, h/2); c.new_sub_path(); c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2); c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()
def soft_shadow(c, x, y, w, h, r, a=.10, spread=26):
    for k in range(8, 0, -1):
        e = spread*k/8; rr(c, x-e/2, y-e/2+e*0.5, w+e, h+e, r+e/2); col(c, '1B2340', a/8*(1-k/9)); c.fill()

def background(c, t=0.0):
    col(c, BG); c.paint()
    # halos pastel très doux qui dérivent lentement
    for (x, y, r, h, a, ph) in ((170, 380, 480, 'D2E3FC', .7, 0), (950, 900, 460, 'FAD2CF', .45, 1.7), (160, 1350, 440, 'FEEFC3', .55, 2.4), (900, 1720, 520, 'CEEAD6', .6, 3.1)):
        xx = x+40*math.sin(t*0.25+ph); yy = y+30*math.cos(t*0.2+ph)
        g = cairo.RadialGradient(xx, yy, 0, xx, yy, r); g.add_color_stop_rgba(0, *hx(h, a)); g.add_color_stop_rgba(1, *hx(h, 0)); c.set_source(g); c.paint()
    # trame de points discrète
    col(c, '1B2340', .045)
    for i in range(0, W, 36):
        for j in range(0, H, 36): c.arc(i+18, j+18, 1.6, 0, 2*math.pi); c.fill()

def magnifier(c, x, y, s, color=SUB):
    c.set_line_width(s*0.16); c.set_line_cap(1); col(c, color)
    c.arc(x-s*0.12, y-s*0.12, s*0.36, 0, 2*math.pi); c.stroke(); c.move_to(x+s*0.14, y+s*0.14); c.line_to(x+s*0.46, y+s*0.46); c.stroke()
def mic(c, x, y, s, color=BLUE):
    col(c, color); rr(c, x-s*0.17, y-s*0.45, s*0.34, s*0.6, s*0.17); c.fill()
    c.set_line_width(s*0.09); c.arc(x, y-s*0.02, s*0.32, 0.15*math.pi, 0.85*math.pi); c.stroke(); c.move_to(x, y+s*0.3); c.line_to(x, y+s*0.45); c.stroke()
def searchbar(c, q, y=470, cursor=True, w=900, focus=1.0):
    x = 540-w/2; h = 116
    soft_shadow(c, x, y-h/2, w, h, h/2, .16*focus)
    rr(c, x, y-h/2, w, h, h/2); col(c, 'FFFFFF'); c.fill()
    rr(c, x, y-h/2, w, h, h/2); c.set_line_width(2); col(c, BLUE if focus > .5 else LINE, .55 if focus > .5 else 1); c.stroke()
    magnifier(c, x+64, y, 40)
    tx = x+118; maxw = w-230
    s = q; fs = 40
    while tw(c, s, 'm', fs) > maxw and fs > 28: fs -= 2
    text(c, s, tx, y, 'm', fs, INK, 'l')
    if cursor: col(c, BLUE); c.rectangle(tx+tw(c, s, 'm', fs)+6, y-26, 4, 52); c.fill()
    mic(c, x+w-66, y+6, 46)
def chip(c, s, x, y, color=BLUE, size=30, fill=True):
    w = tw(c, s, 'sb', size)+44; rr(c, x-w/2, y-size*0.85, w, size*1.7, size*0.85)
    col(c, color, .12 if fill else 0); c.fill_preserve(); col(c, color, .9); c.set_line_width(2); c.stroke()
    text(c, s, x, y, 'sb', size, color)
def card(c, x, y, w, h, title=None, src="résultat · avril-juin 2026"):
    soft_shadow(c, x, y, w, h, 34, .12)
    rr(c, x, y, w, h, 34); col(c, 'FFFFFF'); c.fill(); rr(c, x, y, w, h, 34); c.set_line_width(1.5); col(c, LINE); c.stroke()
    c.arc(x+56, y+58, 16, 0, 2*math.pi); col(c, BLUE, .15); c.fill(); c.set_line_width(2.4); col(c, BLUE); c.arc(x+56, y+58, 9, 0, 2*math.pi); c.stroke()
    text(c, src, x+86, y+58, 'm', 26, SUB, 'l')
    if title: text(c, title, x+40, y+122, 'xb', 40, INK, 'l')
def caption(c, words, y=1352, size=46, accent=None):
    accent = accent or BLUE
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 800: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k:
                rr(c, x, yy-34, wd[i], 66, 14); col(c, accent); c.fill(); text(c, w, x+10, yy, 'b', size, INK if accent == YELLOW else 'FFFFFF', 'l')
            else: text(c, w, x, yy, 'b', size, INK, 'l')
            x += wd[i]+sp
def progress(c, u):
    col(c, INK, .08); rr(c, 140, 260, 800, 6, 3); c.fill()
    c.save(); rr(c, 140, 260, max(6, 800*u), 6, 3); c.clip()
    for i, h in enumerate(GCOLS): col(c, h); c.rectangle(140+i*200, 255, 200, 16); c.fill()
    c.restore()
def kicker(c, s, y=360, color=SUB, size=26): text(c, s, 540, y, 'sb', size, color, 'c', 1, 5)
def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); return s, cairo.Context(s)
def to_img(s):
    s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
