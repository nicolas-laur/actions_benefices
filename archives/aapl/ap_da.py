import sys, math, cairo, numpy as np
sys.path.insert(0,'/home/claude/msft')
_a=sys.argv; sys.argv=['x','info']
import ms
sys.argv=_a
from ms import place, glass, glow_text, chip, mini_chart, lowblur
from ui import hx, col, tw, txt, rr, to_pil, W, H
from glass import tilt_quad, surf, pil, pill, RED, GRN, BLU, YEL
from PIL import Image, ImageFilter
TI=('F5F5F7','8E9196')
def stage(tint=None, a=0.0):
    s,c=surf(W,H); col(c,'000000'); c.paint()
    g=cairo.RadialGradient(540,-200,0,540,-200,1500); g.add_color_stop_rgba(0,*hx('5A6070',.55)); g.add_color_stop_rgba(.5,*hx('1A1C22',.35)); g.add_color_stop_rgba(1,*hx('000000',0)); c.set_source(g); c.paint()
    f=cairo.RadialGradient(540,1500,0,540,1500,700); f.add_color_stop_rgba(0,*hx('2A3550',.45)); f.add_color_stop_rgba(1,*hx('000000',0)); c.set_source(f); c.paint()
    if tint:
        t=cairo.RadialGradient(540,800,0,540,800,900); t.add_color_stop_rgba(0,*hx(tint,a)); t.add_color_stop_rgba(1,*hx(tint,0)); c.set_source(t); c.paint()
    im=pil(s).convert('RGB'); arr=np.asarray(im).astype(np.int16)+(np.random.default_rng(4).standard_normal((H,W,1))*2.5).astype(np.int16)
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8)).convert('RGBA')
def phone(w=420,h=860,screen=None):
    s,c=surf(w,h)
    rr(c,0,0,w,h,70); g=cairo.LinearGradient(0,0,w,h)
    for o,v in ((0,'D8DADF'),(.25,'7C8088'),(.5,'C9CBD0'),(.75,'6B6F77'),(1,'B9BCC2')): g.add_color_stop_rgb(o,*hx(v)[:3])
    c.set_source(g); c.fill()
    rr(c,12,12,w-24,h-24,60); col(c,'050506'); c.fill()
    if screen: c.save(); rr(c,22,22,w-44,h-44,52); c.clip(); c.translate(22,22); screen(c,w-44,h-44); c.restore()
    rr(c,w/2-60,40,120,34,17); col(c,'000000'); c.fill()
    c.save(); rr(c,12,12,w-24,h-24,60); c.clip(); g2=cairo.LinearGradient(0,0,w,h*.6)
    for o,v in ((0,0),(.35,0),(.42,.14),(.5,0)): g2.add_color_stop_rgba(o,1,1,1,v)
    c.set_source(g2); c.paint(); c.restore()
    return pil(s)
def screen_chart(color=GRN, pts=None, label="AAPL", sub="336,64 $"):
    pts=pts or [(0,143),(.15,175),(.25,130),(.4,190),(.55,230),(.7,250),(.8,200),(.88,255),(.95,330),(1,337)]
    def f(c,w,h):
        g=cairo.LinearGradient(0,0,0,h); g.add_color_stop_rgb(0,*hx('0B0D12')[:3]); g.add_color_stop_rgb(1,*hx('11151E')[:3]); c.set_source(g); c.paint()
        txt(c,label,40,140,"Poppins",36,'FFFFFF',True,'l'); txt(c,sub,40,195,"Poppins",48,'FFFFFF',True,'l')
        c.save(); c.translate(0,260); mini_chart(c,w,h-420,pts,color,5); c.restore()
    return f
def k1():
    cv=stage()
    place(cv,phone(400,820,screen_chart()),tilt_quad(790,800,400,820,ry=-0.55,rx=0.06),1.0,0,.7,1.5)
    place(cv,glass(380,150,lambda c,w,h:(txt(c,"1976 · 2026",w/2,58,"JetBrains Mono",24,'FFFFFF',False,'c',1,3),txt(c,"50 ANS",w/2,108,"Poppins",40,'FFFFFF',True))),
          tilt_quad(290,470,380,150,ry=0.5),1.0,20,.5)
    glow_text(cv,"5 000",500,880,250,top=TI[0],bottom=TI[1],glow='9FB4D8',ga=.35)
    ov,c=surf(W,H); ms_prog(c,.05); pill(c,"MILLIARDS DE DOLLARS · RECORD",540,1110,'FFFFFF',22)
    ms.draw_caption.__globals__  # noqa
    cap(c,[("Apple",0),("vaut",0),("près",0),("de",0),("5 000 milliards",1),("…",0)])
    cv.alpha_composite(to_pil(ov)); return cv
