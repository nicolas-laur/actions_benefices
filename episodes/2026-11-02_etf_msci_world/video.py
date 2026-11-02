"""C'est quoi un ETF MSCI World ? Format recherche (accroche question). DA PEA/CTO : globe en points qui s'allume pays par pays,
panneaux de verre, grands chiffres lumineux, logos des premières positions ; Mister Coin classique (3 clips).
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

# ---------- minutage (voix Thomas 29,0 s) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(q1=0.0, q2=2.85, achat=5.15, pays=9.12, logos=10.43, att=12.87, us=13.81, chine=15.66, frais=17.86, frais2=18.61, mille=21.2, envoie=25.65, end=29.6)
DUR = T['end']
CAPS = [(T['q1'], "C'est quoi, un [ETF MSCI World] ?"), (T['q2'], "Et pourquoi tout le monde en met dans son [PEA] ?"),
        (T['achat'], "En un seul achat, tu deviens actionnaire de [1 249 entreprises],"), (T['pays'], "dans [23 pays]."),
        (T['logos'], "[Nvidia], [Apple], [Microsoft]…"), (T['att'], "Mais [attention] :"), (T['us'], "[73 %] sont américaines,"),
        (T['chine'], "et il n'y a ni la [Chine] ni [l'Inde]."), (T['frais'], "Les [frais] ?"), (T['frais2'], "[2 à 4 €] par an pour 1 000 € placés."),
        (T['mille'], "Et 1 000 € placés il y a 5 ans valent aujourd'hui [1 771 €]."), (T['envoie'], "[Envoie-la] à quelqu'un qui pense que la bourse, c'est compliqué.")]
HL = {T['q1']: BLUE, T['q2']: GOLD, T['achat']: BLUE, T['pays']: GOLD, T['logos']: BLUE, T['att']: PINK, T['us']: GOLD, T['chine']: PINK,
      T['frais']: BLUE, T['frais2']: GREEN, T['mille']: GOLD, T['envoie']: GOLD}
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
# ---------- globe en points : rendu orthographique maison (texture des terres en points de la vidéo PEA/CTO) ----------
GDIR = f'{D}/globe'
DOTS = cv2.imread(f'{GDIR}/dots.png', cv2.IMREAD_GRAYSCALE).astype(np.float32)/255
PAYS = cv2.imread(f'{GDIR}/pays.png', cv2.IMREAD_GRAYSCALE)
GH, GW = DOTS.shape
DEVN = 23
def _centroids():
    lon = (np.arange(GW)+.5)/GW*360-180; lat = 90-(np.arange(GH)+.5)/GH*180; out = {}
    for k in list(range(1, DEVN+1))+[30, 31]:
        ys, xs = np.nonzero(PAYS == k)
        if len(xs) == 0: continue
        if k == 1: m = (lon[xs] > -130) & (lat[ys] < 50); ys, xs = ys[m], xs[m]      # États-Unis continentaux (sans l'Alaska)
        out[k] = (float(np.degrees(np.arctan2(np.sin(np.radians(lon[xs])).mean(), np.cos(np.radians(lon[xs])).mean()))), float(lat[ys].mean()))
    return out
CENT = _centroids()
LON0, LON1, LONUS, LONAS = -25.0, 232.0, 263.0, 457.0     # vers l'est : Europe, Asie, Pacifique, Amériques ; puis l'Asie pour la Chine et l'Inde
def view(t):
    """longitude face caméra (déroulée, toujours vers l'est) et inclinaison"""
    a, b = T['achat'], T['logos']-.2
    if t < a: lon = LON0+2*a-46*(1-ease(t/a))-2*(a-t)*ease(t/a)       # ouverture : le globe arrive en tournant puis ralentit
    elif t < b:
        u = (t-a)/(b-a); s0 = LON0+2*a; lon = s0+2*(t-a)+(LON1-s0-2*(b-a))*inout(u)
    elif t < 15.30: lon = LON1+(LONUS-LON1)*inout((t-b)/(T['us']-b))+6*max(0, t-T['us'])
    elif t < 16.75: s0 = LONUS+6*(15.30-T['us']); lon = s0+(LONAS-s0)*inout((t-15.30)/1.45)
    else: lon = LONAS+7*(t-16.75)*ease((t-16.75)/.6)
    if t < T['us']: tilt = 22+14*inout((t-a)/(T['us']-a))
    else: tilt = 36-10*inout((t-15.30)/1.45)
    return lon, tilt
def _unwrap(k):
    lonc = CENT[k][0]
    while lonc < LON0+5: lonc += 360
    return lonc
_ORDER = sorted(range(1, DEVN+1), key=_unwrap)                      # d'ouest en est, dans le sens de rotation
def _cross(k):
    for t in np.arange(T['achat'], T['logos'], .01):
        if view(t)[0] >= _unwrap(k)-(45 if k <= 2 else 32): return t
    return T['logos']-.4
def _lits():
    out, prev = {}, T['achat']+.1
    for k in _ORDER: prev = max(_cross(k), prev+.13); out[k] = prev
    return out
_L = _lits()
def lit_time(k): return _L[k]
LIT = {k: lit_time(k) for k in range(1, DEVN+1)}
def lit_count(t): return sum(1 for k in LIT if t >= LIT[k])
_GRID = {}
def _grid(S):
    if S not in _GRID:
        u = (np.arange(S)+.5)/S*2-1; X, Y = np.meshgrid(u, u); R2 = X*X+Y*Y
        _GRID[S] = (X, -Y, np.sqrt(np.clip(1-R2, 0, 1)), np.sqrt(R2))
    return _GRID[S]
def project(lon, lat, t, cx, cy, S):
    """position à l'écran d'un point (lon, lat) et s'il est visible"""
    lon0, tl = view(t); l = np.radians(lon-lon0); p = np.radians(lat); tr = np.radians(tl)
    x = np.cos(p)*np.sin(l); Y = np.sin(p); Z = np.cos(p)*np.cos(l)
    y = Y*np.cos(tr)-Z*np.sin(tr); z = Y*np.sin(tr)+Z*np.cos(tr)
    return cx+x*S/2, cy-y*S/2, z > 0
def country_state(t):
    """intensité d'allumage (cyan) par pays, or pour les États-Unis à « soixante-treize », rouge pour la Chine et l'Inde"""
    lit = np.zeros(256, np.float32); gold = np.zeros(256, np.float32); red = np.zeros(256, np.float32)
    for k, t0 in LIT.items(): lit[k] = ease((t-t0)/.35)
    us = ease((t-T['us'])/.45); gold[1] = us
    lit[2:DEVN+1] *= 1-.45*us
    red[30] = red[31] = ease((t-16.35)/.5)
    return lit, gold, red
def globe_rgba(t, S):
    X, Y, Z, R = _grid(S); lon0, tl = view(t); tr = np.radians(tl)
    Yw = Y*np.cos(tr)+Z*np.sin(tr); Zw = -Y*np.sin(tr)+Z*np.cos(tr)
    lat = np.degrees(np.arcsin(np.clip(Yw, -1, 1))); lon = (np.degrees(np.arctan2(X, Zw))+lon0+180) % 360
    mx = (lon/360*GW).astype(np.float32); my = ((90-lat)/180*GH).astype(np.float32)
    d = cv2.remap(DOTS, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    pid = cv2.remap(PAYS, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_WRAP)
    lit, gold, red = country_state(t); L, G, Rr = lit[pid], gold[pid], red[pid]
    shade = .35+.65*np.clip(-.45*X+.55*Y+.7*Z, 0, 1)
    base = np.stack([14+10*shade, 18+12*shade, 24+16*shade], -1)
    grey = np.array([120, 130, 146], np.float32)*(.45+.55*shade)[..., None]
    cy_ = np.array(rgb(CY))*255; gd_ = np.array(rgb(GD))*255; rd_ = np.array(rgb(RD))*255
    col = grey*(1-L[..., None]) + cy_*L[..., None]
    col = col*(1-G[..., None]) + gd_*G[..., None]
    col = col*(1-Rr[..., None]) + rd_*Rr[..., None]*.9
    on = np.clip(L+G+Rr, 0, 1)[..., None]
    img = base*(1-d[..., None]) + col*d[..., None]*(1+.45*on)
    bloom = cv2.GaussianBlur((col*d[..., None]*on).astype(np.float32), (0, 0), S/110)
    img = np.clip(img+bloom*1.5, 0, 255)
    a = np.clip((1-R)*S/2, 0, 1)
    return np.dstack([img, a*255]).astype(np.uint8)
def gplace(t):
    """position, taille, flou et opacité du globe selon la scène"""
    big = (540, 700, 820, 0.0, 1.0); low = (540, 1340, 1480, 7.0, .42)
    if t < T['frais']-.45: s = big
    else: u = inout((t-T['frais']+.45)/.8); s = tuple(lerp(a_, b_, u) for a_, b_ in zip(big, low))
    x, y, S, bl, al = s
    S *= lerp(1.22, 1, ease(t/1.2))*(1+.018*math.sin(t*1.25))        # arrivée en zoom, puis respiration lente
    y += 8*math.sin(t*.9)
    return x, y, int(S)//2*2, bl, al
def gc_points(a, b, n=40):
    """points d'un arc de grand cercle entre deux (lon, lat), légèrement soulevé au-dessus du globe"""
    def v(lo, la): lo, la = np.radians(lo), np.radians(la); return np.array([np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)])
    p, q = v(*a), v(*b); om = math.acos(float(np.clip(p @ q, -1, 1))) or 1e-6; out = []
    for i in range(n+1):
        u = i/n; w = (math.sin((1-u)*om)*p+math.sin(u*om)*q)/math.sin(om); lift = 1+.10*math.sin(math.pi*u)*min(1, om/1.2)
        out.append((math.degrees(math.atan2(w[1], w[0])), math.degrees(math.asin(np.clip(w[2], -1, 1))), lift))
    return out
def proj3(lon, lat, lift, t, cx, cy, S):
    lon0, tl = view(t); l = np.radians(lon-lon0); p = np.radians(lat); tr = np.radians(tl)
    x = np.cos(p)*np.sin(l)*lift; Y = np.sin(p)*lift; Z = np.cos(p)*np.cos(l)*lift
    y = Y*np.cos(tr)-Z*np.sin(tr); z = Y*np.sin(tr)+Z*np.cos(tr)
    vis = z > 0 or (x*x+y*y) > 1.0
    return cx+x*S/2, cy-y*S/2, vis
def orbit(c, t, cx, cy, S, al, front):
    """anneau d'orbite incliné, avec deux satellites lumineux ; la moitié arrière passe derrière le globe"""
    R_, ry, rot = S*.66, S*.66*.24, -.32
    for j, (ph, colr) in enumerate(((0.0, CY), (math.pi, GD))):
        th0 = t*.9+ph
        for k in range(36):
            th = th0-k*.035; x, y = R_*math.cos(th), ry*math.sin(th)
            if (math.sin(th) > 0) != front: continue
            X = cx+x*math.cos(rot)-y*math.sin(rot); Y = cy+x*math.sin(rot)+y*math.cos(rot)
            c.arc(X, Y, 5.5*(1-k/36)+.5, 0, 2*math.pi); col(c, colr, al*(1-k/36)*(.9 if k == 0 else .45)); c.fill()
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(R_, ry)
    c.arc(0, 0, 1, 0 if front else math.pi, math.pi if front else 2*math.pi); c.restore(); c.set_line_width(1.6); col(c, 'A8EEFF', .16*al); c.stroke()
def links(c, t, cx, cy, S, al):
    """arcs lumineux d'un pays allumé au suivant, et onde qui s'élargit à chaque allumage"""
    order = sorted(LIT, key=LIT.get)
    for i, k in enumerate(order):
        u = t-LIT[k]
        if u < 0: break
        if u < 1.0:
            x, y, vis = project(*CENT[k], t, cx, cy, S)
            if vis:
                r_ = 8+70*ease(u/1.0); c.arc(x, y, r_, 0, 2*math.pi); c.set_line_width(3); col(c, GD if k == 1 else CY, al*(1-u)*.8); c.stroke()
        if i and u < 1.6:
            pts = gc_points(CENT[order[i-1]], CENT[k]); m = int(len(pts)*ease(min(1, u/.45)))
            fade = 1-ease((u-.8)/.8)
            for a_, b_ in zip(pts[:m], pts[1:m]):
                x0, y0, v0 = proj3(*a_, t, cx, cy, S); x1, y1, v1 = proj3(*b_, t, cx, cy, S)
                if v0 and v1:
                    c.move_to(x0, y0); c.line_to(x1, y1); c.set_line_width(2.6); col(c, 'C8F6FF', al*fade*.85); c.stroke()
    for kk, t0, colr in ((1, T['us'], GD), (30, 16.35, RD), (31, 16.55, RD)):
        u = t-t0
        if 0 < u < 1.4:
            x, y, vis = project(*CENT[kk], t, cx, cy, S)
            if vis:
                for j in range(2):
                    uu = u-j*.3
                    if uu > 0: c.arc(x, y, 20+170*ease(uu/1.1), 0, 2*math.pi); c.set_line_width(4); col(c, colr, al*max(0, 1-uu/1.1)*.8); c.stroke()
def background(t):
    cv = bg_base().copy(); s, c = surface()
    X, Y, R, A, P = stars()
    for x, y, r, a_, p in zip(X, Y, R, A, P):
        xx = (x-t*6) % W                                              # les étoiles glissent doucement : le globe file dans l'espace
        c.arc(xx, y, r, 0, 2*math.pi); c.set_source_rgba(1, 1, 1, a_*(.7+.3*math.sin(t*1.3+p))); c.fill()
    for k, (hx_, hy, rad, colr) in enumerate(((300, 420, 520, GD), (820, 1250, 560, CY), (520, 1780, 480, GD))):      # halos colorés qui dérivent
        x = hx_+60*math.sin(t*.25+k*2); y = hy+40*math.cos(t*.2+k)
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *rgb(colr), .08); g.add_color_stop_rgba(1, *rgb(colr), 0)
        c.set_source(g); c.arc(x, y, rad, 0, 2*math.pi); c.fill()
    cx, cy, S, bl, al = gplace(t)
    tint = np.array(rgb(CY))*(1-ease((t-T['us'])/.5))+np.array(rgb(GD))*ease((t-T['us'])/.5)
    R1 = S*.5*1.18; g = cairo.RadialGradient(cx, cy, 0, cx, cy, R1)
    g.add_color_stop_rgba(0, *tint, 0); g.add_color_stop_rgba(.8, *tint, 0); g.add_color_stop_rgba(.85, *tint, .32*al); g.add_color_stop_rgba(1, *tint, 0)
    c.set_source(g); c.arc(cx, cy, R1, 0, 2*math.pi); c.fill()
    orbit(c, t, cx, cy, S, al, False)
    cv.alpha_composite(to_img(s))
    gi = Image.fromarray(globe_rgba(t, S), 'RGBA')
    if bl > .5: gi = lowblur(gi, bl, 2)
    if al < .999: gi = with_alpha(gi, al)
    cv.alpha_composite(gi, (int(cx-S/2), int(cy-S/2)))
    s2, c2 = surface(); orbit(c2, t, cx, cy, S, al, True)
    if bl < 1: links(c2, t, cx, cy, S, al)
    cv.alpha_composite(to_img(s2))
    return cv

