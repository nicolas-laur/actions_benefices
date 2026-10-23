import math, cairo
def hx(h,a=1): return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
OUT='4A2A10'; Y1='FFD43B'; Y2='F2A516'; Y3='C97A0B'; HI='FFF3B0'; GRN='1FA37A'; GRN_D='0B5C45'
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def circ(c,x,y,r): c.new_path(); c.arc(x,y,r,0,2*math.pi)
def disc(c,x,y,r,fill,outline=OUT,lw=10):
    circ(c,x,y,r)
    if isinstance(fill,str): col(c,fill)
    else: c.set_source(fill)
    c.fill_preserve(); col(c,outline); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
def lin(c,x0,y0,x1,y1,stops):
    g=cairo.LinearGradient(x0,y0,x1,y1)
    for o,h in stops: g.add_color_stop_rgb(o,*hx(h)[:3])
    return g
def star(c,x,y,r,color='FFFFFF'):
    c.new_path(); n=4
    for i in range(n*2):
        a=math.pi/2*i/1 *0.5*2/ 2 if False else i*math.pi/4-math.pi/2; rr=r if i%2==0 else r*.28
        (c.move_to if i==0 else c.line_to)(x+rr*math.cos(a),y+rr*math.sin(a))
    c.close_path(); col(c,color); c.fill()
