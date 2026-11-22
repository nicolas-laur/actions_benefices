"""Couverture de buy, borrow, die (style maison, lib/cards_lib.py) : salon du manoir assombri en haut, titre « BUY, BORROW, DIE »,
sous-titre « LA MÉTHODE DES MILLIARDAIRES », question « Et toi, tu en penses quoi ? », Mister Coin qui confie un secret en bas avec un halo doré."""
import cairo, numpy as np, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from PIL import Image, ImageFilter
import cards_lib as cards
from cards_lib import W, H
TMP = f'{HERE}/tmp'; os.makedirs(TMP, exist_ok=True)
def still(src, n, dst):
    if not os.path.exists(dst):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', f'select=eq(n\\,{n})', '-vframes', '1', dst], check=True)
    return Image.open(dst).convert('RGB')
def bg(c):
    d = still(f'{HERE}/decors/sr/decor_manoir.mp4', 60, f'{TMP}/manoir_couv.png').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.72, .62, .58, .25, .4])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2); dark = np.clip(dark+.22*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Et toi, tu en penses quoi ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
path = f'{HERE}/couverture.png'; cards.card("BUY, BORROW, DIE", False, path, sub=("LA MÉTHODE DES MILLIARDAIRES",))
im = Image.open(path).convert('RGBA')
a, m = VC._key(np.asarray(still(f'{ROOT}/mister_coin/veo/classique_parle_confidence.mp4', 130, f'{TMP}/confidence_couv.png')))
ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
hh = 640; ch = ch.resize((int(ch.width*hh/ch.height), hh), Image.LANCZOS)
x0, y0 = (W-ch.width)//2, 1240
halo = Image.new('RGBA', (W, H), (255, 200, 110, 0)); gl = Image.new('RGBA', (W, H), 0); gl.alpha_composite(ch, (x0, y0))
halo.putalpha(gl.getchannel('A').filter(ImageFilter.GaussianBlur(45)).point(lambda v: int(v*.7))); im.alpha_composite(halo); im.alpha_composite(gl)
im.convert('RGB').save(path); print('ok')
