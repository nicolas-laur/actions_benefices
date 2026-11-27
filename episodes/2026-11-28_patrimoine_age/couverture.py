"""Couverture de « Les Français de ton âge ont combien d'argent ? » (style maison, lib/cards_lib.py) : la toise du couloir assombrie,
titre « TON ÂGE, TON ARGENT », sous-titre « COMBIEN ONT LES FRANÇAIS ? », question « Et toi, ta marque est où ? »,
gros plan de Mister Coin (lib/gros_plan.py, expression EXPR, « reflechit » par défaut)."""
import cairo, numpy as np, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from PIL import Image
import cards_lib as cards
from cards_lib import W, H
TMP = f'{HERE}/tmp'; os.makedirs(TMP, exist_ok=True)
def still(src, n, dst):
    if not os.path.exists(dst):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', f'select=eq(n\\,{n})', '-vframes', '1', dst], check=True)
    return Image.open(dst).convert('RGB')
def bg(c):
    d = still(f'{HERE}/decors/sr/decor_couloir.mp4', 70, f'{TMP}/couloir_couv.png').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.72, .62, .58, .25, .4])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2); dark = np.clip(dark+.22*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
EXPR = os.environ.get('EXPR', 'reflechit')
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Et toi, ta marque est où ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
path = f'{HERE}/couverture.png'; cards.card("TON ÂGE, TON ARGENT", False, path, sub=("COMBIEN ONT LES FRANÇAIS ?",))
im = Image.open(path).convert('RGBA')
import gros_plan; gros_plan.coller(im, EXPR)
im.convert('RGB').save(path); print('ok')
