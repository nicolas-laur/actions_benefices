"""Interpolation 60 i/s d'un décor en travelling latéral, sans flux optique : le flux se trompe sur les textures répétitives
(pavés, vitrines) et fait scintiller l'image. Ici, chaque image intermédiaire mélange les deux images voisines recalées
sur le décalage mesuré entre elles (corrélation de phase) : mouvement continu, sans déchirure.
python3 interp_pan.py <nom> <clé hd> <durée> <vitesse> <départ>   (décor decors/sr/decor_<nom>.mp4 -> decors/hd/<clé>.mp4)"""
import os, sys, subprocess, cv2, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
def run(name, key, dur, sp, start):
    cap = cv2.VideoCapture(f'{D}/decors/sr/decor_{name}.mp4'); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
    win = cv2.createHanningWindow(g[0].shape[::-1], cv2.CV_32F)
    sh = [cv2.phaseCorrelate(g[i], g[i+1], win)[0] for i in range(len(g)-1)]
    sx = np.array([s[0] for s in sh]); sy = np.array([s[1] for s in sh])
    k = np.ones(5)/5; sx = np.convolve(np.pad(sx, 2, 'edge'), k, 'valid'); sy = np.convolve(np.pad(sy, 2, 'edge'), k, 'valid')   # décalage lissé
    h, w = fr[0].shape[:2]; out = f'{D}/decors/hd/{key}.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', '60', '-i', '-',
                           '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', '-pix_fmt', 'yuv420p', out+'.tmp.mp4'], stdin=subprocess.PIPE)
    def shift(img, dx, dy): return cv2.warpAffine(img, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    for n in range(int((dur+.7)*60)):
        s = start*24+n/60*24*sp; i = min(int(s), len(fr)-2); u = min(1.0, s-i)
        a = shift(fr[i], sx[i]*u, sy[i]*u).astype(np.float32); b = shift(fr[i+1], -sx[i]*(1-u), -sy[i]*(1-u)).astype(np.float32)
        ff.stdin.write(np.clip(a*(1-u)+b*u, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); os.replace(out+'.tmp.mp4', out); print('ok', key)
if __name__ == '__main__': run(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
