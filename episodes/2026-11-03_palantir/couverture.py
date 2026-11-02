"""Couverture Palantir, DA historique de la ligne fil rouge (fond noir, nom épuré, « Et toi, tu achètes ? », Mister Coin classique)
avec la touche du dossier classifié : l'œil Gemini de l'accroche en haut, fondu dans le noir, et des rubans de lumière rouges en bas.
Mister Coin inquiet (image 40 du clip classique_parle_inquiet, détourée)."""
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
EYE = still(f'{HERE}/decors/oeil.mp4', 48, f'{TMP}/oeil_couv.png')          # 2 s : œil grand ouvert, regard caméra
def bg(c):
    c.set_source_rgb(*hx('050506')[:3]); c.paint()
    e = EYE.resize((int(EYE.width*1080*1.25/EYE.width), int(EYE.height*1080*1.25/EYE.width)), Image.LANCZOS)
    px, py = 180/360*e.width, 316/640*e.height                                # pupille (repérée sur l'image 360×640)
    ox, oy = int(540-px), int(470-py)
    a = np.asarray(e).astype(np.float32)/255
    a = a*np.array([1.0, .82, .78])                                            # légère dominante rouge, ton dossier
    ys = (np.arange(e.height)+oy)[:, None]; fade = np.clip((760-ys)/330, 0, 1)**1.4*np.clip((ys+40)/260, 0, 1)
    a *= (.78*fade)[..., None]
    im = Image.fromarray((np.clip(a, 0, 1)*255).astype(np.uint8)).convert('RGBA')
    canvas = Image.new('RGBA', (W, H), (5, 5, 6, 255)); canvas.alpha_composite(im, (ox, oy)) if ox >= 0 and oy >= 0 else canvas.paste(im, (ox, oy))
    lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); k = cairo.Context(lay); k.set_operator(cairo.OPERATOR_ADD)
    for (x, y, rx, ry, colr, al) in ((540, 1560, 1150, 70, 'E8402A', .9), (600, 1650, 1100, 45, '8A1A12', .9), (470, 1480, 1000, 36, 'FF8A5C', .45),
                                     (640, 1760, 1200, 80, '2A0806', .6), (560, 1600, 700, 16, 'FFFFFF', .5), (430, 1420, 900, 22, 'FFC9B8', .25)):
        k.save(); k.translate(x, y); k.rotate(-0.42+0.04*((x//10) % 3)); k.scale(rx, ry)
        r = cairo.RadialGradient(0, 0, 0, 0, 0, 1); r.add_color_stop_rgba(0, *hx(colr, al)); r.add_color_stop_rgba(1, *hx(colr, 0)); k.set_source(r); k.arc(0, 0, 1, 0, 2*math.pi); k.fill(); k.restore()
    lay.flush(); rib = Image.frombuffer('RGBA', (W, H), bytes(lay.get_data()), 'raw', 'BGRa', lay.get_stride(), 1).filter(ImageFilter.GaussianBlur(28))
    arr = np.asarray(rib).astype(np.float32); f2 = np.clip((np.arange(H)-700)/700, 0, 1)[:, None, None]; arr[..., :3] *= f2
    base = np.asarray(canvas.convert('RGB')).astype(np.float32); out = np.clip(base+arr[..., :3], 0, 255).astype(np.uint8)
    b = Image.fromarray(out).convert('RGBA').tobytes('raw', 'BGRa'); src = cairo.ImageSurface.create_for_data(bytearray(b), cairo.FORMAT_ARGB32, W, H)
    c.set_source_surface(src); c.paint()
    # repères de viseur, discrets, comme dans la vidéo
    c.set_source_rgba(1, 1, 1, .35); c.set_line_width(3)
    for (x, y, dx, dy) in ((60, 215, 1, 1), (1020, 215, -1, 1)):
        c.move_to(x, y+44*dy); c.line_to(x, y); c.line_to(x+44*dx, y); c.stroke()
cards.bg = bg
import veo_coin as VC
for slot, name in ((False, 'couverture.png'), (True, 'couverture_emplacement_logo.png')):
    path = f'{HERE}/{name}'; cards.card("PALANTIR", slot, path, sub=("ELLE AIDE LES ÉTATS", "À TOUT SAVOIR DE TOI"))
    if slot: continue
    im = Image.open(path).convert('RGBA')
    fr = still(f'{ROOT}/mister_coin/veo/classique_parle_inquiet.mp4', 40, f'{TMP}/coin_inquiet_couv.png')
    a, m = VC._key(np.asarray(fr))
    ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); ch.putalpha(Image.fromarray((m*255).astype(np.uint8))); ch = ch.crop(ch.getbbox())
    h = 560; ch = ch.resize((int(ch.width*h/ch.height), h), Image.LANCZOS); cx, feet = 540, 1770
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-ch.width*.4, feet-16, cx+ch.width*.4, feet+14), fill=170)
    im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    im.alpha_composite(ch, (int(cx-ch.width/2), feet-h)); im.convert('RGB').save(path)
print('ok')
