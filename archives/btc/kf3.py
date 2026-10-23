"""v3 : graphiques explosifs. Fusée log du prix depuis la pizza + barres qui crèvent le verre."""
import sys, random; sys.path.insert(0, '/home/claude/btc')
from bglass import *
NB = ' '
BG = '/home/claude/btc/kf_rain.png'
def fin(cv, fn, t):
    darken_band(cv, 1240, 1470, .6)
    s, c = surface(); fn(c); cv.alpha_composite(to_img(s)); return finish(cv, t, 5.0)
def burst(c, x, y, r0, r1, n=18, color=GOLD, a=1, seed=3, rot=0):
    """rayons d'explosion + étincelles"""
    rnd = random.Random(seed)
    for k in range(n):
        ang = rot+2*math.pi*k/n+rnd.uniform(-.08, .08); ra = r0+rnd.uniform(0, (r1-r0)*.4); rb = r1*rnd.uniform(.7, 1.1)
        g = cairo.LinearGradient(x+ra*math.cos(ang), y+ra*math.sin(ang), x+rb*math.cos(ang), y+rb*math.sin(ang))
        g.add_color_stop_rgba(0, *hx(color, .9*a)); g.add_color_stop_rgba(1, *hx(color, 0)); c.set_source(g); c.set_line_width(rnd.uniform(3, 7)); c.set_line_cap(1)
        c.move_to(x+ra*math.cos(ang), y+ra*math.sin(ang)); c.line_to(x+rb*math.cos(ang), y+rb*math.sin(ang)); c.stroke()
    for k in range(40):
        ang = rnd.uniform(0, 2*math.pi); d = rnd.uniform(r0, r1*1.2); rr_ = rnd.uniform(2, 6)
        col(c, rnd.choice((GOLD, CREAM, ORANGE)), a*rnd.uniform(.4, 1)); c.arc(x+d*math.cos(ang), y+d*math.sin(ang), rr_, 0, 2*math.pi); c.fill()

# prix du BTC en $ (points clés, approx.) depuis la pizza
LOGP = [(2010.39, .0041), (2010.9, .3), (2011.45, 30), (2011.9, 2.5), (2012.6, 12), (2013.3, 230), (2013.5, 70), (2013.92, 1150), (2015.05, 200),
        (2016.5, 650), (2017.96, 19000), (2018.96, 3200), (2019.5, 12000), (2020.2, 5000), (2021.3, 60000), (2021.55, 31000), (2021.86, 67000),
        (2022.88, 15800), (2024.2, 70000), (2024.95, 98000), (2025.77, 124000), (2026.5, 58566), (2026.79, 82709)]

def k2():
    cv = rain_bg(BG, .5, 8); darkspot(cv, 540, 760, 700, 760, .7)
    X0, X1, Y0, Y1 = 60, 800, 600, 90
    def px(y, p): return X0+(y-2010.39)/(2026.79-2010.39)*(X1-X0), Y0+(Y1-Y0)*(math.log10(p)+3)/(math.log10(150000)+3)
    def chart(c, w, h):
        text(c, "PRIX D'UN BITCOIN · ÉCHELLE LOG", 40, 46, 'sb', 24, 'FFE2A8', 'l', 1, 2)
        for p, lab in ((.01, "0,01 $"), (1, "1 $"), (100, "100 $"), (10000, "10 000 $")):
            y = px(2010.39, p)[1]; c.set_line_width(1); col(c, WHITE, .12); c.move_to(X0, y); c.line_to(w-40, y); c.stroke(); text(c, lab, X0+4, y-14, 'm', 20, SUB, 'l')
        c.move_to(*px(*LOGP[0]))
        for p in LOGP[1:]: c.line_to(*px(*p))
        c.line_to(px(*LOGP[-1])[0], Y0); c.line_to(X0, Y0); c.close_path()
        g = cairo.LinearGradient(0, Y1, 0, Y0); g.add_color_stop_rgba(0, *hx(ORANGE, .45)); g.add_color_stop_rgba(1, *hx(ORANGE, 0)); c.set_source(g); c.fill()
        for a_, lw in ((.08, 34), (.18, 18), (1, 7)):
            c.move_to(*px(*LOGP[0]))
            for p in LOGP[1:]: c.line_to(*px(*p))
            c.set_line_width(lw); c.set_line_join(1); c.set_line_cap(1); col(c, GOLD, a_); c.stroke()
        x, y = px(*LOGP[0]); c.arc(x, y, 12, 0, 2*math.pi); col(c, CREAM); c.fill(); text(c, "2010 · 0,004 $", x+10, y+40, 'xb', 26, CREAM, 'l')
        x, y = px(*LOGP[-1]); burst(c, x, y, 16, 110, 16, GOLD, .9); c.arc(x, y, 13, 0, 2*math.pi); col(c, WHITE); c.fill()
        text(c, "82 700 $", x-30, y+70, 'xb', 32, CREAM, 'r')
        for yy in (2010, 2014, 2018, 2022, 2026): text(c, str(yy), px(yy+.39 if yy == 2010 else yy, 1)[0], h-26, 'm', 22, SUB)
    p = gpanel(860, 680, chart)
    place(cv, p, tilt_quad(540, 900, 860, 680, ry=.24, rx=.1), 1, 26, .55)
    glow_text(cv, "×20 000 000", 540, 360, 150)
    def d(c):
        scrub(c, 150, .2)
        text(c, "UN BITCOIN, DEPUIS LA PIZZA", 540, 230, 'sb', 32, 'FFE2A8', 'c', 1, 6)
        caption(c, [("À", 0), ("l'époque,", 0), ("ça", 0), ("valait", 0), ("41" + NB + "dollars.", 1)])
    return fin(cv, d, 6)

