"""Mister Coin en clips Veo (Gemini) : détourage du fond vert, mise à l'échelle commune, enchaînements en fondu, boucles.

    from veo_coin import VeoCoin
    mc = VeoCoin(planning=[(0.0, 'aristo_entre_gauche', 'une'), (10.0, 'aristo_parle_neutre', 'boucle'), …],
                 x=500, pieds=1725, largeur_piece=220)
    rgb, alpha = mc.layer(t)        # tableaux float32 1080×1920 (couleur 0-255, alpha 0-1) à composer sur le décor

Chaque clip est décrit dans CLIPS : (fichier, largeur de la pièce dans le clip, centre x de la pièce, y des pieds).
'une' : le clip est joué une fois puis reste sur sa dernière image ; 'boucle' : il recommence avec un fondu de FONDU secondes.
Pour les entrées, le bord gauche du clip est calé sur le bord de l'écran (ancre 'bord'), pour qu'il entre vraiment par le côté."""
import os, subprocess, functools, math
import numpy as np, cv2
D = os.path.dirname(os.path.abspath(__file__)); V = f'{D}/veo'
W, H = 1080, 1920; FONDU = .4; CLIP_FPS = 24
# zones où il parle (images) et où il se tait, mesurées sur l'ouverture de la bouche
PAROLE = {'aristo_parle_neutre': ((24, 196), (198, 239)), 'aristo_parle_enthousiaste_16x9': ((27, 212), (214, 239)),
          'aristo_parle_explique': (((36, 86), (132, 188)), (200, 239))}   # images 88-130 : une troisième main sur la canne, exclues
# hauteur du personnage (chapeau → pieds, pose neutre) : c'est elle qui sert à la mise à l'échelle, pour qu'il garde la même taille d'un clip à l'autre
HAUTEUR = {'aristo_entre_gauche': 518*280/105*0+0, 'aristo_parle_neutre': 965, 'aristo_parle_enthousiaste_16x9': 417, 'aristo_parle_explique': 419, 'aristo_parle_enthousiaste': 1053}
CLIPS = {'aristo_entre_gauche': ((1280, 720), 280, 637, 711, 'bord'),
         'aristo_parle_neutre': ((720, 1280), 347, 346, 1117, 'centre'),
         'aristo_parle_enthousiaste_16x9': ((1280, 720), 174, 634, 579, 'centre'),
         'aristo_parle_explique': ((1280, 720), 175, 635, 581, 'centre'),
         'aristo_parle_enthousiaste': ((720, 1280), 440, 343, 1143, 'centre')}

REACTIONS = {}
def _from_catalogue():
    """les clips analysés par veo_catalogue.py complètent automatiquement CLIPS, PAROLE et HAUTEUR"""
    import json
    p = f'{V}/catalogue.json'
    if not os.path.exists(p): return
    for nm, c in json.load(open(p)).items():
        if nm in CLIPS: continue
        CLIPS[nm] = (tuple(c['format']), c['piece'], c['cx'], c['pieds'], 'bord' if 'entre' in nm or 'sort' in nm else 'centre')
        if c.get('hauteur'): HAUTEUR[nm] = c['hauteur']
        if c.get('type') == 'reaction': REACTIONS[nm] = tuple(c['action']); continue      # réactions (joie, saut…) : jouées d'un bloc, jamais pour parler
        if c.get('parle') and c.get('silence'):
            pl = [tuple(x) for x in c['parle']]; PAROLE[nm] = ((pl[0] if len(pl) == 1 else tuple(pl)), tuple(c['silence'][-1]))
_from_catalogue()
def _key(a):
    a = a.astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    al = 1-np.clip((ks-30)/60, 0, 1); al = cv2.GaussianBlur(al, (0, 0), .7)
    sp = ks > 0; a[..., 1] = np.where(sp, np.minimum(G, R*.75+B*.25), G); a[..., 2] = np.where(sp, np.minimum(B, R), B)
    dk = (a.sum(2) < 330) & (a[..., 2] > a[..., 0]*.8)          # traits sombres teintés de vert/bleu ramenés au brun
    a[..., 2] = np.where(dk, a[..., 0]*.55, a[..., 2]); a[..., 1] = np.where(dk, np.minimum(a[..., 1], a[..., 0]*.75), a[..., 1])
    return a, al

