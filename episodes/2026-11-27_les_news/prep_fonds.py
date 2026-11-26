"""Préparation des fonds Gemini du 27/11 (fonds/src/ → fonds/) : Gemini a laissé des bandes unies.
Bande en bas (couverture, phare) : on complète par un reflet flouté et assombri du sol mouillé ou de la mer (zone de Mister Coin, assombrie par fond()).
Bande au milieu (port, fête foraine) : on retire la bande et on raccorde le haut et le bas de l'image (fondu de 40 lignes) ; fond() recadre ensuite. Le « 1 » du podium (Dell) est effacé (pas de chiffre dans les décors)."""
import cv2, numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
COUPE = {'couverture': 2143, 'huang': 2082}                                    # première ligne de la bande unie (détectée : écart-type < 6 sur ≥ 60 lignes)
BANDE = {'douane': (1991, 2297), 'cac40': (1904, 2144)}                          # bande unie au milieu : début, fin
def reflet(a, y):
    H = a.shape[0]; n = H-y; haut = a[:y]
    m = haut[y-n:][::-1].astype(np.float32)                                       # miroir des n lignes au-dessus de la coupe
    m = cv2.GaussianBlur(m, (0, 0), 5)*np.linspace(.92, .7, n)[:, None, None]
    out = a.copy(); out[y:] = m.clip(0, 255).astype(np.uint8)
    return out
def recoud(a, y0, y1, k=40):
    h, b = a[:y0].astype(np.float32), a[y1:].astype(np.float32)
    w = np.linspace(0, 1, k)[:, None, None]; joint = h[-k:]*(1-w)+b[:k]*w
    return np.concatenate([h[:-k], joint, b[k:]]).astype(np.uint8)
for f in sorted(os.listdir(f'{D}/fonds/src')):
    n = f[5:-4]; a = cv2.imread(f'{D}/fonds/src/{f}')
    if n in COUPE: a = reflet(a, COUPE[n])
    if n in BANDE: a = recoud(a, *BANDE[n])
    if n == 'dell':
        m = np.zeros(a.shape[:2], np.uint8); m[470:524, 1068:1108] = 255; a = cv2.inpaint(a, m, 7, cv2.INPAINT_TELEA)
    cv2.imwrite(f'{D}/fonds/{f}', a, [cv2.IMWRITE_JPEG_QUALITY, 95])
print('ok')
