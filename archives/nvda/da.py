import math, cairo, numpy as np, random
from PIL import Image, ImageFilter
W,H=1080,1920
def hx(h,a=1): return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
BG,BG2,GRN,GRN_L,GRN_D,WHITE,GREY,RED='07080A','0E1114','76FF3A','C8FF9E','2E7A12','F4F6F2','8A9298','FF3B4E'
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def font(c,fam,size,bold=False): c.select_font_face(fam,0,cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c,s,fam,size,bold=False,track=0):
    font(c,fam,size,bold); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def txt(c,s,x,y,fam,size,color,bold=False,align='c',a=1,track=0):
    w=tw(c,s,fam,size,bold,track); x0=x-w/2 if align=='c' else (x-w if align=='r' else x)
    asc,desc=c.font_extents()[:2]; yy=y+(asc-desc)/2*0.8; col(c,color,a)
    for ch in s: c.move_to(x0,yy); c.show_text(ch); x0+=c.text_extents(ch).x_advance+track
    return w
def to_pil(s): s.flush(); return Image.frombuffer('RGBA',(s.get_width(),s.get_height()),bytes(s.get_data()),'raw','BGRA',s.get_stride(),1)
def to_cairo(im):
    d=bytearray(im.tobytes('raw','BGRA')); return cairo.ImageSurface.create_for_data(d,cairo.FORMAT_ARGB32,im.width,im.height,im.width*4)
def neon(c,draw,blur=18,strength=1.0):
    """dessine draw() net + halo flou additif"""
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); k=cairo.Context(s); draw(k)
    g=to_cairo(to_pil(s).filter(ImageFilter.GaussianBlur(blur)))
    c.save(); c.set_operator(cairo.OPERATOR_ADD); c.set_source_surface(g,0,0); c.paint_with_alpha(strength); c.restore()
    c.set_source_surface(s,0,0); c.paint()
_BG=None
def background():
    global _BG
    if _BG: return _BG
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); col(c,BG); c.paint()
    r=cairo.RadialGradient(540,860,0,540,860,1100); r.add_color_stop_rgba(0,*hx('14301A',.9)); r.add_color_stop_rgba(1,*hx(BG,0)); c.set_source(r); c.paint()
    col(c,'FFFFFF',.035); c.set_line_width(1)
    for x in range(0,W,60): c.move_to(x+.5,0); c.line_to(x+.5,H)
    for y in range(0,H,60): c.move_to(0,y+.5); c.line_to(W,y+.5)
    c.stroke()
    rng=np.random.default_rng(2); n=(rng.standard_normal((H,W))*5).astype(np.int16)
    s.flush(); a=np.ndarray((H,W,4),np.uint8,s.get_data())
    for k in range(3): a[:,:,k]=np.clip(a[:,:,k].astype(np.int16)+n,0,255)
    s.mark_dirty(); _BG=s; return s
def circuits(c,u=1.0,seed=5,color=GRN,a=.55):
    rnd=random.Random(seed); c.set_line_width(2.2); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for i in range(14):
        side=i%2; y0=rnd.randrange(330,1250,30); x=0 if side==0 else W; y=y0; pts=[(x,y)]
        tx=540+(-1 if side==0 else 1)*rnd.choice([150,190,230]); 
        x1=x+(1 if side==0 else -1)*rnd.randrange(80,260,20); pts.append((x1,y))
        ty=rnd.randrange(700,1020,20); dy=ty-y; x2=x1+(1 if side==0 else -1)*abs(dy); pts.append((x2 if abs(x2-540)>abs(tx-540) else tx,ty)); pts.append((tx,ty))
        L=sum(math.dist(pts[j],pts[j+1]) for j in range(len(pts)-1)); rem=L*u
        c.new_path(); c.move_to(*pts[0]); last=pts[0]
        for j in range(len(pts)-1):
            d=math.dist(pts[j],pts[j+1])
            if rem<=0: break
            if d<1e-6: continue
            f=min(1,rem/d); last=(pts[j][0]+(pts[j+1][0]-pts[j][0])*f,pts[j][1]+(pts[j+1][1]-pts[j][1])*f); c.line_to(*last); rem-=d
        col(c,color,a); c.stroke()
        c.new_path(); c.arc(*last,4.5,0,2*math.pi); col(c,color,a+.3); c.fill()
