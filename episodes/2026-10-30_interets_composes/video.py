"""Intérêts composés : 100 € par mois pendant 40 ans à 7 %. DA de la vidéo PEA/CTO (validée) : fond sombre étoilé, panneaux de verre
en perspective (courbes du capital et des versements), grands chiffres lumineux ; Mister Coin classique.
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from veo_coin import VeoCoin
FPS = int(os.environ.get('FPS', 60)); NB = ' '
NAVY = '1E2A44'; WHITE = 'FFFFFF'; GOLD = 'F5B400'; GOLD2 = 'FFD34D'; BLUE = '3A86FF'; GREEN = '2DB36F'; PINK = 'FF5DA2'; GREY = '8A94A8'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def rgb(h, k=1.0, w=0.0):
    h = h.lstrip('#'); v = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]; return [min(1, x*k*(1-w)+w) for x in v]

# ---------- minutage (voix Thomas 28,9 s) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(p1=0.0, lm=2.91, places=3.93, b20=7.21, a51=10.0, mais=11.81, b40=12.84, a250=16.10, pq=18.70, parce=19.34,
         boule=22.19, secret=23.90, tot=26.20, toi=27.60, end=29.6)
DUR = T['end']
CAPS = [(T['p1'], "Tu sais que plus tu es patient, plus tu deviens [riche] ?"), (T['lm'], "Laisse-moi [t'expliquer]."),
        (T['places'], "Tu places [100 € par mois], à 7 % par an."), (T['b20'], "Au bout de 20 ans, tu as versé [24 000 euros]…"),
        (T['a51'], "et tu en as [51 000] !"), (T['mais'], "Mais [attends la suite]."),
        (T['b40'], "Au bout de 40 ans, tu as versé [48 000 euros]…"), (T['a250'], "et tu en as près de [250 000] !"),
        (T['pq'], "[Pourquoi] ?"), (T['parce'], "Parce que tes intérêts rapportent à leur tour [des intérêts]."),
        (T['boule'], "C'est l'effet [boule de neige]."), (T['secret'], "Le secret, ce n'est pas de placer beaucoup."),
        (T['tot'], "C'est de [commencer tôt]."), (T['toi'], "Et toi, tu commences [quand] ?")]
HL = {T['p1']: GOLD, T['lm']: BLUE, T['places']: BLUE, T['b20']: BLUE, T['a51']: GOLD, T['mais']: PINK, T['b40']: BLUE, T['a250']: GOLD,
      T['pq']: PINK, T['parce']: GOLD, T['boule']: GOLD, T['secret']: BLUE, T['tot']: GREEN, T['toi']: PINK}
def parse(s):
    s = re.sub(r'(\d) (\d{3})', r'\1'+NB+r'\2', s)
    for a_ in (' :', ' ?', ' €', ' %', ' !'): s = s.replace(a_, NB+a_[1:])
    for m in re.findall(r'\[([^\]]+)\]', s): s = s.replace('['+m+']', '['+m.replace(' ', NB)+']')
    return [(tok.replace('[', '').replace(']', '').replace(NB, ' '), '[' in tok) for tok in s.split(' ')]
def cap_at(t):
    k = None
    for i, (a, _) in enumerate(CAPS):
        if t >= a: k = i
    return k
def caption(c, words, hl, y=1060, size=44, a=1):
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 760: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, '0B0E14', .72*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 14); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, NAVY if hl in (GOLD, GOLD2) else WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- outils ----------
def big(c, s, x, y, size, color, a=1, scale=1.0, tilt=0.0, edge=NAVY, lw=12, shadow=True):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(scale, scale)
    c.select_font_face('Luckiest Guy'); c.set_font_size(size); ext = c.text_extents(s)
    if shadow: c.move_to(-ext.x_advance/2+6, size*.36+9); c.text_path(s); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, NAVY, .35*a); c.stroke_preserve(); c.fill()
    c.move_to(-ext.x_advance/2, size*.36); c.text_path(s); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, edge, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def pill(c, s, x, y, bg, fg=WHITE, a=1, size=24, align='c'):
    if a <= 0: return 0
    w = tw(c, s, 'fd', size, 1)+44; x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    rr(c, x0+3, y-size*.95+5, w, size*1.9, size*.95); col(c, NAVY, .3*a); c.fill()
    rr(c, x0, y-size*.95, w, size*1.9, size*.95); col(c, bg, a); c.fill_preserve(); c.set_line_width(3); col(c, NAVY, a); c.stroke()
    text(c, s, x0+w/2, y, 'fd', size, fg, 'c', a, 1); return w
def card(c, x, y, w, h, a=1):
    """carte façon dessin animé : blanc, gros contour marine, ombre décalée nette"""
    if a <= 0: return
    rr(c, x+10, y+12, w, h, 38); col(c, NAVY, .30*a); c.fill()
    rr(c, x, y, w, h, 38); col(c, WHITE, .97*a); c.fill_preserve(); c.set_line_width(6); col(c, NAVY, a); c.stroke()
def fmt(v, d=0): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
EMO = []; FADE = [1.0]
def put_emoji(ch, x, y, size, k, a=1.0):
    a *= FADE[0]
    if k > 0 and a > 0: EMO.append((ch, x, y, size, k, a))
def draw_emoji(cv, ch, x, y, size, k, a):
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    if a < 1: e = e.copy(); e.putalpha(e.getchannel('A').point(lambda v: int(v*a)))
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))

# ---------- la finance ----------
R7 = (1.07)**(1/12)-1
def capital(years):
    n = years*12
    return 100*((1+R7)**n-1)/R7*(1+R7) if n > 0 else 0.0
def years_at(t):
    """frise des années : 0 → 20 pendant « Tu places… / Au bout de vingt ans », pause, puis 20 → 40 qui s'emballe"""
    if t < T['places']: return 0.0
    if t < T['mais']: return 20*inout((t-T['places'])/(T['b20']+.5-T['places']))
    return 20+20*clamp((t-T['b40']+.1)/1.25)**1.6

