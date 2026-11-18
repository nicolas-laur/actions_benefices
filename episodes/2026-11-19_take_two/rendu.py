"""Rendu final de l'épisode Take-Two / GTA 6 (lancé le 17/11 au soir, à la demande de Nicolas).
Étapes, chacune reprenable :
  python3 rendu.py utilises            → tmp/utilises.json : images de clip réellement montrées (passage à vide, sans dessin)
  python3 rendu.py sr                  → decors/sr/<clip>/fNNNN.jpg : affinage Real-ESRGAN de ces seules images (lib/sr, ×4 puis 1080×1920)
  python3 rendu.py images A B          → tmp/rendu/partNN.mp4 : images de A à B secondes (deux processus en parallèle)
  python3 rendu.py son                 → tmp/rendu/son.wav : voix + ambiance des clips + bruitages des deux transitions
  python3 rendu.py assemble            → 2026-11-19_take_two_sans_musique.mp4 (CRF 15, 16 Mb/s max, 30 i/s, AAC 48 kHz)
30 i/s : les plans Veo et les décors sont en 24 i/s ; l'interpolation en 60 i/s (minterpolate) déforme le dessin cartoon et
coûterait plusieurs heures de plus sur cette machine. On pourra la tenter ensuite sur les plans les plus lents si besoin."""
import os, sys, json, glob, subprocess, time
import numpy as np, cv2
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
FPS = 30; OUT = f'{D}/tmp/rendu'; os.makedirs(OUT, exist_ok=True)

def charger():
    import importlib.util as u
    spec = u.spec_from_file_location('maq', f'{D}/maquettes.py'); m = u.module_from_spec(spec); spec.loader.exec_module(m)
    m.assembler_voix(); return m

def utilises():
    m = charger(); Z = np.zeros((m.H, m.W, 3), np.float32)
    m._image_clip = lambda path, i: Z                                      # aucun décodage
    for nom in ('verre', 'texte', 'pill', 'tuile', 'emoji_', 'tendance', 'fleche', 'plaque', '_rr'):
        setattr(m, nom, lambda img, *a, **k: img)
    m.A = m.I = lambda img, *a, **k: img; m.sous_titre = lambda img, t: img; m.pose = lambda img, *a, **k: img
    m.courbe = lambda img, *a, **k: (img, (0, 0)); m.cadre = lambda img: img
    m.TSAT.finition = lambda im, *a, **k: im; m.TSAT.grade = lambda im, *a, **k: im; m.TSAT.vue = lambda *a, **k: Z
    for k in range(int(m.FIN*FPS)): m.image(k/FPS)
    for k in range(int(m.OUTRO*FPS)+2):
        x = (3.0+k/FPS*.1)*24; m.frame(m.pl('mc_billets'), int(x)/24); m.frame(m.pl('mc_billets'), (int(x)+1)/24)
    res = {os.path.basename(p)[:-4]: sorted(v) for p, v in m.UTILISES.items()}
    json.dump(res, open(f'{D}/tmp/utilises.json', 'w')); print({k: len(v) for k, v in res.items()}, sum(len(v) for v in res.values()))

def sr():
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
    S = ort.InferenceSession(f'{D}/../../lib/sr/realesr_animevideov3.onnx', so, providers=['CPUExecutionProvider'])
    U = json.load(open(f'{D}/tmp/utilises.json')); tot = sum(len(v) for v in U.values()); fait = 0; t0 = time.time()
    for nom, idx in U.items():
        src = f'{D}/plans/{nom}.mp4' if os.path.exists(f'{D}/plans/{nom}.mp4') else f'{D}/decors/{nom}.mp4'
        od = f'{D}/decors/sr/{nom}'; os.makedirs(od, exist_ok=True); cap = cv2.VideoCapture(src); cur = -1; f = None
        for i in idx:
            fait += 1; out = f'{od}/f{i:04d}.jpg'
            if os.path.exists(out): continue
            if not (cur < i <= cur+8): cap.set(cv2.CAP_PROP_POS_FRAMES, i); cur = i-1
            while cur < i: ok, f = cap.read(); cur += 1
            x = (f[..., ::-1].astype(np.float32)/255).transpose(2, 0, 1)[None].copy()
            y = S.run(None, {'input': x})[0][0].transpose(1, 2, 0)
            y = (np.clip(cv2.resize(y, (1080, 1920), interpolation=cv2.INTER_AREA), 0, 1)*255+.5).astype(np.uint8)[..., ::-1]
            cv2.imwrite(out+'.part.jpg', y, [cv2.IMWRITE_JPEG_QUALITY, 96]); os.replace(out+'.part.jpg', out)
            if fait % 20 == 0: print(f'sr {fait}/{tot}  {(time.time()-t0)/60:.0f} min', flush=True)
    print('sr ok', flush=True)

def images(a, b, nom):
    m = charger(); n0, n1 = int(round(a*FPS)), int(round(min(b, m.FIN_VID)*FPS))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '12', '-preset', 'slow', '-pix_fmt', 'yuv420p', f'{OUT}/{nom}.part.mp4'], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(n0, n1):
        ff.stdin.write(np.clip(m.image(k/FPS), 0, 255).astype(np.uint8).tobytes())
        if (k-n0) % 60 == 0: print(f'{nom} {k-n0}/{n1-n0}  {(time.time()-t0)/60:.1f} min', flush=True)
    ff.stdin.close(); ff.wait(); os.replace(f'{OUT}/{nom}.part.mp4', f'{OUT}/{nom}.mp4'); print(nom, 'ok', flush=True)

def son():
    import wave
    m = charger(); sr_ = 48000; L = int(m.FIN_VID*sr_)
    v = np.frombuffer(wave.open(f'{D}/voix/voice_provisoire.wav').readframes(10**9), np.int16).astype(np.float32)/32768
    a = np.zeros((L, 2), np.float32); n = min(L, len(v)); a[:n] = v[:n, None]
    a += m.ambiance(sr_, 0, m.FIN_VID)[:L]
    for fx, t in ((m.TSAT.son(sr_), m.TS), (m.TSAT.mini_son(sr_), m.T_MINI)):
        k = int(t*sr_); n = min(L-k, len(fx)); a[k:k+n] += fx[:n]*.8
    a = a/max(1.0, np.abs(a).max()/10**(-1/20))
    with wave.open(f'{OUT}/son.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr_); w.writeframes((a*32767).astype(np.int16).tobytes())
    print('son ok', round(L/sr_, 2), 's')

def assemble():
    parts = sorted(glob.glob(f'{OUT}/part*.mp4')); parts = [p for p in parts if not p.endswith('.part.mp4')]
    open(f'{OUT}/liste.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
    sortie = f'{D}/2026-11-19_take_two_sans_musique.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/liste.txt', '-i', f'{OUT}/son.wav',
                    '-c:v', 'libx264', '-crf', '15', '-maxrate', '16M', '-bufsize', '32M', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', sortie], check=True)
    print('ok', sortie)

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'utilises': utilises()
    elif c == 'sr': sr()
    elif c == 'images': images(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif c == 'tout':                                        # morceaux de 10 s, un seul processus (mémoire limitée), reprenable
        m = charger(); n = int(np.ceil(m.FIN_VID/10)); del m
        for k in range(n):
            if not os.path.exists(f'{OUT}/part{k:02d}.mp4'): subprocess.run([sys.executable, __file__, 'images', str(k*10), str((k+1)*10), f'part{k:02d}'], check=True)
        print('images ok', flush=True)
    elif c == 'son': son()
    elif c == 'assemble': assemble()
