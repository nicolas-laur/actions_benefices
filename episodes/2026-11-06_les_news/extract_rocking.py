"""Détourage du clip Gemini « Mister Coin endormi dans son rocking-chair » (couverture) : images 1,3 s → 10 s, fond vert retiré."""
import sys, os, cv2, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f'{HERE}/../..'); sys.path.insert(0, f'{ROOT}/mister_coin')
import veo_coin as VC
os.makedirs(f'{HERE}/rock', exist_ok=True)
cap = cv2.VideoCapture(f'{ROOT}/mister_coin/veo/classique_rocking_chair.mp4'); i = 0; n = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if i >= 31:
        a, m = VC._key(f[:, :, ::-1]); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((np.clip(m, 0, 1)*255).astype(np.uint8)))
        im.save(f'{HERE}/rock/r_{n:03d}.png'); n += 1
    i += 1
print(n, 'images')
