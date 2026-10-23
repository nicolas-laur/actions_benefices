"""Netflix : test voix off (ElevenLabs, fournie par Nicolas), 33 s, promesse plein écran dès 0:00.
DA salle de projection, récit en « épisodes ». Aucun logo ni élément graphique de la marque."""
import sys, math, re, subprocess, os, functools
import numpy as np, cairo
from PIL import Image
_a = sys.argv; sys.argv = ['x', 'info']
sys.path.insert(0, '/home/claude/lvmh')
from lvmh import logo_symbol
sys.argv = _a
sys.path.insert(0, '/home/claude/nflx')
from nty import *
FPS = 60
P0, FX0, P1, FX1 = 63.38, 1.1562, 70.46, 1.1188
SH = 1000*FX0/P0; VAL = SH*P1/FX1
assert round(VAL) == 1149
DUR = 33.4
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def win(t, a, b, fi=.25, fo=.25):
    if t < a or t > b: return 0.0
    return min(1.0 if a <= 0 else ease((t-a)/fi), clamp((b-t)/fo))
NB = '\u00a0'

# ---------- sous-titres calés sur la voix (pauses mesurées sur le fichier) ----------
CAPS = [(0.00, "J'ai regardé ce que seraient devenus"), (1.45, "[1 000 €] placés dans Netflix"), (2.75, "il y a cinq ans."),
        (4.10, "Résultat :"), (5.10, "à peine [1 150 €]."), (7.40, "Pourtant,"), (8.03, "Netflix n'a jamais autant gagné :"),
        (10.09, "[13,6 milliards] de dollars"), (12.05, "de bénéfice,"), (12.97, "sur un an, en hausse de [33 %]."),
        (15.55, "Le problème ?"), (16.64, "En un an,"), (17.38, "l'action a perdu [43 %]."),
        (19.78, "Netflix a tenté de racheter"), (21.30, "[Warner Bros]…"), (22.22, "et a perdu la bataille"), (23.40, "face à [Paramount]."),
        (24.84, "Prochains résultats le [20 octobre]."), (27.04, "Alors, bonne affaire"), (28.36, "ou [piège] ?"),
        (29.34, "Dis-moi en commentaire :"), (30.58, "tu [achètes],"), (31.03, "tu [vends]"), (31.96, "ou tu [attends] ?")]
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k

# ---------- couches mises en cache ----------
@functools.lru_cache(maxsize=None)
def G(key):
    if key == 'hook': return glow(lambda c: text(c, "1 149 €", 540, 830, 'a', 300, CREAM), (60, 16), (1.6, 1.2))
    if key == 'm43': return glow(lambda c: text(c, "−43 %", 935, 1050, 'a', 120, CRIM, 'r'), (34, 10), (1.5, 1.0), False)
    if key == 'oct': return glow(lambda c: text(c, "20 OCTOBRE", 540, 675, 'a', 104, CRIM), (34, 10), (1.3, 1.0), False)
    if key == 'end1149': return glow(lambda c: text(c, "1 149 €", 725, 790, 'a', 84, CREAM, 'l'), (30, 10), (1.3, 1.0), False)
def lay(im, layer, a):
    if a <= 0: return
    if a >= .999: im.alpha_composite(layer); return
    l = layer.copy(); al = np.asarray(l.getchannel('A')).astype(np.float32)*a; l.putalpha(Image.fromarray(al.astype(np.uint8))); im.alpha_composite(l)

# ---------- scènes ----------
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()

def sA(c, t):
    tag(c, "1 000 € DANS NETFLIX IL Y A 5 ANS", 540, 420)
    text(c, "AUJOURD'HUI", 540, 560, 'sb', 34, SUB, 'c', 1, 8)
    text(c, "5 ans pour… +149 €", 540, 1040, 'xb', 54, WHITE)
    pill(c, "Tu achètes ? Réponds 1, 2 ou 3", 1160)

PATH = [(0, 1000), (.03, 1090), (.07, 640), (.11, 330), (.13, 307), (.18, 420), (.25, 520), (.33, 690), (.43, 804), (.5, 980), (.57, 1250),
        (.63, 1571), (.68, 1800), (.73, 2088), (.77, 1950), (.8, 1760), (.86, 1500), (.92, 1280), (1.0, 1149)]
