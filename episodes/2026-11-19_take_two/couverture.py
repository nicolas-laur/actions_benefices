"""Couverture Take-Two / GTA 6 (18/11, demande de Nicolas) : la mosaïque d'écran de chargement de l'ouverture, recadrée case par case
pour que Mister Coin soit entier dans chacune ; en haut, case agrandie sur le saut de la course-poursuite avec les voitures de police
(choix de Nicolas, 18/11), dessous le cabriolet et le pistolet à billets ; titre et question réunis sur le bandeau. Titre « GTA 6 · OU L'ACTION ? » en Big Shoulders sur un bandeau violet incliné
comme les séparations, question « Et toi, tu as acheté GTA 6 ? » sur le bandeau du bas. Images affinées (decors/sr)."""
import os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
W, H = 1080, 1920; BORD = (38, 14, 58)
CASES = [((0, 0), (1080, 0), (1080, 1160), (0, 1240)), ((0, 1240), (560, 1198), (500, 1920), (0, 1920)),
         ((560, 1198), (1080, 1160), (1080, 1920), (500, 1920))]
LIGNES = (((0, 1240), (1080, 1160)), ((560, 1198), (500, 1920)))
# (clip, image, grossissement, centre vertical visé dans l'image d'origine 1080×1920, centre horizontal)
PLANS = [('mc_poursuite', 174, 1.0, 1180, 560), ('mc_cabriolet', 80, 1.0, 840, 470), ('mc_billets', 80, 1.0, 820, 560)]
img = np.zeros((H, W, 3), np.float32)+np.array(BORD, np.float32)
for poly, (nom, i, z, cy, cx) in zip(CASES, PLANS):
    f = cv2.cvtColor(cv2.imread(f'{HERE}/decors/sr/{nom}/f{i:04d}.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32)
    pts = np.array(poly, np.int32); x0, y0 = pts.min(0); x1, y1 = pts.max(0); w, h = x1-x0, y1-y0
    s = max(w/W, h/H)*z
    if z >= 1:
        g = cv2.resize(f, (int(W*s)+2, int(H*s)+2), interpolation=cv2.INTER_AREA)
        oy = int(np.clip(cy*s-h/2, 0, g.shape[0]-h)); ox = int(np.clip(cx*s-w/2, 0, g.shape[1]-w))
    else:                                   # image moins large que la case : côtés remplis par la même image floutée et assombrie
        s0 = max(w/W, h/H); fond = cv2.resize(f, (int(W*s0)+2, int(H*s0)+2), interpolation=cv2.INTER_AREA)
        o0 = int(np.clip(cy*s0-h/2, 0, fond.shape[0]-h)); fond = cv2.GaussianBlur(fond[o0:o0+h, :w], (0, 0), 28)*.55
        p_ = cv2.resize(f, (int(W*s), int(H*s)), interpolation=cv2.INTER_AREA); oy_ = int(np.clip(cy*s-h/2, 0, p_.shape[0]-h)); p_ = p_[oy_:oy_+h]
        g = fond.copy(); xo = (w-p_.shape[1])//2
        sh = np.zeros((h, w), np.float32); sh[:, max(0, xo-6):xo+p_.shape[1]+6] = 1; sh = cv2.GaussianBlur(sh, (0, 0), 18)*.6
        g = g*(1-sh[..., None]); g[:, xo:xo+p_.shape[1]] = p_; oy, ox = 0, 0
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [pts], 1.0, cv2.LINE_AA)
    t = np.zeros_like(img); t[y0:y1, x0:x1] = g[oy:oy+h, ox:ox+w]; img = img*(1-m[..., None])+t*m[..., None]
for a, b in LIGNES:
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
def titre_question(d, L):
    f1 = ImageFont.truetype(FB, 200); f2 = ImageFont.truetype(FB, 100); f3 = ImageFont.truetype(FP, 52)
    w1 = d.textlength('GTA 6', font=f1); w2 = d.textlength("OU L'ACTION ?", font=f2); x = (L.width-(w1+40+w2))/2
    d.text((x, 118), 'GTA 6', font=f1, fill=(255, 238, 200), anchor='lm'); d.text((x+w1+40, 124), "OU L'ACTION ?", font=f2, fill=(255, 205, 90), anchor='lm')
    d.text((L.width/2, 262), 'Et toi, tu as acheté GTA 6 ?', font=f3, fill=(255, 255, 255), anchor='mm')
def question(d, L):
    f = ImageFont.truetype(FP, 54); d.text((L.width/2, L.height/2+2), 'Et toi, tu as acheté GTA 6 ?', font=f, fill=(255, 255, 255), anchor='mm')
bandeau(1212, 330, titre_question)
im.convert('RGB').save(f'{HERE}/couverture.png'); print('ok')
