"""Suivi du mur sur la vidéo d'ORIGINE (24 i/s, vraies images) : points KLT image par image, homographies chaînées,
trajectoire des coins lissée par spline, puis rééchantillonnée sur la version ralentie (×4,25, 30 i/s).
Sortie : wallH.npy (une homographie par image ralentie, image 0 -> image t, en pixels 1080×1920)."""
import cv2, numpy as np
from scipy.interpolate import UnivariateSpline
D = '/home/claude/actu'; SC = 1.5; SLOW = 4.25
cap = cv2.VideoCapture(f'{D}/studio.mp4'); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
print('images', len(frames))
POLY = np.float32([[200, 430], [1080, 360], [1080, 900], [200, 905]])/SC
Q0 = np.float32([[258, 582], [1062, 524], [1062, 874], [258, 880]])/SC
Htot = np.eye(3); Hs = [Htot.copy()]
for i in range(1, len(frames)):
    a, b = frames[i-1], frames[i]
    poly = cv2.perspectiveTransform(POLY[None], Htot)[0]
    m = np.zeros_like(a); cv2.fillPoly(m, [poly.astype(np.int32)], 255)
    ch = cv2.perspectiveTransform(np.float32([[[500/SC, 880/SC], [830/SC, 1000/SC]]]), Htot)[0]      # fauteuils exclus
    cv2.rectangle(m, tuple(ch[0].astype(int)-20), tuple(ch[1].astype(int)+20), 0, -1)
    p0 = cv2.goodFeaturesToTrack(a, 600, .01, 6, mask=m)
    p1, st, _ = cv2.calcOpticalFlowPyrLK(a, b, p0, None, winSize=(21, 21), maxLevel=3)
    p0b, st2, _ = cv2.calcOpticalFlowPyrLK(b, a, p1, None, winSize=(21, 21), maxLevel=3)     # contrôle aller-retour
    good = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(p0b-p0, axis=2)[:, 0] < .5)
    Hstep, inl = cv2.findHomography(p0[good], p1[good], cv2.RANSAC, 1.0)
    if Hstep is None: Hstep = np.eye(3)
    Htot = Hstep @ Htot; Hs.append(Htot.copy())
    if i % 40 == 0: print(i, int(good.sum()), int(inl.sum()) if inl is not None else 0, flush=True)
Hs = np.array(Hs)
q = np.array([cv2.perspectiveTransform(Q0[None], H)[0] for H in Hs])*SC        # coins en pixels 1080×1920
P0 = Q0*SC
t = np.arange(len(q))/24.0
n_slow = len([1 for _ in range(int(len(q)/24*SLOW*30)+1)])
ts = np.arange(n_slow)/30.0/SLOW
qs = np.zeros((n_slow, 4, 2))
for k in range(4):
    for d in range(2):
        sp = UnivariateSpline(t, q[:, k, d], k=4, s=len(t)*.25)       # lissage : supprime le tremblement, garde le mouvement de caméra
        qs[:, k, d] = sp(np.clip(ts, 0, t[-1]))
H_out = np.array([cv2.getPerspectiveTransform(P0, c.astype(np.float32)) for c in qs])
np.save(f'{D}/wallH.npy', H_out)
dd = np.diff(qs, 1, axis=0); print('ok', n_slow, 'saut max par image', np.abs(dd).max(), 'moyen', np.abs(dd).mean())
