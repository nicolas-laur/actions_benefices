"""Mister Coin v2 : moteur d'animation fluide (même usage que MisterCoin, calque RGBA 1080×1920 par image).

    from coin2 import Coin2
    mc = Coin2('voix.wav', places={'a': (540, 1655, .28), 'b': (300, 1655, .28, True)}, debut='a',
               actions=[(3.0, 4.2, 'point', (820, 600)), (6.1, 6.6, 'ravi'), (9.0, 12.0, 'souci')],
               sauts_de_place=[(5.0, 'b', 'marche', 1.6)], bulles=[(7.0, 8.5, "Super !", 'droite')],
               gestes_mots=[2.1, 4.8], objets=[(10, 12, image_rgba, 'D', .8)])
    calque = mc.layer(t)

Principes (inspirés de l'animation 2D classique, cf. l'exemple Miss Minutes validé par Nicolas) :
- jamais figé : respiration, balancement, micro-mouvements des mains ;
- tout est amorti : chaque paramètre suit sa cible avec un ressort critique (pas de saut, pas de fondu d'images) ;
- la parole fait vivre le corps : petits rebonds et étirements sur les attaques de syllabes, bouche continue ;
- la marche pose vraiment les pieds (phase calée sur la distance parcourue : aucun glissement) ;
- anticipation et écrasement sur les sauts, gestes automatiques sur les mots clés.

actions : (t0, t1, type[, cible]) avec type parmi
    expressions : 'ravi', 'joie', 'inquiet', 'souci', 'abattu', 'surpris', 'fache', 'neutre'
    gestes      : 'point' (cible écran (x, y) facultative), 'thumb', 'wave', 'haussement', 'tenir', 'mains_hanches', 'reflechit'
"""
import os, sys, math, functools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import rig2
from mister_coin import MisterCoin, _place, silences

W, H = 1080, 1920; FPS = 60
FEET = np.array([1000., rig2.FEET_Y])
def ease(p): p = min(1, max(0, p)); return p*p*(3-2*p)
def clamp(x, a=0., b=1.): return max(a, min(b, x))

EXPR = {'neutre': dict(sourcil=0, froncé=0, sourire=.6, paupiere=0, plisse=0),
        'ravi': dict(sourcil=.45, froncé=0, sourire=1, paupiere=0, plisse=.55),
        'joie': dict(sourcil=.7, froncé=0, sourire=1, paupiere=0, plisse=.45),
        'inquiet': dict(sourcil=.55, froncé=-.85, sourire=-.5, paupiere=.12, plisse=0),
        'souci': dict(sourcil=.4, froncé=-.7, sourire=-.25, paupiere=.08, plisse=0),
        'abattu': dict(sourcil=-.15, froncé=-.6, sourire=-.75, paupiere=.38, plisse=0),
        'surpris': dict(sourcil=1, froncé=0, sourire=.1, paupiere=0, plisse=0),
        'fache': dict(sourcil=-.35, froncé=.85, sourire=-.35, paupiere=.15, plisse=0)}
GESTE_EXPR = {'point': 'neutre', 'thumb': 'ravi', 'wave': 'ravi', 'haussement': 'souci', 'tenir': 'neutre', 'mains_hanches': 'neutre', 'reflechit': 'souci'}
REST_G, REST_D = (430., 2010.), (1520., 1990.)
SH_G, SH_D = None, None

