"""Carburant : où part l'argent d'un plein de gazole ? Station-service néo-rétro de nuit, néons rouges.
Vue du ciel (voix off), descente de caméra jusqu'à la pompe, Mister Coin classique (clips Veo) ;
le compteur de la pompe défile au fil des postes, la jauge de décomposition se remplit à gauche.
usage : python3 video.py info | png t1 t2 … | seg sortie.mp4 f0 f1"""
import sys, os, math, functools, subprocess, re, json
import numpy as np, cairo, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); sys.path.insert(0, f'{ROOT}/lib'); sys.path.insert(0, f'{ROOT}/mister_coin')
from nty import text, surface, to_img, rr, col, tw, W, H, finish
from logo import logo_symbol
from veo_coin import VeoCoin
FPS = int(os.environ.get('FPS', 60)); NB = '\u00a0'
WHITE = 'FFFFFF'; INK = '120A10'; NEON = 'FF2D55'; NEON2 = 'FFB3C2'; GOLD = 'F2B53A'; GREEN = '2DB36F'; GREY = '9AA0AA'
C_PET, C_TRA, C_ACC, C_TVA = 'F08C2A', '2F8FE8', 'E8344A', '9B5CF6'
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1-(1-x)**3
def inout(x): x = clamp(x); return x*x*(3-2*x)
def back(x, s=1.7): x = clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a, b, u): return a+(b-a)*u

# ---------- minutage (voix Thomas 58 s + 1 s de silence inséré à 3,25 s pour la descente) ----------
VOICE = f'{D}/voice_full.wav'
T = dict(vo=0.0, cent=4.35, prix=5.99, prend=9.15, deux=11.13, alors=12.88, abord=14.82, c53=16.96, fevrier=18.34, ensuite=22.39, c14=24.57,
         station=25.63, etat=29.30, accise=30.77, c30=33.11, tva=34.11, c20=35.05, caroui=36.06, taxe=38.02, total=39.23, seul=42.34,
         paradoxe=44.66, an=45.71, auj=49.06, c42=49.76, nonpas=51.02, plus=52.65, flambe=53.96, fin=55.96, quand=57.29, end=59.7)
if os.path.exists(f'{D}/timing.json'): T.update(json.load(open(f'{D}/timing.json')))
DUR = T['end']
T_DESC, T_LAND = 3.25, 4.33          # plongée vers la station, puis Mister Coin se pose
CAPS = [(T['vo'], "Je vais te révéler ce qu'on ne te dit pas forcément sur [le prix du carburant]."), (3.3, ""),
        (T['cent'], "[118 euros] !"), (T['prix'], "C'est le prix d'un plein de [50 litres] de gazole en ce moment."),
        (T['prend'], "On prend le [gazole] pour notre démonstration :"), (T['deux'], "[2,36 €] le litre."),
        (T['alors'], "Alors, où part [ton argent] ?"), (T['abord'], "D'abord, le [pétrole] et son raffinage :"), (T['c53'], "[53 euros]."),
        (T['fevrier'], "Et depuis février, la marge des raffineurs a été [multipliée par six]."),
        (T['ensuite'], "Ensuite, le [transport] et la station :"), (T['c14'], "[14 euros]."),
        (T['station'], "Et la station, elle, ne garde [qu'1 à 4 euros] sur ton plein."),
        (T['etat'], "Et puis il y a [l'État]."), (T['accise'], "[L'accise], l'ancienne TICPE :"), (T['c30'], "[30 euros]."),
        (T['tva'], "Et la [TVA] :"), (T['c20'], "[20 euros]."), (T['caroui'], "Car oui, tu paies de la TVA… [sur une taxe] !"),
        (T['total'], "Au total, l'État encaisse [50 euros] sur ton plein."), (T['seul'], "À lui seul, c'est [lui qui encaisse le plus]."),
        (T['paradoxe'], "Le [paradoxe] ?"), (T['an'], "Il y a un an, les taxes pesaient [54 %] du prix."), (T['auj'], "Aujourd'hui, [42 %]."),
        (T['nonpas'], "Non pas parce que l'État prend moins, il encaisse [même plus],"), (T['flambe'], "mais parce que le pétrole [a flambé]."),
        (T['fin'], "Maintenant, tu comprendras tout quand tu iras faire [ton plein] d'essence !")]
