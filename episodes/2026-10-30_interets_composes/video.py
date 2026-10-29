"""Intérêts composés : 100 € par mois pendant 40 ans à 7 %. Colline cartoon, boule de neige de pièces d'or qui dévale le chemin
et grossit avec le capital ; carte façon dessin animé en haut (années, versements, capital, barre versé / intérêts) ; Mister Coin classique.
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
    rr(c, 540-bw/2+6, y0-50+8, bw, bh, 26); col(c, NAVY, .35*a); c.fill()
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, NAVY, .88*a); c.fill()
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
    c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s)
    if shadow: c.move_to(-ext.x_advance/2+6, size*.36+9); c.text_path(s); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, NAVY, .35*a); c.stroke_preserve(); c.fill()
    c.move_to(-ext.x_advance/2, size*.36); c.text_path(s); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, edge, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def pill(c, s, x, y, bg, fg=WHITE, a=1, size=24, align='c'):
    if a <= 0: return 0
    w = tw(c, s, 'xb', size, 1)+44; x0 = x-w/2 if align == 'c' else (x-w if align == 'r' else x)
    rr(c, x0+3, y-size*.95+5, w, size*1.9, size*.95); col(c, NAVY, .3*a); c.fill()
    rr(c, x0, y-size*.95, w, size*1.9, size*.95); col(c, bg, a); c.fill_preserve(); c.set_line_width(3); col(c, NAVY, a); c.stroke()
    text(c, s, x0+w/2, y, 'xb', size, fg, 'c', a, 1); return w
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

# ---------- décor : colline, nuages qui dérivent, soleil, pollen ----------
@functools.lru_cache(maxsize=1)
def decor_layers():
    im = Image.open(f'{D}/decors/colline.jpg').convert('RGB'); im = im.resize((int(im.width*1920/im.height), 1920), Image.LANCZOS)
    x0 = (im.width-W)//2; a = np.asarray(im.crop((x0, 0, x0+W, H))).astype(np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; yy = np.mgrid[0:H, 0:W][0]
    cl = ((R > 205) & (G > 210) & (B > 225) & (B >= R-4) & (yy < 760)).astype(np.uint8)
    cl = cv2.dilate(cl, np.ones((9, 9), np.uint8))
    small = cv2.resize(a.astype(np.uint8), (W//3, H//3)); ms = cv2.resize(cl, (W//3, H//3), interpolation=cv2.INTER_NEAREST)
    clean = cv2.inpaint(small, ms, 9, cv2.INPAINT_TELEA); clean = cv2.resize(clean, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    clean = cv2.GaussianBlur(clean, (0, 0), 3)
    m = cv2.GaussianBlur(cl.astype(np.float32), (0, 0), 2.5)
    sky = a*(1-m[..., None])+clean*m[..., None]                     # ciel sans nuages
    return a, sky, m
def decor(t):
    a, sky, m = decor_layers()
    dx = 7.0*t                                                         # les nuages dérivent doucement vers la droite
    M = np.float32([[1, 0, dx], [0, 1, 0]])
    cl = cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_CONSTANT); mm = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_CONSTANT)
    out = sky*(1-mm[..., None])+cl*mm[..., None]
    out = out*(1-m[..., None]*0)                                       # sol et collines inchangés hors des nuages
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay)
    for k in range(7):                                                 # rayons du soleil qui tournent lentement
        ang = -.25+k*.16+.05*math.sin(t*.5+k); L = 1500
        p = [(0, 560), (L*math.cos(ang-.035), 560+L*math.sin(ang-.035)), (L*math.cos(ang+.035), 560+L*math.sin(ang+.035))]
        d.polygon(p, fill=(255, 250, 215, int(26+14*math.sin(t*1.3+k*1.7))))
    lay = lay.filter(ImageFilter.GaussianBlur(18)); im.alpha_composite(lay)
    lay = Image.new('RGBA', (W, H), 0); d = ImageDraw.Draw(lay); rng = np.random.default_rng(7)
    for i in range(45):                                                # pollen doré qui flotte
        x0_, y0_, sp = rng.uniform(0, W), rng.uniform(700, 1900), rng.uniform(10, 30)
        x = (x0_+sp*t+25*math.sin(t*.7+i)) % W; y = y0_-12*t+18*math.sin(t*.9+i*1.3); y = (y-700) % 1200+700; r = rng.uniform(1.5, 3.5)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 245, 180, int(rng.uniform(90, 200))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(.6)))
    return im

# ---------- la boule de neige de pièces ----------
PATH = np.array([(745, 1060), (705, 1140), (620, 1195), (470, 1240), (330, 1290), (225, 1350), (185, 1420), (215, 1500), (330, 1560), (480, 1600), (630, 1626)], np.float32)
def _catmull(P, n=60):
    out = []
    for i in range(len(P)-1):
        p0, p1, p2, p3 = P[max(0, i-1)], P[i], P[i+1], P[min(len(P)-1, i+2)]
        for u in np.linspace(0, 1, n, endpoint=False):
            out.append(.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u**3))
    out.append(P[-1]); return np.array(out)
@functools.lru_cache(maxsize=1)
def path_arc():
    C = _catmull(PATH); seg = np.linalg.norm(np.diff(C, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); return C, s/s[-1]
def path_pt(u):
    C, s = path_arc(); return np.array([np.interp(u, s, C[:, 0]), np.interp(u, s, C[:, 1])])
def path_u(y):
    """position le long du chemin : ~1/3 du chemin à 20 ans (bien visible), au bout à 40 ans"""
    return .26*clamp(y/20)**1.1 if y <= 20 else .26+.74*inout((y-20)/20)
def persp(p): return lerp(.22, 1.0, clamp((p[1]-1060)/(1622-1060)))
def ball_state(t):
    y = years_at(t); u = path_u(y); p = path_pt(u)
    cap = capital(y); g = 34+230*math.sqrt(cap/capital(40)) if y > 0 else 0
    r = persp(p)*g
    if t > T['a51']: r *= 1+.10*math.exp(-(t-T['a51'])*6)*math.sin((t-T['a51'])*18)        # petit rebond aux révélations
    if t > T['a250']: r *= 1+.12*math.exp(-(t-T['a250'])*5)*math.sin((t-T['a250'])*16)
    return p, r, u
@functools.lru_cache(maxsize=1)
def roll_table():
    """angles de roulement intégrés le long du trajet (rouler à gauche fait tourner dans le plan, descendre fait basculer vers l'avant)"""
    ts = np.arange(0, DUR+.5, 1/240); az, ax = [0.0], [0.0]; prev = None
    for t in ts:
        p, r, _ = ball_state(t)
        if prev is not None and r > 1:
            d = p-prev; az.append(az[-1]+d[0]/r); ax.append(ax[-1]+d[1]/r*1.4)
        elif prev is not None: az.append(az[-1]); ax.append(ax[-1])
        prev = p
    return ts, np.array(az), np.array(ax)
@functools.lru_cache(maxsize=1)
def coin_pts():
    n = 70; i = np.arange(n)+.5; phi = np.arccos(1-2*i/n); th = math.pi*(1+5**.5)*i
    return np.stack([np.cos(th)*np.sin(phi), np.sin(th)*np.sin(phi), np.cos(phi)], 1)
def draw_ball(c, cx, cy, r, az, ax, t):
    if r < 2: return
    g = cairo.RadialGradient(cx-r*.35, cy-r*.4, r*.05, cx, cy, r*1.05)
    g.add_color_stop_rgb(0, *rgb('FFF0A0')); g.add_color_stop_rgb(.45, *rgb('F7C232')); g.add_color_stop_rgb(1, *rgb('B9750F'))
    c.arc(cx, cy, r, 0, 2*math.pi); c.set_source(g); c.fill()
    P = coin_pts().copy()
    ca, sa = math.cos(ax), math.sin(ax); y_, z_ = P[:, 1]*ca-P[:, 2]*sa, P[:, 1]*sa+P[:, 2]*ca; P[:, 1], P[:, 2] = y_, z_
    cz, sz = math.cos(az), math.sin(az); x_, y_ = P[:, 0]*cz-P[:, 1]*sz, P[:, 0]*sz+P[:, 1]*cz; P[:, 0], P[:, 1] = x_, y_
    order = np.argsort(P[:, 2]); rc = r*.26
    for k in order:
        x, y, z = P[k]
        if z < -.05: continue
        px, py = cx+x*r*.93, cy+y*r*.93; ang = math.atan2(y, x); fo = max(.18, z)
        c.save(); c.translate(px, py); c.rotate(ang); c.scale(fo, 1)
        sh = .55+.45*clamp(z+(-x-y)*.35)
        c.save(); c.translate(r*.025, r*.035); c.arc(0, 0, rc*1.03, 0, 2*math.pi); c.restore(); col(c, '5A3604', .35); c.fill()      # ombre portée de la pièce
        gg = cairo.RadialGradient(-rc*.3, -rc*.35, rc*.05, 0, 0, rc)
        gg.add_color_stop_rgb(0, *rgb('FFE98A', .85+.2*sh)); gg.add_color_stop_rgb(.7, *rgb('EDA51C', .8+.3*sh)); gg.add_color_stop_rgb(1, *rgb('B9750F', .8+.3*sh))
        c.arc(0, 0, rc, 0, 2*math.pi); c.set_source(gg); c.fill_preserve()
        c.restore(); c.set_line_width(max(1, r*.018)); col(c, '8A5208', .9); c.stroke()
        c.save(); c.translate(px, py); c.rotate(ang); c.scale(fo, 1)
        c.arc(0, 0, rc*.72, 0, 2*math.pi); c.restore(); c.set_line_width(max(.8, r*.012)); col(c, 'FFE58A', .55*sh); c.stroke()
    g2 = cairo.RadialGradient(cx-r*.38, cy-r*.42, 0, cx-r*.38, cy-r*.42, r*.5)        # reflet
    g2.add_color_stop_rgba(0, 1, 1, 1, .55); g2.add_color_stop_rgba(1, 1, 1, 1, 0)
    c.arc(cx, cy, r, 0, 2*math.pi); c.set_source(g2); c.fill()
    c.arc(cx, cy, r, 0, 2*math.pi); c.set_line_width(max(2, r*.035)); col(c, '5A3604', .95); c.stroke()
    for k in range(4):                                                 # éclats qui scintillent sur la boule
        ph = (t*.9+k*.27) % 1
        if ph < .25:
            a = math.sin(math.pi*ph/.25); ang = k*1.7+1; sx, sy = cx+math.cos(ang)*r*.6, cy+math.sin(ang)*r*.6; s = r*.18*a+3
            c.move_to(sx-s, sy); c.line_to(sx+s, sy); c.move_to(sx, sy-s); c.line_to(sx, sy+s); c.set_line_width(max(2, r*.02)); col(c, 'FFFFFF', .9*a); c.stroke()
def ball_layer(c, t):
    if t < T['places']-.05: return
    p, r, u = ball_state(t); ts, AZ, AX = roll_table(); i = min(len(ts)-1, int(t*240))
    cx, cy = p[0], p[1]-r*.9
    c.save(); c.translate(p[0], p[1]+r*.02); c.scale(1, .22); c.arc(0, 0, r*1.05, 0, 2*math.pi); c.restore()
    col(c, '1E3A10', .35); c.fill()
    draw_ball(c, cx, cy, r, AZ[i], AX[i], t)
    a = ease((t-T['places']+.05)/.3)
    return a

# ---------- carte du haut ----------
CX0, CY0, CX1, CY1 = 60, 210, 1020, 880
def hud(c, t):
    if t < T['places']-.15:                                            # chiffre choc dès l'image 0
        k = t
        pill(c, "100 € PAR MOIS", 540, 330, BLUE, WHITE, 1, 30)
        big(c, "249 000 €", 540, 520, 190, GOLD, 1, 1+.04*math.sin(t*3), edge=NAVY, lw=14)
        pill(c, "PENDANT 40 ANS", 540, 720, WHITE, NAVY, 1, 30)
        fo = 1-ease((t-(T['places']-.45))/.3)
        return fo
    return 1.0
def hud_card(c, t, with_card=True):
    ka = ease((t-T['places']+.1)/.35)
    if with_card: card(c, CX0, CY0, CX1-CX0, CY1-CY0, ka)
    a = ka
    text(c, "Hypothèse : 7 %/an, intérêts réinvestis · avant inflation et impôts", 540, CY1-34, 'b', 23, '5A6478', 'c', a)
    if t < T['pq']-.12:
        y = years_at(t)
        text(c, "ANNÉE", CX0+50, CY0+62, 'xb', 24, '5A6478', 'l', a, 3)
        big(c, f"{int(y+1e-6)}", CX0+50+60, CY0+140, 96, NAVY, a, 1, edge=WHITE, lw=2, shadow=False)
        pill(c, "100 €/MOIS", CX1-40, CY0+70, BLUE, WHITE, a, 22, 'r'); pill(c, "7 %/AN", CX1-40, CY0+136, GREEN, WHITE, a, 22, 'r')
        # frise des années
        fx0, fx1, fy = CX0+190, CX1-250, CY0+104
        rr(c, fx0, fy-9, fx1-fx0, 18, 9); col(c, 'E6EAF2', a); c.fill()
        rr(c, fx0, fy-9, max(18, (fx1-fx0)*y/40), 18, 9); col(c, GOLD, a); c.fill()
        for k in (0, 10, 20, 30, 40):
            xx = fx0+(fx1-fx0)*k/40; text(c, str(k), xx, fy+36, 'xb', 22, '5A6478', 'c', a)
        # versements
        text(c, "TU AS VERSÉ", CX0+50, CY0+240, 'xb', 28, '5A6478', 'l', a, 2)
        text(c, fmt(1200*y)+" €", CX1-50, CY0+242, 'a', 64, BLUE, 'r', a)
        # capital
        text(c, "TU AS", CX0+50, CY0+352, 'xb', 28, '5A6478', 'l', a, 2)
        if t < T['a51']-.05 or T['b40'] <= t < T['a250']-.05:
            pu = .5+.5*math.sin(t*9)
            big(c, "?", CX1-110, CY0+352, 110, PINK, a*(.75+.25*pu), 1+.06*pu, edge=NAVY, lw=8, shadow=False)
            cap_show, kk = None, 0
        else:
            st = T['a51'] if t < T['b40'] else T['a250']; val = capital(20) if t < T['b40'] else capital(40); kk = t-st
            big(c, fmt(val)+" €", CX1-50-tw(c, fmt(val)+" €", 'a', 110)/2, CY0+352, 110, GOLD, a, lerp(1.35, 1, back(kk/.45)), edge=NAVY, lw=10)
            cap_show = val
        # barre versé / intérêts (échelle : 249 000 €)
        bx0, bx1, by = CX0+50, CX1-50, CY0+470; BW = bx1-bx0; mx = capital(40)
        rr(c, bx0, by, BW, 56, 28); col(c, 'EEF1F7', a); c.fill()
        if t >= T['a51']:
            if t < T['b40']: v, i_, k_ = 24000, capital(20)-24000, inout((t-T['a51'])/.8)
            else:
                k2 = inout((t-T['a250'])/.9) if t >= T['a250'] else 0
                v, i_, k_ = lerp(24000, 48000, k2), lerp(capital(20)-24000, capital(40)-48000, k2), 1
            wv, wi = BW*v/mx*k_, BW*i_/mx*k_
            c.save(); rr(c, bx0, by, BW, 56, 28); c.clip()
            c.rectangle(bx0, by, wv, 56); col(c, BLUE, a); c.fill(); c.rectangle(bx0+wv, by, wi, 56); col(c, GOLD, a); c.fill()
            g = cairo.LinearGradient(0, by, 0, by+56); g.add_color_stop_rgba(0, 1, 1, 1, .35); g.add_color_stop_rgba(.5, 1, 1, 1, 0); c.rectangle(bx0, by, wv+wi, 56); c.set_source(g); c.fill(); c.restore()
            rr(c, bx0, by, BW, 56, 28); c.set_line_width(4); col(c, NAVY, a); c.stroke()
            kl = ease((t-(T['a51'] if t < T['b40'] else T['a250'])-.5)/.3)
            rr(c, bx0, by+80, 22, 22, 6); col(c, BLUE, a*kl); c.fill(); vt, it = (24000, capital(20)-24000) if t < T['b40'] else (48000, capital(40)-48000)      # légende : valeurs finales, jamais des valeurs intermédiaires
            text(c, f"VERSÉ {fmt(vt)} €", bx0+32, by+91, 'xb', 24, NAVY, 'l', a*kl, 1)
            rr(c, bx0+400, by+80, 22, 22, 6); col(c, GOLD, a*kl); c.fill(); text(c, f"INTÉRÊTS {fmt(it)} €", bx0+432, by+91, 'xb', 24, NAVY, 'l', a*kl, 1)
        else:
            rr(c, bx0, by, BW, 56, 28); c.set_line_width(4); col(c, NAVY, a); c.stroke()
        if t >= T['a250']+.7:
            pill(c, "×4,9 EN 20 ANS", CX0+50, CY0+404, PINK, WHITE, a*ease((t-T['a250']-.7)/.3), 22, 'l'); put_emoji('🚀', CX0+330, CY0+398, 44, t-T['a250']-.9)
        return
    if t < T['secret']-.12:                                            # pourquoi : les intérêts rapportent des intérêts
        kp = t-T['pq']
        big(c, "POURQUOI ?", 540, CY0+92, 84, PINK, ease(kp/.25), lerp(1.3, 1, back(kp/.4)), edge=NAVY, lw=8)
        steps = [("100 €", None), ("107 €", "+7 €"), ("114,49 €", "+7,49 €"), ("122,50 €", "+8,01 €")]
        for i, (v, gnr) in enumerate(steps):
            ti = T['parce']+.2+i*.55; k = ease((t-ti)/.3)
            if k <= 0: continue
            x = 540+(i-1.5)*232; y = CY0+300
            rr(c, x-90, y-62, 180, 124, 26); col(c, 'FFF6D6', a*k); c.fill_preserve(); c.set_line_width(4); col(c, NAVY, a*k); c.stroke()
            text(c, f"ANNÉE {i}", x, y-34, 'xb', 20, '5A6478', 'c', a*k, 1); text(c, v, x, y+14, 'a', 44, NAVY, 'c', a*k)
            if gnr: pill(c, gnr, x, y+94, GREEN, WHITE, a*k, 22)
            if i: c.move_to(x-138, y); c.line_to(x-98, y); c.set_line_width(5); col(c, NAVY, a*k); c.stroke(); c.move_to(x-108, y-10); c.line_to(x-98, y); c.line_to(x-108, y+10); c.stroke()
        text(c, "CHAQUE ANNÉE, TU GAGNES PLUS", 540, CY0+452, 'xb', 28, NAVY, 'c', ease((t-T['parce']-1.8)/.3), 1)
        text(c, "QUE L'ANNÉE D'AVANT", 540, CY0+490, 'xb', 28, NAVY, 'c', ease((t-T['parce']-1.8)/.3), 1)
        kb = t-T['boule']
        if kb > 0: pill(c, "L'EFFET BOULE DE NEIGE", 540, CY0+560, GOLD, NAVY, ease(kb/.25), 34); put_emoji('❄️', 870, CY0+556, 64, kb-.15)
        return
    if t < T['toi']-.12:                                               # le secret : commencer tôt
        ks = t-T['secret']
        big(c, "LE SECRET ?", 540, CY0+92, 84, BLUE, ease(ks/.25), lerp(1.3, 1, back(ks/.4)), edge=NAVY, lw=8)
        bx0, BW = CX0+50, CX1-CX0-100; mx = capital(40)
        for i, (lab, yrs, colr, t0) in enumerate((("COMMENCER 10 ANS PLUS TARD (30 ANS)", 30, GREY, T['secret']+.6), ("COMMENCER TÔT (40 ANS)", 40, GREEN, T['tot']))):
            k = ease((t-t0)/.3)
            if k <= 0: continue
            y = CY0+215+i*175; v = capital(yrs); w = BW*v/mx*inout((t-t0)/.8)
            text(c, lab, bx0, y, 'xb', 25, NAVY, 'l', a*k, 1)
            rr(c, bx0, y+30, BW, 60, 30); col(c, 'EEF1F7', a*k); c.fill()
            if w > 4: rr(c, bx0, y+30, max(60, w), 60, 30); col(c, colr, a*k); c.fill()
            rr(c, bx0, y+30, BW, 60, 30); c.set_line_width(4); col(c, NAVY, a*k); c.stroke()
            text(c, fmt(v)+" €", bx0+max(60, w)-20, y+61, 'a', 40, WHITE if w > 300 else NAVY, 'r' if w > 300 else 'l', a*ease((t-t0-.5)/.3))
        if t > T['tot']+.9: pill(c, "2 FOIS PLUS, SANS VERSER PLUS", 540, CY0+590, GOLD, NAVY, ease((t-T['tot']-.9)/.3), 26)
        return
    kt = t-T['toi']                                                    # question finale
    big(c, "ET TOI,", 540, CY0+180, 110, NAVY, ease(kt/.25), edge=WHITE, lw=2, shadow=False)
    big(c, "TU COMMENCES QUAND ?", 540, CY0+330, 92, PINK, ease((kt-.2)/.3), lerp(1.25, 1, back((kt-.2)/.4)), edge=NAVY, lw=8)
    al = ease((kt-.8)/.4)
    if al > 0:
        c.push_group(); logo_symbol(c, 420, CY0+480, 24); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 444, CY0+480, 'b', 24, NAVY, 'l', al)
