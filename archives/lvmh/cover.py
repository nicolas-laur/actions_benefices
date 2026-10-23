"""Couvertures « LVMH, TU ACHÈTES ? » (avec et sans emplacement logo officiel)."""
import sys, math
sys.argv = ['x', 'info']
import cairo
import lvmh as V
from lvmh import txt, caps, hair, glow, tw, src, SERIF, SANS, INK, INK_2, GOLD, GOLD_D, GOLD_L, BORDEAUX, IVORY_L, W, H

def cover(path, slot):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source_surface(V.paper(), 0, 0); c.paint()
    cx, cy = 540, 930
    glow(c, cx, cy, 520, GOLD_L, 0.45)
    for i, r in enumerate((250, 360, 470, 580, 690)):
        c.new_path(); c.save(); c.translate(cx, cy); c.scale(r*0.78, r*0.9); c.arc(0, 0, 1, 0, 2*math.pi); c.restore()
        src(c, GOLD, 0.30-0.04*i); c.set_line_width(1.2); c.stroke()
        a = math.radians([300, 25, 210, 140, 330][i])
        glow(c, cx+r*0.78*math.cos(a), cy+r*0.9*math.sin(a), 16, GOLD_L, 0.9)
        c.new_path(); c.arc(cx+r*0.78*math.cos(a), cy+r*0.9*math.sin(a), 4, 0, 2*math.pi); src(c, GOLD_D, 0.8); c.fill()
    y0 = 0
    if slot:
        c.new_path(); V.rr(c, 410, 380, 260, 260, 26); c.set_dash([14, 10]); src(c, INK_2, 0.8); c.set_line_width(3); c.stroke(); c.set_dash([])
        caps(c, "LOGO", 540, 510, 22, INK_2, 0.8); y0 = 150
    else:
        caps(c, "LE GÉANT DU LUXE", 540, 470, 26, GOLD_D)
        hair(c, 470, 515, 610, 515, GOLD, 1.4)
    txt(c, "LVMH,", 540, 700+y0*0.6, 190, INK, SERIF, True, False)
    txt(c, "tu achètes ?", 540, 880+y0*0.6, 140, GOLD_D, SERIF, False, True)
    yb = 1040+y0*0.6
    w = tw(c, "−57 % depuis son sommet", SERIF, 56, False, True)+90
    c.rectangle(540-w/2, yb, w, 104); src(c, BORDEAUX); c.fill()
    c.rectangle(540-w/2+8, yb+8, w-16, 88); src(c, IVORY_L, 0.55); c.set_line_width(1); c.stroke()
    txt(c, "−57 % depuis son sommet", 540, yb+52, 56, IVORY_L, SERIF, False, True)
    caps(c, "DE 904 € À 385 € L'ACTION", 540, yb+160, 24, INK_2)
    V.logo_symbol(c, 418, 1540, 74)
    txt(c, "Actions_Benefices", 470, 1540, 44, INK, SERIF, False, True, 'l')
    s.write_to_png(path)

cover('cover_lvmh.png', False)
cover('cover_lvmh_logo.png', True)
print('ok')
