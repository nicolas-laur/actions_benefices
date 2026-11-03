"""Ton iPhone ou des actions Apple ? Format court 15 s (accroche question). DA PEA/CTO : fond sombre étoilé, panneaux de verre,
grands chiffres lumineux ; un téléphone générique de 2007 (dessiné, aucune marque) qui finit au fond d'un tiroir, la tuile Apple
(autorisée par Nicolas) et un compteur qui monte de 399 € à ≈ 27 100 €. Mister Coin classique (3 clips).
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re
import numpy as np, cairo, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from veo_coin import VeoCoin
sys.path.insert(0, f'{ROOT}/archives/msft'); sys.path.insert(0, f'{ROOT}/archives/btc')
from bglass import gpanel, place, glow_text, tilt_quad, with_alpha
FPS = int(os.environ.get('FPS', 60)); NB = '\u00a0'
NAVY = '1E2A44'; WHITE = 'FFFFFF'; GOLD = 'F5B400'; BLUE = '3A86FF'; GREEN = '2DB36F'; PINK = 'FF5DA2'
CY = '35D6FF'; CY2 = 'A8EEFF'; GD = 'FFC24A'; GD2 = 'FFE3A0'; GR = '3FE08A'; RD = 'FF4057'; ICE = 'E8EEF8'; INK = '0B0E14'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u
def rgb(h, k=1.0, w=0.0):
    h = h.lstrip('#'); v = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]; return [min(1, x*k*(1-w)+w) for x in v]
def fmt(v, d=0): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')

# ---------- minutage (voix Thomas 15,12 s, pauses relevées au silencedetect) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(q=0.0, sorti=1.87, prix=3.83, auj=6.09, tiroir=6.83, etsi=8.59, apple=9.83, aurais=11.21, num=11.90, etoi=13.49, choisi=14.13, fin=15.12)
DUR = 15.9
VAL = 27100                                                           # 399 € → 89,4 actions → ≈ 27 100 € (voir sources.md)
CAPS = [(T['q'], "Tu te souviens du [premier iPhone] ?"), (T['sorti'], "Sorti en France en 2007, à [399 €]…"),
        (T['auj'], "Aujourd'hui, il traîne au fond d'un [tiroir]."), (T['etsi'], "Et si tu avais acheté des [actions Apple] à la place ?"),
        (T['aurais'], "Tu aurais environ [27 000 €]."), (T['etoi'], "Et toi, tu aurais [choisi quoi] ?")]
HL = {T['q']: BLUE, T['sorti']: GOLD, T['auj']: PINK, T['etsi']: BLUE, T['aurais']: GOLD, T['etoi']: GOLD}
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
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, INK, .72*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 14); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, NAVY if hl == GOLD else WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- outils ----------
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
EMO = []
def put_emoji(ch, x, y, size, k, a=1.0):
    if k > 0 and a > 0: EMO.append((ch, x, y, size, k, a))
def draw_emoji(cv, ch, x, y, size, k, a):
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    if a < 1: e = with_alpha(e, a)
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))
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
    rng = np.random.default_rng(3); return rng.uniform(0, W, 240), rng.uniform(0, H, 240), rng.uniform(.6, 1.7, 240), rng.uniform(.08, .35, 240), rng.uniform(0, 6.3, 240)
def background(t):
    cv = bg_base().copy(); s, c = surface()
    X, Y, R, A, P = stars()
    for x, y, r, a_, p in zip(X, Y, R, A, P):
        yy = (y-t*10) % H                                             # les étoiles montent doucement, comme le compteur
        c.arc(x, yy, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a_*(.7+.3*math.sin(t*1.3+p))); c.fill()
    warm = ease((t-T['aurais'])/1.5)                                   # halos froids qui se réchauffent quand la somme grimpe
    for k, (hx_, hy, rad) in enumerate(((300, 420, 520), (820, 1150, 560), (520, 1780, 480))):
        x = hx_+60*math.sin(t*.3+k*2); y = hy+40*math.cos(t*.25+k)
        tint = np.array(rgb(CY))*(1-warm)+np.array(rgb(GD))*warm
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *tint, .09); g.add_color_stop_rgba(1, *tint, 0)
        c.set_source(g); c.arc(x, y, rad, 0, 2*math.pi); c.fill()
    cv.alpha_composite(to_img(s)); return cv

# ---------- le téléphone générique de 2007 (dessiné : verre noir, cadre chromé, bouton rond, icônes génériques) ----------
ICONS = ['3FE08A', '35D6FF', 'FFC24A', 'FF5DA2', 'FF8A3D', '8E7CFF', 'E8EEF8', '3A86FF', 'FF4057', '2DB36F', 'FFD34D', '9AA7BD', '35D6FF', 'FF8A3D', '3FE08A', 'FFC24A']
def phone(c, x, y, s, rot=0.0, a=1.0, glow=0.0):
    if a <= 0: return
    w, h = 300, 560
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.push_group()
    if glow > 0:
        g = cairo.RadialGradient(0, 0, 0, 0, 0, 420); g.add_color_stop_rgba(0, *rgb(CY), .22*glow); g.add_color_stop_rgba(1, *rgb(CY), 0)
        c.set_source(g); c.arc(0, 0, 420, 0, 2*math.pi); c.fill()
    rr(c, -w/2+10, -h/2+18, w, h, 46); col(c, '000000', .45); c.fill()                  # ombre
    g = cairo.LinearGradient(-w/2, 0, w/2, 0)                                           # cadre chromé
    for u, k in ((0, 'C9CED8'), (.18, 'F4F6FA'), (.5, '9AA1AE'), (.82, 'EEF1F6'), (1, 'B9BFCA')): g.add_color_stop_rgb(u, *rgb(k))
    rr(c, -w/2, -h/2, w, h, 46); c.set_source(g); c.fill()
    rr(c, -w/2+9, -h/2+9, w-18, h-18, 40); col(c, '0A0B0E'); c.fill()                  # face noire
    rr(c, -118, -190, 236, 352, 6)                                                       # écran
    gs = cairo.LinearGradient(0, -190, 0, 162); gs.add_color_stop_rgb(0, *rgb('1B3A6B')); gs.add_color_stop_rgb(1, *rgb('0D1A33')); c.set_source(gs); c.fill()
    text(c, "9:41", 0, -172, 'b', 15, WHITE, 'c', .9)
    for i, colr in enumerate(ICONS):
        r_, k_ = divmod(i, 4); ix = -90+k_*60; iy = -128+r_*72
        gi = cairo.LinearGradient(0, iy-22, 0, iy+22); gi.add_color_stop_rgb(0, *rgb(colr, 1, .25)); gi.add_color_stop_rgb(1, *rgb(colr, .8))
        rr(c, ix-22, iy-22, 44, 44, 10); c.set_source(gi); c.fill()
        rr(c, ix-22, iy-22, 44, 20, 10); c.set_source_rgba(1, 1, 1, .18); c.fill()            # reflet des icônes de l'époque
    for k_ in range(4):                                                                   # barre du bas
        ix = -90+k_*60; rr(c, ix-22, 118, 44, 44, 10); col(c, ICONS[k_*3+1], .9); c.fill()
    c.move_to(-118, -190); c.line_to(118, -190); c.line_to(118, -40); c.curve_to(40, -80, -40, -120, -118, -60); c.close_path()
    c.set_source_rgba(1, 1, 1, .07); c.fill()                                             # reflet du verre
    c.arc(0, 224, 24, 0, 2*math.pi); col(c, '1A1C22'); c.fill_preserve(); c.set_line_width(2); col(c, '5A606B'); c.stroke()
    rr(c, -8, 216, 16, 16, 3); c.set_line_width(2); col(c, '8A909B'); c.stroke()            # bouton rond
    rr(c, -26, -238, 52, 7, 3.5); col(c, '2A2D35'); c.fill()                                # écouteur
    c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
def phone_state(t):
    """position du téléphone de 0 à 8 s : arrive, flotte, puis glisse et rétrécit dans le tiroir"""
    u0 = back(t/.55, 1.3)
    s = lerp(.7, 1.0, u0); y = 670; x = 540; rot = .05*math.sin(t*1.6); g = 1.0
    if t > T['prix']: x = lerp(540, 450, ease((t-T['prix'])/.5))                        # laisse la place à l'étiquette
    if t > T['auj']:
        k = ease((t-T['auj'])/.5); x = lerp(x, 540, k); y = lerp(670, 500, k); s = lerp(s, .62, k); g = 1-k
    if t > T['tiroir']:
        k = inout((t-T['tiroir'])/.75); y = lerp(500, 715, k); s = lerp(.62, .5, k); rot = lerp(rot, 1.35, k)
    return x, y, s, rot, g

# ---------- étiquette de prix qui se balance (amortie, comme une vraie étiquette au bout d'une ficelle) ----------
def price_tag(c, t, a, px, py):
    k = t-T['prix']
    if k <= 0: return
    ang = .5*math.exp(-k*2.2)*math.cos(k*7.5)-.18
    ax, ay = px+130, py-210                                                              # attache : coin haut droit du téléphone
    L = 170*ease(k/.25); tx, ty = ax+L*math.sin(ang)+70, ay+L*math.cos(ang)
    c.move_to(ax, ay); c.curve_to(ax+40, ay+30, tx-50, ty-60, tx, ty); c.set_line_width(3); col(c, 'D8C9A8', a); c.stroke()
    c.save(); c.translate(tx, ty); c.rotate(ang*.6-.12); sc = back(k/.35, 1.6); c.scale(sc, sc)
    c.move_to(-12, -10); c.line_to(150, -10); c.line_to(150, 120); c.line_to(-12, 120); c.line_to(-40, 55); c.close_path()
    c.set_source_rgba(0, 0, 0, .35*a); c.save(); c.translate(6, 8); c.fill(); c.restore()
    c.move_to(-12, -10); c.line_to(150, -10); c.line_to(150, 120); c.line_to(-12, 120); c.line_to(-40, 55); c.close_path()
    g = cairo.LinearGradient(0, -10, 0, 120); g.add_color_stop_rgb(0, *rgb('FFF4DA')); g.add_color_stop_rgb(1, *rgb('F2DFB0')); c.set_source(g)
    c.push_group(); c.fill(); c.arc(-14, 55, 9, 0, 2*math.pi); c.set_operator(cairo.OPERATOR_CLEAR); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a)
    text(c, "399 €", 62, 52, 'xb', 50, '7A1020', 'c', a)
    text(c, "29/11/2007", 62, 96, 'sb', 20, '7A1020', 'c', .8*a)
    c.restore()

# ---------- le tiroir (bois sombre, vue un peu plongeante) ----------
DX, DY, DW = 540, 735, 640                                                               # milieu de l'arête haute de la façade
def drawer_open(t):
    o = ease((t-T['auj']-.15)/.5)                                                         # ouverture
    cl = inout((t-(T['tiroir']+.8))/.45)                                                  # fermeture une fois le téléphone dedans
    return o*(1-cl)
def drawer(c, t, a, part):
    """part='back' : caisson et fond ; part='front' : façade et poignée"""
    o = drawer_open(t); depth = 150*o; rise = 60*(1-ease((t-T['auj'])/.45))
    y = DY+rise
    if part == 'back':
        c.move_to(DX-DW/2, y); c.line_to(DX-DW/2+50, y-depth); c.line_to(DX+DW/2-50, y-depth); c.line_to(DX+DW/2, y); c.close_path()
        g = cairo.LinearGradient(0, y-depth, 0, y); g.add_color_stop_rgb(0, *rgb('1C120C')); g.add_color_stop_rgb(1, *rgb('3A271A'))
        c.set_source(g); c.push_group(); c.fill_preserve(); c.pop_group_to_source(); c.paint_with_alpha(a)
        for xx in (DX-DW/2+25, DX+DW/2-25):                                                # côtés du caisson
            c.move_to(xx, y); c.line_to(xx+(25 if xx < DX else -25), y-depth); c.set_line_width(4); col(c, '5A3E2A', .8*a); c.stroke()
    else:
        fh = 190
        g = cairo.LinearGradient(0, y, 0, y+fh)
        for u, k in ((0, '7A5638'), (.08, '5E412B'), (1, '3E2A1B')): g.add_color_stop_rgb(u, *rgb(k))
        rr(c, DX-DW/2+8, y+12, DW, fh, 14); c.set_source_rgba(0, 0, 0, .45*a); c.fill()
        rr(c, DX-DW/2, y, DW, fh, 14); c.set_source(g); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a)
        for j in range(7):                                                                 # veinage du bois, discret
            yy = y+24+j*24; c.move_to(DX-DW/2+30, yy)
            for xx in range(0, DW-60, 40): c.line_to(DX-DW/2+30+xx, yy+4*math.sin(xx*.03+j))
            c.set_line_width(1.5); c.set_source_rgba(0, 0, 0, .12*a); c.stroke()
        rr(c, DX-90, y+fh/2-14, 180, 28, 14)                                                # poignée laiton
        gh = cairo.LinearGradient(0, y+fh/2-14, 0, y+fh/2+14); gh.add_color_stop_rgb(0, *rgb('FFE3A0')); gh.add_color_stop_rgb(1, *rgb('B8842E'))
        c.set_source(gh); c.push_group(); c.fill(); c.pop_group_to_source(); c.paint_with_alpha(a)
DUST = [(np.random.default_rng(5).uniform(-280, 280), np.random.default_rng(i).uniform(.5, 1.2), np.random.default_rng(i+50).uniform(-1, 1)) for i in range(14)]
def dust(c, t, a):
    k = t-(T['tiroir']+1.2)                                                                # petit nuage de poussière à la fermeture
    if not 0 < k < 1.2: return
    for i, (dx, sp, d) in enumerate(DUST):
        x = DX+dx+d*80*k; y = DY-10-60*k*sp; r = 10+26*k
        c.arc(x, y, r, 0, 2*math.pi); c.set_source_rgba(.85, .8, .72, .18*a*(1-k/1.2)); c.fill()

# ---------- tuile Apple ----------
@functools.lru_cache(maxsize=24)
def logo_tile(size):
    im = Image.open(f'{D}/logos/AAPL.png').convert('RGBA').resize((size, size), Image.LANCZOS)
    sh = Image.new('RGBA', (size+60, size+60), 0); m = Image.new('L', (size+60, size+60), 0)
    ImageDraw.Draw(m).rounded_rectangle((30, 40, 30+size, 40+size), radius=size*.22, fill=150)
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(12))); sh.alpha_composite(im, (30, 30)); return sh
def tile_state(t):
    k = t-T['apple']
    if k <= 0: return None
    s = back(k/.45, 1.6); x, y, sz = 540, 520, 230
    ka = t-T['aurais']
    if ka > 0: u = inout(ka/.5); y = lerp(520, 300, u); sz = lerp(230, 130, u)
    return x, y, sz*s

# ---------- scènes ----------
def sPhone(cv, c, t, a):
    """0 → 8,6 s : le premier iPhone, son prix, puis le tiroir"""
    x, y, s, rot, g = phone_state(t)
    k = t
    glow_text(cv, "LE PREMIER iPHONE", 540, 235, 92, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.55, a=a*ease(k/.25)*(1-ease((t-T['auj'])/.3)), scale=lerp(1.25, 1, back(k/.45, 1.3)), reflect=False)
    put_emoji('🤔', 905, 230, 64, t-.45, a*(1-ease((t-T['sorti'])/.3)))
    ks = t-T['sorti']
    if ks > 0:
        grp(c, a*ease(ks/.25)*(1-ease((t-T['auj'])/.3)), lambda c: gpill(c, "SORTI EN FRANCE LE 29/11/2007", 540, 335, GD, 30), dy=12*(1-ease(ks/.3)))
        put_emoji('🇫🇷', 540+300, 335, 52, ks-.35, a*(1-ease((t-T['auj'])/.3)))
    ka = t-T['auj']
    if ka > 0: grp(c, a*ease(ka/.25), lambda c: gpill(c, "19 ANS PLUS TARD", 540, 300, 'E8EEF8', 32), dy=12*(1-ease(ka/.3)))
    if t > T['auj']: drawer(c, t, a*ease(ka/.3), 'back')
    if t > T['tiroir']:                                                                     # le téléphone passe derrière la façade
        kd = inout((t-T['tiroir'])/.75); top = lerp(0, DY-150*drawer_open(t)+6, kd)
        c.save(); c.rectangle(0, top, W, DY-top); c.clip(); phone(c, x, y, s, rot, a, 0); c.restore()
    else: phone(c, x, y, s, rot, a, g)
    if t > T['auj']: drawer(c, t, a*ease(ka/.3), 'front'); dust(c, t, a)
    if t < T['auj']+.3: price_tag(c, t, a*(1-ease((t-T['auj'])/.3)), x, y)
def sApple(cv, c, t, a):
    """8,6 → 11,2 s : 399 € qui partent en actions Apple"""
    k = t-T['etsi']
    out = 1-ease((t-T['aurais'])/.35)
    glow_text(cv, "ET SI…", 540, 250, 96, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.25)*out, scale=lerp(1.3, 1, back(k/.4)), reflect=False)
    ts = tile_state(t)
    if k > .25 and (ts is None or t < T['apple']+.3):                                      # la somme file vers la tuile
        u = ease((k-.25)/.9); xx = 540; yy = lerp(860, 560, u)
        glow_text(cv, "399 €", xx, yy, 84, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6, a=a*ease((k-.25)/.2)*(1-ease((t-T['apple'])/.25)), reflect=False, scale=lerp(1, .6, ease((t-T['apple']+.3)/.4)))
    if ts and out > 0:
        x, y, sz = ts; im = logo_tile(max(8, int(sz)))
        cv.alpha_composite(with_alpha(im, a*out*ease((t-T['apple'])/.12)), (int(x-im.width/2), int(y-im.height/2)))
    kp = t-(T['apple']+.45)
    if kp > 0:
        grp(c, a*ease(kp/.25)*out, lambda c: gpill(c, "399 € = 89 ACTIONS APPLE", 540, 735, GD, 34), dy=12*(1-ease(kp/.3)))
        grp(c, a*ease((kp-.2)/.3)*out, lambda c: text(c, "au cours du 29/11/2007, divisions d'actions comprises", 540, 812, 'sb', 24, ICE, 'c', .75))
        put_emoji('📈', 760, 420, 70, kp-.1, a*out)
def val_at(t):
    u = clamp((t-(T['num']-.35))/1.25)                                                     # débit régulier, départ et arrivée en douceur
    u = u*u*(3-2*u)*.25+u*.75
    return 399+(VAL-399)*u
def sCount(cv, c, t, a):
    """11,2 → 13,5 s : le compteur grimpe jusqu'à ≈ 27 100 €"""
    k = t-T['aurais']; u = ease(k/.4)
    ts = tile_state(t)
    if ts:
        x, y, sz = ts; im = logo_tile(max(8, int(sz)))
        cv.alpha_composite(with_alpha(im, a), (int(x-im.width/2), int(y-im.height/2)))
    def d(kk, w, h):
        text(kk, "TES 399 € EN ACTIONS APPLE, AUJOURD'HUI", w/2, 56, 'xb', 26, ICE, 'c', .9, 2)
        kk.move_to(60, h-78); kk.line_to(w-60, h-78); kk.set_line_width(1.5); col(kk, WHITE, .14); kk.stroke()
        text(kk, "Clôture du 2/11/2026, taux BCE, hors dividendes", w/2, h-40, 'sb', 22, ICE, 'c', .65)
    place(cv, gp(880, 330, d, 'FFE9C0'), tilt_quad(540, 590+30*(1-u), 880, 330, rx=.05+.25*(1-u)), a*ease(k/.35), 18, .5)
    v = val_at(t); done = t > T['num']+.9
    if done: grp(c, a*ease((t-T['num']-.9)/.2), lambda c: text(c, "≈", 212, 598, 'xb', 96, GD2, 'c', 1))
    glow_text(cv, fmt(round(v/100)*100 if done else v)+" €", 555 if done else 540, 600, 120 if not done else 126,
              top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.75 if done else .55, a=a*ease(k/.25), reflect=False,
              scale=lerp(1.12, 1, back((t-T['num']-.9)/.35)) if done else 1.0)
    kp = t-(T['num']+1.05)
    if kp > 0: grp(c, a*ease(kp/.25), lambda c: gpill(c, "×68 EN 19 ANS", 540, 820, GR, 36), dy=12*(1-ease(kp/.3)))
    put_emoji('🤑', 700, 290, 70, t-(T['num']+1.0), a)
