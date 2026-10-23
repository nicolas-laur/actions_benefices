"""Texture procédurale haute définition d'une carte électronique (générique, aucune marque) :
vernis épargne sombre, pistes cuivre, vias, pastilles étamées, sérigraphie blanche (repères génériques).
Sorties : pcb_col.png (couleur), pcb_h.png (relief), pcb_m.png (métal : pistes + pastilles), pcb_lab.png (sérigraphie)."""
import random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
N = 4096; rnd = random.Random(11)
col = Image.new('RGB', (N, N), (14, 18, 24)); h = Image.new('L', (N, N), 40); m = Image.new('L', (N, N), 0)
dc, dh, dm = ImageDraw.Draw(col), ImageDraw.Draw(h), ImageDraw.Draw(m)
# grain du vernis
noise = Image.effect_noise((N, N), 18).filter(ImageFilter.GaussianBlur(1.2))
col = Image.blend(col, Image.merge('RGB', (noise.point(lambda v: v//9), noise.point(lambda v: v//8), noise.point(lambda v: v//6))), .35)
dc = ImageDraw.Draw(col)
CU = (30, 38, 48); CUH = 95
def track(pts, w):
    dc.line(pts, fill=CU, width=w, joint='curve'); dh.line(pts, fill=CUH, width=w, joint='curve'); dm.line(pts, fill=150, width=w, joint='curve')
def via(x, y, r):
    dc.ellipse([x-r, y-r, x+r, y+r], fill=(170, 172, 168)); dc.ellipse([x-r*.45, y-r*.45, x+r*.45, y+r*.45], fill=(8, 8, 10))
    dh.ellipse([x-r, y-r, x+r, y+r], fill=150); dm.ellipse([x-r, y-r, x+r, y+r], fill=255)
# faisceaux de pistes : bus parallèles avec coudes à 45°
for b in range(70):
    n = rnd.randint(4, 16); w = rnd.choice((5, 6, 8, 10)); gap = w*rnd.uniform(2.2, 3.2)
    x0, y0 = rnd.uniform(0, N), rnd.uniform(0, N); horiz = rnd.random() < .5
    L1, L2, L3 = rnd.uniform(150, 900), rnd.uniform(60, 300), rnd.uniform(150, 900); d = rnd.choice((-1, 1))
    for i in range(n):
        o = i*gap
        if horiz:
            p = [(x0, y0+o), (x0+L1+o*d*0, y0+o), (x0+L1+L2, y0+o+d*L2), (x0+L1+L2+L3, y0+o+d*L2)]
        else:
            p = [(x0+o, y0), (x0+o, y0+L1), (x0+o+d*L2, y0+L1+L2), (x0+o+d*L2, y0+L1+L2+L3)]
        track(p, w)
        if rnd.random() < .5: via(*p[-1], w*1.6)
# vias dispersés et zones de masse hachurées
for k in range(700): via(rnd.uniform(0, N), rnd.uniform(0, N), rnd.choice((6, 7, 9)))
for k in range(0):
    x, y, w_, h_ = rnd.uniform(0, N), rnd.uniform(0, N), rnd.uniform(120, 420), rnd.uniform(120, 420)
    for j in range(0, int(w_+h_), 14): dc.line([(x+j, y), (x+j-h_, y+h_)], fill=(30, 36, 44), width=4)
# empreintes de composants : pastilles étamées + sérigraphie
lab = Image.new('L', (N, N), 0); dl = ImageDraw.Draw(lab)
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 22)
except Exception: F = ImageFont.load_default()
for k in range(420):
    x, y = rnd.uniform(0, N), rnd.uniform(0, N); kind = rnd.random()
    if kind < .75:   # passif 0603
        a = rnd.random() < .5; pw, ph, sp = (14, 18, 22) if a else (18, 14, 22)
        for s in (-1, 1):
            cx, cy = (x+s*sp, y) if a else (x, y+s*sp)
            dc.rectangle([cx-pw/2, cy-ph/2, cx+pw/2, cy+ph/2], fill=(190, 192, 186)); dm.rectangle([cx-pw/2, cy-ph/2, cx+pw/2, cy+ph/2], fill=255)
        dl.rectangle([x-40, y-30, x+40, y+30] if a else [x-30, y-40, x+30, y+40], outline=255, width=2)
        if rnd.random() < .3: dl.text((x+44, y-12), rnd.choice('RCLQ')+str(rnd.randint(1, 499)), font=F, fill=255)
    else:           # circuit intégré : rangées de pastilles
        n = rnd.randint(6, 14); pitch = 16
        for s in (-1, 1):
            for i in range(n):
                cx = x-n*pitch/2+i*pitch; cy = y+s*n*pitch*.35
                dc.rectangle([cx-4, cy-12, cx+4, cy+12], fill=(186, 188, 182)); dm.rectangle([cx-4, cy-12, cx+4, cy+12], fill=255)
        dl.rectangle([x-n*pitch/2-14, y-n*pitch*.35+18, x+n*pitch/2+14, y+n*pitch*.35-18], outline=255, width=2)
        dl.ellipse([x-n*pitch/2-4, y-n*pitch*.35+24, x-n*pitch/2+6, y-n*pitch*.35+34], fill=255)
        dl.text((x-n*pitch/2, y-n*pitch*.35-30), 'U'+str(rnd.randint(1, 99)), font=F, fill=255)
lab = lab.filter(ImageFilter.GaussianBlur(.6))
col = Image.composite(Image.new('RGB', (N, N), (205, 208, 212)), col, lab.point(lambda v: int(v*.85)))
h = h.filter(ImageFilter.GaussianBlur(1.5))
col.save('/home/claude/intc/pcb_col.png'); h.save('/home/claude/intc/pcb_h.png'); m.save('/home/claude/intc/pcb_m.png')
print('ok')
