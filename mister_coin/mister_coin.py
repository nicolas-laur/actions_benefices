"""Mister Coin, présentateur des vidéos Actions_Bénéfices : calque réutilisable à poser sur n'importe quel montage.

Utilisation type (dans le compositeur d'une vidéo) :
    import sys; sys.path.insert(0, '/chemin/vers/mister_coin')
    from mister_coin import MisterCoin
    mc = MisterCoin('voix.wav',
                    places={'bas': (540, 1655, .40), 'gauche': (305, 1100, .30)},   # (x centre de la pièce, y des pieds, zoom)
                    debut='bas',
                    moments=[(3.5, 'negatif'), (9.9, 'pouce'), (11.7, 'montre'), (36.4, 'positif')],
                    sauts_de_place=[(11.05, 'gauche')],          # grand saut d'une place à l'autre
                    petits_sauts=[9.9, 31.25],                   # sauts de joie sur place
                    coucous=[(.2, 3.3), (40.3, 41.6)],            # salut de la main
                    entree=(0.0, 1.3, 1350))                     # arrive en marchant depuis la droite
    calque = mc.layer(t)        # PIL RGBA 1080×1920 : ombre + personnage, à coller par-dessus le décor et les panneaux

Règles de jeu validées (octobre 2026) :
- pas de gros plan : il garde une taille constante et illustre ce qui est dit ;
- mouvements lents et continus : énergie de la voix lissée ~0,3 s, respiration, balancement, fondus de 0,14 s entre poses ;
- grimace (inquiet) et joie (ravi) UNIQUEMENT dans les silences de la voix ; pendant qu'il parle d'une mauvaise nouvelle,
  sourcils inquiets + bouche qui continue de parler (pose « souci ») ;
- ses deux mains doivent rester dans le cadre (vérifier la place « gauche » avec le bras qui salue)."""
import os, sys, math, functools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import puppet as P, rig

W, H = 1080, 1920
FEET = np.array([1000., 2080.])
def ease(p): p = min(1, max(0, p)); return p*p*(3-2*p)
def fade(t, a, b, r=.25): return ease((t-a)/r)*ease((b-t)/r)

def silences(wav, seuil_db=-38, min_s=.18):
    """liste des silences (début, fin) de la voix, en secondes"""
    from scipy.io import wavfile
    sr, x = wavfile.read(wav); x = x.astype(float)
    if x.ndim > 1: x = x.mean(1)
    x /= abs(x).max()+1e-9; hop = sr//100; n = len(x)//hop
    db = 20*np.log10(np.sqrt((x[:n*hop].reshape(n, hop)**2).mean(1))+1e-6); sil = db < seuil_db
    out, i = [], 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            if j-i >= min_s*100 or j == n: out.append((i/100, j/100 if j < n else j/100+3))   # la fin du fichier compte comme un silence
            i = j
        else: i += 1
    return out

def actions_auto(wav, moments, duree_geste=1.0):
    """transforme des moments (t, type) en poses calées sur la voix.
    negatif : « souci » (sourcils inquiets, il parle) jusqu'au prochain silence, puis grimace « inquiet » dans ce silence
    positif : « ravi » dans le prochain silence ; montre : doigt pointé ; pouce : pouce levé"""
    sil = silences(wav); acts = []
    def next_sil(t):
        for a, b in sil:
            if b-max(a, t) >= .3: return max(a, t), b
        return None
    for t, kind in sorted(moments):
        if kind in ('montre', 'pouce'): acts.append((t, t+duree_geste, 'point' if kind == 'montre' else 'thumb')); continue
        if kind == 'negatif':
            s0 = next((p for p in sil if p[1] > t+.25), None)              # premier silence, même court : fin de la phrase
            if s0 is None: continue
            a, b = max(s0[0], t), s0[1]
            if a-t > .25: acts.append((t, a-.03, 'souci'))
            if b-a >= .3: acts.append((a, min(b, a+.6), 'inquiet'))       # grimace seulement si le silence est assez long
            continue
        s = next_sil(t)
        if s is None or s[0]-t > 2.5: continue
        a, b = s
        if kind == 'positif': acts.append((a, min(b, a+2.0), 'ravi'))
    acts.sort(); clean = []
    for a, b, p in acts:                                  # pas de chevauchement : la pose suivante l'emporte
        if clean and clean[-1][1] > a: clean[-1] = (clean[-1][0], a, clean[-1][2])
        if b > a: clean.append((a, b, p))
    merged = []
    for a, b, p in clean:
        if merged and merged[-1][2] == p and a-merged[-1][1] < .06: merged[-1] = (merged[-1][0], b, p)
        else: merged.append((a, b, p))
    return [c for c in merged if c[1]-c[0] > .12]