def k2():
    cv=stage('3B4A6B',.35)
    glow_text(cv,"Passage de relais",540,420,92,top=TI[0],bottom=TI[1],glow='9FB4D8',ga=.3,reflect=False,track=-2)
    def card(name,role,yrs,accent):
        return lambda c,w,h:(txt(c,yrs,44,62,"JetBrains Mono",24,'BFC6D4',False,'l',1,3),txt(c,name,44,150,"Poppins",58,'FFFFFF',True,'l'),txt(c,role,44,215,"Poppins",28,'C9CED8',False,'l'),
                             c.new_path(),c.arc(w-60,62,10,0,2*math.pi),col(c,accent),c.fill())
    place(cv,glass(560,280,card("Tim Cook","Président exécutif","PDG 2011 · 2026",'8E9196')),tilt_quad(470,700,560,280,ry=0.45,rx=-0.05),.85,22,.5,1.5)
    place(cv,glass(600,290,card("John Ternus","Nouveau PDG","DEPUIS LE 1ER SEPT. 2026",GRN)),tilt_quad(600,1010,600,290,ry=-0.35,rx=0.04),1.0,22,.55)
    ov,c=surf(W,H); ms_prog(c,.35)
    cap(c,[("1er",0),("septembre",0),(":",0),("John Ternus",1),("succède",0),("à",0),("Tim",0),("Cook.",0)])
    cv.alpha_composite(to_pil(ov)); return cv
def k3():
    cv=stage('F25022',.28)
    place(cv,phone(400,820,screen_chart(RED,[(0,341),(.2,338),(.4,336),(.6,330),(.8,334),(1,333)],"iPhone 18 Pro","Commandes")),tilt_quad(540,760,400,820,ry=0.25,rx=0.12),1.0,0,.7)
    for (x,y,s,cl,ry) in ((360,1050,"COMMANDES −15 %",RED,0.45),(620,1160,"SIRI IA : 1 AN DE RETARD",YEL,-0.35),(320,430,"PER : 36",RED,0.45)):
        k=chip(s,cl); place(cv,k,tilt_quad(x,y,k.width*.9,96*.9,ry=ry),1,14,.4)
    ov,c=surf(W,H); ms_prog(c,.7)
    cap(c,[("Mais",0),("l'iPhone",0),("18",0),("Pro",0),("se",0),("vendrait",0),("moins",1),("bien.",0)],kcol=RED)
    cv.alpha_composite(to_pil(ov)); return cv
def ms_prog(c,u,colr='FFFFFF'):
    col(c,'FFFFFF',.15); rr(c,140,260,800,6,3); c.fill(); rr(c,140,260,max(6,800*u),6,3); col(c,colr,.9); c.fill()
def cap(c,words,kcol='FFFFFF'):
    from glass import caption
    if kcol=='FFFFFF':
        # mot clé : pastille titane, texte noir
        size=48; sp=tw(c,' ',"Poppins",size,True); wd=[tw(c,w,"Poppins",size,True)+(28 if k else 0) for w,k in words]
        lines,cur,cw=[],[],0
        for i,w in enumerate(wd):
            need=w+(sp if cur else 0)
            if cur and cw+need>760: lines.append((cur,cw)); cur,cw=[],0; need=w
            cur.append(i); cw+=need
        lines.append((cur,cw)); y0=1352-(len(lines)-1)*37
        for li,(idx,lw) in enumerate(lines):
            x=540-lw/2; yy=y0+li*74
            for i in idx:
                w,k=words[i]
                if k:
                    rr(c,x,yy-34,wd[i],66,33); g=cairo.LinearGradient(x,yy-34,x+wd[i],yy+32)
                    for o,v in ((0,'F5F5F7'),(.5,'BFC2C8'),(1,'E6E7EA')): g.add_color_stop_rgb(o,*hx(v)[:3])
                    c.set_source(g); c.fill(); txt(c,w,x+14,yy,"Poppins",size,'0A0A0C',True,'l')
                else: txt(c,w,x+2,yy+3,"Poppins",size,'000000',True,'l',.5); txt(c,w,x,yy,"Poppins",size,'FFFFFF',True,'l')
                x+=wd[i]+sp
    else: caption(c,words,kcol=kcol)
if __name__=="__main__":
    ims=[]
    for n,f in (("k1_record",k1),("k2_relais",k2),("k3_doute",k3)):
        im=f().convert('RGB'); im.save(n+".png"); ims.append(im)
    sh=Image.new('RGB',(1680,1000),'white')
    for i,im in enumerate(ims): sh.paste(im.resize((540,960)),(20+i*550,20))
    sh.save("sheet.png")
