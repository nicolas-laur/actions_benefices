"""Répare couv_victoire.png : le poing droit et son bras sont coupés par le bord de l'image source.
On reconstruit le côté droit avec le poing et le bras gauches (complets) retournés en miroir, posés sur le droit, cachés derrière la pièce,
sur une toile élargie de PAD px à droite."""
from PIL import Image; import numpy as np, cv2, sys
import os; SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'couv_victoire_origine.png')   # pose d'origine, coupée au bord
g=np.asarray(Image.open(SRC)).astype(np.float32); H,W=g.shape[:2]; a=g[...,3]
DX=int(sys.argv[1]) if len(sys.argv)>1 else -10; DY=int(sys.argv[2]) if len(sys.argv)>2 else 58
PAD=220
# poing + bras gauches : composante jusqu'à 1800, puis bras seul (colonnes 0-170) jusqu'en bas
m=np.zeros((H,W),bool)
sub=(a[1100:1800,:330]>20).astype(np.uint8); n,lab=cv2.connectedComponents(sub); m[1100:1800,:330]=lab==lab[200,40]
sub=(a[1790:,:170]>20).astype(np.uint8); n,lab=cv2.connectedComponents(sub); k=lab[5,np.nonzero(sub[5])[0][0]]; m[1790:,:170]|=lab==k
patch=g.copy(); patch[...,3]*=m
patch=patch[:, ::-1]                                    # miroir : colonne x -> W-1-x
out=np.zeros((H,W+PAD,4),np.float32); out[:,:W]=g
# position : le poing miroir recouvre le poing droit (décalage DX, DY)
M=np.float32([[1,0,DX],[0,1,DY]])
P=cv2.warpAffine(patch,M,(W+PAD,H),flags=cv2.INTER_LINEAR)
# caché derrière la pièce (ellipse) et derrière le chapeau (on garde l'original là où il est opaque et brun foncé ? non : poing devant le chapeau dans l'original)
# silhouette exacte de la pièce (tranche striée comprise) : sur chaque ligne, du centre de la pièce vers la droite, jusqu'au premier
# pixel transparent (un espace sépare toujours le bras de la pièce dans l'original)
a0_=out[...,3]>20; droite=np.full(H, -1)
for r in range(1290, 2330):
    row=a0_[r, 775:]; z=np.nonzero(~row)[0]; droite[r]=775+(z[0] if len(z) else row.size)-1
rr_=np.arange(1290,2330); dd=droite[1290:2330].astype(float)
ok=dd<np.percentile(dd,60)+40                                   # rangées où le balayage n'a pas filé dans le bras
A_=np.c_[rr_[ok]**2, rr_[ok], np.ones(ok.sum())]; cf=np.linalg.lstsq(A_, (dd[ok]-775)**2, rcond=None)[0]
fit=775+np.sqrt(np.clip(A_.dot(cf) if False else np.c_[rr_**2, rr_, np.ones(rr_.size)].dot(cf), 0, None))
droite[1290:2330]=np.minimum(dd, fit+8).astype(int)
coin=np.zeros((H,W+PAD),bool)
for r in range(1290, 2330): coin[r, :droite[r]+1]=True
# effacer l'ancien poing et bras droits coupés : tout ce qui est à droite de la pièce, sous le chapeau
old=a0_&~coin; old[:1330]=False; old[:, :1150]=False
old[1230:1330, 1350:]=a0_[1230:1330, 1350:]                     # haut de l'ancien poing, à droite du bord du chapeau
out[...,3]=np.where(old,0,out[...,3])
# le poing passe devant (comme dans l'original, devant le bord du chapeau) ; le bras, sous le poignet, passe DERRIÈRE la pièce :
# il est masqué par tout ce qui est opaque dans l'original (tranche striée comprise), pour rejoindre la pièce par son contour
POIGNET=1560+DY
derriere=np.zeros((H,W+PAD),bool); derriere[POIGNET:]=True
pa=P[...,3]/255
pa=np.where(derriere, pa*(~coin), pa)
al=pa[...,None]; a0=out[...,3:4]/255
out[...,:3]=out[...,:3]*(1-al)+P[...,:3]*al
out[...,3]=np.maximum(out[...,3], pa*255)
# le poing gauche touchait le bord gauche (contour extérieur coupé net) : on referme le côté coupé par une demi-ellipse
# remplie de blanc de gant et cerclée du même contour brun foncé
edge=W-1+DX
col_=P[1150+DY:1560+DY, edge-4, 3]>20; rr=np.nonzero(col_)[0]+1150+DY; ra, rb=rr.min(), rr.max()
cy=(ra+rb)/2; hy=(rb-ra)/2+2; bul=50; th=12; X0=edge-36
yy2,xx2=np.mgrid[0:H,0:W+PAD].astype(np.float32)
inside=(((xx2-X0)/bul)**2+((yy2-cy)/hy)**2<1)&(xx2>X0)
ring=(((xx2-X0)/(bul+th))**2+((yy2-cy)/(hy+th))**2<1)&(xx2>X0)&~inside
zone=out[ra:rb, X0-60:X0, :3].reshape(-1,3); lum=zone.sum(1); GLOVE=np.median(zone[lum>np.percentile(lum,70)],0); OUT=np.array([46,22,22],np.float32)
fi=cv2.GaussianBlur(inside.astype(np.float32),(0,0),4)*(xx2>X0-12); fi=np.maximum(fi, inside)   # raccord fondu au début du remplissage
out[...,:3]=out[...,:3]*(1-fi[...,None])+GLOVE*fi[...,None]; out[...,3]=np.maximum(out[...,3], inside*255.)
out[ring,:3]=OUT; out[ring,3]=255

Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(os.path.join(os.path.dirname(SRC), 'couv_victoire.png'))
