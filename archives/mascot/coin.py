"""Mister Coin : mascotte Actions_Benefices, redessinée en vectoriel (style cartoon années 30, bras « tuyau »), entièrement paramétrable.
draw(c, p) dessine le personnage dans un repère 700×900 (centre de la pièce en (350, 380)).
p : dict de paramètres d'animation (bouche, yeux, bras, jambes, chapeau, rebond…)."""
import math, cairo

INK = (0.20, 0.10, 0.03); GOLD = (0.98, 0.74, 0.16); GOLD_L = (1.0, 0.86, 0.38); GOLD_D = (0.88, 0.56, 0.07)
EDGE = (0.86, 0.55, 0.09); EDGE_D = (0.70, 0.40, 0.05); WHITE = (1, 1, 1); GLOVE_SH = (0.82, 0.84, 0.88)
MOUTH = (0.36, 0.08, 0.04); TONGUE = (0.93, 0.40, 0.36); BLUSH = (1.0, 0.55, 0.25); BROWN = (0.36, 0.20, 0.10); BROWN_L = (0.55, 0.32, 0.16)
HAT = (0.24, 0.18, 0.14); HAT_L = (0.36, 0.28, 0.22); BAND = (0.95, 0.62, 0.15); BOW = (0.85, 0.50, 0.12)
LW = 8.0
DEFAULT = dict(bounce=0.0, tilt=0.0, mouth_open=0.0, smile=1.0, blink=0.0, look=(0.15, -0.05), brow=0.0,
               arm_l='wave', arm_r='hip', wave=0.0, leg_phase=0.0, hat_tilt=0.0, hat_lift=0.0, squash=0.0, blush=1.0)

def ink(c, w=LW): c.set_source_rgb(*INK); c.set_line_width(w); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
def fill_ink(c, rgb, w=LW): c.set_source_rgb(*rgb); c.fill_preserve(); ink(c, w)
def ellipse(c, x, y, rx, ry, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2*math.pi); c.restore()
def star(c, x, y, r, rot=0.0):
    for k in range(10):
        a = rot-math.pi/2+k*math.pi/5; rr = r if k % 2 == 0 else r*.45
        (c.move_to if k == 0 else c.line_to)(x+rr*math.cos(a), y+rr*math.sin(a))
    c.close_path()

def tube(c, pts, w=24):
    """membre « tuyau » : courbe de Bézier épaisse avec contour"""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
    for lw, rgb in ((w+LW*2, INK), (w, GOLD)):
        c.move_to(x0, y0); c.curve_to(x1, y1, x2, y2, x3, y3); c.set_source_rgb(*rgb); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.move_to(x0, y0); c.curve_to(x1, y1, x2, y2, x3, y3); c.set_source_rgba(1, 1, 1, .25); c.set_line_width(w*.25); c.stroke()

