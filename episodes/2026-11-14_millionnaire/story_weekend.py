"""Story « Bon week-end » (13/11/2026) : décor du haricot géant au coucher du soleil (agrandi par Real-ESRGAN), Mister Coin qui saute de joie,
lettres peintes 1930. Sortie : out/story_bon_weekend.png (1080×1920). Zones sûres des stories : rien d'important au-dessus de y = 250 ni sous y = 1580."""
import os, sys, math, cv2, numpy as np, cairo
from PIL import Image, ImageFilter, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
os.environ['APERCU'] = '1'
import video_col as C, veo_coin as VC, scenes as S
W, H = 1080, 1920
cap = cv2.VideoCapture(f'{D}/decors/decor_haricot_geant.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, 200); ok, f = cap.read()
import sr_decors
bg = sr_decors.sr(f)[..., ::-1].astype(np.float32)
y = np.arange(H)[:, None, None]; bg *= 1-np.interp(y, [0, 300, 800, 1300, H], [.35, .15, .05, .0, .25])        # léger voile en haut et en bas
im = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')
# Mister Coin fou de joie (clip classique_joie, en plein saut, bras en l'air)
cj = cv2.VideoCapture(f'{S.ROOT}/mister_coin/veo/classique_joie.mp4'); cj.set(cv2.CAP_PROP_POS_FRAMES, int(sys.argv[1]) if len(sys.argv) > 1 else 118); ok, fr = cj.read()
a, m = VC._key(fr[..., ::-1].copy()); ch = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); ch.putalpha(Image.fromarray((m*255).astype(np.uint8)))
ch = ch.crop(ch.getbbox()); hh = 760; ch = ch.resize((int(ch.width*hh/ch.height), hh), Image.LANCZOS)
cx, top = 540, 760
sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((cx-170, 1560, cx+170, 1600), fill=140)                   # ombre au sol (il est en l'air)
im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
glow = Image.new('RGBA', (W, H), (255, 210, 120, 0)); g = Image.new('L', (W, H), 0); g.paste(ch.getchannel('A'), (cx-ch.width//2, top))
glow.putalpha(g.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v*.55))); im.alpha_composite(glow)
im.alpha_composite(ch, (cx-ch.width//2, top))
# textes peints
s, c = S.surface()
C.paint(c, "BON", 540, 330, 120, C.CREAM, rot=-.04)
C.paint(c, "WEEK-END !", 540, 480, 132, C.YEL, rot=-.04)
C.paint(c, "Demain : millionnaire", 540, 615, 46, C.CREAM)
C.paint(c, f"avec 402{S.NB}€ par mois ?", 540, 680, 46, C.CREAM)
for (x, yy, r) in ((170, 300, 30), (905, 300, 26), (130, 560, 20), (950, 540, 24), (150, 720, 16), (930, 720, 18)): C.star(c, x, yy, r)
im.alpha_composite(C.to_img(s))
S.put_emoji(im, '☀️', 330, 330, 84); S.put_emoji(im, '🎉', 750, 330, 84)
os.makedirs(f'{D}/out', exist_ok=True); im.convert('RGB').save(f'{D}/out/story_bon_weekend.png'); print('ok')