HL = {T['vo']: NEON, T['cent']: NEON, T['prix']: NEON, T['prend']: GOLD, T['deux']: GOLD, T['alors']: NEON, T['abord']: C_PET, T['c53']: C_PET,
      T['fevrier']: C_PET, T['ensuite']: C_TRA, T['c14']: C_TRA, T['station']: C_TRA, T['etat']: GOLD, T['accise']: C_ACC, T['c30']: C_ACC,
      T['tva']: C_TVA, T['c20']: C_TVA, T['caroui']: C_TVA, T['total']: GOLD, T['seul']: GOLD, T['paradoxe']: GOLD, T['an']: GREY, T['auj']: GOLD,
      T['nonpas']: GREEN, T['flambe']: C_PET, T['fin']: NEON}
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
    """zone sûre Réels / TikTok / Shorts : au-dessus de l'interface du bas (≥ 1500 px) et loin des icônes de droite (x > 950)"""
    sp = tw(c, ' ', 'b', size); wd = [tw(c, w, 'b', size)+(20 if k else 0) for w, k in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(wd):
        need = w+(sp if cur else 0)
        if cur and cw+need > 760: lines.append((cur, cw)); cur, cw = [], 0; need = w
        cur.append(i); cw += need
    lines.append((cur, cw)); y0 = y-(len(lines)-1)*36
    bw = max(lw for _, lw in lines)+60; bh = len(lines)*72+28
    rr(c, 540-bw/2, y0-50, bw, bh, 26); col(c, '0E0610', .74*a); c.fill()
    for li, (idx, lw) in enumerate(lines):
        x = 540-lw/2; yy = y0+li*72
        for i in idx:
            w, k = words[i]
            if k: rr(c, x, yy-34, wd[i], 64, 12); col(c, hl, a); c.fill(); text(c, w, x+10, yy, 'b', size, WHITE, 'l', a)
            else: text(c, w, x, yy, 'b', size, WHITE, 'l', a)
            x += wd[i]+sp

# ---------- outils graphiques ----------
def big(c, s, x, y, size, color, a=1, scale=1.0, tilt=0.0, edge=WHITE, lw=12):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(scale, scale)
    c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s)
    c.move_to(-ext.x_advance/2+5, size*.36+7); c.text_path(s); col(c, '000000', .35*a); c.fill()
    c.move_to(-ext.x_advance/2, size*.36); c.text_path(s); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, edge, a); c.stroke_preserve(); col(c, color, a); c.fill()
    c.restore()
def tag(c, s, x, y, color, a=1, size=30, fg=WHITE, align='c'):
    if a <= 0: return
    w = tw(c, s, 'xb', size, 2)+56; x0 = x-w/2 if align == 'c' else x
    rr(c, x0, y-size*.95, w, size*1.9, size*.95); col(c, color, a); c.fill(); text(c, s, x0+w/2, y, 'xb', size, fg, 'c', a, 2)
EMOJI_FONT = f'{ROOT}/fonts/NotoColorEmoji.ttf'
@functools.lru_cache(maxsize=32)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109); im = Image.new('RGBA', (180, 180), 0)
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((size, int(size*im.height/im.width)), Image.LANCZOS)
EMO = []
FADE = [1.0]                                 # opacité du contenu du panneau (fondu entre deux contenus)
def put_emoji(ch, x, y, size, k, a=1.0):
    a *= FADE[0]
    if k > 0 and a > 0: EMO.append((ch, x, y, size, k, a))
def draw_emoji(cv, ch, x, y, size, k, a):
    if not os.path.exists(EMOJI_FONT): return
    s = back(k/.35, 2.2)
    if s <= .02: return
    e = emoji(ch, size); e = e.resize((max(1, int(e.width*s)), max(1, int(e.height*s))))
    if a < 1: e = e.copy(); e.putalpha(e.getchannel('A').point(lambda v: int(v*a)))
    cv.alpha_composite(e, (int(x-e.width/2), int(y-e.height/2)))

# ---------- néons : scintillement ----------
def flick(t, ph=0.0):
    """intensité du néon : respiration lente et douce, sans coupure (pas d'effet de saut d'image)"""
    return 1+.045*math.sin(t*2.2+ph)+.02*math.sin(t*5.1+ph*1.7)

# ---------- décors ----------
def _load(name):
    return np.asarray(Image.open(f'{D}/decors/{name}.jpg').convert('RGB')).astype(np.float32)
@functools.lru_cache(maxsize=1)
def aerial():
    """vue du ciel (pleine résolution 1792 × 2400) + masques : néons de l'auvent, reflets rouges, traînées de phares"""
    a = _load('station_haut'); R, G, B = a[..., 0], a[..., 1], a[..., 2]; h, w = R.shape
    yy, xx = np.mgrid[0:h, 0:w]
    neon = ((R > 175) & (R-G > 80) & (R-B > 40) & (yy < 1250)).astype(np.float32)
    refl = ((R > 110) & (R-G > 60) & (yy >= 1250)).astype(np.float32)
    trail = ((np.minimum(np.minimum(R, G), B) > 165) & (xx < 620) & (yy > 620) & (yy < 1500)).astype(np.float32)
    tail = ((R > 150) & (R-G > 70) & (xx < 620) & (yy > 1650)).astype(np.float32)
    bl = lambda m, s: cv2.GaussianBlur(m, (0, 0), s)
    return a, bl(neon, 1.2), bl(refl, 2), bl(trail, 1), bl(tail, 1.5), yy.astype(np.float32)
