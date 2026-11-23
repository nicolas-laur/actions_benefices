"""Interpolation 60 i/s par flux optique (interp_flow.py) de chaque passage de décor, dès que son affinage Real-ESRGAN est fini ; reprenable."""
import os, sys, subprocess, cv2
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import video_col as VC
os.makedirs(f'{D}/decors/hd', exist_ok=True)
for (a, b, d) in VC.BLOCS:
    key = f'{d}_{a:.2f}'
    if os.path.exists(f'{D}/decors/hd/{key}.mp4'): continue
    if not os.path.exists(f'{D}/decors/sr/decor_{d}.mp4'): print('attente', d, flush=True); continue
    c = cv2.VideoCapture(f'{D}/decors/decor_{d}.mp4'); n = min(VC.NMAX.get(d, 9999), int(c.get(cv2.CAP_PROP_FRAME_COUNT))); c.release()
    sp = min(1.0, (n-1)/24/max(.1, b-a))
    subprocess.run([sys.executable, f'{D}/interp_flow.py', d, key, f'{b-a:.3f}', f'{sp:.5f}', '0'], check=True)