# ---------- pluie de logos : d'autres entreprises de l'indice, pendant « mille deux cent quarante-neuf entreprises » ----------
RAIN_FILES = sorted(os.listdir(f'{D}/logos/pluie'))
def _rain():
    rng = np.random.default_rng(7); out = []
    for i, f in enumerate(rng.permutation(RAIN_FILES)):
        t0 = T['achat']+.35+i*.085+rng.uniform(0, .06)
        out.append(dict(f=str(f), t0=t0, x=rng.uniform(70, 1010), sz=int(rng.uniform(78, 112)), rot0=rng.uniform(-25, 25), vr=rng.uniform(-90, 90),
                        dur=rng.uniform(1.5, 2.1), drift=rng.uniform(-60, 60)))
    return out
RAIN = _rain()
@functools.lru_cache(maxsize=128)
def rain_tile(f, sz):
    im = Image.open(f'{D}/logos/pluie/{f}').convert('RGBA').resize((sz, sz), Image.LANCZOS)
    sh = Image.new('RGBA', (sz+30, sz+30), 0); m = Image.new('L', (sz+30, sz+30), 0)
    ImageDraw.Draw(m).rounded_rectangle((15, 20, 15+sz, 20+sz), radius=sz*.22, fill=140); sh.putalpha(m.filter(ImageFilter.GaussianBlur(7))); sh.alpha_composite(im, (15, 15)); return sh
