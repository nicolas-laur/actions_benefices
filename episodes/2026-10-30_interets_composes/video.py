"""Intérêts composés : 100 € par mois pendant 40 ans à 7 %. Colline cartoon animée ; graphique en courbes façon dessin animé
(capital et versements tracés année après année, aire des intérêts, bulles de valeurs) ; polices cartoon ; Mister Coin classique.
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
    sp = tw(c, ' ', 'fd', size); wd = [tw(c, w, 'fd', size)+(20 if k else 0) for w, k in words]
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
            if k: rr(c, x, yy-34, wd[i], 64, 14); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'fd', size, NAVY if hl in (GOLD, GOLD2) else WHITE, 'l', a)
            else: text(c, w, x, yy, 'fd', size, WHITE, 'l', a)
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

# ---------- polices cartoon ----------
import mty
mty.FAM['lg'] = ('Luckiest Guy', 0); mty.FAM['fd'] = ('Fredoka', 1); mty.FAM['fs'] = ('Fredoka SemiBold', 0)

# ---------- panneau : graphique en courbes ----------
CX0, CY0, CX1, CY1 = 50, 200, 1030, 958
PX0, PX1, PY0, PY1 = 196, 975, 372, 832                          # zone du tracé
VMAX = 280000
def gx(y): return PX0+(PX1-PX0)*y/40
def gy(v): return PY1-(PY1-PY0)*v/VMAX
def bubble(c, s, x, y, bg, fg, a=1, size=40, k=1.0, tail=True):
    """bulle de valeur façon BD, pointe vers (x, y)"""
    if a <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    w = tw(c, s, 'lg', size)+40; h = size*1.45; bx, by = -w/2, -h-22
    rr(c, bx+5, by+7, w, h, h/2); col(c, NAVY, .3*a); c.fill()
    rr(c, bx, by, w, h, h/2); col(c, bg, a); c.fill_preserve(); c.set_line_width(4); col(c, NAVY, a); c.stroke()
    if tail:
        c.move_to(-12, by+h-2); c.line_to(0, -4); c.line_to(12, by+h-2); c.close_path(); col(c, bg, a); c.fill_preserve(); c.set_line_width(4); col(c, NAVY, a); c.stroke()
        c.rectangle(-10, by+h-8, 20, 8); col(c, bg, a); c.fill()
    text(c, s, 0, by+h/2+2, 'lg', size, fg, 'c', a)
    c.restore()
def curve(c, f, y0, y1, step=.2):
    ys = np.arange(y0, y1+1e-6, step)
    if len(ys) == 0 or ys[-1] < y1: ys = np.append(ys, y1)
    c.move_to(gx(ys[0]), gy(f(ys[0])))
    for y in ys[1:]: c.line_to(gx(y), gy(f(y)))
    return ys
def dot(c, x, y, colr, a, r=13):
    c.arc(x, y, r+4, 0, 2*math.pi); col(c, NAVY, a); c.fill(); c.arc(x, y, r, 0, 2*math.pi); col(c, colr, a); c.fill()
    c.arc(x-r*.3, y-r*.35, r*.35, 0, 2*math.pi); col(c, WHITE, .7*a); c.fill()
def chart(c, t, a, Y, phase):
    """grille, aires (versé / intérêts), courbes épaisses à contour marine, tête de courbe animée"""
    for v in range(0, 250001, 50000):
        yy = gy(v); c.set_dash([2, 10] if v else []); c.move_to(PX0, yy); c.line_to(PX1, yy); c.set_line_width(3 if v == 0 else 2.5); c.set_line_cap(cairo.LINE_CAP_ROUND)
        col(c, NAVY if v == 0 else 'B8C2D6', a); c.stroke(); c.set_dash([])
        text(c, "0" if v == 0 else f"{v//1000} k€", PX0-18, yy, 'fd', 24, '5A6478', 'r', a)
    for k in (0, 10, 20, 30, 40):
        text(c, str(k), gx(k), PY1+34, 'fd', 26, '5A6478', 'c', a)
    text(c, "ANS", PX1, PY1+34, 'fd', 22, '5A6478', 'r', a*0)                # (l'année est déjà affichée en grand)
    if Y <= 0: return
    dim = 1-.55*ease((t-T['secret'])/.4)
    # aires
    curve(c, lambda y: 1200*y, 0, Y); c.line_to(gx(Y), gy(0)); c.line_to(gx(0), gy(0)); c.close_path(); col(c, 'CFE0FF', .9*a); c.fill()
    ys = curve(c, capital, 0, Y)
    for y in ys[::-1]: c.line_to(gx(y), gy(1200*y))
    c.close_path()
    pulse = 1.0
    if phase == 'pq' and t > T['parce']: pulse = .8+.2*math.sin((t-T['parce'])*7)
    col(c, 'FFE38A', .95*a*pulse*dim+.0); c.fill()
    # courbes
    for f_, colr, w_ in ((lambda y: 1200*y, BLUE, 9), (capital, GOLD, 13)):
        curve(c, f_, 0, Y); c.set_line_width(w_+8); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, NAVY, a); c.stroke()
        curve(c, f_, 0, Y); c.set_line_width(w_); col(c, colr, a); c.stroke()
    # étiquettes des aires
    if Y >= 36:                                                        # étiquettes posées seulement là où l'aire est déjà tracée
        ka = a*clamp((Y-36)/2)*(1-ease((t-T['secret'])/.3))
        text(c, "INTÉRÊTS", gx(33.5), gy((capital(33.5)+1200*33.5)/2)+4, 'lg', 30, 'B57F00', 'c', ka)
        text(c, "VERSÉ", gx(34.5), gy(1200*34.5/2)+2, 'lg', 24, '2F6FD6', 'c', ka)
    dot(c, gx(Y), gy(1200*Y), BLUE, a, 11); dot(c, gx(Y), gy(capital(Y)), GOLD, a, 14)
def years_panel_header(c, t, a, Y):
    text(c, "ANNÉE", CX0+46, CY0+56, 'fd', 26, '5A6478', 'l', a, 2)
    text(c, f"{int(Y+1e-6)}", CX0+46, CY0+118, 'lg', 76, NAVY, 'l', a)
    kp = a*(1-ease((t-T['pq']+.3)/.3))                                  # les pastilles laissent la place aux titres « Pourquoi ? » et « Le secret ? »
    pill(c, "100 €/MOIS", CX1-226, CY0+70, BLUE, WHITE, kp, 26, 'r'); pill(c, "7 %/AN", CX1-40, CY0+70, GREEN, WHITE, kp, 26, 'r')
def hud(c, t):
    """chiffre choc dès l'image 0"""
    pill(c, "100 € PAR MOIS", 540, 330, BLUE, WHITE, 1, 34)
    big(c, "249 000 €", 540, 515, 170, GOLD, 1, 1+.03*math.sin(t*3), edge=NAVY, lw=16)
    pill(c, "PENDANT 40 ANS", 540, 720, WHITE, NAVY, 1, 34)
    return 1-ease((t-(T['places']-.45))/.3)
