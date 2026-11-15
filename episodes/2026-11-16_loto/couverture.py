"""Couverture du Loto : la foule de Mister Coin inquiets, TOI qui rit sous le projecteur, « LOTO OU PLACEMENT ? »."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
import zoom_foule as ZF
D = os.path.dirname(os.path.abspath(__file__)); F = f'{D}/../../fonts/AlfaSlabOne-Regular.ttf'
W, H = 1080, 1920
im, (x, y, sz) = ZF.frame(.97, W, H, cy=1020, ta=.35)
img = Image.fromarray(np.clip(im[..., ::-1], 0, 255).astype(np.uint8)).convert('RGBA')
lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
d.rounded_rectangle([60, 230, 1020, 700], 60, fill=(33, 15, 40, 190))
def t(txt, yy, s, col): d.text((W/2, yy), txt, font=ImageFont.truetype(F, s), anchor='mm', fill=col, stroke_width=max(4, s//14), stroke_fill=(40, 20, 50))
t("LE LOTO", 330, 130, (255, 226, 120)); t("OU LE PLACEMENT ?", 470, 84, (255, 245, 225)); t("1 chance sur 19 068 840", 610, 56, (255, 140, 140))
img = Image.alpha_composite(img, lay); img.convert('RGB').save(f'{D}/couverture.png'); print('ok')
