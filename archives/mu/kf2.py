"""DA Micron v2 : la mémoire HBM (produit phare) en 3D, en héros devant le data center néon."""
import sys, random; sys.path.insert(0, '/home/claude/mu')
from kf import *
from PIL import ImageFilter

def product(path, size, blur=0, bright=1.0):
    im = Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im = Image.merge('RGBA', (*ImageEnhance.Contrast(im.convert('RGB')).enhance(1.18).split(), im.split()[3]))
    if bright != 1: im = Image.merge('RGBA', (*ImageEnhance.Brightness(im.convert('RGB')).enhance(bright).split(), im.split()[3]))
    return im
def put_product(cv, im, cx, cy):
    """pose la puce : halo de lumière dessous + reflet doux au sol + la puce"""
    w, h = im.size; x0, y0 = int(cx-w/2), int(cy-h/2)
    s, c = surface(); c.save(); c.translate(cx, cy+h*.18); c.scale(w*.55, h*.16)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, *hx('3FE7FF', .45)); g.add_color_stop_rgba(.5, *hx(VI, .18)); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.arc(0, 0, 1, 0, 2*math.pi); c.fill(); c.restore(); cv.alpha_composite(to_img(s))
    a = im.split()[3]; glow = Image.new('RGBA', im.size, (60, 200, 255, 0)); glow.putalpha(a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v*.45)))
    cv.alpha_composite(glow, (x0, y0)); cv.alpha_composite(im, (x0, y0))
def callout(c, x0, y0, x1, y1, label, sub, color=CY, side='l'):
    c.set_line_width(2.5); col(c, color, .9); c.move_to(x0, y0); c.line_to(x1, y1); c.line_to(x1+(-60 if side == 'l' else 60), y1); c.stroke()
    c.arc(x0, y0, 9, 0, 2*math.pi); col(c, color); c.fill(); c.arc(x0, y0, 18, 0, 2*math.pi); c.set_line_width(2); col(c, color, .4); c.stroke()
    xx = x1+(-70 if side == 'l' else 70)
    text(c, label, xx, y1-20, 'xb', 38, WHITE, 'r' if side == 'l' else 'l'); text(c, sub, xx, y1+22, 'm', 26, ICE, 'r' if side == 'l' else 'l')

def k1():
    cv = bg(.5, 7); darkspot(cv, 540, 700, 700, 700, .55)
    put_product(cv, product('/home/claude/mu/hbm_kf1.png', 860), 540, 560)
    gt(cv, "14 000 €", 540, 1010, 220)
    chip = cpanel(520, 100, lambda k, w, h: text(k, "1 000 € · IL Y A 5 ANS", w/2, h/2, 'xb', 32, ICE, 'c', 1, 3), r=50)
    place(cv, chip, tilt_quad(540, 220, 520, 100, ry=-.2, rx=-.1), 1, 16, .35)
    def d(c):
        bar(c, .02); pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1215, CY, INKB)
        cap(c, [("Quatorze", 0), ("mille" + NB + "euros.", 1)])
    return fin(cv, d, 0)

def k2():
    cv = bg(.45, 9); darkspot(cv, 540, 760, 720, 760, .6)
    S = 1000; cx, cy = 560, 840
    put_product(cv, product('/home/claude/mu/hbm_kf61.png', S), cx, cy)
    gt(cv, "MICRON", 540, 250, 150)
    def d(c):
        bar(c, .2)
        text(c, "LA MÉMOIRE DE L'IA", 540, 370, 'sb', 32, ICE, 'c', 1, 8)
        ox, oy = cx-S/2, cy-S/2
        callout(c, ox+.34*S, oy+.26*S, ox+.50*S, oy+.17*S, "HBM", "12 puces mémoire empilées", CY, 'r')
        callout(c, ox+.57*S, oy+.56*S, ox+.48*S, oy+.86*S, "Processeur IA", "la mémoire est collée au calcul", VI, 'l')
        cap(c, [("Elle", 0), ("fabrique", 0), ("la", 0), ("mémoire", 1), ("des", 0), ("serveurs", 0), ("de", 0), ("l'IA.", 0)])
    return fin(cv, d, 8)

def k3():
    cv = bg(.42, 9)
    put_product(cv, product('/home/claude/mu/hbm_kf1.png', 900, 10, .55), 540, 520); darkspot(cv, 540, 900, 700, 600, .5)
    PX, PY, PW, PH = 110, 640, 860, 560; BASE = 360; SC = 2.2
    def chart(k, w, h):
        text(k, "BÉNÉFICE NET ANNUEL · MILLIARDS $", 40, 46, 'sb', 24, ICE, 'l', 1, 2)
        k.set_line_width(2); col(k, WHITE, .3); k.move_to(40, BASE); k.line_to(w-40, BASE); k.stroke()
        for i, (y, v) in enumerate(NI[:4]):
            x = 60+i*160; hh = abs(v)*SC*6
            if v >= 0: rr(k, x, BASE-hh, 110, max(4, hh), 8); col(k, CY); k.fill(); text(k, f"{v:.1f}".replace('.', ','), x+55, BASE-hh-26, 'xb', 28, ICE)
            else: rr(k, x, BASE, 110, hh, 8); col(k, MG); k.fill(); text(k, f"−{abs(v):.1f}".replace('.', ','), x+55, BASE+hh+26, 'xb', 28, MG)
            text(k, y, x+55, h-40, 'm', 24, SUBC)
        text(k, "2026", 60+4*160+55, h-40, 'xb', 24, ICE)
    place(cv, cpanel(PW, PH, chart), [(PX, PY), (PX+PW, PY), (PX+PW, PY+PH), (PX, PY+PH)], 1, 26, .55)
    darken_band(cv, 1240, 1470, .6)
    s, c = surface()
    x = PX+60+4*160; bot = PY+BASE; top = -40
    for a_, e in ((.10, 40), (.2, 20), (.35, 8)): rr(c, x-e, top, 110+2*e, bot-top+e, 16); col(c, CY, a_); c.fill()
    gr = cairo.LinearGradient(0, top, 0, bot); gr.add_color_stop_rgb(0, 1, 1, 1); gr.add_color_stop_rgb(.3, *hx(CY)[:3]); gr.add_color_stop_rgb(1, *hx('0077A8')[:3])
    rr(c, x, top, 110, bot-top, 8); c.set_source(gr); c.fill(); burst(c, x+55, PY+4, 30, 230, 22, CY, .95, 7)
    bar(c, .35); cap(c, [("En", 0), ("un", 0), ("an,", 0), ("son", 0), ("bénéfice", 0), ("×10.", 1)])
    cv.alpha_composite(to_img(s))
    gt(cv, "85 Md$", 380, 330, 140); s2, c2 = surface(); text(c2, "×10 en un an", 380, 450, 'xb', 42, '3FD08A'); cv.alpha_composite(to_img(s2))
    return finish(cv, 12, 4.0)

ims = [k1(), k2(), k3()]
for im, n in zip(ims, ('mu2_da_k1_promesse', 'mu2_da_k2_hbm', 'mu2_da_k3_benefice')): im.save(f'/home/claude/mu/{n}.png')
sh = Image.new('RGB', (1680, 1000), 'white')
for i, im in enumerate(ims): sh.paste(im.resize((540, 960)), (20+i*550, 20))
sh.save('/home/claude/mu/sheet2.png')
