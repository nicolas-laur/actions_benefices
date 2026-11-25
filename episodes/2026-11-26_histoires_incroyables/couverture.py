"""Couverture des « 3 histoires incroyables » (style maison, lib/cards_lib.py) : le prêteur sur gages assombri, titre « 3 HISTOIRES INCROYABLES »,
sous-titre « 10 % D'APPLE POUR 800 $ ? », question « Et toi, tu aurais vendu ? », gros plan de Mister Coin bouche bée devant un prix (lib/gros_plan.py)."""
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
    _sr = f'{HERE}/decors/sr/decor_preteur.mp4'; d = still(_sr if os.path.exists(_sr) else f'{HERE}/decors/decor_preteur.mp4', 40, f'{TMP}/preteur_couv{"_sr" if os.path.exists(_sr) else ""}.png').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.72, .62, .58, .25, .4])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2); dark = np.clip(dark+.22*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
EXPR = os.environ.get('EXPR', 'bouche_bee_prix')
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Et toi, tu aurais vendu ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
path = f'{HERE}/couverture.png'; cards.card("3 HISTOIRES INCROYABLES", False, path, sub=("10 % D'APPLE POUR 800 $ ?",))
im = Image.open(path).convert('RGBA')
import gros_plan; gros_plan.coller(im, EXPR)                                                   # gros plan maison (lib/gros_plan.py)
im.convert('RGB').save(path); print('ok')