BUBBLE_FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
def _place(p):
    """place = (x, y des pieds, zoom[, miroir][, inclinaison en degrés])"""
    p = tuple(p); return (p[0], p[1], p[2], bool(p[3]) if len(p) > 3 else False, p[4] if len(p) > 4 else 0.)

class MisterCoin:
    def __init__(self, wav, places, debut, moments=(), actions=None, sauts_de_place=(), petits_sauts=(), coucous=(), entree=None,
                 duree_saut=.55, marches=(), assis=(), danses=(), bulles=(), hauteur_saut=320, trajet=None):
        """sauts_de_place : (t, place) saut en arc, ou (t, place, 'marche', durée) déplacement en marchant
        marches : (t0, t1) marche sur place ; assis : (t0, t1) assis (jambes tendues devant) ; danses : (t0, t1) petits sauts + balancement
        bulles : (t0, t1, texte) bulle de BD au-dessus de lui ; miroir : il regarde/pointe vers la gauche"""
        self.places = {k: _place(v) for k, v in places.items()}; self.debut = debut
        self.actions = actions if actions is not None else actions_auto(wav, moments)
        self.pup = P.Puppet(wav, self.actions)
        moves, cur = [], debut
        for m in sorted(sauts_de_place, key=lambda m: m[0]):
            if len(m) > 2 and m[2] == 'marche': moves.append((m[0], m[3], cur, m[1], 'marche'))
            else: moves.append((m[0], duree_saut, cur, m[1], 'saut'))
            cur = m[1]
        self.moves = moves; self.hops = list(petits_sauts); self.waves = list(coucous); self.walk = entree
        self.marches = list(marches); self.assis = list(assis); self.danses = list(danses); self.bulles = list(bulles)
        self.hjump = hauteur_saut; self.trajet = trajet   # trajet(t) -> (x, y, zoom, miroir, inclinaison, marche 0..1) ou None
        lv = self.pup.level.astype(float); a = 1-math.exp(-1/(.3*30)); o = lv.copy()
        for k in range(1, len(o)): o[k] = o[k-1]+a*(o[k]-o[k-1])
        for k in range(len(o)-2, -1, -1): o[k] = o[k+1]+a*(o[k]-o[k+1])
        self.lv = o
    # ---------- temps ----------
    def lv_at(self, t): return float(np.interp(t*30, np.arange(len(self.lv)), self.lv))
    def pose_seg(self, t):
        start, prev, pose = 0., 'wave', 'wave'
        for a, b, p in self.actions:
            if t < a: break
            if t < b: return p, (prev if abs(a-start) < .06 else 'wave'), t-a
            prev, pose, start = p, 'wave', b
        return 'wave', prev, t-start
    @staticmethod
    def jumpcurve(d, dur, height):
        if d < -.15 or d >= dur+.3: return 0., 0.
        if d < 0: return 0., -.07*math.sin(math.pi/2*(d+.15)/.15)
        if d < dur:
            p = d/dur; return height*math.sin(math.pi*p), (-.07+.13*ease(p/.25) if p < .25 else .06*(1-ease((p-.25)/.5)))
        u = (d-dur)/.3; return 0., -.07*math.sin(math.pi*u)*(1-u)
    def place_at(self, t):
        """(x, y, zoom, miroir 0..1, inclinaison), hauteur de saut, étirement, marche en cours (0..1)"""
        p = self.places[self.debut]; pos = [p[0], p[1], p[2], float(p[3]), p[4]]; jump = 0.; st = 0.; walking = 0.
        for t0, d, a, b, kind in self.moves:
            B = self.places[b]
            if t >= t0+d: pos = [B[0], B[1], B[2], float(B[3]), B[4]]
            if kind == 'saut' and t0-.15 <= t < t0+d+.3:
                # saut : arc au-dessus du trajet le plus haut ; demi-tour en l'air si le miroir change
                A = self.places[a]; h = self.hjump+max(0, A[1]-B[1])*.35
                jump, st = self.jumpcurve(t-t0, d, h)
                if t0 <= t < t0+d:
                    e = ease((t-t0)/d); pos = [A[i]+(B[i]-A[i])*e for i in range(3)]+[float(A[3])+(float(B[3])-float(A[3]))*e, A[4]+(B[4]-A[4])*e]
            if kind == 'marche' and t0 <= t < t0+d:
                A = self.places[a]; e = (t-t0)/d; e = e*e*(3-2*e)*.25+e*.75
                pos = [A[i]+(B[i]-A[i])*e for i in range(3)]+[float(A[3]), A[4]+(B[4]-A[4])*e]; walking = fade(t, t0, t0+d, .2)
        return pos, jump, st, walking
    def hop_at(self, t):
        for h in self.hops:
            if h-.15 <= t < h+.8: return self.jumpcurve(t-h, .5, 190)
        for a, b in self.danses:                       # danse : petits sauts réguliers
            if a <= t < b:
                d = (t-a) % .62; return self.jumpcurve(d, .42, 95)
        return 0., 0.
    # ---------- image ----------
    def layer(self, t):
        pup = self.pup; i = min(len(pup.mouth)-1, int(t*30)); lv = self.lv_at(t); TAU = 2*math.pi
        pose, prev, since = self.pose_seg(t)
        blink = any(0 <= t-b < .12 for b in pup.blinks) and pose != 'ravi'
        (cx, fy, z, mir, tilt), jump, st1, walking = self.place_at(t); hy, st2 = self.hop_at(t); st = st1+st2
        if self.trajet is not None:                     # position imposée image par image (ex. marcher sur une courbe)
            tr = self.trajet(t)
            if tr is not None:
                cx, fy, z, mir, tilt, walking = tr[0], tr[1], tr[2], float(tr[3]), tr[4], tr[5]
                if len(tr) > 6: jump = tr[6]
        if self.walk:
            w0, w1, wx0 = self.walk; wk = fade(t, w0-1, w1, .3); wx = wx0*(1-ease((t-w0)/(w1-w0))) if t < w1 else 0
        else: wk, wx = 0, 0
        wk = max(wk, walking, max([fade(t, a, b, .2) for a, b in self.marches]+[0]))
        sit = max([fade(t, a, b, .2) for a, b in self.assis]+[0])
        dance = max([fade(t, a, b, .2) for a, b in self.danses]+[0])
        legA = 3*math.sin(TAU*t/3.2); legB = -3*math.sin(TAU*t/3.2+.6)
        bob = 9*lv*(1-math.cos(TAU*t*1.35))/2
        rot = 1.8*math.sin(TAU*t/3.4)+1.6*lv*math.sin(TAU*t/1.5)+tilt*(1-2*(mir > .5))
        ph = TAU*1.8*t
        legA += wk*20*math.sin(ph); legB -= wk*20*math.sin(ph); bob += wk*20*(1-math.cos(2*ph))/2; rot += wk*3*math.sin(ph)
        rot += dance*7*math.sin(TAU*t/.62)
        air = min(1, (hy+jump)/120); legA += (14-legA)*air; legB += (-10-legB)*air
        # assis : jambes tendues vers l'avant, le corps descend de la longueur des jambes
        legA += (78-legA)*sit; legB += (62-legB)*sit
        wv = max([fade(t, a, b) for a, b in self.waves]+[0])
        armA = (1-wv)*(4*math.sin(TAU*t/2.9)+4*lv*math.sin(TAU*t/1.6))+wv*(-4+12*math.sin(TAU*1.7*t))
        armA += dance*14*math.sin(TAU*t/.62)
        if pose == 'thumb': armA = 8*math.exp(-since*5)*math.sin(since*12)
        swell = 1+.03*math.sin(math.pi*min(since, .35)/.35) if pose != 'wave' else 1
        breath = .01*math.sin(TAU*t/2.6)
        flipx = 1-2*mir if 0 < mir < 1 else (-1 if mir >= 1 else 1)        # demi-tour en l'air : écrasement horizontal
        sx = swell*(1-.8*st)*(1-breath)*max(.08, abs(flipx)); sy = swell*(1+st)*(1+breath)
        m = int(pup.mouth[i])
        cv = rig.character(pose, m, blink, legA, legB, armA)
        k = ease(since/.14)
        if k < 1 and prev != pose: cv = Image.blend(rig.character(prev, m, blink, legA, legB, armA), cv, k)
        F = FEET.copy()
        if mir >= .5: cv = cv.transpose(Image.FLIP_LEFT_RIGHT); F[0] = cv.width-1-F[0]
        S = np.array([cx, fy], float); off = np.array([wx, -hy-bob-jump/z+sit*480])
        th = math.radians(rot); c, s_ = math.cos(th), math.sin(th)
        Rinv = np.array([[c, -s_], [s_, c]]); Dinv = np.diag([1/sx, 1/sy]); Mx = Dinv@Rinv/z
        b = F+Dinv@Rinv@(-S/z-off)
        char = cv.transform((W, H), Image.AFFINE, (Mx[0, 0], Mx[0, 1], b[0], Mx[1, 0], Mx[1, 1], b[1]), resample=Image.BICUBIC)
        out = Image.new('RGBA', (W, H), 0)
        if sit < .5:
            kk = 1/(1+(hy*z+jump)/120); fx = cx+z*wx; rw = 300*z*kk
            sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((fx-rw, fy-24*z, fx+rw, fy+18*z), fill=int(160*kk*(1-2*sit)))
            out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
        out.alpha_composite(char)
        for bl in self.bulles:
            a, b2, txt = bl[:3]; side = bl[3] if len(bl) > 3 and isinstance(bl[3], str) else 'haut'
            if a-.05 <= t < b2+.2:
                lift = (hy*z+jump)+bob*z
                hx = cx+z*wx; top = fy-z*(1830-sit*480)-lift                  # haut du chapeau
                mouth = (hx+z*(-20 if mir < .5 else 20), fy-z*(830-sit*480)-lift)   # bouche, au centre bas de la pièce
                self._bubble(out, txt, side, (hx, top), mouth, z*525, t-a, b2-t)
        return out
    @staticmethod
    @functools.lru_cache(maxsize=32)
    def _bubble_img(txt):
        """corps de la bulle (sans la queue) : texte en une ou deux lignes"""
        from PIL import ImageFont
        f = ImageFont.truetype(BUBBLE_FONT, 40); words = txt.split(' '); lines, cur = [], ''
        for w_ in words:
            test = (cur+' '+w_).strip()
            if f.getlength(test) > 420 and cur: lines.append(cur); cur = w_
            else: cur = test
        lines.append(cur)
        tw_ = int(max(f.getlength(l) for l in lines)); th_ = 52*len(lines)
        Wb, Hb = tw_+64, th_+44; im = Image.new('RGBA', (Wb+10, Hb+10), 0); d = ImageDraw.Draw(im)
        d.rounded_rectangle((5, 5, 5+Wb, 5+Hb), 30, fill=(255, 255, 255, 255), outline=(25, 18, 10, 255), width=5)
        for k_, l in enumerate(lines): d.text((5+Wb//2, 5+22+26+52*k_), l, font=f, fill=(25, 18, 10, 255), anchor='mm')
        return im
    def _bubble(self, out, txt, side, head, mouth, R, since, until):
        """bulle toujours accrochée à lui : au-dessus de la tête (queue vers le chapeau) ou sur le côté (queue vers la bouche)"""
        body = self._bubble_img(txt); s = back_(since/.3)*ease(until/.2) if since >= 0 else 0
        if s <= .02: return
        bw, bh = body.size; M = 14
        if side == 'haut':
            bx = min(max(M, head[0]-bw/2), W-M-bw); by = max(M, head[1]-bh-48)
            base = (min(max(bx+40, head[0]), bx+bw-40), by+bh-8); tip = (head[0], head[1]-6); horiz = False
        else:
            left = side == 'gauche'
            ex = mouth[0]-R*.95 if left else mouth[0]+R*.95                # bord de la pièce, à hauteur de bouche
            bx = ex-60-bw if left else ex+60; bx = min(max(M, bx), W-M-bw)
            by = min(max(M, mouth[1]-bh*.85), H-M-bh)
            base = (bx+bw-8 if left else bx+8, min(max(by+30, mouth[1]-10), by+bh-30)); tip = (ex, mouth[1]); horiz = True
        # mise à l'échelle autour du point d'attache de la queue (effet « pop »)
        im = body.resize((max(1, int(bw*s)), max(1, int(bh*s))), Image.BICUBIC)
        ox = base[0]+(bx-base[0])*s; oy = base[1]+(by-base[1])*s
        lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
        tipx = base[0]+(tip[0]-base[0])*s; tipy = base[1]+(tip[1]-base[1])*s
        if horiz: p1, p2 = (base[0], base[1]-22*s), (base[0], base[1]+22*s)
        else: p1, p2 = (base[0]-24*s, base[1]), (base[0]+24*s, base[1])
        d.polygon([p1, (tipx, tipy), p2], fill=(255, 255, 255, 255), outline=(25, 18, 10, 255), width=5)
        lay.alpha_composite(im, (int(ox), int(oy)))
        # recouvre le trait de la queue à l'intérieur de la bulle
        ImageDraw.Draw(lay).polygon([(p1[0]+(3 if horiz and side == 'droite' else (-3 if horiz else 0)), p1[1]+(0 if horiz else -3)),
                                     (p2[0]+(3 if horiz and side == 'droite' else (-3 if horiz else 0)), p2[1]+(0 if horiz else -3)),
                                     ((p1[0]+p2[0])/2+((tipx-base[0])*.12), (p1[1]+p2[1])/2+((tipy-base[1])*.12))], fill=(255, 255, 255, 255))
        out.alpha_composite(lay)

def back_(x, s=1.7):
    x = min(1, max(0, x)); return 1+(s+1)*(x-1)**3+s*(x-1)**2

if __name__ == '__main__':
    # test rapide : python3 mister_coin.py voix.wav  -> apercu_mister_coin.png (4 instants)
    wav = sys.argv[1]
    mc = MisterCoin(wav, {'bas': (540, 1655, .40)}, 'bas', moments=[(1.0, 'negatif'), (4.0, 'pouce')], coucous=[(.2, 1.5)])
    print('poses :', mc.actions)
    c = Image.new('RGB', (4*270, 480), (20, 22, 28))
    for j, t in enumerate((.5, 1.5, 3.0, 4.3)):
        im = Image.new('RGBA', (W, H), (20, 22, 28, 255)); im.alpha_composite(mc.layer(t)); c.paste(im.convert('RGB').resize((270, 480)), (j*270, 0))
    c.save('apercu_mister_coin.png'); print('ok')
