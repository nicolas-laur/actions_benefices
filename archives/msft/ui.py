import math, cairo, numpy as np
from PIL import Image, ImageFilter
W,H=1080,1920
def hx(h,a=1):
    if len(h)==8: a*=int(h[6:8],16)/255
    return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
RED,GRN,BLU,YEL='F25022','7FBA00','00A4EF','FFB900'
INK,INK2,PANEL,PANEL2,LINE='1B1F24','5F6872','FAFBFC','EEF1F4','D9DEE3'
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def font(c,fam,size,bold=False): c.select_font_face(fam,0,cairo.FONT_WEIGHT_BOLD if bold else 0); c.set_font_size(size)
def tw(c,s,fam,size,bold=False,track=0):
    font(c,fam,size,bold); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def txt(c,s,x,y,fam,size,color,bold=False,align='c',a=1,track=0):
    if a<=0.003: return 0
    w=tw(c,s,fam,size,bold,track); x0=x-w/2 if align=='c' else (x-w if align=='r' else x)
    asc,desc=c.font_extents()[:2]; yy=y+(asc-desc)/2*0.8; col(c,color,a)
    for ch in s: c.move_to(x0,yy); c.show_text(ch); x0+=c.text_extents(ch).x_advance+track
    return w
def rr(c,x,y,w,h,r):
    r=min(r,w/2,h/2); c.new_sub_path(); c.arc(x+w-r,y+r,r,-math.pi/2,0); c.arc(x+w-r,y+h-r,r,0,math.pi/2); c.arc(x+r,y+h-r,r,math.pi/2,math.pi); c.arc(x+r,y+r,r,math.pi,1.5*math.pi); c.close_path()
def to_pil(s): s.flush(); return Image.frombuffer('RGBA',(s.get_width(),s.get_height()),bytes(s.get_data()),'raw','BGRA',s.get_stride(),1)
def to_cairo(im): d=bytearray(im.tobytes('raw','BGRA')); return cairo.ImageSurface.create_for_data(d,cairo.FORMAT_ARGB32,im.width,im.height,im.width*4)
_SH={}
def shadow(c,x,y,w,h,r,a=1.0,blur=34,dy=18):
    key=(int(w),int(h),int(r),blur)
    if key not in _SH:
        m=blur*3; s=cairo.ImageSurface(cairo.FORMAT_ARGB32,int(w)+2*m,int(h)+2*m); k=cairo.Context(s)
        rr(k,m,m,w,h,r); k.set_source_rgba(0.02,0.05,0.12,0.42); k.fill()
        _SH[key]=(to_cairo(to_pil(s).filter(ImageFilter.GaussianBlur(blur))),m)
    g,m=_SH[key]; c.set_source_surface(g,x-m,y-m+dy); c.paint_with_alpha(a)
_BG={}
def wallpaper(tint=0.0):
    k=round(tint,2)
    if k in _BG: return _BG[k]
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s)
    g=cairo.LinearGradient(0,0,0,H); g.add_color_stop_rgb(0,*hx('0A1A3F')[:3]); g.add_color_stop_rgb(1,*hx('0E3A8C')[:3]); c.set_source(g); c.paint()
    for (x,y,r,h_,a) in ((180,520,700,'1E7BFF',.55),(950,1300,800,'00A4EF',.45),(600,1750,600,'6B5CFF',.35)):
        rg=cairo.RadialGradient(x,y,0,x,y,r); rg.add_color_stop_rgba(0,*hx(h_,a)); rg.add_color_stop_rgba(1,*hx(h_,0)); c.set_source(rg); c.paint()
    # ruban façon fond d'écran (sans logo)
    c.save(); c.translate(540,980)
    for i in range(7):
        c.new_path(); c.move_to(-900,200+i*26); c.curve_to(-300,-300+i*30,300,600-i*20,900,-100+i*24)
        col(c,'FFFFFF',.035+i*.006); c.set_line_width(40-i*4); c.stroke()
    c.restore()
    if tint>0: col(c,'3A0A0A',tint); c.paint()
    rng=np.random.default_rng(1); n=(rng.standard_normal((H,W))*3).astype(np.int16); s.flush(); a_=np.ndarray((H,W,4),np.uint8,s.get_data())
    for i in range(3): a_[:,:,i]=np.clip(a_[:,:,i].astype(np.int16)+n,0,255)
    s.mark_dirty(); _BG[k]=s; return s
