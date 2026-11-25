"""Banque d'expressions de Mister Coin pour l'accueil (25/11/2026).
Pour chaque pose de site/assets/img/expr/ (exportée par poses_hd.py en 1080 px), repère le disque de la pièce
(plus grand cercle doré, par transformée de distance) et écrit site/assets/img/expr/index.json :
{nom: [largeur, hauteur, x du centre, y du centre, rayon]} en pixels. coin.js s'en sert pour poser chaque expression
avec le disque toujours au même endroit (le centre de l'arc) et toujours de la même taille, quel que soit l'écran."""
import json, os, glob, numpy as np, cv2
from PIL import Image
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'img', 'expr')
ORDRE = ['salut', 'joie', 'etoiles', 'rire', 'pouce', 'site_saut_joie', 'choc', 'sceptique', 'reflechit', 'haussement', 'site_trophee', 'facepalm',
         'sueur', 'site_megaphone', 'inquiet', 'loupe', 'question', 'site_tirelire', 'court', 'triste', 'site_parapluie', 'site_dort']
# disques mesurés à la main (mains ou objet devant la pièce : la détection automatique s'y trompe)
MANUEL = {'rire': (343, 432, 290), 'sueur': (333, 437, 300), 'sceptique': (311, 435, 300), 'site_tirelire': (465, 383, 270)}
out = {}
for n in ORDRE:
    im = np.array(Image.open(f'{D}/{n}.webp').convert('RGBA'))
    hsv = cv2.cvtColor(im[..., :3], cv2.COLOR_RGB2HSV)
    or_ = ((hsv[..., 0] >= 8) & (hsv[..., 0] <= 32) & (hsv[..., 1] > 90) & (hsv[..., 2] > 120) & (im[..., 3] > 128)).astype(np.uint8)
    # le visage (yeux, bouche, traits) troue le doré : on referme avant de mesurer
    or_ = cv2.morphologyEx(or_, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    # bouchage des trous (yeux, bouche, nœud, gants posés sur la pièce) : tout ce qui n'est pas relié au bord de l'image est rempli
    ext = np.zeros((or_.shape[0] + 2, or_.shape[1] + 2), np.uint8); f = or_.copy()
    cv2.floodFill(f, ext, (0, 0), 1); or_ = or_ | (1 - f)
    dist = cv2.distanceTransform(or_, cv2.DIST_L2, 5)
    y, x = np.unravel_index(dist.argmax(), dist.shape)
    r = float(dist.max())
    # une main ou un objet posé sur la pièce rétrécit le cercle inscrit : on cherche alors le contour du disque (Hough) parmi les cercles
    # plus grands qui passent près de ce centre, et on garde le plus doré
    gris = cv2.medianBlur(cv2.cvtColor(im[..., :3], cv2.COLOR_RGB2GRAY), 5)
    c = cv2.HoughCircles(gris, cv2.HOUGH_GRADIENT, 1.2, 40, param1=120, param2=40, minRadius=int(r * .95), maxRadius=int(r * 1.9))
    if c is not None:
        yy, xx = np.mgrid[:or_.shape[0], :or_.shape[1]]
        best = None
        for cx, cy, cr in c[0][:30]:
            if np.hypot(cx - x, cy - y) > cr - r * .6: continue          # le cercle inscrit doit tenir dedans
            disque = (xx - cx) ** 2 + (yy - cy) ** 2 <= cr ** 2
            plein = or_[disque].mean()
            if plein > .9 and (best is None or cr > best[2]): best = (cx, cy, cr)
        if best and best[2] > r * 1.08: x, y, r = best
    if n in MANUEL: x, y, r = MANUEL[n]
    out[n] = [im.shape[1], im.shape[0], int(x), int(y), int(r)]
    print(n, out[n])
json.dump(out, open(f'{D}/index.json', 'w'))
