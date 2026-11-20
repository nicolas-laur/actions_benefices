"""Affinage Real-ESRGAN des décors, reprenable : les images sont encodées par tranches de 24 (decors/sr/<nom>_parts/), une tranche finie
n'est jamais refaite, puis assemblées en decors/sr/decor_<nom>.mp4. Notaire à part (nouvelle version 9:16 attendue)."""
import os, sys, subprocess, cv2
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import sr_decors as S
def job(name, nmax, step=24):
    out = f'{D}/decors/sr/decor_{name}.mp4'
    if os.path.exists(out): return
    pd = f'{D}/decors/sr/{name}_parts'; os.makedirs(pd, exist_ok=True)
    cap = cv2.VideoCapture(f'{D}/decors/decor_{name}.mp4'); n = min(nmax, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))); cap.release()
    parts = []
    for a in range(0, n, step):
        p = f'{pd}/p{a:04d}.mp4'; parts.append(p)
        if os.path.exists(p): continue
        cap = cv2.VideoCapture(f'{D}/decors/decor_{name}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, a)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '24', '-i', '-',
                               '-c:v', 'libx264', '-crf', '8', '-preset', 'medium', '-pix_fmt', 'yuv420p', p+'.tmp.mp4'], stdin=subprocess.PIPE)
        for i in range(a, min(n, a+step)):
            ok, f = cap.read()
            if not ok: break
            ff.stdin.write(S.sr(f).tobytes())
        ff.stdin.close(); ff.wait(); cap.release(); os.replace(p+'.tmp.mp4', p); print(name, min(n, a+step), '/', n, flush=True)
    lst = f'{pd}/liste.txt'; open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True); print('ok', name, flush=True)
if __name__ == '__main__':
    todo = sys.argv[1:] or ['coffres', 'manoir', 'guichet', 'krach', 'hemicycle', 'salon']
    N = dict(coffres=150)
    for d in todo: job(d, N.get(d, 240))
