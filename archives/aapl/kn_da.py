import cairo
from kn import *
def k1(c):
    slide(c); progress(c,.04)
    eyebrow(c,"Apple · capitalisation",470)
    gtext(c,"5 000",540,700,'black',250,SUNSET,track=-8)
    text(c,"milliards de dollars.",540,900,'xb',84,'F5F5F7',track=-2)
    text(c,"Record historique · 25 septembre 2026",540,1010,'m',30,'86868B')
    caption(c,[("Apple",0),("vaut",0),("près",0),("de",0),("5 000 milliards.",1)],kstops=SUNSET)
def k2(c):
    slide(c,False); progress(c,.35,False)
    eyebrow(c,"Nouveau PDG · 1er septembre 2026",520,'6E6E73')
    text(c,"John",540,700,'black',190,'1D1D1F',track=-6)
    text(c,"Ternus.",540,880,'black',190,'1D1D1F',track=-6)
    text(c,"Tim Cook devient président exécutif.",540,1060,'m',36,'6E6E73')
    caption(c,[("Après",0),("15",0),("ans,",0),("Tim",0),("Cook",0),("passe",0),("la",0),("main.",1)],dark=False,kstops=[(0,'1D1D1F'),(1,'6E6E73')])
def k3(c):
    slide(c); progress(c,.5)
    eyebrow(c,"Chiffre d'affaires · avril-juin 2026",400)
    gtext(c,"109,4 Md$",540,540,'black',125,OCEAN,track=-4)
    bars(c,[("iPhone",54.3,"54,3 Md$"),("Services",30.7,"30,7 Md$"),("Mac",10.4,"10,4 Md$"),("Wearables",7.9,"7,9 Md$"),("iPad",6.2,"6,2 Md$")],180,700,480,bh=50,gap=70)
    caption(c,[("L'iPhone",0),("pèse",0),("la",0),("moitié",1),("des",0),("ventes.",0)],kstops=OCEAN)
def k4(c):
    slide(c); progress(c,.75)
    def scr(k,w,h):
        g=cairo.LinearGradient(0,0,w,h); g.add_color_stop_rgb(0,*hx('1C0A0E')[:3]); g.add_color_stop_rgb(1,*hx('3A0B18')[:3]); k.set_source(g); k.paint()
        text(k,"Siri",w/2,h*.45,'black',110,'FFFFFF'); text(k,"bientôt…",w/2,h*.45+100,'m',36,'FF9F9F')
    hero_phone(c,540,640,330,680,REDG,scr)
    gtext(c,"1 an de retard.",540,1100,'black',96,REDG,track=-2)
    caption(c,[("Le",0),("Siri",0),("dopé",0),("à",0),("l'IA",0),("se",0),("fait",0),("attendre.",1)],kstops=REDG)
if __name__=="__main__":
    from PIL import Image
    ims=[]
    for n,f in (("kn1_record",k1),("kn2_ternus",k2),("kn3_ventes",k3),("kn4_siri",k4)):
        s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s); f(c); s.write_to_png(n+".png"); ims.append(Image.open(n+".png").convert('RGB'))
    sh=Image.new('RGB',(4*430+50,800),'white')
    for i,im in enumerate(ims): sh.paste(im.resize((420,746)),(10+i*430,25))
    sh.save("sheet_kn.png")