def glove(c, x, y, ang, pose, s=1.0):
    """gant blanc de cartoon : 'open' (main ouverte), 'fist' (poing), 'point' (index tendu), 'thumb' (pouce levé)"""
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    # manchette
    c.new_path(); c.move_to(-26, -10); c.curve_to(-30, 6, -30, 18, -24, 26); c.line_to(24, 26); c.curve_to(30, 18, 30, 6, 26, -10); c.close_path(); fill_ink(c, WHITE, 6)
    if pose == 'open':
        for fx, a, l in ((-22, -.22, 52), (-7, -.07, 60), (8, .07, 60), (23, .2, 52)):
            c.save(); c.translate(fx, -44); c.rotate(a); c.new_path()
            c.move_to(-10.5, 8); c.line_to(-10.5, -l+10.5); c.arc(0, -l+10.5, 10.5, math.pi, 0); c.line_to(10.5, 8); c.close_path(); fill_ink(c, WHITE, 6); c.restore()
        c.new_path(); c.save(); c.translate(-36, -26); c.rotate(-.85); c.move_to(-10, 6); c.line_to(-10, -30); c.arc(0, -30, 10, math.pi, 0); c.line_to(10, 6); c.close_path(); c.restore(); fill_ink(c, WHITE, 6)
        c.new_path(); c.move_to(-34, -6); c.curve_to(-40, -40, -30, -58, 0, -58); c.curve_to(30, -58, 40, -40, 34, -6); c.close_path(); c.set_source_rgb(*WHITE); c.fill_preserve()
        c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
        for k in (-12, 0, 12):
            c.move_to(k, -42); c.line_to(k, -24); c.set_source_rgb(*INK); c.set_line_width(3.5); c.stroke()
    else:
        c.new_path(); ellipse(c, 0, -30, 40, 34); fill_ink(c, WHITE, 6)
        for k in range(4):                                  # phalanges repliées
            c.new_path(); ellipse(c, -24+k*16, -54, 10, 9); fill_ink(c, WHITE, 5)
        if pose == 'point':
            c.save(); c.translate(-6, -60); c.new_path(); c.move_to(-11, 4); c.line_to(-11, -58); c.arc(0, -58, 11, math.pi, 0); c.line_to(11, 4); c.close_path(); fill_ink(c, WHITE, 6); c.restore()
        if pose == 'thumb':
            c.save(); c.translate(-38, -40); c.rotate(-.25); c.new_path(); c.move_to(-11, 10); c.line_to(-11, -40); c.arc(0, -40, 11, math.pi, 0); c.line_to(11, 10); c.close_path(); fill_ink(c, WHITE, 6); c.restore()
        else:
            c.new_path(); c.save(); c.translate(-38, -30); c.rotate(.4); ellipse(c, 0, 0, 11, 20); c.restore(); fill_ink(c, WHITE, 6)
        c.move_to(-8, -20); c.curve_to(0, -12, 10, -12, 18, -20); c.set_source_rgb(*INK); c.set_line_width(3.5); c.stroke()
    c.restore()

