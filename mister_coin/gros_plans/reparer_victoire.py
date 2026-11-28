"""Répare couv_victoire.png (pose « victoire » des couvertures) : dans l'image d'origine (couv_victoire_origine.png), le poing droit
est coupé par le bord droit et le côté extérieur du bras droit aussi (sur une vingtaine de pixels).
1. Le poing droit est remplacé par le poing gauche retourné en miroir (le gauche n'a perdu que l'extrême bord de son contour)
   posé pour que sa manchette recouvre le haut du bras d'origine.
2. Le bras droit d'origine est gardé tel quel (il passe devant la tranche de la pièce) ; son côté extérieur coupé est prolongé
   (même couleur, largeur mesurée plus bas où le bras est complet) et cerclé du même contour brun foncé.
Sortie : couv_victoire.png, sur une toile élargie de PAD px à droite (gros_plan.coller recadre sur la silhouette).
usage : python3 reparer_victoire.py"""
import os
from PIL import Image
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
g = np.asarray(Image.open(f'{HERE}/couv_victoire_origine.png')).astype(np.float32); H, W = g.shape[:2]
PAD = 160; DX, DY = 47, 90                      # décalage du poing miroir : sa manchette tombe sur le haut du bras droit d'origine
OUT = np.array([46, 22, 22], np.float32)       # brun foncé des contours
out = np.zeros((H, W+PAD, 4), np.float32); out[:, :W] = g
a0 = out[..., 3] > 20

# silhouette de la pièce (tranche comprise) : de son centre vers la droite jusqu'au premier pixel transparent, bornée par un ajustement
droite = np.full(H, -1)
for r in range(1290, 2330):
    row = a0[r, 775:]; z = np.nonzero(~row)[0]; droite[r] = 775+(z[0] if len(z) else row.size)-1
rr = np.arange(1290, 2330); dd = droite[1290:2330].astype(float); ok = dd < np.percentile(dd, 60)+40
cf = np.linalg.lstsq(np.c_[rr[ok]**2, rr[ok], np.ones(ok.sum())], (dd[ok]-775)**2, rcond=None)[0]
fit = 775+np.sqrt(np.clip(np.c_[rr**2, rr, np.ones(rr.size)].dot(cf), 0, None)); droite[1290:2330] = np.minimum(dd, fit+8).astype(int)

# 1. effacer l'ancien poing droit (à droite de la pièce, au-dessus du bras) et le haut qui dépasse à droite du bord du chapeau
old = np.zeros((H, W+PAD), bool)
for r in range(1330, 1600): old[r, max(1200 if r < 1450 else 1150, droite[r]+1):] = True   # le bord du chapeau (jusqu'à 1200) est gardé
old[1230:1330, 1300:] = True
out[..., 3] = np.where(old & a0, 0, out[..., 3])

# 2. prolonger le côté extérieur du bras droit coupé (lignes où il touche le bord) : bord extérieur = bord intérieur + largeur du bras
#    complet (mesurée plus bas, ≈ 100 px contour compris), courbe lissée ; on repeint aussi les derniers pixels anti-crénelés de la coupure
bras = {}
for r in range(1585, 1800):
    xs = np.nonzero(a0[r, 1290:W])[0]
    if len(xs) and xs[-1]+1290 >= W-4: bras[r] = xs[0]+1290                       # bord intérieur du bras
rs = np.array(sorted(bras)); xin = np.array([bras[r] for r in rs], float)
xin = np.convolve(np.pad(xin, 15, mode='edge'), np.ones(31)/31, 'valid')
xout = xin+100
for r, xo in zip(rs, xout):
    xo_i = int(round(xo)); x_f = int(round(xo-12))
    if xo_i <= W-10: continue
    c = out[r, W-16, :3].copy()
    out[r, W-10:max(W-10, x_f), :3] = c; out[r, W-10:max(W-10, x_f), 3] = 255        # remplissage, teinte du bras près du bord
    out[r, x_f:xo_i, :3] = OUT; out[r, x_f:xo_i, 3] = 255                            # contour
    fr = xo-xo_i+.5
    if 0 < fr < 1: out[r, xo_i, :3] = OUT; out[r, xo_i, 3] = 255*fr                  # bord extérieur adouci
    out[r, xo_i+1:W+PAD, 3] = 0
# 3. poing gauche (avec un peu de poignet) retourné en miroir, posé par-dessus
m = np.zeros((H, W), bool)
sub = (g[1100:1535, :330, 3] > 20).astype(np.uint8); n, lab = cv2.connectedComponents(sub); m[1100:1535, :330] = lab == lab[200, 40]
patch = g.copy(); patch[..., 3] *= m; patch = patch[:, ::-1]
P = cv2.warpAffine(patch, np.float32([[1, 0, DX], [0, 1, DY]]), (W+PAD, H), flags=cv2.INTER_LINEAR)
pa = P[..., 3:4]/255; out[..., :3] = out[..., :3]*(1-pa)+P[..., :3]*pa; out[..., 3] = np.maximum(out[..., 3], P[..., 3])
# (son côté extérieur n'avait perdu que l'extrême bord de son contour : rien à refermer, le contour reste visible)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(f'{HERE}/couv_victoire.png')
