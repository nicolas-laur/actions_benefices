"""Convertit des clips Veo de Mister Coin (fond vert, mister_coin/veo/) en WebP animés transparents + son MP3 pour le site.
Usage : python3 site/outils/clips_coin.py   -> site/assets/anim/<nom>.webp et <nom>.mp3"""
import os, sys, subprocess, tempfile, numpy as np
from PIL import Image
RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(RACINE, 'mister_coin'))
from detoure_poses import detoure  # même détourage que les poses fixes
SRC = os.path.join(RACINE, 'mister_coin', 'veo'); OUT = os.path.join(RACINE, 'site', 'assets', 'anim')
# nom : (clip, début s, fin s)
CLIPS = {'saut': ('classique_saut_place', 0.3, 4.3), 'joie': ('classique_joie', 0.5, 4.5), 'rire': ('classique_rire', 0.5, 4.5),
         'danse': ('classique_danse_joie_silence', 0.5, 4.5), 'pouce': ('classique_pouce', 0.5, 4.0), 'choc': ('classique_choc', 0.3, 3.3)}
FPS, H = 15, 400
def detoure_rgba(png):
    """detoure() recadre ; on veut garder le cadre complet pour que toutes les images restent alignées"""
    import cv2
    bgr = cv2.imread(png); hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s = hsv[..., 0], hsv[..., 1]
    g = np.clip((s - 60) / 60, 0, 1) * np.clip(1 - np.abs(h - 62) / 25, 0, 1); a = 1 - g
    m = (a > .5).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    big = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > .002 * m.size]
    a *= np.isin(lab, big).astype(np.float32); a = cv2.GaussianBlur(a, (3, 3), 0)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32); rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]) + 25)
    return Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
os.makedirs(OUT, exist_ok=True)
for nom, (clip, t0, t1) in CLIPS.items():
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-to', str(t1), '-i', f'{SRC}/{clip}.mp4', '-vf', f'fps={FPS}', f'{d}/%04d.png'], check=True)
        fr = [detoure_rgba(f'{d}/{f}') for f in sorted(os.listdir(d))]
    box = None
    for im in fr:
        b = im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
        if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    # cadre commun, pieds en bas, un peu de marge
    x0, y0, x1, y1 = box; m = 8; box = (max(0, x0 - m), max(0, y0 - m), x1 + m, y1 + 2)
    fr = [im.crop(box) for im in fr]; w = int(fr[0].width * H / fr[0].height)
    fr = [im.resize((w, H), Image.LANCZOS) for im in fr]
    fr[0].save(f'{OUT}/{nom}.webp', save_all=True, append_images=fr[1:], duration=int(1000 / FPS), loop=0, quality=72, method=5, lossless=False)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-to', str(t1), '-i', f'{SRC}/{clip}.mp4', '-vn', '-ac', '1', '-b:a', '64k', f'{OUT}/{nom}.mp3'], check=True)
    print(nom, len(fr), 'images', (w, H), os.path.getsize(f'{OUT}/{nom}.webp') // 1024, 'Ko', os.path.getsize(f'{OUT}/{nom}.mp3') // 1024, 'Ko son')
