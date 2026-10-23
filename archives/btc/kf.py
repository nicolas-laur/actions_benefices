import sys; sys.path.insert(0, '/home/claude/btc')
from bty import *
NB = ' '
COIN = '/home/claude/btc/kf_coin.png'
def compose(bg, draw_fn, glows=(), t=0):
    im = bg.copy()
    for g in glows: im.alpha_composite(g)
    s, c = surface(); draw_fn(c); im.alpha_composite(to_img(s)); return finish(im, t, 6.0)

def k1():
    bg = coin_bg(COIN, .62, .27, 0, .95)
    big = glow(lambda c: text(c, "742 M€", 540, 990, 'a', 250, GOLD), (60, 16), (1.4, 1.1))
    def d(c):
        scrub(c, 150, .02)
        tag(c, "MAI 2010 · 10 000 BTC", 540, 690)
        pizza_icon(c, 300, 800, .7); pizza_icon(c, 780, 800, .7)
        text(c, "2 PIZZAS =", 540, 800, 'a', 84, CREAM, 'c', 1, 2)
        text(c, "payées 41 $ à l'époque", 540, 1135, 'xb', 40, SUB)
        pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1230)
        caption(c, [("Deux", 0), ("pizzas", 0), ("à", 0), ("742" + NB + "millions" + NB + "d'euros.", 1)])
    return compose(bg, d, [big])

def k2():
    bg = coin_bg(COIN, .9, .5, 26, .55)
    def d(c):
        scrub(c, 150, .45)
        text(c, "1 000 € IL Y A 10 ANS", 540, 330, 'a', 80, CREAM, 'c', 1, 2)
        glass(c, 70, 410, 940, 820)
        head(c, 120, 460, "OCT. 2016 → OCT. 2026", "Ta mise en euros")
        X0, X1, Y0, Y1 = 130, 950, 1060, 720
        def px(y, v): return X0+(y-2016.79)/10*(X1-X0), Y0+(Y1-Y0)*v/190000
        pts = PATH10
        c.move_to(*px(*pts[0]))
        for p in pts[1:]: c.line_to(*px(*p))
        c.line_to(px(pts[-1][0], 0)[0], Y0); c.line_to(X0, Y0); c.close_path()
        g = cairo.LinearGradient(0, Y1, 0, Y0); g.add_color_stop_rgba(0, *hx(ORANGE, .35)); g.add_color_stop_rgba(1, *hx(ORANGE, 0)); c.set_source(g); c.fill()
        c.set_line_width(6); c.set_line_join(1); col(c, GOLD); c.move_to(*px(*pts[0]))
        for p in pts[1:]: c.line_to(*px(*p))
        c.stroke(); c.arc(*px(*pts[-1]), 11, 0, 2*math.pi); col(c, CREAM); c.fill()
        for yr, v, lab in ((2018.96, PATH10[4][1], "−84 %"), (2022.88, PATH10[12][1], "−77 %")):
            x, y = px(yr, v); w = tw(c, lab, 'xb', 28)+24; rr(c, x-w/2, y+16, w, 46, 10); col(c, RED); c.fill(); text(c, lab, x, y+39, 'xb', 28, WHITE)
        for yy in (2017, 2019, 2021, 2023, 2025): text(c, str(yy), px(yy, 0)[0], 1160, 'm', 22, SUB)
        text(c, "127 500 €", 120, 620, 'a', 92, GOLD, 'l')
        w = tw(c, "×128", 'xb', 40)+36; xx = 140+tw(c, "127 500 €", 'a', 92); rr(c, xx, 588, w, 64, 14); col(c, GREEN); c.fill(); text(c, "×128", xx+w/2, 620, 'xb', 40, INK)
        text(c, "valeur approx. · change €/$ inclus", 540, 1203, 'm', 21, SUB, 'c', .8)
        caption(c, [("Aujourd'hui,", 0), ("tu", 0), ("aurais", 0), ("127" + NB + "000" + NB + "euros.", 1)])
    return compose(bg, d, [], 12)

def k3():
    bg = coin_bg(COIN, .8, .30, 0, .7)
    def d(c):
        scrub(c, 150, .9)
        glass(c, 90, 760, 900, 470)
        text(c, "AUJOURD'HUI", 540, 820, 'sb', 28, SUB, 'c', 1, 6)
        text(c, "−34 % SOUS SON RECORD", 540, 900, 'a', 76, RED)
        for i, (n, s) in enumerate((("1", "J'achète"), ("2", "Je vends"), ("3", "J'attends"))):
            y = 970+i*82; rr(c, 200, y, 680, 68, 16); col(c, ORANGE if i == 0 else WHITE, .95 if i == 0 else .08); c.fill()
            if i: rr(c, 200, y, 680, 68, 16); c.set_line_width(2); col(c, ORANGE, .6); c.stroke()
            text(c, n, 250, y+34, 'a', 40, INK if i == 0 else WHITE); text(c, s, 300, y+34, 'xb', 34, INK if i == 0 else WHITE, 'l')
        caption(c, [("Alors,", 0), ("opportunité", 0), ("ou", 0), ("piège" + NB + "?", 1)])
    return compose(bg, d, [glow(lambda c: text(c, "−34 % SOUS SON RECORD", 540, 900, 'a', 76, RED), (26,), (1.2,), False)], 28)

ims = [k1(), k2(), k3()]
for im, n in zip(ims, ('b_da_k1_pizza', 'b_da_k2_10ans', 'b_da_k3_record')): im.save(f'/home/claude/btc/{n}.png')
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('/home/claude/btc/sheet.png')