def rain(cv, t, a):
    for r in RAIN:
        u = (t-r['t0'])/r['dur']
        if not 0 <= u <= 1: continue
        y = -80+1180*u*u+120*u; x = r['x']+r['drift']*u
        al = a*min(1, u/.08)*(1-ease((y-900)/220))
        band = clamp(1-abs(y-320)/170)                                  # en traversant les compteurs, les logos s'effacent presque
        al *= 1-.82*band
        if al <= .01: continue
        im = rain_tile(r['f'], r['sz']).rotate(r['rot0']+r['vr']*u*r['dur'], resample=Image.BICUBIC, expand=True)
        cv.alpha_composite(with_alpha(im, al), (int(x-im.width/2), int(y-im.height/2)))

# ---------- logos des premières positions (poids au 30/09/2026, fiche MSCI) ----------
TOP = [('NVDA', 'Nvidia', '5,8 %'), ('AAPL', 'Apple', '5,4 %'), ('MSFT', 'Microsoft', '4,0 %'), ('GOOGL', 'Alphabet', '4,0 %'), ('AMZN', 'Amazon', '2,7 %'),
       ('META', 'Meta', '1,8 %'), ('AVGO', 'Broadcom', '1,8 %'), ('MU', 'Micron', '1,3 %'), ('TSLA', 'Tesla', '1,1 %')]
