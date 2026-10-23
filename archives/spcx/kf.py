import sys; sys.path.insert(0, '/home/claude/spcx')
from sty import *

def base(t, alt, cloud=True):
    cv = sky(t, alt)
    cl = clouds(t, alt) if cloud else None
    if cl: cv.alpha_composite(cl)
    return cv
def fin(cv, fn, t):
    darken_band(cv, 1240, 1470, .55); s, c = surface(); fn(c); cv.alpha_composite(to_img(s)); return finish(cv, t, 4.0)

def k1():
    t = .3; cv = base(t, .12)
    sm = smoke(t, 540, 1330, .12, 1.0); cv.alpha_composite(sm)
    put_rocket(cv, t, 540, 1230, .72)
    darkspot(cv, 540, 330, 600, 240, .35)
    chip = spanel(560, 96, lambda k, w, h: text(k, "1 000 € AU SOMMET DE JUIN", w/2, h/2, 'xb', 30, ICE, 'c', 1, 3), r=48)
    place(cv, chip, tilt_quad(540, 170, 560, 96, ry=-.2, rx=-.1), 1, 14, .3)
    gtw(cv, "682 €", 540, 360, 230)
    def d(c):
        sbar(c, .02); pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 545, FIRE, INKB)
        capw(c, [("Six" + NB + "cent" + NB + "quatre-vingts" + NB + "euros.", 1)])
    return fin(cv, d, t)

PTS = [(0, 135), (.18, 160), (.42, 180), (.7, 205), (1, 225.64)]
def k2():
    t = 6.0; cv = base(t, .45)
    X0, X1, Y0, Y1 = 150, 700, 1190, 560
    def px(u, p): return X0+u*(X1-X0), Y0+(Y1-Y0)*(p-130)/(226-130)
    s, c = surface(); trail(c, [px(*q) for q in PTS])
    x0, y0 = px(*PTS[0]); c.arc(x0, y0, 12, 0, 2*math.pi); col(c, WHITE); c.fill()
    text(c, "135 $ · 12 juin", x0+20, y0+46, 'xb', 30, ICE, 'l')
    cv.alpha_composite(to_img(s))
    xe, ye = px(*PTS[-1]); xp, yp = px(*PTS[-2]); ang = math.degrees(math.atan2(xe-xp, -(ye-yp)))
    put_rocket(cv, t, xe, ye, .42, angle=ang)
    gtw(cv, "+67 %", 360, 330, 170)
    def card(k, w, h):
        text(k, "ELON MUSK", 40, 46, 'sb', 24, ICE, 'l', 1, 3); text(k, "1er trillionnaire", 40, 104, 'a', 52, WHITE, 'l')
        text(k, "de l'histoire", 40, 150, 'xb', 26, SUBC, 'l')
    place(cv, spanel(470, 190, card), tilt_quad(700, 1010, 470, 190, ry=-.22, rx=-.08), 1, 16, .4)
    def d(c):
        sbar(c, .25); text(c, "EN 4 JOURS", 360, 470, 'sb', 32, HOT, 'c', 1, 8)
        text(c, "225 $ · 16 juin", xe+30, ye+40, 'xb', 30, ICE, 'l')
        capw(c, [("En", 0), ("quatre", 0), ("jours,", 0), ("l'action", 0), ("grimpe", 0), ("de", 0), ("67" + NB + "%.", 1)])
    return fin(cv, d, t)

FALL = [(0, 225.64), (.15, 200), (.3, 182), (.5, 150), (.7, 128), (1, 113.5)]
def k3():
    t = 14.0; cv = base(t, .75, False)
    X0, X1, Y0, Y1 = 160, 900, 1150, 420
    def px(u, p): return X0+u*(X1-X0), Y1+(Y0-Y1)*(230-p)/(230-100)
    s, c = surface()
    trail(c, [px(*q) for q in FALL], RED_)
    x0, y0 = px(*FALL[0]); c.arc(x0, y0, 12, 0, 2*math.pi); col(c, WHITE); c.fill(); text(c, "225 $", x0, y0-40, 'xb', 30, ICE)
    cv.alpha_composite(to_img(s))
    xe, ye = px(*FALL[-1]); put_rocket(cv, t, xe-170, ye-230, .44, angle=150, power=0.0, shake=0)
    # petites bouffées de fumée de moteur coupé
    s, c = surface(); rnd = random.Random(2)
    for k in range(12):
        x, y = xe-30+rnd.uniform(-60, 60)-k*12, ye-260-k*28; r = 20+k*4; col(c, 'B8BCC8', .18*(1-k/12)); c.arc(x, y, r, 0, 2*math.pi); c.fill()
    cv.alpha_composite(to_img(s).filter(ImageFilter.GaussianBlur(8)))
    gtw(cv, "−50 %", 540, 300, 190, bottom='FF8A95', glow=RED_)
    def d(c):
        sbar(c, .5); text(c, "EN 6 SEMAINES", 540, 450, 'sb', 32, 'FF8A95', 'c', 1, 8)
        text(c, "113 $ · fin juillet", xe-60, ye+50, 'xb', 30, ICE, 'r')
        capw(c, [("Puis", 0), ("tout", 0), ("s'effondre.", 1)])
    return fin(cv, d, t)

if __name__ == '__main__':
    ims = [k1(), k2(), k3()]
    for im, n in zip(ims, ('sx_da_k1_promesse', 'sx_da_k2_envol', 'sx_da_k3_chute')): im.save(f'/home/claude/spcx/{n}.png')
    sh = Image.new('RGB', (1680, 1000), 'white')
    for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
    sh.save('/home/claude/spcx/sheet.png')
