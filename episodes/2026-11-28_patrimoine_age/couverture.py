"""Couverture de « Les Français de ton âge ont combien d'argent ? » (style maison, lib/cards_lib.py) : la toise du couloir assombrie,
titre, sous-titre et question réglables (TITRE, SOUS, QUESTION), fond FOND (toise ou couloir),
gros plan de Mister Coin (lib/gros_plan.py, expression EXPR, largeur TAILLE). SORTIE : chemin du PNG."""
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
    if FOND == 'toise': d = Image.open(f'{HERE}/decors/ref_toise.jpg').convert('RGB').resize((W, H), Image.LANCZOS)
    else: d = still(f'{HERE}/decors/sr/decor_couloir.mp4', 70, f'{TMP}/couloir_couv.png').resize((W, H), Image.LANCZOS)
    from PIL import ImageEnhance
    d = ImageEnhance.Color(d).enhance(1.45); d = ImageEnhance.Contrast(d).enhance(1.12)          # couleurs vives (retour du 27/11 : « couleurs ternes »)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.30, .22, .22, .05, .12])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-910)/150.0)**2)*np.exp(-((xs-540)/600.0)**2); dark = np.clip(dark+.42*band, 0, .9)   # voile sombre seulement sous le texte
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
EXPR = os.environ.get('EXPR', 'etoiles'); FOND = os.environ.get('FOND', 'toise')
TITRE = os.environ.get('TITRE', "TON ÂGE, TON ARGENT"); SOUS = os.environ.get('SOUS', "LES FRANÇAIS ONT COMBIEN ?")
QUESTION = os.environ.get('QUESTION', "Et toi, ta marque est où ?"); TAILLE = float(os.environ.get('TAILLE', '.78'))
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = QUESTION; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
path = os.environ.get('SORTIE', f'{HERE}/couverture.png'); cards.card(TITRE, False, path, sub=(SOUS,))
im = Image.open(path).convert('RGBA')
import gros_plan; gros_plan.coller(im, EXPR, largeur_max=TAILLE)
im.convert('RGB').save(path); print('ok')