def sEnd(cv, c, t, a):
    """13,5 s → fin : la question, deux choix pour les commentaires"""
    k = t-T['etoi']
    glow_text(cv, "ET TOI ?", 540, 250, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a*ease(k/.25), scale=lerp(1.3, 1, back(k/.4)), reflect=False)
    for j, (emo, lab, colr) in enumerate((('📱', "L'IPHONE", CY), ('📈', "LES ACTIONS", GD))):
        kk = t-(T['etoi']+.25+j*.18)
        if kk <= 0: continue
        cx = 540+(-205 if j == 0 else 205); cy = 505
        beat = 1+.05*math.exp(-max(0, t-T['choisi'])*4)*math.sin(max(0, t-T['choisi'])*14) if t > T['choisi'] else 1
        def d(kq, w, h, lab=lab, colr=colr):
            text(kq, lab, w/2, h-52, 'xb', 34, WHITE, 'c', 1, 2)
            rr(kq, w/2-60, h-22, 120, 6, 3); col(kq, colr, .9); kq.fill()
        place(cv, gp(360, 300, d, 'CFE8FF' if j == 0 else 'FFE9C0'), tilt_quad(cx, cy+20*(1-ease(kk/.35)), 360*beat, 300*beat, ry=(.12 if j == 0 else -.12)*(1-ease(kk/.4))), a*ease(kk/.3), 18, .5)
        put_emoji(emo, cx, cy-40, 110, kk-.1, a)
    grp(c, a*ease((k-.7)/.3), lambda c: text(c, "Dis-le en commentaire", 540, 700, 'xb', 36, WHITE, 'c', 1))
    al = ease((t-T['choisi']-.4)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 790, 40); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 443, 790, 'b', 28, WHITE, 'l', al)
        text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 850, 'sb', 21, ICE, 'c', .65*al)
        text(c, "Les performances passées ne préjugent pas des performances futures.", 540, 880, 'sb', 21, ICE, 'c', .65*al)
    grp(c, a, lg)
SCENES = [(sPhone, 0.0, T['etsi']+.15), (sApple, T['etsi']-.1, T['aurais']+.4), (sCount, T['aurais']-.1, T['etoi']), (sEnd, T['etoi']-.1, DUR+1)]

# ---------- Mister Coin (3 clips : question, enthousiaste, question ; changements pendant les silences 8,07-8,59 et 13,02-13,49) ----------
QUES, ENT = 'classique_parle_question', 'classique_parle_enthousiaste'
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(0.0, QUES, 'voix'), (8.25, ENT, 'voix'), (13.2, QUES, 'voix')], voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t): return CX_COIN, FEET+MC.hop_dy(t)

def frame(t):
    EMO.clear()
    cv = background(t)
    s, c = surface()
    for fn, a0, b0 in SCENES:
        al = 1.0 if (a0 <= 0 and t < b0-.25) else (0.0 if t < a0 or t > b0 else min(ease((t-a0)/.3), clamp((b0-t)/.25)))
        if al > 0: fn(cv, c, t, al)
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
    if kk is not None and t < T['fin']+.35:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        al_ *= 1-ease((t-T['fin'])/.3)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'impact'), (.15, 'whoosh'), (T['sorti'], 'swish'), (T['sorti']+.35, 'pop'), (T['prix'], 'swish'), (T['prix']+.2, 'tick'),
          (T['auj'], 'swish'), (T['auj']+.2, 'whoosh'), (T['tiroir']+.1, 'whoosh'), (T['tiroir']+.72, 'thud'), (T['tiroir']+1.22, 'clack'),
          (T['etsi'], 'swish'), (T['etsi']+.3, 'riser'), (T['apple'], 'impact'), (T['apple']+.05, 'glint'), (T['apple']+.45, 'pop'), (T['apple']+.55, 'pop'),
          (T['aurais'], 'swish'), (T['num']-.35, 'count'), (T['num']+.9, 'impact'), (T['num']+.95, 'coins'), (T['num']+1.0, 'paid'), (T['num']+1.05, 'pop'),
          (T['etoi'], 'swish'), (T['etoi']+.25, 'pop'), (T['etoi']+.43, 'pop'), (T['choisi'], 'tick'), (T['choisi']+.4, 'glint')]
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
