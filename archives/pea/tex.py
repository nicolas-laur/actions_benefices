"""Textures du globe (équirectangulaire 4096×2048) depuis Natural Earth : terres en points, masque monde, masque PEA (UE + EEE)."""
import shapefile, numpy as np
from PIL import Image, ImageDraw, ImageFilter
EEA = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland',
       'Italy','Latvia','Lithuania','Luxembourg','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden','Norway','Iceland']
W, H = 4096, 2048
r = shapefile.Reader('ne/naturalearth_lowres.shp')
names = [x['name'] for x in r.records()]
miss = [n for n in EEA if n not in names]; print('absents', miss)
allm = Image.new('L', (W, H), 0); eu = Image.new('L', (W, H), 0); da, de = ImageDraw.Draw(allm), ImageDraw.Draw(eu)
def px(lon, lat): return ((lon+180)/360*W, (90-lat)/180*H)
for sh, rec in zip(r.shapes(), r.records()):
    if rec['name'] == 'Antarctica': continue
    pts = sh.points; parts = list(sh.parts)+[len(pts)]
    for a, b in zip(parts[:-1], parts[1:]):
        ring = [px(*p) for p in pts[a:b]]
        da.polygon(ring, fill=255)
        if rec['name'] in EEA and min(p[0] for p in pts[a:b]) > -30: de.polygon(ring, fill=255)   # sans la Guyane
allm.save('m_all.png'); eu.save('m_eu.png')
# terres en points (grille hexagonale, espacement constant à l'écran : resserré en longitude près des pôles)
dots = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(dots); A = np.asarray(allm)
step = 11
for j, y in enumerate(range(step//2, H, step)):
    lat = 90-y/H*180; sx = step/max(.2, np.cos(np.radians(lat)))
    x = (j % 2)*sx/2
    while x < W:
        if A[int(y), int(x) % W] > 0: dd.ellipse([x-3.2, y-3.2*max(.2, np.cos(np.radians(lat)))**0, x+3.2, y+3.2], fill=255)
        x += sx
dots.save('dots.png')
for n, im in (('m_all', allm), ('m_eu', eu)):
    Image.composite(dots, Image.new('L', (W, H), 0), im).save(f'{n}_dots.png')
print('ok')
