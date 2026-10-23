import math, cairo
def hx(h,a=1):
    if len(h)==8: a=a*int(h[6:8],16)/255
    return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def lin(x0,y0,x1,y1,stops):
    g=cairo.LinearGradient(x0,y0,x1,y1)
    for o,h in stops: g.add_color_stop_rgba(o,*hx(h))
    return g
def rad(x,y,r0,r1,stops,fx=None,fy=None):
    g=cairo.RadialGradient(fx if fx is not None else x,fy if fy is not None else y,r0,x,y,r1)
    for o,h in stops: g.add_color_stop_rgba(o,*hx(h))
    return g
def circ(c,x,y,r): c.new_path(); c.arc(x,y,r,0,2*math.pi)
SH,HI,MID='9A5A06','FFF4B8','F2B01E'
def arc_path(c,s,cx,cy,r,mid,size,top,track):
    c.select_font_face("Poppins",0,cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    adv=[c.text_extents(ch).x_advance+track for ch in s]; rr=r if top else r+size*0.72
    span=sum(adv)/rr; a=mid-span/2 if top else mid+span/2
    for ch,w in zip(s,adv):
        da=w/rr; ac=a+da/2 if top else a-da/2
        c.save(); c.translate(cx+rr*math.cos(ac),cy+rr*math.sin(ac)); c.rotate(ac+math.pi/2 if top else ac-math.pi/2)
        c.move_to(-w/2+track/2,0); c.text_path(ch); c.restore(); a=a+da if top else a-da
def star_path(c,x,y,r,n=5,inner=.45):
    for i in range(2*n):
        a=-math.pi/2+i*math.pi/n; rr=r if i%2==0 else r*inner
        (c.move_to if i==0 else c.line_to)(x+rr*math.cos(a),y+rr*math.sin(a))
    c.close_path()
def emboss_fill(c,build,d,base):
    for dx,dy,color in ((d,d,SH),(-d*.7,-d*.7,HI)):
        c.save(); c.translate(dx,dy); c.new_path(); build(); col(c,color); c.fill(); c.restore()
    c.new_path(); build(); c.set_source(base); c.fill()
def emboss_stroke(c,build,d,base,lw):
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for dx,dy,color in ((d,d,SH),(-d*.7,-d*.7,HI)):
        c.save(); c.translate(dx,dy); c.new_path(); build(); col(c,color); c.set_line_width(lw); c.stroke(); c.restore()
    c.new_path(); build(); c.set_source(base); c.set_line_width(lw); c.stroke()
def coin_face(c,cx,cy,R,text=True):
    # tranche / biseau extérieur
    circ(c,cx,cy,R); c.set_source(lin(cx-R,cy-R,cx+R,cy+R,[(0,'FFE58A'),(.45,'F5B723'),(1,'B8670A')])); c.fill()
    circ(c,cx,cy,R); col(c,'7A4305'); c.set_line_width(R*.018); c.stroke()
    # crènelage du rebord
    for i in range(90):
        a=2*math.pi*i/90; c.new_path(); c.move_to(cx+R*.955*math.cos(a),cy+R*.955*math.sin(a)); c.line_to(cx+R*.995*math.cos(a),cy+R*.995*math.sin(a))
        col(c,'8A4D06',.45); c.set_line_width(R*.012); c.stroke()
    # biseau intérieur (inversé = creux)
    circ(c,cx,cy,R*.9); c.set_source(lin(cx+R,cy+R,cx-R,cy-R,[(0,'FFE27A'),(.5,'F0A91C'),(1,'B5650A')])); c.fill()
    # champ
    circ(c,cx,cy,R*.84); c.set_source(rad(cx,cy,0,R*.9,[(0,'FFD447'),(.7,'F7B825'),(1,'E39A12')],cx-R*.25,cy-R*.3)); c.fill()
    # anneau en relief
    emboss_stroke(c,lambda: c.arc(cx,cy,R*.6,0,2*math.pi),R*.012,lin(cx-R,cy-R,cx+R,cy+R,[(0,'FFE27A'),(1,'E8A01A')]),R*.025)
    base=lin(cx-R,cy-R,cx+R,cy+R,[(0,'FFE68C'),(.5,'F7BE2E'),(1,'E9A21A')])
    if text:
        emboss_fill(c,lambda: arc_path(c,"ACTIONS",cx,cy,R*.665,-math.pi/2,R*.145,True,R*.03),R*.014,base)
        emboss_fill(c,lambda: arc_path(c,"BÉNÉFICES",cx,cy,R*.73-R*.03-R*.15*.72+R*.0,math.pi/2,R*.15,False,R*.025) ,R*.014,base) if False else None
        emboss_fill(c,lambda: arc_path(c,"BÉNÉFICES",cx,cy,R*.635,math.pi/2,R*.145,False,R*.025),R*.014,base)
        for sx in (-1,1): emboss_fill(c,lambda sx=sx: star_path(c,cx+sx*R*.72,cy,R*.045),R*.008,base)
    # courbe en relief au centre
    k=R*.0047
    def curve():
        c.save(); c.translate(cx,cy+R*.03); c.scale(k,k); c.translate(-102,-107)
        c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54); c.restore()
    def area():
        c.save(); c.translate(cx,cy+R*.03); c.scale(k,k); c.translate(-102,-107)
        c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54); c.line_to(164,160); c.line_to(40,160); c.close_path(); c.restore()
    emboss_stroke(c,curve,R*.016,base,R*.07)
    def dot(): c.save(); c.translate(cx,cy+R*.03); c.scale(k,k); c.translate(-102,-107); c.arc(164,54,14,0,2*math.pi); c.restore()
    emboss_fill(c,dot,R*.016,base)
    # brillance
    c.save(); circ(c,cx,cy,R); c.clip()
    g=lin(cx-R,cy-R,cx+R*.2,cy+R*.2,[(0,'FFFFFF00'),(.42,'FFFFFF00'),(.5,'FFFFFF73'),(.58,'FFFFFF00'),(1,'FFFFFF00')]); c.set_source(g); c.paint()
    c.restore()
