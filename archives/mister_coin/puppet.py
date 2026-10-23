"""Mister Coin, marionnette à partir des illustrations générées (fond vert détouré).
- parole : 4 bouches (fermée, mi-ouverte, ouverte, « O ») choisies selon l'énergie de la voix, image par image
- clignement : yeux fermés incrustés quelques centièmes de seconde toutes les 2,5 à 5 s
- poses : salut (base), pouce levé, doigt pointé ; réactions : ravi, inquiet (bouche figée)
- mouvement : rebond en rythme avec la parole, balancement, petit « pop » aux changements de pose
usage dans un montage : P = Puppet(voix.wav, actions) ; img = P.frame(t)  -> PIL RGBA (896×1200)"""
import os, math, functools
import numpy as np
from PIL import Image, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); SRC = f'{D}/src'; S = .5
MOUTH_BOX = (700, 1060, 1180, 1360)       # zone de la bouche (pixels de l'image d'origine 1792×2400)
EYES_BOX = (740, 640, 1240, 1060)
FULL = {'bulle', 'billets', 'chute', 'abattu', 'barbe', 'joie'}   # poses ajoutées le 23 oct. (à placer dans les silences de la voix)        # zone des yeux

@functools.lru_cache(maxsize=None)
def keyed(name):
    """détourage du fond vert : clé sur G - max(R, B), contours adoucis, débordement vert neutralisé"""
    a = np.asarray(Image.open(f'{SRC}/{name}.jpg').convert('RGB'), np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; ks = G-np.maximum(R, B)
    alpha = 1-np.clip((ks-25)/70, 0, 1)
    al = Image.fromarray((alpha*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    spill = ks > 0; a[..., 1] = np.where(spill, np.maximum(R, B)+np.clip(ks, 0, 0)*0, G)     # vert -> neutre sur les bords
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(al)
    return im
def region(base, src, box, feather=18):
    """remplace une zone de base par la même zone de src, avec un fondu doux sur les bords"""
    x0, y0, x1, y1 = box; m = Image.new('L', base.size, 0)
    m.paste(255, (x0+feather, y0+feather, x1-feather, y1-feather)); m = m.filter(ImageFilter.GaussianBlur(feather*.6))
    out = base.copy(); out.paste(src, (0, 0), m) if False else None
    return Image.composite(src, base, m)

@functools.lru_cache(maxsize=64)
def compose(pose, mouth, blink):
    """pose : 'wave' | 'thumb' | 'point' | 'ravi' | 'inquiet' ; mouth : 0..3 ; blink : bool"""
    if pose in FULL:                                          # poses entières (chute, joie, barbe…) : image complète, sans synchro labiale
        im = keyed(pose)
    elif pose in ('ravi', 'inquiet'):
        im = keyed(pose)
        if blink and pose == 'inquiet': pass
    else:
        mouths = ['bouche_fermee', 'bouche_mi', 'bouche_ouverte', 'bouche_o']
        if pose == 'souci':                                   # sourcils inquiets mais la bouche continue de parler
            im = region(keyed(mouths[{0: 0, 1: 1, 2: 1, 3: 3}[mouth]]), keyed('inquiet'), (700, 560, 1300, 1060), 24)
        elif pose == 'wave': im = keyed(mouths[mouth])
        else: im = region(keyed(pose), keyed(mouths[mouth]), MOUTH_BOX)
        if blink: im = region(im, keyed('yeux_fermes'), EYES_BOX, 24)
    w, h = im.size
    return im.resize((int(w*S), int(h*S)), Image.LANCZOS)

class Puppet:
    def __init__(self, wav, actions, fps=30, seed=3):
        """actions : liste (t0, t1, pose) ; en dehors : 'wave'"""
        from scipy.io import wavfile
        sr, x = wavfile.read(wav); x = x.astype(np.float32)
        if x.ndim > 1: x = x.mean(1)
        x /= (np.abs(x).max()+1e-9); hop = sr//fps
        n = len(x)//hop; rms = np.sqrt((x[:n*hop].reshape(n, hop)**2).mean(1))
        db = 20*np.log10(rms+1e-6); lv = np.clip((db+42)/30, 0, 1)        # 0 silence -> 1 voix forte
        # bouche : seuils avec maintien minimal de 2 images (pas de clignotement)
        m = np.zeros(n, int); cur, hold = 0, 0; rng = np.random.default_rng(seed)
        for i in range(n):
            want = 0 if lv[i] < .2 else (1 if lv[i] < .5 else 2)
            if want == 2 and rng.random() < .18: want = 3                   # « O » de temps en temps : bouche plus vivante
            if hold <= 0 and want != cur: cur, hold = want, 2
            hold -= 1; m[i] = cur
        self.mouth, self.level, self.fps = m, np.convolve(lv, np.ones(5)/5, 'same'), fps
        self.actions = actions
        ts, t = [], 1.2
        while t < n/fps+5: ts.append(t); t += rng.uniform(2.4, 4.8)
        self.blinks = ts
    def pose_at(self, t):
        for t0, t1, p in self.actions:
            if t0 <= t < t1: return p, t-t0, t1-t
        return 'wave', 99, 99
    def frame(self, t):
        i = min(len(self.mouth)-1, max(0, int(t*self.fps)))
        pose, since, until = self.pose_at(t)
        blink = any(0 <= t-b < .12 for b in self.blinks) and pose not in ('ravi',)
        im = compose(pose, int(self.mouth[i]), blink)
        # mouvement : rebond quand il parle, léger balancement, « pop » au changement de pose
        lv = float(self.level[i])
        bob = 10*abs(math.sin(t*6.2))*lv+4*math.sin(t*2.1)
        rot = 2.2*math.sin(t*1.3)+1.5*lv*math.sin(t*5.1)
        pop = 1+.06*math.exp(-since*14) if since < .5 else 1
        sx = pop*(1+.012*math.sin(t*2.1)); sy = pop*(1-.012*math.sin(t*2.1))
        w, h = im.size; nw, nh = int(w*sx), int(h*sy)
        im2 = im.resize((nw, nh), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC, expand=False, center=(nw/2, nh*.92))
        return im2, -bob, (nw-w, nh-h)
