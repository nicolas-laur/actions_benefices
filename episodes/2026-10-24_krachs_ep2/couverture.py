"""Couverture Krachs ép. 2 : ciel d'orage cartoon flouté et assombri, titre de la série, Mister Coin abattu en bas."""
import cairo, numpy as np, sys, math
import os; HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); sys.path.insert(0, f'{ROOT}/mister_coin'); sys.path.insert(0, f'{ROOT}/lib')
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import cards_lib as cards
from cards_lib import W, H, hx, put, fit
def bg(c):
    im = Image.open(f'{HERE}/decors/ciel.jpg').convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(7))
    im = ImageEnhance.Brightness(im).enhance(.5)
    yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt(((xx-W/2)/(W*.55))**2+((yy-H*.42)/(H*.30))**2)
    a = np.asarray(im).astype(np.float32)*(1-.55*np.clip(1.15-d, 0, 1))[..., None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')
    src = cairo.ImageSurface.create_for_data(bytearray(im.tobytes('raw', 'BGRa')), cairo.FORMAT_ARGB32, W, H, W*4); c.set_source_surface(src); c.paint()
def make(path, tagline="Et toi, tu aurais tenu 15 ans ?"):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); bg(c)
    put(c, "KRACHS · ÉPISODE 2", 640, "Poppins Medium", 30, 'FFFFFF', 8, .7)
    name = "BULLE INTERNET 2000"; sz = fit(c, name, "Poppins Medium", 80, 8, 940); put(c, name, 760, "Poppins Medium", sz, 'FFFFFF', 8)
    c.move_to(500, 820); c.line_to(580, 820); c.set_source_rgba(*hx('FFFFFF', .5)); c.set_line_width(2); c.stroke()
    put(c, tagline, 950, "Poppins Light", 54, 'FFFFFF', 1)
    s.write_to_png(path)
    im = Image.open(path).convert('RGBA')
    import rig, puppet as P
    ch = rig.character('abattu', 0, False, 0, 0, 0); ch = ch.crop(ch.getbbox()); h = 640; ch = ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS)
    cx, feet = 560, 1680
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.32, feet-16, cx+ch.width*.32, feet+14), fill=150)
    im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    gl = Image.new('L', (W, H), 0); ImageDraw.Draw(gl).ellipse((cx-ch.width*.45, feet-h*.95, cx+ch.width*.45, feet-h*.3), fill=60)
    im.paste((255, 190, 80, 255), (0, 0), gl.filter(ImageFilter.GaussianBlur(90)))
    im.alpha_composite(ch, (int(cx-ch.width*.53), feet-h)); im.convert('RGB').save(path)
make(f'{HERE}/couverture.png')