# ---------- DA « PEA/CTO » : fond sombre étoilé, panneaux de verre en perspective, grands chiffres lumineux ----------
sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from bglass import gpanel, place, glow_text, tilt_quad, darkspot, darken_band, surf, pil, with_alpha, lowblur
import nty
CY = '35D6FF'; CY2 = 'A8EEFF'; GD = 'FFC24A'; GD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4057'; ICE = 'E8EEF8'; INK = '0B0E14'
def grp(c, a, fn, dy=0):
    if a <= 0: return
    c.save(); c.translate(0, dy); c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(min(1, a)); c.restore()
def gp(w, h, draw, tint='CFE8FF'): return gpanel(w, h, draw, tint=tint, ta=.08, edge=.75)
def gpill(c, s, x, y, colr, size=34, a=1, fg=INK):
    w = tw(c, s, 'xb', size, 2)+60; rr(c, x-w/2, y-size*.95, w, size*1.9, size*.95); col(c, colr, a); c.fill(); text(c, s, x, y, 'xb', size, fg, 'c', a, 2)
@functools.lru_cache(maxsize=1)
def bg_base():
    s, c = surface()
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *rgb('04060B')); g.add_color_stop_rgb(.55, *rgb('070A12')); g.add_color_stop_rgb(1, *rgb('0B0F18')); c.set_source(g); c.paint()
    return to_img(s)
@functools.lru_cache(maxsize=1)
def stars():
    rng = np.random.default_rng(2); return rng.uniform(0, W, 260), rng.uniform(0, H, 260), rng.uniform(.6, 1.7, 260), rng.uniform(.08, .35, 260), rng.uniform(0, 6.3, 260)
