"""DA « keynote » Apple : grandes affirmations typographiques, dégradés, noir/blanc, produit sous lumière."""
import math, cairo, numpy as np
from PIL import Image, ImageFilter
W,H=1080,1920
def hx(h,a=1): return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
F={'black':"Inter Display Black",'xb':"Inter Display ExtraBold",'b':"Inter Display",'sb':"Inter Display SemiBold",'m':"Inter Display Medium",'r':"Inter Display Light"}
def font(c,w,size):
    c.select_font_face(F[w],0,cairo.FONT_WEIGHT_BOLD if w=='b' else 0); c.set_font_size(size)
def tw(c,s,w,size,track=0):
    font(c,w,size); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def path_text(c,s,x,y,w,size,align='c',track=0):
    tw_=tw(c,s,w,size,track); x0=x-tw_/2 if align=='c' else (x-tw_ if align=='r' else x)
    asc,desc=c.font_extents()[:2]; yy=y+(asc-desc)/2*0.8; c.new_path()
    for ch in s: c.move_to(x0,yy); c.text_path(ch); x0+=c.text_extents(ch).x_advance+track
    return tw_
def text(c,s,x,y,w,size,color,align='c',a=1,track=0):
    path_text(c,s,x,y,w,size,align,track); col(c,color,a); c.fill()
def gtext(c,s,x,y,w,size,stops,align='c',track=0,a=1,diag=True):
    tw_=path_text(c,s,x,y,w,size,align,track); x0=x-tw_/2 if align=='c' else x
    g=cairo.LinearGradient(x0,y-size*.5,x0+tw_,y+size*.5) if diag else cairo.LinearGradient(0,y-size*.5,0,y+size*.5)
    for o,h in stops: g.add_color_stop_rgba(o,*hx(h,a))
    c.set_source(g); c.fill()
SUNSET=[(0,'FF9F0A'),(.45,'FF375F'),(1,'BF5AF2')]
OCEAN=[(0,'64D2FF'),(.5,'0A84FF'),(1,'5E5CE6')]
TITAN=[(0,'F5F5F7'),(.5,'A1A4AA'),(1,'E3E4E7')]
REDG=[(0,'FF6961'),(1,'FF2D55')]
GREENG=[(0,'30D158'),(1,'A6F15A')]
def slide(c,dark=True):
    if dark:
        col(c,'000000'); c.paint()
        g=cairo.RadialGradient(540,900,0,540,900,1100); g.add_color_stop_rgba(0,*hx('16181D',.9)); g.add_color_stop_rgba(1,*hx('000000',0)); c.set_source(g); c.paint()
    else:
        col(c,'FBFBFD'); c.paint()
        g=cairo.RadialGradient(540,900,200,540,900,1300); g.add_color_stop_rgba(0,*hx('FFFFFF',0)); g.add_color_stop_rgba(1,*hx('E8E8ED',.9)); c.set_source(g); c.paint()
def eyebrow(c,s,y,color='86868B'): text(c,s,540,y,'sb',30,color)
def rr(c,x,y,w,h,r):
    r=min(r,w/2,h/2); c.new_sub_path(); c.arc(x+w-r,y+r,r,-math.pi/2,0); c.arc(x+w-r,y+h-r,r,0,math.pi/2); c.arc(x+r,y+h-r,r,math.pi/2,math.pi); c.arc(x+r,y+r,r,math.pi,1.5*math.pi); c.close_path()
def caption(c,words,dark=True,kstops=TITAN,y=1352,size=46):
    fg='F5F5F7' if dark else '1D1D1F'
    sp=tw(c,' ','b',size); wd=[tw(c,w,'b',size) for w,k in words]
    lines,cur,cw=[],[],0
    for i,w in enumerate(wd):
        need=w+(sp if cur else 0)
        if cur and cw+need>780: lines.append((cur,cw)); cur,cw=[],0; need=w
        cur.append(i); cw+=need
    lines.append((cur,cw)); y0=y-(len(lines)-1)*35
    for li,(idx,lw) in enumerate(lines):
        x=540-lw/2; yy=y0+li*70
        for i in idx:
            w,k=words[i]
            if k: gtext(c,w,x,yy,'b',size,kstops,'l')
            else: text(c,w,x,yy,'b',size,fg,'l')
            x+=wd[i]+sp
