"""Détourage des poses fixes de Mister Coin (fond vert Gemini) -> PNG RGBA recadré.
Usage : python3 detoure_poses.py [--petits] src.jpg nom [src2.jpg nom2 ...]  (--petits : garde gouttes et petites pièces détachées)  -> mister_coin/poses/<nom>.png"""
import sys, os, numpy as np, cv2
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'poses')

def detoure(path, seuil=.002, opaques=(), recadre=True, hmax=900):
    """opaques : rectangles (x0, y0, x1, y1) de la source gardés tels quels, pour un accessoire qui contient du vert (flèche peinte…)"""
    bgr = cv2.imread(path); hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # vert (y compris l'ombre portée, plus sombre) : teinte 40-85 sur 180, saturé
    g = np.clip((s - 60) / 60, 0, 1) * np.clip(1 - np.abs(h - 62) / 25, 0, 1)
    alpha = 1 - g
    m = (alpha > .5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)          # garder le personnage (plus grande zone)
    keep = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    big = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > seuil * m.size]   # + morceaux détachés notables (chapeau, main)
    alpha *= np.isin(lab, big).astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    brut = rgb.copy()
    gmax = np.maximum(rgb[..., 0], rgb[..., 2])                       # anti-débordement du vert sur les bords
    rgb[..., 1] = np.minimum(rgb[..., 1], gmax + 25)
    v = hsv[..., 2]
    for x0, y0, x1, y1 in opaques:
        z = (v[y0:y1, x0:x1] < 215) & (h[y0:y1, x0:x1] <= 56)                                    # vert plus sombre que le fond Gemini : celui de l'accessoire
        alpha[y0:y1, x0:x1][z] = 1; rgb[y0:y1, x0:x1][z] = brut[y0:y1, x0:x1][z]
    im = Image.fromarray(np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
    if recadre: im = im.crop(im.getbbox())
    if hmax and im.height > hmax: im = im.resize((int(im.width * hmax / im.height), hmax), Image.LANCZOS)
    return im

if __name__ == '__main__':
    a = sys.argv[1:]
    seuil = .002
    if a and a[0].startswith('--petits'):   # garder les petits éléments détachés (gouttes, pièces qui tombent)
        seuil = .00005; a = a[1:]
    for src, nom in zip(a[::2], a[1::2]):
        im = detoure(src, seuil); im.save(f'{OUT}/{nom}.png'); print(nom, im.size)
