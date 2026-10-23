"""DA SpaceX « décollage cinéma » : ciel qui passe du crépuscule à l'espace, flamme et fumée procédurales en 2D, fusée 3D originale."""
import math, random, sys, functools
import numpy as np, cairo
from PIL import Image, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/mu')
from bglass import *
NB = ' '
FIRE = 'FF8A2A'; HOT = 'FFD27A'; ICE = 'DDEBFF'; SUBC = 'A9B6CC'; INKB = '0A0D14'; CYN = '35D6FF'; RED_ = 'FF4D5E'; GRN = '3FD08A'

def _noise(n=512, oct_=5, seed=1):
    rng = np.random.default_rng(seed); out = np.zeros((n, n), np.float32); amp = 1.0; tot = 0
    for o in range(oct_):
        k = 4*2**o; g = rng.random((k, k)).astype(np.float32)
        im = Image.fromarray((g*255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += amp*np.asarray(im, np.float32)/255; tot += amp; amp *= .5
    out /= tot; return (out-out.min())/(out.max()-out.min())
NZ = _noise(); NZ2 = _noise(seed=7)

def sky(t, alt):
    """alt 0 = crépuscule au sol, 1 = espace"""
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H)
    top = [lerp_c('0B1530', '010205', alt)]; mid = lerp_c('1B2A55', '03050C', alt); bot = lerp_c('C2562A', '06070E', min(1, alt*1.6))
    g.add_color_stop_rgb(0, *hx(top[0])[:3]); g.add_color_stop_rgb(.62, *hx(mid)[:3]); g.add_color_stop_rgb(1, *hx(bot)[:3]); c.set_source(g); c.paint()
    rnd = random.Random(3)
    for k in range(260):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(.6, 2.2); tw_ = .6+.4*math.sin(t*rnd.uniform(1, 4)+k)
        col(c, 'FFFFFF', (.15+.75*alt)*rnd.uniform(.3, 1)*tw_); c.arc(x, y, r, 0, 2*math.pi); c.fill()
    return to_img(s)
def lerp_c(a, b, u):
    u = max(0, min(1, u)); A, B = hx(a), hx(b); return ''.join(f'{int((A[i]+(B[i]-A[i])*u)*255):02X}' for i in range(3))

def clouds(t, alt, speed=1.0):
    """bancs de nuages qui défilent vers le bas pendant l'ascension (disparaissent en altitude)"""
    a = max(0, 1-alt*1.4)
    if a <= 0: return None
    n = NZ; off = int((t*120*speed)) % 512
    band = np.roll(n, off, axis=0); band2 = np.roll(NZ2, off*2 % 512, axis=0)
    m = np.clip((band*.6+band2*.4-.5)*3.2, 0, 1)
    im = Image.fromarray((m*255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    rgb = Image.new('RGB', (W, H), (150, 140, 160)); out = rgb.convert('RGBA'); out.putalpha(im.point(lambda v: int(v*.55*a)))
    return out

def flame(t, power=1.0, length=900, width=230):
    """flamme procédurale : cœur blanc, jaune, orange, bords qui ondulent (bruit qui défile)"""
    h, w = int(length/2), int(width)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); v = yy/h; u = (xx-w/2)/(w/2)
    off = int(t*900) % 512; nz = np.roll(NZ, off, axis=0)[:h, :w] if w <= 512 else None
    nz = np.asarray(Image.fromarray((np.roll(NZ, off, axis=0)*255).astype(np.uint8)).resize((w, h)), np.float32)/255
    wid = (.32+.68*np.sin(np.pi*np.clip(v*1.5+.08, 0, 1)))*(1-v)**.5   # largeur le long de la flamme
    wob = (nz-.5)*.35*v
    d = np.abs(u+wob)/np.maximum(wid, 1e-3)
    core = np.clip(1-d, 0, 1)**1.2*(1-v)**1.4
    body = np.clip(1-d*.8, 0, 1)*(1-v)**.9*(.65+.5*nz)
    inten = np.clip((core*1.4+body)*power, 0, 1.6)
    r = np.clip(inten*1.4, 0, 1); g = np.clip(inten*1.05-.1, 0, 1); b = np.clip(inten*1.4-.95, 0, 1)
    al = np.clip(inten*1.2, 0, 1)
    arr = np.dstack([r, g, b, al])*255
    im = Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((w, length), Image.BICUBIC)
    glow_ = im.filter(ImageFilter.GaussianBlur(24)); out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(glow_); out.alpha_composite(glow_); out.alpha_composite(im)
    return out

def smoke(t, cx, top_y, alt, power=1.0):
    """panache de fumée en volutes : bruit grossier seuillé + ombrage, éclairé en orange près de la flamme"""
    h = H-int(top_y)
    if h <= 20 or power <= 0: return None
    sw, sh = W//4, max(8, h//4)
    off = int(t*90) % 512
    big = np.roll(NZ2, -off, axis=0); big2 = np.roll(NZ, -int(t*55) % 512, axis=1)
    def samp(a, zoom): return np.asarray(Image.fromarray((a[:int(512/zoom), :int(512/zoom)]*255).astype(np.uint8)).resize((sw, sh), Image.BICUBIC), np.float32)/255
    n1 = samp(big, 3.0); n2 = samp(big2, 1.6); n = n1*.65+n2*.35
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32); v = yy/sh; u = (xx*4-cx)/(110+v*1500)
    shape = np.clip(1.2-np.abs(u), 0, 1)*np.clip(v*6, 0, 1)
    dens = np.clip((n*1.2+shape*1.1-.95)*2.6, 0, 1)*shape**.3*power*max(0, 1-alt*1.3)
    shade = np.clip(.85+1.8*(n-np.roll(n, 3, axis=0)), .35, 1.25)
    lit = np.exp(-v*2.5)
    r = np.clip(shade*(.72+.5*lit), 0, 1); g = np.clip(shade*(.68+.18*lit), 0, 1); b = np.clip(shade*(.70-.2*lit), 0, 1)
    arr = np.dstack([r, g, b, np.clip(dens*1.1, 0, 1)])
    im = Image.fromarray((arr*255).astype(np.uint8), 'RGBA').resize((W, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(im, (0, int(top_y))); return out

@functools.lru_cache(maxsize=4)
def rocket_img(scale):
    im = Image.open('/home/claude/spcx/rocket_still.png').convert('RGBA')
    return im.resize((int(im.width*scale), int(im.height*scale)), Image.LANCZOS)
NOZ = (300, 990)   # tuyère dans le rendu 600x1200
def put_rocket(cv, t, cx, cy, scale=.8, angle=0.0, power=1.0, shake=1.0, a=1.0):
    """pose la fusée (tuyère en cx, cy), avec flamme et vibration"""
    jx = shake*2.2*math.sin(t*61)*power; jy = shake*1.6*math.cos(t*47)*power
    r = rocket_img(scale); nx, ny = NOZ[0]*scale, NOZ[1]*scale
    if power > .02:
        fl = flame(t, power, int(1250*scale*power**.5), int(300*scale))
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(fl, (int(cx-fl.width/2+jx), int(cy-12*scale+jy)))
        if angle: layer = layer.rotate(-angle, center=(cx, cy), resample=Image.BILINEAR)
        cv.alpha_composite(with_alpha(layer, a))
        # halo lumineux autour de la tuyère
        s, c = surface(); g = cairo.RadialGradient(cx, cy+60*scale, 0, cx, cy+60*scale, 420*scale); g.add_color_stop_rgba(0, *hx(FIRE, .45*power)); g.add_color_stop_rgba(1, *hx(FIRE, 0))
        c.set_source(g); c.paint(); cv.alpha_composite(with_alpha(to_img(s), a))
    if power > .02:
        r = r.copy(); a_ = np.asarray(r).astype(np.float32); hh = a_.shape[0]
        k_ = np.clip((np.arange(hh)/hh-.45)/.4, 0, 1)[:, None]**1.6*power
        a_[..., 0] = np.clip(a_[..., 0]+k_*120, 0, 255); a_[..., 1] = np.clip(a_[..., 1]+k_*40, 0, 255); a_[..., 2] = np.clip(a_[..., 2]-k_*30, 0, 255)
        r = Image.fromarray(a_.astype(np.uint8), 'RGBA')
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(r, (int(cx-nx+jx), int(cy-ny+jy)))
    if angle: layer = layer.rotate(-angle, center=(cx, cy), resample=Image.BICUBIC)
    cv.alpha_composite(with_alpha(layer, a))

def spanel(w, h, draw=None, r=36): return gpanel(w, h, draw, r, ta=.09, edge=.7, tint='DDEBFF')
def gtw(cv, s, x, y, size, **k):
    kw = dict(top='FFFFFF', bottom='FFC27A', glow=FIRE, ga=.7); kw.update(k); glow_text(cv, s, x, y, size, **kw)
def capw(c, words, y=1352, size=46, a=1):
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
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, FIRE, a); c.fill(); text(c, w, x+10, yy, 'b', size, INKB, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp
def sbar(c, u):
    rr(c, 140, 146, 800, 8, 4); col(c, WHITE, .18); c.fill(); rr(c, 140, 146, max(8, 800*u), 8, 4); col(c, FIRE); c.fill()

def trail(c, pts, color=HOT, a=1.0):
    """traînée de condensation qui suit la courbe : large voile flou + cœur lumineux"""
    for a_, lw in ((.05, 90), (.08, 50), (.18, 22), (1, 7)):
        c.move_to(*pts[0])
        for q in pts[1:]: c.line_to(*q)
        c.set_line_width(lw); c.set_line_join(1); c.set_line_cap(1); col(c, color if lw < 30 else 'FFFFFF', a_*a); c.stroke()