def background(t):
    cv = bg_base().copy(); s, c = surface()
    X, Y, R, A, P = stars()
    for x, y, r, a_, p in zip(X, Y, R, A, P):                          # poussière d'étoiles qui scintille doucement
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a_*(.7+.3*math.sin(t*1.3+p))); c.fill()
    for k, (cx, cy, rad, colr) in enumerate(((300, 520, 520, GD), (820, 1250, 560, CY), (520, 1780, 480, GD))):      # halos colorés qui dérivent
        x = cx+60*math.sin(t*.25+k*2); y = cy+40*math.cos(t*.2+k)
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *rgb(colr), .10); g.add_color_stop_rgba(1, *rgb(colr), 0)
        c.set_source(g); c.arc(x, y, rad, 0, 2*math.pi); c.fill()
    cv.alpha_composite(to_img(s)); return cv

# ---------- scènes ----------
VMAX = 260000
def sHook(cv, c, t, a):
    glow_text(cv, "249 000 €", 540, 420, 190, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a, scale=lerp(1.25, 1, back(t/.45, 1.3)))
    grp(c, a*ease((t-.5)/.3), lambda c: text(c, "AVEC 100 € PAR MOIS", 540, 590, 'xb', 42, WHITE, 'c', 1, 4))
    grp(c, a*ease((t-.9)/.3), lambda c: gpill(c, "PENDANT 40 ANS", 540, 690, GD, 34))
    put_emoji('⏳', 540, 240, 100, t-.3, a)
def chart_panel(t):
    """panneau de verre : courbe du capital (or) et des versements (cyan), aire des intérêts, année et montants"""
    Y = years_at(t)
    def d(kk, w, h):
        X0, X1, Y0, Y1 = 150, w-60, 210, h-110
        gx = lambda y: X0+(X1-X0)*y/40; gy = lambda v: Y1-(Y1-Y0)*v/VMAX
        text(kk, "ANNÉE", 50, 58, 'sb', 24, ICE, 'l', .75, 3)
        text(kk, f"{int(Y+1e-6)}", 50, 120, 'a', 74, WHITE, 'l', 1)
        text(kk, "100 €/MOIS · 7 %/AN", w-50, 58, 'xb', 24, GD2, 'r', .9, 2)
        for v in range(0, 250001, 50000):
            yy = gy(v); kk.move_to(X0, yy); kk.line_to(X1, yy); kk.set_line_width(1.5 if v else 2); col(kk, 'FFFFFF', .10 if v else .35); kk.stroke()
            text(kk, "0" if v == 0 else f"{v//1000} k€", X0-16, yy, 'sb', 22, ICE, 'r', .7)
        for k in (0, 10, 20, 30, 40): text(kk, f"{k} ANS" if k == 40 else str(k), gx(k), Y1+36, 'sb', 22, ICE, 'c', .7)
        text(kk, "Hypothèse : 7 %/an, intérêts réinvestis · avant inflation et impôts", w/2, h-28, 'sb', 22, ICE, 'c', .65)
        if Y <= 0: return
        ys = np.append(np.arange(0, Y, .2), Y)
        # aire des intérêts (entre les deux courbes) puis aire des versements
        kk.move_to(gx(0), gy(0))
        for y in ys: kk.line_to(gx(y), gy(capital(y)))
        for y in ys[::-1]: kk.line_to(gx(y), gy(1200*y))
        kk.close_path(); g = cairo.LinearGradient(0, Y0, 0, Y1); g.add_color_stop_rgba(0, *rgb(GD), .38); g.add_color_stop_rgba(1, *rgb(GD), .10); kk.set_source(g); kk.fill()
        kk.move_to(gx(0), gy(0))
        for y in ys: kk.line_to(gx(y), gy(1200*y))
        kk.line_to(gx(Y), gy(0)); kk.close_path(); col(kk, CY, .14); kk.fill()
        for f_, colr, lw in ((lambda y: 1200*y, CY, 5), (capital, GD, 7)):
            for wdt, al in ((lw*3.2, .12), (lw*1.8, .22), (lw, 1.0)):
                kk.move_to(gx(0), gy(0))
                for y in ys: kk.line_to(gx(y), gy(f_(y)))
                kk.set_line_width(wdt); kk.set_line_cap(cairo.LINE_CAP_ROUND); kk.set_line_join(cairo.LINE_JOIN_ROUND); col(kk, colr if al < 1 else (CY2 if colr == CY else GD2), al); kk.stroke()
            kk.arc(gx(Y), gy(f_(Y)), lw*1.3, 0, 2*math.pi); col(kk, WHITE, 1); kk.fill()
        if Y >= 34:
            ka = clamp((Y-34)/3)
            text(kk, "INTÉRÊTS", gx(32), gy((capital(32)+1200*32)/2), 'xb', 26, GD2, 'c', ka, 3)
            text(kk, "VERSÉ", gx(33), gy(1200*33/2)+2, 'xb', 22, CY2, 'c', ka, 3)
        # repères aux révélations
        for yr, t0, cap in ((20, T['a51'], capital(20)), (40, T['a250'], capital(40))):
            if t >= t0:
                k = ease((t-t0)/.3); kk.set_dash([6, 8]); kk.move_to(gx(yr), gy(cap)); kk.line_to(gx(yr), Y1); kk.set_line_width(2); col(kk, GD2, .5*k); kk.stroke(); kk.set_dash([])
        return
    return gp(900, 720, d), Y
