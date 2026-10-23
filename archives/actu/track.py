"""Suivi du mur d'écrans du plateau : homographie image 0 -> image t (SIFT + RANSAC sur la zone du mur et son habillage bois).
Sortie : wallH.npy (N×3×3). usage : python track.py"""
import cv2, numpy as np, os, json
D = '/home/claude/actu'
S = .5
def gray(i): return cv2.cvtColor(cv2.resize(cv2.imread(f'{D}/bg30/{i:04d}.jpg'), None, fx=S, fy=S, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
# zone du plan du mur dans l'image 0 (pleine résolution) : écrans + bandeau bois au-dessus, sans les fauteuils ni le bureau
poly0 = np.array([[200, 430], [1080, 360], [1080, 900], [200, 905]], np.float32)
sift = cv2.SIFT_create(nfeatures=3000, contrastThreshold=.02)
g0 = gray(0); m0 = np.zeros_like(g0); cv2.fillPoly(m0, [(poly0*S).astype(np.int32)], 255)
# on exclut les fauteuils (dépassent devant le bas du mur)
cv2.rectangle(m0, (int(500*S), int(880*S)), (int(830*S), int(1000*S)), 0, -1)
k0, d0 = sift.detectAndCompute(g0, m0)
bf = cv2.BFMatcher(cv2.NORM_L2)
n = len([f for f in os.listdir(f'{D}/bg30') if f.endswith('.jpg')])
Hs = []; Hprev = np.eye(3)
for i in range(n):
    g = gray(i)
    # masque suivant : le polygone transporté par la dernière homographie, un peu élargi
    poly = cv2.perspectiveTransform(poly0[None], Hprev)[0]
    m = np.zeros_like(g); cv2.fillPoly(m, [(poly*S).astype(np.int32)], 255); m = cv2.dilate(m, np.ones((15, 15), np.uint8))
    k, d = sift.detectAndCompute(g, m)
    H = Hprev
    if d is not None and len(k) > 20:
        mt = bf.knnMatch(d0, d, k=2); good = [a for a, b in mt if a.distance < .72*b.distance]
        if len(good) > 25:
            p0 = np.float32([k0[a.queryIdx].pt for a in good])/S; p1 = np.float32([k[a.trainIdx].pt for a in good])/S
            Hn, inl = cv2.findHomography(p0, p1, cv2.RANSAC, 3.0)
            if Hn is not None and inl.sum() > 20: H = Hn
    Hs.append(H); Hprev = H
    if i % 50 == 0: print(i, len(k) if d is not None else 0, flush=True)
Hs = np.array(Hs)
# lissage temporel (le mouvement de caméra est lent et continu)
from scipy.ndimage import gaussian_filter1d
corners = np.array([cv2.perspectiveTransform(poly0[None], H)[0] for H in Hs])
cs = gaussian_filter1d(corners, 3, axis=0)
Hsm = np.array([cv2.getPerspectiveTransform(poly0, c.astype(np.float32)) for c in cs])
np.save(f'{D}/wallH.npy', Hsm); print('ok', n)