@functools.lru_cache(maxsize=1)
def ground():
    """vue au sol, mise à l'échelle finale (1434 × 1920, cadrage x 300 → 1380) + masques néons et reflets"""
    im = Image.open(f'{D}/decors/station_sol.jpg').convert('RGB'); im = im.resize((int(im.width*1920/im.height), 1920), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]; h, w = R.shape
    yy, xx = np.mgrid[0:h, 0:w]
    neon = ((R > 170) & (R-G > 70) & (R-B > 30) & (yy < 1000)).astype(np.float32)
    refl = ((R > 100) & (R-G > 55) & (yy >= 1350)).astype(np.float32)
    bl = lambda m, s: cv2.GaussianBlur(m, (0, 0), s)
    return a, bl(neon, 1.5), bl(refl, 2.5)
GX0 = 300                                    # cadrage final dans l'image au sol
SCR = (640, 768, 864, 984)                   # écran de la pompe (coordonnées écran final)
def aerial_img(t):
    a, neon, refl, trail, tail, yy = aerial()
    f = flick(t); fr = 1+(f-1)*.6
    out = a*(1+neon[..., None]*(f-1)*.95)*(1+refl[..., None]*(fr-1)*.8)
    wave = (.5+.5*np.sin(yy/60-t*4))**3                               # des phares glissent doucement sur la route
    out += (trail*wave)[..., None]*np.array([45, 45, 40], np.float32)
    wave2 = (.5+.5*np.sin(yy/70+t*3.5))**3
    out += (tail*wave2)[..., None]*np.array([60, 6, 12], np.float32)
    return np.clip(out, 0, 255)
def ground_img(t):
    a, neon, refl = ground()
    f = flick(t, 1.3); fr = 1+(f-1)*.7
    out = a*(1+neon[..., None]*(f-1)*.95)
    sh = .08*np.sin(t*2.3)                                             # les flaques ondulent un peu
    out = out*(1+refl[..., None]*((fr-1)*.8+sh))
    return np.clip(out, 0, 255)

# ---------- compteur de la pompe (dessiné sur l'image au sol) ----------
PRICE = 2.3555; PARTS = [(53.35, C_PET), (14.42, C_TRA), (30.38, C_ACC), (19.63, C_TVA)]
P_START, P_END = T_LAND+.35, DUR-1.1          # la pompe débite du début à la fin de l'exposé, comme une vraie pompe
def euros_at(t):
    u = clamp((t-P_START)/(P_END-P_START))
    g = .88*u+.12*inout(u)                                                # débit régulier, démarrage et arrêt adoucis
    return 117.78*g
def fmt(v, d=2): return f"{v:,.{d}f}".replace(',', ' ').replace('.', ',')
# afficheur à 7 segments (comme sur les pompes) : segments éteints visibles en fantôme, segments allumés en néon rouge
SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg', ' ': ''}
def seg_digit(c, ch, x, y, h, lit, ghost=.07):
    """un chiffre à 7 segments ; (x, y) = coin bas gauche ; lit = intensité 0..1"""
    w = h*.52; th = h*.13; sl = h*.09                                       # largeur, épaisseur, inclinaison
    def P(px, py): return x+px+sl*(py/h), y-py                              # point incliné
    def seg(name):
        hh = h/2; g = th*.18
        if name in 'ad g'.replace(' ', ''):
            yy = {'a': h, 'g': hh, 'd': 0}[name]; x0_, x1_ = g+th*.5, w-g-th*.5
            pts = [(x0_, yy), (x0_+th*.5, yy+th*.5), (x1_-th*.5, yy+th*.5), (x1_, yy), (x1_-th*.5, yy-th*.5), (x0_+th*.5, yy-th*.5)]
        else:
            xx = {'b': w, 'c': w, 'e': 0, 'f': 0}[name]; y0_, y1_ = ((hh+g, h-g) if name in 'bf' else (g, hh-g))
            pts = [(xx, y0_+th*.3), (xx+th*.5, y0_+th*.8), (xx+th*.5, y1_-th*.8), (xx, y1_-th*.3), (xx-th*.5, y1_-th*.8), (xx-th*.5, y0_+th*.8)]
        c.move_to(*P(*pts[0]))
        for q in pts[1:]: c.line_to(*P(*q))
        c.close_path()
    on = SEG.get(ch, '')
    for nm in 'abcdefg':
        seg(nm); col(c, 'FF2D55', ghost); c.fill()
    for nm in on:
        for wdt, al in ((th*1.6, .10), (th*.8, .22)):
            seg(nm); c.set_line_width(wdt); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, NEON, al*lit); c.stroke()
        seg(nm); col(c, 'FF3B5F', lit); c.fill_preserve(); col(c, 'FFC9D4', .35*lit); c.set_line_width(1); c.stroke()
    return w+h*.2
def seg_text(c, s_, xr, y, h, t, seed=0):
    """nombre aligné à droite sur xr ; la virgule est un point lumineux ; chaque chiffre crépite légèrement"""
    xs = []; wd = h*.52+h*.2; x = xr
    for k, ch in enumerate(reversed(s_)):
        if ch == ',':
            x -= h*.22; xs.append((ch, x)); continue
        x -= wd; xs.append((ch, x))
    for k, (ch, x) in enumerate(xs):
        n = k+seed*7
        lit = .9+.08*math.sin(t*37+n*1.7)+.05*math.sin(t*91+n*3.1)        # grésillement permanent
        for a0, d0 in CRACK:
            if a0 <= t < a0+d0 and (int(a0*10)+n) % 5 == 0: lit *= .55     # micro-coupure rare d'un chiffre
        if ch == ',':
            c.arc(x+h*.08, y-h*.05, h*.06, 0, 2*math.pi); col(c, 'FF3B5F', lit); c.fill()
        else: seg_digit(c, ch, x, y, h, lit)