@functools.lru_cache(maxsize=16)
def logo_tile(key, size):
    im = Image.open(f'{D}/logos/{key}.png').convert('RGBA').resize((size, size), Image.LANCZOS)
    sh = Image.new('RGBA', (size+40, size+40), 0); m = Image.new('L', (size+40, size+40), 0)
    ImageDraw.Draw(m).rounded_rectangle((20, 26, 20+size, 26+size), radius=size*.22, fill=150)
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(9))); sh.alpha_composite(im, (20, 20)); return sh
def tile_slots():
    out = []
    for i in range(9):
        row, k = (0, i) if i < 5 else (1, i-5); n = 5 if row == 0 else 4
        out.append((540+(k-(n-1)/2)*178, 300+row*205))
    return out
def logo_t(i): return T['logos']+.08+i*.17

# ---------- scènes ----------
def sHook(cv, c, t, a):
    grp(c, a*ease(t/.25), lambda c: text(c, "C'EST QUOI UN", 540, 255, 'xb', 50, WHITE, 'c', 1, 4))
    glow_text(cv, "ETF MSCI WORLD ?", 540, 360, 108, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.55, a=a, scale=lerp(1.25, 1, back(t/.45, 1.3)))
    k = t-T['q2']
    if k > 0: grp(c, a*ease(k/.25), lambda c: gpill(c, "ET POURQUOI DANS TON PEA ?", 540, 480, GD, 34), dy=12*(1-ease(k/.3)))
    put_emoji('🌍', 870, 250, 70, t-.35, a)
