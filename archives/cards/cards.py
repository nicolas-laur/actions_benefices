import math, cairo
W,H=1080,1920
def hx(h,a=1): return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
def width(c,s,fam,size,track):
    c.select_font_face(fam,0,0); c.set_font_size(size); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def put(c,s,y,fam,size,color,track=0,a=1,x=540):
    w=width(c,s,fam,size,track); x0=x-w/2; c.set_source_rgba(*hx(color,a))
    for ch in s: c.move_to(x0,y); c.show_text(ch); x0+=c.text_extents(ch).x_advance+track
    return w
def bg(c):
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hx('05070C')[:3]); g.add_color_stop_rgb(.55,*hx('0A1730')[:3]); g.add_color_stop_rgb(1,*hx('12306B')[:3]); c.set_source(g); c.paint()
    r=cairo.RadialGradient(540,1500,0,540,1500,900); r.add_color_stop_rgba(0,*hx('2D5BB8',.35)); r.add_color_stop_rgba(1,*hx('2D5BB8',0)); c.set_source(r); c.paint()
def fit(c,s,fam,size,track,maxw):
    while width(c,s,fam,size,track)>maxw: size-=2
    return size
def card(name,slot,path):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); bg(c)
    if slot:
        c.new_path(); x,y,sz,r=390,500,300,36
        c.new_sub_path(); c.arc(x+sz-r,y+r,r,-math.pi/2,0); c.arc(x+sz-r,y+sz-r,r,0,math.pi/2); c.arc(x+r,y+sz-r,r,math.pi/2,math.pi); c.arc(x+r,y+r,r,math.pi,1.5*math.pi); c.close_path()
        c.set_source_rgba(*hx('FFFFFF',.06)); c.fill_preserve(); c.set_dash([14,12]); c.set_source_rgba(*hx('FFFFFF',.55)); c.set_line_width(2.5); c.stroke(); c.set_dash([])
        put(c,"LOGO",y+sz/2+8,"Poppins Medium",26,'FFFFFF',8,.6)
        sz_=fit(c,name,"Poppins Medium",34,10,880); put(c,name,930,"Poppins Medium",sz_,'FFFFFF',10,.85); qy=1090
    else:
        sz_=fit(c,name,"Poppins Medium",92,10,900); put(c,name,800,"Poppins Medium",sz_,'FFFFFF',10); 
        c.new_path(); c.move_to(500,860); c.line_to(580,860); c.set_source_rgba(*hx('FFFFFF',.5)); c.set_line_width(2); c.stroke(); qy=1000
    put(c,"Et toi, tu achètes ?",qy+(0 if not slot else 0),"Poppins Light",58,'FFFFFF',1)
    s.write_to_png(path)
for key,name in (("lvmh","LVMH"),("airliquide","AIR LIQUIDE"),("totalenergies","TOTALENERGIES")):
    card(name,False,f"{key}_tu_achetes.png"); card(name,True,f"{key}_tu_achetes_emplacement_logo.png")
from PIL import Image
fs=[f"{k}_tu_achetes{x}.png" for k in ("lvmh","airliquide","totalenergies") for x in ("","_emplacement_logo")]
sh=Image.new('RGB',(6*360,640),'white')
for i,f in enumerate(fs): sh.paste(Image.open(f).convert('RGB').resize((360,640)),(i*360,0))
sh.save('sheet.png')
