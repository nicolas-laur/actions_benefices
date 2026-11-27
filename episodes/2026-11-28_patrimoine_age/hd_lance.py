"""Interpolation 60 i/s par flux optique (interp_flow.py) de chaque passage de décor, dès que son affinage Real-ESRGAN est fini ; reprenable.
Chaque passage suit les nœuds video_col.KN (temps vidéo -> image source), convertis en positions dans decors/sr/decor_<nom>.mp4,
qui ne contient que les plages saines (decors/sr/index.json)."""
import os, sys, json, subprocess
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import video_col as VC
os.makedirs(f'{D}/decors/hd', exist_ok=True)
IDX = json.load(open(f'{D}/decors/sr/index.json'))
for (a, b, d) in VC.BLOCS:
    key = f'{d}_{a:.2f}'
    if os.path.exists(f'{D}/decors/hd/{key}.mp4'): continue
    if not os.path.exists(f'{D}/decors/sr/decor_{d}.mp4'): print('attente', d, flush=True); continue
    idx = IDX[d]
    def pos(s):                                                       # image source (peut être fractionnaire) -> position dans le fichier affiné
        i = int(s); u = s-i; p = idx.index(i); return p+u if u > 1e-6 else float(p)
    kn = ','.join(f'{t-a:.4f}:{pos(s):.4f}' for (t, s) in VC.KN[(d, a)])
    subprocess.run([sys.executable, f'{D}/interp_flow.py', d, key, f'{b-a:.3f}', '1', '0', kn], check=True)
