import math, cairo
IV,INK,GOLD,GREEN,TEAL,DEEP='F4EFE6','17140F','A8834C','0F5C4D','14A38B','0B4B3F'
def hx(h,a=1): return (int(h[0:2],16)/255,int(h[2:4],16)/255,int(h[4:6],16)/255,a)
def col(c,h,a=1): c.set_source_rgba(*hx(h,a))
def font(c,fam,size,bold=False,italic=False):
    c.select_font_face(fam,cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
def tw(c,s,fam,size,bold=False,italic=False,track=0):
    font(c,fam,size,bold,italic); return sum(c.text_extents(ch).x_advance+track for ch in s)-track
def text(c,s,x,y,fam,size,color,bold=False,italic=False,track=0,align='l'):
    w=tw(c,s,fam,size,bold,italic,track); x0=x-w/2 if align=='c' else x
    col(c,color); font(c,fam,size,bold,italic)
    for ch in s: c.move_to(x0,y); c.show_text(ch); x0+=c.text_extents(ch).x_advance+track
    return w
def dot(c,x,y,r,color): c.new_path(); c.arc(x,y,r,0,2*math.pi); col(c,color); c.fill()
def line(c,pts,w,color,cap=cairo.LINE_CAP_ROUND,curve=False):
    c.new_path(); c.move_to(*pts[0])
    if curve:
        for i in range(1,len(pts),3): c.curve_to(*pts[i],*pts[i+1],*pts[i+2])
    else:
        for p in pts[1:]: c.line_to(*p)
    col(c,color); c.set_line_width(w); c.set_line_cap(cap); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
def squircle(c,x,y,s,r): 
    c.new_sub_path(); c.arc(x+s-r,y+r,r,-math.pi/2,0); c.arc(x+s-r,y+s-r,r,0,math.pi/2); c.arc(x+r,y+s-r,r,math.pi/2,math.pi); c.arc(x+r,y+r,r,math.pi,1.5*math.pi); c.close_path()

# symboles dessinés dans un repère 200x200
def symA(c,bg):
    c.new_path(); c.arc(100,100,94,0,2*math.pi); col(c,GREEN); c.set_line_width(6); c.stroke()
    line(c,[(46,138),(72,134),(84,108),(106,110),(128,112),(138,84),(158,58)],7,GREEN,curve=False) if False else None
    line(c,[(44,136),(70,134),(84,108),(104,108),(126,108),(136,86),(158,60)],7,GREEN,curve=True)
    dot(c,158,60,9,GOLD)
def symB(c,bg):
    squircle(c,4,4,192,52); col(c,GREEN); c.fill()
    text(c,"AB",100,104,"Bodoni Moda",84,IV,True,False,-2,'c')
    line(c,[(52,160),(92,148),(116,155),(148,128)],4,GOLD); dot(c,148,128,7,GOLD)
def symC(c,bg):
    c.new_path(); c.arc(100,100,98,0,2*math.pi); col(c,INK); c.fill()
    c.new_path(); c.arc(100,100,88,0,2*math.pi); col(c,IV,.8); c.set_line_width(2.5); c.stroke()
    line(c,[(42,142),(88,110),(110,124),(160,58)],6,IV,cairo.LINE_CAP_BUTT); dot(c,160,58,8,GOLD)
def symD(c,bg):
    squircle(c,4,4,192,58)
    g=cairo.LinearGradient(0,0,200,200); g.add_color_stop_rgb(0,*hx(TEAL)[:3]); g.add_color_stop_rgb(1,*hx(DEEP)[:3]); c.set_source(g); c.fill()
    c.new_path(); c.move_to(40,146); c.curve_to(80,142,100,124,120,98); c.curve_to(138,76,150,66,164,54); c.line_to(164,160); c.line_to(40,160); c.close_path(); col(c,'FFFFFF',.13); c.fill()
    line(c,[(40,146),(80,142),(100,124),(120,98),(138,76),(150,66),(164,54)],6,'FFFFFF',curve=True); dot(c,164,54,9,'FFFFFF')
def symE(c,bg):
    c.new_path(); c.arc(100,100,88,math.radians(-52),math.radians(262)); col(c,GREEN); c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    line(c,[(58,132),(92,116),(112,124),(176,36)],7,GREEN); dot(c,176,36,11,GOLD)
def symF(c,bg):
    c.new_path(); c.arc(100,100,98,0,2*math.pi); col(c,IV); c.fill()
    c.new_path(); c.arc(100,100,98,0,2*math.pi); col(c,GOLD,.6); c.set_line_width(2); c.stroke()
    text(c,"A",96,124,"Bodoni Moda",108,GREEN,False,True,0,'c')
    line(c,[(62,156),(100,146),(122,152),(152,124)],4,GOLD); dot(c,152,124,6,GOLD)

def wmA(c,x,y,fg):  # sobre : Poppins medium espacé + filet or
    w=text(c,"Actions",x,y,"Poppins Medium",54,fg,False,False,2); 
    c.new_path(); c.move_to(x+w+14,y-14); c.line_to(x+w+50,y-26); col(c,GOLD); c.set_line_width(4); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    text(c,"Bénéfices",x+w+64,y,"Poppins Medium",54,fg,False,False,2)
def wmB(c,x,y,fg):  # paire sérif / sans
    w=text(c,"Actions",x,y,"Bodoni Moda",64,fg,False,True,0)
    text(c,"BÉNÉFICES",x+3,y+44,"Poppins",23,GOLD,False,False,8)
def wmC(c,x,y,fg):  # petites capitales
    text(c,"ACTIONS",x,y-6,"Poppins Medium",42,fg,False,False,12); 
    c.new_path(); c.move_to(x,y+18); c.line_to(x+300,y+18); col(c,GOLD); c.set_line_width(1.5); c.stroke()
    text(c,"BÉNÉFICES",x,y+60,"Poppins Medium",42,fg,False,False,12)
def wmD(c,x,y,fg):  # gras moderne
    w=text(c,"Actions",x,y,"Poppins",58,fg,True,False,-1.5)
    text(c,"Bénéfices",x+w+10,y,"Poppins",58,fg,False,False,-1.5)
def wmE(c,x,y,fg):
    w=text(c,"Actions",x,y,"Poppins",52,fg,True,False,-1); 
    c.new_path(); c.move_to(x+w+8,y-2); c.line_to(x+w+34,y-30); col(c,GOLD); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    text(c,"Bénéfices",x+w+44,y,"Poppins",52,fg,False,False,-1)
def wmF(c,x,y,fg):
    w=text(c,"Actions",x,y,"Bodoni Moda",70,fg,False,True,-1)
    c.new_path(); c.move_to(x+w+10,y-4); c.line_to(x+w+46,y-40); col(c,GOLD); c.set_line_width(4); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    text(c,"Bénéfices",x+w+58,y,"Poppins Medium",44,fg,False,False,0)

VARS=[("A · Évolution douce","anneau fin, trait affiné, vert profond",symA,wmA,IV,INK),
      ("B · Monogramme AB","carré arrondi, sérif Bodoni, trait or",symB,wmB,IV,INK),
      ("C · Nuit","fond encre, filet ivoire, trait tendu",symC,wmC,INK,IV),
      ("D · Moderne","dégradé teal vers vert sombre, aire translucide",symD,wmD,IV,INK),
      ("E · Anneau ouvert","la courbe sort du cercle, point or",symE,wmE,IV,INK),
      ("F · Éditorial","avatar sérif italique, wordmark Bodoni + Poppins",symF,wmF,IV,INK)]
def sym_at(c,fn,bg,x,y,s):
    c.save(); c.translate(x,y); c.scale(s/200,s/200); fn(c,bg); c.restore()
TW,TH=1000,520
def tile(c,i,v):
    name,desc,sym,wm,bg,fg=v
    c.save(); col(c,bg); c.rectangle(0,0,TW,TH); c.fill()
    c.rectangle(0.5,0.5,TW-1,TH-1); col(c,GOLD,.5); c.set_line_width(1); c.stroke()
    text(c,name.upper(),36,48,"Poppins Medium",18,GOLD,False,False,3)
    text(c,desc,36,76,"Poppins",16,fg if bg==INK else '6E665A')
    sym_at(c,sym,bg,40,120,230)
    wm(c,310,230 if wm not in (wmC,wmB) else 200,fg)
    # versions réduites et avatar rond
    y=400
    sym_at(c,sym,bg,310,y-20,92)
    sym_at(c,sym,bg,430,y-4,56)
    sym_at(c,sym,bg,520,y+8,32)
    c.new_path(); c.arc(760,y+26,52,0,2*math.pi); c.save(); c.clip(); col(c,bg=='F4EFE6' and 'E6DDCC' or '2A2620'); c.paint(); sym_at(c,sym,bg,712,y-22,96); c.restore()
    c.new_path(); c.arc(760,y+26,52,0,2*math.pi); col(c,GOLD,.6); c.set_line_width(1); c.stroke()
    text(c,"avatar",760,y+100,"Poppins",13,'6E665A' if bg!=INK else IV,False,False,2,'c')
    c.restore()
def main():
    cols,rows=2,3; s=cairo.ImageSurface(cairo.FORMAT_ARGB32,TW*cols+30*(cols+1),TH*rows+30*(rows+1)); c=cairo.Context(s)
    col(c,'D9D2C3'); c.paint()
    for i,v in enumerate(VARS):
        c.save(); c.translate(30+(i%cols)*(TW+30),30+(i//cols)*(TH+30)); tile(c,i,v); c.restore()
    s.write_to_png('logos_sheet.png')
    for i,v in enumerate(VARS):
        t=cairo.ImageSurface(cairo.FORMAT_ARGB32,TW,TH); cc=cairo.Context(t); tile(cc,i,v); t.write_to_png(f'logo_{v[0][0]}.png')
main()
