"""Interpolation 60 i/s des décors déjà affinés (decors_hd.job), dans l'ordre des blocs ; ignore ceux dont l'affinage n'est pas fini."""
import os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import decors_hd as H, video_col as VC_
for (a, b, d) in VC_.BLOCS:
    if not os.path.exists(f'{D}/decors/sr/decor_{d}.mp4'): print('attente', d, flush=True); continue
    n = H.nfr(f'{D}/decors/decor_{d}.mp4'); sp = min(1.0, (n-1)/24/max(.1, b-a)); H.job(d, f'{d}_{a:.2f}', a, b, sp)
