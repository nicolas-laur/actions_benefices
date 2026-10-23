import sys, math, subprocess, cairo, numpy as np
from PIL import Image, ImageFilter
from kn import *
FPS=60; SEG=[("retro","1984.",SUNSET,"Le Macintosh",[("1984",0),(":",0),("le",0),("Macintosh",0),("popularise",0),("la",0),("souris.",1)]),
             ("player","2001.",OCEAN,"Un baladeur",[("2001",0),(":",0),("l'iPod",0),("met",0),("1 000 chansons",1),("dans",0),("la",0),("poche.",0)]),
             ("phone","2007.",SUNSET,"Un téléphone",[("2007",0),(":",0),("l'iPhone.",0),("Tout",0),("change.",1)])]
D=2.8; DUR=D*3+0.3
_cache={}
def obj(name,i):
    k=(name,i)
    if k not in _cache:
        im=Image.open(f'b3d/seq_{name}/{i:04d}.png').convert('RGBA'); _cache[k]=im
        if len(_cache)>40: _cache.pop(next(iter(_cache)))
    return _cache[k]
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def frame(t):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); slide(c); progress(c,t/DUR)
    si=min(2,int(t//D)); lt=t-si*D; name,year,stops,_,cap=SEG[si]
    a_in=ease(lt/0.45); a_out=1-ease((lt-(D-0.35))/0.35) if lt>D-0.35 else 1; a=a_in*a_out
    # titre année
    c.save(); c.translate(0,24*(1-a_in)); c.push_group(); gtext(c,year,540,430,'black',190,stops,track=-6)
    # balayage de lumière sur le titre
    u=(lt-0.3)/1.0
    if 0<u<1:
        c.set_operator(cairo.OPERATOR_ATOP); g=cairo.LinearGradient(200+700*u-120,300,200+700*u+120,560)
        g.add_color_stop_rgba(0,1,1,1,0); g.add_color_stop_rgba(.5,1,1,1,.55); g.add_color_stop_rgba(1,1,1,1,0); c.set_source(g); c.paint()
    c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    # sous-titres mot à mot
    c.push_group(); caption(c,cap,kstops=stops); c.pop_group_to_source(); c.paint_with_alpha(min(a_out,ease((lt-0.2)/0.4)))
    s.flush(); base=Image.frombuffer('RGBA',(W,H),bytes(s.get_data()),'raw','BGRA',s.get_stride(),1).copy()
    # objet 3D + reflet au sol
    idx=min(71,int(lt/D*72)); im=obj(name,idx); sc=1.25*(0.94+0.06*ease(lt/0.8)); size=int(720*sc)
    o=im.resize((size,size),Image.BICUBIC)
    if a<1: o.putalpha(o.split()[3].point(lambda v:int(v*a)))
    x=540-size//2; y=890-size//2
    bb=o.getbbox()
    if bb:
        hh=int((bb[3]-bb[1])*0.3); refl=o.crop((0,bb[3]-hh,size,bb[3])).transpose(Image.FLIP_TOP_BOTTOM)
        grad=np.linspace(0.18,0,refl.size[1])[:,None]; al=(np.asarray(refl.split()[3]).astype(float)*grad).astype(np.uint8)
        refl.putalpha(Image.fromarray(al)); refl=refl.filter(ImageFilter.GaussianBlur(4)); base.alpha_composite(refl,(x,y+bb[3]+8))
    base.alpha_composite(o,(x,y))
    if t>DUR-0.3: base=Image.blend(base,Image.new('RGBA',(W,H),(0,0,0,255)),min(1,(t-(DUR-0.3))/0.3))
    return base
if __name__=="__main__":
    if sys.argv[1]=='png':
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'smp_{ts}.png')
    else:
        ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','sample_video.mp4'],stdin=subprocess.PIPE)
        for i in range(int(DUR*FPS)): ff.stdin.write(frame(i/FPS).tobytes())
        ff.stdin.close(); ff.wait(); print('done')
