"""Couverture Take-Two / GTA 6 (18/11, demande de Nicolas) : la mosaïque d'écran de chargement de l'ouverture, recadrée case par case
pour que Mister Coin soit entier dans chacune (Venice, cabriolet, pistolet à billets, yacht ; la poursuite est écartée à cause de
l'étoile Mercedes, trop visible en couverture). Titre « GTA 6 · OU L'ACTION ? » en Big Shoulders sur un bandeau violet incliné
comme les séparations, question « Et toi, tu as acheté GTA 6 ? » sur le bandeau du bas. Images affinées (decors/sr)."""
import os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
W, H = 1080, 1920; BORD = (38, 14, 58)
CASES = [((0, 0), (1080, 0), (1080, 610), (0, 690)), ((0, 690), (560, 648), (500, 1333), (0, 1360)),
         ((560, 648), (1080, 610), (1080, 1300), (500, 1333)), ((0, 1360), (1080, 1300), (1080, 1920), (0, 1920))]
# (clip, image, grossissement, centre vertical visé dans l'image d'origine 1080×1920, centre horizontal)
PLANS = [('mc_venice', 40, 1.0, 820, 540), ('mc_cabriolet', 80, 1.05, 760, 470), ('mc_billets', 80, 1.0, 800, 560), ('mc_yacht', 190, 1.0, 760, 520)]
img = np.zeros((H, W, 3), np.float32)+np.array(BORD, np.float32)
for poly, (nom, i, z, cy, cx) in zip(CASES, PLANS):
    f = cv2.cvtColor(cv2.imread(f'{HERE}/decors/sr/{nom}/f{i:04d}.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32)
    pts = np.array(poly, np.int32); x0, y0 = pts.min(0); x1, y1 = pts.max(0); w, h = x1-x0, y1-y0
    s = max(w/W, h/H)*z; g = cv2.resize(f, (int(W*s)+2, int(H*s)+2), interpolation=cv2.INTER_AREA)
    oy = int(np.clip(cy*s-h/2, 0, g.shape[0]-h)); ox = int(np.clip(cx*s-w/2, 0, g.shape[1]-w))
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [pts], 1.0, cv2.LINE_AA)
    t = np.zeros_like(img); t[y0:y1, x0:x1] = g[oy:oy+h, ox:ox+w]; img = img*(1-m[..., None])+t*m[..., None]
for a, b in (((0, 690), (1080, 610)), ((560, 648), (500, 1333)), ((0, 1360), (1080, 1300))):
    cv2.line(img, a, b, BORD, 26, cv2.LINE_AA)
m = np.ones((H, W), np.float32); m[16:H-16, 16:W-16] = 0; img = img*(1-m[..., None])+np.array(BORD, np.float32)*m[..., None]
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')

ANG = np.degrees(np.arctan2(80, 1080))                       # inclinaison des séparations (≈ 4,2°)
def bandeau(cy, haut, contenu):
    """bandeau violet foncé incliné comme les séparations, ombre portée, contenu dessiné à plat puis tourné"""
    L = Image.new('RGBA', (1400, haut), BORD+(245,)); contenu(ImageDraw.Draw(L), L)
    L = L.rotate(ANG, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', L.size, (0, 0, 0, 0)); sh.putalpha(L.getchannel('A').filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v*.6)))
    x, y = (W-L.width)//2, int(cy-L.height/2); im.alpha_composite(sh, (x, y+12)); im.alpha_composite(L, (x, y))
FB = f'{ROOT}/fonts/BigShouldersDisplay-Black.ttf'; FP = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
def titre(d, L):
    f1 = ImageFont.truetype(FB, 210); f2 = ImageFont.truetype(FB, 104)
    w1 = d.textlength('GTA 6', font=f1); w2 = d.textlength("OU L'ACTION ?", font=f2); x = (L.width-(w1+40+w2))/2
    d.text((x, L.height/2), 'GTA 6', font=f1, fill=(255, 238, 200), anchor='lm')
    d.text((x+w1+40, L.height/2+6), "OU L'ACTION ?", font=f2, fill=(255, 205, 90), anchor='lm')
def question(d, L):
    f = ImageFont.truetype(FP, 54); d.text((L.width/2, L.height/2+2), 'Et toi, tu as acheté GTA 6 ?', font=f, fill=(255, 255, 255), anchor='mm')
bandeau(650, 250, titre)
bandeau(1330, 118, question)
im.convert('RGB').save(f'{HERE}/couverture.png'); print('ok')