CRACK = [(a/10, .05) for a in range(52, 600, 23)]                       # instants de crépitement (environ toutes les 2,3 s)
def counter(c, t, ox):
    x0, y0, x1, y1 = SCR; x0 += ox; x1 += ox
    rr(c, x0+5, y0+5, x1-x0-10, y1-y0-10, 8); col(c, '050206', .97); c.fill()
    g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, 1, .2, .35, .05); g.add_color_stop_rgba(1, 1, .2, .35, 0)
    rr(c, x0+5, y0+5, x1-x0-10, y1-y0-10, 8); c.set_source(g); c.fill()
    e = euros_at(t); L = e/PRICE
    text(c, "€ À PAYER", x0+18, y0+26, 'xb', 12, 'FF8FA3', 'l', .9, 2)
    seg_text(c, fmt(e), x1-14, y0+100, 52, t, 0)
    c.move_to(x0+14, y0+120); c.line_to(x1-14, y0+120); c.set_line_width(1.2); col(c, NEON, .3); c.stroke()
    text(c, "LITRES", x0+18, y0+142, 'xb', 12, 'FF8FA3', 'l', .9, 2); seg_text(c, fmt(L), x1-16, y0+164, 30, t, 1)
    text(c, "PRIX/L", x0+18, y0+184, 'xb', 12, 'FF8FA3', 'l', .9, 2); seg_text(c, "2,356", x1-16, y0+202, 26, t, 2)

# ---------- caméra ----------
def view(arr, box):
    """recadre une zone (x0, y0, w, h) de l'image source sur 1080 × 1920"""
    x0, y0, w, h = box; sx, sy = W/w, H/h
    M = np.float32([[sx, 0, -x0*sx], [0, sy, -y0*sy]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
AP = (1050., 1000.)                          # centre de l'auvent dans la vue du ciel (pleine résolution)
def aerial_box(z):
    x0, w = 221., 1350.; y0, h = 0., 2400.
    return (AP[0]+(x0-AP[0])/z, AP[1]+(y0-AP[1])/z, w/z, h/z)
def aerial_frame(t):
    if t < T_DESC: z = 1+.13*inout(t/T_DESC)
    else: u = clamp((t-T_DESC)/.75); z = 1.13+2.6*u**2.2
    img = aerial_img(t)
    if t < T_DESC: return view(img, aerial_box(z))
    acc = sum(view(img, aerial_box(z*k)) for k in (1, .965, .93, .895)) / 4    # flou de vitesse pendant la plongée
    return acc
def ground_box(t):
    final = (GX0, 0., 1080., 1920.)
    if t >= T_LAND+.35: return final
    u = ease((t-3.8)/(T_LAND+.35-3.8)); s = lerp(1.85, 1, u)
    w, h = 1080/s, 1920/s; cx = lerp(1010, GX0+540, u); y0 = 0.
    return (cx-w/2, y0, w, h)

# ---------- panneau de gauche (jauge, paradoxe) ----------
PX0, PY0, PX1, PY1 = 36, 218, 566, 940
TUBE_X0, TUBE_X1, TUBE_Y1, TUBE_H = 70, 182, 902, 540
def rgb(h, k=1.0, mix_white=0.0):
    h = h.lstrip('#'); v = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    return [min(1, x*k*(1-mix_white)+mix_white) for x in v]
def panel(c, a):
    """carte en verre fumé, liseré néon doux"""
    if a <= 0: return
    for w_, al in ((10, .06), (5, .10)):
        rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 30); c.set_line_width(w_); col(c, NEON, al*a); c.stroke()
    g = cairo.LinearGradient(0, PY0, 0, PY1); g.add_color_stop_rgba(0, .07, .03, .08, .86*a); g.add_color_stop_rgba(1, .03, .01, .04, .90*a)
    rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 30); c.set_source(g); c.fill()
    rr(c, PX0, PY0, PX1-PX0, PY1-PY0, 30); c.set_line_width(1.6); col(c, 'FF8FA6', .55*a); c.stroke()
STARTS = lambda: [(T['abord'], T['c53']), (T['ensuite'], T['c14']), (T['accise'], T['c30']), (T['tva'], T['c20'])]
NAMES = ["PÉTROLE ET RAFFINAGE", "TRANSPORT ET STATION", "ACCISE (EX-TICPE)", "TVA (20 %)"]
BX0, BX1 = 66, 536; BW = BX1-BX0; SB_Y = PY0+112; R0 = PY0+192; RH = 118
def fill_k(i, t, final=False):
    if final: return 1.0
    return inout((t-STARTS()[i][1]+.25)/1.0)
