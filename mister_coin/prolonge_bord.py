"""Prolonge un gros plan détouré dont un bras sort du cadre de l'image Gemini (coupé net au bord) : agrandit la toile de M pixels à gauche
et à droite, puis redessine, rangée par rangée, la partie du bras hors cadre. Le contour extérieur est extrapolé par une parabole calée
sur le contour visible juste au-dessus et juste au-dessous de la coupe ; le remplissage reprend la couleur du bord, puis le trait sombre.
python3 mister_coin/prolonge_bord.py mister_coin/gros_plans/couv_<expression>.png"""
import sys, numpy as np
from PIL import Image
M, TRAIT, MARGE = 120, 20, 70
def runs(col):
    ys = np.where(col)[0]
    if not len(ys): return []
    out, st, pv = [], ys[0], ys[0]
    for y in ys[1:]:
        if y != pv+1: out.append((st, pv)); st = y
        pv = y
    return out+[(st, pv)]
def prolonge(p):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32); h, w = a.shape[:2]
    b = np.zeros((h, w+2*M, 4), np.float32); b[:, M:M+w] = a
    for cote in (+1, -1):
        bx = M+w-1 if cote > 0 else M                                    # colonne du bord coupé, dans la nouvelle toile
        for (y0, y1) in runs(b[:, bx, 3] > 128):
            if y1-y0 < 30: continue
            # contour extérieur visible juste au-dessus et au-dessous de la coupe
            pts = []
            for y in list(range(max(0, y0-MARGE), y0))+list(range(y1+1, min(h, y1+1+MARGE))):
                xs = np.where(b[y, :, 3] > 128)[0]
                if not len(xs): continue
                xe = xs.max() if cote > 0 else xs.min()
                if abs(xe-bx) < 90: pts.append((y, xe))
            if len(pts) < 10: continue
            Y, X = np.array(pts, float).T; c = np.polyfit(Y, X, 2)
            trait = np.median(b[y1-5:y1+5, bx-TRAIT*cote if cote > 0 else bx, :3], 0) if False else np.array([50, 22, 18], np.float32)
            for y in range(y0, y1+1):
                xe = np.polyval(c, y); ext = (xe-bx)*cote                  # avancée du contour au-delà du bord
                if ext <= 0: continue
                ext = min(ext, M-2); fill = b[y, bx, :3].copy()
                for k in range(1, int(np.ceil(ext))+1):
                    x = bx+cote*k; d = ext-k                               # distance au contour extérieur
                    colr = trait if d < TRAIT else fill
                    al = 255*min(1.0, d+1)
                    b[y, x, :3] = colr; b[y, x, 3] = al
    Image.fromarray(b.clip(0, 255).astype(np.uint8), 'RGBA').save(p); print('ok', p, b.shape[1], 'px de large')
if __name__ == '__main__': prolonge(sys.argv[1])
