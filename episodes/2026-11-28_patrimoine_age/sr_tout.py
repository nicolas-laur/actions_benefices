"""Affinage Real-ESRGAN des seules images utilisées par la vidéo (les vidéos Gemini du 27/11 ont des défauts : on ne garde que des plages saines).
- toise_bas : fondu enchaîné parasite vers un plan large à partir de l'image 152 → on n'utilise que 76-102 ;
- toise_milieu : saut de plan à l'image 127 (et un second vers 180) → 0-42 puis 139-154, le saut caché pendant un saut de Mister Coin ;
- toise_haut : accélération brutale images 144-150 → on s'arrête à 112 ;
- couloir, horloge : sains.
Sortie : decors/sr/decor_<nom>.mp4 (24 i/s) avec seulement ces images, et decors/sr/index.json {nom: [indices source]}.
usage : python3 sr_tout.py   (reprend où il s'est arrêté, décor par décor)"""
import os, sys, json, subprocess, cv2
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, f'{D}/../2026-11-26_histoires_incroyables')
import sr_decors as S
PLAGES = {'toise_bas': [(76, 102)], 'toise_milieu': [(0, 42), (139, 154)], 'toise_haut': [(0, 112)], 'couloir': [(0, 82)], 'horloge': [(0, 125)]}
os.makedirs(f'{D}/decors/sr', exist_ok=True)
idx = {n: [i for a, b in p for i in range(a, b+1)] for n, p in PLAGES.items()}
json.dump(idx, open(f'{D}/decors/sr/index.json', 'w'))
for n, keep in idx.items():
    out = f'{D}/decors/sr/decor_{n}.mp4'
    if os.path.exists(out): continue
    cap = cv2.VideoCapture(f'{D}/decors/decor_{n}.mp4'); ks = set(keep)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '24', '-i', '-',
                           '-c:v', 'libx264', '-crf', '8', '-preset', 'medium', '-pix_fmt', 'yuv420p', out+'.part.mp4'], stdin=subprocess.PIPE)
    for i in range(max(keep)+1):
        ok, f = cap.read()
        if not ok: break
        if i in ks: ff.stdin.write(S.sr(f).tobytes())
        if i % 20 == 0: print(n, i, '/', max(keep), flush=True)
    ff.stdin.close(); ff.wait(); os.replace(out+'.part.mp4', out); print('ok', n, len(keep), flush=True)
