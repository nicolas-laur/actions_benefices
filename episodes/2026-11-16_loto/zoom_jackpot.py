"""Zoom vertigineux « 1 chance sur 19 068 840 » : une mer de 4 367 × 4 367 grilles (≈ 19 millions) vue en entier, puis zoom ×1 200
jusqu'à TA grille dorée. Rendu par pyramide de blocs 16 × 16 (chaque niveau = 16 × 16 blocs du niveau précédent réduits),
avec un bloc « spécial » par niveau qui contient la grille dorée : la cible reste exacte à tous les zooms.
Usage : zoom_jackpot.frame(u, W, H) -> image BGR (u de 0 à 1) ; python3 zoom_jackpot.py = aperçu mp4."""
import os, math, numpy as np, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
N = 4367                       # 4 367² = 19 070 689 ≈ 19 068 840
TX, TY = 2911, 1733            # position de TA grille (hors centre)
C = 256                        # taille de la texture d'une grille (px)
BG = (40, 22, 52)              # fond violet nuit (BGR plus bas)
def _cell(gold=False):
    im = Image.open(f'{D}/props/grille_loto.png').convert('RGBA'); im.thumbnail((int(C*.84), int(C*.84)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    if gold:
        l = a[..., :3].mean(-1, keepdims=True)/255; a[..., :3] = np.clip(l*np.array([255, 205, 70])*1.25, 0, 255)
    cell = np.zeros((C, C, 3), np.float32); cell[:] = BG[::-1]
    h, w = a.shape[:2]; y0, x0 = (C-h)//2, (C-w)//2; al = a[..., 3:]/255
    cell[y0:y0+h, x0:x0+w] = cell[y0:y0+h, x0:x0+w]*(1-al)+a[..., [2, 1, 0]]*al
    return cell
MIPS = {}                      # pyramide de mip-maps (grille normale, grille dorée) : échantillonnage sans scintillement
def _build():
    for key, gold in (('n', False), ('g', True)):
        m = [_cell(gold)]
        while m[-1].shape[0] > 1: m.append(cv2.resize(m[-1], (max(1, m[-1].shape[1]//2), max(1, m[-1].shape[0]//2)), interpolation=cv2.INTER_AREA))
        MIPS[key] = m
def _sample(key, s, ox, oy, W, H, wrap):
    """Grilles de taille s px, origine (ox, oy) ; interpolation entre deux niveaux de mip (trilinéaire)."""
    m = MIPS[key]; lod = max(0., math.log2(C/s)); l0 = min(int(lod), len(m)-1); l1 = min(l0+1, len(m)-1); f = lod-int(lod) if l1 > l0 else 0
    out = 0
    for l, w in ((l0, 1-f), (l1, f)):
        if w <= 0: continue
        t = m[l]; r = t.shape[0]/s
        M = np.float32([[r, 0, -ox*r], [0, r, -oy*r]])
        im = cv2.warpAffine(t, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                            borderMode=cv2.BORDER_WRAP if wrap else cv2.BORDER_CONSTANT, borderValue=(-1, -1, -1))
        out = out+w*im
    return out
def ease(x): return x*x*(3-2*x)
def frame(u, W=1080, H=1920, cy=None):
    if not MIPS: _build()
    cy = H*.44 if cy is None else cy
    s0, s1 = W*.92/N, 300.0                                  # taille d'une grille (px) : grille entière -> grille géante
    e = ease(min(1, max(0, u)))
    s = math.exp(math.log(s0)+(math.log(s1)-math.log(s0))*e)
    p0 = np.array([W/2-s0*N/2+s0*(TX+.5), cy-s0*N/2+s0*(TY+.5)])   # où est la cible quand tout est visible
    pt = p0+(np.array([W/2, cy])-p0)*ease(min(1, e*1.15))
    ox, oy = pt[0]-s*(TX+.5), pt[1]-s*(TY+.5)                # origine de la grille à l'écran
    img = _sample('n', s, ox, oy, W, H, True)
    g = _sample('g', s, ox+TX*s, oy+TY*s, W, H, False)          # la grille dorée, une seule fois, par-dessus
    msk = (g[..., :1] >= 0).astype(np.float32); img = img*(1-msk)+np.maximum(g, 0)*msk
    xx = np.arange(W, dtype=np.float32)[None, :, None]; yy = np.arange(H, dtype=np.float32)[:, None, None]
    ins = np.clip(np.minimum(np.minimum(xx-ox+.5, ox+N*s-xx+.5), np.minimum(yy-oy+.5, oy+N*s-yy+.5)), 0, 1)   # bord de la mer de grilles
    img = img*ins+np.float32(BG[::-1])*(1-ins)
    return np.clip(img, 0, 255).astype(np.uint8), (pt[0], pt[1], s)
if __name__ == '__main__':
    from PIL import ImageDraw, ImageFont
    W, H, F = 1080, 1920, 60
    FT = ImageFont.truetype(f'{D}/../../fonts/AlfaSlabOne-Regular.ttf', 92); FS = ImageFont.truetype(f'{D}/../../fonts/AlfaSlabOne-Regular.ttf', 54)
    ff = __import__('subprocess').Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(F), '-i', '-',
                                         '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', f'{D}/zoom_apercu.mp4'], stdin=__import__('subprocess').PIPE)
    for i in range(int(7.0*F)):
        t = i/F; u = max(0, (t-.8)/5.0); im, (x, y, sz) = frame(u, W, H)
        pil = Image.fromarray(im[..., ::-1]); d = ImageDraw.Draw(pil)
        r = max(16, sz*.72); a = .5+.5*math.sin(t*7)
        d.ellipse([x-r, y-r, x+r, y+r], outline=(255, 205, 70), width=6)
        if sz < 30: d.ellipse([x-r-8*a, y-r-8*a, x+r+8*a, y+r+8*a], outline=(255, 225, 120), width=3)
        al = 1-min(1, max(0, (u-.55)/.2))
        if al > 0:
            lay = Image.new('RGBA', pil.size, 0); dl = ImageDraw.Draw(lay); c = int(255*al)
            dl.text((W/2, 250), "19 068 840 grilles", font=FT, anchor='mm', fill=(255, 235, 200, c), stroke_width=6, stroke_fill=(40, 20, 50, c))
            pil = Image.alpha_composite(pil.convert('RGBA'), lay).convert('RGB'); d = ImageDraw.Draw(pil)
        if u > .85:
            k = min(1, (u-.85)/.12); lay = Image.new('RGBA', pil.size, 0); dl = ImageDraw.Draw(lay); c = int(255*k)
            dl.text((x, y-r-70), "TOI", font=FT, anchor='mm', fill=(255, 205, 70, c), stroke_width=7, stroke_fill=(40, 20, 50, c))
            dl.text((x, y+r+60), "1 chance", font=FS, anchor='mm', fill=(255, 245, 225, c), stroke_width=5, stroke_fill=(40, 20, 50, c))
            pil = Image.alpha_composite(pil.convert('RGBA'), lay).convert('RGB')
        ff.stdin.write(np.asarray(pil)[..., ::-1].tobytes())
    ff.stdin.close(); ff.wait()
