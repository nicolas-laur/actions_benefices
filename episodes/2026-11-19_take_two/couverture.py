"""Couverture Take-Two / GTA 6 (style maison, comme le loto) : boulevard néon de Miami assombri, titre « GTA 6 » en Big Shoulders
(police réservée à la couverture, 17/11), « OU L'ACTION ? », question « Et toi, tu as acheté GTA 6 ? », Mister Coin joyeux en bas,
quelques billets autour de lui (émojis Noto). Aucun logo du jeu."""
import cairo, numpy as np, sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import cards_lib as cards
from cards_lib import W, H
TMP = f'{HERE}/tmp'; os.makedirs(TMP, exist_ok=True)
def bg(c):
    d = Image.open(f'{HERE}/decors/sr/decor_boulevard/f0120.jpg').convert('RGB').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.70, .58, .55, .22, .35])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-760)/230.0)**2)*np.exp(-((xs-540)/520.0)**2); dark = np.clip(dark+.22*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Et toi, tu as acheté GTA 6 ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
path = f'{HERE}/couverture.png'; cards.card("", False, path, sub=("OU L'ACTION ?",))
im = Image.open(path).convert('RGBA')
# titre en Big Shoulders, dégradé blanc vers or, ombre douce
F = ImageFont.truetype(f'{ROOT}/fonts/BigShouldersDisplay-Black.ttf', 330)
txt = "GTA 6"; bb = F.getbbox(txt); tw, th = bb[2]-bb[0], bb[3]-bb[1]; x0, y0 = (W-tw)//2-bb[0], 800-th-bb[1]-18
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).text((x0, y0), txt, font=F, fill=255)
yy = np.linspace(0, 1, H)[:, None]; t0, t1 = (800-th-18)/H, 782/H; k = np.clip((yy-t0)/(t1-t0), 0, 1)
grad = np.zeros((H, W, 4), np.uint8); grad[..., 0] = 255; grad[..., 1] = (248-34*k).astype(np.uint8); grad[..., 2] = (235-145*k).astype(np.uint8)
grad[..., 3] = np.asarray(m); g = Image.fromarray(grad, 'RGBA')
sh = Image.new('RGBA', (W, H), (10, 0, 20, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v*.75)))
glow = Image.new('RGBA', (W, H), (255, 170, 60, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v*.45)))
im.alpha_composite(glow); im.alpha_composite(sh, (0, 10)); im.alpha_composite(g)
# Mister Coin joyeux
import veo_coin as VC
src = f'{TMP}/joie_couv.png'
if not os.path.exists(src): subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{ROOT}/mister_coin/veo/classique_joie.mp4', '-vf', 'select=eq(n\\,110)', '-vframes', '1', src], check=True)
a, mk = VC._key(np.asarray(Image.open(src).convert('RGB')))
ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); ch.putalpha(Image.fromarray((mk*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
hh = 640; ch = ch.resize((int(ch.width*hh/ch.height), hh), Image.LANCZOS)
cx0, cy0 = (W-ch.width)//2, 1240
halo = Image.new('RGBA', (W, H), (255, 200, 110, 0)); gl = Image.new('RGBA', (W, H), 0); gl.alpha_composite(ch, (cx0, cy0))
halo.putalpha(gl.getchannel('A').filter(ImageFilter.GaussianBlur(45)).point(lambda v: int(v*.7))); im.alpha_composite(halo); im.alpha_composite(gl)
# billets autour de lui
FE = ImageFont.truetype(f'{ROOT}/fonts/NotoColorEmoji.ttf', 109)
def billet(x, y, taille, rot):
    e = Image.new('RGBA', (180, 180), 0); ImageDraw.Draw(e).text((10, 10), '💵', font=FE, embedded_color=True); e = e.crop(e.getbbox())
    e = e.resize((taille, int(taille*e.height/e.width)), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC, expand=True)
    s_ = Image.new('RGBA', e.size, (0, 0, 0, 0)); s_.putalpha(e.getchannel('A').filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v*.4)))
    im.alpha_composite(s_, (int(x-e.width/2)+6, int(y-e.height/2)+10)); im.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
for (x, y, t, r) in ((125, 1205, 140, -14), (950, 1195, 150, 12), (115, 1600, 130, 8), (960, 1585, 140, -10)):
    billet(x, y, t, r)
im.convert('RGB').save(path); print('ok')
