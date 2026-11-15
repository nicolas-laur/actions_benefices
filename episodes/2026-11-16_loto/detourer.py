"""Détoure les accessoires Gemini sur fond vert (accessoires/*.jpg -> props/*.png) : alpha = 1 - clip((g - max(r, b) - 40) / 80),
vert résiduel retiré des bords (despill), recadrage au contenu."""
import glob, os, numpy as np
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{D}/props', exist_ok=True)
for f in glob.glob(f'{D}/accessoires/*.jpg'):
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.float32); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    al = 1-np.clip((g-np.maximum(r, b)-40)/80, 0, 1)
    a[..., 1] = np.minimum(g, np.maximum(r, b)+10)                     # despill
    im = Image.fromarray(np.dstack([a, al*255]).astype(np.uint8), 'RGBA'); im = im.crop(im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    im.save(f'{D}/props/{os.path.basename(f)[:-4]}.png'); print(os.path.basename(f), im.size)