def chip(c,cx,cy,s,glow=1.0):
    h=s/2
    col(c,'0B0E10'); c.rectangle(cx-h,cy-h,s,s); c.fill()
    c.set_line_width(3); col(c,GRN,.9); c.rectangle(cx-h,cy-h,s,s); c.stroke()
    for i in range(10):  # broches
        p=-h+s*(i+.5)/10
        for (x0,y0,x1,y1) in ((cx+p,cy-h,cx+p,cy-h-26),(cx+p,cy+h,cx+p,cy+h+26),(cx-h,cy+p,cx-h-26,cy+p),(cx+h,cy+p,cx+h+26,cy+p)):
            c.new_path(); c.move_to(x0,y0); c.line_to(x1,y1); col(c,GRN,.75); c.set_line_width(5); c.stroke()
    d=s*.62; col(c,'12161A'); c.rectangle(cx-d/2,cy-d/2,d,d); c.fill()
    for i in range(6):
        for j in range(6):
            q=d/6; col(c,GRN,.10+.5*((i*7+j*3)%5==0)); c.rectangle(cx-d/2+i*q+4,cy-d/2+j*q+4,q-8,q-8); c.fill()
    col(c,GRN_L,.8); c.set_line_width(1.5); c.rectangle(cx-d/2,cy-d/2,d,d); c.stroke()
def caption(c,words,y=1350,size=50):
    # mots blancs, mot-clé sur pavé vert texte noir
    items=[(w,k) for w,k in words]; sp=tw(c,' ',"Poppins",size,True)
    wd=[tw(c,w,"Poppins",size,True)+(24 if k else 0) for w,k in items]
    lines,cur,cw=[],[],0
    for i,w in enumerate(wd):
        need=w+(sp if cur else 0)
        if cur and cw+need>760: lines.append((cur,cw)); cur,cw=[],0; need=w
        cur.append(i); cw+=need
    lines.append((cur,cw)); y0=y-(len(lines)-1)*38
    for li,(idx,lw) in enumerate(lines):
        x=540-lw/2; yy=y0+li*76
        for i in idx:
            w,k=items[i]
            if k:
                c.save(); c.translate(x+wd[i]/2,yy); c.rotate(-0.025); col(c,GRN); c.rectangle(-wd[i]/2,-34,wd[i],66); c.fill(); c.restore()
                txt(c,w,x+12,yy,"Poppins",size,'050505',True,'l')
            else:
                txt(c,w,x+2,yy+3,"Poppins",size,'000000',True,'l',.6); txt(c,w,x,yy,"Poppins",size,WHITE,True,'l')
            x+=wd[i]+sp
def progress(c,u):
    col(c,'FFFFFF',.15); c.rectangle(140,262,800,5); c.fill(); col(c,GRN); c.rectangle(140,262,800*u,5); c.fill()
def tag(c,s,y,color=GRN):
    w=tw(c,s,"JetBrains Mono",24,False,3)+40
    c.new_path(); c.rectangle(540-w/2,y-24,w,48); col(c,color,.12); c.fill(); col(c,color,.8); c.set_line_width(1.5); c.rectangle(540-w/2,y-24,w,48); c.stroke()
    txt(c,s,540,y,"JetBrains Mono",24,color,False,'c',1,3)

def k1(c):
    c.set_source_surface(background(),0,0); c.paint(); progress(c,.06)
    neon(c,lambda k: circuits(k,1.0,5,GRN,.28),14,.6)
    tag(c,"NVDA · 5 ANS",360)
    txt(c,"1 000 €",540,470,"Anton",110,GREY)
    c.new_path(); c.move_to(390,472); c.line_to(690,456); col(c,RED,.9); c.set_line_width(6); c.stroke()
    neon(c,lambda k: txt(k,"×11",540,800,"Anton",400,GRN),28,1.1)
    txt(c,"11 486 €",540,1090,"Anton",110,WHITE)
    caption(c,[("1",0),("000",0),("€",0),("il",0),("y",0),("a",0),("5",0),("ans",0),("dans",0),("Nvidia",1),("?",0)])
