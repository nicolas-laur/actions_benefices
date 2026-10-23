"""Textures des écrans de la salle de marché : tickers fictifs (vert = euphorie, rouge = panique), tuilables horizontalement."""
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
def tick_names(n, seed):
    r = random.Random(seed); A = 'ABCDEFGHJKLMNPRSTUVWXZ'
    return [''.join(r.choice(A) for _ in range(r.choice((3, 4)))) for _ in range(n)]
def board(mode, w=2048, h=512, rows=4, seed=1):
    """bandeau LED : rangées de tickers fictifs, largeur exacte d'un cycle de texte donc tuilable"""
    r = random.Random(seed); up = mode == 'up'; f = ImageFont.truetype(MONO, int(h/rows*0.55))
    tmp = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    lines = []
    for k in range(rows):
        items = []; L = 0
        for nm in tick_names(40, seed*10+k):
            v = r.uniform(12, 480); p = r.uniform(0.4, 6.5) if up else -r.uniform(2.5, 14)
            if up and r.random() < .12: p = -r.uniform(.1, .9)
            if not up and r.random() < .06: p = r.uniform(.1, .5)
            s1 = f'{nm} {v:.2f} '; s2 = ('▲' if p > 0 else '▼') + f'{p:+.1f}%    '
            items.append((s1, s2, p)); L += tmp.textlength(s1+s2, font=f)
            if L >= w: break
        lines.append((items, L))
    W = int(max(L for _, L in lines)); im = Image.new('RGB', (W, h), (2, 2, 3)); d = ImageDraw.Draw(im)
    for k, (items, L) in enumerate(lines):
        y = k*h/rows + h/rows*0.2; x = 0; sc = W/L
        for s1, s2, p in items:
            col = (60, 255, 120) if p > 0 else (255, 50, 60)
            d.text((x, y), s1, font=f, fill=(235, 238, 245)); d.text((x+d.textlength(s1, font=f), y), s2, font=f, fill=col)
            x += d.textlength(s1+s2, font=f)*sc
    g = Image.new('L', (W, h), 0); gd = ImageDraw.Draw(g)
    for yy in range(0, h, 4): gd.line([(0, yy), (W, yy)], fill=90)
    return Image.composite(Image.new('RGB', (W, h), (0, 0, 0)), im, g.point(lambda v: int(v*.6)))
def monitor(mode, seed, w=512, h=320):
    """écran de trader : courbe + carnet d'ordres fictif"""
    im = Image.new('RGB', (w, h), (4, 6, 10)); d = ImageDraw.Draw(im); r = random.Random(seed); up = mode == 'up'
    col = (60, 255, 120) if up else (255, 50, 60)
    for gx in range(0, w, 64): d.line([(gx, 0), (gx, h*0.62)], fill=(18, 24, 34))
    for gy in range(0, int(h*0.62), 40): d.line([(0, gy), (w, gy)], fill=(18, 24, 34))
    pts = []; v = h*0.45
    for i in range(41):
        v += r.uniform(-14, 9) if up else r.uniform(-6, 15)
        if not up and i > 28: v += 4
        v = max(12, min(h*0.6, v)); pts.append((i*w/40, v))
    d.line(pts, fill=col, width=5)
    f = ImageFont.truetype(MONO, 26)
    for k, nm in enumerate(tick_names(3, seed)):
        p = r.uniform(.5, 5) if up else -r.uniform(3, 12)
        d.text((14, h*0.66+k*34), f'{nm}', font=f, fill=(225, 230, 240)); d.text((w*0.55, h*0.66+k*34), f'{p:+.1f}%', font=f, fill=col)
    return im
if __name__ == '__main__':
    for m in ('up', 'down'):
        board(m, seed=3).save(f'board_{m}.png'); board(m, w=2048, h=256, rows=2, seed=9).save(f'band_{m}.png')
        for k in range(6): monitor(m, k+1).save(f'mon_{m}_{k}.png')
    print('ok')
