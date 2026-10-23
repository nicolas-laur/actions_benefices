from ty import *
def k1(c):
    progress(c,.05)
    text(c,"AMAZON · VALEUR EN BOURSE",540,350,"JetBrains Mono",26,GR,True,'c',1,4)
    text(c,"2 800",540,500,"Archivo Black",210,WH)
    text(c,"MILLIARDS DE DOLLARS",540,640,"JetBrains Mono",34,OR,True,'c',1,6)
    label(c,700,820,["COLIS N° 2001","ÉTAT : ENDOMMAGÉ"],380,0.06,"−90 %")
    caption(c,[("Amazon",0),("a",0),("perdu",0),("plus",0),("de",0),("90 %",1),("en",0),("2001.",0)])
def k2(c):
    progress(c,.45)
    text(c,"AMAZON WEB SERVICES",540,350,"JetBrains Mono",26,'9FD4FF',True,'c',1,4)
    text(c,"AWS",540,500,"Archivo Black",230,WH)
    text(c,"42,2 MD$ EN 3 MOIS",540,650,"JetBrains Mono",36,'9FD4FF',True,'c',1,4)
    c.save(); c.translate(540,740); c.rectangle(-150,-36,300,72); col(c,OR); c.fill(); text(c,"+37 %",0,0,"Archivo Black",52,'111111',False,'c',1,0,False); c.restore()
    caption(c,[("Le",0),("cloud",0),("d'Amazon",0),(":",0),("sa",0),("vraie",0),("machine",1),("à",0),("cash.",0)])
def k3(c):
    progress(c,.85)
    text(c,"TES 1 000 € IL Y A 5 ANS",540,350,"JetBrains Mono",28,GR,True,'c',1,4)
    w1=tw(c,"≈ ","Poppins",90,True); w2=tw(c,"1 650 €","Archivo Black",140); x0=540-(w1+w2)/2; text(c,"≈",x0,480,"Poppins",90,WH,True,'l'); text(c,"1 650 €",x0+w1,480,"Archivo Black",140,WH,False,'l')
    label(c,330,700,["OCT. 2021","1 CARTON = 100 €"],330,-0.05,"1 000 €")
    label(c,760,640,["OCT. 2026","AUCUN DIVIDENDE"],340,0.05,"1 650 €")
    caption(c,[("Tes",0),("1 000 €",0),("?",0),("≈ 1 650 €.",1),("×1,65",0),("en",0),("5",0),("ans.",0)])
compose('b3d/kf_warehouse.png',k1,'amzn_da_k1_entrepot.png')
compose('b3d/kf_dc.png',k2,'amzn_da_k2_aws.png')
compose('b3d/kf_stacks.png',k3,'amzn_da_k3_cartons.png')
from PIL import Image
ims=[Image.open(f) for f in ('amzn_da_k1_entrepot.png','amzn_da_k2_aws.png','amzn_da_k3_cartons.png')]
sh=Image.new('RGB',(1680,1000),'white')
for i,im in enumerate(ims): sh.paste(im.resize((540,960)),(20+i*550,20))
sh.save('sheet.png')