class VeoCoin:
    def __init__(self, planning, voix=None, x=500, pieds=1725, largeur_piece=220, dossier=V, duree=None, lisse=False):
        """planning : (t0, clip, mode) ; mode 'une' (joué une fois) ou 'voix' (il parle quand la voix parle, se tait dans les silences)"""
        self.lisse = lisse
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
        (w, h), cw, cx, fy, anc = CLIPS[name]; s = self.cw*2.45/HAUTEUR[name] if HAUTEUR.get(name) else self.cw/cw
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
    # ---------- mode « lisse » : enchaînements par correspondance de pose (pas de fondu entre deux poses différentes) ----------
    @functools.lru_cache(maxsize=16)
    def _feat(self, name):
        """silhouette de chaque image du clip, réduite au 1/6 et placée dans un repère commun (pieds au même point) : sert à comparer les poses"""
        F, (ox, oy), anc = self._frames(name); k = 6; CW, CH = 130, 140
        out = np.zeros((len(F), CH, CW), np.float32); c0, r0 = 65, 125
        for i, f in enumerate(F):
            h, w = f.shape[:2]; sm = cv2.resize(f, (w//k, h//k), interpolation=cv2.INTER_AREA); _, m = _key(sm)
            x0, y0 = int(round(c0+ox/k)), int(round(r0+oy/k)); hh, ww = m.shape
            a0, b0 = max(0, x0), max(0, y0); a1, b1 = min(CW, x0+ww), min(CH, y0+hh)
            if a1 > a0 and b1 > b0: out[i, b0:b1, a0:a1] = m[b0-y0:b1-y0, a0-x0:a1-x0]
        return out
    def _global_sequence(self):
        """une seule séquence pour toute la vidéo ; le planning choisit les clips autorisés (l'humeur).
        - il parle (images de parole) quand la voix parle, et revient à sa pose neutre (images de fin) dans les silences,
          en jouant réellement les images qui y mènent (jamais de saut d'image) ;
        - dans un même clip, une reprise de parole peut repartir d'une autre image si la pose est quasi identique (coupe invisible) ;
        - changement de clip (nouvelle humeur, ou variété après 8 s) uniquement pendant un petit saut sur place, au sommet du saut."""
        if 'g' in self.seq: return self.seq['g']
        names = sorted({n for _, nm, _ in self.plan for n in ([nm] if isinstance(nm, str) else nm)})
        info, feat = {}, {}
        for nm in names:
            tp, q = PAROLE[nm]; info[nm] = ([tp] if isinstance(tp[0], int) else list(tp), q, len(self._frames(nm)[0])); feat[nm] = self._feat(nm)
        def D(a, pa, b, pb): return float(np.abs(feat[a][pa]-feat[b][pb]).mean())
        nat = np.median([D(n, i, n, i+1) for n in names for i in range(info[n][2]-1)]); THR = max(.004, 1.3*nat)
        S0 = int(self.plan[0][0]*CLIP_FPS); S1 = int(len(self.speak))
        allowed = []
        for s in range(S0, S1):
            cur = None
            for t0, nm, _ in self.plan:
                if s >= int(t0*CLIP_FPS): cur = nm
            allowed.append([cur] if isinstance(cur, str) else list(cur))
        sp = [bool(self.speak[min(len(self.speak)-1, s)]) for s in range(S0, S1)]
        used = {nm: np.full(info[nm][2], -1e9) for nm in names}; last_clip = {nm: -1e9 for nm in names}
        def target(nm, talk):
            return info[nm][0] if talk else [info[nm][1]]
        cur = allowed[0][0]; p = info[cur][1][0]; d = 1; out = []; hops = []; since = 0; pend = None; hop_cool = 0
        for i in range(S1-S0):
            s = i+S0; talk = sp[i]; al = allowed[i]
            new_run = i == 0 or sp[i-1] != talk
            # 1) changement de clip pendant un saut
            if pend is None and hop_cool <= 0:
                need = cur not in al
                soon = any(al != allowed[j] for j in range(i, min(len(allowed), i+24*4)))
                if not need and not soon and not talk and new_run and since > 24*8 and len(al) > 1:
                    L = 0
                    while i+L < len(sp) and not sp[i+L]: L += 1
                    need = L >= 10
                if need:
                    cands = [n for n in al if n != cur] or al
                    nm = min(cands, key=lambda n: last_clip[n]); pend = (nm, i+4); hops.append(s); hop_cool = 24*3
            if pend and i == pend[1]:
                nm = pend[0]; tg = target(nm, talk); best = None
                for (a, b) in tg:
                    for q in range(a, b+1):
                        sc = D(cur, p, nm, q)+THR*.5*math.exp(-(s-used[nm][q])/240)
                        if best is None or sc < best[0]: best = (sc, q)
                out_fade = (cur, p); cur, p = nm, best[1]; since = 0; pend = None; last_clip[nm] = s
                fade = 4
            else: fade = 0
            hop_cool -= 1
            # 2) reprise de parole : coupe invisible vers une image moins vue, si la pose est quasi identique
            tg = target(cur, talk); inside = [r for r in tg if r[0] <= p <= r[1]]
            if talk and new_run and fade == 0:
                best = None
                for (a, b) in tg:
                    for q in range(a, b+1):
                        dd = D(cur, p, cur, q)
                        if dd <= THR and abs(q-p) > 6:
                            sc = used[cur][q]
                            if best is None or sc < best[0]: best = (sc, q)
                if best is not None and (not inside or used[cur][best[1]] < used[cur][p]-24*4): p = best[1]; inside = [r for r in tg if r[0] <= p <= r[1]]
            # 3) image suivante : aller-retour dans la plage, ou marche réelle vers la plage voulue
            if fade: out.append((cur, p, cur, p, 0.))                     # coupe franche au sommet du saut (pas de double image)
            elif out and out[-1][4] > 0 and len(out) > 1 and out[-1][2] != out[-1][0]:
                fc, fp = out[-1][2], out[-1][3]; w = out[-1][4]-.17
                out.append((cur, p, fc, fp, max(0., w)))
            else: out.append((cur, p, cur, p, 0.))
            used[cur][p] = s; since += 1; n = info[cur][2]
            if inside:
                a, b = inside[0]
                if p+d > b or p+d < a: d = -d
                p = int(min(b, max(a, p+d)))
            else:
                mid = [(abs(p-(a if p < a else b)), (a if p < a else b)) for a, b in tg]; goal = min(mid)[1]
                d = 1 if goal > p else -1; p = int(min(n-1, max(0, p+d)))
        self.seq['g'] = (S0, out); self.hops = [h/CLIP_FPS for h in hops]; return self.seq['g']
    def hop_dy(self, t):
        """décalage vertical du petit saut sur place (négatif = vers le haut) ; à ajouter à la position des pieds"""
        if not getattr(self, 'lisse', False): return 0.0
        self._global_sequence(); y = 0.0
        for h in self.hops:
            u = t-(h-.05)
            if 0 <= u < .1: y += 10*math.sin(math.pi*u/.1)                       # il se tasse
            elif .1 <= u < .38: v = (u-.1)/.28; y -= 70*math.sin(math.pi*v)         # saut (sommet au moment du changement)
            elif .38 <= u < .48: y += 8*math.sin(math.pi*(u-.38)/.1)               # réception
        return y
    def _parts(self, k, t):
        if getattr(self, 'lisse', False):
            s0, seq = self._global_sequence(); i = min(len(seq)-1, max(0, int(t*CLIP_FPS)-s0)); nm, p, nc, c, w = seq[i]
            F, off, anc = self._frames(nm); parts = [(F, off, anc, F[p], 1-w)]
            if w > 0: G, offc, ancc = self._frames(nc); parts.append((G, offc, ancc, G[c], w))
            return parts
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
        if cur > 0 and t-t0 < FONDU and not getattr(self, 'lisse', False):
            r2, a2 = self._layer_one(cur-1, t, X, Y); a = (t-t0)/FONDU
            rgb, al = rgb*a+r2*(1-a), al*a+a2*(1-a)
        col = rgb/np.maximum(al, 1e-4)[..., None]
        return np.clip(col, 0, 255), np.clip(al, 0, 1)
    def feet_x(self, al, Y=None):
        Y = self.feet if Y is None else int(Y)
        band = al[max(0, Y-60):Y+4]; cols = np.where(band.max(0) > .5)[0]
        return None if len(cols) == 0 else (cols.min()+cols.max())/2
