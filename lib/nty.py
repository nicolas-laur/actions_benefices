"""DA Netflix : salle de projection. Faisceau de projecteur, poussière, grain de film, typographie d'affiche (Anton),
cartes « épisode » d'une plateforme de streaming générique. Aucun logo, aucun « N », aucun visuel de la marque."""
import math, random, sys, cairo
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, __import__('os').path.dirname(__file__))
from mty import hx, col, tw, _path, rr, W, H
import mty
mty.FAM['a'] = ('Anton', 0)
from mty import FAM, font

CRIM = 'E3263B'; DCRIM = '8E0F1E'; GOLD = 'F4B940'; CREAM = 'FFF1DC'; WHITE = 'FFFFFF'; SUB = 'B7A9A0'; INK = '120A0A'; GREEN = '3FD08A'

def text(c, s, x, y, f, size, color=WHITE, align='c', a=1, track=0):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    col(c, color, a); _path(c, s, x0, yy, f, size, track); c.fill(); return w
def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); return s, cairo.Context(s)
def to_img(s):
    s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()

# ---------- fond : salle obscure + faisceau ----------
_base = None
def room():
    """fond fixe : velours sombre, sièges en silhouette, vignette"""
    global _base
    if _base is not None: return _base
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('0A0607')[:3]); g.add_color_stop_rgb(.6, *hx('150709')[:3]); g.add_color_stop_rgb(1, *hx('050304')[:3]); c.set_source(g); c.paint()
    # rideaux de velours sur les côtés (plis verticaux)
    for side in (0, 1):
        for k in range(9):
            x = (k*26 if side == 0 else W-k*26-26); a = .10+.06*math.sin(k*1.7)
            gr = cairo.LinearGradient(x, 0, x+26, 0); gr.add_color_stop_rgba(0, *hx(DCRIM, 0)); gr.add_color_stop_rgba(.5, *hx(DCRIM, a)); gr.add_color_stop_rgba(1, *hx(DCRIM, 0))
            c.set_source(gr); c.rectangle(x, 0, 26, H); c.fill()
    # rangées de fauteuils en silhouette tout en bas
    for row in range(3):
        y = 1720+row*70; col(c, '000000', .55+row*.15)
        for i in range(-1, 12):
            x = i*100+(50 if row % 2 else 0); rr(c, x, y, 86, 140, 30); c.fill()
    im = to_img(s)
    _base = im; return im

_beam = None
def beam(t, a=1.0):
    """faisceau du projecteur depuis le haut, légèrement vacillant, avec poussière qui dérive"""
    global _beam
    if _beam is None:
        s, c = surface()
        c.move_to(540-40, -20); c.line_to(540+40, -20); c.line_to(540+560, 1250); c.line_to(540-560, 1250); c.close_path()
        g = cairo.LinearGradient(0, 0, 0, 1250); g.add_color_stop_rgba(0, *hx(CREAM, .22)); g.add_color_stop_rgba(.55, *hx(CREAM, .07)); g.add_color_stop_rgba(1, *hx(CREAM, 0))
        c.set_source(g); c.fill()
        _beam = np.asarray(to_img(s).filter(ImageFilter.GaussianBlur(28))).copy()
    flick = 1+.04*math.sin(t*23.0)+.03*math.sin(t*7.3)
    b = _beam.copy(); b[..., 3] = np.clip(b[..., 3].astype(np.float32)*a*flick, 0, 255).astype(np.uint8)
    im = Image.fromarray(b, 'RGBA')
    s, c = surface(); rnd = random.Random(7)
    for k in range(140):
        x0, y0, sp, r = rnd.uniform(0, W), rnd.uniform(0, 1300), rnd.uniform(6, 22), rnd.uniform(1.0, 2.8)
        y = (y0+t*sp) % 1300; x = x0+14*math.sin(t*.5+k)
        inside = max(0, 1-abs(x-540)/(60+0.44*y))
        if inside <= 0: continue
        col(c, CREAM, .55*inside*a*(1-y/1300)); c.arc(x, y, r, 0, 2*math.pi); c.fill()
    im.alpha_composite(to_img(s)); return im

_grain = None
def grain(t):
    global _grain
    if _grain is None:
        rnd = np.random.default_rng(1); _grain = [rnd.normal(0, 1, (H//2, W//2)).astype(np.float32) for _ in range(6)]
    return _grain[int(t*24) % 6]
_v = None
def _vig():
    global _v
    if _v is None:
        yy, xx = np.mgrid[0:H, 0:W]; _v = (1-.42*np.clip(((xx-540)/760)**2+((yy-900)/1250)**2, 0, 1)).astype(np.float32)[:, :, None]
    return _v
def finish(im, t, strength=7.0):
    """grain de film + vignette, appliqué à l'image RGB finale"""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    g = np.repeat(np.repeat(grain(t), 2, 0), 2, 1)[:, :, None]
    a = np.clip(a*_vig()+g*strength, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGB')

def glow(draw, radius=(44, 14), strength=(2.2, 1.6), core=True):
    s, c = surface(); draw(c); im = to_img(s)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for r, k in zip(radius, strength):
        b = im.filter(ImageFilter.GaussianBlur(r)); a = np.asarray(b).astype(np.float32); a[..., 3] = np.clip(a[..., 3]*k, 0, 255)
        out.alpha_composite(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    if core: out.alpha_composite(im)
    return out

# ---------- éléments ----------
def tag(c, s, x, y, color=CRIM, size=28, fg=WHITE, a=1):
    w = tw(c, s, 'xb', size, 2)+44; rr(c, x-w/2, y-26, w, 52, 8); col(c, color, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2); return w
def pill(c, s, y, color=CRIM, a=1):
    w = tw(c, s, 'xb', 34)+70; rr(c, 540-w/2, y-38, w, 76, 38); col(c, color, a); c.fill(); text(c, s, 540, y, 'xb', 34, WHITE, 'c', a)
def ep_card(c, x, y, w, h, a=1):
    """carte « épisode » de plateforme générique : verre sombre, liseré"""
    rr(c, x, y, w, h, 28); col(c, '1A0D0F', .78*a); c.fill()
    g = cairo.LinearGradient(x, y, x, y+h); g.add_color_stop_rgba(0, 1, 1, 1, .07*a); g.add_color_stop_rgba(.3, 1, 1, 1, 0); rr(c, x, y, w, h, 28); c.set_source(g); c.fill()
    rr(c, x, y, w, h, 28); c.set_line_width(2); col(c, WHITE, .14*a); c.stroke()
def ep_head(c, x, y, ep, title, a=1):
    text(c, ep, x, y, 'sb', 26, SUB, 'l', a, 3); text(c, title, x, y+50, 'xb', 42, WHITE, 'l', a)
def scrub(c, y, u, a=1, x0=140, x1=940, color=CRIM):
    """barre de lecture"""
    rr(c, x0, y-4, x1-x0, 8, 4); col(c, WHITE, .2*a); c.fill()
    rr(c, x0, y-4, max(8, (x1-x0)*u), 8, 4); col(c, color, a); c.fill()
    c.arc(x0+(x1-x0)*u, y, 13, 0, 2*math.pi); col(c, WHITE, a); c.fill()
def caption(c, words, y=1352, size=46, accent=CRIM, a=1):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, accent, a); c.fill(); text(c, w, x+10, yy, 'b', size, WHITE, 'l', a)
            else:
                col(c, '000000', .55*a); _path(c, w, x+3, yy+(c.font_extents()[0]-c.font_extents()[1])/2*0.8+4, 'b', size, 0); c.fill()
                text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp
