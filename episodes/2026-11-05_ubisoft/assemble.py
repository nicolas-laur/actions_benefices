"""Assemblage provisoire Ubisoft, sans voix : obscurité et lueur → clocher (marche, saut, spirale qui se dessine) → fondu au noir
(on descend de la tour) → souterrain : la brèche, puis le premier panneau de verre. Les minutages se recaleront sur la voix.
usage : python3 assemble.py png t1 t2 … | render"""
import os, sys, math, subprocess
os.environ.setdefault('TXT', '0'); os.environ.setdefault('AMB', '0')
import numpy as np, cv2
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import proto_intro as I, proto_breche as B
W, H, FPS = I.W, I.H, 60
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def inout(x): x = clamp(x); return x*x*(3-2*x)
DARK = 1.4                                  # obscurité et lueur avant que la scène s'ouvre
S_END = I.T_JUMP+.05+I.LOGO_DRAW+.7         # fin de la scène du clocher : spirale tracée et allumée
FADE = .7                                   # fondu au noir : on descend
B_SKIP = 1.0                                # on entre dans la brèche un peu après son début
T_B = DARK+S_END+FADE+.25                   # début de la brèche sur la timeline
DUR = T_B+(B.DUR-B_SKIP)
def iris(img, t):
    """l'obscurité s'ouvre depuis une lueur au centre de l'horizon"""
    a = np.asarray(img).astype(np.float32); u = inout(t/(DARK+.9))
    yy, xx = np.mgrid[0:H, 0:W]; d = np.hypot((xx-540)/1.0, (yy-760)/1.15)
    r = 60+1500*u**1.6; m = np.clip(1-(d-r*.55)/(r*.45+1), 0, 1)**1.5
    glow = np.exp(-(d/150)**2)*.22*(1-u)**2                                                  # lueur chaude au cœur
    a[..., :3] = a[..., :3]*m[..., None]+np.array([255, 196, 120])*glow[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), a.shape[2] == 4 and 'RGBA' or 'RGB')
def frame(t):
    if t < T_B:
        s = max(0.0, t-DARK)                                                              # la scène reste figée dans le noir, puis démarre
        im = I.frame(min(s, S_END)).convert('RGB')
        if t < DARK+.9: im = iris(im, t)
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