class Coin2:
    def __init__(self, wav, places, debut, actions=(), sauts_de_place=(), petits_sauts=(), coucous=(), bulles=(), trajet=None,
                 gestes_mots=(), objets=(), duree_saut=.55, hauteur_saut=320, duree=None):
        self.places = {k: _place(v) for k, v in places.items()}; self.debut = debut
        self.actions = sorted(actions, key=lambda a: a[0]); self.bulles = list(bulles); self.trajet = trajet
        self.hops = list(petits_sauts); self.waves = list(coucous); self.objets = list(objets); self.hjump = hauteur_saut
        moves, cur = [], debut
        for m in sorted(sauts_de_place, key=lambda m: m[0]):
            if len(m) > 2 and m[2] == 'marche': moves.append((m[0], m[3], cur, m[1], 'marche'))
            else: moves.append((m[0], duree_saut, cur, m[1], 'saut'))
            cur = m[1]
        self.moves = moves
        self._voice(wav, duree)
        self._precompute(gestes_mots)
    # ---------- voix : niveau, attaques, « sifflantes » ----------
    def _voice(self, wav, duree):
        from scipy.io import wavfile
        sr, x = wavfile.read(wav); x = x.astype(np.float32)
        if x.ndim > 1: x = x.mean(1)
        x /= (np.abs(x).max()+1e-9); hop = sr//FPS; n = len(x)//hop
        fr = x[:n*hop].reshape(n, hop)
        db = 20*np.log10(np.sqrt((fr**2).mean(1))+1e-6); lv = np.clip((db+44)/32, 0, 1)
        zcr = (np.abs(np.diff(np.sign(fr), axis=1)) > 0).mean(1); z = np.clip((zcr-.08)/.25, 0, 1)
        self.n = max(n, int(((duree or n/FPS)+3)*FPS)); pad = self.n-n
        self.lv = np.pad(lv, (0, pad)); self.zc = np.pad(z, (0, pad))
        d = np.diff(np.convolve(self.lv, np.ones(3)/3, 'same'), prepend=0)
        self.onset = np.clip(d*6, 0, 1)                              # attaques de syllabes
        rng = np.random.default_rng(7); bl, t = [], 1.3
        while t < self.n/FPS: bl.append(t); t += rng.uniform(2.2, 4.6)
        self.blinks = bl
    # ---------- position (même logique que la v1 : places, sauts en arc, marche) ----------
    @staticmethod
    def jumpcurve(d, dur, height):
        if d < -.18 or d >= dur+.32: return 0., 0.
        if d < 0: return 0., -.10*math.sin(math.pi/2*(d+.18)/.18)          # anticipation : il se tasse
        if d < dur:
            p = d/dur; return height*math.sin(math.pi*p), (-.10+.18*ease(p/.22) if p < .22 else .08*(1-ease((p-.22)/.5)))
        u = (d-dur)/.32; return 0., -.12*math.sin(math.pi*u)*(1-u)          # écrasement à l'atterrissage
    def place_at(self, t):
        p = self.places[self.debut]; pos = [p[0], p[1], p[2], float(p[3]), p[4]]; jump = 0.; st = 0.; walking = 0.
        for t0, d, a, b, kind in self.moves:
            B = self.places[b]
            if t >= t0+d: pos = [B[0], B[1], B[2], float(B[3]), B[4]]
            if kind == 'saut' and t0-.18 <= t < t0+d+.32:
                A = self.places[a]; h = self.hjump+max(0, A[1]-B[1])*.35
                jump, st = self.jumpcurve(t-t0, d, h)
                if t0 <= t < t0+d:
                    e = ease((t-t0)/d); pos = [A[i]+(B[i]-A[i])*e for i in range(3)]+[float(A[3])+(float(B[3])-float(A[3]))*e, A[4]+(B[4]-A[4])*e]
            if kind == 'marche' and t0 <= t < t0+d:
                A = self.places[a]; e = (t-t0)/d; e = e*e*(3-2*e)*.3+e*.7
                pos = [A[i]+(B[i]-A[i])*e for i in range(3)]+[float(A[3]), A[4]+(B[4]-A[4])*e]
                walking = 1.0 if .03 < (t-t0)/d < .97 else .5
        if self.trajet is not None:
            tr = self.trajet(t)
            if tr is not None:
                pos = [tr[0], tr[1], tr[2], float(tr[3]), tr[4]]; walking = tr[5]
                if len(tr) > 6: jump = tr[6]
        for h in self.hops:
            if h-.18 <= t < h+.85:
                hy, s2 = self.jumpcurve(t-h, .5, 190); jump += hy; st += s2
        return pos, jump, st, walking
    # ---------- cibles et ressorts, calculés une fois pour toute la vidéo ----------
    def _action_at(self, t):
        for a in self.actions:
            if a[0] <= t < a[1]: return a
        return None
    def _precompute(self, beats):
        n = self.n; ts = np.arange(n)/FPS
        CH = ['hGx', 'hGy', 'hGa', 'hGb', 'hDx', 'hDy', 'hDa', 'hDb', 'tilt', 'dy', 'sourcil', 'froncé', 'sourire', 'paupiere', 'plisse', 'wk']
        tg = {k: np.zeros(n) for k in CH}; self.glove = [None]*n; self.objet = [None]*n
        beats = sorted(beats); self.mirror = np.zeros(n)
        pos_x = np.zeros(n); pos_z = np.ones(n)
        for i, t in enumerate(ts):
            pos, jump, st, walking = self.place_at(t); pos_x[i] = pos[0]; pos_z[i] = pos[2]; self.mirror[i] = pos[3]
            act = self._action_at(t); kind = act[2] if act else None
            ex = EXPR.get(kind, EXPR[GESTE_EXPR.get(kind, 'neutre')]) if kind else EXPR['neutre']
            for k in ('sourcil', 'froncé', 'sourire', 'paupiere', 'plisse'): tg[k][i] = ex[k]
            # mains au repos, avec une petite dérive qui les garde vivantes
            gx, gy = REST_G[0]+18*math.sin(t*1.3), REST_G[1]+14*math.sin(t*1.7+1)
            dx_, dy_ = REST_D[0]+18*math.sin(t*1.1+2), REST_D[1]+14*math.sin(t*1.5)
            gG = gD = 'ouvert'; aG = aD = None; bG, bD = .45, -.45; tilt = 0.; dy = 0.
            since = t-act[0] if act else 0.
            if kind in ('ravi', 'joie'):
                gx, gy, aG, gD = 300, 1180, -25, 'ouvert'; dx_, dy_, aD = 1660, 1150, 25; bG, bD = -.3, .3; dy = -30 if kind == 'joie' else -12
            elif kind in ('inquiet', 'souci'):
                gx, gy, gG, bG = 760, 2050, 'poing', .25; dx_, dy_, gD, bD = 1200, 2040, 'poing', -.25; tilt = -2
            elif kind == 'abattu':
                gx, gy, bG = 600, 2330, .15; dx_, dy_, bD = 1350, 2330, -.15; dy = 40; tilt = 4
            elif kind == 'surpris':
                gx, gy, aG = 380, 1500, -30; dx_, dy_, aD = 1580, 1480, 30; dy = -20
            elif kind == 'fache':
                gx, gy, gG = 640, 2120, 'poing'; dx_, dy_, gD = 1310, 2110, 'poing'; tilt = 3
            elif kind == 'point':
                tgt = act[3] if len(act) > 3 else None; sh = np.array(rig2.body()[2]['epaule_D'])
                if tgt is not None:                                     # cible écran -> repère kit (sans tenir compte du miroir ici)
                    k_ = np.array([FEET[0]+(tgt[0]-pos[0])/pos[2]*(-1 if pos[3] >= .5 else 1), FEET[1]+(tgt[1]-pos[1])/pos[2]])
                    v = k_-sh; L = np.linalg.norm(v)+1e-6; v = v/L*min(L, 620); dx_, dy_ = sh+v
                else: dx_, dy_ = 1760, 1150
                gD, aD, bD = 'index', None, -.15; tilt = -3
            elif kind == 'thumb':
                dx_, dy_, gD, aD, bD = 1620, 1560, 'pouce', 0, -.55; tilt = -2
            elif kind == 'wave':
                w = math.sin(since*11); dx_, dy_, gD, aD, bD = 1660+40*w, 1180, 'ouvert', 12+16*w, -.3
            elif kind == 'haussement':
                gx, gy, aG = 330, 1720, -75; dx_, dy_, aD = 1610, 1700, 75; dy = -25; bG, bD = .5, -.5
            elif kind == 'mains_hanches':
                gx, gy, gG, aG, bG = 520, 2040, 'poing', 200, -.9; dx_, dy_, gD, aD, bD = 1420, 2030, 'poing', 160, .9
            elif kind == 'reflechit':
                dx_, dy_, gD, aD, bD = 1290, 1860, 'index', -20, .8; tilt = 3
            elif kind == 'tenir':
                dx_, dy_, gD, aD, bD = 1600, 1720, 'tenir', 0, -.5
            for a, b in self.waves:                                       # coucou
                if a <= t < b:
                    w = math.sin((t-a)*11); dx_, dy_, gD, aD, bD = 1660+40*w, 1180, 'ouvert', 12+16*w, -.3
            for ob in self.objets:                                        # objet tenu
                if ob[0] <= t < ob[1]:
                    self.objet[i] = (ob[2], ob[3], ob[4])
                    if ob[3] == 'D' and kind not in ('point',): dx_, dy_, gD, aD, bD = 1600, 1720, 'tenir', 0, -.5
                    if ob[3] == 'G': gx, gy, gG, aG, bG = 360, 1740, 'tenir', 0, .5
            if kind is None:                                             # gestes automatiques sur les mots clés (main ouverte qui accompagne)
                for j, bt in enumerate(beats):
                    if bt-.1 <= t < bt+.65:
                        u = math.sin(math.pi*clamp((t-bt+.1)/.75))
                        if j % 2 == 0: dx_, dy_, aD = dx_+(1610-dx_)*u, dy_+(1640-dy_)*u, 18*u
                        else: gx, gy, aG = gx+(350-gx)*u, gy+(1660-gy)*u, -18*u
            tg['hGx'][i], tg['hGy'][i], tg['hGa'][i], tg['hGb'][i] = gx, gy, (np.nan if aG is None else aG), bG
            tg['hDx'][i], tg['hDy'][i], tg['hDa'][i], tg['hDb'][i] = dx_, dy_, (np.nan if aD is None else aD), bD
            tg['tilt'][i], tg['dy'][i], tg['wk'][i] = tilt, dy, walking
            self.glove[i] = (gG, gD)
        # ressorts critiques (semi-implicite, 60 i/s)
        W_ = dict(hGx=10, hGy=10, hGa=12, hGb=9, hDx=10, hDy=10, hDa=12, hDb=9, tilt=7, dy=8, sourcil=13, froncé=11, sourire=12,
                  paupiere=12, plisse=11, wk=7)
        self.tr = {}
        for k, arr in tg.items():
            w = W_[k]; out = np.zeros(n); nanm = np.isnan(arr)
            if nanm.any():                                               # angle « libre » (None) : suivi de l'avant-bras, marqué à part
                self.free = getattr(self, 'free', {}); self.free[k] = nanm.astype(float)
                fm = self.free[k]; sm = np.zeros(n); vv = 0.
                for i in range(n): vv += (14**2*(fm[i]-sm[i-1 if i else 0])-2*14*vv)/FPS; sm[i] = (sm[i-1] if i else fm[0])+vv/FPS
                self.free[k] = np.clip(sm, 0, 1); arr = np.where(nanm, 0., arr)
            x, v = arr[0], 0.
            for i in range(n):
                v += (w*w*(arr[i]-x)-2*w*v)/FPS; x += v/FPS; out[i] = x
            self.tr[k] = out
        self.free = getattr(self, 'free', {})
        # bouche : attaque rapide, relâche plus lente ; sifflantes = bouche plus fermée et plus large
        mo = np.zeros(n); x = 0.
        for i in range(n):
            want = clamp((self.lv[i]-.12)/.55)*(1-.55*self.zc[i]); k = .55 if want > x else .28; x += (want-x)*k; mo[i] = x
        self.mouth = mo
        sq = np.zeros(n); x = v = 0.
        for i in range(n):                                               # rebond élastique sur les attaques de syllabes
            v += -.10*self.onset[i]*30
            v += (16**2*(0-x)-2*.35*16*v)/FPS; x += v/FPS; sq[i] = x
        self.sq = np.clip(sq, -.06, .06)
        dist = np.cumsum(np.abs(np.diff(pos_x, prepend=pos_x[0]))/np.maximum(pos_z, .05))   # distance parcourue (repère kit)
        self.dist = dist; self.vdir = np.sign(np.convolve(np.diff(pos_x, prepend=pos_x[0]), np.ones(9)/9, 'same'))
    # ---------- image ----------
    def _idx(self, t): return min(self.n-1, max(0, int(round(t*FPS))))
    def pose_at(self, t):
        i = self._idx(t); tr = self.tr; lv = float(np.convolve(self.lv, np.ones(15)/15, 'same')[i]) if False else float(self.lv[i])
        gG, gD = self.glove[i]
        pos, jump, st, walking = self.place_at(t); mir = pos[3] >= .5
        wk = clamp(tr['wk'][i])
        # marche : phase calée sur la distance (pas de glissement), pieds au sol pendant l'appui
        L = 115.; ph = self.dist[i]/(4*L); dirl = self.vdir[i]*(-1 if mir else 1) or 1
        legs = {}
        for side, off, base in (('G', 0., (870., 2560.)), ('D', .5, (1100., 2560.))):
            u = (ph+off) % 1
            if u < .5: fx = L-2*L*(u/.5); lift = 0.; ang = 0.
            else: w = (u-.5)/.5; fx = -L+2*L*ease(w); lift = 80*math.sin(math.pi*w); ang = 18*math.sin(math.pi*w)
            fx *= dirl
            air = clamp(jump/90)
            legs[side] = (base[0]+fx*wk, base[1]-lift*wk-air*70, ang*wk*dirl+air*14)
        bob = -24*abs(math.sin(2*math.pi*ph))*wk
        breath = 7*math.sin(2*math.pi*t/3.3)
        sway = 1.4*math.sin(2*math.pi*t/4.3)+2.2*lv*math.sin(2*math.pi*t/1.6)
        tilt = tr['tilt'][i]+sway+3*math.sin(2*math.pi*ph)*wk
        dy = tr['dy'][i]+breath*.6+bob-10*lv
        def hand(side):
            x, y, a, b = tr['h'+side+'x'][i], tr['h'+side+'y'][i], tr['h'+side+'a'][i], tr['h'+side+'b'][i]
            sw = math.sin(2*math.pi*ph)*wk*(1 if side == 'G' else -1)         # bras qui balancent pendant la marche
            x += 120*sw*dirl; y += -10*abs(sw)
            if jump > 0: y -= min(260, jump*1.2)                                 # bras qui montent en l'air
            fr = self.free.get('h'+side+'a')
            ang = None if (fr is not None and fr[i] > .5) else a
            return (x, y+dy*.6, gG if side == 'G' else gD, ang, b)
        blink = min([abs(t-b_) for b_ in self.blinks]+[1])
        lid = max(tr['paupiere'][i], clamp(1-blink/.07)) if blink < .07 else tr['paupiere'][i]
        mo = float(self.mouth[i])
        face = dict(sourcil=tr['sourcil'][i]+.25*mo, froncé=tr['froncé'][i], sourire=tr['sourire'][i]*(1-.3*mo), paupiere=lid,
                    plisse=tr['plisse'][i], bouche=mo, large=1-.15*mo+.25*self.zc[i])
        return dict(corps=(0, dy, tilt), visage=face, bras={'G': hand('G'), 'D': hand('D')}, jambes=legs, objet=self.objet[i],
                    pointes=(dirl if wk > .4 else 0)), pos, jump, st, wk
    def layer(self, t):
        p, pos, jump, st, wk = self.pose_at(t); i = self._idx(t)
        cv = rig2.draw(p)
        cx, fy, z, mir, ptilt = pos
        flipx = 1-2*mir if 0 < mir < 1 else (-1 if mir >= 1 else 1)
        F = FEET*rig2.RES
        if mir >= .5: cv = cv.transpose(Image.FLIP_LEFT_RIGHT); F = np.array([cv.width-1-F[0], F[1]])
        sq = float(self.sq[i])+st
        sx = (1-.7*sq)*max(.08, abs(flipx)); sy = 1+sq
        zz = z/rig2.RES; th = math.radians(ptilt*(1-2*(mir >= .5)))
        c, s_ = math.cos(th), math.sin(th)
        Rinv = np.array([[c, -s_], [s_, c]]); Dinv = np.diag([1/sx, 1/sy]); Mx = Dinv@Rinv/zz
        S = np.array([cx, fy-jump*z], float); b = F-Mx@S
        import cv2
        A = np.array([[Mx[0, 0], Mx[0, 1], b[0]], [Mx[1, 0], Mx[1, 1], b[1]]])          # écran -> toile : inverse pour OpenCV
        char = Image.fromarray(cv2.warpAffine(np.asarray(cv), A, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                              borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)), 'RGBA')
        out = Image.new('RGBA', (W, H), 0)
        kk = 1/(1+jump*z/120); rw = 300*z*kk
        bx0, by0 = int(cx-rw-40), int(fy-24*z-40); sh = Image.new('L', (int(2*rw+80), int(42*z+80)), 0)
        ImageDraw.Draw(sh).ellipse((40, 40, 40+2*rw, 40+42*z), fill=int(150*kk))
        out.paste((0, 0, 0, 255), (bx0, by0, bx0+sh.width, by0+sh.height), sh.filter(ImageFilter.GaussianBlur(14)))
        out.alpha_composite(char)
        for bl in self.bulles:
            a, b2, txt = bl[:3]; side = bl[3] if len(bl) > 3 and isinstance(bl[3], str) else 'haut'
            if a-.05 <= t < b2+.2:
                top = (cx, fy-z*(rig2.FEET_Y-650)-jump*z); mouth = (cx+z*(30 if mir < .5 else -30), fy-z*(rig2.FEET_Y-1500)-jump*z)
                MisterCoin._bubble(MisterCoin, out, txt, side, top, mouth, z*470, t-a, b2-t)
        return out
