"""DA Bitcoin : pièce ₿ en or massif (Blender) en fond, typographie d'affiche, cartes de verre sombre aux liserés dorés."""
import math, sys, cairo
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/nflx')
import nty
from nty import text, surface, to_img, glow, rr, col, hx, tw, _path, W, H, finish
GOLD = 'F5B544'; ORANGE = 'F7931A'; CREAM = 'FFF1DC'; WHITE = 'FFFFFF'; SUB = 'B9A893'; RED = 'E5484D'; GREEN = '3FD08A'; INK = '120C06'

def coin_bg(path, scale=1.0, cy=0.5, blur=0, dim=1.0):
    """fond : rendu de la pièce, recadré/zoomé, éventuellement flouté (profondeur de champ 2D)"""
    im = Image.open(path).convert('RGB').resize((W, H), Image.LANCZOS)
    if scale != 1.0 or cy != .5:
        w, h = int(W*scale), int(H*scale); big = im.resize((w, h), Image.LANCZOS)
        canvas = Image.new('RGB', (W, H), tuple(int(v) for v in np.asarray(im)[5, 5])); ox = (W-w)//2; oy = int(H*cy-h*0.40)
        yy, xx = np.mgrid[0:h, 0:w]; d = np.sqrt(((xx-w/2)/(w*.5))**2+((yy-h*.4)/(h*.42))**2)
        mask = Image.fromarray((np.clip((1-d)/.25, 0, 1)*255).astype(np.uint8))
        canvas.paste(big, (ox, oy), mask); im = canvas
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dim != 1.0: im = ImageEnhance.Brightness(im).enhance(dim)
    return im.convert('RGBA')

def tag(c, s, x, y, color=ORANGE, size=28, fg=INK, a=1):
    w = tw(c, s, 'xb', size, 2)+44; rr(c, x-w/2, y-26, w, 52, 8); col(c, color, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2); return w
def pill(c, s, y, color=ORANGE, fg=INK, a=1):
    w = tw(c, s, 'xb', 34)+70; rr(c, 540-w/2, y-38, w, 76, 38); col(c, color, a); c.fill(); text(c, s, 540, y, 'xb', 34, fg, 'c', a)
def glass(c, x, y, w, h, a=1, r=28):
    rr(c, x, y, w, h, r); col(c, '140D07', .80*a); c.fill()
    g = cairo.LinearGradient(x, y, x, y+h); g.add_color_stop_rgba(0, *hx(GOLD, .10*a)); g.add_color_stop_rgba(.35, *hx(GOLD, 0)); rr(c, x, y, w, h, r); c.set_source(g); c.fill()
    rr(c, x, y, w, h, r); c.set_line_width(2); col(c, GOLD, .35*a); c.stroke()
def head(c, x, y, k, title, a=1):
    text(c, k, x, y, 'sb', 26, SUB, 'l', a, 3); text(c, title, x, y+50, 'xb', 42, WHITE, 'l', a)
def scrub(c, y, u, a=1):
    rr(c, 140, y-4, 800, 8, 4); col(c, WHITE, .18*a); c.fill(); rr(c, 140, y-4, max(8, 800*u), 8, 4); col(c, ORANGE, a); c.fill()
def caption(c, words, y=1352, size=46, a=1):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, ORANGE, a); c.fill(); text(c, w, x+10, yy, 'b', size, INK, 'l', a)
            else:
                font_ext = (lambda: (nty.font(c, 'b', size), c.font_extents())[1])(); col(c, '000000', .55*a); _path(c, w, x+3, yy+(font_ext[0]-font_ext[1])/2*0.8+4, 'b', size, 0); c.fill()
                text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp
def pizza_icon(c, x, y, s=1.0, a=1):
    """part de pizza générique (dessin original)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-46, -40); c.line_to(46, -40); c.line_to(0, 62); c.close_path(); col(c, 'F2C46B', a); c.fill()
    rr(c, -52, -54, 104, 22, 11); col(c, 'C9853A', a); c.fill()
    for px, py, r in ((-16, -18, 9), (14, -14, 8), (0, 14, 8), (-4, 38, 6)): c.arc(px, py, r, 0, 2*math.pi); col(c, 'C8402F', a); c.fill()
    c.restore()

# trajectoire de 1 000 € placés le 14 oct. 2016 (1,718 BTC), en € ; points mensuels approximatifs (cours $ / change ≈)
def _v(usd, fx=1.12): return 1.718*usd/fx
PATH10 = [(2016.79, 1000), (2017.4, _v(2500)), (2017.96, _v(19000)), (2018.3, _v(8000)), (2018.96, _v(3200)), (2019.5, _v(11000)), (2020.2, _v(5000)),
          (2020.9, _v(19000)), (2021.3, _v(60000)), (2021.55, _v(31000)), (2021.86, _v(67000)), (2022.5, _v(20000)), (2022.88, _v(15800, 1.03)),
          (2023.5, _v(30000)), (2024.2, _v(70000)), (2024.6, _v(55000)), (2024.95, _v(98000, 1.04)), (2025.3, _v(80000)), (2025.77, _v(124000, 1.16)),
          (2026.2, _v(85000)), (2026.5, _v(58566, 1.16)), (2026.79, 127546)]
