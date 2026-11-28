"""Répare couv_victoire.png : le poing droit et son bras sont coupés par le bord de l'image source.
On reconstruit le côté droit avec le poing et le bras gauches (complets) retournés en miroir, posés sur le droit, cachés derrière la pièce,
sur une toile élargie de PAD px à droite."""
from PIL import Image; import numpy as np, cv2, sys
import os; SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'couv_victoire_origine.png')   # pose d'origine, coupée au bord
g=np.asarray(Image.open(SRC)).astype(np.float32); H,W=g.shape[:2]; a=g[...,3]
DX=int(sys.argv[1]) if len(sys.argv)>1 else 0; DY=int(sys.argv[2]) if len(sys.argv)>2 else 76
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
yy,xx=np.mgrid[0:H,0:W+PAD]; coin=((xx-775)/520.)**2+((yy-1792)/510.)**2<1
pa=P[...,3]/255*(~coin)
# effacer l'ancien poing/bras droit coupé hors pièce et hors chapeau : pixels de l'original à droite de 1150, lignes 1230-2300, non bruns (chapeau)
o=out[...,:3]; br=(o[...,0]<120)&(o[...,1]<90)&(o[...,2]<80)&(o[...,0]>40)   # brun du chapeau
old=np.zeros((H,W+PAD),bool); old[1230:2300,1150:W]=True; old&=~coin
hat=np.zeros((H,W+PAD),bool); hat[:1330,:]=True                              # le chapeau est au-dessus de 1330
old&=~hat
out[...,3]=np.where(old,0,out[...,3])
al=pa[...,None]; out[...,:3]=out[...,:3]*(1-al)+P[...,:3]*al; out[...,3]=np.maximum(out[...,3],P[...,3]*(~coin))
# le poing gauche touchait le bord gauche (contour extérieur coupé net) : on referme le côté coupé par une demi-ellipse
# remplie de blanc de gant et cerclée du même contour brun foncé
edge=W-1+DX
col_=out[1150+DY:1560+DY, edge-4, 3]>20; rr=np.nonzero(col_)[0]+1150+DY; ra, rb=rr.min(), rr.max()
cy=(ra+rb)/2+2; hy=(rb-ra)/2+8; bul=50; th=12; X0=edge-36
yy2,xx2=np.mgrid[0:H,0:W+PAD].astype(np.float32)
inside=(((xx2-X0)/bul)**2+((yy2-cy)/hy)**2<1)&(xx2>X0)
ring=(((xx2-X0)/(bul+th))**2+((yy2-cy)/(hy+th))**2<1)&(xx2>X0)&~inside
zone=out[ra:rb, X0-60:X0, :3].reshape(-1,3); lum=zone.sum(1); GLOVE=np.median(zone[lum>np.percentile(lum,70)],0); OUT=np.array([46,22,22],np.float32)
out[inside,:3]=GLOVE; out[inside,3]=255
out[ring,:3]=OUT; out[ring,3]=255

Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(os.path.join(os.path.dirname(SRC), 'couv_victoire.png'))
