import math, cairo, os
from logos import hx, text, tw
TEAL,DEEP,INK,IV='14A38B','0B4B3F','17140F','F4EFE6'
OUT='pack'
def mark(c):  # aire + courbe + point, repère 200x200
    c.new_path(); c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54); c.line_to(164,160); c.line_to(40,160); c.close_path(); c.set_source_rgba(1,1,1,.13); c.fill()
    c.new_path(); c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54)
    c.set_source_rgb(1,1,1); c.set_line_width(6); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.new_path(); c.arc(164,54,9,0,2*math.pi); c.fill()
def grad(c,x0,y0,x1,y1):
    g=cairo.LinearGradient(x0,y0,x1,y1); g.add_color_stop_rgb(0,*hx(TEAL)[:3]); g.add_color_stop_rgb(1,*hx(DEEP)[:3]); c.set_source(g)
def sq(c,x,y,s,r):
    c.new_sub_path(); c.arc(x+s-r,y+r,r,-math.pi/2,0); c.arc(x+s-r,y+s-r,r,0,math.pi/2); c.arc(x+r,y+s-r,r,math.pi/2,math.pi); c.arc(x+r,y+r,r,math.pi,1.5*math.pi); c.close_path()
def rounded(c,s):  # symbole carré arrondi, fond transparent
    c.save(); c.scale(s/200,s/200); sq(c,4,4,192,58); grad(c,0,0,200,200); c.fill(); mark(c); c.restore()
def bleed(c,s):    # carré plein pour avatar (la plateforme découpe en rond)
    c.save(); c.scale(s/200,s/200); c.rectangle(0,0,200,200); grad(c,0,0,200,200); c.fill()
    c.translate(100,100); c.scale(1.0,1.0); c.translate(-102,-107); mark(c); c.restore()
def surf(kind,w,h,path=None):
    if kind=='png': return cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    return cairo.SVGSurface(path,w,h)
def make(name,w,h,fn):
    s=surf('png',w,h); c=cairo.Context(s); fn(c); s.write_to_png(f'{OUT}/{name}.png')
    sv=cairo.SVGSurface(f'{OUT}/{name}.svg',w,h); c=cairo.Context(sv); fn(c); sv.finish()
def wm(color):
    def f(c):
        rounded(c,176); x=176+30
        w=text(c,"Actions",x,118,"Poppins",104,color,True,False,-2.5); text(c,"Bénéfices",x+w+16,118,"Poppins",104,color,False,False,-2.5)
    return f
W=176+30+int(0)  # largeur calculée ci-dessous
k=cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32,4,4))
tot=206+tw(k,"Actions","Poppins",104,True,False,-2.5)+16+tw(k,"Bénéfices","Poppins",104,False,False,-2.5)+6
WW=int(tot)+10
make('symbole_arrondi_transparent_1024',1024,1024,lambda c:rounded(c,1024))
make('avatar_carre_1024',1024,1024,lambda c:bleed(c,1024))
make('wordmark_horizontal_fond_clair',WW,176,wm(INK))
make('wordmark_horizontal_fond_sombre',WW,176,wm(IV))
# aperçu rond + petites tailles, et PNG utilitaires
for s in (512,180,48):
    make(f'symbole_arrondi_{s}',s,s,lambda c,s=s:rounded(c,s)) if False else None
import PIL.Image as I
av=I.open(f'{OUT}/avatar_carre_1024.png').convert('RGBA'); sm=I.open(f'{OUT}/symbole_arrondi_transparent_1024.png')
for s in (512,180,48): sm.resize((s,s),I.LANCZOS).save(f'{OUT}/symbole_arrondi_{s}.png')
av.resize((400,400),I.LANCZOS).save(f'{OUT}/avatar_carre_400.png')
from PIL import ImageDraw
m=I.new('L',(1024,1024),0); ImageDraw.Draw(m).ellipse((0,0,1023,1023),fill=255); r=I.new('RGBA',(1024,1024),(0,0,0,0)); r.paste(av,(0,0),m); r.save(f'{OUT}/apercu_avatar_rond.png')
# planche de contrôle
sh=I.new('RGB',(1500,760),(244,239,230)); sh.paste(I.open(f'{OUT}/avatar_carre_1024.png').resize((300,300)).convert('RGB'),(30,30)); sh.paste(r.resize((300,300)),(350,30),r.resize((300,300)))
sh.paste(sm.resize((300,300)),(670,30),sm.resize((300,300)))
d=I.new('RGB',(1500,330),(23,20,15)); a=I.open(f'{OUT}/wordmark_horizontal_fond_sombre.png'); b=I.open(f'{OUT}/wordmark_horizontal_fond_clair.png')
sh.paste(b.resize((int(WW*0.6),int(176*0.6))),(30,380),b.resize((int(WW*0.6),int(176*0.6))))
sh.paste(d,(0,430)); sh.paste(a.resize((int(WW*0.6),int(176*0.6))),(30,520),a.resize((int(WW*0.6),int(176*0.6))))
sh.save('pack_check.png'); print(WW, os.listdir(OUT))