def bar(c, x, y, w, h, colr, a, track=True, full=BW):
    if track: rr(c, x, y, full, h, h/2); col(c, 'FFFFFF', .08*a); c.fill()
    if w > .5:
        g = cairo.LinearGradient(x, 0, x+max(w, 1), 0); g.add_color_stop_rgba(0, *rgb(colr, .85), a); g.add_color_stop_rgba(1, *rgb(colr, 1, .2), a)
        rr(c, x, y, max(w, h), h, h/2); c.set_source(g); c.fill()
        g2 = cairo.LinearGradient(0, y, 0, y+h); g2.add_color_stop_rgba(0, 1, 1, 1, .28*a); g2.add_color_stop_rgba(.5, 1, 1, 1, 0)
        rr(c, x, y, max(w, h), h, h/2); c.set_source(g2); c.fill()
def gauge(c, t, a, mode='parts'):
    """tableau de décomposition : barre empilée graduée en haut, une ligne par poste (barre proportionnelle + montant exact), total en bas"""
    final = mode == 'final'; ks = [fill_k(i, t, final) for i in range(4)]
    # barre empilée, graduée
    rr(c, BX0, SB_Y, BW, 30, 15); col(c, 'FFFFFF', .08*a); c.fill()
    c.save(); rr(c, BX0, SB_Y, BW, 30, 15); c.clip(); x = BX0
    for i, ((v, colr), k) in enumerate(zip(PARTS, ks)):
        w = BW*v/117.78*k; dim = .3 if (mode == 'etat' and i < 2) else 1.0
        if w > .3:
            c.rectangle(x, SB_Y, w, 30); col(c, colr, a*dim); c.fill()
            if x > BX0: c.move_to(x, SB_Y); c.line_to(x, SB_Y+30); c.set_line_width(2); col(c, '0B0610', a); c.stroke()
        x += w
    g2 = cairo.LinearGradient(0, SB_Y, 0, SB_Y+30); g2.add_color_stop_rgba(0, 1, 1, 1, .25*a); g2.add_color_stop_rgba(.5, 1, 1, 1, 0)
    c.rectangle(BX0, SB_Y, BW, 30); c.set_source(g2); c.fill(); c.restore()
    for v in (0, 25, 50, 75, 100):
        xx = BX0+BW*v/117.78; c.move_to(xx, SB_Y+36); c.line_to(xx, SB_Y+43); c.set_line_width(1.5); col(c, 'FFFFFF', .35*a); c.stroke()
        text(c, f"{v} €" if v == 100 else str(v), xx, SB_Y+56, 'xb', 12, 'B9AEC0', 'c', a)
    # lignes
    rows = []
    for i, ((v, colr), k) in enumerate(zip(PARTS, ks)):
        tn, tv = STARTS()[i]; y = R0+i*RH; rows.append(y)
        ka = 1.0 if final else ease((t-tn)/.4)
        if ka <= 0: continue
        dim = .3 if (mode == 'etat' and i < 2) else 1.0; al = ka*a*dim; dx = 18*(1-ka)
        rr(c, BX0+dx, y-9, 16, 16, 4); col(c, colr, al); c.fill()
        text(c, NAMES[i], BX0+28+dx, y, 'xb', 18, 'EDE6F0', 'l', al, 1)
        if k > 0: text(c, fmt(v*k)+" €", BX1, y+2, 'a', 40, fmt_col(colr), 'r', al)
        bar(c, BX0, y+30, BW*v/117.78*k, 14, colr, al)
        if not final and mode != 'etat':
            if i == 0 and t > T['fevrier']+.9: note(c, "MARGE DES RAFFINEURS ×6 DEPUIS FÉVRIER", BX0, y+70, C_PET, ease((t-T['fevrier']-.9)/.35), 14)
            if i == 1 and t > T['station']+1.2: note(c, "DONT STATION : 1 À 4 € PAR PLEIN", BX0, y+70, C_TRA, ease((t-T['station']-1.2)/.35), 14)
    # total
    ty = R0+4*RH; tot = sum(v*k for (v, _), k in zip(PARTS, ks))
    if tot > 0 and mode != 'etat':
        c.move_to(BX0, ty-36); c.line_to(BX1, ty-36); c.set_line_width(1.5); col(c, 'FFFFFF', .3*a); c.stroke()
        text(c, "TOTAL DU PLEIN", BX0, ty, 'xb', 18, WHITE, 'l', a, 2); text(c, fmt(tot)+" €", BX1, ty+2, 'a', 44, WHITE, 'r', a)
    return rows
def fmt_col(colr): return '%02X%02X%02X' % tuple(int(x*255) for x in rgb(colr, 1.0, .22))
def note(c, s_, x, y, colr, a, size=16):
    """petite pastille contour, pour une précision"""
    if a <= 0: return
    w = tw(c, s_, 'xb', size, 1)+28; rr(c, x, y-size*.95, w, size*1.9, size*.95); col(c, colr, .22*a); c.fill_preserve(); c.set_line_width(1.6); col(c, colr, a); c.stroke()
    text(c, s_, x+14, y, 'xb', size, WHITE, 'l', a, 1)
