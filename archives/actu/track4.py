"""Suivi des 4 croisements de jointures du panneau GAUCHE du mur (plan unique), par corrélation sur la carte des lignes sombres
(insensible au dégradé animé des écrans), puis trajectoires lissées par polynôme de degré 3. Sortie : wallH.npy (image 0 -> t)."""
import cv2, numpy as np
D = '/home/claude/actu'; N = 1265
P0 = np.float32([[477, 702], [705, 698], [705, 833], [477, 834]])
def dark(i):
    im = cv2.imread(f'{D}/bg30/{i:04d}.jpg', 0).astype(np.float32)
    return np.clip(cv2.GaussianBlur(im, (0, 0), 6)-im, 0, None)
d0 = dark(0); R = 22
# affiner les points de départ sur la carte : maximum de « croix sombre » autour de la position estimée
def cross_score(dm, x, y):
    return dm[y-1:y+2, x-R:x+R].sum()+dm[y-R:y+R, x-1:x+2].sum()
P = []
for x, y in P0.astype(int):
    best = max(((cross_score(d0, x+dx, y+dy), x+dx, y+dy) for dx in range(-6, 7) for dy in range(-6, 7)))
    P.append((best[1], best[2]))
P = np.float32(P); print('départ', P.tolist())
tpl = [d0[int(y)-R:int(y)+R+1, int(x)-R:int(x)+R+1].copy() for x, y in P]
track = [P.copy()]; cur = P.copy(); S = 10
for i in range(1, N):
    dm = dark(i); new = []
    for k, (x, y) in enumerate(cur):
        xi, yi = int(round(x)), int(round(y))
        win = dm[yi-R-S:yi+R+S+1, xi-R-S:xi+R+S+1]
        res = cv2.matchTemplate(win, tpl[k], cv2.TM_CCOEFF_NORMED)
        _, mx, _, ml = cv2.minMaxLoc(res); px, py = ml
        def sub(a, b, c): d = a-2*b+c; return 0 if abs(d) < 1e-6 else .5*(a-c)/d
        ox = sub(res[py, px-1], res[py, px], res[py, px+1]) if 0 < px < res.shape[1]-1 else 0
        oy = sub(res[py-1, px], res[py, px], res[py+1, px]) if 0 < py < res.shape[0]-1 else 0
        new.append((xi-S+px+ox, yi-S+py+oy))
    cur = np.float32(new); track.append(cur.copy())
    if i % 200 == 0: print(i, cur.round(1).tolist(), flush=True)
q = np.array(track); t = np.arange(N)/N; fit = np.zeros_like(q)
for k in range(4):
    for d in range(2): fit[:, k, d] = np.polyval(np.polyfit(t, q[:, k, d], 3), t)
print('écart brut/ajusté : moyen', np.abs(q-fit).mean().round(2), 'max', np.abs(q-fit).max().round(2))
np.save(f'{D}/wall_pts.npy', fit); np.save(f'{D}/wall_pts_raw.npy', q)
H = np.array([cv2.getPerspectiveTransform(P, f.astype(np.float32)) for f in fit]); np.save(f'{D}/wallH.npy', H); np.save(f'{D}/wall_P0.npy', P)
print('ok')
