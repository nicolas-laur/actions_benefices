"""Suivi (flux optique dense DIS, médiane) d'un point du plateau du comptoir du prêteur, sous les pieds de Mister Coin, sur toutes les images du décor
d'origine dans le cadrage agrandi (×1,29 depuis le haut) : decors/preteur_pieds.json = [(x, y)] par image source. python3 suivi_comptoir.py x0 y0 image_début image_fin -> decors/preteur_pieds_<début>.json"""
import os, sys, json, cv2, numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from bords import zoomed
x0, y0, i0, i1 = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
cap = cv2.VideoCapture(f'{D}/decors/decor_preteur.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, i0); prev = None; out = [(x0, y0)]; k = i0
while True:                                                          # flux dense (le bois du plateau a peu de coins à suivre) : médiane dans une boîte sous les pieds
    ok, f = cap.read()
    if not ok or k > i1: break
    k += 1
    g = cv2.cvtColor(zoomed(f, 1.29), cv2.COLOR_BGR2GRAY)
    if prev is not None:
        F = DIS.calc(prev, g, None); x, y = out[-1]; xa, xb, ya, yb = int(max(0, x-200)), int(min(1080, x+200)), int(max(0, y-60)), int(min(1920, y+60))
        d = np.median(F[ya:yb, xa:xb].reshape(-1, 2), 0); out.append((x+float(d[0]), y+float(d[1])))
    prev = g
json.dump(out, open(f'{D}/decors/preteur_pieds_{i0}.json', 'w'))
for i in range(0, len(out), 20): print(i0+i, [int(v) for v in out[i]])
