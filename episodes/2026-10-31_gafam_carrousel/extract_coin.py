"""Détourage des poses de Mister Coin classique pour le carrousel (une image choisie dans chaque clip de la banque)."""
import sys, os, cv2, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f'{HERE}/../..'); sys.path.insert(0, f'{ROOT}/mister_coin')
import veo_coin as VC
POSES = dict(joie=('joie', 118), pouce=('pouce', 118), choc=('choc', 84), facepalm=('facepalm', 135), inquiet=('parle_inquiet', 135),
             question=('parle_question', 100), montre=('montre_haut_droite', 104), rire=('rire', 104), triste=('parle_triste', 135))
for k, (clip, i) in POSES.items():
    cap = cv2.VideoCapture(f'{ROOT}/mister_coin/veo/classique_{clip}.mp4'); cap.set(1, i); ok, f = cap.read()
    a, m = VC._key(f[:, :, ::-1]); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((m*255).astype(np.uint8)))
    im = im.crop(im.getbbox()); im.save(f'{HERE}/coin/{k}.png'); print(k, im.size)