def hud_card(c, t, with_card=True):
    ka = ease((t-T['places']+.1)/.35)
    if with_card: card(c, CX0, CY0, CX1-CX0, CY1-CY0, ka)
    a = ka
    text(c, "Hypothèse : 7 %/an, intérêts réinvestis · avant inflation et impôts", 540, CY1-30, 'fs', 23, '5A6478', 'c', a)
    if t < T['toi']-.12:
        Y = years_at(t); phase = 'pq' if T['pq'] <= t < T['secret'] else ('secret' if t >= T['secret'] else 'main')
        years_panel_header(c, t, a, Y)
        chart(c, t, a, Y, phase)
        # bulles « versé » et « capital »
        if T['b20'] <= t < T['b40']+.2:
            kv = ease((t-T['b20']-.6)/.3); bubble(c, "24 000 €", gx(20)+100, gy(24000)+78, BLUE, WHITE, a*kv, 28, lerp(.6, 1, back(kv)), tail=False)
        if T['a51'] <= t:
            k = t-T['a51']; ka5 = ease(k/.25)
            if t < T['b40']: bubble(c, "51 041 €", gx(20), gy(capital(20))-6, GOLD, NAVY, a*ka5, 44, lerp(1.5, 1, back(k/.45)))
            elif t < T['secret']: bubble(c, "51 041 €", gx(20), gy(capital(20))-6, 'FFF1B8', NAVY, a*.9*(1-ease((t-(T['secret']-.35))/.3)), 28)
        if T['b40']+1.3 <= t < T['pq']:
            kv = ease((t-T['b40']-1.3)/.3); bubble(c, "48 000 €", gx(40)-90, gy(48000)+82, BLUE, WHITE, a*kv, 28, lerp(.6, 1, back(kv)), tail=False)
        if T['b40'] <= t < T['a250']-.05 and years_at(t) >= 39.99:
            pu = .5+.5*math.sin(t*9); bubble(c, "?", gx(40), gy(capital(40))-6, PINK, WHITE, a, 50, 1+.08*pu)
        if t >= T['a250']-.05:
            k = t-T['a250']; ka5 = ease(k/.25)
            hb = 1-ease((t-T['pq']+.2)/.3)+ease((t-T['secret'])/.3)          # la bulle s'efface pendant « Pourquoi ? »
            bubble(c, "248 552 €", gx(40)-190, gy(capital(40))+40, GOLD, NAVY, a*ka5*clamp(hb), 52, lerp(1.5, 1, back(k/.45)), tail=False)
            if t >= T['a250']+.7 and t < T['pq']-.1:
                pill(c, "×4,9 EN 20 ANS", gx(20)+10, gy(160000), PINK, WHITE, a*ease((t-T['a250']-.7)/.3), 28); put_emoji('🚀', gx(20)+205, gy(160000)-4, 52, t-T['a250']-.9)
        if phase == 'pq':                                                  # pourquoi : les intérêts rapportent des intérêts
            kp = t-T['pq']; fq = 1-ease((t-(T['secret']-.35))/.3)          # tout s'efface avant « Le secret ? »
            c.push_group()
            big(c, "POURQUOI ?", 540, CY0+66, 64, PINK, ease(kp/.25), lerp(1.3, 1, back(kp/.4)), edge=NAVY, lw=8)
            steps = [("100 €", None), ("107 €", "+7 €"), ("114,49 €", "+7,49 €"), ("122,50 €", "+8,01 €")]
            for i, (v, gnr) in enumerate(steps):
                ti = T['parce']+.2+i*.55; k = ease((t-ti)/.3)
                if k <= 0: continue
                x = PX0+76+i*146; y = PY0+120
                rr(c, x-66, y-46, 132, 92, 22); col(c, 'FFF6D6', a*k); c.fill_preserve(); c.set_line_width(4); col(c, NAVY, a*k); c.stroke()
                text(c, f"AN {i}", x, y-22, 'fd', 20, '5A6478', 'c', a*k); text(c, v, x, y+14, 'lg', 26 if len(v) > 6 else 30, NAVY, 'c', a*k)
                if gnr: pill(c, gnr, x, y+76, GREEN, WHITE, a*k, 21)
                if i: c.move_to(x-82, y); c.line_to(x-70, y); c.set_line_width(4); col(c, NAVY, a*k); c.stroke()
            kb = t-T['boule']
            if kb > 0: pill(c, "L'EFFET BOULE DE NEIGE", PX0+305, PY0+272, GOLD, NAVY, ease(kb/.25), 32); put_emoji('❄️', PX0+52, PY0+268, 56, kb-.15, fq)
            c.pop_group_to_source(); c.paint_with_alpha(max(0, fq))
        if phase == 'secret':                                              # le secret : commencer tôt
            ks = t-T['secret']
            big(c, "LE SECRET ?", 540, CY0+66, 64, BLUE, ease(ks/.25), lerp(1.3, 1, back(ks/.4)), edge=NAVY, lw=8)
            kl = inout((t-T['secret']-.6)/1.2)
            if kl > 0:
                late = lambda y: capital(max(0, y-10))
                yl = 10+30*kl
                curve(c, late, 10, yl); c.set_line_width(19); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, NAVY, a); c.stroke()
                curve(c, late, 10, yl); c.set_line_width(11); col(c, '9AA4BA', a); c.stroke()
                dot(c, gx(yl), gy(late(yl)), '8A95AD', a, 12)
                if kl >= 1:
                    ke = ease((t-T['secret']-1.8)/.3)
                    bubble(c, "117 606 €", gx(40)-118, gy(capital(30))+92, 'E3E8F1', NAVY, a*ke, 40, tail=False)
                    text(c, "10 ANS PLUS TARD", gx(40)-118, gy(capital(30))-8, 'lg', 24, '5A6478', 'c', a*ke)
            kt = t-T['tot']
            if kt > 0:
                text(c, "COMMENCER TÔT", gx(27), gy(capital(34))-6, 'lg', 32, 'B57F00', 'c', ease(kt/.3))
                if kt > .9: pill(c, "×2,1 EN COMMENÇANT TÔT", PX0+10, PY0+40, GOLD, NAVY, ease((kt-.9)/.3), 26, 'l')
        return
    kt = t-T['toi']                                                        # question finale
    big(c, "ET TOI,", 540, CY0+230, 120, NAVY, ease(kt/.25), edge=WHITE, lw=2, shadow=False)
    big(c, "TU COMMENCES", 540, CY0+390, 96, PINK, ease((kt-.15)/.3), lerp(1.25, 1, back((kt-.15)/.4)), edge=NAVY, lw=8)
    big(c, "QUAND ?", 540, CY0+520, 110, PINK, ease((kt-.3)/.3), lerp(1.25, 1, back((kt-.3)/.4)), edge=NAVY, lw=8)
    al = ease((kt-.8)/.4)
    if al > 0:
        c.push_group(); logo_symbol(c, 408, CY0+640, 26); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 434, CY0+640, 'fd', 28, NAVY, 'l', al)
