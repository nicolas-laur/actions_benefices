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
# zones où il parle (images) et où il se tait, mesurées sur l'ouverture de la bouche
PAROLE = {'aristo_parle_neutre': ((24, 196), (198, 239)), 'aristo_parle_enthousiaste_16x9': ((27, 212), (214, 239)),
          'aristo_parle_explique': (((36, 86), (132, 188)), (200, 239))}   # images 88-130 : une troisième main sur la canne, exclues
CLIPS = {'aristo_entre_gauche': ((1280, 720), 280, 637, 711, 'bord'),
         'aristo_parle_neutre': ((720, 1280), 347, 346, 1117, 'centre'),
         'aristo_parle_enthousiaste_16x9': ((1280, 720), 174, 634, 579, 'centre'),
         'aristo_parle_explique': ((1280, 720), 175, 635, 581, 'centre'),
         'aristo_parle_enthousiaste': ((720, 1280), 440, 343, 1143, 'centre')}

def _key(a):
    a = a.astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = 1-np.clip((ks-30)/60, 0, 1); al = cv2.GaussianBlur(al, (0, 0), .7)
    sp = ks > 0; a[..., 1] = np.where(sp, np.minimum(G, R*.75+B*.25), G); a[..., 2] = np.where(sp, np.minimum(B, R), B)
    dk = (a.sum(2) < 330) & (a[..., 2] > a[..., 0]*.8)          # traits sombres teintés de vert/bleu ramenés au brun
    a[..., 2] = np.where(dk, a[..., 0]*.55, a[..., 2]); a[..., 1] = np.where(dk, np.minimum(a[..., 1], a[..., 0]*.75), a[..., 1])
    return a, al

