"""Affinage Real-ESRGAN des décors et des plans Veo de l'épisode Take-Two (720×1280, 24 i/s, 240 images chacun).
Même méthode que l'épisode millionnaire (modèle lib/sr/realesr_animevideov3.onnx, ×4 puis ramené en 1080×1920), mais reprise
possible image par image : chaque paquet de 24 images est écrit dans decors/sr/<nom>/pNNN.mp4, puis les paquets sont recollés en
decors/sr/<nom>.mp4. Le découpage n'étant pas encore figé, on traite les clips entiers, dans l'ordre de priorité ci-dessous.
usage : python3 sr_decors.py [nom …]      (sans argument : tous, dans l'ordre de ORDRE)"""
import os, sys, glob, subprocess, time, cv2, numpy as np, onnxruntime as ort
D = os.path.dirname(os.path.abspath(__file__))
SRC = {**{os.path.basename(p)[:-4]: p for p in glob.glob(f'{D}/decors/*.mp4')},
       **{os.path.basename(p)[:-4]: p for p in glob.glob(f'{D}/plans/*.mp4')}}
ORDRE = ['mc_venice', 'mc_cabriolet', 'mc_pier', 'mc_billets', 'mc_poursuite', 'decor_2013', 'decor_tour',
         'decor_plage_nuit', 'mc_yacht', 'decor_boulevard']
PAQ = 24
so = ort.SessionOptions(); so.intra_op_num_threads = int(os.environ.get('SR_THREADS', os.cpu_count()))
SESS = ort.InferenceSession(f'{D}/../../lib/sr/realesr_animevideov3.onnx', so, providers=['CPUExecutionProvider'])
def sr(bgr):
    x = (bgr[..., ::-1].astype(np.float32)/255).transpose(2, 0, 1)[None].copy()
    y = SESS.run(None, {'input': x})[0][0].transpose(1, 2, 0)
    return (np.clip(cv2.resize(y, (1080, 1920), interpolation=cv2.INTER_AREA), 0, 1)*255+.5).astype(np.uint8)[..., ::-1]
def enc(path):
    return subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '24',
                             '-i', '-', '-c:v', 'libx264', '-crf', '8', '-preset', 'medium', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def job(name):
    out = f'{D}/decors/sr/{name}.mp4'; pd = f'{D}/decors/sr/{name}'
    if os.path.exists(out): return
    os.makedirs(pd, exist_ok=True)
    cap = cv2.VideoCapture(SRC[name]); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); np_ = (n+PAQ-1)//PAQ
    for k in range(np_):
        p = f'{pd}/p{k:03d}.mp4'
        if os.path.exists(p): continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, k*PAQ); t0 = time.time(); ff = enc(p+'.part.mp4'); m = 0
        for _ in range(min(PAQ, n-k*PAQ)):
            ok, f = cap.read()
            if not ok: break
            ff.stdin.write(sr(f).tobytes()); m += 1
        ff.stdin.close(); ff.wait(); os.replace(p+'.part.mp4', p)
        print(f'{name} paquet {k+1}/{np_} ({m} images, {(time.time()-t0)/max(1, m):.1f} s/image)', flush=True)
    lst = f'{pd}/liste.txt'
    open(lst, 'w').write(''.join(f"file 'p{k:03d}.mp4'\n" for k in range(np_)))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out+'.part.mp4'], check=True)
    os.replace(out+'.part.mp4', out); print('ok', name, n, flush=True)
if __name__ == '__main__':
    for nm in (sys.argv[1:] or ORDRE): job(nm)
