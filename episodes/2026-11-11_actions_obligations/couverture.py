"""Couverture actions / obligations, fond : la rue devant la boulangerie (demande du 11/11), certificat d'action et obligation en haut avec halo
(à la place d'un logo), nom + « PROPRIÉTAIRE OU PRÊTEUR », question, Mister Coin et le boulanger."""
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
def bg(c):   # décor de la rue (devant la boulangerie), assombri en haut pour la lisibilité des textes
    d = still(f'{HERE}/decors/decor_rue.mp4', 0, f'{TMP}/rue_couv.png').resize((int(W*1.2), int(H*1.2)), Image.LANCZOS)
    d = d.crop((20, 250, 20+W, 250+H))                                  # léger zoom : l'enseigne anglaise « for rent » sort du cadre
    arr = np.asarray(d).astype(np.float32); y = np.arange(H)[:, None, None]
    dark = np.interp(y, [0, 700, 1150, 1500, H], [.80, .62, .30, .05, .25])
    arr *= 1-dark; b = Image.fromarray(arr.astype(np.uint8)).convert('RGBA').tobytes('raw', 'BGRa')
    src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H); c.set_source_surface(src); c.paint()
cards.bg = bg
_put = cards.put
def _q(c, s_, y, fam, size, *a, **k):
    if s_ == "Et toi, tu achètes ?": s_ = "Tu sais ce que tu achètes ?"; size = cards.fit(c, s_, fam, size, 0, 900)
    return _put(c, s_, y, fam, size, *a, **k)
cards.put = _q
import veo_coin as VC
for slot, name in ((False, 'couverture.png'), (True, 'couverture_emplacement_logo.png')):
    path = f'{HERE}/{name}'; cards.card("ACTION OU OBLIGATION", slot, path, sub=("PROPRIÉTAIRE OU PRÊTEUR ?",))
    if slot: continue
    im = Image.open(path).convert('RGBA')
    def cut(src, n, dst, h):
        a, m = VC._key(np.asarray(still(src, n, dst)))
        ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
        return ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS)
    feet = 1770
    for ch, cx in ((cut(f'{ROOT}/mister_coin/veo/classique_parle_question.mp4', 30, f'{TMP}/coin_couv.png', 520), 360), (cut(f'{ROOT}/mister_coin/veo/boulanger_jongle.mp4', 0, f'{TMP}/boulanger_couv.png', 600), 730)):
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.35, feet-16, cx+ch.width*.35, feet+14), fill=170)
        im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
        im.alpha_composite(ch, (int(cx-ch.width/2), feet-ch.height))
    def prop(n, w):
        p = Image.open(f'{HERE}/props/{n}.png').convert('RGBA'); p = p.crop(p.getbbox()); return p.resize((w, int(p.height*w/p.width)), Image.LANCZOS)
    for p, cx, rot in ((prop('certificat_action', 400), 330, 6), (prop('obligation_coupons', 300), 760, -6)):
        p = p.rotate(rot, expand=True, resample=Image.BICUBIC)
        gl = Image.new('RGBA', (p.width+200, p.height+200), 0); gl.alpha_composite(p, (100, 100)); a_ = gl.getchannel('A').filter(ImageFilter.GaussianBlur(34))
        halo = Image.new('RGBA', gl.size, (255, 200, 110, 0)); halo.putalpha(a_.point(lambda v: int(v*.85)))
        cy = 450; im.alpha_composite(halo, (cx-gl.width//2, cy-gl.height//2)); im.alpha_composite(p, (cx-p.width//2, cy-p.height//2))
    im.convert('RGB').save(path)
print('ok')
