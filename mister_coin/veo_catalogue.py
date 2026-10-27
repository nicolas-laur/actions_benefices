"""Catalogue de la banque de clips Veo : analyse automatique de chaque nouveau clip déposé dans veo/.
usage : python3 veo_catalogue.py            -> analyse les clips absents de veo/catalogue.json et l'enregistre
Pour chaque clip : format, largeur de la pièce, centre x et pieds (pour la mise à l'échelle commune),
et les plages d'images où il parle (bouche animée) ou se tait, mesurées sur l'ouverture de la bouche."""
import os, json, subprocess, sys
import numpy as np
from scipy import ndimage
D = os.path.dirname(os.path.abspath(__file__)); V = f'{D}/veo'; CAT = f'{V}/catalogue.json'
def frames(path):
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path],
                                   capture_output=True, text=True).stdout.strip().split(','))
    p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return (w, h), np.frombuffer(p, np.uint8).reshape(-1, h, w, 3)
def analyse(path):
    (w, h), F = frames(path); ws, cxs, feet, act, hts = [], [], [], [], []
    for a in F:
        a = a.astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
        m = (R > 200) & (G > 140) & (G < 220) & (B < 110) & (R-B > 110); lab, n = ndimage.label(m)
        fg = (G-np.maximum(R, B)) < 40; yy = np.where(fg.any(1))[0]
        if n == 0 or len(yy) == 0: ws.append(0); cxs.append(-1); feet.append(-1); act.append(0); continue
        k = 1+np.argmax(ndimage.sum(m, lab, range(1, n+1))); ys, xs = np.where(lab == k)
        cw = xs.max()-xs.min(); cx = (xs.min()+xs.max())//2; top = ys.min()
        box = a[top+int(cw*.62):top+int(cw*.85), max(0, cx-int(cw*.22)):cx+int(cw*.16)]
        r, g, b = box[..., 0], box[..., 1], box[..., 2]
        hts.append(int(yy.max()-yy.min())); ws.append(int(cw)); cxs.append(int(cx)); feet.append(int(yy.max())); act.append(int((((r < 140) & (g < 90)) | ((r > 170) & (g < 120) & (b < 120))).sum()))
    ws_ = np.array(ws); ok = ws_ > np.percentile(ws_, 50)*.8
    cw = int(np.median(ws_[ok])); act = np.array(act, float)/max(1, cw*cw)
    base = np.percentile(act, 10); var = np.abs(np.diff(act, prepend=act[0]))
    talk = np.convolve((var > .01) | (act > base*1.6), np.ones(9)/9, 'same') > .3        # bouche qui bouge
    runs, i = [], 0
    while i < len(talk):
        j = i
        while j < len(talk) and talk[j] == talk[i]: j += 1
        runs.append((bool(talk[i]), i, j-1)); i = j
    parle = [(a, b) for t, a, b in runs if t and b-a > 24]
    silence = [(a, b) for t, a, b in runs if not t and b-a > 10]
    return dict(format=[w, h], piece=cw, hauteur=int(np.median(np.array(hts)[:30] if len(hts) > 30 else hts)),   # hauteur en pose neutre (début du clip) : sert à l'échelle commune
                cx=int(np.median(np.array(cxs)[ok])), pieds=int(np.median(np.array(feet)[ok])),
                images=len(F), parle=parle, silence=silence)
if __name__ == '__main__':
    cat = json.load(open(CAT)) if os.path.exists(CAT) else {}
    for f in sorted(os.listdir(V)):
        if f.endswith('.mp4') and f[:-4] not in cat and not f.startswith(('clip_', 'test')):
            cat[f[:-4]] = analyse(f'{V}/{f}'); print(f[:-4], cat[f[:-4]])
    json.dump(cat, open(CAT, 'w'), indent=1, ensure_ascii=False)