def counter_txt(v): return fmt(v)
def sCount(cv, c, t, a):
    k = t-T['achat']
    rain(cv, t, a)
    def plate(c):                                                     # voile sombre derrière les compteurs : ils restent lisibles sous la pluie
        for x in (300, 790):
            g = cairo.RadialGradient(x, 330, 0, x, 330, 260); g.add_color_stop_rgba(0, 0.02, 0.03, 0.06, .85); g.add_color_stop_rgba(.6, 0.02, 0.03, 0.06, .6); g.add_color_stop_rgba(1, 0.02, 0.03, 0.06, 0)
            c.save(); c.translate(x, 330); c.scale(1, .55); c.translate(-x, -330); c.set_source(g); c.arc(x, 330, 260, 0, 2*math.pi); c.fill(); c.restore()
    s_, c_ = surface(); plate(c_); cv.alpha_composite(with_alpha(to_img(s_), a*ease(k/.3)))
    n = int(round(1249*ease(clamp((k-.25)/1.9)))) if k > .25 else 0
    glow_text(cv, fmt(n), 300, 300, 120, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.25), reflect=False)
    grp(c, a*ease(k/.3), lambda c: text(c, "ENTREPRISES", 300, 400, 'xb', 34, ICE, 'c', .95, 4))
    p = lit_count(t)
    glow_text(cv, str(p), 790, 300, 120, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.6, a=a*ease(k/.25), reflect=False)
    grp(c, a*ease(k/.3), lambda c: text(c, "PAYS", 790, 400, 'xb', 34, ICE, 'c', .95, 4))
    kk = t-T['pays']
    if kk > 0: grp(c, a*ease(kk/.3), lambda c: gpill(c, "EN UN SEUL ACHAT", 540, 485, GR, 30))
