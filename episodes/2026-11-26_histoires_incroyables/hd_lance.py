"""Interpolation 60 i/s par flux optique (interp_flow.py) de chaque passage de décor, dès que son affinage Real-ESRGAN est fini ; reprenable.
Chaque passage montre les images source SRC[(nom, début)] = (i0, i1) étirées sur sa durée (video_col.SRC)."""
import os, sys, subprocess
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import video_col as VC
os.makedirs(f'{D}/decors/hd', exist_ok=True)
for (a, b, d) in VC.BLOCS:
    key = f'{d}_{a:.2f}'
    if os.path.exists(f'{D}/decors/hd/{key}.mp4'): continue
    if not os.path.exists(f'{D}/decors/sr/decor_{d}.mp4'): print('attente', d, flush=True); continue
    i0, i1 = VC.SRC[(d, round(a, 2))]; sp = (i1-i0)/24/max(.1, b-a)
    subprocess.run([sys.executable, f'{D}/interp_flow.py', d, key, f'{b-a:.3f}', f'{sp:.5f}', str(i0)], check=True)
