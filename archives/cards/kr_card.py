"""Couverture Krachs ép. 1 : salle de marché 3D en panique (rendu pit.py), floutée et assombrie, voile rouge."""
import cairo, numpy as np, sys
from PIL import Image, ImageFilter, ImageEnhance
import cards_lib as cards
from cards_lib import W, H, hx
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/krach08/seq_down/f0001.png'
def bg(c):
    im = Image.open(SRC).convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(7))
    im = ImageEnhance.Brightness(im).enhance(.55)
    yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt(((xx-W/2)/(W*.55))**2+((yy-H*.47)/(H*.30))**2)
    a = np.asarray(im).astype(np.float32)*(1-.55*np.clip(1.15-d, 0, 1))[..., None]   # zone de texte plus sombre au centre
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')
    d_ = bytearray(im.tobytes('raw', 'BGRa')); src = cairo.ImageSurface.create_for_data(d_, cairo.FORMAT_ARGB32, W, H, W*4)
    c.set_source_surface(src); c.paint()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hx('3A0507', .35)); g.add_color_stop_rgba(1, *hx('000000', .25)); c.set_source(g); c.paint()
cards.bg = bg
cards.card("KRACH 2008", False, "/home/claude/krach08/krach2008_tu_achetes.png")
cards.card("KRACH 2008", True, "/home/claude/krach08/krach2008_tu_achetes_emplacement_logo.png")
s = Image.new('RGB', (740, 660), 'white')
for i, f in enumerate(("krach2008_tu_achetes", "krach2008_tu_achetes_emplacement_logo")): s.paste(Image.open(f"/home/claude/krach08/{f}.png").convert('RGB').resize((360, 640)), (10+i*370, 10))
s.save('/tmp/k08/cards_sheet.png')
