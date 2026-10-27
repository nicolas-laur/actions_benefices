"""Mister Coin en clips Veo (Gemini) : détourage du fond vert, mise à l'échelle commune, enchaînements en fondu, boucles.

    from veo_coin import VeoCoin
    mc = VeoCoin(planning=[(0.0, 'aristo_entre_gauche', 'une'), (10.0, 'aristo_parle_neutre', 'boucle'), …],
                 x=500, pieds=1725, largeur_piece=220)
    rgb, alpha = mc.layer(t)        # tableaux float32 1080×1920 (couleur 0-255, alpha 0-1) à composer sur le décor

Chaque clip est décrit dans CLIPS : (fichier, largeur de la pièce dans le clip, centre x de la pièce, y des pieds).
'une' : le clip est joué une fois puis reste sur sa dernière image ; 'boucle' : il recommence avec un fondu de FONDU secondes.
Pour les entrées, le bord gauche du clip est calé sur le bord de l'écran (ancre 'bord'), pour qu'il entre vraiment par le côté."""
import os, subprocess, functools
import numpy as np, cv2
D = os.path.dirname(os.path.abspath(__file__)); V = f'{D}/veo'
W, H = 1080, 1920; FONDU = .4; CLIP_FPS = 24
CLIPS = {'aristo_entre_gauche': ((1280, 720), 280, 637, 711, 'bord'),
         'aristo_parle_neutre': ((720, 1280), 347, 346, 1117, 'centre'),
         'aristo_parle_enthousiaste': ((720, 1280), 440, 343, 1143, 'centre')}

def _key(a):
    a = a.astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = 1-np.clip((ks-30)/60, 0, 1); al = cv2.GaussianBlur(al, (0, 0), .7)
    sp = ks > 0; a[..., 1] = np.where(sp, np.minimum(G, R*.75+B*.25), G); a[..., 2] = np.where(sp, np.minimum(B, R), B)
    dk = (a.sum(2) < 330) & (a[..., 2] > a[..., 0]*.8)          # traits sombres teintés de vert/bleu ramenés au brun
    a[..., 2] = np.where(dk, a[..., 0]*.55, a[..., 2]); a[..., 1] = np.where(dk, np.minimum(a[..., 1], a[..., 0]*.75), a[..., 1])
    return a, al

class VeoCoin:
    def __init__(self, planning, x=500, pieds=1725, largeur_piece=220, dossier=V):
        self.plan = sorted(planning); self.x, self.feet, self.cw, self.dir = x, pieds, largeur_piece, dossier
    @functools.lru_cache(maxsize=4)
    def _frames(self, name):
        """images du clip déjà mises à l'échelle finale (uint8), en mémoire"""
        (w, h), cw, cx, fy, anc = CLIPS[name]; s = self.cw/cw
        ws, hs = int(round(w*s/2))*2, int(round(h*s/2))*2
        p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{self.dir}/{name}.mp4', '-vf', f'scale={ws}:{hs}:flags=lanczos',
                            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
        F = np.frombuffer(p, np.uint8).reshape(-1, hs, ws, 3)
        ox = 0 if anc == 'bord' else self.x-cx*s                   # coin haut-gauche du clip à l'écran
        if anc == 'bord': self.x_bord = cx*s
        return F, (int(round(ox)), int(round(self.feet-fy*s)))
    def _clip_frame(self, name, u, mode):
        F, off = self._frames(name); n = len(F); dur = n/CLIP_FPS
        if mode == 'une': return [(F[min(n-1, int(u*CLIP_FPS))], 1.)], off
        per = dur-FONDU; k = u % per; i = int(k*CLIP_FPS)
        if u >= per and k < FONDU:                                   # fondu entre la fin et le début de la boucle
            j = min(n-1, int((k+per)*CLIP_FPS)); a = k/FONDU
            return [(F[j], 1-a), (F[i], a)], off
        return [(F[i], 1.)], off
    def _layer_one(self, name, u, mode):
        parts, (ox, oy) = self._clip_frame(name, u, mode)
        rgb = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
        for f, wgt in parts:
            a, m = _key(f); h, w = m.shape
            x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+w), min(H, oy+h)
            if x1 <= x0 or y1 <= y0: continue
            sa = a[y0-oy:y1-oy, x0-ox:x1-ox]; sm = m[y0-oy:y1-oy, x0-ox:x1-ox]*wgt
            rgb[y0:y1, x0:x1] += sa*sm[..., None]; al[y0:y1, x0:x1] += sm
        return rgb, al                                               # couleur prémultipliée
    def layer(self, t):
        """(couleur 0-255, alpha 0-1) de Mister Coin à l'instant t, avec fondu entre deux clips du planning"""
        cur = None
        for k, (t0, name, mode) in enumerate(self.plan):
            if t >= t0: cur = k
        if cur is None: return np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)
        t0, name, mode = self.plan[cur]; rgb, al = self._layer_one(name, t-t0, mode)
        if cur > 0 and t-t0 < FONDU:
            p0, pn, pm = self.plan[cur-1]; r2, a2 = self._layer_one(pn, t-p0, pm); a = (t-t0)/FONDU
            rgb, al = rgb*a+r2*(1-a), al*a+a2*(1-a)
        col = rgb/np.maximum(al, 1e-4)[..., None]
        return np.clip(col, 0, 255), np.clip(al, 0, 1)
    def feet_x(self, al):
        """centre des pieds (pour l'ombre) à partir du masque"""
        band = al[self.feet-60:self.feet+4]; cols = np.where(band.max(0) > .5)[0]
        return None if len(cols) == 0 else (cols.min()+cols.max())/2
