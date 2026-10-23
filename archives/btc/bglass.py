"""Verre 3D (recette Microsoft) adapté au Bitcoin : panneaux de verre en perspective, dépoli sur le fond, ombre, texte lumineux doré avec reflet."""
import math, sys, cairo, functools
import numpy as np
from PIL import Image, ImageFilter, ImageChops
sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/msft')
from glass import coeffs, tilt_quad
from bty import *
from nty import _path
import nty
from PIL import ImageEnhance

def surf(w, h): s = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h)); return s, cairo.Context(s)
def pil(s):
    s.flush(); return Image.frombuffer('RGBA', (s.get_width(), s.get_height()), bytes(s.get_data()), 'raw', 'BGRa', s.get_stride(), 1).copy()
def lowblur(im, radius, f=4):
    w, h = im.size; return im.resize((w//f, h//f), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius/f)).resize((w, h), Image.BILINEAR)
def with_alpha(img, a):
    if a >= 0.999: return img
    im = img.copy(); im.putalpha(im.split()[3].point(lambda v: int(v*a))); return im
def place(cv, panel, quad, a=1.0, frost=24, shadow=0.5, dof=0.0):
    """pose un panneau de verre en perspective : ombre portée, dépoli du fond derrière, panneau"""
    if a <= 0.01: return
    w, h = panel.size; cf = coeffs(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    warped = with_alpha(panel, a).transform((W, H), Image.PERSPECTIVE, cf, Image.BICUBIC)
    m = warped.split()[3].point(lambda v: 255 if v > 6 else 0)
    if shadow > 0:
        sh = lowblur(m.convert('RGBA'), 40).split()[0]; sh = ImageChops.offset(sh, 0, 30).point(lambda v: int(v*shadow*a))
        cv.paste((8, 4, 0, 255), (0, 0), sh)
    if frost > 0:
        cv.paste(lowblur(cv, frost), (0, 0), m.point(lambda v: int(v*a)))
    if dof > 0: warped = lowblur(warped, dof, 2)
    cv.alpha_composite(warped)
def gpanel(w, h, draw=None, r=36, ta=0.10, edge=0.65, tint='FFE2A8'):
    """verre teinté or : remplissage dégradé, reflet diagonal, liseré lumineux"""
    s, c = surf(w, h)
    rr(c, 1, 1, w-2, h-2, r); g = cairo.LinearGradient(0, 0, w*.6, h); g.add_color_stop_rgba(0, *hx(tint, ta*1.8)); g.add_color_stop_rgba(1, *hx('1A0F05', .55)); c.set_source(g); c.fill()
    c.save(); rr(c, 1, 1, w-2, h-2, r); c.clip(); g2 = cairo.LinearGradient(0, 0, w, h*.7)
    for o, v in ((0, 0), (.32, 0), (.38, .10), (.46, 0)): g2.add_color_stop_rgba(o, 1, 1, 1, v)
    c.set_source(g2); c.paint(); c.restore()
    rr(c, 1.5, 1.5, w-3, h-3, r); g3 = cairo.LinearGradient(0, 0, w, h)
    for o, v in ((0, edge), (.5, edge*.25), (1, edge*.6)): g3.add_color_stop_rgba(o, *hx(tint, v))
    c.set_source(g3); c.set_line_width(2.4); c.stroke()
    if draw: draw(c, w, h)
    return pil(s)
_GT = {}
def glow_text(cv, s, x, y, size, top='FFF0C8', bottom='F5A623', glow='F7931A', ga=0.85, a=1.0, scale=1.0, reflect=True, track=0, fam='a'):
    """grand chiffre à dégradé, halo et reflet"""
    if a <= 0.01: return
    key = (s, size, top, bottom, glow, reflect, fam)
    if key not in _GT:
        k = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4))
        pad = int(size*0.6); w = int(tw(k, s, fam, size, track))+2*pad; h = int(size*2.2)
        S, c = surf(w, h); nty.font(c, fam, size)
        asc, desc = c.font_extents()[:2]; cy = h*0.38; yy = cy+(asc-desc)/2*0.8
        _path(c, s, pad, yy, fam, size, track)
        g = cairo.LinearGradient(0, cy-size*.45, 0, cy+size*.4); g.add_color_stop_rgb(0, *hx(top)[:3]); g.add_color_stop_rgb(1, *hx(bottom)[:3]); c.set_source(g); c.fill()
        im = pil(S); al = im.split()[3]
        gl = Image.new('RGBA', im.size, tuple(int(v*255) for v in hx(glow)[:3])+(0,)); gl.putalpha(lowblur(al.convert('RGBA'), size*.2, 2).split()[0].point(lambda v: int(v*ga)))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(gl)
        if reflect:
            top_ = int(yy-asc*0.78); bot = int(yy+desc*0.3); band = im.crop((0, top_, w, bot)).transpose(Image.FLIP_TOP_BOTTOM)
            grad = np.linspace(0.18, 0, band.size[1])[:, None]; aa = (np.asarray(band.split()[3]).astype(float)*grad).astype(np.uint8)
            band.putalpha(Image.fromarray(aa)); out.alpha_composite(band.filter(ImageFilter.GaussianBlur(3)), (0, min(h-band.size[1], bot+6)))
        out.alpha_composite(im); _GT[key] = (out, cy)
    img, cy = _GT[key]
    if scale != 1.0: img = img.resize((max(1, int(img.width*scale)), max(1, int(img.height*scale))), Image.BILINEAR); cy *= scale
    img = with_alpha(img, a); cv.alpha_composite(img, (int(x-img.width/2), int(y-cy)))

def rain_bg(path, dim=0.85, blur=0):
    im = Image.open(path).convert('RGB').resize((W, H), Image.LANCZOS)
    if blur: im = lowblur(im, blur, 2)
    if dim != 1: im = ImageEnhance.Brightness(im).enhance(dim)
    return im.convert('RGBA')
def darken_band(cv, y0, y1, a=.55):
    """voile sombre derrière les sous-titres pour la lisibilité"""
    s, c = surface(); g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(.5, 0, 0, 0, a); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.rectangle(0, y0, W, y1-y0); c.set_source(g); c.fill(); cv.alpha_composite(to_img(s))

def darkspot(cv, cx, cy, rx, ry, a=.6):
    """assombrissement doux derrière le contenu"""
    s, c = surface(); c.save(); c.translate(cx, cy); c.scale(rx, ry)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, 0, 0, 0, a); g.add_color_stop_rgba(.6, 0, 0, 0, a*.6); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore(); cv.alpha_composite(to_img(s))