def money_lines(cv, c, t, a):
    """sous le panneau : versé (cyan) et capital (or, en grand chiffre lumineux) ; le capital reste caché jusqu'à la voix"""
    Y = years_at(t)
    grp(c, a, lambda c: (text(c, "TU AS VERSÉ", 120, 905, 'xb', 30, ICE, 'l', .85, 3), text(c, fmt(1200*Y)+" €", 960, 905, 'a', 58, CY2, 'r', 1)))
def sChart(cv, c, t, a):
    panel, Y = chart_panel(t)
    k = t-T['places']; e = ease(k/.45)
    place(cv, panel, tilt_quad(540, 500+40*(1-e), 900, 720, ry=-.10-.25*(1-e), rx=.05), a*e, 14, .55)
    # bulle de capital (grand chiffre lumineux) près de la tête de courbe
    if T['a51'] <= t < T['b40']:
        kk = t-T['a51']; glow_text(cv, "51 041 €", 640, 360, 110, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.75, a=a*ease(kk/.25)*clamp((T['b40']-t)/.25), scale=lerp(1.35, 1, back(kk/.45)))
    if T['b20'] <= t < T['b40']:
        grp(c, a*ease((t-T['b20']-.4)/.3)*clamp((T['b40']-t)/.25), lambda c: gpill(c, "VERSÉ : 24 000 €", 640, 460, CY, 28))
    if T['b40'] <= t < T['a250']-.05 and years_at(t) > 39.9:
        pu = .5+.5*math.sin(t*8); glow_text(cv, "?", 760, 330, 120, top='FFFFFF', bottom='FF9AA6', glow='FF4057', ga=.7, a=a*(.7+.3*pu))
    if T['b40']+1.2 <= t:
        grp(c, a*ease((t-T['b40']-1.2)/.3), lambda c: gpill(c, "VERSÉ : 48 000 €", 640, 460, CY, 28))
    if t >= T['a250']:
        kk = t-T['a250']; glow_text(cv, "248 552 €", 600, 350, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.8, a=a*ease(kk/.25), scale=lerp(1.4, 1, back(kk/.45)))
        if kk > .8: grp(c, a*ease((kk-.8)/.3), lambda c: gpill(c, "×4,9 EN 20 ANS", 600, 540, GR, 28))
