import math, cairo, numpy as np
from PIL import Image, ImageFilter, ImageChops
from ui import hx, col, tw, txt, rr, to_pil, to_cairo, W, H
RED,GRN,BLU,YEL='F25022','7FBA00','00A4EF','FFB900'
def surf(w,h): s=cairo.ImageSurface(cairo.FORMAT_ARGB32,int(w),int(h)); return s, cairo.Context(s)
def pil(s): return to_pil(s).copy()
# ---------- fond « aurore » ----------
def aurora(blobs, base=('03050B','070C1C'), seed=3):
    s,c=surf(W,H); g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hx(base[0])[:3]); g.add_color_stop_rgb(1,*hx(base[1])[:3]); c.set_source(g); c.paint()
    for x,y,r,h_,a in blobs:
        rg=cairo.RadialGradient(x,y,0,x,y,r); rg.add_color_stop_rgba(0,*hx(h_,a)); rg.add_color_stop_rgba(.5,*hx(h_,a*.35)); rg.add_color_stop_rgba(1,*hx(h_,0)); c.set_source(rg); c.paint()
    rng=np.random.default_rng(seed)
    for i in range(60):   # poussière / bokeh
        x,y,r=rng.uniform(0,W),rng.uniform(250,1700),rng.uniform(1,4); a=rng.uniform(.05,.35)
        c.new_path(); c.arc(x,y,r,0,2*math.pi); col(c,'FFFFFF',a); c.fill()
    im=pil(s).convert('RGB'); a_=np.asarray(im).astype(np.int16); n=(rng.standard_normal((H,W,1))*3).astype(np.int16)
    return Image.fromarray(np.clip(a_+n,0,255).astype(np.uint8)).convert('RGBA')
# ---------- perspective ----------
def coeffs(dst, src):
    A=[]; B=[]
    for (x,y),(X,Y) in zip(dst,src):
        A.append([x,y,1,0,0,0,-X*x,-X*y]); A.append([0,0,0,x,y,1,-Y*x,-Y*y]); B+= [X,Y]
    return np.linalg.solve(np.array(A,float),np.array(B,float)).tolist()
def tilt_quad(cx,cy,w,h,ry=0.0,rx=0.0,depth=1800):
    """projette un rectangle tourné autour des axes Y (ry) et X (rx), en radians"""
    pts=[]
    for (u,v) in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)):
        x,y,z=u,v,0.0
        x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
        y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
        f=depth/(depth+z); pts.append((cx+x*f,cy+y*f))
    return pts
def place(canvas, panel, quad, frost=26, shadow=0.55, dof=0.0):
    """compose un panneau de verre (RGBA) sur canvas en perspective, avec flou d'arrière-plan et ombre"""
    w,h=panel.size; src=[(0,0),(w,0),(w,h),(0,h)]
    cf=coeffs(quad,src)
    warped=panel.transform((W,H),Image.PERSPECTIVE,cf,Image.BICUBIC)
    mask=warped.split()[3]
    shape=Image.new('L',(w,h),0); shape.paste(panel.split()[3].point(lambda v:255 if v>8 else 0))
    smask=shape.transform((W,H),Image.PERSPECTIVE,cf,Image.BICUBIC)
    if shadow>0:
        sh=smask.filter(ImageFilter.GaussianBlur(40)); sh=ImageChops.offset(sh,0,30).point(lambda v:int(v*shadow))
        canvas.paste(Image.new('RGBA',(W,H),(0,0,10,255)),(0,0),sh)
    if frost>0:
        bl=canvas.filter(ImageFilter.GaussianBlur(frost)); canvas.paste(bl,(0,0),smask)
    if dof>0: warped=warped.filter(ImageFilter.GaussianBlur(dof))
    canvas.alpha_composite(warped)
    return canvas
def glass_panel(w,h,draw=None,r=36,tint='FFFFFF',ta=0.12,edge=0.6):
    s,c=surf(w,h)
    rr(c,1,1,w-2,h-2,r); g=cairo.LinearGradient(0,0,w*.6,h); g.add_color_stop_rgba(0,*hx(tint,ta*1.8)); g.add_color_stop_rgba(1,*hx(tint,ta*.6)); c.set_source(g); c.fill()
    # reflet spéculaire diagonal
    c.save(); rr(c,1,1,w-2,h-2,r); c.clip(); g2=cairo.LinearGradient(0,0,w,h*.7)
    g2.add_color_stop_rgba(0,1,1,1,0); g2.add_color_stop_rgba(.32,1,1,1,.0); g2.add_color_stop_rgba(.38,1,1,1,.10); g2.add_color_stop_rgba(.46,1,1,1,0); c.set_source(g2); c.paint(); c.restore()
    # bord lumineux
    rr(c,1.5,1.5,w-3,h-3,r); g3=cairo.LinearGradient(0,0,w,h); g3.add_color_stop_rgba(0,1,1,1,edge); g3.add_color_stop_rgba(.5,1,1,1,edge*.25); g3.add_color_stop_rgba(1,1,1,1,edge*.6)
    c.set_source(g3); c.set_line_width(2.2); c.stroke()
    if draw: draw(c,w,h)
    return pil(s)