def arrow(c, x0, y0, x1, y1, bend, colr, a, w=4):
    """flèche courbe de (x0,y0) vers (x1,y1), en pointillés"""
    mx = (x0+x1)/2+bend
    c.set_dash([10, 7]); c.move_to(x0, y0); c.curve_to(mx, y0, mx, y1, x1, y1); c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, colr, a); c.stroke(); c.set_dash([])
    for s_ in (-1, 1):
        c.move_to(x1, y1); c.line_to(x1-15*math.cos(s_*.55), y1-15*math.sin(s_*.55))
    c.set_line_width(w); c.stroke()
def left(c, t):
    """le fond du panneau reste en place ; seul son contenu change, en fondu enchaîné (pas de saut)"""
    FADE[0] = 1.0
    if T['alors']-.15 <= t < T['paradoxe']-.12: fo = 1-ease((t-(T['paradoxe']-.45))/.3)
    elif T['paradoxe']-.12 <= t < T['fin']-.12: fo = 1-ease((t-(T['fin']-.45))/.3)
    else: fo = 1.0
    if t >= T['alors']-.15: panel(c, ease((t-T['alors'])/.35))
    if fo < 1:
        FADE[0] = fo; c.push_group(); _left(c, t); c.pop_group_to_source(); c.paint_with_alpha(max(0, fo)); return
    _left(c, t)
def _left(c, t):
    a = 1.0
    if t < T['alors']-.15:                                                 # intro : le chiffre choc
        k = t-T['cent']
        big(c, "118 €", 300, 420, 190, 'FF5A78', ease(k/.2), lerp(1.3, 1, back(k/.45)), edge=WHITE, lw=10)
        kp = t-T['prix']
        if kp > 0:
            text(c, "UN PLEIN DE 50 LITRES", 300, 600, 'xb', 34, WHITE, 'c', ease(kp/.3), 1)
            put_emoji('⛽', 300, 700, 80, kp-.2)
        kg = t-T['prend']
        if kg > 0: tag(c, "GAZOLE · 2,36 €/L", 300, 820, GOLD, ease(kg/.3), 30, INK)
        kd = t-T['deux']
        if kd > 0: text(c, "PRIX MOYEN · SEMAINE DU 2 OCTOBRE", 300, 890, 'xb', 17, 'D8C9D4', 'c', ease(kd/.3), 1)
        return
    if t < T['paradoxe']-.12:                                              # le tableau se remplit
        ka = ease((t-T['alors'])/.35)
        text(c, "OÙ PART TON ARGENT ?", (PX0+PX1)/2, PY0+50, 'a', 46, WHITE, 'c', ka)
        mode = 'etat' if t >= T['total'] else 'parts'
        rows = gauge(c, t, ka, mode)
        if T['caroui'] <= t < T['total']:                                  # la TVA se paie aussi sur l'accise
            kt = ease((t-T['taxe']+.2)/.4)
            if kt > 0:
                arrow(c, BX0-8, rows[3]+36, BX0-8, rows[2]+30, -22, 'FFD34D', kt, 3)
                note(c, "CALCULÉE AUSSI SUR L'ACCISE", BX0, rows[3]+70, 'FFC21A', kt, 14)
        if t >= T['total']:
            ke = ease((t-T['total'])/.35); y0_, y1_ = rows[2]-28, rows[3]+56
            for w_, al in ((8, .15), (2.5, 1.0)):
                rr(c, BX0-14, y0_, BW+28, y1_-y0_, 16); c.set_line_width(w_); col(c, GOLD, al*ke); c.stroke()
            ty = R0+4*RH
            c.move_to(BX0, ty-36); c.line_to(BX1, ty-36); c.set_line_width(1.5); col(c, GOLD, .5*ke); c.stroke()
            text(c, "L'ÉTAT", BX0, ty-6, 'xb', 20, GOLD, 'l', ke, 3); text(c, "42 % DU PLEIN", BX0, ty+20, 'xb', 15, 'F6E2B0', 'l', ease((t-T['total']-.4)/.3), 2)
            big(c, "50,01 €", BX1-118, ty+2, 56, GOLD, ke, lerp(1.2, 1, back((t-T['total'])/.45)), edge=INK, lw=6)
            ks_ = t-T['seul']
            if ks_ > 0:
                kk = ease(ks_/.3); note(c, "LE PREMIER ENCAISSEUR", (PX0+PX1)/2-118, rows[2]-56, GOLD, kk, 18); put_emoji('👑', (PX0+PX1)/2+176, rows[2]-58, 40, ks_-.15)
        return
    if t < T['fin']-.12:                                                   # le paradoxe
        kp = t-T['paradoxe']
        text(c, "LE PARADOXE", (PX0+PX1)/2, PY0+50, 'a', 50, GOLD, 'c', ease(kp/.3))
        text(c, "PART DES TAXES DANS LE PRIX", (PX0+PX1)/2, PY0+104, 'xb', 19, 'D8C9D4', 'c', ease((kp-.2)/.3), 2)
        for i, (t0, lab, v, cl) in enumerate(((T['an'], "IL Y A UN AN", 54, GREY), (T['auj'], "AUJOURD'HUI", 42, GOLD))):
            u = inout((t-t0-.3)/.7)
            if t < t0: continue
            y = 400+i*130; ka_ = ease((t-t0)/.3)
            text(c, lab, BX0, y, 'xb', 20, 'EDE6F0', 'l', ka_, 2); text(c, f"{round(v*u)} %", BX1, y+2, 'a', 44, fmt_col(cl), 'r', ka_)
            bar(c, BX0, y+32, BW*v/100*u, 34, cl, ka_)
            for q in (25, 50, 75):
                xx = BX0+BW*q/100; c.move_to(xx, y+32); c.line_to(xx, y+66); c.set_line_width(1); col(c, '0B0610', .6*ka_); c.stroke()
        kn = t-T['plus']+.4
        if kn > 0:
            c.move_to(BX0, 650); c.line_to(BX1, 650); c.set_line_width(1.5); col(c, 'FFFFFF', .25*ease(kn/.3)); c.stroke()
            text(c, "TAXES PAR LITRE", BX0, 690, 'xb', 18, 'D8C9D4', 'l', ease(kn/.3), 2)
            text(c, "≈ 0,88 € → 1,00 €", BX1, 734, 'xb', 36, GREEN, 'r', ease(kn/.3)); put_emoji('⬆️', BX0+20, 734, 40, kn-.3)
        kf = t-T['flambe']-.5
        if kf > 0:
            text(c, "PÉTROLE PAR LITRE", BX0, 800, 'xb', 18, 'D8C9D4', 'l', ease(kf/.3), 2)
            text(c, "≈ 0,52 € → 1,07 €", BX1, 844, 'xb', 36, C_PET, 'r', ease(kf/.3)); put_emoji('🔥', BX0+20, 844, 44, kf-.3)
        return
    kf = t-T['fin']; ka = ease(kf/.35)                       # récapitulatif final
    text(c, "TON PLEIN DE 117,78 €", (PX0+PX1)/2, PY0+48, 'a', 44, WHITE, 'c', ka)
    gauge(c, t, ka, 'final')
    al = ease((t-T['quand']-.6)/.4)
    if al > 0:
        c.push_group(); logo_symbol(c, 214, PY0+94, 18); c.pop_group_to_source(); c.paint_with_alpha(al)
        text(c, "Actions_Benefices", 232, PY0+94, 'b', 19, WHITE, 'l', al)