def sWhy(cv, c, t, a):
    k = t-T['pq']
    glow_text(cv, "POURQUOI ?", 540, 290, 130, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.55, a=a*ease(k/.3), scale=lerp(1.25, 1, back(k/.4)))
    def d(kk, w, h):
        text(kk, "100 € PLACÉS À 7 % PAR AN", w/2, 60, 'xb', 28, WHITE, 'c', 1, 3)
        steps = [("100 €", None), ("107 €", "+7 €"), ("114,49 €", "+7,49 €"), ("122,50 €", "+8,01 €")]
        for i, (v, g_) in enumerate(steps):
            u = ease((t-T['parce']-.2-i*.55)/.35)
            if u <= 0: continue
            x = 120+i*(w-240)/3; y = 190
            grp(kk, u, lambda kk, x=x, y=y, v=v, i=i, g_=g_: (text(kk, f"AN {i}", x, y-58, 'sb', 22, ICE, 'c', .75, 3), text(kk, v, x, y, 'a', 52 if len(v) < 7 else 44, GD2 if i else WHITE, 'c', 1),
                                                                (gpill(kk, g_, x, y+70, GR, 24) if g_ else None)))
            if i: grp(kk, u, lambda kk, x=x, y=y: (kk.move_to(x-(w-240)/6-24, y), kk.line_to(x-(w-240)/6+10, y), kk.set_line_width(3), col(kk, ICE, .6), kk.stroke()))
        text(kk, "CHAQUE ANNÉE, LES INTÉRÊTS RAPPORTENT DES INTÉRÊTS", w/2, h-50, 'xb', 24, GD2, 'c', ease((t-T['parce']-1.9)/.3), 2)
    e = ease((k-.2)/.45)
    place(cv, gp(900, 360, d, 'FFE9C0'), tilt_quad(540, 560+40*(1-e), 900, 360, ry=.10+.25*(1-e), rx=.05), a*e, 14, .55)
    kb = t-T['boule']
    if kb > 0:
        glow_text(cv, "L'EFFET BOULE DE NEIGE", 540, 830, 82, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6, a=a*ease(kb/.25), scale=lerp(1.25, 1, back(kb/.4)))
        put_emoji('❄️', 540, 930, 80, kb-.2, a)
def sSecret(cv, c, t, a):
    k = t-T['secret']
    glow_text(cv, "LE SECRET ?", 540, 290, 120, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.55, a=a*ease(k/.3), scale=lerp(1.25, 1, back(k/.4)))
    def card(name, colr, tint, yrs, sub, t0):
        def d(kk, w, h):
            text(kk, name, w/2, 60, 'xb', 28, colr, 'c', 1, 3)
            YB, HB = 420, 200; X = w/2-65; WB = 130; u = ease((t-t0)/.9); v = capital(yrs)
            hb = HB*v/capital(40)*u; rr(kk, X, YB-hb, WB, hb, 12); col(kk, GD if colr == GD else CY2, .9); kk.fill()
            text(kk, fmt(v*u)+" €", w/2, YB-hb-42, 'a', 54, WHITE, 'c', 1)
            text(kk, sub, w/2, h-60, 'xb', 22, ICE, 'c', .85, 1)
        return gp(440, 520, d, tint)
    e1 = ease((k-.3)/.45); e2 = ease((t-T['tot']+.2)/.45)
    place(cv, card("10 ANS PLUS TARD", CY, 'CFE8FF', 30, "30 ANS DE VERSEMENTS", T['secret']+.5), tilt_quad(290, 620+40*(1-e1), 440, 520, ry=.16+.3*(1-e1), rx=.05), a*e1, 14, .55)
    if t > T['tot']-.25:
        place(cv, card("COMMENCER TÔT", GD, 'FFE9C0', 40, "40 ANS DE VERSEMENTS", T['tot']), tilt_quad(790, 620+40*(1-e2), 440, 520, ry=-.16-.3*(1-e2), rx=.05), a*e2, 14, .55)
    kd = t-T['tot']-.9
    if kd > 0: grp(c, a*ease(kd/.3), lambda c: gpill(c, "×2,1 EN COMMENÇANT 10 ANS PLUS TÔT", 540, 940, GR, 26))
