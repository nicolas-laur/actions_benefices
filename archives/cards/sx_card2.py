"""Couverture SpaceX : fond spatial étoilé + Terre vue de l'orbite (rendu 3D procédural earth.py) en bas à droite."""
import cairo, math, random, numpy as np
from PIL import Image, ImageFilter
import cards_lib as cards
from cards_lib import W, H, hx
def bg(c):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('020309')[:3]); g.add_color_stop_rgb(1, *hx('050812')[:3]); c.set_source(g); c.paint()
    rnd = random.Random(11)
    for k in range(420):   # étoiles
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(.5, 1.9); c.set_source_rgba(1, 1, 1, rnd.uniform(.15, .8)); c.arc(x, y, r, 0, 2*math.pi); c.fill()
    e0 = Image.open('/home/claude/spcx/earth_card.png').convert('RGBA'); e = Image.new('RGBA', (W, H), (0, 0, 0, 0)); e.alpha_composite(e0, (60, 400))
    # halo atmosphérique doux autour du limbe (2D)
    a = e.split()[3]; halo = Image.new('RGBA', e.size, (70, 140, 255, 0)); halo.putalpha(a.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v*.55)))
    lay = Image.new('RGBA', e.size, (0, 0, 0, 0)); lay.alpha_composite(halo); lay.alpha_composite(e)
    # le haut de l'image reste propre pour le texte : fondu de la planète vers le haut
    arr = np.asarray(lay).astype(np.float32); yy = np.arange(H)[:, None]; arr[..., 3] *= 1.0
    lay = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    d = bytearray(lay.tobytes('raw', 'BGRa')); src = cairo.ImageSurface.create_for_data(d, cairo.FORMAT_ARGB32, W, H, W*4)
    c.set_source_surface(src); c.paint()
cards.bg = bg
cards.card("SPACEX", False, "/mnt/user-data/outputs/cartes/spacex_tu_achetes.png")
cards.card("SPACEX", True, "/mnt/user-data/outputs/cartes/spacex_tu_achetes_emplacement_logo.png")
s = Image.new('RGB', (740, 660), 'white')
for i, f in enumerate(("spacex_tu_achetes", "spacex_tu_achetes_emplacement_logo")): s.paste(Image.open(f"/mnt/user-data/outputs/cartes/{f}.png").convert('RGB').resize((360, 640)), (10+i*370, 10))
s.save('/home/claude/spcx/cards_sheet2.png')