def k3():
    cv = rain_bg(BG, .5, 8); darkspot(cv, 540, 760, 700, 760, .7)
    PX, PY, PW, PH = 110, 560, 860, 640          # panneau à plat : coordonnées écran = panneau + décalage
    BASE = 520; SC = 300/127546
    bars = [("1 an", 748, RED), ("5 ans", 1503, GOLD), ("10 ans", 127546, GOLD), ("13 ans", 716608, ORANGE)]
    def chart(c, w, h):
        text(c, "1 000 € PLACÉS IL Y A…", 40, 46, 'sb', 24, 'FFE2A8', 'l', 1, 2)
        c.set_line_width(2); col(c, WHITE, .3); c.move_to(40, BASE); c.line_to(w-40, BASE); c.stroke()
        for i, (lab, v, cl) in enumerate(bars):
            x = 70+i*195; hh = max(6, v*SC)
            text(c, lab, x+70, BASE+45, 'xb', 30, WHITE)
            if i < 3:
                rr(c, x, BASE-hh, 140, hh, 10); col(c, cl); c.fill()
                lab2 = f"{v:,.0f} €".replace(',', ' '); text(c, lab2, x+70, BASE-hh-28, 'xb', 30 if i < 2 else 34, CREAM)
        text(c, "valeur au 14 oct. 2026 · change €/$ inclus", w/2, h-40, 'm', 21, SUB, 'c', .85)
    p = gpanel(PW, PH, chart)
    place(cv, p, [(PX, PY), (PX+PW, PY), (PX+PW, PY+PH), (PX, PY+PH)], 1, 26, .55)
    def d(c):
        scrub(c, 150, .55)
        # la barre des 13 ans traverse le verre et sort de l'écran
        x = PX+70+3*195; top = -40; bot = PY+BASE
        for a_, e in ((.10, 40), (.2, 20), (.35, 8)):
            rr(c, x-e, top, 140+2*e, bot-top+e, 16); col(c, ORANGE, a_); c.fill()
        g = cairo.LinearGradient(0, top, 0, bot); g.add_color_stop_rgb(0, *hx('FFE7B0')[:3]); g.add_color_stop_rgb(.3, *hx(ORANGE)[:3]); g.add_color_stop_rgb(1, *hx('C2600A')[:3])
        rr(c, x, top, 140, bot-top, 10); c.set_source(g); c.fill()
        burst(c, x+70, PY+4, 30, 230, 22, GOLD, .95, 7)
        # éclats de verre
        rnd = random.Random(4)
        for k in range(14):
            sx, sy = x+70+rnd.uniform(-150, 150), PY+rnd.uniform(-160, 10); s_ = rnd.uniform(10, 26); r_ = rnd.uniform(0, 6.28)
            c.save(); c.translate(sx, sy); c.rotate(r_); c.move_to(0, -s_); c.line_to(s_*.6, s_*.4); c.line_to(-s_*.5, s_*.6); c.close_path()
            col(c, 'FFF3D6', .35); c.fill_preserve(); col(c, WHITE, .7); c.set_line_width(1.5); c.stroke(); c.restore()
        caption(c, [("Il", 0), ("y", 0), ("a", 0), ("treize", 0), ("ans…", 0), ("plus", 0), ("de", 0), ("700" + NB + "000" + NB + "€.", 1)])
    darken_band(cv, 1240, 1470, .6); s_, c_ = surface(); d(c_); cv.alpha_composite(to_img(s_))
    glow_text(cv, "716 600 €", 400, 330, 104)
    s2, c2 = surface(); text(c2, "×717", 400, 450, 'xb', 44, GREEN); cv.alpha_composite(to_img(s2))
    out = finish(cv, 18, 5.0)
    return out

ims = [Image.open('/home/claude/btc/b2_da_k1_pizza.png'), k2(), k3(), Image.open('/home/claude/btc/b2_da_k3_record.png')]
for im, n in zip(ims[1:3], ('b3_da_k2_fusee', 'b3_da_k3_barres')): im.save(f'/home/claude/btc/{n}.png')
sh = Image.new('RGB', (4*550+10, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.convert('RGB').resize((540, 960)), (10+i*550, 20))
sh.save('/home/claude/btc/sheet3.png')
