"""Suivi des plaques de laiton de la toise (points posés à la main sur l'image 0, transformation de la planche suivie image par image,
lissée) : decors/plaques_<nom>.json = {plaque: [[x, y] par image source]} en coordonnées 1080×1920."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '../../lib'); import coin_integration as CI
# bord supérieur avant de chaque plaque à l'image 0 (mesuré sur la grille), zone de la planche suivie
P0 = {'toise_bas': {'b': (600, 1128), 'h': (600, 452)},
      'toise_milieu': {'b': (600, 1468)},
      'toise_haut': {'b': (615, 1478), 'h': (615, 700)}}
ZONE = {'toise_bas': (420, 0, 900, 1500), 'toise_milieu': (380, 0, 900, 1920), 'toise_haut': (380, 0, 900, 1920)}
NMAX = {'toise_bas': 151, 'toise_milieu': 127, 'toise_haut': 143}
for n, pts in P0.items():
    cap = cv2.VideoCapture(f'decors/decor_{n}.mp4'); fr = []
    while len(fr) < NMAX[n]:
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(cv2.resize(f, (1080, 1920), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
    out = {}
    for k, p in pts.items():
        P, S = CI.suivi_surface(fr, p, ZONE[n], lissage=9); out[k] = P.round(1).tolist()
        print(n, k, 'y:', ' '.join(f'{int(y)}' for y in P[::10, 1]))
    json.dump(out, open(f'decors/plaques_{n}.json', 'w'))
