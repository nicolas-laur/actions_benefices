"""Gros plans de Mister Coin pour les couvertures (24/11/2026).

Les 14 expressions sont dans mister_coin/gros_plans/couv_*.png (détourées, cadre complet 1438 × 2576 : le bas de l'image est le bas de la couverture).
coller() les pose en bas d'une couverture 1080 × 1920 du gabarit lib/cards_lib.py, sous le titre et la question, avec le halo doré habituel.
Liste et usages : mister_coin/veo/prompts_gemini_gros_plans_couvertures.md.
"""
import os
from PIL import Image, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, '..', 'mister_coin', 'gros_plans')
EXPRESSIONS = sorted(f[5:-4] for f in os.listdir(DOSSIER) if f.startswith('couv_') and f.endswith('.png'))

def coller(im, expression, haut_libre=1110, largeur_max=1.0, halo=.7):
    """im : couverture RGBA (1080 × 1920). expression : 'choc', 'etoiles', 'sceptique'…
    haut_libre : y au-dessus duquel rien de Mister Coin ne doit monter (titre, sous-titre et question restent dégagés).
    Il est mis à l'échelle pour tenir sous haut_libre et dans la largeur, centré, posé sur le bas de la couverture."""
    W, H = im.size
    g = Image.open(os.path.join(DOSSIER, f'couv_{expression}.png')).convert('RGBA')
    x0, y0, x1, y1 = g.getbbox()
    e = min(W * largeur_max / g.width, (H - haut_libre) / (g.height - y0))
    g = g.resize((round(g.width * e), round(g.height * e)), Image.LANCZOS)
    cx = (x0 + x1) / 2 * e
    pos = (round(W / 2 - cx), H - g.height)
    calque = Image.new('RGBA', (W, H), 0)
    if pos[0] < 0: g = g.crop((-pos[0], 0, g.width, g.height)); pos = (0, pos[1])   # alpha_composite refuse les positions négatives
    calque.alpha_composite(g, pos)
    lueur = Image.new('RGBA', (W, H), (255, 200, 110, 0))
    lueur.putalpha(calque.getchannel('A').filter(ImageFilter.GaussianBlur(45)).point(lambda v: int(v * halo)))
    im.alpha_composite(lueur); im.alpha_composite(calque)
    return im
