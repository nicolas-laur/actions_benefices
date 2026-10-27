"""Couverture Hermès, DA historique de la ligne fil rouge : fond noir, rubans de lumière aux couleurs du sujet (or, champagne, brun),
nom épuré + « Et toi, tu achètes ? », Mister Coin aristocrate (dessin Gemini détouré)."""
import cairo, math, numpy as np, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from PIL import Image, ImageFilter, ImageDraw
import cards_lib as cards
from cards_lib import W, H, hx
def bg(c):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('030405')[:3]); g.add_color_stop_rgb(.5, *hx('05080C')[:3]); g.add_color_stop_rgb(1, *hx('0A1016')[:3]); c.set_source(g); c.paint()
    lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); k = cairo.Context(lay); k.set_operator(cairo.OPERATOR_ADD)
    for (x, y, rx, ry, colr, a) in ((540, 1560, 1150, 70, 'D9A441', .95), (600, 1650, 1100, 45, '7A4E12', .9), (470, 1480, 1000, 38, 'F3D9A0', .6),
                                    (640, 1760, 1200, 80, '3E2708', .6), (560, 1600, 700, 16, 'FFFFFF', .6), (430, 1420, 900, 24, 'FFF0C8', .3)):
        k.save(); k.translate(x, y); k.rotate(-0.42+0.04*((x//10) % 3)); k.scale(rx, ry)
        r = cairo.RadialGradient(0, 0, 0, 0, 0, 1); r.add_color_stop_rgba(0, *hx(colr, a)); r.add_color_stop_rgba(1, *hx(colr, 0)); k.set_source(r); k.arc(0, 0, 1, 0, 2*math.pi); k.fill(); k.restore()
    lay.flush(); im = Image.frombuffer('RGBA', (W, H), bytes(lay.get_data()), 'raw', 'BGRa', lay.get_stride(), 1).filter(ImageFilter.GaussianBlur(28))
    arr = np.asarray(im).astype(np.float32); fade = np.clip((np.arange(H)-700)/700, 0, 1)[:, None, None]; arr[..., :3] *= fade; arr[..., 3] *= fade[..., 0]
    b = Image.fromarray(arr.astype(np.uint8), 'RGBA').tobytes('raw', 'BGRa'); src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H)
    c.set_operator(cairo.OPERATOR_ADD); c.set_source_surface(src); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
cards.bg = bg
for slot, name in ((False, 'couverture.png'), (True, 'couverture_emplacement_logo.png')):
    path = f'{HERE}/{name}'; cards.card("HERMÈS", slot, path)
    if slot: continue
    import rig
    im = Image.open(path).convert('RGBA'); import veo_coin as VC; a, m = VC._key(np.asarray(Image.open(f"{ROOT}/mister_coin/veo/aristocrate_reference_hd.jpg").convert("RGB"))); ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop((0, 0, ch.width, int(ch.height*.86))); ch = ch.crop(ch.getbbox())
    h = 600; ch = ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS); cx, feet = 540, 1770
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.4, feet-16, cx+ch.width*.4, feet+14), fill=170)
    im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(ch, (int(cx-ch.width/2), feet-h)); im.convert('RGB').save(path)
