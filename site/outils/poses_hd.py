"""Poses fixes de Mister Coin en haute définition pour le site : la meilleure source du dépôt (mister_coin/poses ou images
sur fond vert des épisodes), agrandie ×4 par Real-ESRGAN si elle fait moins de 720 px, détourée à haute résolution,
puis enregistrée en WebP de 720 px de haut (2× la taille d'affichage maximale). Sortie : site/assets/img/<nom>.webp"""
import glob, os, sys, numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clips_coin as C            # même modèle Real-ESRGAN et même détourage que les animations
R = C.RACINE; OUT = os.environ.get('POSES_OUT') or os.path.join(R, 'site', 'assets', 'img'); H = int(os.environ.get('POSES_H', 720))   # banque d'expressions : POSES_H=1080 POSES_OUT=site/assets/img/expr
os.makedirs(OUT, exist_ok=True)
NOMS = ['choc', 'court', 'etoiles', 'facepalm', 'haussement', 'inquiet', 'joie', 'journal', 'lit_journal_v2_titre', 'loupe', 'montre',
        'neutre', 'pouce', 'question', 'reflechit', 'rire', 'rocking', 'salut', 'sceptique', 'sueur', 'triste']
ALIAS = {'salut': ['salut_chapeau'], 'rocking': ['rocking_chair'], 'journal': ['lit_journal']}
def source(n):
    c = []
    for a in ALIAS.get(n, [n]):
        c += glob.glob(f'{R}/mister_coin/src_site/{a}.jpg') + glob.glob(f'{R}/mister_coin/poses/{a}.png') + glob.glob(f'{R}/episodes/*/coin/{a}.png') + glob.glob(f'{R}/episodes/*/decors/coin_{a}_couverture.png')
    return max(c, key=lambda p: Image.open(p).size[1])
# poses dont l'accessoire contient du vert ou de petits éléments détachés : déjà détourées finement par mister_coin/detoure_poses.py,
# on les convertit telles quelles (un second détourage effacerait la flèche verte, les gouttes, les pièces qui tombent)
DIRECTES = {'site_graphique', 'site_arrosoir', 'site_parapluie'}
VERT = (26, 240, 20)   # BGR du fond vert Gemini
for n in (sys.argv[1:] or NOMS):
    p = source(n); im = Image.open(p)
    if n in DIRECTES:
        p = f'{R}/mister_coin/poses/{n}.png'; im = Image.open(p)
        im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS); im.save(f'{OUT}/{n}.webp', quality=88, method=6); print(n, 'converti tel quel'); continue
    if im.mode == 'RGBA':     # détourage existant : on le repose sur du vert pour que l'agrandissement traite les bords comme dans les clips
        fond = Image.new('RGBA', im.size, VERT[::-1] + (255,)); fond.alpha_composite(im); bgr = cv2.cvtColor(np.array(fond.convert('RGB')), cv2.COLOR_RGB2BGR)
    else: bgr = cv2.cvtColor(np.array(im.convert('RGB')), cv2.COLOR_RGB2BGR)
    a = C.alpha(bgr); ys, xs = np.where(a > .15); m = 12
    y0, y1, x0, x1 = max(0, ys.min() - m), min(bgr.shape[0], ys.max() + m), max(0, xs.min() - m), min(bgr.shape[1], xs.max() + m)
    crop = np.ascontiguousarray(bgr[y0:y1, x0:x1])
    if crop.shape[0] < H * 1.2: crop = C.sr(crop)                     # trop petite : agrandissement ×4
    out = C.rgba(crop, C.alpha(crop, 5)); out = out.crop(out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    out = out.resize((int(out.width * H / out.height), H), Image.LANCZOS)
    out.save(f'{OUT}/{n}.webp', quality=90, method=6)
    print(n, os.path.relpath(p, R), im.size, '->', out.size, os.path.getsize(f'{OUT}/{n}.webp') // 1024, 'Ko', flush=True)