CX0, CX1, CY0, CY1 = 150, 700, 1080, 640    # zone du graphique (valeur 0 en bas, 2 200 € en haut)
def px(u, v): return CX0+u*(CX1-CX0), CY0+(CY1-CY0)*v/2200
def sB(c, t):
    ep_card(c, 90, 430, 900, 790)
    ep_head(c, 140, 480, "ÉPISODE 1", "5 ans de montagnes russes")
    # mise de départ en pointillés
    y = px(0, 1000)[1]; c.set_dash([10, 10]); c.set_line_width(2); col(c, WHITE, .3); c.move_to(CX0, y); c.line_to(CX1+30, y); c.stroke(); c.set_dash([])
    text(c, "mise : 1 000 €", CX1+30, y+26, 'm', 22, SUB, 'r')
    for i, yr in enumerate(("2021", "2022", "2023", "2024", "2025", "2026")):
        text(c, yr, CX0+i/5*(CX1-CX0), CY0+40, 'm', 22, SUB, 'l' if i == 0 else ('r' if i == 5 else 'c'))
    u = ease((t-4.1)/1.25)
    pts = [p for p in PATH if p[0] <= u]
    if u > 0 and pts[-1][0] < u:   # point interpolé au bout du tracé
        j = len(pts); a0, b0 = PATH[j-1], PATH[j]; f = (u-a0[0])/(b0[0]-a0[0]); pts = pts+[(u, lerp(a0[1], b0[1], f))]
    if len(pts) > 1:
        c.move_to(*px(*pts[0]))
        for p in pts[1:]: c.line_to(*px(*p))
        c.line_to(px(pts[-1][0], 0)[0], CY0); c.line_to(CX0, CY0); c.close_path()
        g = cairo.LinearGradient(0, CY1, 0, CY0); g.add_color_stop_rgba(0, *hx(CRIM, .35)); g.add_color_stop_rgba(1, *hx(CRIM, 0)); c.set_source(g); c.fill()
        c.set_line_width(7); c.set_line_join(1); c.set_line_cap(1); col(c, CREAM); c.move_to(*px(*pts[0]))
        for p in pts[1:]: c.line_to(*px(*p))
        c.stroke(); c.arc(*px(*pts[-1]), 11, 0, 2*math.pi); c.fill()
    for uu, v, lab, up in ((.13, 307, "≈ 300 €", False), (.73, 2088, "≈ 2 100 €", True)):
        if u >= uu:
            a = ease((u-uu)/.08); x, y = px(uu, v); text(c, lab, x, y+(-40 if up else 44), 'xb', 30, GOLD if up else CRIM, 'c', a)
    if t >= 5.35:
        e = back((t-5.35)/.35); c.save(); c.translate(725, 790); c.scale(.6+.4*e, .6+.4*e); c.translate(-725, -790)
        text(c, "1 149 €", 725, 790, 'a', 84, CREAM, 'l'); c.restore()
    text(c, "valeur de tes 1 000 € · approx., change €/$ inclus", 540, 1180, 'm', 21, SUB, 'c', .8)

BARS = [(4.49, "2022"), (5.41, "2023"), (8.71, "2024"), (10.98, "2025"), (13.65, "12 mois")]
def ep2(c, t):
    ep_card(c, 90, 450, 900, 360)
    ep_head(c, 140, 500, "ÉPISODE 2", "Bénéfice record")
    for i, (v, l) in enumerate(BARS):
        g_ = ease((t-8.0-i*.3)/.4); h = v/13.65*170*g_; x = 145+i*92
        if h > 1: rr(c, x, 760-h, 62, h, 10); col(c, GOLD if i == 4 else '5A4A3A'); c.fill()
        text(c, l, x+31, 785, 'm', 22, SUB)
    if t >= 10.09:
        u = ease((t-10.09)/.6); v = 13.6*u; s = f"{v:.1f}".replace('.', ',')+" Md$"
        e = back((t-10.09)/.3); c.save(); c.translate(935, 640); c.scale(.7+.3*e, .7+.3*e); c.translate(-935, -640)
        text(c, s, 935, 640, 'a', 92, GOLD, 'r'); c.restore()
    if t >= 14.15: text(c, "+33 % sur un an", 935, 712, 'xb', 30, GREEN, 'r', ease((t-14.15)/.25))
FALL = [(0, .05), (.15, .0), (.3, .12), (.45, .2), (.6, .45), (.75, .62), (.88, .78), (1, .86)]
def ep3(c, t):
    ep_card(c, 90, 840, 900, 360)
    ep_head(c, 140, 890, "ÉPISODE 3", "L'action s'effondre")
    u = ease((t-17.3)/1.0)
    if u > 0:
        c.set_line_width(7); c.set_line_join(1); c.set_line_cap(1); col(c, CRIM); last = None
        for i, (uu, v) in enumerate(FALL):
            if uu > u:
                p0 = FALL[i-1]; f = (u-p0[0])/(uu-p0[0]); last = (lerp(p0[0], uu, f), lerp(p0[1], v, f)); c.line_to(150+last[0]*440, 1010+last[1]*150); break
            (c.move_to if i == 0 else c.line_to)(150+uu*440, 1010+v*150); last = (uu, v)
        c.stroke(); c.arc(150+last[0]*440, 1010+last[1]*150, 10, 0, 2*math.pi); c.fill()
    if t >= 16.64: text(c, "en un an", 935, 1135, 'xb', 30, SUB, 'r', ease((t-16.64)/.25))
    if t >= 18.31:
        e = back((t-18.31)/.3); c.save(); c.translate(935, 1050); c.scale(.6+.4*e, .6+.4*e); c.translate(-935, -1050)
        text(c, "−43 %", 935, 1050, 'a', 120, CRIM, 'r'); c.restore()