def hud_all(c, t):
    """la carte change de contenu en fondu enchaîné (le cadre reste en place)"""
    FADE[0] = 1.0
    if t < T['places']-.15:
        fo = hud(c, t)
        if fo < 1:
            pass
        return fo
    fo = 1.0
    for edge in (T['pq'], T['secret'], T['toi']):
        if edge-.45 <= t < edge-.12: fo = 1-ease((t-(edge-.45))/.3)
    if fo < 1:
        card(c, CX0, CY0, CX1-CX0, CY1-CY0, ease((t-T['places']+.1)/.35))       # le cadre reste opaque, seul le contenu s'efface
        FADE[0] = fo; c.push_group(); hud_card(c, t, False); c.pop_group_to_source(); c.paint_with_alpha(max(0, fo)); return 1.0
    hud_card(c, t); return 1.0

# ---------- Mister Coin ----------
ENT, EXP, CONF, QUES = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_confidence', 'classique_parle_question'
CX_COIN, FEET = 230, 1700
MC = VeoCoin([(0.0, [ENT, EXP], 'voix'), (11.55, CONF, 'voix'), (12.74, ENT, 'voix'), (18.4, EXP, 'voix'), (27.3, QUES, 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t): return CX_COIN, FEET+MC.hop_dy(t)

def frame(t):
    EMO.clear()
    cv = decor(t)
    s, c = surface(); ball_layer(c, t); cv.alpha_composite(to_img(s))
    X, Y = coin_pos(t); rgb_, al = MC.layer(t, X, Y)
    a = np.asarray(cv.convert('RGB')).astype(np.float32)
    fx = MC.feet_x(al, Y) if Y > FEET-30 else X
    if fx is not None:
        k = 1/(1+max(0, FEET-Y)/150)
        m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (int(100*k)+1, int(15*k)+1), 0, 0, 360, .4*k, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
        a *= (1-m[..., None])
    a = a*(1-al[..., None])+rgb_*al[..., None]
    cv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface()
    if t < T['places']-.15:
        c.push_group(); fo = hud(c, t); c.pop_group_to_source(); c.paint_with_alpha(fo)
        if t > T['places']-.45: card(c, CX0, CY0, CX1-CX0, CY1-CY0, ease((t-T['places']+.45)/.3)*.0)
    else: hud_all(c, t)
    cv.alpha_composite(to_img(s))
    for e in EMO: draw_emoji(cv, *e)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.4 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        al_ *= 1-ease((t-(DUR-.7))/.3)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 2.0)

def events():
    ev = [(0.0, 'impact'), (T['places'], 'swish'), (T['places']+.2, 'roll'), (T['a51'], 'impact'), (T['a51']+.05, 'coins'), (T['mais'], 'riser'),
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