def sLogos(cv, c, t, a):
    sl = tile_slots(); ux, uy, vis = project(-98, 39, T['logos'], *gplace(T['logos'])[:2], gplace(T['logos'])[2])
    for i, (key, nm, w) in enumerate(TOP):
        k = t-logo_t(i)
        if k <= 0: continue
        u = ease(k/.42); x = lerp(ux, sl[i][0], u); y = lerp(uy, sl[i][1], u) - 60*math.sin(math.pi*clamp(k/.42))
        sz = int(lerp(40, 128, back(k/.5, 1.6))); im = with_alpha(logo_tile(key, max(8, sz)), a*ease(k/.12))
        cv.alpha_composite(im, (int(x-im.width/2), int(y-im.height/2+3)))
        if k > .35: grp(c, a*ease((k-.35)/.2), lambda c, i=i, w=w: text(c, w, sl[i][0], sl[i][1]+92, 'xb', 26, WHITE, 'c', 1))
    kp = t-(logo_t(8)+.45)
    if kp > 0: grp(c, a*ease(kp/.25), lambda c: gpill(c, "CES 9 GÉANTS = 28 % DE L'INDICE", 540, 735, GD, 28), dy=10*(1-ease(kp/.3)))
def sWarn(cv, c, t, a):
    k = t-T['att']
    grp(c, a*ease(k/.2), lambda c: gpill(c, "MAIS ATTENTION", 540, 250, RD, 36, fg=WHITE), dy=-14*(1-ease(k/.25)))
    put_emoji('⚠️', 820, 250, 56, k-.1, a)
    ku = t-T['us']; out = 1-ease((t-T['chine']-.05)/.3)
    if ku > 0:
        glow_text(cv, "73 %", 540, 400, 170, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.75, a=a*ease(ku/.2)*out, scale=lerp(1.3, 1, back(ku/.4)))
        grp(c, a*ease((ku-.2)/.25)*out, lambda c: text(c, "AMÉRICAINES", 540, 530, 'xb', 42, WHITE, 'c', 1, 5))
    kc = t-T['chine']
    if kc > 0:
        glow_text(cv, "NI LA CHINE,", 540, 375, 104, top='FFFFFF', bottom='FFC2C9', glow='FF4057', ga=.55, a=a*ease((kc-.15)/.25), scale=lerp(1.25, 1, back((kc-.15)/.4)))
        glow_text(cv, "NI L'INDE", 540, 495, 104, top='FFFFFF', bottom='FFC2C9', glow='FF4057', ga=.55, a=a*ease((kc-.75)/.25), scale=lerp(1.25, 1, back((kc-.75)/.4)))
        grp(c, a*ease((kc-1.1)/.3), lambda c: gpill(c, "PAYS ÉMERGENTS : UN AUTRE INDICE", 540, 590, 'E8EEF8', 26))
