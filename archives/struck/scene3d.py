import math, cairo, random
import struck as S
from struck import hx, col, lin, rad, coin_face
def ell(c,cx,cy,R,sx,sy,rot):
    c.save(); c.translate(cx,cy); c.rotate(rot); c.scale(sx,sy); c.new_path(); c.arc(0,0,R,0,2*math.pi); c.restore()
def coin3d(c,cx,cy,R,sx,sy,rot,dx,dy,text=True,steps=26):
    # tranche : ellipses empilées de l'arrière vers l'avant
    for k in range(steps,0,-1):
        t=k/steps; x,y=cx+dx*t,cy+dy*t
        ell(c,x,y,R,sx,sy,rot)
        c.set_source(lin(x-R*sx*1.05,y,x+R*sx*1.05,y,[(0,'8C3F00'),(.22,'E08A0C'),(.45,'FFC93A'),(.62,'F5A515'),(1,'7A3500')])); c.fill()
        if k%2==0: ell(c,x,y,R,sx,sy,rot); col(c,'5A2A00',.10); c.fill()
    ell(c,cx+dx,cy+dy,R,sx,sy,rot); col(c,'5A2A00',.35); c.set_line_width(2); c.stroke()
    # face frappée
    c.save(); c.translate(cx,cy); c.rotate(rot); c.scale(sx,sy); coin_face(c,0,0,R,text); c.restore()
    ell(c,cx,cy,R,sx,sy,rot); col(c,'7A3A00',.6); c.set_line_width(2.5); c.stroke()
def orb(c,x,y,r,warm=True):
    c.new_path(); c.arc(x,y,r,0,2*math.pi)
    stops=[(0,'FFF6C8FF'),(.35,'FFC83AF0'),(.8,'F59A0ACC'),(1,'F59A0A00')] if warm else [(0,'FFFFFFDD'),(.6,'FFF1D6AA'),(1,'FFF1D600')]
    c.set_source(rad(x,y,0,r,stops,x-r*.3,y-r*.3)); c.fill()
def scene(c,W,bg):
    if bg: c.set_source(rad(W/2,W*.5,0,W*.75,[(0,'FFF6DE'),(1,'F1DFB4')])); c.paint()
    k=W/1400
    c.save(); c.scale(k,k)
    for x,y,r,w in ((210,330,46,False),(830,180,40,True),(150,560,14,True),(905,520,30,False),(260,690,22,False),(1160,300,18,True),(1230,620,12,True)): orb(c,x,y,r,w)
    # ombre au sol
    c.save(); c.translate(760,1150); c.scale(560,70); c.new_path(); c.arc(0,0,1,0,2*math.pi); c.set_source(rad(0,0,0,1,[(0,'5A2A0060'),(1,'5A2A0000')])); c.fill(); c.restore()
    random.seed(4)
    jit=[(0,0),(-26,.05),(18,-.04),(-14,.06),(30,-.03),(-20,.04),(8,-.02)]
    for i,(jx,jr) in enumerate(jit):
        coin3d(c,770+jx,1010-i*78,235,1,.42,jr,0,62,text=(i==len(jit)-1))
    coin3d(c,1110,1030,170,1,.45,.08,0,44)
    coin3d(c,915,1120,180,1,.47,-.06,0,46)
    coin3d(c,420,905,265,.84,1,-.12,44,-6)
    c.restore()
for name,bg in (("pile_frappee_transparent",False),("pile_frappee_fond_creme",True)):
    s=cairo.ImageSurface(cairo.FORMAT_ARGB32,1400,1400); cx=cairo.Context(s); scene(cx,1400,bg); s.write_to_png(name+".png")