class VeoCoin:
    def __init__(self, planning, voix=None, x=500, pieds=1725, largeur_piece=220, dossier=V, duree=None):
        """planning : (t0, clip, mode) ; mode 'une' (joué une fois) ou 'voix' (il parle quand la voix parle, se tait dans les silences)"""
        self.plan = sorted(planning); self.x, self.feet, self.cw, self.dir = x, pieds, largeur_piece, dossier
        self.speak = None
        if voix:
            from scipy.io import wavfile
            sr, a = wavfile.read(voix); a = a.astype(np.float32)
            if a.ndim > 1: a = a.mean(1)
            a /= np.abs(a).max()+1e-9; hop = sr//CLIP_FPS; n = len(a)//hop
            db = 20*np.log10(np.sqrt((a[:n*hop].reshape(n, hop)**2).mean(1))+1e-6); sp = db > -38
            i = 0                                                    # trous de moins de 0,35 s comblés (respirations)
            while i < n:
                if not sp[i]:
                    j = i
                    while j < n and not sp[j]: j += 1
                    if j < n and i > 0 and j-i < int(.35*CLIP_FPS): sp[i:j] = True
                    i = j
                else: i += 1
            self.speak = np.pad(sp, (0, int(((duree or 0)+5)*CLIP_FPS)))
        self.seq = {}
    @functools.lru_cache(maxsize=8)
    def _frames(self, name):
        """images du clip déjà mises à l'échelle finale (uint8), en mémoire ; décalage du coin haut-gauche par rapport au point (x, pieds)"""
        (w, h), cw, cx, fy, anc = CLIPS[name]; s = self.cw/cw
        # recadrage autour du personnage (les clips 16:9 ont de grandes marges vertes) : 2,5 fois moins de mémoire
        if anc == 'bord': x0, x1 = 0, w
        else: x0, x1 = max(0, int(cx-cw*1.9)), min(w, int(cx+cw*1.9))
        y0 = max(0, int(fy-cw*3.6)); y1 = min(h, int(fy+cw*.15))
        cw_, ch_ = (x1-x0)//2*2, (y1-y0)//2*2
        ws, hs = int(round(cw_*s/2))*2, int(round(ch_*s/2))*2
        p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{self.dir}/{name}.mp4', '-vf', f'crop={cw_}:{ch_}:{x0}:{y0},scale={ws}:{hs}:flags=lanczos',
                            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
        F = np.frombuffer(p, np.uint8).reshape(-1, hs, ws, 3)
        cx, fy = cx-x0, fy-y0
        return F, (-cx*s, -fy*s), anc
    def _sequence(self, k):
        """mode 'voix' : liste (clip, image, clip en fondu, image en fondu, poids) à 24 i/s, calée sur la voix.
        Plusieurs clips possibles : il change de clip dans les silences (poses neutres, fondu invisible), et chaque reprise de parole
        part des images les moins vues récemment, pour limiter au maximum les répétitions."""
        if k in self.seq: return self.seq[k]
        t0, names, mode = self.plan[k]; t1 = self.plan[k+1][0] if k+1 < len(self.plan) else len(self.speak)/CLIP_FPS
        names = [names] if isinstance(names, str) else list(names)
        info = {}
        for nm in names:
            tp, q = PAROLE[nm]; info[nm] = ([tp] if isinstance(tp[0], int) else list(tp), q, len(self._frames(nm)[0]))
        used = {nm: np.full(info[nm][2], -1e9) for nm in names}       # dernière fois (pas) où chaque image a été montrée
        S0, S1 = int(t0*CLIP_FPS), int(t1*CLIP_FPS)+2
        sp = np.array([bool(self.speak[min(len(self.speak)-1, s)]) for s in range(S0, S1)])
        out = []; cur = names[0]; p = info[cur][1][0]; d = 1; seg = info[cur][1]; fade = None; last_talk = None
        def run_len(i, val):
            j = i
            while j < len(sp) and sp[j] == val: j += 1
            return j-i
        i = 0
        while i < len(sp):
            talk = bool(sp[i]); L = run_len(i, talk)
            old = (cur, p)
            if talk:
                cands = [nm for nm in names if nm != last_talk] or names
                best = None
                for nm in cands:                                       # meilleur départ : images les moins récemment vues
                    for (a, b) in info[nm][0]:
                        span = b-a
                        for st, dd in [(x, 1) for x in range(a, min(b, a+10)+1, 2)]+[(x, -1) for x in range(max(a, b-10), b+1, 2)]:   # départs proches de la pose neutre
                            if True:
                                q = st; ddd = dd; last = []
                                for _ in range(min(L, 48)):
                                    last.append(q); q += ddd
                                    if q >= b: q, ddd = b, -1
                                    if q <= a and ddd < 0: q, ddd = a, 1
                                score = float(np.mean(i+S0-used[nm][last])) + (30 if nm != cur else 0)
                                if best is None or score > best[0]: best = (score, nm, (a, b), st, dd)
                _, nm, seg, p, d = best; last_talk = nm
            else:
                nm = cur
                if L >= 8 and len(names) > 1:                          # silence assez long : on passe au clip le moins vu
                    nm = min(names, key=lambda x: (used[x].max(), x == cur))
                seg = info[nm][1]; p = seg[0]; d = 1
            if (nm, p) != old and i > 0: fade = (old[0], old[1], 6)
            cur = nm
            for _ in range(L):
                a, b = seg
                if p >= b: p, d = b, -1
                if p <= a and d < 0: p, d = a, 1
                if fade and fade[2] > 0:
                    fc, fp, r = fade; n_ = info[fc][2]
                    out.append((cur, p, fc, min(n_-1, max(0, fp)), r/7)); fade = (fc, fp, r-1)
                else: out.append((cur, p, cur, p, 0.))
                used[cur][p] = i+S0; p += d; i += 1
        self.seq[k] = (S0, out); return self.seq[k]
    def _parts(self, k, t):
        t0, name, mode = self.plan[k]
        if mode == 'une':
            F, off, anc = self._frames(name); n = len(F); return [(F, off, anc, F[min(n-1, int((t-t0)*CLIP_FPS))], 1.)]
        s0, seq = self._sequence(k); i = min(len(seq)-1, max(0, int(t*CLIP_FPS)-s0)); nm, p, nc, c, w = seq[i]
        F, off, anc = self._frames(nm); parts = [(F, off, anc, F[p], 1-w)]
        if w > 0: G, offc, ancc = self._frames(nc); parts.append((G, offc, ancc, G[c], w))
        return parts
    def _layer_one(self, k, t, X, Y):
        rgb = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
        for F, (ox, oy), anc, f, wgt in self._parts(k, t):
            ox = int(round(0 if anc == 'bord' else X+ox)); oy = int(round(Y+oy))
            a, m = _key(f); h, w = m.shape
            x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+w), min(H, oy+h)
            if x1 <= x0 or y1 <= y0: continue
            sa = a[y0-oy:y1-oy, x0-ox:x1-ox]; sm = m[y0-oy:y1-oy, x0-ox:x1-ox]*wgt
            rgb[y0:y1, x0:x1] += sa*sm[..., None]; al[y0:y1, x0:x1] += sm
        return rgb, al
    def layer(self, t, X=None, Y=None):
        """(couleur 0-255, alpha 0-1) de Mister Coin ; (X, Y) : position des pieds à l'écran (par défaut x, pieds)"""
        X = self.x if X is None else X; Y = self.feet if Y is None else Y
        cur = None
        for k, (t0, name, mode) in enumerate(self.plan):
            if t >= t0: cur = k
        if cur is None: return np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)
        rgb, al = self._layer_one(cur, t, X, Y)
        t0 = self.plan[cur][0]
        if cur > 0 and t-t0 < FONDU:
            r2, a2 = self._layer_one(cur-1, t, X, Y); a = (t-t0)/FONDU
            rgb, al = rgb*a+r2*(1-a), al*a+a2*(1-a)
        col = rgb/np.maximum(al, 1e-4)[..., None]
        return np.clip(col, 0, 255), np.clip(al, 0, 1)
    def feet_x(self, al, Y=None):
        Y = self.feet if Y is None else int(Y)
        band = al[max(0, Y-60):Y+4]; cols = np.where(band.max(0) > .5)[0]
        return None if len(cols) == 0 else (cols.min()+cols.max())/2
