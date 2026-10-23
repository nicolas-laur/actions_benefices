"""DA Micron : data center néon (Blender) + verre 3D teinté cyan + graphiques explosifs."""
import sys, random; sys.path.insert(0, '/home/claude/btc'); sys.path.insert(0, '/home/claude/mu')
from bglass import *
NB = ' '
CY = '00E5FF'; VI = '8B5CF6'; MG = 'FF3DBB'; ICE = 'D8F7FF'; SUBC = '9FB3C8'; INKB = '04121A'
BG = '/home/claude/mu/kf_dc.png'
def bg(dim=.6, blur=0):
    im = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS)
    if blur: im = lowblur(im, blur, 2)
    return ImageEnhance.Brightness(im).enhance(dim).convert('RGBA')
def cpanel(w, h, draw=None, r=36): return gpanel(w, h, draw, r, ta=.10, edge=.7, tint='BDF4FF')
def gt(cv, s, x, y, size, **k):
    kw = dict(top='FFFFFF', bottom='7FEFFF', glow=CY, ga=.8); kw.update(k); glow_text(cv, s, x, y, size, **kw)
def cap(c, words, y=1352, size=46, a=1):
    """sous-titres : mot-clé surligné cyan"""
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 800: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 66, 12); col(c, CY, a); c.fill(); text(c, w, x+10, yy, 'b', size, INKB, 'l', a)
            else: text(c, w, x+3, yy+4, 'b', size, '000000', 'l', .55*a); text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp
def bar(c, u):
    rr(c, 140, 146, 800, 8, 4); col(c, WHITE, .18); c.fill(); rr(c, 140, 146, max(8, 800*u), 8, 4); col(c, CY); c.fill()
def burst(c, x, y, r0, r1, n=18, color=CY, a=1, seed=3):
    rnd = random.Random(seed)
    for k in range(n):
        ang = 2*math.pi*k/n+rnd.uniform(-.08, .08); ra = r0+rnd.uniform(0, (r1-r0)*.4); rb = r1*rnd.uniform(.7, 1.1)
        g = cairo.LinearGradient(x+ra*math.cos(ang), y+ra*math.sin(ang), x+rb*math.cos(ang), y+rb*math.sin(ang))
        g.add_color_stop_rgba(0, *hx(color, .9*a)); g.add_color_stop_rgba(1, *hx(color, 0)); c.set_source(g); c.set_line_width(rnd.uniform(3, 7)); c.set_line_cap(1)
        c.move_to(x+ra*math.cos(ang), y+ra*math.sin(ang)); c.line_to(x+rb*math.cos(ang), y+rb*math.sin(ang)); c.stroke()
    for k in range(40):
        ang = rnd.uniform(0, 2*math.pi); d = rnd.uniform(r0, r1*1.2)
        col(c, rnd.choice((CY, ICE, VI)), a*rnd.uniform(.4, 1)); c.arc(x+d*math.cos(ang), y+d*math.sin(ang), rnd.uniform(2, 6), 0, 2*math.pi); c.fill()
def fin(cv, fn, t):
    darken_band(cv, 1240, 1470, .6); s, c = surface(); fn(c); cv.alpha_composite(to_img(s)); return finish(cv, t, 4.0)

def k1():
    cv = bg(.62, 2); darkspot(cv, 540, 760, 640, 600, .65)
    chip = cpanel(520, 110, lambda k, w, h: text(k, "1 000 € · IL Y A 5 ANS", w/2, h/2, 'xb', 34, ICE, 'c', 1, 3), r=55)
    place(cv, chip, tilt_quad(540, 470, 520, 110, ry=-.25, rx=-.1), 1, 18, .4)
    gt(cv, "14 000 €", 540, 760, 230)
    def name_card(k, w, h):
        text(k, "DANS UNE ENTREPRISE", w/2, 58, 'sb', 26, ICE, 'c', 1, 4); text(k, "QUE TU NE CONNAIS PAS", w/2, 100, 'sb', 26, ICE, 'c', 1, 4)
        rr(k, 110, 140, w-220, 74, 14); col(k, '0B1E2A', .9); k.fill()
        for i in range(9): rr(k, 130+i*((w-260)/9), 160, (w-260)/9-14, 34, 8); col(k, CY, .35+.25*(i % 2)); k.fill()
    place(cv, cpanel(600, 240, name_card), tilt_quad(540, 1040, 600, 240, ry=.22, rx=.12), 1, 20, .5)
    def d(c):
        bar(c, .02); pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1225, CY, INKB)
        cap(c, [("Quatorze", 0), ("mille" + NB + "euros.", 1)])
    return fin(cv, d, 0)

