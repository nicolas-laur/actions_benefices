"""DA McDonald's v2 : néon de nuit. Fond sombre chaud avec bokeh, chiffres en tubes néon, borne en verre, ticket papier éclairé."""
import math, random, cairo
import numpy as np
from PIL import Image, ImageFilter
from mty import hx, col, FAM, font, tw, _path, rr, W, H
YEL = 'FFC72C'; RED = 'FF3B2F'; DRED = 'C8160B'; INK = '1D1D1B'; CREAM = 'FFF6E3'; GREEN = '35D07F'; WHITE = 'FFFFFF'; SUB = 'B9A89A'
def text(c, s, x, y, f, size, color=WHITE, align='c', a=1, track=0):
    w = tw(c, s, f, size, track); x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    asc, desc = c.font_extents()[:2]; yy = y+(asc-desc)/2*0.8
    col(c, color, a); _path(c, s, x0, yy, f, size, track); c.fill(); return w
def to_img(s):
    s.flush(); return Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
def surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); return s, cairo.Context(s)

_bok = None
def bokeh_layer():
    """fond : nuit chaude, lumières floues de restaurant (calculé une fois)"""
    global _bok
    if _bok is not None: return _bok
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('0B0504')[:3]); g.add_color_stop_rgb(.55, *hx('1A0806')[:3]); g.add_color_stop_rgb(1, *hx('070303')[:3]); c.set_source(g); c.paint()
    rnd = random.Random(5)
    for k in range(70):
        x, y = rnd.uniform(-50, W+50), rnd.uniform(0, H); r = rnd.uniform(20, 90); cc = rnd.choice([YEL, YEL, 'FF8A3D', RED, 'FFE3A0'])
        gr = cairo.RadialGradient(x, y, 0, x, y, r); gr.add_color_stop_rgba(0, *hx(cc, rnd.uniform(.08, .28))); gr.add_color_stop_rgba(.7, *hx(cc, rnd.uniform(.05, .15))); gr.add_color_stop_rgba(1, *hx(cc, 0))
        c.set_source(gr); c.arc(x, y, r, 0, 2*math.pi); c.fill()
    im = to_img(s).filter(ImageFilter.GaussianBlur(14))
    _bok = im; return im