# ---------- vue du ciel : titre néon ----------
def neon_title(c, t):
    f = flick(t, 2.1) if t > .4 else 1.0; a = clamp(f, .3, 1)
    for s_, y, size in (("118 €", 330, 210), ("LE PLEIN", 520, 104)):
        c.save(); c.select_font_face('Anton'); c.set_font_size(size); ext = c.text_extents(s_)
        x = 540-ext.x_advance/2
        for wdt, al in ((26, .10), (16, .18), (8, .35)):
            c.move_to(x, y+size*.36); c.text_path(s_); c.set_line_width(wdt); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, NEON, al*a); c.stroke()
        c.move_to(x, y+size*.36); c.text_path(s_); c.set_line_width(4); col(c, NEON2, a); c.stroke_preserve(); col(c, 'FFF1F4', .95*a); c.fill(); c.restore()
    text(c, "CE QU'ON NE TE DIT PAS SUR TON PLEIN", 540, 640, 'xb', 26, WHITE, 'c', ease((t-.3)/.4), 2)

# ---------- pluie ----------
@functools.lru_cache(maxsize=1)
def drops():
    rng = np.random.default_rng(11); return rng.uniform(0, W, 150), rng.uniform(0, H, 150), rng.uniform(900, 1500, 150), rng.uniform(18, 40, 150), rng.uniform(25, 70, 150)
def rain(lay, t, k=1.0):
    d = ImageDraw.Draw(lay); X, Y, S, L, A = drops()
    for x0, y0, s, l, a in zip(X, Y, S, L, A):
        y = (y0+s*t) % (H+60)-30; x = (x0-s*t*.12) % W
        d.line((x, y, x-l*.12, y+l), fill=(220, 225, 255, int(a*k)), width=2)

# ---------- Mister Coin (clips Veo, version classique) ----------
EXP, ENT = 'classique_parle_explique', 'classique_parle_enthousiaste'
CX_COIN, FEET = 330, 1700
INQ, TRI = 'classique_parle_inquiet', 'classique_parle_triste'
# humeur selon le propos (changements calés dans les silences) : enthousiaste au début, inquiet quand l'État arrive, triste sur le total et le paradoxe, de nouveau enjoué à la fin
CONF, QUES = 'classique_parle_confidence', 'classique_parle_question'
# confidence sur « tu paies de la TVA… sur une taxe », question sur « Le paradoxe ? »
MC = VeoCoin([(3.95, [ENT, EXP], 'voix'), (29.0, [INQ, EXP], 'voix'), (35.75, CONF, 'voix'), (39.0, [TRI, INQ], 'voix'), (44.3, QUES, 'voix'),
              (48.75, [TRI, INQ], 'voix'), (55.7, [ENT, EXP], 'voix')],
             voix=VOICE, duree=DUR, x=CX_COIN, pieds=FEET, largeur_piece=220, lisse=True)