def glow_text(canvas, s, x, y, size, fam="Poppins", bold=True, top='FFFFFF', bottom='9FD8FF', glow='00A4EF', ga=0.8, reflect=True, track=-4):
    """grand texte à dégradé, halo et reflet au sol"""
    L,c=surf(W,H); w=tw(c,s,fam,size,bold,track); x0=x-w/2
    c.select_font_face(fam,0,cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
    asc,desc=c.font_extents()[:2]; yy=y+(asc-desc)/2*0.8
    c.new_path(); xx=x0
    for ch in s: c.move_to(xx,yy); c.text_path(ch); xx+=c.text_extents(ch).x_advance+track
    g=cairo.LinearGradient(0,y-size*.45,0,y+size*.4); g.add_color_stop_rgb(0,*hx(top)[:3]); g.add_color_stop_rgb(1,*hx(bottom)[:3]); c.set_source(g); c.fill()
    im=pil(L)
    gl=Image.new('RGBA',(W,H),hx(glow)[:3] and tuple(int(v*255) for v in hx(glow)[:3])+(0,)); a=im.split()[3].filter(ImageFilter.GaussianBlur(size*.18)).point(lambda v:int(v*ga))
    gl.putalpha(a); canvas.alpha_composite(gl)
    if reflect:
        top_=int(yy-asc*0.78); bot=int(yy+desc*0.3); band=im.crop((0,top_,W,bot)).transpose(Image.FLIP_TOP_BOTTOM)
        fade=Image.linear_gradient('L').resize(band.size).point(lambda v:int(v*0.0)) 
        grad=np.linspace(0.16,0,band.size[1])[:,None]*np.ones((1,band.size[0])); al=(np.asarray(band.split()[3]).astype(float)*grad).astype(np.uint8)
        band.putalpha(Image.fromarray(al)); band=band.filter(ImageFilter.GaussianBlur(3)); canvas.alpha_composite(band,(0,bot+6))
    canvas.alpha_composite(im)
    return canvas
def cairo_layer(fn):
    s,c=surf(W,H); fn(c); return pil(s)
def caption(c,words,y=1350,size=48,kcol=BLU):
    sp=tw(c,' ',"Poppins",size,True); wd=[tw(c,w,"Poppins",size,True)+(28 if k else 0) for w,k in words]
    lines,cur,cw=[],[],0
    for i,w in enumerate(wd):
        need=w+(sp if cur else 0)
        if cur and cw+need>760: lines.append((cur,cw)); cur,cw=[],0; need=w
        cur.append(i); cw+=need
    lines.append((cur,cw)); y0=y-(len(lines)-1)*37
    for li,(idx,lw) in enumerate(lines):
        x=540-lw/2; yy=y0+li*74
        for i in idx:
            w,k=words[i]
            if k:
                rr(c,x,yy-34,wd[i],66,33); g=cairo.LinearGradient(x,0,x+wd[i],0); g.add_color_stop_rgba(0,*hx(kcol)); g.add_color_stop_rgba(1,*hx(kcol,.75)); c.set_source(g); c.fill()
                txt(c,w,x+14,yy,"Poppins",size,'FFFFFF',True,'l')
            else: txt(c,w,x+2,yy+3,"Poppins",size,'000000',True,'l',.5); txt(c,w,x,yy,"Poppins",size,'FFFFFF',True,'l')
            x+=wd[i]+sp
def progress(c,u,color=BLU):
    col(c,'FFFFFF',.15); rr(c,140,260,800,6,3); c.fill(); rr(c,140,260,max(6,800*u),6,3); col(c,color); c.fill()
def pill(c,s,x,y,color='FFFFFF',size=24,a=.12):
    w=tw(c,s,"JetBrains Mono",size,False,3)+44; rr(c,x-w/2,y-24,w,48,24); col(c,'FFFFFF',a); c.fill()
    rr(c,x-w/2+.5,y-23.5,w-1,47,24); col(c,'FFFFFF',.35); c.set_line_width(1.2); c.stroke(); txt(c,s,x,y,"JetBrains Mono",size,color,False,'c',1,3)