def sFees(cv, c, t, a):
    k = t-T['frais']
    glow_text(cv, "LES FRAIS ?", 540, 290, 110, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease(k/.25), scale=lerp(1.25, 1, back(k/.4)))
    k2 = t-T['frais2']
    if k2 > 0:
        def d(kk, w, h):
            text(kk, "PAR AN, POUR UN ETF MSCI WORLD AU PEA", w/2, 52, 'xb', 28, ICE, 'c', .9, 2)
            text(kk, "soit 2 à 4 € pour 1 000 € placés", w/2, 285, 'xb', 38, 'B6FFD6', 'c', 1)
            kk.move_to(60, 338); kk.line_to(w-60, 338); kk.set_line_width(1.5); col(kk, WHITE, .14); kk.stroke()
            text(kk, "Hors PEA : dès 0,06 % par an", w/2, 380, 'sb', 30, ICE, 'c', .85)
        place(cv, gp(860, 440, d), tilt_quad(540, 640+30*(1-ease(k2/.4)), 860, 440, rx=.06+.25*(1-ease(k2/.4))), a*ease(k2/.35), 18, .5)
        glow_text(cv, "0,20 % À 0,38 %", 540, 598, 104, top='FFFFFF', bottom='B6FFD6', glow='3FE08A', ga=.6, a=a*ease((k2-.2)/.25), scale=lerp(1.3, 1, back((k2-.2)/.4)))
        put_emoji('💶', 905, 445, 60, k2-.45, a)
VAL = 1771
PX, PY, PW, PH_ = 540, 590, 900, 600
YB, HB = PY-PH_/2+PH_-130, 250
def bar_h(t, j):
    k = t-T['mille']
    if j == 0: return HB*1000/VAL*ease(clamp((k-.3)/.5))
    if k < 1.6: return HB*1000/VAL*ease(clamp((k-.7)/.5))
    return HB*val_at(t)/VAL
def val_at(t): return 1000+(VAL-1000)*ease(clamp((t-(T['mille']+1.6))/1.6))
def sGrowth(cv, c, t, a):
    k = t-T['mille']; u = ease(k/.4)
    def d(kk, w, h):
        text(kk, "1 000 € PLACÉS DANS UN ETF MSCI WORLD", w/2, 58, 'xb', 28, ICE, 'c', .9, 2)
        for j, (lab, colr) in enumerate((("IL Y A 5 ANS", CY2), ("AUJOURD'HUI", GD))):
            cx = w/2+(-200 if j == 0 else 200); hb = bar_h(t, j); yb = h-130
            g = cairo.LinearGradient(0, yb-hb, 0, yb); g.add_color_stop_rgba(0, *rgb(colr), .98); g.add_color_stop_rgba(1, *rgb(colr), .55)
            rr(kk, cx-75, yb-hb, 150, hb, 14); kk.set_source(g); kk.fill()
            text(kk, lab, cx, yb+38, 'xb', 24, ICE, 'c', .85, 2)
        text(kk, "ETF CW8, du 30/09/2021 au 30/09/2026, dividendes réinvestis, avant impôts", w/2, h-36, 'sb', 20, ICE, 'c', .6)
    place(cv, gp(PW, PH_, d, 'FFE9C0'), tilt_quad(PX, PY+30*(1-u), PW, PH_, rx=.05+.25*(1-u)), a*ease(k/.35), 18, .5)
    if k > .6: glow_text(cv, "1 000 €", PX-200, YB-bar_h(t, 0)-42, 54, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.4, a=a*ease((k-.6)/.3), reflect=False)
    if k > 1.0: glow_text(cv, fmt(val_at(t))+" €", PX+200, YB-bar_h(t, 1)-46, 64, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a*ease((k-1.0)/.3), reflect=False)
    kp = t-(T['mille']+3.3)
    if kp > 0: grp(c, a*ease(kp/.25), lambda c: gpill(c, "+77 % EN 5 ANS", 540, 240, GR, 34), dy=10*(1-ease(kp/.3)))
