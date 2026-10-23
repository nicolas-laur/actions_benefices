from mty2 import *
NB = ' '
def frame(layers_draw, neons=(), extra=None):
    base = bokeh_layer().copy()
    for n in neons: base.alpha_composite(n)
    if extra is not None: base.alpha_composite(extra)
    s, c = surface(); layers_draw(c); base.alpha_composite(to_img(s)); return base
def k1():
    neons = [neon_text("1 004 €", 540, 860, 230, YEL, track=-4)]
    def d(c):
        progress(c, .02)
        text(c, "1 000 € DANS MCDO IL Y A 5 ANS", 540, 420, 'sb', 34, YEL, 'c', 1, 4)
        text(c, "1 000 €", 540, 560, 'k', 104, WHITE, 'c', .55)
        c.set_line_width(8); col(c, YEL, .9); c.move_to(540, 640); c.line_to(540, 715); c.stroke(); c.move_to(508, 688); c.line_to(540, 722); c.line_to(572, 688); c.stroke()
        text(c, "5 ans pour gagner… 4 €", 540, 1035, 'xb', 52, WHITE)
        w = tw(c, "Tu achètes ? Réponds 1, 2 ou 3", 'xb', 34)+70; rr(c, 540-w/2, 1140, w, 76, 38); col(c, RED); c.fill(); text(c, "Tu achètes ? Réponds 1, 2 ou 3", 540, 1178, 'xb', 34, WHITE)
        caption(c, [("5", 0), ("ans", 0), ("de", 0), ("McDo", 0), ("en", 0), ("Bourse", 0), ("=", 0), ("+4" + NB + "€.", 1)])
    return frame(d, neons)
def k2():
    neons = [glow_layer(lambda c: (rr(c, 70, 380, 940, 860, 40), c.set_line_width(5), col(c, YEL), c.stroke()), (22, 8), (.9, 1.0))]
    def d(c):
        progress(c, .5)
        glass_panel(c, 70, 380, 940, 860, 40, '2A0C08', .55)
        text(c, "TA COMMANDE · 5 ANS", 120, 440, 'xb', 40, YEL, 'l')
        kiosk_row(c, 510, "L'ACTION", "depuis son plus haut de février", "−30 %", RED, 'down')
        kiosk_row(c, 680, "CLIENTS MODESTES", "ils viennent moins depuis 2 ans", "↓", RED, 'people')
        kiosk_row(c, 850, "VENTES COMPARABLES", "avril-juin 2026, au ralenti", "+1,3 %", WHITE, 'flat')
        kiosk_row(c, 1020, "DIVIDENDES", "versés en 5 ans sur 1 000 €", "+140 €", GREEN, 'coin', .45)
        caption(c, [("Les", 0), ("clients", 0), ("modestes", 0), ("viennent", 0), ("moins", 1), ("depuis", 0), ("2", 0), ("ans.", 0)])
    return frame(d, neons)
def k3():
    def d(c):
        progress(c, .85)
        caption(c, [("Total" + NB + ":", 0), ("≈" + NB + "1" + NB + "143" + NB + "€,", 1), ("grâce", 0), ("aux", 0), ("dividendes.", 0)])
    # halo chaud derrière le ticket
    halo = glow_layer(lambda c: (rr(c, 190, 330, 700, 880, 6), col(c, 'FFB347', .35), c.fill()), (60, 30), (1.0, .6))
    return frame(d, [halo], receipt_img(1.0))
ims = [k1(), k2(), k3()]
for im, n in zip(ims, ('m_da_k1_promesse', 'm_da_k2_borne', 'm_da_k3_ticket')): im.convert('RGB').save(f'{n}.png')
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.convert('RGB').resize((540, 960)), (20+i*550, 20))
sh.save('sheet2.png')
