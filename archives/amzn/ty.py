import math, cairo
from PIL import Image
W,H=1080,1920
OR='FF9900'; NAVY='131A22'; WH='F7F7F5'; GR='A7B0BA'
def hx(h,a=1): return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def font(c,fam,size,bold=False): c.select_font_face(fam,0,cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c,s,fam,size,bold=False,track=0):
    font(c,fam,size,bold); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def text(c,s,x,y,fam,size,color,bold=False,align='c',a=1,track=0,shadow=True):
    w=tw(c,s,fam,size,bold,track); x0=x-w/2 if align=='c' else (x-w if align=='r' else x)
    asc,desc=c.font_extents()[:2]; yy=y+(asc-desc)/2*0.8
    for pass_ in ((0,) if not shadow else (1,0)):
        xx=x0
        if pass_: col(c,'000000',.55*a)
        else: col(c,color,a)
        for ch in s: c.move_to(xx+(3 if pass_ else 0),yy+(4 if pass_ else 0)); c.show_text(ch); xx+=c.text_extents(ch).x_advance+track
    return w
def rr(c,x,y,w,h,r):
    r=min(r,w/2,h/2); c.new_sub_path(); c.arc(x+w-r,y+r,r,-math.pi/2,0); c.arc(x+w-r,y+h-r,r,0,math.pi/2); c.arc(x+r,y+h-r,r,math.pi/2,math.pi); c.arc(x+r,y+r,r,math.pi,1.5*math.pi); c.close_path()
def label(c,x,y,lines,w=420,rot=-0.03,big=None):
    """étiquette d'expédition : fond blanc cassé, texte noir mono, code-barres"""
    h=40+len(lines)*38+(70 if big else 0)+60
    c.save(); c.translate(x,y); c.rotate(rot)
    c.rectangle(-w/2+6,-h/2+8,w,h); col(c,'000000',.35); c.fill()
    c.rectangle(-w/2,-h/2,w,h); col(c,'F4F1EA'); c.fill()
    c.rectangle(-w/2,-h/2,w,10); col(c,OR); c.fill()
    yy=-h/2+46
    for l in lines: text(c,l,-w/2+24,yy,"JetBrains Mono",24,'111111',True,'l',1,1,False); yy+=38
    if big: text(c,big,-w/2+24,yy+22,"Archivo Black",58,'111111',False,'l',1,0,False); yy+=70
    for i in range(48):
        bw=[2,4,1,3][i*7%4]; c.rectangle(-w/2+24+i*7.6,yy,bw,40); col(c,'111111'); c.fill()
    c.restore()
def caption(c,words,y=1352,size=46):
    sp=tw(c,' ',"Poppins",size,True); wd=[tw(c,w,"Poppins",size,True)+(24 if k else 0) for w,k in words]
    lines,cur,cw=[],[],0
    for i,w in enumerate(wd):
        need=w+(sp if cur else 0)
        if cur and cw+need>780: lines.append((cur,cw)); cur,cw=[],0; need=w
        cur.append(i); cw+=need
    lines.append((cur,cw)); y0=y-(len(lines)-1)*36
    for li,(idx,lw) in enumerate(lines):
        x=540-lw/2; yy=y0+li*72
        for i in idx:
            w,k=words[i]
            if k:
                c.save(); c.translate(x+wd[i]/2,yy); c.rotate(-0.02); c.rectangle(-wd[i]/2,-32,wd[i],62); col(c,OR); c.fill(); c.restore()
                text(c,w,x+12,yy,"Poppins",size,'111111',True,'l',1,0,False)
            else: text(c,w,x,yy,"Poppins",size,WH,True,'l')
            x+=wd[i]+sp
def progress(c,u):
    col(c,'FFFFFF',.18); c.rectangle(140,260,800,6); c.fill(); col(c,OR); c.rectangle(140,260,800*u,6); c.fill()
def vignette(c):
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgba(0,0,0,0,.75); g.add_color_stop_rgba(.22,0,0,0,.45); g.add_color_stop_rgba(.38,0,0,0,0); g.add_color_stop_rgba(.62,0,0,0,0); g.add_color_stop_rgba(.85,0,0,0,.6); g.add_color_stop_rgba(1,0,0,0,.7); c.set_source(g); c.paint()
def compose(bg,draw,out):
    im=Image.open(bg).convert('RGBA').resize((W,H),Image.LANCZOS)
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); vignette(c); draw(c); s.flush()
    ov=Image.frombuffer('RGBA',(W,H),bytes(s.get_data()),'raw','BGRa',s.get_stride(),1); im.alpha_composite(ov); im.convert('RGB').save(out)