def progress(c,u,dark=True):
    col(c,'FFFFFF' if dark else '000000',.15); rr(c,140,260,800,5,2.5); c.fill(); rr(c,140,260,max(5,800*u),5,2.5); col(c,'FFFFFF' if dark else '1D1D1F',.85); c.fill()
def to_pil(s): s.flush(); return Image.frombuffer('RGBA',(s.get_width(),s.get_height()),bytes(s.get_data()),'raw','BGRA',s.get_stride(),1).copy()
def glow_under(c_surface, stops, cx, cy, rx, ry, a=0.6):
    """halo coloré doux sous un élément"""
    k=cairo.Context(c_surface); k.save(); k.translate(cx,cy); k.scale(rx,ry)
    g=cairo.RadialGradient(0,0,0,0,0,1)
    n=len(stops)
    for o,h in stops: g.add_color_stop_rgba(0 if o==0 else min(.6,o*0.6),*hx(h,a*(1-o*0.5)))
    g.add_color_stop_rgba(1,*hx(stops[-1][1],0)); k.set_source(g); k.new_path(); k.arc(0,0,1,0,2*math.pi); k.fill(); k.restore()
def hero_phone(c,cx,cy,w,h,rim=SUNSET,screen=None,a=1.0):
    """téléphone de face, éclairé en contre-jour par un liseré coloré"""
    x,y=cx-w/2,cy-h/2
    # halo de contre-jour
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); k=cairo.Context(s)
    rr(k,x-6,y-6,w+12,h+12,w*.2); g=cairo.LinearGradient(x,y,x+w,y+h)
    for o,hh in rim: g.add_color_stop_rgb(o,*hx(hh)[:3])
    k.set_source(g); k.fill()
    im=to_pil(s).filter(ImageFilter.GaussianBlur(60)); d=bytearray(im.tobytes('raw','BGRA'))
    gs=cairo.ImageSurface.create_for_data(d,cairo.FORMAT_ARGB32,W,H,W*4); c.set_source_surface(gs,0,0); c.paint_with_alpha(.9*a)
    # cadre titane
    rr(c,x,y,w,h,w*.18); g=cairo.LinearGradient(x,y,x+w,y)
    for o,v in ((0,'8E9196'),(.08,'E5E6E9'),(.5,'5C6068'),(.92,'E5E6E9'),(1,'8E9196')): g.add_color_stop_rgba(o,*hx(v,a))
    c.set_source(g); c.fill()
    rr(c,x+10,y+10,w-20,h-20,w*.16); col(c,'000000',a); c.fill()
    if screen: c.save(); rr(c,x+18,y+18,w-36,h-36,w*.14); c.clip(); c.translate(x+18,y+18); screen(c,w-36,h-36); c.restore()
    rr(c,cx-w*.14,y+30,w*.28,30,15); col(c,'000000',a); c.fill()
    # reflet
    c.save(); rr(c,x+10,y+10,w-20,h-20,w*.16); c.clip(); g2=cairo.LinearGradient(x,y,x+w,y+h*.5)
    for o,v in ((0,0),(.3,0),(.38,.12*a),(.46,0)): g2.add_color_stop_rgba(o,1,1,1,v)
    c.set_source(g2); c.paint(); c.restore()
def bars(c,items,x0,y0,wmax,bh=58,gap=34,dark=True,hl=0,hstops=OCEAN,t_label='F5F5F7'):
    vmax=max(v for _,v,_ in items)
    for i,(lab,v,txtv) in enumerate(items):
        y=y0+i*(bh+gap); w=wmax*v/vmax
        rr(c,x0,y,w,bh,bh/2)
        if i==hl:
            g=cairo.LinearGradient(x0,0,x0+w,0)
            for o,h in hstops: g.add_color_stop_rgb(o,*hx(h)[:3])
            c.set_source(g)
        else: col(c,'3A3A3C' if dark else 'D2D2D7')
        c.fill()
        text(c,lab,x0,y-24,'sb',26,'A1A1A6','l')
        text(c,txtv,x0+w+18,y+bh/2,'b',30,t_label if i==hl else '86868B','l')