def sparkle(c,x,y,r,a=1):
    c.new_path()
    for i in range(8):
        ang=i*math.pi/4-math.pi/2; rr=r if i%2==0 else r*.18
        (c.move_to if i==0 else c.line_to)(x+rr*math.cos(ang),y+rr*math.sin(ang))
    c.close_path(); col(c,'FFFFFF',a); c.fill()
    circ(c,x,y,r*.5); c.set_source(rad(x,y,0,r*.5,[(0,'FFFFFFAA'),(1,'FFFFFF00')])); c.fill()
def flat_coin(c,x,y,rx,ry,th):
    # tranche
    c.new_path(); c.save(); c.translate(x,y); c.scale(rx,ry); c.arc(0,0,1,0,math.pi); c.restore()
    c.line_to(x-rx,y-th); c.save(); c.translate(x,y-th); c.scale(rx,ry); c.arc_negative(0,0,1,math.pi,0); c.restore(); c.close_path()
    c.set_source(lin(x-rx,y,x+rx,y,[(0,'B8670A'),(.3,'F5B723'),(.55,'FFE27A'),(1,'9A5306')])); c.fill()
    for i in range(24):
        xx=x-rx+2*rx*(i+.5)/24; f=math.sqrt(max(0,1-((xx-x)/rx)**2))
        c.new_path(); c.move_to(xx,y-th+ry*f); c.line_to(xx,y+ry*f); col(c,'8A4D06',.3); c.set_line_width(1.6); c.stroke()
    # face
    c.save(); c.translate(x,y-th); c.scale(rx,ry); c.new_path(); c.arc(0,0,1,0,2*math.pi); c.restore()
    c.set_source(lin(x-rx,y-th-ry,x+rx,y-th+ry,[(0,'FFE58A'),(.5,'F5B723'),(1,'D88A10')])); c.fill()
    c.save(); c.translate(x,y-th); c.scale(rx*.8,ry*.8); c.new_path(); c.arc(0,0,1,0,2*math.pi); c.restore()
    col(c,'B8670A',.6); c.set_line_width(2.5); c.stroke()
def stack(c,x,y,n,rx,ry,th):
    for i in range(n):
        flat_coin(c,x+((i*37)%7-3)*1.5,y-i*th,rx,ry,th)
def scene(c,W,H,full=True):
    if full:
        c.set_source(rad(W/2,H*.48,0,W*.75,[(0,'FFF6DE'),(1,'F3E3BC')])); c.paint()
        # ombre au sol
        c.save(); c.translate(W/2,H*.83); c.scale(W*.42,H*.035); circ(c,0,0,1); c.set_source(rad(0,0,0,1,[(0,'5A3A0A55'),(1,'5A3A0A00')])); c.fill(); c.restore()
        stack(c,W*.22,H*.82,6,W*.13,H*.035,H*.024)
        stack(c,W*.79,H*.83,4,W*.12,H*.033,H*.024)
        flat_coin(c,W*.36,H*.86,W*.11,H*.03,H*.02); flat_coin(c,W*.66,H*.87,W*.1,H*.028,H*.02)
        coin_face(c,W/2,H*.47,W*.33)
        for x,y,r in ((.82,.2,.045),(.17,.33,.03),(.75,.62,.022),(.3,.13,.02)): sparkle(c,W*x,H*y,W*r)
    else:
        coin_face(c,W/2,H/2,W*.47)
for name,full in (("piece_frappee_scene",True),("piece_frappee_seule",False)):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1400,1400); c=cairo.Context(s); scene(c,1400,1400,full); s.write_to_png(name+".png")
from PIL import Image
a=Image.open("piece_frappee_scene.png").convert('RGB').resize((900,900)); b=Image.open("piece_frappee_seule.png")
sh=Image.new('RGB',(1500,960),(232,217,181)); sh.paste(a,(30,30))
for s_,y in ((440,40),(160,520),(80,720),(40,840)):
    bb=b.resize((s_,s_),Image.LANCZOS); sh.paste(bb,(960+(440-s_)//2,y),bb)
sh.save("struck_sheet.png")