NI = [("2022", 8.69), ("2023", -5.83), ("2024", 0.78), ("2025", 8.54), ("2026", 84.97)]
def k2():
    cv = bg(.5, 8); darkspot(cv, 540, 760, 700, 760, .7)
    PX, PY, PW, PH = 110, 620, 860, 580; BASE = 360; SC = 2.2
    def chart(k, w, h):
        text(k, "BÉNÉFICE NET ANNUEL · MILLIARDS $", 40, 46, 'sb', 24, ICE, 'l', 1, 2)
        k.set_line_width(2); col(k, WHITE, .3); k.move_to(40, BASE); k.line_to(w-40, BASE); k.stroke()
        for i, (y, v) in enumerate(NI[:4]):
            x = 60+i*160; hh = abs(v)*SC*6
            if v >= 0: rr(k, x, BASE-hh, 110, max(4, hh), 8); col(k, CY if v > 0 else SUBC); k.fill(); text(k, f"{v:.1f}".replace('.', ','), x+55, BASE-hh-26, 'xb', 28, ICE)
            else: rr(k, x, BASE, 110, hh, 8); col(k, MG); k.fill(); text(k, f"−{abs(v):.1f}".replace('.', ','), x+55, BASE+hh+26, 'xb', 28, MG)
            text(k, y, x+55, h-50, 'm', 24, SUBC)
        text(k, "2026", 60+4*160+55, h-50, 'xb', 24, ICE)
        text(k, "exercices clos fin août / début sept.", w/2, h-16, 'm', 19, SUBC, 'c', .8)
    place(cv, cpanel(PW, PH, chart), [(PX, PY), (PX+PW, PY), (PX+PW, PY+PH), (PX, PY+PH)], 1, 26, .55)
    def d(c):
        bar(c, .35)
        x = PX+60+4*160; bot = PY+BASE; top = -40
        for a_, e in ((.10, 40), (.2, 20), (.35, 8)): rr(c, x-e, top, 110+2*e, bot-top+e, 16); col(c, CY, a_); c.fill()
        gr = cairo.LinearGradient(0, top, 0, bot); gr.add_color_stop_rgb(0, *hx('FFFFFF')[:3]); gr.add_color_stop_rgb(.3, *hx(CY)[:3]); gr.add_color_stop_rgb(1, *hx('0077A8')[:3])
        rr(c, x, top, 110, bot-top, 8); c.set_source(gr); c.fill()
        burst(c, x+55, PY+4, 30, 230, 22, CY, .95, 7)
        rnd = random.Random(4)
        for k in range(14):
            sx, sy = x+55+rnd.uniform(-150, 150), PY+rnd.uniform(-160, 10); s_ = rnd.uniform(10, 26)
            c.save(); c.translate(sx, sy); c.rotate(rnd.uniform(0, 6.28)); c.move_to(0, -s_); c.line_to(s_*.6, s_*.4); c.line_to(-s_*.5, s_*.6); c.close_path()
            col(c, ICE, .35); c.fill_preserve(); col(c, WHITE, .7); c.set_line_width(1.5); c.stroke(); c.restore()
        cap(c, [("En", 0), ("un", 0), ("an,", 0), ("son", 0), ("bénéfice", 0), ("×10.", 1)])
    darken_band(cv, 1240, 1470, .6); s, c = surface(); d(c); cv.alpha_composite(to_img(s))
    gt(cv, "85 Md$", 380, 330, 140); s2, c2 = surface(); text(c2, "×10 en un an", 380, 450, 'xb', 42, '3FD08A'); cv.alpha_composite(to_img(s2))
    return finish(cv, 10, 4.0)

def k3():
    cv = bg(.55, 6); darkspot(cv, 540, 760, 680, 700, .7)
    gt(cv, "PÉPITE", 540, 330, 140)
    gt(cv, "OU SOMMET ?", 540, 480, 120, bottom='FF9AE0', glow=MG)
    def choices(k, w, h):
        for i, (n, s) in enumerate((("1", "J'achète"), ("2", "Je vends"), ("3", "J'attends"))):
            y = 30+i*92; on = i == 0; rr(k, 30, y, w-60, 74, 37); col(k, CY if on else WHITE, .95 if on else .1); k.fill()
            text(k, n, 80, y+37, 'a', 40, INKB if on else WHITE); text(k, s, 130, y+37, 'xb', 34, INKB if on else WHITE, 'l')
    place(cv, cpanel(620, 330, choices, r=48), tilt_quad(540, 960, 620, 330, ry=-.2, rx=.1), 1, 22, .5)
    def card(k, w, h):
        text(k, "2022", 40, 44, 'sb', 22, ICE, 'l', 1, 2); text(k, "−43 %", 40, 100, 'a', 54, MG, 'l')
        text(k, "DEPUIS JUIN", w-40, 44, 'sb', 22, ICE, 'r', 1, 2); text(k, "−27 %", w-40, 100, 'a', 54, MG, 'r')
    place(cv, cpanel(560, 150, card), tilt_quad(540, 680, 560, 150, ry=.2, rx=-.1), .95, 18, .4)
    def d(c):
        bar(c, .9); cap(c, [("Alors,", 0), ("pépite", 0), ("ou", 0), ("sommet" + NB + "?", 1)])
    return fin(cv, d, 28)

if __name__ == "__main__":
    ims = [k1(), k2(), k3()]
    for im, n in zip(ims, ('mu_da_k1_promesse', 'mu_da_k2_benefice', 'mu_da_k3_choix')): im.save(f'/home/claude/mu/{n}.png')
    sh = Image.new('RGB', (1680, 1000), 'white')
    for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
    sh.save('/home/claude/mu/sheet.png')
