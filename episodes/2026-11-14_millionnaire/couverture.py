"""Couverture « millionnaire » : haricot magique en pièces d'or au coucher du soleil (assombri en haut), titre + « AVEC 402 € PAR MOIS ? »,
question, Mister Coin en gros plan aux yeux en étoiles en bas (comme dans la vidéo)."""
import cairo, math, numpy as np, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from PIL import Image, ImageFilter, ImageDraw
import cards_lib as cards
from cards_lib import W, H, hx
TMP = f'{HERE}/tmp'; os.makedirs(TMP, exist_ok=True)
def still(src, n, dst):
    if not os.path.exists(dst):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', f'select=eq(n\\,{n})', '-vframes', '1', dst], check=True)
    return Image.open(dst).convert('RGB')
def bg(c):   # le haricot géant au coucher du soleil, assombri en haut pour la lisibilité des textes
    d = still(f'{HERE}/decors/decor_haricot_geant.mp4', 120, f'{TMP}/haricot_couv.png').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.70, .58, .55, .12, .30])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2)   # voile sombre doux derrière les textes
    dark = np.clip(dark+.25*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Tu commences à quel âge ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
GP_N, GP_W, GP_Y = int(os.environ.get('GP_N', 55)), int(os.environ.get('GP_W', 740)), int(os.environ.get('GP_Y', 1110))
for slot, name in ((False, 'couverture.png'), (True, 'couverture_emplacement_logo.png')):
    path = f'{HERE}/{name}'; cards.card("MILLIONNAIRE", slot, path, sub=("AVEC 402 € PAR MOIS ?",))
    if slot: continue
    im = Image.open(path).convert('RGBA')
    def cut(src, n, dst, h):
        a, m = VC._key(np.asarray(still(src, n, dst)))
        ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
        return ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS)
    # Mister Coin en gros plan, les yeux en étoiles (image du gros plan de la vidéo), le bas de la pièce sort du cadre
    a_, m_ = VC._key(np.asarray(still(f'{HERE}/coin/gros_plan_etoiles.mp4', GP_N, f'{TMP}/coin_etoiles_couv.png')))
    ch = Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m_*255).astype(np.uint8)))
    ch = ch.resize((GP_W, int(ch.height*GP_W/ch.width)), Image.LANCZOS)
    fx = np.clip(np.minimum(np.arange(GP_W), GP_W-1-np.arange(GP_W))/90, 0, 1)**1.5   # bords gauche et droit du clip fondus : pas de coupe nette
    ch.putalpha(Image.fromarray((np.asarray(ch.getchannel('A')).astype(np.float32)*fx[None, :]).astype(np.uint8)))
    top = ch.getchannel('A').getbbox()[1]; x0 = (W-ch.width)//2; y0 = GP_Y-top
    gl = Image.new('RGBA', (W, H), 0); gl.alpha_composite(ch, (x0, y0)) if y0 >= 0 else gl.alpha_composite(ch.crop((0, -y0, ch.width, ch.height)), (x0, 0))
    halo = Image.new('RGBA', (W, H), (255, 200, 110, 0)); halo.putalpha(gl.getchannel('A').filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v*.6)))
    im.alpha_composite(halo); im.alpha_composite(gl)
    im.convert('RGB').save(path)
print('ok')