def sCta(cv, c, t, a):
    k = t-T['envoie']
    glow_text(cv, "ENVOIE-LA", 540, 300, 130, top='FFFFFF', bottom='FFE3A0', glow='FFB020', ga=.7, a=a*ease(k/.25), scale=lerp(1.3, 1, back(k/.4)))
    grp(c, a*ease((k-.3)/.3), lambda c: text(c, "à quelqu'un qui pense que", 540, 430, 'xb', 42, WHITE, 'c', 1))
    glow_text(cv, "LA BOURSE, C'EST COMPLIQUÉ", 540, 520, 72, top='FFFFFF', bottom='CFF4FF', glow='35D6FF', ga=.5, a=a*ease((k-.9)/.3))
    put_emoji('📤', 540, 650, 80, k-1.4, a)
    al = ease((k-1.8)/.4)
    def lg(c):
        c.push_group(); logo_symbol(c, 410, 770, 44); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 443, 770, 'b', 30, WHITE, 'l', al)
        text(c, "Contenu pédagogique, pas un conseil en investissement.", 540, 840, 'sb', 22, ICE, 'c', .65*al)
        text(c, "Les performances passées ne préjugent pas des performances futures.", 540, 872, 'sb', 22, ICE, 'c', .65*al)
    grp(c, a, lg)
SCENES = [(sHook, 0.0, T['achat']), (sCount, T['achat']-.1, T['logos']), (sLogos, T['logos']-.1, T['att']), (sWarn, T['att']-.1, T['frais']),
          (sFees, T['frais']-.1, T['mille']), (sGrowth, T['mille']-.1, T['envoie']), (sCta, T['envoie']-.1, DUR+1)]

# ---------- Mister Coin (3 clips : question, inquiet, enthousiaste) ----------
QUES, INQ, ENT = 'classique_parle_question', 'classique_parle_inquiet', 'classique_parle_enthousiaste'
CX_COIN, FEET = 540, 1700
MC = VeoCoin([(0.0, QUES, 'voix'), (12.70, INQ, 'voix'), (21.0, ENT, 'voix')], voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t): return CX_COIN, FEET+MC.hop_dy(t)

def frame(t):
    EMO.clear(); FADE[0] = 1.0
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
    if kk is not None and t < DUR-.4 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        al_ *= 1-ease((t-(DUR-.7))/.3)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, GOLD), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'impact'), (T['q2'], 'swish'), (T['achat'], 'swish'), (T['achat']+.25, 'tick'), (T['pays'], 'pop'), (T['logos'], 'whoosh'),
          (logo_t(8)+.45, 'glint'), (T['att'], 'riser'), (T['us'], 'impact'), (15.30, 'whoosh'), (T['chine']+.15, 'thud'), (T['chine']+.75, 'thud'),
          (T['frais'], 'swish'), (T['frais2']+.2, 'impact'), (T['frais2']+.45, 'coin'), (T['mille'], 'swish'), (T['mille']+1.6, 'tick'),
          (T['mille']+3.2, 'impact'), (T['mille']+3.25, 'coins'), (T['mille']+3.3, 'paid'), (T['envoie'], 'swish'), (T['envoie']+1.4, 'pop')]
    ev += [(LIT[k], 'zap2') for k in sorted(LIT, key=LIT.get)]
    ev += [(logo_t(i)+.38, 'pop') for i in range(9)]
    ev += [(r['t0']+.15, 'drop') for r in RAIN[::2]]                    # petits « plic » de la pluie de logos
    ev += [(T['achat']+.3, 'swish')]
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
