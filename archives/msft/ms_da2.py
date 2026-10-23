import math, cairo
from glass import *
def mini_chart(c,w,h,pts,color=BLU,lw=5,fill=True,glow=True):
    X_=lambda u:40+u*(w-80); vmin=min(v for _,v in pts); vmax=max(v for _,v in pts); Y_=lambda v:h-50-(v-vmin)/(vmax-vmin)*(h-120)
    if glow:
        for k_,a_ in ((22,.08),(12,.16)):
            c.new_path(); c.move_to(X_(pts[0][0]),Y_(pts[0][1])); [c.line_to(X_(u),Y_(v)) for u,v in pts[1:]]
            col(c,color,a_); c.set_line_width(lw+k_); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    X=lambda u:40+u*(w-80); vmin=min(v for _,v in pts); vmax=max(v for _,v in pts); Y=lambda v:h-50-(v-vmin)/(vmax-vmin)*(h-120)
    if fill:
        c.new_path(); c.move_to(X(pts[0][0]),h-40); [c.line_to(X(u),Y(v)) for u,v in pts]; c.line_to(X(pts[-1][0]),h-40); c.close_path()
        g=cairo.LinearGradient(0,60,0,h); g.add_color_stop_rgba(0,*hx(color,.35)); g.add_color_stop_rgba(1,*hx(color,0)); c.set_source(g); c.fill()
    c.new_path(); c.move_to(X(pts[0][0]),Y(pts[0][1])); [c.line_to(X(u),Y(v)) for u,v in pts[1:]]
    col(c,color); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    return X,Y
CURVE=[(0,283),(.08,336),(.22,214),(.4,330),(.55,420),(.66,470),(.72,537),(.8,505),(.86,400),(.9,349),(.92,405),(.96,500),(1,523)]
def k1():
    cv=aurora([(250,600,800,'00A4EF',.55),(900,1100,700,'7FBA00',.35),(600,1650,700,'5B3BFF',.35),(950,350,500,'00A4EF',.25)])
    # panneaux en arrière-plan, inclinés
    p1=glass_panel(520,340,lambda c,w,h:(txt(c,"MSFT",36,50,"JetBrains Mono",22,'BFE6FF',False,'l',1,3),mini_chart(c,w,h,[(0,349),(.3,360),(.55,420),(.7,470),(.85,505),(1,513)],GRN)))
    place(cv,p1,tilt_quad(290,560,520,340,ry=0.55,rx=-0.12),frost=18,dof=2.5)
    p2=glass_panel(460,250,lambda c,w,h:(txt(c,"30 JUILLET 2026",w/2,80,"JetBrains Mono",24,'FFFFFF',False,'c',1,3),txt(c,"+15,5 %",w/2,165,"Poppins",64,'BDF56A',True)))
    place(cv,p2,tilt_quad(800,500,460,250,ry=-0.55,rx=-0.1),frost=18,dof=2.0)
    glow_text(cv,"+450",540,820,300,top='FFFFFF',bottom='A8E2FF',glow='00A4EF',ga=.9)
    ov=cairo_layer(lambda c:(progress(c,.05),pill(c,"MILLIARDS DE DOLLARS · EN 1 JOUR",540,1100,'FFFFFF',22),
                              txt(c,"Le plus gros gain en une journée de l'histoire boursière",540,1165,"Poppins",24,'D6E4F5',False,'c',.9),
                              caption(c,[("450",0),("milliards",0),("gagnés",0),("en",0),("UNE",1),("journée.",0)])))
    cv.alpha_composite(ov); return cv
def k2():
    cv=aurora([(540,700,800,'F25022',.45),(150,1300,600,'8A0F2A',.45),(950,400,500,'FF7A3D',.2)],base=('050203','120407'))
    p=glass_panel(760,460,lambda c,w,h:(txt(c,"MSFT · 2026",40,50,"JetBrains Mono",22,'FFD2C8',False,'l',1,3),
                  mini_chart(c,w,h,[(0,537),(.15,520),(.3,470),(.45,430),(.6,400),(.75,372),(.88,360),(1,349)],RED,6)),tint='FFFFFF',ta=.07)
    place(cv,p,tilt_quad(540,620,760,460,ry=0.0,rx=0.5),frost=22,dof=3.5)
    glow_text(cv,"−35 %",540,900,250,top='FFFFFF',bottom='FF9A80',glow='F25022',ga=1.0)
    ov=cairo_layer(lambda c:(progress(c,.45,RED),pill(c,"DU RECORD D'OCT. 2025 AU PLUS BAS DE JUIN",540,1160,'FFFFFF',20),
                              caption(c,[("Juin",0),("2026",0),(":",0),("−35 %",1),("depuis",0),("le",0),("record.",0)],kcol=RED)))
    cv.alpha_composite(ov); return cv
def k3():
    cv=aurora([(300,500,700,'00A4EF',.45),(900,1200,700,'5B3BFF',.35),(540,1700,600,'00A4EF',.25)])
    def chartbody(c,w,h):
        txt(c,"MSFT · 5 ANS",44,54,"JetBrains Mono",24,'BFE6FF',False,'l',1,3)
        for v in (300,400,500):
            pass
        X,Y=mini_chart(c,w,h,CURVE,BLU,7)
        for u,v,cl in ((.9,349,RED),(.96,500,GRN),(1,523,'FFFFFF')):
            c.new_path(); c.arc(X(u),Y(v),11,0,2*math.pi); col(c,cl); c.fill()
    p=glass_panel(860,600,chartbody)
    place(cv,p,tilt_quad(560,700,860,600,ry=-0.45,rx=0.08),frost=24)
    # puces flottantes au premier plan
    for (x,y,s,cl,ry) in ((330,1080,"349 $ · JUIN",RED,0.45),(760,1080,"+15 % EN 1 JOUR",GRN,-0.45)):
        chip=glass_panel(330,96,lambda c,w,h,s=s,cl=cl:(c.new_path(),c.arc(36,h/2,9,0,2*math.pi),col(c,cl),c.fill(),txt(c,s,58,h/2,"JetBrains Mono",24,'FFFFFF',True,'l')),r=48,ta=.14)
        place(cv,chip,tilt_quad(x,y,330,96,ry=ry),frost=14,shadow=.4)
    ov=cairo_layer(lambda c:(progress(c,.6),caption(c,[("Des",0),("montagnes russes",1),("en",0),("2026.",0)])))
    cv.alpha_composite(ov); return cv
if __name__=="__main__":
    from PIL import Image
    ims=[]
    for n,f in (("k1_record",k1),("k2_chute",k2),("k3_courbe",k3)):
        im=f().convert('RGB'); im.save(n+"_v2.png"); ims.append(im)
    sh=Image.new('RGB',(1680,1000),'white')
    for i,im in enumerate(ims): sh.paste(im.resize((540,960)),(20+i*550,20))
    sh.save("sheet2.png")