def arc_text(c,s,cx,cy,r,mid,size,top,track=0,fill='FFF8DC',lw=9):
    c.select_font_face("Poppins",0,cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    adv=[c.text_extents(ch).x_advance+track for ch in s]; rr=r if top else r+size*0.72
    span=sum(adv)/rr; a=mid-span/2 if top else mid+span/2
    for stage in (0,1):
        a_=a
        for ch,w in zip(s,adv):
            da=w/rr; ac=a_+da/2 if top else a_-da/2
            c.save(); c.translate(cx+rr*math.cos(ac),cy+rr*math.sin(ac)); c.rotate(ac+math.pi/2 if top else ac-math.pi/2)
            c.move_to(-w/2+track/2,0); c.text_path(ch)
            if stage==0: col(c,OUT); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
            else: col(c,fill); c.fill()
            c.restore(); a_=a_+da if top else a_-da
def coin_body(c,cx,cy,R):
    disc(c,cx,cy,R,lin(c,cx-R,cy-R,cx+R,cy+R,[(0,'FFE066'),(.55,Y1),(1,Y2)]),OUT,R*.045)
    # crans stylisés sur la tranche
    col(c,OUT,.55); c.set_line_width(R*.02); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(36):
        a=2*math.pi*i/36; c.new_path(); c.move_to(cx+R*.86*math.cos(a),cy+R*.86*math.sin(a)); c.line_to(cx+R*.93*math.cos(a),cy+R*.93*math.sin(a)); c.stroke()
    disc(c,cx,cy,R*.78,lin(c,cx+R,cy+R,cx-R,cy-R,[(0,'F7B52A'),(1,'FFE27A')]),OUT,R*.03)

def shine(c,cx,cy,R):
    c.new_path(); c.arc(cx,cy,R*.86,math.radians(200),math.radians(262)); col(c,'FFFFFF',.9); c.set_line_width(R*.06); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.new_path(); c.arc(cx,cy,R*.86,math.radians(272),math.radians(282)); c.stroke()
def chart(c,cx,cy,k,color=GRN,out=OUT):
    c.save(); c.translate(cx,cy); c.scale(k,k); c.translate(-102,-107)
    pts=lambda: (c.move_to(40,146),c.curve_to(80,142,100,124,120,98),c.curve_to(138,76,150,66,164,54))
    c.new_path(); pts(); col(c,out); c.set_line_width(22); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.new_path(); c.arc(164,54,17,0,2*math.pi); col(c,out); c.fill()
    c.new_path(); pts(); col(c,color); c.set_line_width(11); c.stroke()
    c.new_path(); c.arc(164,54,11,0,2*math.pi); col(c,'FFFFFF'); c.fill(); c.new_path(); c.arc(164,54,11,0,2*math.pi); col(c,color); c.set_line_width(5); c.stroke(); c.restore()
def shadow(c,cx,cy,w,h): 
    c.save(); c.translate(cx,cy); c.scale(w,h); circ(c,0,0,1); col(c,'4A2A10',.18); c.fill(); c.restore()
def coinA(c,cx,cy,R):
    shadow(c,cx,cy+R*1.08,R*.8,R*.1); coin_body(c,cx,cy,R)
    arc_text(c,"ACTIONS",cx,cy,R*.55,-math.pi/2,R*.19,True,R*.02); arc_text(c,"BÉNÉFICES",cx,cy,R*.55,math.pi/2,R*.19,False,R*.02)
    chart(c,cx,cy+R*.02,R*.0046); shine(c,cx,cy,R); star(c,cx+R*.95,cy-R*.78,R*.17); star(c,cx-R*1.02,cy+R*.58,R*.11)
def face(c,cx,cy,R):
    for sx in (-1,1):
        c.save(); c.translate(cx+sx*R*.2,cy-R*.1); c.scale(1,1.3); circ(c,0,0,R*.075); col(c,OUT); c.fill(); c.restore()
        circ(c,cx+sx*R*.2+R*.02,cy-R*.1-R*.05,R*.025); col(c,'FFFFFF'); c.fill()
        circ(c,cx+sx*R*.36,cy+R*.1,R*.07); col(c,'FF8A65',.55); c.fill()
    c.new_path(); c.arc(cx,cy+R*.06,R*.15,math.radians(20),math.radians(160)); col(c,OUT); c.set_line_width(R*.05); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
def arrow(c,x,y,s):
    c.save(); c.translate(x,y); c.scale(s,s); c.rotate(-math.pi/4)
    c.new_path(); c.move_to(-60,14); c.line_to(20,14); c.line_to(20,36); c.line_to(70,0); c.line_to(20,-36); c.line_to(20,-14); c.line_to(-60,-14); c.close_path()
    col(c,GRN); c.fill_preserve(); col(c,OUT); c.set_line_width(9); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke(); c.restore()
def coinB(c,cx,cy,R):
    shadow(c,cx,cy+R*1.08,R*.8,R*.1); coin_body(c,cx,cy,R)
    arc_text(c,"ACTIONS",cx,cy,R*.55,-math.pi/2,R*.19,True,R*.02); arc_text(c,"BÉNÉFICES",cx,cy,R*.55,math.pi/2,R*.19,False,R*.02)
    face(c,cx,cy+R*.02,R*.9); shine(c,cx,cy,R); arrow(c,cx+R*.92,cy-R*.72,R*.0055); star(c,cx-R*1.02,cy-R*.5,R*.12)
def coinC(c,cx,cy,R):  # pièce inclinée avec épaisseur, traînée de petites pièces
    shadow(c,cx,cy+R*1.1,R*.85,R*.1)
    c.save(); c.translate(cx,cy); c.rotate(math.radians(-12))
    for d in range(14,0,-2):  # épaisseur
        disc(c,d*R*.012,d*R*.012,R,'D98A0C',OUT,R*.045 if d==14 else 0.1)
    disc(c,0,0,R,lin(c,-R,-R,R,R,[(0,'FFE066'),(.55,Y1),(1,Y2)]),OUT,R*.045)
    disc(c,0,0,R*.78,lin(c,R,R,-R,-R,[(0,'F7B52A'),(1,'FFE27A')]),OUT,R*.03)
    arc_text(c,"ACTIONS",0,0,R*.55,-math.pi/2,R*.19,True,R*.02); arc_text(c,"BÉNÉFICES",0,0,R*.55,math.pi/2,R*.19,False,R*.02)
    chart(c,0,R*.02,R*.0046); shine(c,0,0,R); c.restore()
    for i,(x,y,r) in enumerate(((-1.25,.2,.1),(-1.4,.55,.07),(-1.1,.75,.05))):
        c.save(); c.translate(cx+x*R,cy+y*R); disc(c,0,0,R*r*1.6,Y1,OUT,R*.02); c.restore()
    star(c,cx+R*.98,cy-R*.8,R*.18); star(c,cx+R*1.15,cy-R*.4,R*.09)
S=700
def tile(c,x,y,fn,name,sub):
    c.save(); c.translate(x,y); g=cairo.LinearGradient(0,0,0,S+110); g.add_color_stop_rgb(0,*hx('FFF7E0')[:3]); g.add_color_stop_rgb(1,*hx('FFE9B8')[:3]); c.set_source(g); c.rectangle(0,0,S,S+110); c.fill()
    c.select_font_face("Poppins",0,cairo.FONT_WEIGHT_BOLD); c.set_font_size(20); col(c,Y3); c.move_to(30,44); c.show_text(name)
    c.select_font_face("Poppins",0,0); c.set_font_size(15); col(c,'6B4A1F'); c.move_to(30,70); c.show_text(sub)
    fn(c,S/2,S/2+30,S*.3)
    for s_,px in ((96,40),(56,160),(32,240)):
        c.save(); c.translate(px,S+8); c.scale(s_/200,s_/200); fn(c,100,100,86); c.restore()
    c.restore()
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,S*3+120,S+110+60); c=cairo.Context(s); col(c,'E8D9B5'); c.paint()
tile(c,30,30,coinA,"A · PIÈCE CARTOON","contour épais, reflet, étincelles, courbe verte")
tile(c,S+60,30,coinB,"B · PIÈCE MASCOTTE","un visage souriant, flèche qui monte")
tile(c,2*S+90,30,coinC,"C · PIÈCE EN MOUVEMENT","inclinée, avec épaisseur et petites pièces")
s.write_to_png('toon_sheet.png')
for n,f in (('A',coinA),('B',coinB),('C',coinC)):
    t=cairo.ImageSurface(cairo.FORMAT_ARGB32,1024,1024); cc=cairo.Context(t); f(cc,512,500,380); t.write_to_png(f'coin_cartoon_{n}.png')
