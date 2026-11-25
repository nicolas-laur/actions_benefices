"""Interpolation 60 i/s par flux optique (OpenCV DIS) pour les décors à grand mouvement de caméra (la rue : panoramique vertical rapide),
là où minterpolate de ffmpeg saccade et fige par moments. Source : decors/sr/decor_<nom>.mp4 (24 i/s, 1080×1920).
Chaque image de sortie est calculée entre les deux images sources voisines : les deux sont déformées le long du flux puis fondues.
usage : python3 interp_flow.py <nom> <clé hd> <durée s> <vitesse> <image source de départ> [u:s,u:s… : temps de scène -> image source]   ->  decors/hd/<clé>.mp4"""
import os, sys, subprocess, cv2, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def flow(a, b, s=.5):
    ga = cv2.cvtColor(cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    f = DIS.calc(ga, gb, None)
    return cv2.resize(f, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR)/s
def run(name, key, dur, sp, start, knots=None):
    cap = cv2.VideoCapture(f'{D}/decors/sr/decor_{name}.mp4'); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    h, w = fr[0].shape[:2]; gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    out = f'{D}/decors/hd/{key}.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', '60', '-i', '-',
                           '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', '-pix_fmt', 'yuv420p', out+'.tmp.mp4'], stdin=subprocess.PIPE)
    cache = {}
    for k in range(int((dur+.7)*60)):
        s = start+k/60*24*sp if not knots else float(np.interp(k/60, [u for u, _ in knots], [v for _, v in knots])); i = min(int(s), len(fr)-2); a = min(1.0, s-i)
        if a < 1e-3: ff.stdin.write(fr[i].tobytes()); continue
        if i not in cache: cache.clear(); cache[i] = (flow(fr[i], fr[i+1]), flow(fr[i+1], fr[i]))
        f01, f10 = cache[i]
        w0 = cv2.remap(fr[i], gx-a*f01[..., 0], gy-a*f01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(fr[i+1], gx-(1-a)*f10[..., 0], gy-(1-a)*f10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        ff.stdin.write(cv2.addWeighted(w0, 1-a, w1, a, 0).tobytes())
    ff.stdin.close(); ff.wait(); os.replace(out+'.tmp.mp4', out); print('ok', key, flush=True)
if __name__ == '__main__':
    kn = [tuple(map(float, p.split(':'))) for p in sys.argv[6].split(',')] if len(sys.argv) > 6 else None
    run(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), kn)
