"""Couverture actions / obligations, DA historique : fond noir, rubans de lumière dorés, certificat d'action et obligation en haut avec halo
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
def bg(c):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('030405')[:3]); g.add_color_stop_rgb(.5, *hx('0A0704')[:3]); g.add_color_stop_rgb(1, *hx('1A1006')[:3]); c.set_source(g); c.paint()
    lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); k = cairo.Context(lay); k.set_operator(cairo.OPERATOR_ADD)
    for (x, y, rx, ry, colr, a) in ((540, 1560, 1150, 70, 'D99A1E', .95), (600, 1650, 1100, 45, 'A8640A', .9), (470, 1480, 1000, 38, 'FFD98A', .55),
                                    (640, 1760, 1200, 80, '3B2306', .6), (560, 1600, 700, 16, 'FFFFFF', .6), (430, 1420, 900, 24, 'FFE9C2', .3)):
        k.save(); k.translate(x, y); k.rotate(-0.42+0.04*((x//10) % 3)); k.scale(rx, ry)
        r = cairo.RadialGradient(0, 0, 0, 0, 0, 1); r.add_color_stop_rgba(0, *hx(colr, a)); r.add_color_stop_rgba(1, *hx(colr, 0)); k.set_source(r); k.arc(0, 0, 1, 0, 2*math.pi); k.fill(); k.restore()
    lay.flush(); im = Image.frombuffer('RGBA', (W, H), bytes(lay.get_data()), 'raw', 'BGRa', lay.get_stride(), 1).filter(ImageFilter.GaussianBlur(28))
    arr = np.asarray(im).astype(np.float32); fade = np.clip((np.arange(H)-700)/700, 0, 1)[:, None, None]; arr[..., :3] *= fade; arr[..., 3] *= fade[..., 0]
    b = Image.fromarray(arr.astype(np.uint8), 'RGBA').tobytes('raw', 'BGRa'); src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H)
    c.set_operator(cairo.OPERATOR_ADD); c.set_source_surface(src); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
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