def sCta(cv, c, t, a):
    k = t-T['toi']
    glow_text(cv, "ET TOI,", 540, 380, 130, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.3))
    glow_text(cv, "TU COMMENCES", 540, 540, 100, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a*ease((k-.15)/.3), scale=lerp(1.3, 1, back((k-.15)/.4)))
    glow_text(cv, "QUAND ?", 540, 680, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a*ease((k-.3)/.3), scale=lerp(1.3, 1, back((k-.3)/.4)))
    al = ease((k-.8)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 820, 46); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 445, 820, 'b', 30, WHITE, 'l', al)
    grp(c, a, lg)
SCENES = [(sHook, 0.0, T['places']), (sChart, T['places']-.1, T['pq']), (sWhy, T['pq']-.1, T['secret']), (sSecret, T['secret']-.1, T['toi']), (sCta, T['toi']-.1, DUR+1)]
def hypothese(c, t):
    if False:                         # rappel de l'hypothèse sous les cartes du « secret »
        text(c, "Hypothèse : 7 %/an · avant inflation et impôts", 540, 920, 'sb', 22, ICE, 'c', .6*ease((t-T['secret']-.2)/.4)*clamp((T['toi']-.1-t)/.25))

# ---------- Mister Coin ----------
ENT, EXP, CONF, QUES = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_confidence', 'classique_parle_question'
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(0.0, [ENT, EXP], 'voix'), (11.55, CONF, 'voix'), (12.74, ENT, 'voix'), (18.4, EXP, 'voix'), (27.3, QUES, 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t): return CX_COIN, FEET+MC.hop_dy(t)

def frame(t):
    EMO.clear(); FADE[0] = 1.0
    cv = background(t)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
    hypothese(c, t)
    cv.alpha_composite(to_img(s))
    for e in EMO: draw_emoji(cv, *e)
    X, Y = coin_pos(t); rgb_, al = MC.layer(t, X, Y)
    a = np.asarray(cv.convert('RGB')).astype(np.float32)
    fx = MC.feet_x(al, Y) if Y > FEET-30 else X
    if fx is not None:
        k = 1/(1+max(0, FEET-Y)/150)
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (int(100*k)+1, int(15*k)+1), 0, 0, 360, .55*k, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
        a *= (1-m[..., None])
    a = a*(1-al[..., None])+rgb_*al[..., None]
    cv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.4 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        al_ *= 1-ease((t-(DUR-.7))/.3)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'impact'), (T['places'], 'swish'), (T['a51'], 'impact'), (T['a51']+.05, 'coins'), (T['mais'], 'riser'),
          (T['b40'], 'whoosh'), (T['a250'], 'impact'), (T['a250']+.05, 'tadaa'), (T['a250']+.7, 'pop'), (T['pq'], 'swish'),
          (T['boule'], 'glint'), (T['secret'], 'swish'), (T['tot'], 'pop'), (T['tot']+.9, 'pop'), (T['toi'], 'swish'), (T['toi']+.8, 'paid')]
    ev += [(T['parce']+.2+i*.55, 'pop') for i in range(4)]
    ev += [(T['places']+(T['b20']+.5-T['places'])*k/20, 'tick') for k in range(0, 20, 2)]       # tic de la frise des années
    ev += [(h-.05, 'hop') for h in (MC._global_sequence() and MC.hops)]
    return sorted(ev)

def main():
    if sys.argv[1] == 'info': print(DUR); return
    if sys.argv[1] == 'png':
        os.makedirs(f'{D}/prev', exist_ok=True)
        for ts in sys.argv[2:]: frame(float(ts)).convert('RGB').save(f'{D}/prev/p_{ts}.png')
        return
    out, a_, b_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a_, min(b_, int(DUR*FPS))): ff.stdin.write(frame(i/FPS).convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print('done', int(DUR*FPS))
if __name__ == '__main__': main()