def hud_all(c, t):
    """le cadre reste en place ; seul le contenu passe en fondu vers la question finale"""
    FADE[0] = 1.0; edge = T['toi']
    if edge-.45 <= t < edge-.12:
        fo = 1-ease((t-(edge-.45))/.3)
        card(c, CX0, CY0, CX1-CX0, CY1-CY0, 1.0)
        FADE[0] = fo; c.push_group(); hud_card(c, t, False); c.pop_group_to_source(); c.paint_with_alpha(max(0, fo)); return
    hud_card(c, t)

# ---------- Mister Coin ----------
ENT, EXP, CONF, QUES = 'classique_parle_enthousiaste', 'classique_parle_explique', 'classique_parle_confidence', 'classique_parle_question'
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(0.0, [ENT, EXP], 'voix'), (11.55, CONF, 'voix'), (12.74, ENT, 'voix'), (18.4, EXP, 'voix'), (27.3, QUES, 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t): return CX_COIN, FEET+MC.hop_dy(t)

def frame(t):
    EMO.clear()
    cv = decor(t)
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
    ev = [(0.0, 'impact'), (T['places'], 'swish'), (T['a51'], 'impact'), (T['a51']+.05, 'coins'), (T['mais'], 'riser'),
          (T['b40'], 'whoosh'), (T['a250'], 'impact'), (T['a250']+.05, 'tadaa'), (T['a250']+.7, 'pop'), (T['pq'], 'swish'),
          (T['boule'], 'glint'), (T['secret'], 'swish'), (T['secret']+.6, 'draw'), (T['tot'], 'pop'), (T['tot']+.9, 'pop'), (T['toi'], 'swish'), (T['toi']+.8, 'paid')]
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