def sD(c, t):
    ep_card(c, 90, 450, 900, 770)
    ep_head(c, 140, 500, "ÉPISODE 4", "Le rachat raté")
    text(c, "WARNER BROS.", 540, 660, 'a', 110, CREAM)
    text(c, "studios, séries, catalogue : à vendre", 540, 735, 'm', 26, SUB)
    def row(y, name, status, sc, a, dim=False):
        def d(c):
            rr(c, 140, y, 800, 110, 20); col(c, WHITE, .05 if dim else .09); c.fill()
            text(c, name, 180, y+55, 'xb', 42, SUB if dim else WHITE, 'l')
            w = tw(c, status, 'xb', 28, 2)+40; rr(c, 900-w, y+30, w, 50, 10); col(c, sc, .25 if dim else 1); c.fill(); text(c, status, 900-w/2, y+55, 'xb', 28, WHITE, 'c', .6 if dim else 1, 2)
            if dim: c.set_line_width(4); col(c, SUB, .8); c.move_to(176, y+57); c.line_to(176+tw(c, name, 'xb', 42), y+57); c.stroke()
        grp(c, a, d, 30*(1-a))
    out = t >= 22.9
    row(800, "Netflix", "SE RETIRE" if out else "OFFRE", '6B5F5A' if out else GOLD, ease((t-19.95)/.3), out)
    row(935, "Paramount", "SURENCHÈRE", CRIM, ease((t-22.25)/.3))
    if t >= 23.47:
        e = back((t-23.47)/.3); c.save(); c.translate(540, 1130); c.scale(.6+.4*e, .6+.4*e); c.rotate(-.04*(1-ease((t-23.47)/.4))); c.translate(-540, -1130)
        w = tw(c, "ADJUGÉ À PARAMOUNT", 'a', 52, 3)+60; rr(c, 540-w/2, 1090, w, 80, 12); c.set_line_width(5); col(c, CRIM); c.stroke()
        text(c, "ADJUGÉ À PARAMOUNT", 540, 1130, 'a', 52, CRIM, 'c', 1, 3); c.restore()

def sE(c, t):
    ep_card(c, 90, 400, 900, 830)
    text(c, "ÉPISODE SUIVANT", 540, 465, 'sb', 28, SUB, 'c', 1, 6)
    text(c, "RÉSULTATS", 540, 565, 'a', 104, CREAM, 'c', ease((t-24.95)/.3))
    if t >= 25.75:
        e = back((t-25.75)/.3); c.save(); c.translate(540, 675); c.scale(.6+.4*e, .6+.4*e); c.translate(-540, -675)
        text(c, "20 OCTOBRE", 540, 675, 'a', 104, CRIM); c.restore()
    cx, cy, r = 540, 810, 52; u = clamp((t-24.84)/(DUR-24.84))
    c.set_line_width(9); col(c, WHITE, .15); c.arc(cx, cy, r, 0, 2*math.pi); c.stroke()
    c.set_line_cap(1); col(c, CREAM); c.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*u); c.stroke()
    text(c, str(max(1, 6-int(u*6))), cx, cy, 'a', 48, CREAM)
    for i, (n, s, t0) in enumerate((("1", "J'achète", 30.58), ("2", "Je vends", 31.03), ("3", "J'attends", 31.96))):
        if t < t0: continue
        y = 900+i*86; on = t0 <= t < (31.03, 31.96, 32.9)[i]; e = back((t-t0)/.3)
        def d(c, y=y, n=n, s=s, on=on):
            rr(c, 200, y, 680, 70, 16); col(c, CRIM if on else WHITE, .95 if on else .1); c.fill()
            if not on: rr(c, 200, y, 680, 70, 16); c.set_line_width(2); col(c, CRIM, .7); c.stroke()
            text(c, n, 250, y+35, 'a', 40, WHITE); text(c, s, 300, y+35, 'xb', 34, WHITE, 'l')
        c.save(); c.translate(540, y+35); c.scale(.8+.2*e, .8+.2*e); c.translate(-540, -y-35); d(c); c.restore()
    if t >= 29.3:
        a = ease((t-29.3)/.4)
        c.save(); c.push_group(); logo_symbol(c, 440, 1188, 50); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
        text(c, "Actions_Benefices", 475, 1188, 'b', 30, WHITE, 'l', a)

