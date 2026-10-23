import sys; sys.path.insert(0, '/home/claude/btc')
from bglass import *
NB = ' '
BG = '/home/claude/btc/kf_rain.png'
def fin(cv, fn, t):
    darken_band(cv, 1240, 1470, .6)
    s, c = surface(); fn(c); cv.alpha_composite(to_img(s)); return finish(cv, t, 5.0)

def k1():
    cv = rain_bg(BG, .62, 3); darkspot(cv, 540, 820, 620, 560)
    p = gpanel(560, 230, lambda c, w, h: (text(c, "MAI 2010 · 10 000 BTC", w/2, 58, 'sb', 26, 'FFE2A8', 'c', 1, 3),
                                           pizza_icon(c, 95, 150, .62), pizza_icon(c, w-95, 150, .62),
                                           text(c, "2 PIZZAS", w/2, 152, 'a', 86, CREAM, 'c', 1, 2)))
    place(cv, p, tilt_quad(540, 560, 560, 230, ry=-.28, rx=-.12), 1, 20, .5)
    glow_text(cv, "742 M€", 540, 860, 250)
    def d(c):
        scrub(c, 150, .02)
        text(c, "payées 41 $ à l'époque", 540, 1060, 'xb', 40, CREAM)
        pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1165)
        caption(c, [("Deux", 0), ("pizzas", 0), ("à", 0), ("742" + NB + "millions" + NB + "d'euros.", 1)])
    return fin(cv, d, 0)

def k2():
    cv = rain_bg(BG, .55, 8); darkspot(cv, 540, 700, 640, 700)
    def chart(c, w, h):
        text(c, "1 000 € · OCT. 2016 → OCT. 2026", 40, 50, 'sb', 24, 'FFE2A8', 'l', 1, 2)
        X0, X1, Y0, Y1 = 50, w-50, h-90, 150
        def px(y, v): return X0+(y-2016.79)/10*(X1-X0), Y0+(Y1-Y0)*v/190000
        c.move_to(*px(*PATH10[0]))
        for p in PATH10[1:]: c.line_to(*px(*p))
        c.line_to(X1, Y0); c.line_to(X0, Y0); c.close_path()
        g = cairo.LinearGradient(0, Y1, 0, Y0); g.add_color_stop_rgba(0, *hx(ORANGE, .38)); g.add_color_stop_rgba(1, *hx(ORANGE, 0)); c.set_source(g); c.fill()
        for a_, lw in ((.1, 26), (.2, 14), (1, 6)):
            c.move_to(*px(*PATH10[0]))
            for p in PATH10[1:]: c.line_to(*px(*p))
            c.set_line_width(lw); c.set_line_join(1); col(c, GOLD, a_); c.stroke()
        c.arc(*px(*PATH10[-1]), 11, 0, 2*math.pi); col(c, CREAM); c.fill()
        for yr, v, lab in ((2018.96, PATH10[4][1], "−84 %"), (2022.88, PATH10[12][1], "−77 %")):
            x, y = px(yr, v); w_ = tw(c, lab, 'xb', 28)+24; rr(c, x-w_/2, y+16, w_, 46, 10); col(c, RED); c.fill(); text(c, lab, x, y+39, 'xb', 28, WHITE)
        for yy in (2017, 2019, 2021, 2023, 2025): text(c, str(yy), px(yy, 0)[0], h-28, 'm', 22, SUB)
    p = gpanel(860, 600, chart)
    place(cv, p, tilt_quad(540, 860, 860, 600, ry=.22, rx=.08), 1, 26, .55)
    glow_text(cv, "127 500 €", 540, 370, 170)
    def d(c):
        scrub(c, 150, .45)
        text(c, "1 000 € IL Y A 10 ANS", 540, 250, 'sb', 32, 'FFE2A8', 'c', 1, 6)
        w = tw(c, "×128", 'xb', 40)+40; rr(c, 540-w/2, 470, w, 64, 32); col(c, GREEN); c.fill(); text(c, "×128", 540, 502, 'xb', 40, INK)
        text(c, "valeur approx. · change €/$ inclus", 540, 1205, 'm', 21, SUB, 'c', .8)
        caption(c, [("Aujourd'hui,", 0), ("tu", 0), ("aurais", 0), ("127" + NB + "000" + NB + "euros.", 1)], y=1352)
    return fin(cv, d, 12)

def k3():
    cv = rain_bg(BG, .58, 6); darkspot(cv, 540, 700, 620, 600)
    glow_text(cv, "−34 %", 540, 470, 230, top='FFFFFF', bottom='FF6B6B', glow='E5484D', ga=.6)
    def choices(c, w, h):
        for i, (n, s) in enumerate((("1", "J'achète"), ("2", "Je vends"), ("3", "J'attends"))):
            y = 30+i*92; rr(c, 30, y, w-60, 74, 37); col(c, ORANGE if i == 0 else WHITE, .95 if i == 0 else .1); c.fill()
            text(c, n, 80, y+37, 'a', 40, INK if i == 0 else WHITE); text(c, s, 130, y+37, 'xb', 34, INK if i == 0 else WHITE, 'l')
    p = gpanel(620, 330, choices, r=48)
    place(cv, p, tilt_quad(540, 960, 620, 330, ry=-.2, rx=.1), 1, 22, .5)
    def d(c):
        scrub(c, 150, .9)
        text(c, "SOUS SON RECORD D'OCTOBRE 2025", 540, 690, 'sb', 30, 'FFE2A8', 'c', 1, 4)
        caption(c, [("Alors,", 0), ("opportunité", 0), ("ou", 0), ("piège" + NB + "?", 1)])
    return fin(cv, d, 28)

ims = [k1(), k2(), k3()]
for im, n in zip(ims, ('b2_da_k1_pizza', 'b2_da_k2_10ans', 'b2_da_k3_record')): im.save(f'/home/claude/btc/{n}.png')
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('/home/claude/btc/sheet2.png')
