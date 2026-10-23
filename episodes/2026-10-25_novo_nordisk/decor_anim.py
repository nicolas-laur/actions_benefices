"""Animations des décors du laboratoire (Novo Nordisk) : tapis roulant de stylos, vapeur, voyants, ambiance.
Chaque fonction prend le temps t (s) et renvoie une image RGBA 1080×1920 du décor animé."""
import os, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
D = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

@functools.lru_cache(maxsize=8)
def decor(name):
    """décor Gemini 3:4 recadré en 9:16, avec 8 % de marge pour le travelling"""
    im = Image.open(f'{D}/decors/{name}.png').convert('RGB')
    im = im.resize((int(im.width*1920/im.height), 1920), Image.LANCZOS); x = (im.width-1080)//2
    return im.crop((x, 0, x+1080, 1920))

# ---------- stylo (objet Gemini détouré, bouchon retiré, couché dans l'axe horizontal) ----------
@functools.lru_cache(maxsize=1)
def pen():
    a = np.asarray(Image.open(f'{D}/poses/stylo.png').convert('RGB')).astype(np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = np.clip(1-(ks-25)/70, 0, 1)
    from scipy import ndimage
    lab, n = ndimage.label(al > .5); sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n+1))
    al = al*(lab == 1+np.argmax(sizes))                       # garde le corps du stylo, pas le bouchon
    a[..., 1] = np.where(ks > 0, np.maximum(R, B), G)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((al*255).astype(np.uint8)))
    im = im.crop(im.getbbox()).rotate(-45.7, expand=True, resample=Image.BICUBIC)
    return im.crop(im.getbbox())

# ---------- tapis roulant (salle de production) ----------
V = np.array([700., 820.]); NEAR = np.array([-90., 1062.])
BELT = [(0, 984), (586, 849), (586, 860), (0, 1086)]              # surface du tapis (repérée sur le décor)
@functools.lru_cache(maxsize=1)
def production_base():
    """décor de production sans les stylos dessinés : surface du tapis repeinte"""
    im = decor('production').convert('RGBA'); s = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(s)
    d.polygon(BELT, fill=(132, 156, 163, 255))
    a = np.asarray(s).astype(np.float32); yy, xx = np.mgrid[0:H, 0:W]
    a[..., :3] += (xx/586*16)[..., None]                       # un peu plus clair au loin
    s = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); im.alpha_composite(s)
    d = ImageDraw.Draw(im); d.line([BELT[0], BELT[1]], fill=(20, 24, 26, 255), width=4); d.line([BELT[3], BELT[2]], fill=(20, 24, 26, 255), width=3)
    return im
def belt_mask():
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(BELT, fill=255); return m
BMASK = None
def production(t, speed=1.3):
    global BMASK
    if BMASK is None: BMASK = belt_mask()
    im = production_base().copy(); lay = Image.new('RGBA', (W, H), 0); P = pen()
    off = (t*speed) % 1.0
    for k in range(40, -1, -1):                                # du plus loin au plus proche
        d = k-off; z = 1+d*.42
        if z < .7: continue
        c = V+(NEAR-V)/z; sl_ = .26/z**1.45; sw_ = .21/z
        ang = math.degrees(math.atan2(-(V[1]-c[1]), V[0]-c[0]))
        p = P.resize((max(2, int(P.width*sl_)), max(2, int(P.height*sw_))), Image.BICUBIC).rotate(ang, expand=True, resample=Image.BICUBIC)
        sh = Image.new('RGBA', p.size, (0, 0, 0, 70)); sh.putalpha(p.getchannel('A').point(lambda v: int(v*.3)))
        lay.alpha_composite(sh, (int(c[0]-p.width/2+3), int(c[1]-p.height/2+4)))
        lay.alpha_composite(p, (int(c[0]-p.width/2), int(c[1]-p.height/2)))
        # rayures transversales du tapis qui défilent
    sl = Image.new('RGBA', (W, H), 0); ds = ImageDraw.Draw(sl)
    for k in range(60):
        d = k*.5-((t*speed*2) % 1)*.5; z = 1+d*.62
        if z < .7: continue
        c = V+(NEAR-V)/z; w = 75/z
        ds.line([(c[0]-w*.2, c[1]-w*.55), (c[0]+w*.2, c[1]+w*.55)], fill=(60, 75, 80, int(90/max(1, z*.6))), width=max(1, int(3/z+.5)))
    lay = Image.alpha_composite(sl, lay)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel('A')), np.asarray(BMASK.filter(ImageFilter.GaussianBlur(1))))))
    im.alpha_composite(lay)
    steam(im, t, [(667, 676), (773, 676)])
    blink(im, t, 'production')
    return im