def taskbar(c, t=0):
    col(c,'0B1426',.72); c.rectangle(0,1830,W,90); c.fill(); col(c,'FFFFFF',.08); c.rectangle(0,1830,W,1); c.fill()
    for i,h_ in enumerate((BLU,GRN,YEL,RED)):
        rr(c,420+i*64,1852,46,46,10); col(c,'FFFFFF',.10); c.fill(); c.new_path(); c.arc(443+i*64,1875,9,0,2*math.pi); col(c,h_); c.fill()
    txt(c,"16:53",990,1875,"Poppins",22,'FFFFFF',False,'c',.8)
def window(c,x,y,w,h,title,accent=BLU,body=None,a=1.0,danger=False):
    if a<=0.003: return
    c.push_group()
    shadow(c,x,y,w,h,18)
    rr(c,x,y,w,h,18); col(c,PANEL); c.fill()
    c.save(); rr(c,x,y,w,h,18); c.clip(); col(c,RED if danger else PANEL2); c.rectangle(x,y,w,64); c.fill(); c.restore()
    col(c,accent); c.rectangle(x+24,y+24,16,16); c.fill()
    txt(c,title,x+54,y+33,"Poppins Medium",22,'FFFFFF' if danger else INK,False,'l')
    fg='FFFFFF' if danger else INK2
    bx=x+w-140; col(c,fg); c.rectangle(bx,y+32,16,2); c.fill()
    c.rectangle(bx+46.5,y+24.5,15,15); c.set_line_width(2); c.stroke()
    c.new_path(); c.move_to(bx+94,y+25); c.line_to(bx+108,y+39); c.move_to(bx+108,y+25); c.line_to(bx+94,y+39); c.stroke()
    col(c,LINE); c.rectangle(x,y+64,w,1); c.fill()
    rr(c,x+.5,y+.5,w-1,h-1,18); col(c,'000000',.08); c.set_line_width(1); c.stroke()
    if body: c.save(); c.translate(x,y+64); body(c,w,h-64); c.restore()
    c.pop_group_to_source(); c.paint_with_alpha(a)
def cursor(c,x,y,s=1.0,click=0.0):
    c.save(); c.translate(x,y); c.scale(s,s)
    if click>0: c.new_path(); c.arc(0,0,30*click+6,0,2*math.pi); col(c,'FFFFFF',.5*(1-click)); c.set_line_width(3); c.stroke()
    c.new_path(); c.move_to(0,0); c.line_to(0,46); c.line_to(11,35); c.line_to(20,56); c.line_to(28,52); c.line_to(19,32); c.line_to(34,32); c.close_path()
    col(c,'FFFFFF'); c.fill_preserve(); col(c,'000000'); c.set_line_width(2.5); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke(); c.restore()
def progressbar(c,x,y,w,u,color=BLU,h=18):
    rr(c,x,y,w,h,h/2); col(c,'E1E6EB'); c.fill()
    if u>0: rr(c,x,y,max(h,w*u),h,h/2); col(c,color); c.fill()
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
                rr(c,x,yy-34,wd[i],66,14); col(c,kcol); c.fill(); txt(c,w,x+14,yy,"Poppins",size,'FFFFFF',True,'l')
            else: txt(c,w,x+2,yy+3,"Poppins",size,'000000',True,'l',.45); txt(c,w,x,yy,"Poppins",size,'FFFFFF',True,'l')
            x+=wd[i]+sp
def progress(c,u,color=BLU):
    col(c,'FFFFFF',.18); rr(c,140,260,800,8,4); c.fill(); rr(c,140,260,max(8,800*u),8,4); col(c,color); c.fill()
