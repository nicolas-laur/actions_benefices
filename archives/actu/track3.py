"""Suivi du mur, version stable : homographies image à image (KLT + contrôle aller-retour) sur le décor ralenti,
puis chaque coin est ajusté par un polynôme de degré 3 dans le temps (le travelling est régulier : aucun tremblement possible)."""
import cv2, numpy as np
D = '/home/claude/actu'; N = 1265
POLY = np.float32([[200, 430], [1080, 360], [1080, 900], [200, 905]])
Q0 = np.float32([[258, 582], [1062, 524], [1062, 874], [258, 880]])
def g(i): return cv2.cvtColor(cv2.imread(f'{D}/bg30/{i:04d}.jpg'), cv2.COLOR_BGR2GRAY)
Htot = np.eye(3); qs = [Q0.copy()]; prev = g(0)
for i in range(1, N):
    cur = g(i)
    poly = cv2.perspectiveTransform(POLY[None], Htot)[0]
    m = np.zeros_like(prev); cv2.fillPoly(m, [poly.astype(np.int32)], 255)
    ch = cv2.perspectiveTransform(np.float32([[[480, 860], [850, 1020]]]), Htot)[0]
    cv2.rectangle(m, tuple(ch[0].astype(int)), tuple(ch[1].astype(int)), 0, -1)
    p0 = cv2.goodFeaturesToTrack(prev, 500, .01, 8, mask=m)
    p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, p0, None, winSize=(31, 31), maxLevel=3)
    pb, st2, _ = cv2.calcOpticalFlowPyrLK(cur, prev, p1, None, winSize=(31, 31), maxLevel=3)
    ok = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(pb-p0, axis=2)[:, 0] < .3)
    Hs, _ = cv2.findHomography(p0[ok], p1[ok], cv2.RANSAC, .8)
    if Hs is not None: Htot = Hs @ Htot
    qs.append(cv2.perspectiveTransform(Q0[None], Htot)[0]); prev = cur
    if i % 200 == 0: print(i, int(ok.sum()), flush=True)
q = np.array(qs); t = np.arange(N)/N
fit = np.zeros_like(q)
for k in range(4):
    for d in range(2):
        c = np.polyfit(t, q[:, k, d], 3); fit[:, k, d] = np.polyval(c, t)
print('écart brut/ajusté (px) : moyen', np.abs(q-fit).mean().round(2), 'max', np.abs(q-fit).max().round(2))
H_out = np.array([cv2.getPerspectiveTransform(Q0, c.astype(np.float32)) for c in fit])
np.save(f'{D}/wallH.npy', H_out)
d1 = np.abs(np.diff(fit, axis=0)).max(); print('ok, déplacement max par image', round(float(d1), 3))
