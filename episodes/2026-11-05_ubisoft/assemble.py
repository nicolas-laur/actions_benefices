"""Assemblage provisoire Ubisoft, sans voix : obscurité et lueur → clocher (marche, saut, spirale qui se dessine) → fondu au noir
(on descend de la tour) → souterrain : la brèche, puis le premier panneau de verre. Les minutages se recaleront sur la voix.
usage : python3 assemble.py png t1 t2 … | render"""
import os, sys, math, subprocess
os.environ.setdefault('TXT', '0'); os.environ.setdefault('AMB', '0')
import numpy as np, cv2, functools
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import proto_intro as I, proto_breche as B
W, H, FPS = I.W, I.H, 60
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def inout(x): x = clamp(x); return x*x*(3-2*x)
DARK = 3.92                                 # obscurité et lueur : deux mesures de musique avant que la scène s'ouvre
S_END = 13.9                                # fin de la scène du clocher (global 17,8 s) : spirale tracée, « Ubisoft » prononcé
FADE = .7                                   # fondu au noir : on descend
B_SKIP = 1.17                               # l'explosion (3,08 s dans la vidéo Gemini) tombe sur le temps fort de 21,09 s
T_B = 19.18                                 # début de la brèche, sur un premier temps
DUR = T_B+(B.DUR-B_SKIP)
BEAT0, BEAT = .09, .4787                    # grille de la musique de Nicolas
@functools.lru_cache(maxsize=1)
def _grid():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); return xx, yy
_P = np.random.default_rng(9).uniform(0, 1, (90, 4))          # particules en orbite autour de l'orbe
def beat_pulse(t):
    """battement : montée brève puis retombée, plus fort sur le premier temps de chaque mesure"""
    k = (t-BEAT0)/BEAT; n = math.floor(k); d = (k-n)*BEAT
    if n < 0: return 0.0
    amp = 1.0 if n % 4 == 0 else .55
    return amp*math.exp(-d/.16)*min(1, d/.02)
def orb(t, cx=540, cy=820):
    """orbe d'énergie dans le noir : cœur blanc doré, halo cyan, anneaux et particules ; elle pulse sur la musique et grossit avant d'éclater"""
    xx, yy = _grid(); d = np.hypot(xx-cx, yy-cy)
    p = beat_pulse(t); grow = inout((t-(DARK-1.0))/1.0)
    R = 42*(1+.18*p)*(1+1.4*grow)+6*math.sin(t*5)
    core = np.exp(-(d/R)**2)                                                   # cœur
    halo = np.exp(-(d/(R*3.2))**2)*(.55+.45*p)                                 # halo
    far = np.exp(-(d/(R*9))**2)*.18*(1+p)                                      # lueur diffuse
    ring = np.exp(-((d-R*(1.8+1.6*((t*.9) % 1)))/6)**2)*(1-((t*.9) % 1))*.5    # anneau qui s'échappe
    img = np.zeros((H, W, 3), np.float32)
    img += core[..., None]*np.array([255, 246, 225])
    img += halo[..., None]*np.array([120, 200, 255])*.7
    img += far[..., None]*np.array([60, 120, 200])
    img += ring[..., None]*np.array([160, 225, 255])
    for a0, r0, sp, sz in _P:                                                  # particules
        ang = a0*6.283+t*(.6+sp)*(1 if sp > .5 else -1); r = R*(1.6+r0*4.5)*(1+.1*p)
        x, y = cx+r*math.cos(ang), cy+r*math.sin(ang)*.85
        if 0 <= x < W and 0 <= y < H:
            s = 1.5+sz*2.5; x0, y0 = int(x), int(y); r_ = int(s*3)+1
            ys, xs = slice(max(0, y0-r_), min(H, y0+r_)), slice(max(0, x0-r_), min(W, x0+r_))
            dd = np.hypot(xx[ys, xs]-x, yy[ys, xs]-y); img[ys, xs] += (np.exp(-(dd/s)**2)*(.5+.5*p))[..., None]*np.array([200, 235, 255])
    return np.clip(img, 0, 255)
def frame(t):
    if t < T_B:
        s = max(0.0, t-DARK)                                                              # la scène reste figée dans le noir, puis démarre
        im = I.frame(min(s, S_END)).convert('RGB')
        if t < DARK: im = Image.fromarray(orb(t).astype(np.uint8))
        elif t < DARK+.6:                                                            # l'orbe éclate en lumière blanche qui dévoile le clocher
            u = (t-DARK)/.6; a_ = np.asarray(im).astype(np.float32); fl = (1-inout(u))**1.5
            a_ = a_*(1-fl)+np.array([255, 250, 238])*fl; im = Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8))
        kf = t-(DARK+S_END)
        if kf > 0:                                                                        # fondu au noir en glissant vers le bas : on descend
            u = inout(kf/FADE); a = np.asarray(im).astype(np.float32)
            M = np.float32([[1, 0, 0], [0, 1, 140*u]]); a = cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
            a *= (1-u); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return im
    bt = B_SKIP+(t-T_B); im = B.frame(bt).convert('RGB')
    k = t-T_B
    if k < .45: im = Image.fromarray((np.asarray(im).astype(np.float32)*inout(k/.45)).astype(np.uint8))
    return im
def main():
    if sys.argv[1] == 'info': print(round(DUR, 2), round(T_B, 2)); return
    if sys.argv[1] == 'png':
        for ts in sys.argv[2:]: frame(float(ts)).save(f'{D}/prev/a_{ts}.png')
        return
    out = f'{D}/out/apercu_assemblage_ubisoft_muet.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('ok', out)
if __name__ == '__main__': main()
