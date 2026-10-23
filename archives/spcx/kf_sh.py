import sys; sys.path.insert(0, '/home/claude/spcx')
from kf import *
HOLD = [("Elon Musk", 848, "≈ 42 %"), ("Google", 81.9, "900 M$ en 2015"), ("Fidelity", 45.0, ""), ("Gigafund", 25.5, ""), ("Fonds saoudien", 22.9, ""), ("Nvidia", 18.3, "")]
def k4():
    t = 9.0; cv = base(t, .6, False)
    put_rocket(cv, t, 820, 520, .3, angle=35); darkspot(cv, 540, 820, 700, 560, .55)
    PX, PY, PW, PH = 90, 560, 900, 640; SC = 640/90
    def chart(k, w, h):
        text(k, "QUI POSSÈDE SPACEX ? · VALEUR AU 15 OCT.", 40, 46, 'sb', 22, ICE, 'l', 1, 2)
        for i, (n, v, sub) in enumerate(HOLD):
            y = 100+i*88
            text(k, n, 40, y+26, 'xb', 32, WHITE, 'l')
            if sub: text(k, sub, 40, y+60, 'm', 21, SUBC, 'l')
            bw = min(v*SC, 2000); x0 = 330
            if i == 0: continue
            rr(k, x0, y+6, bw*0.55, 44, 10); col(k, HOT if i == 1 else 'C9D6EA', .95); k.fill()
            text(k, f"{v:.0f} Md$".replace('.', ','), x0+bw*.55+14, y+28, 'xb', 28, HOT if i == 1 else ICE, 'l')
    place(cv, spanel(PW, PH, chart), [(PX, PY), (PX+PW, PY), (PX+PW, PY+PH), (PX, PY+PH)], 1, 24, .5)
    darken_band(cv, 1240, 1470, .55)
    s, c = surface()
    # la barre de Musk explose hors du panneau
    x0 = PX+330; y = PY+100; x1 = W+40
    for a_, e in ((.10, 26), (.2, 14), (.35, 6)): rr(c, x0-e, y+6-e, x1-x0+2*e, 44+2*e, 14); col(c, FIRE, a_); c.fill()
    g = cairo.LinearGradient(x0, 0, x1, 0); g.add_color_stop_rgb(0, *hx('FF6A1A')[:3]); g.add_color_stop_rgb(1, *hx(HOT)[:3]); rr(c, x0, y+6, x1-x0, 44, 10); c.set_source(g); c.fill()
    text(c, "≈ 850 Md$", x0+20, y+28, 'k', 36, INKB, 'l')
    sbar(c, .3); capw(c, [("Derrière", 0), ("Musk,", 0), ("Google", 1), ("a", 0), ("misé", 0), ("900", 0), ("millions.", 0)])
    cv.alpha_composite(to_img(s))
    gtw(cv, "×91", 540, 300, 170, top='FFFFFF', bottom='7CF5B0', glow=GRN)
    s2, c2 = surface(); text(c2, "POUR GOOGLE DEPUIS 2015", 540, 430, 'sb', 30, ICE, 'c', 1, 6); cv.alpha_composite(to_img(s2))
    return finish(cv, t, 4.0)
k4().save('/home/claude/spcx/sx_da_k4_actionnaires.png')