def shoe(c, x, y, flip=1, ang=0.0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(flip, 1)
    c.new_path(); c.move_to(-34, 0); c.curve_to(-40, -34, 10, -40, 34, -22); c.curve_to(58, -14, 62, 8, 50, 14); c.line_to(-30, 14); c.curve_to(-38, 12, -38, 6, -34, 0); c.close_path(); fill_ink(c, BROWN, 7)
    c.new_path(); ellipse(c, 14, -20, 16, 7, -.2); c.set_source_rgba(1, 1, 1, .35); c.fill()
    c.move_to(-34, 10); c.line_to(52, 10); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    c.restore()

def hat(c, x, y, ang):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(.82, .82)
    c.new_path(); ellipse(c, 0, 0, 92, 22); fill_ink(c, HAT, 7)                       # bord
    c.new_path(); c.move_to(-56, -2); c.line_to(-62, -104); c.curve_to(-30, -116, 30, -116, 62, -104); c.line_to(56, -2); c.curve_to(30, 10, -30, 10, -56, -2); c.close_path(); fill_ink(c, HAT, 7)
    c.new_path(); c.move_to(-57, -14); c.line_to(-59, -40); c.curve_to(-30, -50, 30, -50, 59, -40); c.line_to(57, -14); c.curve_to(30, -4, -30, -4, -57, -14); c.close_path(); fill_ink(c, BAND, 6)
    c.new_path(); ellipse(c, 0, -106, 62, 13); fill_ink(c, HAT_L, 6)
    c.move_to(-40, -60); c.line_to(-44, -96); c.set_source_rgba(1, 1, 1, .18); c.set_line_width(8); c.stroke()
    c.restore()

def eye(c, x, y, blink, look, rot=0.0):
    rx, ry = 40, 64*(1-.92*blink)
    c.new_path(); ellipse(c, x, y, rx, max(ry, 5), rot); fill_ink(c, WHITE, 7)
    if blink < .7:
        c.save(); ellipse(c, x, y, rx-3, max(ry-3, 2), rot); c.clip()
        px, py = x+look[0]*18, y+look[1]*20+8
        c.new_path(); ellipse(c, px, py, 25, 42*(1-.7*blink)); c.set_source_rgb(*INK); c.fill()
        c.new_path(); c.move_to(px, py); c.line_to(px+30, py-40); c.line_to(px+6, py-48); c.close_path(); c.set_source_rgb(*WHITE); c.fill()   # « part de tarte »
        c.restore()

def mouth(c, x, y, op, smile):
    """op : 0 fermée -> 1 grande ouverte ; smile : 1 sourire, 0 neutre, -1 grimace"""
    w = 96; sy = smile*34
    if op < .08:
        c.move_to(x-w*.7, y-sy*.4); c.curve_to(x-w*.3, y+sy*.6, x+w*.3, y+sy*.6, x+w*.7, y-sy*.4); ink(c, 8)
        return
    top = y-6-12*op+(-sy*.25); bot = y+10+70*op*(.6+.4*max(0, smile))
    c.new_path(); c.move_to(x-w, top-sy*.5); c.curve_to(x-w*.4, top+sy*.2, x+w*.4, top+sy*.2, x+w, top-sy*.5)
    c.curve_to(x+w*.75, bot*.35+top*.65+20, x+w*.35, bot, x, bot); c.curve_to(x-w*.35, bot, x-w*.75, bot*.35+top*.65+20, x-w, top-sy*.5); c.close_path()
    path = c.copy_path(); c.set_source_rgb(*MOUTH); c.fill()
    c.save(); c.append_path(path); c.clip(); c.new_path(); ellipse(c, x+8, bot-4, w*.48, 30*op+8); c.set_source_rgb(*TONGUE); c.fill(); c.restore()
    c.append_path(path); ink(c, 8)
    for s in (-1, 1):   # commissures
        c.move_to(x+s*(w+4), top-sy*.5-8); c.curve_to(x+s*(w+14), top-sy*.5-2, x+s*(w+14), top-sy*.5+6, x+s*(w+6), top-sy*.5+12); ink(c, 6)

def draw(c, p=None):
    q = dict(DEFAULT); q.update(p or {}); p = q
    cx, cy, R = 340, 380-p['bounce'], 230; RX = R*.86
    sq = p['squash']
    # ombre au sol
    c.new_path(); ellipse(c, 360, 862, 170*(1-.15*p['bounce']/40), 22); c.set_source_rgba(.25, .1, 0, .28); c.fill()
    # jambes
    ph = p['leg_phase']
    for s, base_x in ((-1, 312), (1, 392)):
        sw = math.sin(ph+(0 if s < 0 else math.pi))*18
        hip = (base_x, cy+R*.82); foot = (base_x+s*18+sw, 832)
        tube(c, [hip, (hip[0]+s*10, hip[1]+70), (foot[0]-s*6, foot[1]-90), (foot[0], foot[1]-14)], 22)
        shoe(c, foot[0]+(14 if s > 0 else -10), foot[1], 1 if s > 0 else -1, .05*sw/18)
    c.save(); c.translate(cx, cy); c.rotate(p['tilt']); c.scale(1+sq*.06, 1-sq*.06); c.translate(-cx, -cy)
    # bras arrière-plan (gauche de l'image = bras droit du personnage)
    def arm(side, pose, wave):
        sx, sy_ = (cx-R*.92, cy+20) if side < 0 else (cx+R*.95, cy+40)
        if pose == 'wave':
            hx, hy = sx-62+math.sin(wave)*12, sy_-175+math.cos(wave*2)*6; tube(c, [(sx+6, sy_), (sx-70, sy_-10), (hx-6, hy+90), (hx, hy+40)], 24); glove(c, hx, hy+40, -.3+math.sin(wave)*.3, 'open', 1.05)
        elif pose == 'hip':
            hx, hy = sx-side*8, sy_+110; tube(c, [(sx-side*10, sy_), (sx+side*85, sy_+15), (hx+side*80, hy-10), (hx+side*20, hy)], 24); glove(c, hx+side*6, hy+2, side*1.9, 'fist', .95)
        elif pose == 'point':
            hx, hy = sx+side*150, sy_-40; tube(c, [(sx, sy_), (sx+side*60, sy_+10), (hx-side*50, hy+10), (hx, hy+6)], 24); glove(c, hx, hy+6, side*1.45, 'point', 1.0)
        elif pose == 'thumb':
            hx, hy = sx+side*110, sy_-90; tube(c, [(sx, sy_), (sx+side*70, sy_+20), (hx, hy+90), (hx, hy+40)], 24); glove(c, hx, hy+40, 0, 'thumb', 1.05)
        elif pose == 'down':
            hx, hy = sx+side*40, sy_+190; tube(c, [(sx, sy_), (sx+side*50, sy_+40), (hx+side*20, hy-80), (hx, hy-30)], 24); glove(c, hx, hy-30, side*.2+math.pi, 'fist', .95)
    # épaisseur de la pièce (tranche cannelée visible à droite)
    c.new_path(); ellipse(c, cx+34, cy+4, RX, R, -.1); fill_ink(c, EDGE)
    c.save(); ellipse(c, cx+34, cy+4, RX-4, R-4, -.1); c.clip()
    for k in range(-44, 45):
        a = k/44*math.pi/2; x = cx+34+RX*math.cos(a)-10; y = cy+4+R*math.sin(a)
        c.move_to(x, y); c.line_to(x+18, y); c.set_source_rgb(*EDGE_D); c.set_line_width(3); c.stroke()
    c.restore()
    # face
    c.new_path(); ellipse(c, cx, cy, RX, R, -.1)
    g = cairo.RadialGradient(cx-80, cy-110, 20, cx, cy, R*1.05); g.add_color_stop_rgb(0, *GOLD_L); g.add_color_stop_rgb(.55, *GOLD); g.add_color_stop_rgb(1, *GOLD_D)
    c.set_source(g); c.fill_preserve(); ink(c, 9)
    c.new_path(); ellipse(c, cx, cy, RX-30, R-32, -.1); c.set_source_rgba(*GOLD_D, .9); c.set_line_width(6); c.stroke()
    c.new_path(); ellipse(c, cx-2, cy-2, RX-33, R-35, -.1); c.set_source_rgba(1, .95, .7, .5); c.set_line_width(3); c.stroke()
    for k, a in enumerate((-2.25, -1.55, -.85, 2.55, .6)):   # étoiles en relief sur le bord
        star(c, cx+(RX-16)*math.cos(a), cy+(R-16)*math.sin(a), 14, a); c.set_source_rgb(*GOLD_D); c.fill_preserve(); c.set_source_rgba(*INK, .6); c.set_line_width(2.5); c.stroke()
    c.new_path(); ellipse(c, cx-95, cy-120, 46, 22, -.6); c.set_source_rgba(1, 1, 1, .28); c.fill()       # reflet
    # visage
    blink, look = p['blink'], p['look']
    eye(c, cx-58, cy-56, blink, look, -.1); eye(c, cx+44, cy-62, blink, look, .06)
    if p['brow']:
        for s in (-1, 1):
            c.move_to(cx+s*60-34, cy-140-p['brow']*s*0); c.line_to(cx+s*60+34, cy-140+p['brow']*14*s); ink(c, 9)
    c.move_to(cx-6, cy+12); c.curve_to(cx-30, cy+14, cx-30, cy+40, cx-4, cy+40); ink(c, 7)          # nez
    for s in (-1, 1):
        c.new_path(); ellipse(c, cx+s*104-8, cy+36, 26, 16); c.set_source_rgba(*BLUSH, .55*p['blush']); c.fill()
    mouth(c, cx-4, cy+86, p['mouth_open']*.85, p['smile'])
    # nœud papillon
    by = cy+168
    for s in (-1, 1):
        c.new_path(); c.move_to(cx+s*10, by); c.curve_to(cx+s*30, by-30, cx+s*62, by-34, cx+s*66, by-6); c.curve_to(cx+s*68, by+20, cx+s*36, by+28, cx+s*10, by+6); c.close_path(); fill_ink(c, BOW, 6)
        c.move_to(cx+s*24, by-8); c.line_to(cx+s*46, by-14); c.set_source_rgba(*INK, .7); c.set_line_width(3); c.stroke()
    c.new_path(); ellipse(c, cx, by, 16, 18); fill_ink(c, BOW, 6)
    # bras
    arm(-1, p['arm_l'], p['wave']); arm(1, p['arm_r'], p['wave'])
    # chapeau
    hat(c, cx+78, cy-R+26-p['hat_lift'], .26+p['hat_tilt'])
    c.restore()

if __name__ == '__main__':
    import sys
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 700, 900); c = cairo.Context(s)
    c.set_source_rgb(.85, .45, .1); c.paint()
    draw(c, dict(mouth_open=.7)); s.write_to_png(sys.argv[1] if len(sys.argv) > 1 else '/tmp/k08/coin.png')