# ---------- image ----------
SCENES = [('A', 0.0, 4.1), ('B', 4.0, 7.45), ('C', 7.4, 19.75), ('D', 19.7, 24.9), ('E', 24.84, DUR+1)]
BEAM = [(0, 1.0), (4.0, 1.0), (4.4, .6), (24.8, .6), (25.3, .85), (DUR, .85)]
def frame(t):
    ba = float(np.interp(t, [p for p, _ in BEAM], [v for _, v in BEAM]))
    im = room().copy(); im.alpha_composite(beam(t, ba))
    s, c = surface()
    scrub(c, 250, clamp(t/DUR))
    aA = 1.0 if t < 3.85 else clamp((4.1-t)/.25)
    if aA > 0:
        lay(im, G('hook'), aA); grp(c, aA, lambda c: sA(c, t))
    aB = win(t, 4.0, 7.45, .3, .25)
    if aB > 0:
        grp(c, aB, lambda c: sB(c, t), 40*(1-ease((t-4.0)/.35)))
    aC = win(t, 7.4, 19.75, .3, .25)
    if aC > 0:
        tt_ = "POURTANT…" if t < 15.55 else "LE PARADOXE"; ta = ease((t-7.4)/.3) if t < 15.55 else ease((t-15.55)/.3)
        if t > 15.3 and t < 15.55: ta = clamp((15.55-t)/.25)
        grp(c, aC, lambda c: text(c, tt_, 540, 360, 'a', 96, CREAM, 'c', ta, 2))
        y2 = lerp(620, 450, inout((t-15.55)/.45)) if t >= 15.55 else 620
        sc_ = lerp(1.12, 1.0, inout((t-15.55)/.45)) if t >= 15.55 else 1.12
        def e2(c):
            c.translate(540, 630); c.scale(sc_, sc_); c.translate(-540, -630); ep2(c, t)
        grp(c, aC*ease((t-7.4)/.35), e2, y2-450+40*(1-ease((t-7.4)/.35)))
        if t >= 15.65:
            e = ease((t-15.65)/.45); grp(c, aC*e, lambda c: ep3(c, t), 140*(1-e))
    aD = win(t, 19.7, 24.9, .3, .25)
    if aD > 0:
        grp(c, aD, lambda c: text(c, "L'ENCHÈRE", 540, 360, 'a', 96, CREAM, 'c', 1, 2))
        grp(c, aD, lambda c: sD(c, t), 50*(1-ease((t-19.7)/.35)))
    aE = win(t, 24.84, DUR+1, .3, .3)
    if aE > 0:
        grp(c, aE, lambda c: sE(c, t), 50*(1-ease((t-24.84)/.35)))
    # halos sous le texte (une fois les éléments posés)
    if aB > 0 and t >= 5.35: lay(im, G('end1149'), aB*.8*ease((t-5.35)/.3))
    if aC > 0 and t >= 18.31: lay(im, G('m43'), aC*.9*ease((t-18.31)/.3))
    if aE > 0 and t >= 25.75: lay(im, G('oct'), aE*.7*ease((t-25.75)/.3))
    # sous-titres
    k = cap_at(t)
    if k is not None and t < DUR:
        st = CAPS[k][0]; a = 1.0 if st == 0 else ease((t-st)/.12)
        grp(c, a, lambda c: caption(c, parse(CAPS[k][1])), 14*(1-a))
    im.alpha_composite(to_img(s))
    return finish(im, t)

def events():
    return [(0.0, 'impact'), (0.0, 'proj'), (4.0, 'swish'), (4.1, 'tick'), (5.35, 'impact'),
            (7.4, 'swish')]+[(8.0+i*.3, 'pop') for i in range(5)]+[(10.09, 'impact'), (10.09, 'glint'), (14.15, 'pop'),
            (15.55, 'swish'), (17.35, 'crash'), (18.31, 'impact'),
            (19.7, 'swish'), (19.95, 'bid'), (22.25, 'bid'), (22.9, 'low'), (23.47, 'gavel'), (23.47, 'impact'),
            (24.84, 'swish'), (25.75, 'impact'), (29.3, 'pop'), (30.58, 'click'), (31.03, 'click'), (31.96, 'click')]

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs('/home/claude/nflx/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).save(f'/home/claude/nflx/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
