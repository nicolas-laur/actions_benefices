import math, cairo
from ui import *
def k1(c):
    c.set_source_surface(wallpaper(),0,0); c.paint(); progress(c,.05); taskbar(c)
    def body(k,w,h):
        txt(k,"MICROSOFT · 30 JUILLET 2026",w/2,60,"JetBrains Mono",22,INK2,False,'c',1,3)
        txt(k,"+450",w/2,210,"Poppins",190,GRN,True)
        txt(k,"MILLIARDS DE DOLLARS",w/2,330,"Poppins Medium",34,INK,False,'c',1,4)
        rr(k,w/2-170,390,340,70,35); col(k,INK); k.fill(); txt(k,"EN 1 SEULE JOURNÉE",w/2,425,"Poppins",26,'FFFFFF',True)
    window(c,160,420,760,600,"Bourse.exe",GRN,body)
    def b2(k,w,h):
        txt(k,"Record absolu de l'histoire",30,48,"Poppins Medium",24,INK,False,'l'); progressbar(k,30,90,w-60,1.0,GRN)
    window(c,300,1060,560,180,"Notification",YEL,b2)
    cursor(c,820,960,1.3,.4)
    caption(c,[("450",0),("milliards",0),("gagnés",0),("en",0),("UNE",1),("journée.",0)])
def k2(c):
    c.set_source_surface(wallpaper(.25),0,0); c.paint(); progress(c,.5,RED); taskbar(c)
    def chart(k,w,h):
        P=[(0,537),(.1,520),(.2,480),(.35,420),(.45,400),(.55,380),(.62,365),(.7,349)]
        X=lambda u:40+u*(w-80); Y=lambda v:h-60-(v-320)/(560-320)*(h-120)
        k.new_path(); k.move_to(X(P[0][0]),Y(P[0][1])); [k.line_to(X(u),Y(v)) for u,v in P[1:]]; col(k,RED); k.set_line_width(6); k.stroke()
        txt(k,"537 $",X(0)+10,Y(537)-30,"JetBrains Mono",22,INK2,False,'l')
    window(c,160,400,760,560,"Microsoft.Bourse",BLU,chart,.55)
    def err(k,w,h):
        k.new_path(); k.arc(80,110,46,0,2*math.pi); col(k,RED); k.fill(); txt(k,"×",80,108,"Poppins",64,'FFFFFF',True)
        txt(k,"−35 %",150,95,"Poppins",110,INK,True,'l')
        txt(k,"Du record au plus bas de juin",152,190,"Poppins Medium",28,INK2,False,'l')
        for i,(lab,pri) in enumerate((("Annuler",False),("OK",True))):
            bx=w-330+i*165; rr(k,bx,h-90,145,58,10); col(k,BLU if pri else PANEL2); k.fill(); txt(k,lab,bx+72,h-61,"Poppins Medium",24,'FFFFFF' if pri else INK)
    window(c,180,700,720,430,"Erreur · MSFT",RED,err,1,True)
    caption(c,[("Juin",0),("2026",0),(":",0),("−35 %",1),("depuis",0),("le",0),("record.",0)],kcol=RED)
def k3(c):
    c.set_source_surface(wallpaper(),0,0); c.paint(); progress(c,.62); taskbar(c)
    def chart(k,w,h):
        P=[(0,283),(.12,330),(.25,240),(.4,330),(.55,420),(.66,470),(.72,537),(.8,510),(.86,400),(.9,349),(.93,405),(.96,500),(1,523)]
        X=lambda u:40+u*(w-100); Y=lambda v:h-70-(v-200)/(580-200)*(h-140)
        for v in (300,400,500): col(k,LINE); k.rectangle(40,Y(v),w-100,1); k.fill(); txt(k,f"{v}",w-50,Y(v),"JetBrains Mono",18,INK2,False,'l')
        k.new_path(); k.move_to(X(0),Y(283)); [k.line_to(X(u),Y(v)) for u,v in P]; col(k,BLU); k.set_line_width(6); k.set_line_join(cairo.LINE_JOIN_ROUND); k.stroke()
        for u,v,lab,cl,dy in ((.9,349,"349 $",RED,40),(.96,500,"+15 % EN 1 JOUR",GRN,90)):
            k.new_path(); k.arc(X(u),Y(v),9,0,2*math.pi); col(k,cl); k.fill(); txt(k,lab,X(u)-14,Y(v)+dy,"JetBrains Mono",22,cl,True,'r')
        for j,yr in enumerate(("2022","2023","2024","2025","2026")): txt(k,yr,X(.1+j*.2),h-30,"JetBrains Mono",18,INK2)
    window(c,160,380,760,700,"MSFT · 5 ans",BLU,chart)
    def dl(k,w,h):
        txt(k,"1 000 € investis… calcul en cours",30,40,"Poppins Medium",24,INK,False,'l'); progressbar(k,30,80,w-60,.68,BLU)
    window(c,190,1110,700,160,"Tes 1 000 €",YEL,dl)
    cursor(c,700,860,1.3)
    caption(c,[("Des",0),("montagnes russes",1),("en",0),("2026.",0)])
if __name__=="__main__":
    from PIL import Image
    for n,f in (("k1_record",k1),("k2_chute",k2),("k3_courbe",k3)):
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); f(c); s.write_to_png(n+".png")
    sh=Image.new('RGB',(1680,1000),'white')
    for i,n in enumerate(("k1_record","k2_chute","k3_courbe")): sh.paste(Image.open(n+".png").convert('RGB').resize((540,960)),(20+i*550,20))
    sh.save("sheet.png")