def coin_pos(t):
    """il tombe du ciel avec la caméra et se pose devant la pompe"""
    t0 = 3.95
    if t < t0: return None
    if t < T_LAND: u = (t-t0)/(T_LAND-t0); return CX_COIN, lerp(-150, FEET, u**1.8)
    if t < T_LAND+.22: return CX_COIN, FEET+16*math.sin(math.pi*(t-T_LAND)/.22)
    return CX_COIN, FEET+MC.hop_dy(t)                                     # petit saut sur place quand il change de geste

def frame(t):
    EMO.clear()
    if t < 4.05:                                                           # vue du ciel, puis plongée
        A = aerial_frame(t)
    if t >= 3.8:                                                           # vue au sol, la caméra descend
        G = ground_img(t)
        gi = Image.fromarray(G.astype(np.uint8)).convert('RGBA'); s0, c0 = surface()
        lay = Image.new('RGBA', gi.size, 0); s1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, gi.size[0], gi.size[1]); c1 = cairo.Context(s1)
        counter(c1, t, GX0); s1.flush()
        cnt = Image.frombuffer('RGBA', gi.size, bytes(s1.get_data()), 'raw', 'BGRa', s1.get_stride(), 1)
        gi.alpha_composite(cnt); Gv = view(np.asarray(gi.convert('RGB')).astype(np.float32), ground_box(t))
    if t < 3.8: base = A
    elif t < 4.05:
        u = inout((t-3.8)/.25); base = A*(1-u)+Gv*u
        fl = math.sin(math.pi*u)*.35; base = base*(1-fl)+np.array([255, 120, 150], np.float32)*fl      # éclair néon au passage
    else: base = Gv
    cv = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    s, c = surface()
    if t < T_DESC+.35:
        neon_title(c, t); a_t = 1-ease((t-T_DESC)/.35)
        if a_t < 1:
            im = to_img(s); im.putalpha(im.getchannel('A').point(lambda v: int(v*a_t))); cv.alpha_composite(im)
        else: cv.alpha_composite(to_img(s))
    elif t >= T_LAND-.1:
        left(c, t); cv.alpha_composite(to_img(s))
        for e in EMO: draw_emoji(cv, *e)
    p = coin_pos(t)
    if p is not None:
        X, Y = p; rgb, al = MC.layer(t, X, Y)
        a = np.asarray(cv.convert('RGB')).astype(np.float32)
        fx = MC.feet_x(al, Y) if Y > FEET-30 else (X if Y > 300 else None)
        if fx is not None:                                                 # ombre douce au sol (plus petite quand il est en l'air)
            k = 1/(1+max(0, FEET-Y)/150)
            m = np.zeros((H, W), np.float32); cv2.ellipse(m, (int(fx), FEET-3), (int(100*k)+1, int(15*k)+1), 0, 0, 360, .45*k, -1); m = cv2.GaussianBlur(m, (0, 0), 9)
            a *= (1-m[..., None])
        a = a*(1-al[..., None])+rgb*al[..., None]
        cv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), 0); rain(lay, t, .8 if t < 4 else 1.0); cv.alpha_composite(lay)
    s2, c2 = surface(); kk = cap_at(t)
    if kk is not None and t < DUR-.9 and CAPS[kk][1]:
        st0 = CAPS[kk][0]; al_ = 1.0 if st0 == 0 else ease((t-st0)/.12)
        caption(c2, parse(CAPS[kk][1]), HL.get(st0, NEON), a=al_)
    cv.alpha_composite(to_img(s2))
    return finish(cv, t, 3.0)

def events():
    ev = [(0.0, 'neon'), (1.2, 'trans'), (T_DESC, 'whoosh'), (T_DESC+.1, 'riser'), (T_LAND, 'thud'), (T['cent'], 'impact'), (P_START-.05, 'nozzle'),
          (T['prix'], 'pop'), (T['prend'], 'swish'), (T['deux'], 'tick'), (T['alors'], 'swish'),
          (T['c53']-.25, 'fill0'), (T['c14']-.25, 'fill1'), (T['c30']-.25, 'fill2'), (T['c20']-.25, 'fill3'),
          (T['fevrier']+.9, 'pop'), (T['station']+1.2, 'pop'), (T['etat'], 'swish'), (T['taxe']-.2, 'glint'),
          (T['total'], 'impact'), (T['total']+.1, 'coins'), (T['seul'], 'glint'), (T['paradoxe'], 'swish'), (T['paradoxe'], 'low'),
          (T['an']+.3, 'tick'), (T['auj']+.3, 'tick'), (T['plus']-.4, 'pop'), (T['flambe']+.5, 'pop'), (T['fin'], 'swish'),
          (P_END, 'clack'), (T['quand']+.6, 'paid')]
    ev += [(h-.05, 'hop') for h in MC._global_sequence() and MC.hops]
    ev += [(a0, 'zap') for a0, _ in CRACK if P_START < a0 < P_END]          # grésillement de l'afficheur
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
