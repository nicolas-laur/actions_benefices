"""Convertit les clips Veo de Mister Coin (fond vert, mister_coin/veo/) en animations transparentes nettes pour le site.
Chaque image est recadrée sur le personnage, agrandie ×4 par Real-ESRGAN (lib/sr, même modèle que les décors des vidéos),
détourée à haute résolution puis ramenée à 640 px de haut (2× la taille d'affichage, pour les écrans Retina).
Sorties dans site/assets/anim/ : <nom>.webm (VP9 avec transparence : Chrome, Firefox, Edge, Android),
<nom>.webp (WebP animé, pour Safari et iPhone) et <nom>.mp3 (son du clip).
Usage : python3 site/outils/clips_coin.py [noms…] puis python3 site/outils/sons.py"""
import os, sys, subprocess, tempfile, numpy as np, cv2, onnxruntime as ort
from PIL import Image
RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(RACINE, 'mister_coin', 'veo'); OUT = os.path.join(RACINE, 'site', 'assets', 'anim')
CLIPS = {'saut': ('classique_saut_place', 0.3, 4.3), 'joie': ('classique_joie', 0.5, 4.5), 'rire': ('classique_rire', 0.5, 4.5),
         'danse': ('classique_danse_joie_silence', 0.5, 4.5), 'pouce': ('classique_pouce', 0.5, 4.0), 'choc': ('classique_choc', 0.3, 3.3)}
FPS, H = 18, 640
so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
SESS = ort.InferenceSession(os.path.join(RACINE, 'lib', 'sr', 'realesr_animevideov3.onnx'), so, providers=['CPUExecutionProvider'])
def sr(bgr):
    x = (bgr[..., ::-1].astype(np.float32) / 255).transpose(2, 0, 1)[None].copy()
    return (np.clip(SESS.run(None, {'input': x})[0][0].transpose(1, 2, 0), 0, 1) * 255 + .5).astype(np.uint8)[..., ::-1]
def alpha(bgr, flou=3):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32); h, s = hsv[..., 0], hsv[..., 1]
    a = 1 - np.clip((s - 60) / 60, 0, 1) * np.clip(1 - np.abs(h - 62) / 25, 0, 1)
    m = (a > .5).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    big = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > .002 * m.size]
    a *= np.isin(lab, big).astype(np.float32)
    return cv2.GaussianBlur(a, (flou, flou), 0)
def rgba(bgr, a):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]) + 25)    # anti-débordement du vert
    return Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
def main():
  os.makedirs(OUT, exist_ok=True)
  for nom, (clip, t0, t1) in CLIPS.items():
      if len(sys.argv) > 1 and nom not in sys.argv[1:]: continue
      with tempfile.TemporaryDirectory() as d:
          subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-to', str(t1), '-i', f'{SRC}/{clip}.mp4', '-vf', f'fps={FPS}', f'{d}/%04d.png'], check=True)
          fr = [cv2.imread(f'{d}/{f}') for f in sorted(os.listdir(d)) if f.endswith('.png')]
          box = None                                     # cadre commun à tout le clip (pieds immobiles)
          for f in fr:
              ys, xs = np.where(alpha(f) > .15)
              if len(xs): b = (xs.min(), ys.min(), xs.max(), ys.max()); box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
          hh, ww = fr[0].shape[:2]; m = 10
          x0, y0, x1, y1 = max(0, box[0] - m), max(0, box[1] - m), min(ww, box[2] + m), min(hh, box[3] + 3)
          w = int(round((x1 - x0) * H / (y1 - y0) / 2)) * 2      # largeur paire (VP9)
          os.makedirs(f'{d}/o', exist_ok=True); ims = []
          for k, f in enumerate(fr):
              big = np.ascontiguousarray(f[y0:y1, x0:x1])
              if big.shape[0] < H * 0.95: big = sr(big)          # personnage petit dans le cadre : agrandissement ×4
              im = rgba(big, alpha(big, 5)).resize((w, H), Image.LANCZOS); im.save(f'{d}/o/{k:04d}.png'); ims.append(im)
              if k % 20 == 0: print(nom, k, '/', len(fr), flush=True)
          subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{d}/o/%04d.png', '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p',
                          '-b:v', '0', '-crf', '30', '-row-mt', '1', '-auto-alt-ref', '0', f'{OUT}/{nom}.webm'], check=True)
          ims[0].save(f'{OUT}/{nom}.webp', save_all=True, append_images=ims[1:], duration=int(1000 / FPS), loop=0, quality=82, method=4)
      subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-to', str(t1), '-i', f'{SRC}/{clip}.mp4', '-vn', '-ac', '1', '-b:a', '64k', f'{OUT}/{nom}.mp3'], check=True)
      print('ok', nom, (w, H), 'webm', os.path.getsize(f'{OUT}/{nom}.webm') // 1024, 'Ko · webp', os.path.getsize(f'{OUT}/{nom}.webp') // 1024, 'Ko', flush=True)

if __name__ == '__main__':
    main()