# ---------- vapeur ----------
def steam(im, t, sources):
    lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay); rng = np.random.default_rng(7)
    for sx, sy in sources:
        for i in range(14):
            ph = (t*.35+i/14) % 1; x = sx+rng.uniform(-10, 10)+18*math.sin(t*1.3+i)*ph; y = sy-ph*170; r = 10+28*ph
            d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255, int(95*math.sin(math.pi*ph))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))

# ---------- voyants : les pixels bleu-vert des machines clignotent par blocs ----------
@functools.lru_cache(maxsize=8)
def teal_blocks(name):
    a = np.asarray(decor(name)).astype(np.int32); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = (G > R+35) & (B > R+30) & (G > 110)
    yy, xx = np.mgrid[0:H, 0:W]; zone = (xx > 760) & (yy > 600) & (yy < 1400)
    m &= zone; blocks = (yy//90)*20+(xx//90)
    return m, blocks
def blink(im, t, name):
    m, blocks = teal_blocks(name)
    ph = np.sin(t*4.0+blocks*1.7)
    g = np.where(m, np.clip(ph, 0, 1)*55, 0).astype(np.float32)
    a = np.asarray(im).astype(np.float32); a[..., :3] += g[..., None]*np.array([.4, 1, 1])
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))

# ---------- ambiance commune ----------
def camera(im, t, t0, t1, z0=1.0, z1=1.06, cx=540, cy=900):
    """travelling avant lent sur la durée de la scène"""
    u = clamp((t-t0)/max(.1, t1-t0)); u = u*u*(3-2*u); z = z0+(z1-z0)*u
    w, h = W/z, H/z; box = (cx-w*cx/W, cy-h*cy/H, cx-w*cx/W+w, cy-h*cy/H+h)
    return im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
def atmosphere(im, t, seed=3):
    """néons qui respirent + poussière dans la lumière"""
    k = 1+.018*math.sin(t*1.7)+.008*math.sin(t*5.3)
    im = ImageEnhance.Brightness(im).enhance(k)
    lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay); rng = np.random.default_rng(seed)
    for i in range(70):
        x0, y0, sp = rng.uniform(0, W), rng.uniform(0, H*.75), rng.uniform(6, 18)
        x = (x0+sp*t+12*math.sin(t*.6+i)) % W; y = (y0+6*math.sin(t*.9+i*1.3)) % H; r = rng.uniform(1, 2.6)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255, int(rng.uniform(40, 110))))
    im = im.convert('RGBA'); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(.8))); return im
def reflection(char_layer, floor_y, a=.18):
    """reflet de Mister Coin sur le sol brillant : symétrie verticale sous ses pieds, flou et fondu"""
    r = char_layer.transpose(Image.FLIP_TOP_BOTTOM)
    r = r.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, (H-2*floor_y)), Image.BICUBIC)
    al = np.asarray(r.getchannel('A')).astype(np.float32)
    fade = np.clip(1-(np.arange(H)-floor_y)/260, 0, 1)[:, None]; al *= fade*a; al[:int(floor_y)] = 0
    r.putalpha(Image.fromarray(al.astype(np.uint8))); return r.filter(ImageFilter.GaussianBlur(2.5))