def k2(c):
    c.set_source_surface(background(),0,0); c.paint(); progress(c,.55)
    neon(c,lambda k: (circuits(k,1.0,9,GRN,.25),chip(k,540,560,250)),16,.9)
    txt(c,"5 500",540,890,"Anton",230,WHITE)
    txt(c,"MILLIARDS DE DOLLARS",540,1030,"JetBrains Mono",30,GRN,False,'c',1,4)
    # barres de comparaison
    for i,(lab,v,cl) in enumerate((("NVIDIA",5.5,GRN),("TOUT LE CAC 40",3.0,GREY))):
        y=1110+i*70; w=600*v/5.5
        txt(c,lab,170,y,"JetBrains Mono",22,cl,False,'l',1,2)
        col(c,cl,.9 if i==0 else .5); c.rectangle(440,y-16,w*0.78,32); c.fill()
    caption(c,[("Elle",0),("vaut",0),("presque",0),("2 CAC 40",1),("entiers.",0)],1390)
def k3(c):
    c.set_source_surface(background(),0,0); c.paint(); progress(c,.4)
    tag(c,"COURS NVDA · $",340)
    P=[(0,20.7),(.2,32),(.5,24),(1,13.5),(1.3,19),(1.7,40),(2.0,46),(2.3,90),(2.6,120),(2.9,135),(3.2,105),(3.5,147),(3.75,120),(4.0,186),(4.3,207),(4.5,180),(4.75,190),(4.9,210),(4.98,243),(5,230.5)]
    X0,X1,YB,YT=160,850,1180,470
    X=lambda u:X0+u/5*(X1-X0); Y=lambda v:YB-v/260*(YB-YT)
    for v in (50,100,150,200,250):
        col(c,'FFFFFF',.06); c.rectangle(X0,Y(v),X1-X0,1); c.fill(); txt(c,f"{v}",X1+12,Y(v),"JetBrains Mono",18,GREY,False,'l')
    def curve(k,width=5):
        k.new_path(); k.move_to(X(P[0][0]),Y(P[0][1]))
        for u,v in P[1:]: k.line_to(X(u),Y(v))
        col(k,GRN); k.set_line_width(width); k.set_line_join(cairo.LINE_JOIN_ROUND); k.stroke()
    c.new_path(); c.move_to(X(0),YB)
    for u,v in P: c.line_to(X(u),Y(v))
    c.line_to(X(5),YB); c.close_path(); g=cairo.LinearGradient(0,YT,0,YB); g.add_color_stop_rgba(0,*hx(GRN,.28)); g.add_color_stop_rgba(1,*hx(GRN,0)); c.set_source(g); c.fill()
    neon(c,curve,14,1.2)
    for u,v,lab,cl,dy in ((1,13.5,"13,5 $  ·  OCT. 2022",RED,-46),(4.98,243,"243 $  ·  RECORD",GRN,-55)):
        c.new_path(); c.arc(X(u),Y(v),9,0,2*math.pi); col(c,cl); c.fill()
        txt(c,lab,X(u)+(10 if u<3 else -10),Y(v)+dy,"JetBrains Mono",22,cl,False,'l' if u<3 else 'r',1,1)
    txt(c,"×18",X(1.6),Y(185),"Anton",150,WHITE)
    for j,yr in enumerate(("2022","2023","2024","2025","2026")): txt(c,yr,X(.23+j)+40,YB+34,"JetBrains Mono",18,GREY)
    caption(c,[("Du",0),("creux",0),("de",0),("2022",0),("au",0),("record",0),(":",0),("×18.",1)])
if __name__=="__main__":
    for name,fn in (("k1_accroche",k1),("k2_monstre",k2),("k3_courbe",k3)):
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); fn(c); s.write_to_png(name+".png")
    ims=[Image.open(f"{n}.png").convert('RGB').resize((540,960)) for n in ("k1_accroche","k2_monstre","k3_courbe")]
    sh=Image.new('RGB',(1680,1000),'white')
    for i,im in enumerate(ims): sh.paste(im,(20+i*550,20))
    sh.save("sheet.png")
