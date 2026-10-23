import cairo, math, numpy as np
from PIL import Image, ImageFilter
import cards_lib as cards
from cards_lib import W, H, hx
def bg(c):
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hx('030405')[:3]); g.add_color_stop_rgb(.5,*hx('07090C')[:3]); g.add_color_stop_rgb(1,*hx('0E1116')[:3]); c.set_source(g); c.paint()
    # rubans de lumière additifs orange / ambre / bleu nuit
    lay=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); k=cairo.Context(lay); k.set_operator(cairo.OPERATOR_ADD)
    for (x,y,rx,ry,colr,a) in ((540,1560,1150,70,'FF9A3C',.95),(600,1650,1100,45,'8A3A0C',.9),(470,1480,1000,38,'FFD79A',.6),(640,1760,1200,80,'C25A14',.55),(560,1600,700,16,'FFFFFF',.6),(430,1420,900,24,'FFE9C8',.3)):
        k.save(); k.translate(x,y); k.rotate(-0.42+0.04*((x//10)%3)); k.scale(rx,ry)
        r=cairo.RadialGradient(0,0,0,0,0,1); r.add_color_stop_rgba(0,*hx(colr,a)); r.add_color_stop_rgba(1,*hx(colr,0)); k.set_source(r); k.arc(0,0,1,0,2*math.pi); k.fill(); k.restore()
    lay.flush(); im=Image.frombuffer('RGBA',(W,H),bytes(lay.get_data()),'raw','BGRa',lay.get_stride(),1).filter(ImageFilter.GaussianBlur(28))
    arr=np.asarray(im).astype(np.float32); fade=np.clip((np.arange(H)-700)/700,0,1)[:,None,None]; arr[...,:3]*=fade; arr[...,3]*=fade[...,0]
    im=Image.fromarray(arr.astype(np.uint8),'RGBA')
    b=im.tobytes('raw','BGRa'); src=cairo.ImageSurface.create_for_data(bytearray(b),cairo.FORMAT_ARGB32,W,H)
    c.set_operator(cairo.OPERATOR_ADD); c.set_source_surface(src); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
cards.bg=bg
cards.card("COCA-COLA",False,"/mnt/user-data/outputs/cartes/coca_tu_achetes.png")
cards.card("COCA-COLA",True,"/mnt/user-data/outputs/cartes/coca_tu_achetes_emplacement_logo.png")
s=Image.new('RGB',(740,660),'white')
for i,f in enumerate(("coca_tu_achetes","coca_tu_achetes_emplacement_logo")): s.paste(Image.open(f"/mnt/user-data/outputs/cartes/{f}.png").convert('RGB').resize((360,640)),(10+i*370,10))
s.save('/tmp/k08/sheet_coca.png')
