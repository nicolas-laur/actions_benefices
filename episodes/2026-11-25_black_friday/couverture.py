"""Couverture du Black Friday (style maison, lib/cards_lib.py) : gros plan du rayon et de l'étiquette géante « PROMO 199 € barré, 139 €, −30 % » (image de la vidéo), titre « BLACK FRIDAY »,
sous-titre « BONNE AFFAIRE OU MARKETING ? », question « Et toi, tu vas craquer ? », gros plan de Mister Coin sceptique en bas (lib/gros_plan.py)."""
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
    sys.path.insert(0, HERE); import video_col as VCOL
    arr = VCOL.raw_bg(TC).astype(np.float32)                                                   # décor 60 i/s + inscription de l'étiquette, sans sous-titres ni Mister Coin
    S = 360; arr = np.concatenate([arr[S:], arr[::-1][:S]], 0)                                  # remonté : l'étiquette au-dessus du titre (jamais de texte sur du texte)
    y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 220, 300, 600, 700, 1150, 1320, H], [.55, .3, .12, .12, .62, .62, .3, .45])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2); dark = np.clip(dark+.22*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
TC = float(os.environ.get('TC', 42.4))
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Et toi, tu vas craquer ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
path = f'{HERE}/couverture.png'; cards.card("BLACK FRIDAY", False, path, sub=("BONNE AFFAIRE OU MARKETING ?",))
im = Image.open(path).convert('RGBA')
import gros_plan; gros_plan.coller(im, 'sceptique')                                            # gros plan maison : « promesse trop belle »
im.convert('RGB').save(path); print('ok')
