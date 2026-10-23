from vty import *
NB = ' '
def k1(c):
    progress(c, .06); kicker(c, "CHAQUE FOIS QUE TU PAIES"); rule(c)
    gtext(c, "VISA", 540, 520, 'k', 200, track=4)
    text(c, "ENCAISSE", 540, 660, 'k', 110, WH, track=2)
    caption(c, [("Visa", 0), ("ne", 0), ("te", 0), ("prête", 0), ("pas", 0), ("un", 0), ("centime.", 0), ("Mais", 0), ("il", 0), ("touche", 0), ("sur", 0), ("chaque" + NB + "paiement.", 1)])
def k2(c):
    progress(c, .4); kicker(c, "AVRIL-JUIN 2026"); rule(c)
    text(c, "72", 540, 540, 'k', 260, WH)
    gtext(c, "MILLIARDS", 540, 700, 'k', 104, track=2)
    text(c, "DE TRANSACTIONS EN 3 MOIS", 540, 790, 'sb', 32, GR, 'c', 1, 4, False)
    pill(c, "≈ 9" + NB + "200 PAR SECONDE", 540, 1130, 40)
    caption(c, [("Et", 0), ("le", 0), ("compteur", 0), ("ne", 0), ("s'arrête", 0), ("jamais" + NB + ":", 0), ("72" + NB + "milliards", 1), ("de", 0), ("paiements.", 0)])
def k3(c):
    progress(c, .88); kicker(c, "TES 1 000 € IL Y A 5 ANS"); rule(c)
    w1 = tw(c, "≈ ", 'xb', 100); w2 = tw(c, "1 820 €", 'k', 180); x0 = 540-(w1+w2)/2
    text(c, "≈", x0, 530, 'xb', 100, WH, 'l'); gtext(c, "1 820 €", x0+w1, 530, 'k', 180, align='l')
    text(c, "1 772 € d'action  +  48 € de dividendes", 540, 680, 'm', 34, WH, 'c', 1, 0, False)
    text(c, "change €/$ inclus · avant impôts et frais", 540, 735, 'l', 28, GR, 'c', 1, 0, False)
    pill(c, "×1,82", 540, 1130, 56)
    caption(c, [("Tes", 0), ("1" + NB + "000" + NB + "€" + NB + "?", 0), ("≈" + NB + "1" + NB + "820" + NB + "€", 1), ("aujourd'hui,", 0), ("dividendes", 0), ("compris.", 0)])
compose('b3d/kf_k1.png', k1, 'visa_da_k1_peage.png')
compose('b3d/kf_k2.png', k2, 'visa_da_k2_compteur.png')
compose('b3d/kf_k3.png', k3, 'visa_da_k3_reveal.png')
from PIL import Image
ims = [Image.open(f) for f in ('visa_da_k1_peage.png', 'visa_da_k2_compteur.png', 'visa_da_k3_reveal.png')]
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('sheet.png')
