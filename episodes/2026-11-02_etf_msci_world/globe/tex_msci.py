"""Carte des pays (équirectangulaire 4096×2048) : 1-23 = pays développés du MSCI World (ordre d'allumage), 30 = Chine, 31 = Inde."""
import shapefile, numpy as np
from PIL import Image, ImageDraw
W, H = 4096, 2048
DEV = ['United States of America', 'Canada', 'United Kingdom', 'Ireland', 'France', 'Spain', 'Portugal', 'Belgium', 'Netherlands', 'Germany',
       'Switzerland', 'Austria', 'Italy', 'Denmark', 'Norway', 'Sweden', 'Finland', 'Israel', 'Japan', 'Hong Kong', 'Singapore', 'Australia', 'New Zealand']
EXTRA = {'China': 30, 'India': 31}
r = shapefile.Reader('/home/claude/pea/ne/naturalearth_lowres.shp')
im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
def px(lon, lat): return ((lon+180)/360*W, (90-lat)/180*H)
for sh, rec in zip(r.shapes(), r.records()):
    nm = rec['name']; k = DEV.index(nm)+1 if nm in DEV else EXTRA.get(nm)
    if not k: continue
    pts = sh.points; parts = list(sh.parts)+[len(pts)]
    for a, b in zip(parts[:-1], parts[1:]):
        if nm == 'France' and min(p[0] for p in pts[a:b]) < -30: continue          # sans la Guyane
        d.polygon([px(*p) for p in pts[a:b]], fill=k)
for nm, (lon, lat) in {'Hong Kong': (114.17, 22.30), 'Singapore': (103.82, 1.35)}.items():   # trop petits dans la carte : un disque
    x, y = px(lon, lat); k = DEV.index(nm)+1; d.ellipse((x-14, y-14, x+14, y+14), fill=k)
im.save('globe/pays.png'); a = np.asarray(im); print(sorted(set(a.flatten().tolist())))