def glow_layer(draw, radius=(50, 18, 6), strength=(3.4, 2.6, 1.6)):
    """dessine un élément néon : halo large + halo serré + cœur net"""
    s, c = surface(); draw(c); core = to_img(s)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for r, k in zip(radius, strength):
        b = core.filter(ImageFilter.GaussianBlur(r)); a = np.asarray(b).astype(np.float32); a[..., 3] = np.clip(a[..., 3]*k, 0, 255)
        out.alpha_composite(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    out.alpha_composite(core); return out
def neon_text(s, x, y, size, color, f='k', track=0):
    def d(c):
        text(c, s, x, y, f, size, color, 'c', 1, track)
        # reflet blanc au cœur du tube
        c.save(); text(c, s, x, y, f, size, 'FFFFFF', 'c', .18, track); c.restore()
    return glow_layer(d)
def glass_panel(c, x, y, w, h, r=34, tint='FFFFFF', a=.07):
    rr(c, x, y, w, h, r); col(c, tint, a); c.fill()
    g = cairo.LinearGradient(x, y, x+w*.6, y+h); g.add_color_stop_rgba(0, 1, 1, 1, .16); g.add_color_stop_rgba(.35, 1, 1, 1, .03); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    rr(c, x, y, w, h, r); c.set_source(g); c.fill()
    rr(c, x, y, w, h, r); c.set_line_width(2); col(c, 'FFFFFF', .22); c.stroke()
def kiosk_row(c, y, title, detail, price, color, icon, a=1.0):
    c.push_group()
    glass_panel(c, 110, y, 860, 150, 26, 'FFFFFF', .06)
    c.arc(190, y+75, 46, 0, 2*math.pi); col(c, color, .18); c.fill()
    c.set_line_width(7); c.set_line_cap(1); c.set_line_join(1); col(c, color)
    if icon == 'down': c.move_to(160, y+55); c.line_to(185, y+80); c.line_to(200, y+68); c.line_to(222, y+95); c.stroke(); c.move_to(206, y+97); c.line_to(222, y+95); c.line_to(220, y+79); c.stroke()
    elif icon == 'people':
        for dx in (-16, 16): c.arc(190+dx, y+62, 10, 0, 2*math.pi); c.fill(); c.arc(190+dx, y+102, 18, math.pi, 2*math.pi); c.fill()
    elif icon == 'flat': c.move_to(158, y+80); c.line_to(222, y+76); c.stroke()
    elif icon == 'coin': c.arc(190, y+75, 26, 0, 2*math.pi); c.stroke(); text(c, "€", 190, y+77, 'k', 34, color)
    text(c, title, 265, y+52, 'xb', 36, WHITE, 'l'); text(c, detail, 265, y+102, 'm', 28, SUB, 'l')
    text(c, price, 935, y+75, 'k', 48, color, 'r')
    c.pop_group_to_source(); c.paint_with_alpha(a)
def paper_texture():
    rnd = np.random.default_rng(3); n = rnd.normal(0, 1, (H//4, W//4)).astype(np.float32)
    im = Image.fromarray(np.clip(128+n*10, 0, 255).astype(np.uint8), 'L').resize((W, H), Image.BICUBIC); return im
_paper = None
def receipt_img(u=1.0, x=190, w=700, top=330):
    """ticket imprimé : papier texturé, ombre portée, éclairage chaud rasant"""
    global _paper
    if _paper is None: _paper = paper_texture()
    hmax = 880; s, c = surface()
    c.rectangle(x, top, w, hmax); col(c, 'FFF9EC'); c.fill()
    for i in range(0, w, 28): c.move_to(x+i, top+hmax); c.line_to(x+i+14, top+hmax+16); c.line_to(x+i+28, top+hmax); c.fill()
    y = top+70
    def T(sv, xx, yy, f, size, cc, al='c'): text(c, sv, xx, yy, f, size, cc, al)
    T("TICKET · 5 ANS DE BOURSE", x+w/2, y, 'mono', 26, INK); y += 50
    c.set_dash([6, 6]); c.set_line_width(2); col(c, INK, .5); c.move_to(x+40, y); c.line_to(x+w-40, y); c.stroke(); c.set_dash([]); y += 60
    for lab, val, cc in (("Mise de départ", "1 000 €", INK), ("Action (5 ans)", "+4 €", INK), ("Dividendes reçus", "+140 €", '128A4C')):
        T(lab, x+50, y, 'mono', 28, INK, 'l'); T(val, x+w-50, y, 'mono', 30, cc, 'r'); y += 62
    c.set_dash([6, 6]); col(c, INK, .5); c.move_to(x+40, y); c.line_to(x+w-40, y); c.stroke(); c.set_dash([]); y += 80
    T("TOTAL", x+50, y, 'k', 44, INK, 'l'); T("≈ 1 143 €", x+w-50, y, 'k', 60, DRED, 'r'); y += 80
    T("×1,14 en 5 ans", x+w/2, y, 'xb', 36, INK); y += 70
    T("change €/$ inclus · dividendes bruts", x+w/2, y, 'mono', 20, '6B6B6B'); y += 34
    T("avant impôts et frais", x+w/2, y, 'mono', 20, '6B6B6B'); y += 70
    for i in range(46): bw = [3, 6, 2, 4][i*7 % 4]; c.rectangle(x+120+i*10, y, bw, 70); col(c, INK); c.fill()
    im = to_img(s)
    # texture papier + dégradé de lumière chaude (haut éclairé, bas plus sombre)
    a = np.asarray(im).astype(np.float32); tex = (np.asarray(_paper).astype(np.float32)-128)/128
    yy = np.linspace(0, 1, H)[:, None]; light = 1.04-0.22*np.clip((yy*H-top)/hmax, 0, 1)
    for k in range(3): a[..., k] = np.clip(a[..., k]*(light+tex*0.04), 0, 255)
    a[..., 0] = np.clip(a[..., 0]*1.0, 0, 255); a[..., 2] = np.clip(a[..., 2]*0.93, 0, 255)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    # impression progressive
    mask = Image.new('L', (W, H), 0); m = cairo.ImageSurface(cairo.FORMAT_A8, W, H)
    hh = int(top+(hmax+20)*u); arr = np.zeros((H, W), np.uint8); arr[:hh, :] = 255; im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel('A')), arr)))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sa = np.zeros((H, W), np.uint8); sa[top+30:min(hh, top+hmax)+40, x+30:x+w+30] = 150
    sh.putalpha(Image.fromarray(sa).filter(ImageFilter.GaussianBlur(24)))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(im); return out
def caption(c, words, y=1352, size=46, accent=YEL):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, accent); c.fill(); text(c, w, x+10, yy, 'b', size, INK, 'l')
            else: text(c, w, x, yy, 'b', size, WHITE, 'l')
            x += wd[i]+sp
def progress(c, u):
    col(c, WHITE, .15); rr(c, 140, 260, 800, 6, 3); c.fill(); col(c, YEL); rr(c, 140, 260, max(6, 800*u), 6, 3); c.fill()
