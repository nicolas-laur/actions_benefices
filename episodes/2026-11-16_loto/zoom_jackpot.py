"""Zoom vertigineux « 1 chance sur 19 068 840 » : une mer de 4 367 × 4 367 grilles (≈ 19 millions) vue en entier, puis zoom ×1 200
jusqu'à TOI, en doré. Rendu par pyramide de blocs 16 × 16 (chaque niveau = 16 × 16 blocs du niveau précédent réduits),
avec un bloc « spécial » par niveau qui contient la grille dorée : la cible reste exacte à tous les zooms.
Usage : zoom_jackpot.frame(u, W, H) -> image BGR (u de 0 à 1) ; python3 zoom_jackpot.py = aperçu mp4."""
import os, math, numpy as np, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
N = 4367                       # 4 367² = 19 070 689 ≈ 19 068 840
TX, TY = 2911, 1733            # position de TA grille (hors centre)
C = 256                        # taille de la texture d'une grille (px)
BG = (40, 22, 52)              # fond violet nuit (BGR plus bas)
OUT = (55, 32, 24)
SHIRTS = [(226, 87, 76), (46, 150, 150), (232, 182, 64), (110, 150, 205), (120, 170, 90), (200, 110, 160), (240, 140, 70), (90, 110, 170)]
SKINS = [(247, 214, 182), (230, 184, 140), (190, 135, 95), (140, 95, 65)]
HAIRS = [(70, 45, 30), (30, 25, 25), (150, 95, 45), (215, 175, 90), (110, 70, 40)]
def _person(i, gold=False, P=128):
    """Petit personnage 1930 (tête ronde, corps, bras levés), traits brun foncé ; variante i, ou doré pour « toi »."""
    from PIL import ImageDraw
    S = 4; B0 = 128; im = Image.new('RGBA', (B0*S, B0*S), 0); d = ImageDraw.Draw(im); w = 5*S
    sh, sk, hr = SHIRTS[i % 8], SKINS[(i*3+1) % 4], HAIRS[(i*7+2) % 5]
    if gold: sh, sk, hr = (255, 200, 60), (255, 225, 130), (230, 160, 40)
    cx = B0*S//2; arm = 1 if i % 3 else -1                     # bras levés ou baissés selon la variante
    for sx in (-1, 1):                                       # jambes
        d.line([(cx+sx*9*S, 92*S), (cx+sx*12*S, 116*S)], fill=OUT, width=11*S)
        d.line([(cx+sx*9*S, 92*S), (cx+sx*12*S, 116*S)], fill=(60, 60, 80), width=6*S)
    for sx in (-1, 1):                                       # bras
        y2 = 40*S if arm > 0 else 92*S
        d.line([(cx+sx*18*S, 62*S), (cx+sx*33*S, y2)], fill=OUT, width=10*S); d.line([(cx+sx*18*S, 62*S), (cx+sx*33*S, y2)], fill=sh, width=5*S)
        d.ellipse([cx+sx*33*S-6*S, y2-6*S, cx+sx*33*S+6*S, y2+6*S], fill=(250, 250, 245), outline=OUT, width=w//2)   # gants blancs
    d.rounded_rectangle([cx-21*S, 55*S, cx+21*S, 96*S], radius=12*S, fill=sh, outline=OUT, width=w)
    d.ellipse([cx-20*S, 14*S, cx+20*S, 56*S], fill=sk, outline=OUT, width=w)                                            # tête
    d.chord([cx-20*S, 12*S, cx+20*S, 46*S], 180, 360, fill=hr, outline=OUT, width=w)                                      # cheveux
    for sx in (-1, 1): d.ellipse([cx+sx*8*S-3*S, 34*S-4*S, cx+sx*8*S+3*S, 34*S+4*S], fill=OUT)                         # yeux
    d.arc([cx-8*S, 36*S, cx+8*S, 48*S], 20, 160, fill=OUT, width=3*S)                                                     # sourire
    return im.resize((P, P), Image.LANCZOS)
G = 4                                                        # motif de base : 4 × 4 personnages différents
def _cell(gold=False):
    q = C//G
    if gold:                                                 # « toi » : même pose que le personnage qu'il remplace, fond transparent
        j = (TY % G)*G+TX % G; pim = np.asarray(_person(j, True, C)).astype(np.float32)
        return np.dstack([pim[..., [2, 1, 0]]*pim[..., 3:]/255, pim[..., 3:]/255])        # couleurs prémultipliées + alpha
    cell = np.zeros((C, C, 3), np.float32); cell[:] = BG[::-1]
    for j in range(G*G):
        pim = np.asarray(_person(j, False, q)).astype(np.float32); al = pim[..., 3:]/255
        y, x = (j//G)*q, (j % G)*q; cell[y:y+q, x:x+q] = cell[y:y+q, x:x+q]*(1-al)+pim[..., [2, 1, 0]]*al
    return cell
MIPS = {}                      # pyramide de mip-maps (grille normale, grille dorée) : échantillonnage sans scintillement
def _build():
    for key, gold in (('n', False), ('g', True)):
        m = [_cell(gold)]
        while m[-1].shape[0] > 1: m.append(cv2.resize(m[-1], (max(1, m[-1].shape[1]//2), max(1, m[-1].shape[0]//2)), interpolation=cv2.INTER_AREA))
        MIPS[key] = m
def _sample(key, s, ox, oy, W, H, wrap):
    """Grilles de taille s px, origine (ox, oy) ; interpolation entre deux niveaux de mip (trilinéaire)."""
    m = MIPS[key]; lod = max(0., math.log2(C/(s*(G if key == 'n' else 1)))); l0 = min(int(lod), len(m)-1); l1 = min(l0+1, len(m)-1); f = lod-int(lod) if l1 > l0 else 0
    out = 0
    for l, w in ((l0, 1-f), (l1, f)):
        if w <= 0: continue
        t = m[l]; r = t.shape[0]/(s*(G if key == 'n' else 1))
        M = np.float32([[r, 0, -ox*r], [0, r, -oy*r]])
        im = cv2.warpAffine(t, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                            borderMode=cv2.BORDER_WRAP if wrap else cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
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
    img = img*(1-g[..., 3:])+g[..., :3]
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
            dl.text((W/2, 250), "19 068 840 joueurs", font=FT, anchor='mm', fill=(255, 235, 200, c), stroke_width=6, stroke_fill=(40, 20, 50, c))
            pil = Image.alpha_composite(pil.convert('RGBA'), lay).convert('RGB'); d = ImageDraw.Draw(pil)
        if u > .85:
            k = min(1, (u-.85)/.12); lay = Image.new('RGBA', pil.size, 0); dl = ImageDraw.Draw(lay); c = int(255*k)
            dl.text((x, y-r-70), "TOI", font=FT, anchor='mm', fill=(255, 205, 70, c), stroke_width=7, stroke_fill=(40, 20, 50, c))
            dl.text((x, y+r+60), "1 chance", font=FS, anchor='mm', fill=(255, 245, 225, c), stroke_width=5, stroke_fill=(40, 20, 50, c))
            pil = Image.alpha_composite(pil.convert('RGBA'), lay).convert('RGB')
        ff.stdin.write(np.asarray(pil)[..., ::-1].tobytes())
    ff.stdin.close(); ff.wait()
