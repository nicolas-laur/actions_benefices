import math, cairo
import da
from da import W,H,hx,col,tw,txt,background,circuits,chip,GRN,WHITE,GREY
import nv
def cover(path, slot):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); c.set_source_surface(background(),0,0); c.paint()
    nv.neon(c,lambda k: circuits(k,1,5,GRN,.3),14,.6)
    if slot:
        c.set_dash([14,10]); col(c,WHITE,.6); c.set_line_width(3); c.rectangle(410,360,260,260); c.stroke(); c.set_dash([])
        txt(c,"LOGO",540,490,"JetBrains Mono",26,GREY,False,'c',1,6); y=760
    else:
        nv.neon(c,lambda k: chip(k,540,500,220),16,.9); y=780
    nv.neon(c,lambda k: txt(k,"NVIDIA,",540,y,"Anton",210,WHITE),18,.3)
    nv.neon(c,lambda k: txt(k,"TU ACHÈTES ?",540,y+210,"Anton",150,GRN),24,1.0)
    c.save(); c.translate(540,y+400); c.rotate(-0.03); w=tw(c,"×11,5 EN 5 ANS","Anton",70)+70
    col(c,GRN); c.rectangle(-w/2,-52,w,104); c.fill(); txt(c,"×11,5 EN 5 ANS",0,0,"Anton",70,'050505'); c.restore()
    from lvmh import logo_symbol
    w2=tw(c,"Actions_Benefices","Poppins",40,True); x0=540-(86+18+w2)/2
    logo_symbol(c,x0+43,1510,86)
    txt(c,"Actions_Benefices",x0+104,1510,"Poppins",40,WHITE,True,'l')
    s.write_to_png(path)
cover('cover_nvidia.png',False); cover('cover_nvidia_logo.png',True)
from PIL import Image
a=Image.open('cover_nvidia.png').resize((540,960)); b=Image.open('cover_nvidia_logo.png').resize((540,960))
sh=Image.new('RGB',(1090,960),'white'); sh.paste(a,(0,0)); sh.paste(b,(550,0)); sh.save('covers_sheet.png')
