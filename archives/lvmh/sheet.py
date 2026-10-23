import sys, glob
from PIL import Image, ImageDraw
names = sys.argv[2:]; out = sys.argv[1]; s = 0.3; w, h = int(1080*s), int(1920*s); cols = 5
rows = (len(names)+cols-1)//cols; sh = Image.new('RGB', (cols*w, rows*(h+24)), 'white'); d = ImageDraw.Draw(sh)
for i, n in enumerate(names):
    im = Image.open(f'prev_{n}.png').resize((w, h)); o = Image.new('RGBA', im.size, (0,0,0,0)); od = ImageDraw.Draw(o)
    od.rectangle([0, 0, w, 250*s], fill=(255,0,0,40)); od.rectangle([0, h-450*s, w, h], fill=(255,0,0,40)); od.rectangle([w-160*s, 0, w, h], fill=(255,0,0,40))
    im = Image.alpha_composite(im.convert('RGBA'), o).convert('RGB')
    x, y = (i%cols)*w, (i//cols)*(h+24); sh.paste(im, (x, y+24)); d.text((x+6, y+5), n, fill='black')
sh.save(out)
