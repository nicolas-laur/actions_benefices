"""Bord avant du comptoir (prêteur) et de l'établi (garage), image par image du décor d'origine, dans le cadrage agrandi depuis le haut
(sr_decors.ZOOM_TOP) : y à l'écran sur une bande centrale, lissé par un polynôme ; decors/<nom>_bord.json. python3 bords.py [planche]"""
import os, sys, json, cv2, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
Z = {'preteur': 1.12, 'garage': 1.22}; ZONE = {'preteur': (1300, 1880), 'garage': (1450, 1800)}; XB = (440, 640)
def zoomed(f, z):
    f = cv2.resize(f, (1080, 1920)); g = cv2.resize(f, (int(1080*z), int(1920*z))); x0 = (g.shape[1]-1080)//2; return g[:1920, x0:x0+1080]
def track(name):
    cap = cv2.VideoCapture(f'{D}/decors/decor_{name}.mp4'); E = []; y0, y1 = ZONE[name]
    while True:
        ok, f = cap.read()
        if not ok: break
        g = cv2.cvtColor(zoomed(f, Z[name]), cv2.COLOR_BGR2GRAY).astype(float)
        pr = np.convolve(g[y0:y1, XB[0]:XB[1]].mean(1), np.ones(9)/9, 'same'); d = pr[8:]-pr[:-8]; E.append(y0+4+int(np.argmin(d[10:-10]))+10)
    c = np.polyfit(np.arange(len(E)), E, 3); json.dump({'poly': c.tolist(), 'brut': E}, open(f'{D}/decors/{name}_bord.json', 'w')); return np.poly1d(c), E
if __name__ == '__main__':
    for n in Z:
        p, E = track(n); print(n, [int(p(i)) for i in (0, 60, 120, 180, 239)], 'écart max', int(max(abs(p(i)-e) for i, e in enumerate(E))))
        if len(sys.argv) > 1:
            cap = cv2.VideoCapture(f'{D}/decors/decor_{n}.mp4'); fr = []
            for i in (0, 120, 239):
                cap.set(1, i); ok, f = cap.read(); f = zoomed(f, Z[n]); y = int(p(i)); cv2.line(f, (0, y), (1080, y), (0, 0, 255), 4); fr.append(cv2.resize(f, (270, 480)))
            cv2.imwrite(f'{D}/tmp/bord_{n}.jpg', cv2.hconcat(fr))
