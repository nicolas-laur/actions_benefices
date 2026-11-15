"""Couverture du Loto (style maison, comme « millionnaire ») : scène de tirage assombrie en haut, titre « LE LOTO » + « OU LE PLACEMENT ? »,
question « Tu joues au Loto ? », Mister Coin qui rit en bas, entouré de boules (blanches numérotées et rouges)."""
import cairo, math, numpy as np, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import cards_lib as cards
from cards_lib import W, H
TMP = f'{HERE}/tmp'; os.makedirs(TMP, exist_ok=True)
def still(src, n, dst):
    if not os.path.exists(dst):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', f'select=eq(n\\,{n})', '-vframes', '1', dst], check=True)
    return Image.open(dst).convert('RGB')
def bg(c):
    d = still(f'{HERE}/decors/sr/decor_tirage.mp4', 150, f'{TMP}/tirage_couv.png').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.72, .6, .55, .2, .35])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2); dark = np.clip(dark+.25*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Et toi, tu joues au Loto ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
path = f'{HERE}/couverture.png'; cards.card("LE LOTO", False, path, sub=("OU LE PLACEMENT ?",))
im = Image.open(path).convert('RGBA')
# boules autour de Mister Coin
FB = ImageFont.truetype(f'{ROOT}/fonts/AlfaSlabOne-Regular.ttf', 64)
def ball(name, x, y, h, num=None, rot=0):
    b = Image.open(f'{HERE}/props/{name}.png').convert('RGBA'); b = b.resize((int(b.width*h/b.height), h), Image.LANCZOS)
    if num:
        d = ImageDraw.Draw(b); d.text((b.width/2, b.height/2-4), num, font=FB.font_variant(size=int(h*.27)), anchor='mm', fill=(59, 36, 18))
    b = b.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', b.size, (0, 0, 0, 0)); sh.putalpha(b.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v*.45)))
    im.alpha_composite(sh, (int(x-b.width/2)+8, int(y-b.height/2)+12)); im.alpha_composite(b, (int(x-b.width/2), int(y-b.height/2)))
for (x, y, n, r) in ((150, 1290, "7", -8), (930, 1270, "42", 10), (110, 1560, "19", 6), (975, 1540, "13", -6)):
    ball('boule_loto', x, y, 150, n, r)
# Mister Coin qui rit
cap = subprocess.run
a, m = VC._key(np.asarray(still(f'{ROOT}/mister_coin/veo/classique_rire.mp4', 120, f'{TMP}/rire_couv.png')))
ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
hh = 640; ch = ch.resize((int(ch.width*hh/ch.height), hh), Image.LANCZOS)
x0, y0 = (W-ch.width)//2, 1240
halo = Image.new('RGBA', (W, H), (255, 200, 110, 0)); gl = Image.new('RGBA', (W, H), 0); gl.alpha_composite(ch, (x0, y0))
halo.putalpha(gl.getchannel('A').filter(ImageFilter.GaussianBlur(45)).point(lambda v: int(v*.7))); im.alpha_composite(halo); im.alpha_composite(gl)
ball('boule_rouge', 840, 1700, 180, None, 10)
im.convert('RGB').save(path); print('ok')
