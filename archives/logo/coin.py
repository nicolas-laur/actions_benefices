import math, cairo
from logos import hx
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def arc_text(c,s,cx,cy,r,mid,size,color,top,track=0.0,fam="Poppins Medium"):
    c.select_font_face(fam,cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
    adv=[c.text_extents(ch).x_advance+track for ch in s]; rr=r if top else r+size*0.72
    span=sum(adv)/rr; a=mid-span/2 if top else mid+span/2; col(c,color)
    for ch,w in zip(s,adv):
        da=w/rr; ac=a+da/2 if top else a-da/2
        c.save(); c.translate(cx+rr*math.cos(ac),cy+rr*math.sin(ac)); c.rotate(ac+math.pi/2 if top else ac-math.pi/2)
        c.move_to(-w/2+track/2,0); c.show_text(ch); c.restore(); a=a+da if top else a-da
def curve(c,color,sc,cx,cy,lw=6,area=0.16):
    c.save(); c.translate(cx,cy); c.scale(sc,sc); c.translate(-102,-107)
    c.new_path(); c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54); c.line_to(164,160); c.line_to(40,160); c.close_path(); col(c,color,area); c.fill()
    c.new_path(); c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54); col(c,color); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.new_path(); c.arc(164,54,9,0,2*math.pi); col(c,color); c.fill(); c.restore()
def ticks(c,cx,cy,r0,r1,n,color,lw=2):
    col(c,color); c.set_line_width(lw)
    for i in range(n):
        a=2*math.pi*i/n; c.new_path(); c.move_to(cx+r0*math.cos(a),cy+r0*math.sin(a)); c.line_to(cx+r1*math.cos(a),cy+r1*math.sin(a)); c.stroke()
def disc(c,cx,cy,r,stops,angle=(-1,-1,1,1)):
    g=cairo.LinearGradient(cx+angle[0]*r,cy+angle[1]*r,cx+angle[2]*r,cy+angle[3]*r)
    for o,h in stops: g.add_color_stop_rgb(o,*hx(h)[:3])
    c.new_path(); c.arc(cx,cy,r,0,2*math.pi); c.set_source(g); c.fill()
def ring(c,cx,cy,r,color,lw,a=1): c.new_path(); c.arc(cx,cy,r,0,2*math.pi); col(c,color,a); c.set_line_width(lw); c.stroke()
GOLDS=[(0,'F3E2B0'),(.45,'C9A25E'),(1,'8A6A35')]
def coinA(c,cx,cy,R):  # pièce or classique
    disc(c,cx,cy,R,GOLDS); ticks(c,cx,cy,R*.94,R*.985,120,'7E6136',1.6); ring(c,cx,cy,R*.9,'7E6136',2.5); ring(c,cx,cy,R*.9-3,'F3E2B0',1.5,.7)
    disc(c,cx,cy,R*.82,[(0,'E8D29B'),(1,'B38D4A')],(1,1,-1,-1)); ring(c,cx,cy,R*.82,'7E6136',2)
    arc_text(c,"ACTIONS",cx,cy,R*.64,-math.pi/2,R*.15,'5A4423',True,R*.03); arc_text(c,"BÉNÉFICES",cx,cy,R*.64,math.pi/2,R*.15,'5A4423',False,R*.03)
    for sx in (-1,1): c.new_path(); c.arc(cx+sx*R*.72,cy,R*.022,0,2*math.pi); col(c,'5A4423'); c.fill()
    curve(c,'0B4B3F',R*.0036,cx,cy+R*.02,6,.10)
def coinB(c,cx,cy,R):  # pièce verte, liseré or (cohérente avec D)
    disc(c,cx,cy,R,GOLDS); disc(c,cx,cy,R*.93,[(0,'14A38B'),(1,'0B4B3F')]); ticks(c,cx,cy,R*.955,R*.995,120,'7E6136',1.5)
    ring(c,cx,cy,R*.86,'D8C08E',2.2); ring(c,cx,cy,R*.58,'D8C08E',1.4,.7)
    arc_text(c,"ACTIONS",cx,cy,R*.64,-math.pi/2,R*.15,'F4EFE6',True,R*.03); arc_text(c,"BÉNÉFICES",cx,cy,R*.64,math.pi/2,R*.15,'F4EFE6',False,R*.03)
    for sx in (-1,1): c.new_path(); c.arc(cx+sx*R*.72,cy,R*.022,0,2*math.pi); col(c,'D8C08E'); c.fill()
    curve(c,'FFFFFF',R*.0034,cx,cy+R*.02,6,.15)
def coinC(c,cx,cy,R):  # pièce minimaliste, ivoire et encre
    disc(c,cx,cy,R,[(0,'17140F'),(1,'17140F')]); ring(c,cx,cy,R*.94,'D8C08E',2); ring(c,cx,cy,R*.9,'D8C08E',.8,.6)
    arc_text(c,"ACTIONS",cx,cy,R*.68,-math.pi/2,R*.14,'F4EFE6',True,R*.05); arc_text(c,"BÉNÉFICES",cx,cy,R*.68,math.pi/2,R*.14,'F4EFE6',False,R*.05)
    for sx in (-1,1): c.new_path(); c.arc(cx+sx*R*.78,cy,R*.02,0,2*math.pi); col(c,'D8C08E'); c.fill()
    curve(c,'D8C08E',R*.0034,cx,cy+R*.02,5,.12)
S=700
def tile(c,x,y,fn,name,sub,bg,fg):
    c.save(); c.translate(x,y); col(c,bg); c.rectangle(0,0,S,S+110); c.fill(); c.rectangle(.5,.5,S-1,S+109); col(c,'A8834C',.5); c.set_line_width(1); c.stroke()
    c.select_font_face("Poppins Medium",0,0); c.set_font_size(18); col(c,'A8834C'); c.move_to(30,44); c.show_text(name)
    c.select_font_face("Poppins",0,0); c.set_font_size(15); col(c,fg); c.move_to(30,70); c.show_text(sub)
    fn(c,S/2,S/2+40,S*.34)
    for i,(s_,px) in enumerate(((96,40),(56,160),(32,240))):
        c.save(); c.translate(px,S+10); c.scale(s_/200,s_/200); fn(c,100,100,100); c.restore()
    c.restore()
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,S*3+120,S+110+60); c=cairo.Context(s); col(c,'D9D2C3'); c.paint()
tile(c,30,30,coinA,"A · PIÈCE OR","médaille classique, courbe verte au centre",'F4EFE6','6E665A')
tile(c,S+60,30,coinB,"B · PIÈCE VERTE","même dégradé que le logo D, liseré or",'F4EFE6','6E665A')
tile(c,2*S+90,30,coinC,"C · PIÈCE ENCRE","sobre, courbe or sur fond noir",'F4EFE6','6E665A')
s.write_to_png('coins_sheet.png')
for n,f in (('A',coinA),('B',coinB),('C',coinC)):
    t=cairo.ImageSurface(cairo.FORMAT_ARGB32,1024,1024); cc=cairo.Context(t); f(cc,512,512,500); t.write_to_png(f'coin_{n}.png')
