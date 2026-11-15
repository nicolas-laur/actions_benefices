"""Netteté des décors : chaque image des décors Gemini (720×1280) est agrandie ×4 par Real-ESRGAN (modèle animevideov3, dessin animé,
converti en ONNX dans lib/sr/), puis ramenée en 1080×1920. Seules les images réellement utilisées par la vidéo sont traitées.
Sortie : decors/sr/decor_<nom>.mp4 (24 i/s, quasi sans perte), lue ensuite par decors_hd.py pour l'interpolation en 60 i/s."""
import os, sys, subprocess, cv2, numpy as np, onnxruntime as ort
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
os.makedirs(f'{D}/decors/sr', exist_ok=True)
so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
SESS = ort.InferenceSession(f'{D}/../../lib/sr/realesr_animevideov3.onnx', so, providers=['CPUExecutionProvider'])
def sr(bgr):
    x = (bgr[..., ::-1].astype(np.float32)/255).transpose(2, 0, 1)[None].copy()
    y = SESS.run(None, {'input': x})[0][0].transpose(1, 2, 0)
    return (np.clip(cv2.resize(y, (1080, 1920), interpolation=cv2.INTER_AREA), 0, 1)*255+.5).astype(np.uint8)[..., ::-1]
def job(name, nmax):
    src = f'{D}/decors/decor_{name}.mp4'; out = f'{D}/decors/sr/decor_{name}.mp4'
    if os.path.exists(out): return
    cap = cv2.VideoCapture(src); n = min(nmax, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '24', '-i', '-',
                           '-c:v', 'libx264', '-crf', '8', '-preset', 'medium', '-pix_fmt', 'yuv420p', out+'.part.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        ok, f = cap.read()
        if not ok: break
        ff.stdin.write(sr(f).tobytes())
        if i % 40 == 0: print(name, i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); os.replace(out+'.part.mp4', out); print('ok', name, n, flush=True)
if __name__ == '__main__':
    import video_col as VC_
    for (a, b, d) in VC_.BLOCS:
        c = cv2.VideoCapture(f'{D}/decors/decor_{d}.mp4'); n = int(c.get(cv2.CAP_PROP_FRAME_COUNT)); c.release()
        sp = min(1.0, (n-1)/24/max(.1, b-a)); job(d, min(n, int((b-a+.8)*sp*24)+3))
