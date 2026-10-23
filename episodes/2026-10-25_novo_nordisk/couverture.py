"""Couverture Novo Nordisk : salle de contrôle floutée, titre de la ligne fil rouge, Mister Coin mince et abattu."""
import cairo, numpy as np, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin'); sys.path.insert(0, HERE)
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import cards_lib as cards
from cards_lib import W, H, hx, put, fit
import decor_anim as A
def bg(c):
    im = A.decor('controle').filter(ImageFilter.GaussianBlur(7)); im = ImageEnhance.Brightness(im).enhance(.42)
    a = np.asarray(im).astype(np.float32)*[.85, 1.0, 1.0]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    src = cairo.ImageSurface.create_for_data(bytearray(im.tobytes('raw', 'BGRa')), cairo.FORMAT_ARGB32, W, H, W*4); c.set_source_surface(src); c.paint()
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); bg(c)
sz = fit(c, "NOVO NORDISK", "Poppins Medium", 92, 10, 900); put(c, "NOVO NORDISK", 760, "Poppins Medium", sz, 'FFFFFF', 10)
c.move_to(500, 820); c.line_to(580, 820); c.set_source_rgba(*hx('FFFFFF', .5)); c.set_line_width(2); c.stroke()
put(c, "Et toi, tu achètes ?", 950, "Poppins Light", 58, 'FFFFFF', 1)
path = f'{HERE}/couverture.png'; s.write_to_png(path)
import rig
im = Image.open(path).convert('RGBA'); ch = rig.character('mince_abattu', 0, False, 0, 0, 0); ch = ch.crop(ch.getbbox())
h = 620; ch = ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS); cx, feet = 540, 1690
sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.4, feet-16, cx+ch.width*.4, feet+14), fill=150)
im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
gl = Image.new('L', (W, H), 0); ImageDraw.Draw(gl).ellipse((cx-260, feet-h*.95, cx+260, feet-h*.3), fill=55)
im.paste((80, 220, 210, 255), (0, 0), gl.filter(ImageFilter.GaussianBlur(90)))
im.alpha_composite(ch, (int(cx-ch.width/2), feet-h)); im.convert('RGB').save(path)
