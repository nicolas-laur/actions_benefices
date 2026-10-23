from nty import *
NB = ' '
def compose(t, draw_fn, glows=(), beam_a=1.0):
    im = room().copy(); im.alpha_composite(beam(t, beam_a))
    for g in glows: im.alpha_composite(g)
    s, c = surface(); draw_fn(c); im.alpha_composite(to_img(s)); return finish(im, t)

def k1():
    big = glow(lambda c: text(c, "1 149 €", 540, 830, 'a', 300, CREAM), (60, 16), (1.6, 1.2))
    def d(c):
        scrub(c, 250, .03)
        tag(c, "1 000 € DANS NETFLIX IL Y A 5 ANS", 540, 420)
        text(c, "AUJOURD'HUI", 540, 560, 'sb', 34, SUB, 'c', 1, 8)
        text(c, "5 ans pour… +149 €", 540, 1040, 'xb', 54, WHITE)
        pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1160)
        caption(c, [("1" + NB + "000" + NB + "€", 0), ("placés", 0), ("dans", 0), ("Netflix", 0), ("il", 0), ("y", 0), ("a", 0), ("cinq", 0), ("ans.", 0)])
    return compose(0.2, d, [big])

def k2():
    def d(c):
        scrub(c, 250, .48)
        text(c, "LE PARADOXE", 540, 360, 'a', 96, CREAM, 'c', 1, 2)
        # carte bénéfice
        ep_card(c, 90, 450, 900, 360)
        ep_head(c, 140, 500, "ÉPISODE 2", "Bénéfice record")
        vals = [4.49, 5.41, 8.71, 10.98, 13.65]; labs = ["2022", "2023", "2024", "2025", "12 mois"]
        for i, (v, l) in enumerate(zip(vals, labs)):
            h = v/13.65*170; x = 145+i*92
            rr(c, x, 760-h, 62, h, 10); col(c, GOLD if i == 4 else '5A4A3A'); c.fill()
            text(c, l, x+31, 785, 'm', 22, SUB)
        text(c, "13,6 Md$", 935, 640, 'a', 92, GOLD, 'r'); text(c, "+33 % sur un an", 935, 712, 'xb', 30, GREEN, 'r')
        # carte action
        ep_card(c, 90, 840, 900, 360)
        ep_head(c, 140, 890, "ÉPISODE 3", "L'action s'effondre")
        pts = [(0, .05), (.15, .0), (.3, .12), (.45, .2), (.6, .45), (.75, .62), (.88, .78), (1, .86)]
        c.set_line_width(7); c.set_line_join(1); col(c, CRIM)
        for i, (u, v) in enumerate(pts):
            x, y = 150+u*440, 1010+v*150
            (c.move_to if i == 0 else c.line_to)(x, y)
        c.stroke()
        text(c, "−43 %", 935, 1050, 'a', 110, CRIM, 'r'); text(c, "en un an", 935, 1130, 'xb', 30, SUB, 'r')
        caption(c, [("Le", 0), ("problème" + NB + "?", 0), ("L'action", 0), ("a", 0), ("perdu", 0), ("43" + NB + "%.", 1)], y=1380)
    return compose(14.0, d, [glow(lambda c: text(c, "−43 %", 935, 1050, 'a', 110, CRIM, 'r'), (30,), (1.4,), False)], .55)

def k3():
    def d(c):
        scrub(c, 250, .92)
        ep_card(c, 90, 400, 900, 820)
        text(c, "ÉPISODE SUIVANT", 540, 470, 'sb', 28, SUB, 'c', 1, 6)
        text(c, "RÉSULTATS", 540, 560, 'a', 104, CREAM); text(c, "20 OCTOBRE", 540, 680, 'a', 104, CRIM)
        # anneau de compte à rebours
        cx, cy, r = 540, 830, 62
        c.set_line_width(10); col(c, WHITE, .15); c.arc(cx, cy, r, 0, 2*math.pi); c.stroke()
        col(c, CREAM); c.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*.62); c.stroke(); text(c, "6", cx, cy, 'a', 56, CREAM)
        for i, (n, s) in enumerate((("1", "J'achète"), ("2", "Je vends"), ("3", "J'attends"))):
            y = 950+i*86; rr(c, 200, y, 680, 70, 16); col(c, CRIM if i == 0 else WHITE, .95 if i == 0 else .08); c.fill()
            text(c, n, 250, y+35, 'a', 40, WHITE); text(c, s, 300, y+35, 'xb', 34, WHITE, 'l')
        caption(c, [("Bonne", 0), ("affaire", 0), ("ou", 0), ("piège" + NB + "?", 1)], y=1352)
    return compose(28.0, d, [], .8)

ims = [k1(), k2(), k3()]
for im, n in zip(ims, ('n_da_k1_promesse', 'n_da_k2_paradoxe', 'n_da_k3_suivant')): im.save(f'{n}.png')
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('sheet.png')
