"""Rendu complet, reprenable : tranches de 120 images (tmp/chunks/c%06d.mp4) calculées par 2 processus, une tranche finie n'est jamais refaite ;
puis assemblage, son (mix.wav) et export final CRF 15 plafonné à 16 Mb/s. python3 rendu.py  ->  2026-11-26_histoires_incroyables.mp4"""
import os, sys, subprocess, wave
from concurrent.futures import ThreadPoolExecutor
D = os.path.dirname(os.path.abspath(__file__)); CH = f'{D}/tmp/chunks'; os.makedirs(CH, exist_ok=True)
FPS = 60; STEP = 120
sys.path.insert(0, D); import video as V; DUR = V.DUR
N = int(DUR*FPS)
def chunk(a):
    p = f'{CH}/c{a:06d}.mp4'
    if os.path.exists(p): return
    subprocess.run([sys.executable, f'{D}/video_col.py', 'video', p+'.tmp.mp4', str(a), str(min(N, a+STEP))], check=True, stdout=subprocess.DEVNULL)
    os.replace(p+'.tmp.mp4', p); print('tranche', a, '/', N, flush=True)
if __name__ == '__main__':
    todo = list(range(0, N, STEP))
    with ThreadPoolExecutor(2) as ex: list(ex.map(chunk, todo))
    lst = f'{CH}/liste.txt'; open(lst, 'w').write(''.join(f"file 'c{a:06d}.mp4'\n" for a in todo))
    out = f'{D}/2026-11-26_histoires_incroyables.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', f'{D}/mix.wav',
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-maxrate', '16M', '-bufsize', '32M',
                    '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
    print('ok', out, flush=True)
