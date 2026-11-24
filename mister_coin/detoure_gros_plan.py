"""Détourage d'un gros plan de Mister Coin sur fond vert (Gemini) en PNG transparent, sans manger les contours sombres ni les bras.
Masque par dominance du vert (G − max(R, B)), bord adouci, débordement vert retiré, seule la plus grande zone opaque est gardée.
python3 mister_coin/detoure_gros_plan.py source.jpg mister_coin/gros_plans/couv_<expression>.png"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
def detoure(src, dst):
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    vert = G-np.maximum(R, B)                                            # fond : fortement vert ; personnage (or, blanc, brun, contours) : négatif ou faible
    al = 1-np.clip((vert-25)/(70-25), 0, 1)
    lab, n = ndimage.label(al > .5); keep = lab == 1+np.argmax(ndimage.sum(al > .5, lab, range(1, n+1)))
    keep = ndimage.binary_fill_holes(keep); al = al*ndimage.binary_dilation(keep, iterations=3)
    G2 = np.minimum(G, np.maximum(R, B)+8)                               # débordement vert sur les bords
    out = np.dstack([R, np.where(al < .999, G2, G), B, al*255]).clip(0, 255).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(dst); print('ok', dst)
if __name__ == '__main__': detoure(sys.argv[1], sys.argv[2])
