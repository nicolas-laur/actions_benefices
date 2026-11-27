"""Suivi des surfaces où Mister Coin se tient (sol du couloir et de l'horloge, seconde plaque de toise_milieu après le saut de plan) :
decors/sol_<nom>.json = {'p': [[x, y] par image source à partir de i0], 's': [échelle], 'i0': i0}"""
import sys, json, cv2, numpy as np
sys.path.insert(0, '../../lib'); import coin_integration as CI
JOBS = {'couloir': (0, 240, (540, 1690), (200, 1450, 880, 1920)),
        'horloge': (0, 240, (620, 1700), (150, 1600, 1080, 1920)),
        'toise_milieu_b2': (128, 175, (600, 1268), (380, 0, 900, 1920))}
for n, (i0, i1, p, z) in JOBS.items():
    cap = cv2.VideoCapture(f"decors/decor_{n.replace('_b2', '')}.mp4"); cap.set(cv2.CAP_PROP_POS_FRAMES, i0); fr = []
    for i in range(i0, i1):
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(cv2.resize(f, (1080, 1920), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB))
    P, S = CI.suivi_surface(fr, p, z, lissage=9)
    json.dump({'p': P.round(1).tolist(), 's': S.round(4).tolist(), 'i0': i0}, open(f'decors/sol_{n}.json', 'w'))
    print(n, 'y:', ' '.join(f'{int(y)}' for y in P[::10, 1]), '| échelle fin', S[-1].round(2))
