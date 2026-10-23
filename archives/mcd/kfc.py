from mty import *
NB = ' '
def k1(c):
    bg(c); progress(c, .02); promise(c); question_pill(c)
    caption(c, [("5", 0), ("ans", 0), ("de", 0), ("McDo", 0), ("en", 0), ("Bourse", 0), ("=", 0), ("+4" + NB + "€.", 1)])
def k2(c):
    bg(c, 1); progress(c, .5); kiosk_panel(c)
    item(c, 520, "L'ACTION", "depuis son plus haut de février", "−30 %", RED, 'down')
    item(c, 690, "CLIENTS MODESTES", "ils viennent moins depuis 2 ans", "↓", RED, 'people')
    item(c, 860, "VENTES COMPARABLES", "avril-juin 2026, au ralenti", "+1,3 %", INK, 'flat')
    item(c, 1030, "DIVIDENDES", "versés en 5 ans sur 1 000 €", "+140 €", GREEN, 'coin', .5)
    caption(c, [("Les", 0), ("clients", 0), ("modestes", 0), ("viennent", 0), ("moins", 1), ("depuis", 0), ("2", 0), ("ans.", 0)])
def k3(c):
    bg(c, 2); progress(c, .85); receipt(c, 1.0)
    caption(c, [("Sans", 0), ("les", 0), ("dividendes,", 0), ("tu", 0), ("n'aurais", 0), ("presque", 0), ("[rien]", 0), ("gagné.", 0)][:0] or [("Total" + NB + ":", 0), ("≈" + NB + "1" + NB + "143" + NB + "€,", 1), ("grâce", 0), ("aux", 0), ("dividendes.", 0)], y=1352)
for f, n in ((k1, 'm_da_k1_promesse'), (k2, 'm_da_k2_borne'), (k3, 'm_da_k3_ticket')):
    s, c = surface(); f(c); to_img(s).convert('RGB').save(f'{n}.png')
ims = [Image.open(f'{n}.png') for n in ('m_da_k1_promesse', 'm_da_k2_borne', 'm_da_k3_ticket')]
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('sheet.png')
