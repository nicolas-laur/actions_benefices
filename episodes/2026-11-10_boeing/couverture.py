"""Couverture Boeing, DA historique : fond noir, rubans de lumière bleus (bleu Boeing), symbole Boeing blanc en haut avec halo,
nom épuré + « −60 % DEPUIS 2019 », question de fin, Mister Coin inquiet (image 40 du clip classique_parle_inquiet, détourée)."""
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
def bg(c):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('030405')[:3]); g.add_color_stop_rgb(.5, *hx('04070D')[:3]); g.add_color_stop_rgb(1, *hx('081020')[:3]); c.set_source(g); c.paint()
    lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); k = cairo.Context(lay); k.set_operator(cairo.OPERATOR_ADD)
    for (x, y, rx, ry, colr, a) in ((540, 1560, 1150, 70, '1D5BD8', .95), (600, 1650, 1100, 45, '0039A6', .9), (470, 1480, 1000, 38, '9CC0FF', .55),
                                    (640, 1760, 1200, 80, '06173B', .6), (560, 1600, 700, 16, 'FFFFFF', .6), (430, 1420, 900, 24, 'D2E4FF', .3)):
        k.save(); k.translate(x, y); k.rotate(-0.42+0.04*((x//10) % 3)); k.scale(rx, ry)
        r = cairo.RadialGradient(0, 0, 0, 0, 0, 1); r.add_color_stop_rgba(0, *hx(colr, a)); r.add_color_stop_rgba(1, *hx(colr, 0)); k.set_source(r); k.arc(0, 0, 1, 0, 2*math.pi); k.fill(); k.restore()
    lay.flush(); im = Image.frombuffer('RGBA', (W, H), bytes(lay.get_data()), 'raw', 'BGRa', lay.get_stride(), 1).filter(ImageFilter.GaussianBlur(28))
    arr = np.asarray(im).astype(np.float32); fade = np.clip((np.arange(H)-700)/700, 0, 1)[:, None, None]; arr[..., :3] *= fade; arr[..., 3] *= fade[..., 0]
    b = Image.fromarray(arr.astype(np.uint8), 'RGBA').tobytes('raw', 'BGRa'); src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H)
    c.set_operator(cairo.OPERATOR_ADD); c.set_source_surface(src); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "En panne ou bonne affaire ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
for slot, name in ((False, 'couverture.png'), (True, 'couverture_emplacement_logo.png')):
    path = f'{HERE}/{name}'; cards.card("BOEING", slot, path, sub=("−60 % DEPUIS 2019",))
    if slot: continue
    im = Image.open(path).convert('RGBA')
    fr = still(f'{ROOT}/mister_coin/veo/classique_parle_inquiet.mp4', 40, f'{TMP}/coin_inquiet_couv.png')
    a, m = VC._key(np.asarray(fr))
    ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
    h = 560; ch = ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS); cx, feet = 540, 1770
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.4, feet-16, cx+ch.width*.4, feet+14), fill=170)
    im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(ch, (int(cx-ch.width/2), feet-h))
    lg = Image.open(f'{HERE}/logos/boeing_blanc.png').convert('RGBA'); lg = lg.crop(lg.getbbox()); lw = 330; lg = lg.resize((lw, int(lg.height*lw/lg.width)), Image.LANCZOS)
    gl = Image.new('RGBA', (lg.width+200, lg.height+200), 0); gl.alpha_composite(lg, (100, 100)); a_ = gl.getchannel('A').filter(ImageFilter.GaussianBlur(30))
    halo = Image.new('RGBA', gl.size, (110, 160, 255, 0)); halo.putalpha(a_.point(lambda v: int(v*.9)))
    cy = 470; im.alpha_composite(halo, (540-gl.width//2, cy-gl.height//2)); im.alpha_composite(lg, (540-lg.width//2, cy-lg.height//2))
    im.convert('RGB').save(path)
print('ok')
