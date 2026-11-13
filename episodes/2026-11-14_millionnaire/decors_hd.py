"""Décors fluides : chaque décor Gemini (24 i/s) est ralenti à la vitesse de son passage puis interpolé en 60 i/s (images intermédiaires
calculées par compensation de mouvement), pour supprimer les saccades. Source : décors agrandis par Real-ESRGAN (sr_decors.py), sortie en 1080×1920 dans decors/hd/."""
import os, sys, subprocess, cv2
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
os.makedirs(f'{D}/decors/hd', exist_ok=True)
def nfr(p): c = cv2.VideoCapture(p); n = int(c.get(cv2.CAP_PROP_FRAME_COUNT)); c.release(); return n
def job(name, key, a, b, sp):
    src = f'{D}/decors/sr/decor_{name}.mp4'; out = f'{D}/decors/hd/{key}.mp4'               # source : décor agrandi par sr_decors.py (1080×1920)
    if os.path.exists(out): return
    vf = f"setpts=PTS/{sp:.5f},minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', vf, '-t', f'{b-a+.7:.2f}', '-an', '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', out], check=True)
    print('ok', key, round(sp, 3), flush=True)
if __name__ == '__main__':
    import video_col as VC_
    for (a, b, d) in VC_.BLOCS:
        n = nfr(f'{D}/decors/decor_{d}.mp4')
        sp = min(1.0, (n-1)/24/max(.1, b-a))
        job(d, f'{d}_{a:.2f}', a, b, sp)
