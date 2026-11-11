"""Couverture actions / obligations, DA historique : fond noir, rubans de lumière dorés, lingot et créséide en haut avec halo
(à la place d'un logo), nom + « PROPRIÉTAIRE OU PRÊTEUR », question, Mister Coin et le roi Crésus, devant le trésor de Lydie."""
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
def bg(c):   # le trésor de Lydie, la ville antique dans l'arche (demande du 11/11), assombri en haut pour la lisibilité des textes
    d = still(f'{HERE}/decors/decor_lydie.mp4', 144, f'{TMP}/lydie_couv.png').resize((W, H), Image.LANCZOS)
    arr = np.asarray(d.convert('RGB')).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 650, 1120, 1320, H], [.70, .58, .55, .12, .30])
    xs = np.arange(W)[None, :, None]; band = np.exp(-((y-930)/170.0)**2)*np.exp(-((xs-540)/520.0)**2)   # voile sombre doux derrière les textes
    dark = np.clip(dark+.25*band, 0, .9)
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Refuge ou placement qui dort ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
for slot, name in ((False, 'couverture.png'), (True, 'couverture_emplacement_logo.png')):
    path = f'{HERE}/{name}'; cards.card("L'OR", slot, path, sub=("NI PROPRIÉTAIRE, NI PRÊTEUR",))
    if slot: continue
    im = Image.open(path).convert('RGBA')
    def cut(src, n, dst, h):
        a, m = VC._key(np.asarray(still(src, n, dst)))
        ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
        return ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS)
    feet = 1770
    for ch, cx in ((cut(f'{ROOT}/mister_coin/veo/classique_parle_question.mp4', 30, f'{TMP}/coin_couv.png', 520), 400),):
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.35, feet-16, cx+ch.width*.35, feet+14), fill=170)
        im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
        im.alpha_composite(ch, (int(cx-ch.width/2), feet-ch.height))
    ld = Image.open(f'{HERE}/props/cresus.png').convert('RGBA'); ld = ld.resize((int(ld.width*560/ld.height), 560), Image.LANCZOS); im.alpha_composite(ld, (760-ld.width//2, feet-ld.height+12))
    def prop(n, w):
        p = Image.open(f'{HERE}/props/{n}.png').convert('RGBA'); p = p.crop(p.getbbox()); return p.resize((w, int(p.height*w/p.width)), Image.LANCZOS)
    for p, cx, rot in ((prop('lingot', 380), 330, 4), (prop('creseide', 280), 760, -6)):
        p = p.rotate(rot, expand=True, resample=Image.BICUBIC)
        gl = Image.new('RGBA', (p.width+200, p.height+200), 0); gl.alpha_composite(p, (100, 100)); a_ = gl.getchannel('A').filter(ImageFilter.GaussianBlur(34))
        halo = Image.new('RGBA', gl.size, (255, 200, 110, 0)); halo.putalpha(a_.point(lambda v: int(v*.85)))
        cy = 450; im.alpha_composite(halo, (cx-gl.width//2, cy-gl.height//2)); im.alpha_composite(p, (cx-p.width//2, cy-p.height//2))
    im.convert('RGB').save(path)
print('ok')
